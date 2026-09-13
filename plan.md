# CampusVault RAG & Backend Implementation Plan

> **Goal:** Build a hyper-reliable, bug-proof RAG backend for CampusVault and deploy it successfully on free-tier infrastructure, specifically avoiding common Out-Of-Memory (OOM) and timeout errors on Render.

---

## 🚨 Critical Research & Bug-Prevention Strategies

Before writing any code, we must address the three biggest reasons GenAI apps fail during deployment:

1. **The Embedding Model Trap:**
   - ❌ *Deprecated/Legacy:* `all-MiniLM-L6-v2` is widely considered legacy. It has a tiny 512-token context window and lower retrieval accuracy.
   - ✅ **The 2026 Standard:** **`BAAI/bge-small-en-v1.5`**. It’s lightweight (~120MB), extremely fast, and completely destroys older models on retrieval benchmarks (BEIR). We will use this.

2. **The Render Deployment Crash (OOM & Timeout):**
   - ❌ *The Bug:* Render's Free Web Service has **512MB of RAM** and strict boot timeouts. If your app tries to download a HuggingFace model *during startup* (when the app runs), Render will kill the process for taking too long, or the PyTorch overhead will cause an Out-Of-Memory (OOM) crash.
   - ✅ *The Fix:* We will use `huggingface-cli` inside a custom `build.sh` script to download the model into the disk cache *during the build phase*. We will also strictly install the **CPU-only version of PyTorch**, which keeps the RAM footprint under ~350MB.

3. **The Vector Database Scaling Bug:**
   - ❌ *The Bug:* Using standard exact math or `ivfflat` indices in pgvector is slow and outdated.
   - ✅ *The Fix:* We will use the **HNSW** (Hierarchical Navigable Small World) index in Supabase. It is the modern standard for fast vector retrieval and handles scaling beautifully.

---

## 🟢 Phase 1: Local Database Setup via Supabase CLI

We will use the Supabase CLI to create a reproducible, professional local development environment rather than clicking around a dashboard.

**1. Initialize Supabase**
```bash
supabase init
```

**2. Create the Database Blueprint (Migration)**
```bash
supabase migration new init_rag_schema
```
*Inside the generated `supabase/migrations/<timestamp>_init_rag_schema.sql` file, we write:*

```sql
-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create main notes table
CREATE TABLE notes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  content text NOT NULL,
  embedding vector(384), -- 384 dimensions for bge-small-en-v1.5
  file_url text,
  file_name text,
  week_number int,
  course_id text,
  created_at timestamp DEFAULT now()
);

-- Create HNSW index for lightning-fast retrieval
CREATE INDEX on notes USING hnsw (embedding vector_cosine_ops);

-- Similarity Search RPC (Remote Procedure Call)
CREATE OR REPLACE FUNCTION match_notes(
  query_embedding vector(384), match_threshold float, match_count int, filter_week int
)
RETURNS TABLE (id uuid, content text, file_url text, file_name text, similarity float)
LANGUAGE sql STABLE AS $$
  SELECT
    id, content, file_url, file_name,
    1 - (embedding <=> query_embedding) AS similarity
  FROM notes
  WHERE week_number = filter_week AND 1 - (embedding <=> query_embedding) > match_threshold
  ORDER BY embedding <=> query_embedding
  LIMIT match_count;
$$;
```

**3. Start the Local DB Environment**
```bash
supabase start
# This spins up Postgres + pgvector + Storage locally via Docker
```

---

## 🔵 Phase 2: Python Backend & HuggingFace CLI Setup

We need to ensure the dependencies are strictly managed for low RAM usage.

**1. Create `requirements.txt`**
```text
# Requirements
fastapi
uvicorn
python-multipart
python-dotenv
groq
supabase
sentence-transformers
pdfplumber
huggingface_hub
Pillow
```

**2. The Install Strategy (Crucial for Render)**
To avoid installing massive CUDA (GPU) libraries on our server, we must run this specific command:
```bash
# Force CPU-only PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

**3. Pre-Download the Embedder locally**
```bash
# Downloads the model to your local cache (~120MB)
huggingface-cli download BAAI/bge-small-en-v1.5
```

---

## 🟣 Phase 3: Writing the Bug-Proof Backend Code

### 1. `services/embedder.py` (Cached, Fast Embedding)
```python
import os
from sentence_transformers import SentenceTransformer

# Explicitly set HF cache dir so Render doesn't lose the model
os.environ["HF_HOME"] = os.environ.get("HF_HOME", "/opt/render/project/.cache/huggingface")

# Load the modern BAAI model
model = SentenceTransformer("BAAI/bge-small-en-v1.5")

def get_embedding(text: str) -> list[float]:
    return model.encode(text).tolist()
```

### 2. `utils/chunker.py` (Smart Semantic Chunking)
Instead of blindly cutting characters, we split safely.
```python
def semantic_chunk(text: str, max_chars=500, overlap=100) -> list[str]:
    # We will implement logic to split safely on '\n\n' or '.' 
    # to avoid cutting sentences in half (prevents hallucination).
    pass 
```

### 3. FastAPI Server (`main.py`)
- We will expose `/ingest` (Handles OCR via Groq `qwen3.6-27b`, classification, and embedding).
- We will expose `/query` (Runs embedding, Supabase RPC search, and Groq `llama-3.3-70b` RAG generation).

---

## 🟠 Phase 4: Production Deployment via Render (Infrastructure as Code)

To avoid the Render UI completely and ensure the build doesn't crash, we use a `render.yaml` blueprint.

**1. Create `render.yaml` in the root:**
```yaml
services:
  - type: web
    name: campusvault-backend
    env: python
    region: oregon
    plan: free
    buildCommand: "./build.sh"
    startCommand: "uvicorn main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: GROQ_API_KEY
        sync: false
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_SERVICE_KEY
        sync: false
```

**2. Create `build.sh` (The Magic Bullet against OOM)**
This script runs during the Render *build* phase, completely bypassing boot timeouts.
```bash
#!/usr/bin/env bash
# exit on error
set -o errexit

# Install CPU PyTorch first to save space
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

# Use HuggingFace CLI to download the model during the BUILD phase
export HF_HOME="/opt/render/project/.cache/huggingface"
huggingface-cli download BAAI/bge-small-en-v1.5
```
*(Make sure to run `chmod +x build.sh` before pushing).*

**3. Deploy**
Connect the GitHub repo to Render, and Render will automatically read `render.yaml` and execute the safe build pipeline.

---

## ⚫ Phase 5: Frontend Sync via Vercel CLI

Once the backend URL is live on Render (e.g., `https://campusvault-api.onrender.com`), we link the React UI.

**1. Create the React app**
```bash
npm create vite@latest campusvault-ui -- --template react-ts
```

**2. Deploy via Vercel CLI**
```bash
npm i -g vercel
vercel login
vercel link
```

**3. Inject Backend Variables**
```bash
vercel env add VITE_API_URL
# Paste your Render URL here
```

**4. Push to Production**
```bash
vercel --prod
```

---

> **Ready to Execute:** This plan ensures zero deprecated tools, zero hallucinated models, and fully navigates the memory constraints of free-tier cloud deployment.
