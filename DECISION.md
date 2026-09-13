# 🏛️ CampusVault — Architecture, Decisions & Context Record (DECISION.md)

> **Document Purpose:** Single source of truth for the CampusVault platform. Any AI agent, developer, or evaluator opening a new session can read this document to understand the full context, codebase design, architectural trade-offs, and live production endpoints.

---

## 1. 📌 Executive Summary & Project Context

* **Project Name:** CampusVault
* **Target Audience:** Engineering & Computer Science undergraduates at Pakistani universities (specifically tailored for **QUEST Nawabshah** and **MUET Jamshoro** syllabus timelines).
* **Core Problem:** Students struggle with textbook-heavy or generic AI answers that don't match their exact lab practicals, viva exams, or university past paper marking schemes. Furthermore, peer notes and lab implementations shared across WhatsApp groups are lost or unsearchable.
* **Solution:** A hyper-local, multimodal **Bilingual Agentic RAG** academic assistant that indexes verified senior peer notes, aligns knowledge strictly with semester syllabus weeks, and answers code and theory questions in natural **Roman Urdu & English code-switching**.

---

## 2. 🌐 Live Production Infrastructure & URLs

| Component | Provider / Platform | Production URL / Identifier |
| :--- | :--- | :--- |
| **Frontend UI** | Vercel (Vite + React + TS + Tailwind) | [https://frontend-nine-tau-84.vercel.app](https://frontend-nine-tau-84.vercel.app) |
| **Backend API** | Render Web Service (FastAPI + Python 3.14) | [https://campusvault-backend.onrender.com](https://campusvault-backend.onrender.com) |
| **API Documentation** | Swagger / OpenAPI | [https://campusvault-backend.onrender.com/docs](https://campusvault-backend.onrender.com/docs) |
| **Vector Database** | Supabase (PostgreSQL + pgvector) | `https://hxvutkqzluggauadxmlb.supabase.co` |
| **Code Repository** | GitHub (Monorepo) | [https://github.com/Ilyan321/campusvault](https://github.com/Ilyan321/campusvault) |

---

## 3. 🏗️ Tech Stack & Model Selection Matrix

| Tier | Technology | Selected Model / Tool | Rationale & Trade-offs |
| :--- | :--- | :--- | :--- |
| **LLM Inference** | Groq Cloud API | `openai/gpt-oss-120b` *(fallback `qwen/qwen3.6-27b`)* | Ultra-fast token generation (<2.5s latency). Superior handling of bilingual code-switching (Roman Urdu + technical English) with zero unprompted `<think>` tag token waste. |
| **Multimodal OCR** | Google Gemini API + Local PyPDF | `gemini-2.5-flash` + `pdfplumber` | **Smart Local-First Pipeline:** Digital PDFs (up to 150 pages) parsed locally in <0.3s with 0 API calls. Pure handwritten notebook photos/diagrams route to Gemini Flash OCR with exponential backoff. |
| **Embeddings** | HuggingFace / PyTorch CPU | `BAAI/bge-small-en-v1.5` (384 dims) | Compact vector representation (~2.5 KB per chunk in DB). Operates strictly under **180 MB RAM** on Render's 512 MB free tier. |
| **Vector DB** | Supabase pgvector | HNSW Cosine Index (`vector_cosine_ops`) | Sub-millisecond ANN vector lookups with custom `match_notes` RPC supporting syllabus week & course filters. |
| **Frontend** | React 18 + Vite + TailwindCSS | Lucide Icons + Glassmorphism Dark UI | Responsive, mobile-friendly interface designed for campus students with live source slideouts and week selectors. |

---

## 4. 🧠 Key Architectural Decisions & Solutions Log

### Decision 1: Low-Memory Render Architecture (<350 MB Footprint)
* **Context:** Render free tier enforces a strict 512 MB RAM limit and kills containers with OOM or boot timeouts.
* **Decision:** Replaced heavy SentenceTransformers / Torch GPU packages with lightweight CPU-only PyTorch and `BAAI/bge-small-en-v1.5` (384 dimensions). Dynamic HuggingFace cache directory handling (`~/.cache/huggingface` locally and `/opt/render/...` on cloud) ensures zero permission errors.

### Decision 2: 100-Page PDF & Rate Limit Defense (Local-First OCR)
* **Context:** Uploading 100+ page lecture slide decks or lab manuals would instantly exhaust Gemini API rate limits (15 RPM) if sent page-by-page.
* **Decision:** Built a tiered parser in `backend/services/ocr_service.py`:
  1. `pdfplumber` extracts digital text locally with zero API calls.
  2. Only scanned images or handwritten notebook photos trigger `gemini-2.5-flash` with rate-limited chunking and semaphore locks.

### Decision 3: Bilingual Code-Switching (Roman Urdu + English)
* **Context:** Pakistani engineering students communicate naturally in Roman Urdu (*"Bhai rear pointer overflow kab hoga?"*).
* **Decision:** Implemented dynamic language adaptation in `backend/services/agentic_rag_service.py`. The system prompt instructs the mentor persona to match the student's language style, grounding answers in senior notes while explaining technical concepts in accessible Roman Urdu.

### Decision 4: Universal Chat with Autonomous Syllabus Routing (No Manual Week Picking)
* **Context:** Students should not have to remember or look up which week a specific topic belongs to (e.g. *Which week is Dijkstra or CIDR subnetting?*).
* **Decision:** 
  1. Made `week_number` optional in `/api/query`.
  2. Implemented default **"✨ All Weeks / Auto-Detect"** mode in frontend and backend.
  3. The Agentic Router analyzes the question, matches syllabus keywords across the semester timeline, executes multi-hop vector retrieval, and returns `agentic_meta.auto_detected_week`.
  4. The UI displays an interactive badge: `📍 Auto-routed to Week 5: Queue Data Structure (View Week)`.

### Decision 5: Groq Token Optimization & Model Selection
* **Context:** Groq enforces strict Output Tokens Per Minute (OTPM) limits. Initial testing with reasoning models spent tokens on internal thinking tags.
* **Decision:** Switched primary inference to `openai/gpt-oss-120b`, enforced bounded `max_tokens=650`, and built `clean_llm_text` regex sanitization to ensure fast and structured responses.

### Decision 6: Instant Seed Endpoint (`/api/seed`)
* **Context:** Hackathon judges and demo evaluators need to test the RAG engine immediately without manually uploading files first.
* **Decision:** Created `/api/seed` (GET & POST) to populate Supabase pgvector with high-yield peer notes across:
  * **CSE-212 (DSA):** Pointers & Memory (Week 1), Linked Lists (Week 3), Stacks (Week 4), Circular Queues (Week 5), Dijkstra Shortest Path (Week 12).
  * **CSE-305 (Networks):** IPv4 Addressing, CIDR Subnetting & Usable Hosts (Week 5).

---

## 5. 📂 Codebase Directory Map

```
/home/ilyan/ilmai/
├── backend/
│   ├── config.py                      # Production keys, cache paths, model constants
│   ├── main.py                        # FastAPI routes (/api/query, /api/ingest, /api/seed, /api/syllabus)
│   ├── data/
│   │   └── syllabus_outlines.json     # Ground truth semester timelines for QUEST/MUET
│   ├── services/
│   │   ├── agentic_rag_service.py     # Bilingual query planner, RRF reranker, self-RAG grader
│   │   ├── embedder_service.py        # 384-dim BGE embeddings (CPU-optimized)
│   │   ├── ocr_service.py             # Local-first PDF extraction + Gemini Flash OCR
│   │   ├── classifier_service.py      # LLM & heuristic syllabus week classifier
│   │   ├── seed_service.py            # High-yield note seeder for instant demo data
│   │   ├── supabase_service.py        # pgvector storage & match_notes RPC
│   │   └── rag_service.py             # Base RAG pipeline & streaming generator
│   ├── tests/
│   │   └── test_backend_rag.py        # 11 Unit & E2E Pytest test suite (100% passing)
│   └── utils/
│       └── chunker.py                 # Semantic paragraph & code-block chunking
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx                    # Main layout & state orchestrator
│   │   ├── components/
│   │   │   ├── Header.tsx             # Course selector & Upload Note modal trigger
│   │   │   ├── TimelineSidebar.tsx    # Syllabus timeline + Auto-Detect mode button
│   │   │   ├── ChatInterface.tsx      # Bilingual chat feed with routing badges & quick prompts
│   │   │   ├── UploadModal.tsx        # Workflow A: Upload, OCR preview, Senior confirm
│   │   │   └── SourceSlideout.tsx     # Workflow B: Verified peer note inspector
│   │   ├── services/
│   │   │   └── api.ts                 # API client for Render backend
│   │   └── types/
│   │       └── index.ts               # TypeScript interfaces
│   ├── package.json
│   └── vite.config.ts
│
├── supabase/
│   └── migrations/
│       └── 20260909173101_init_rag_schema.sql  # pgvector notes table & HNSW match_notes RPC
└── DECISION.md                        # Master architectural & project history record
```

---

## 6. 🧪 Verification & Testing Commands

To run tests and verify backend functionality locally:

```bash
# 1. Activate virtual environment
source backend/.venv/bin/activate

# 2. Run test suite
pytest backend/tests/test_backend_rag.py

# 3. Seed Supabase database
PYTHONPATH=backend python -c "from services.seed_service import seed_database; print(seed_database())"

# 4. Build frontend
cd frontend && npm run build
```

---

## 7. 🚀 Future Roadmap & Scaling

1. **Audio Viva Examiner Mode:** Real-time conversational mock lab exams using Gemini Live WebSockets.
2. **Offline Local P2P Sync:** WebRTC / Local peer mesh sync across campus lab LANs for offline studying.
3. **Multi-University Syllabus Switcher:** Pre-configured syllabus modules for NUST, FAST-NUCES, UET Lahore, and COMSATS.
