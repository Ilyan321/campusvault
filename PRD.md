# 📚 CampusVault
### *Your Campus. Your Notes. Your AI.*

---

> **Product Requirements Document — Production & Hackathon Edition**
>
> | Field | Detail |
> |---|---|
> | **Project Name** | **CampusVault** (formerly CampusLore) |
> | **Engineering Team** | Shahzaib Ali, Ali Hussain, Aqsa Sarfaraz, Arfa Rehman, Zainab Faiz, Warda Nadeem |
> | **Lead / Architect** | Ilyan Khan |
> | **Version** | 2.0.0 — Production Hackathon Release |
> | **Target Event** | Pak Angels Generative & Agentic AI Training — Cohort 11 Mid-Term Hackathon |
> | **Live Deployments** | • Frontend: [frontend-nine-tau-84.vercel.app](https://frontend-nine-tau-84.vercel.app) / [campusvault.ilyankhan.tech](https://campusvault.ilyankhan.tech)<br>• Backend: [campusvault-backend.onrender.com](https://campusvault-backend.onrender.com) |
> | **Target Users** | Engineering & CS Students (QUEST, MUET, FAST, NUST, UET) |
> | **Budget & Cost Model** | $0 — Local FastEmbed ONNX + Free Cloud Tier Infrastructure |
> | **Document Status** | ✅ Active & Verified |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement & Crisis](#2-problem-statement--crisis)
3. [Target Users & Personas](#3-target-users--personas)
4. [Agentic RAG Architecture & Core Innovations](#4-agentic-rag-architecture--core-innovations)
5. [Core Feature Matrix & Scope](#5-core-feature-matrix--scope)
6. [End-to-End User Workflows](#6-end-to-end-user-workflows)
7. [Full-Stack Technical Architecture](#7-full-stack-technical-architecture)
8. [Curriculum & Syllabus Strategy](#8-curriculum--syllabus-strategy)
9. [Cost, Performance & Rate-Limit Mitigation](#9-cost-performance--rate-limit-mitigation)
10. [Success Metrics & Hackathon Rubric Alignment](#10-success-metrics--hackathon-rubric-alignment)
11. [Future Roadmap (Post-Hackathon)](#11-future-roadmap-post-hackathon)

---

## 1. Executive Summary

University engineering students in Pakistan and across emerging tech hubs face a systemic academic challenge: **the critical knowledge required to pass lab exams, viva assessments, and final papers does not reside in generic textbook definitions**. It lives inside verified senior notebooks, past paper solution derivations, whiteboard snapshots from lab sessions, and shared WhatsApp drive links that vanish after graduation.

**CampusVault** is a hyper-local, production-grade **Agentic RAG Knowledge Engine** designed to solve this crisis. 

Unlike basic, naive RAG systems that perform static keyword matching, CampusVault introduces:
1. **Autonomous Query Routing & Syllabus Planning:** Analyzes student intent, detects subjects across a 16-week semester timeline, and selects targeted retrieval paths.
2. **Deterministic Confidence Gate (≥0.65 threshold):** Prevents hallucinations by enforcing peer-provenance and honestly falling back to a disclaimed *"General AI Mode"* when verified notes are absent.
3. **AST-Aware Chunking Engine:** Protects code functions (Python, C++) and multi-step LaTeX equations from being bisected across chunk boundaries.
4. **Zero-Cost Local Ingestion:** Employs FastEmbed ONNX runtime locally for zero embedding API expenses, sub-20ms database queries, and sub-500ms Server-Sent Events (SSE) token streaming.

---

## 2. Problem Statement & Crisis

### 2.1 Generic AI Hallucinations
Standard LLMs like ChatGPT fail students during high-stakes exam prep:
- They invent non-existent formulas, hallucinate wrong algorithm traces, and generate code that fails on university lab compiler environments.
- They lack alignment with university syllabi, professor marking schemes, and localized exam rubrics.
- They offer zero verifiable citations, leaving students unable to audit the correctness of an answer.

### 2.2 Severe Knowledge Fragmentation
- Over 400+ pages of unstructured lecture slides, handwritten notebook scans, and solved papers disappear across unindexed drives and graduation cycles every year.
- At 3:00 AM before an exam, students waste hours hunting for one derivation or formula across disorganized chats rather than studying.

### 2.3 Naive RAG Limitations
- Standard naive RAG uses arbitrary character-count chunking (e.g. 500 characters) that splits code functions and mathematical derivations in half.
- Naive RAG blindly searches vector stores and forces low-similarity, irrelevant chunks into the prompt, guaranteeing hallucinations.

---

## 3. Target Users & Personas

### Persona A — The Senior Contributor ("Zain / Haris")
* **Profile:** Final-year Computer Systems / Software Engineering student.
* **Pain Point:** Bombarded with repeated WhatsApp requests from 30+ juniors asking for the same lab manuals, handwritten notes, and solved past papers.
* **Goal:** Drag and drop all notes once into a self-indexing repository with automated syllabus tagging and give back to the department.

### Persona B — The Junior Exam Candidate ("Ayesha / Bilal")
* **Profile:** 2nd-year Engineering student facing a high-stakes exam or lab viva in 48 hours.
* **Pain Point:** Textbooks are too dense, slides lack solved examples, and generic AI gives generic answers that lose marks.
* **Goal:** Ask questions in natural bilingual phrasing (*Roman Urdu + English code-switching*) and get step-by-step explanations grounded in real senior notes with instant KaTeX math equations.

---

## 4. Agentic RAG Architecture & Core Innovations

CampusVault is built on three architectural pillars that distinguish it from naive RAG:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      CAMPUSVAULT AGENTIC RAG ENGINE                     │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│  AGENTIC ROUTER  │       │ CONFIDENCE GATE  │       │ AST-AWARE CHUNKER│
│ Classifies topic │       │ Enforces ≥0.65   │       │ Protects code &  │
│ & 16-week ground │       │ similarity barrier│      │ LaTeX equation   │
│ syllabus intent  │       │ Honest fallback  │       │ syntax boundaries│
└──────────────────┘       └──────────────────┘       └──────────────────┘
```

1. **Agentic Query Router:** Decomposes student prompts, dynamically classifies the subject domain (OS, Networks, DSA, DBMS, DLD, Math), maps the 16-week semester timeline, and formulates multi-hop retrieval queries.
2. **Strict Confidence Gate (0.65 Threshold):** Every retrieved chunk is scored. If the cosine similarity is below 0.65, the system abstains from claiming peer authority and explicitly alerts the student: *"Operating in General AI Mode."*
3. **AST-Aware & Semantic Chunker:** Parses source code with Abstract Syntax Trees (preserving whole functions and class definitions) and protects `$$ ... $$` LaTeX blocks so mathematical derivations remain intact.

---

## 5. Core Feature Matrix & Scope

### 5.1 In-Scope (Production Hackathon Scope)

| Feature Module | Priority | Technical Specification |
|---|---|---|
| **Autonomous Subject & Week Routing** | P0 | Automatic syllabus alignment without requiring manual week selection |
| **Bilingual Query Processing** | P0 | Natural Roman Urdu & English code-switching (*"Bhai rear pointer kab reset hoga?"*) |
| **Zero-Cost ONNX Vector Embeddings** | P0 | FastEmbed `BAAI/bge-small-en-v1.5` (384-dim dense vectors) executed locally on CPU |
| **High-Yield Exam Launchpad** | P0 | Pre-loaded, one-click curated exam queries across 6 engineering branches |
| **Sub-500ms Token Streaming** | P0 | Server-Sent Events (SSE) via Groq Llama 3.3 70B |
| **Native KaTeX Math Engine** | P0 | Client-side rendering for matrices, truth tables, subnet calculations, and LaTeX |
| **Peer Provenance & Source Inspector** | P1 | Slide-out panel showing exact senior note chunk, author, and similarity score |
| **Local-First & Multimodal Ingestion** | P1 | `pdfplumber` for zero-cost digital extraction + Gemini Flash OCR for handwritten scans |

### 5.2 Covered Engineering Subjects

1. **Operating Systems (CSE-311):** Process Scheduling, Deadlocks, Paging & Virtual Memory.
2. **Computer Networks (CSE-305):** OSI/TCP-IP, IPv4/IPv6, CIDR Subnetting, Routing Protocols.
3. **Data Structures & Algorithms (CSE-212):** Stacks, Circular Queues, Trees, Graphs, Dijkstra.
4. **Database Management Systems (CSE-220):** Relational Algebra, Normalization (1NF to BCNF), SQL.
5. **Digital Logic Design (CSE-110):** K-Maps, Boolean Algebra, Multiplexers, Flip-Flops.
6. **Applied Mathematics & Linear Algebra (MTH-108):** Matrices, Eigenvalues, Calculus Derivations.

---

## 6. End-to-End User Workflows

### Workflow A — Senior Ingestion & Automated Tagging
1. Senior drags and drops notes (`.pdf`, `.png`, `.jpg`, `.py`, `.cpp`, `.md`).
2. **Local-First Tier:** Digital PDFs (up to 150 pages) parse locally in `<0.3s` with zero API calls. Handwritten images route to Gemini Flash OCR.
3. **AST Chunker:** Splits text along semantic and AST syntactic boundaries.
4. **Classifier Service:** Groq/Heuristic maps content to course ID and syllabus week number.
5. **FastEmbed ONNX:** Generates 384-dim dense vectors locally.
6. **Supabase Save:** Writes chunks to `notes` table with `pgvector` HNSW index.

### Workflow B — Junior Query & Grounded Tutoring
1. Student submits question in English or Roman Urdu via Web / Mobile client.
2. **Router:** Classifies intent and curriculum week.
3. **pgvector Hybrid Search:** Cosine similarity search executes in `<20ms`.
4. **Confidence Gate:** Evaluates top chunks against the `0.65` barrier.
5. **Groq Llama 3.3 70B:** Streams tokens with peer citations and KaTeX equations in `<500ms`.

---

## 7. Full-Stack Technical Architecture

```
┌────────────────────────────────────────────────────────┐
│                   React 18 Frontend                    │
│      (TypeScript + Vite + Tailwind CSS + KaTeX)        │
│          Hosted on Vercel Edge Global CDN              │
└──────────────────────────┬─────────────────────────────┘
                           │ HTTPS / SSE Stream
┌──────────────────────────▼─────────────────────────────┐
│                 FastAPI Async Engine                   │
│        (Python 3.14 on Render Web Service)             │
├────────────────────────────────────────────────────────┤
│  • Agentic Query Router & Syllabus Planner             │
│  • AST-Aware & Semantic Chunker                        │
│  • Local FastEmbed ONNX Runtime (384-dim BGE Vectors)  │
│  • Confidence Gate (0.65 Similarity Guardrail)         │
│  • Local-First pdfplumber + Gemini Flash OCR           │
└──────────────┬──────────────────────────┬──────────────┘
               │                          │
       SQL / pgvector RPC           Groq Cloud API
               │                          │
┌──────────────▼─────────────┐   ┌────────▼──────────────┐
│  Supabase (PostgreSQL)     │   │  Groq Llama 3.3 70B   │
│  • HNSW Cosine Index       │   │  • Low-latency LPU    │
│  • Sub-20ms vector lookups │   │  • SSE token stream   │
└────────────────────────────┘   └───────────────────────┘
```

---

## 8. Curriculum & Syllabus Strategy

CampusVault uses an authoritative `syllabus.json` ontology mapping all 16 semester weeks across foundational engineering subjects.

```json
{
  "course_id": "CSE-305",
  "course_name": "Computer Networks",
  "weeks": [
    {
      "week_number": 5,
      "topic": "IPv4 Addressing & CIDR Subnetting",
      "keywords": ["CIDR", "subnet mask", "slash notation", "usable hosts", "broadcast IP"]
    }
  ]
}
```

* **Auto-Routing:** When a student asks about *"CIDR /26 host calculation"*, the router automatically identifies `CSE-305 Week 5` without manual user intervention.

---

## 9. Cost, Performance & Rate-Limit Mitigation

| Vector / Component | Traditional Approach | CampusVault Zero-Cost Architecture |
|---|---|---|
| **Embedding Cost** | $0.0001 per 1k tokens (OpenAI) | **$0.00** (Local FastEmbed ONNX in-process) |
| **Embedding Latency** | 200–500ms network round-trip | **<15ms** local CPU execution |
| **PDF Ingestion** | Full OCR API on every page ($$) | **Local PyPDF first (<0.3s)**; OCR only for scans |
| **Database Latency** | 100–300ms on external vector DB | **<20ms** via PostgreSQL `pgvector` HNSW |
| **Inference Speed** | 3–6s latency on standard cloud | **<500ms TTFT** on Groq LPU Llama 3.3 70B |
| **RAM Footprint** | >1.2 GB (PyTorch GPU / Spacy) | **Strictly <350 MB** (Render Free Tier Safe) |

---

## 10. Success Metrics & Hackathon Rubric Alignment

| Rubric Dimension | Hackathon Target | CampusVault Delivery | Status |
|---|---|---|:---:|
| **Technical Innovation** | Beyond basic RAG | Agentic Routing + 0.65 Confidence Gate + AST Chunking | ✅ Exceeded |
| **System Performance** | Fast & responsive | Sub-500ms TTFT, <20ms vector search | ✅ Exceeded |
| **Cost & Scalability** | Sustainable architecture | $0 embedding expense, zero external GPU burden | ✅ Exceeded |
| **Academic Impact** | Real student utility | Grounded peer notes + KaTeX math + Roman Urdu support | ✅ Exceeded |
| **Deployment Status** | Live working URL | Deployed on Vercel + Render + Supabase | ✅ Exceeded |

---

## 11. Future Roadmap (Post-Hackathon)

1. **Audio Viva Examiner Mode:** Real-time conversational mock lab exams using Gemini Live WebSockets.
2. **Offline Local P2P Sync:** WebRTC mesh sync for campus computer lab networks during offline study sessions.
3. **Multi-University Expansion:** Pre-configured syllabus modules for NUST, FAST-NUCES, UET Lahore, and COMSATS.

---

*CampusVault — Engineered by students, for students. Powered by Agentic RAG.*
