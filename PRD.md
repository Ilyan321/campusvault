# CampusVault — Product Requirements Document (PRD)

**Document Version:** 2.0  
**Status:** Active  
**Last Updated:** September 2026  
**Owner:** CampusVault Team

---

## 1) Product Overview

CampusVault is an agentic, syllabus-aware academic RAG platform for engineering students.  
It converts scattered peer notes (PDFs, images, code, markdown, text) into a grounded knowledge system where students can:

- Ask natural-language questions (English + Roman Urdu style)
- Get context-grounded answers with source attribution
- Explore course/week-aligned knowledge for exam preparation
- Upload and index senior notes in a guided flow

CampusVault is built to reduce hallucinated academic help and replace fragmented campus knowledge sharing with a persistent, searchable, explainable system.

---

## 2) Problem Statement

Students in technical programs face three recurring issues:

1. **Knowledge fragmentation**
   - High-value exam content is spread across WhatsApp, private drives, screenshots, and personal notebooks.
   - Materials are hard to discover and often lost.

2. **Lack of local academic grounding**
   - Generic AI tools provide broad answers not aligned with local course pacing or exam expectations.
   - Students need answers mapped to course topics and syllabus week context.

3. **Poor support for multimodal study material**
   - Practical knowledge is often in scans, handwritten notes, and code snippets.
   - Typical search systems are weak at extracting and indexing these formats correctly.

---

## 3) Goals and Non-Goals

### 3.1 Goals

- Deliver grounded academic answers with visible source references.
- Support autonomous routing across multiple courses and weeks.
- Support ingestion of multimodal files with fast processing and manual confirmation.
- Keep response and ingestion latency practical for student workflows.
- Run efficiently on free-tier-friendly infrastructure.

### 3.2 Non-Goals (Current Scope)

- Full identity/role management and institutional SSO.
- Native mobile applications.
- Faculty-grade analytics dashboards.
- Real-time collaborative note editing.
- Audio/video ingestion pipeline as a primary channel.

---

## 4) Target Users

### 4.1 Senior Contributor
- Uploads notes/code/slides once
- Optionally aligns to syllabus week
- Expects low-friction indexing and reuse by juniors

### 4.2 Junior Learner
- Asks exam-focused queries in natural phrasing
- Needs clear stepwise explanations with code/math formatting
- Needs “show me source” trust layer

### 4.3 Hackathon/Judge Evaluator
- Needs immediate usable demo state
- Uses seed endpoint and predefined tracks to validate value quickly

---

## 5) Product Scope (Current Repository Implementation)

### 5.1 Core Capabilities

- **Agentic Query Pipeline**
  - Query analysis and expansion
  - Auto-detection of likely course/week/topic
  - Multi-turn context usage (recent conversation turns)
  - Hybrid retrieval and relevance grading

- **Hybrid Retrieval**
  - Dense semantic retrieval via pgvector
  - Lexical retrieval via text matching
  - Reciprocal Rank Fusion (RRF) for combined ranking

- **Confidence/Relevance Behavior**
  - Retrieval relevance grading (HIGH / PARTIAL / LOW)
  - Week expansion fallback when initial relevance is low
  - General/parametric response mode when grounded retrieval is unavailable

- **Multimodal Ingestion**
  - Two-step flow: analyze then confirm
  - Local-first extraction for digital PDFs and text/code files
  - Bounded OCR for scanned pages/images
  - AST/boundary-aware chunking before embeddings

- **Source Traceability**
  - Answer includes source chunk metadata
  - Frontend source slideout to inspect referenced material
  - Raw note and reconstructed note content endpoints

---

## 6) User Workflows

### 6.1 Workflow A — Upload and Index (Senior)

1. User opens Upload modal.
2. User drags/drops or selects a file (`pdf/png/jpg/webp/py/cpp/c/txt/md`).
3. Frontend calls `POST /api/ingest/analyze`.
4. Backend:
   - Extracts text (local parser first; OCR fallback where needed)
   - Runs syllabus classification
   - Returns extracted preview + classification confidence
5. User reviews/edits:
   - Subject tag
   - Topic tag
   - Optional syllabus week alignment
6. Frontend calls `POST /api/ingest/confirm`.
7. Backend:
   - Semantic/AST chunking
   - 384-dim embedding generation
   - Batch insertion into Supabase `notes`
8. UI confirms material is indexed and ready for grounding.

### 6.2 Workflow B — Ask and Learn (Junior)

1. User asks question in chat (free scope or selected week/course scope).
2. Frontend attempts streaming request to `POST /api/query/stream`.
3. Backend:
   - Plans route (course/week/topic + expanded subqueries)
   - Executes dense + lexical retrieval with RRF
   - Grades relevance, builds synthesis prompt, streams output
4. Frontend renders live markdown response with math/code formatting.
5. If streaming fails, frontend falls back to `POST /api/query`.
6. User opens source panel for grounded references.

### 6.3 Workflow C — Demo Bootstrapping

1. Evaluator calls `POST /api/seed` or `GET /api/seed`.
2. Backend inserts predefined high-yield note content.
3. System becomes immediately queryable for demonstrations.

---

## 7) Functional Requirements

### FR-01: Syllabus Retrieval
- System shall expose syllabus catalog via `GET /api/syllabus`.
- Must include courses with week/topic/keywords.

### FR-02: Document Analysis
- System shall accept uploaded file and return:
  - file metadata
  - extracted content
  - preview
  - classification (`course_id`, `assigned_week`, `topic`, `confidence`, `reasoning`)

### FR-03: Ingestion Confirmation
- System shall index confirmed document into vector database with:
  - chunk text
  - embedding
  - file metadata
  - course/week/topic metadata
  - chunk index

### FR-04: Query (Synchronous)
- System shall answer with:
  - generated answer
  - detected/selected scope data
  - sources
  - agentic metadata

### FR-05: Query (Streaming SSE)
- System shall stream incremental token events.
- System shall send metadata event containing routing/source context.

### FR-06: Source Access
- System shall provide:
  - week-specific note listing (`GET /api/notes`)
  - full stitched content by filename (`GET /api/notes/content`)
  - raw text content endpoint (`GET /api/notes/raw/{file_name}`)

### FR-07: Seed Data
- System shall provide a deterministic seed flow for immediate demo readiness.

### FR-08: Session Continuity (Frontend)
- Frontend shall persist chat sessions in local storage.
- User can create, switch, delete, and clear sessions.

---

## 8) Non-Functional Requirements

### NFR-01: Performance
- Query responses should feel interactive (stream-first UX).
- Ingestion analysis should return quick preview for user confirmation.

### NFR-02: Reliability
- Network retry with exponential backoff for key frontend API calls.
- Sync query fallback if streaming request fails.
- Graceful user-facing errors for rate-limit/connectivity conditions.

### NFR-03: Resource Efficiency
- Embedding model fixed to lightweight 384-dim configuration.
- Local-first extraction to reduce OCR API usage/cost.

### NFR-04: Explainability
- Source references must be attached when grounded context exists.
- UI must allow source inspection for trust and auditability.

### NFR-05: Security Baseline
- No secrets should be exposed in documentation or UI responses.
- Input files and user queries must be handled without unsafe execution paths.

---

## 9) System Architecture (As Implemented)

### 9.1 Frontend
- React + TypeScript + Vite + Tailwind
- Main modules:
  - `App.tsx` (state orchestration)
  - `ChatInterface.tsx`
  - `TimelineSidebar.tsx`
  - `UploadModal.tsx`
  - `SourceSlideout.tsx`
  - `HistoryDrawer.tsx`

### 9.2 Backend
- FastAPI service with endpoints for:
  - health
  - syllabus
  - ingestion analyze/confirm
  - query sync/stream
  - seed
  - note retrieval endpoints

### 9.3 Retrieval and Reasoning Layer
- Query planning and expansion
- Dense retrieval + lexical retrieval
- RRF fusion
- Retrieval relevance grading
- Prompt synthesis with recent conversation memory

### 9.4 Data Layer
- Supabase PostgreSQL with pgvector
- `notes` table with vector(384), week/course/topic metadata
- `match_notes` RPC for filtered cosine similarity search
- HNSW vector index + composite course/week index

---

## 10) Data Model Summary

### 10.1 Core Notes Record Fields
- `id` (uuid)
- `content` (chunk text)
- `embedding` (vector(384))
- `file_url`, `file_name`
- `week_number`, `course_id`, `topic`
- `chunk_index`
- `metadata` (jsonb)
- `created_at`

### 10.2 Syllabus Source Structure
- Course-level object:
  - `course_id`
  - `course_name`
  - `department`
  - `syllabus_timeline[]`
- Week-level object:
  - `week`
  - `core_topic`
  - `grounding_keywords[]`

---

## 11) Course Coverage in Current Scope

Current syllabus and UI defaults cover these subjects:

1. CSE-212 — Data Structures & Algorithms  
2. CSE-305 — Data & Computer Networks  
3. CSE-310 — Operating Systems  
4. CSE-315 — Database Systems & SQL  
5. CSE-204 — Digital Logic & Computer Architecture  
6. MATH-201 — Linear Algebra & Applied Mathematics

---

## 12) API Contract Overview

- `GET /health`
- `GET /api/syllabus`
- `POST /api/ingest/analyze`
- `POST /api/ingest/confirm`
- `POST /api/query`
- `POST /api/query/stream` (SSE)
- `GET|POST /api/seed`
- `GET /api/notes`
- `GET /api/notes/content`
- `GET /api/notes/raw/{file_name}`

---

## 13) UX and Interaction Requirements

- Must support both scoped learning (selected week/course) and universal mode.
- Must show clear system state while analyzing/indexing uploads.
- Must support inspectable source references in response flow.
- Must preserve chat continuity across reloads with local storage sessions.
- Must include high-yield starter prompts for fast onboarding.

---

## 14) Validation and Testing Requirements

Current repository includes backend tests validating:

- chunking behavior
- classifier behavior
- embedding dimensions and normalization assumptions
- API health and syllabus endpoints
- query endpoint behavior
- ingestion confirm flow
- streaming endpoint contract
- multi-turn query history behavior

PRD compliance should continue to require regression checks on these flows.

---

## 15) Risks and Mitigations

### Risk A: External model/API rate limits
- **Mitigation:** local-first extraction, bounded OCR scope, retry/fallback UX, optional cache patterns.

### Risk B: Weak retrieval for ambiguous queries
- **Mitigation:** query expansion, hybrid retrieval, relevance grading, adjacent-week retry.

### Risk C: Mismatched scope selection by user
- **Mitigation:** autonomous router + explicit “reset scope” + metadata routing feedback in UI.

### Risk D: Trust gap in AI responses
- **Mitigation:** source-linked answers + source inspector + visible grounded vs general mode behavior.

---

## 16) Release Readiness Checklist

- [ ] All ingestion endpoints stable under expected file types.
- [ ] Query streaming and sync fallback both operational.
- [ ] Source retrieval panel verified end-to-end.
- [ ] Seed flow works in clean environment.
- [ ] Syllabus data validated for all active courses.
- [ ] Backend test suite passing in CI/local.
- [ ] Frontend production build successful.

---

## 17) Roadmap (Post-Current Scope)

- Stronger auth and role-based workflows (student/senior/faculty).
- Expanded ingestion formats (audio/video transcription paths).
- Institution-specific syllabus packs and onboarding flows.
- Advanced analytics for content quality and topic coverage.
- Improved offline/low-connectivity operation modes.

---

## 18) Product Positioning Statement

CampusVault is a grounded academic assistant focused on engineering exam readiness, built around real peer material, transparent sources, and syllabus-aware retrieval—designed for practical study outcomes instead of generic AI responses.
