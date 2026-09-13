import logging
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, PlainTextResponse
from pydantic import BaseModel

from config import SUPABASE_URL, GROQ_API_KEY
from services.ocr_service import extract_text_from_document
from services.classifier_service import classify_syllabus_week, load_syllabus
from services.embedder_service import get_embeddings_batch
from services.supabase_service import upload_file_to_storage, insert_note_chunks, get_supabase_client
from services.rag_service import execute_rag_pipeline
from services.agentic_rag_service import run_agentic_rag, stream_agentic_rag
from utils.chunker import semantic_chunk

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("campusvault.api")

app = FastAPI(
    title="CampusVault RAG API",
    description="Hyper-reliable, low-memory RAG backend for university engineering notes",
    version="1.0.0"
)

# Enable CORS for React frontend on Vercel / localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConfirmIngestRequest(BaseModel):
    file_name: str
    file_url: Optional[str] = None
    course_id: Optional[str] = "General"
    week_number: Optional[int] = None
    topic: Optional[str] = "General Academic"
    content: str

class QueryRequest(BaseModel):
    query: str
    week_number: Optional[int] = None
    course_id: Optional[str] = None
    match_threshold: Optional[float] = 0.25
    match_count: Optional[int] = 4
    history: Optional[List[dict]] = None

@app.get("/")
def root():
    return {
        "app": "CampusVault API",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "database_connected": bool(SUPABASE_URL),
        "groq_configured": bool(GROQ_API_KEY)
    }

@app.get("/api/syllabus")
def get_syllabus():
    """Returns the university syllabus timelines for all courses."""
    return load_syllabus()

@app.post("/api/ingest/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    course_id: Optional[str] = Form(None)
):
    """
    Step 1 of Workflow A: Receives file, extracts text instantly via pypdf / OCR,
    and runs fast AI syllabus classification. Returns parsed preview for confirmation in <1s.
    """
    try:
        content_bytes = await file.read()
        file_name = file.filename or "uploaded_file"
        mime_type = file.content_type or "application/octet-stream"

        # 1. High-Speed Document Text Extraction
        extracted_text = extract_text_from_document(content_bytes, file_name, mime_type)
        
        # 2. Fast AI Syllabus Classifier
        classification = classify_syllabus_week(extracted_text, course_id)

        return {
            "file_name": file_name,
            "file_url": f"/uploads/{file_name}",
            "extracted_text": extracted_text,
            "preview": extracted_text[:400] + ("..." if len(extracted_text) > 400 else ""),
            "classification": classification
        }
    except Exception as e:
        logger.error(f"Error during document analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/ingest/confirm")
def confirm_ingestion(payload: ConfirmIngestRequest):
    """
    Step 2 of Workflow A: Senior confirms or customizes the topic and optional syllabus week.
    Chunks text using AST/recursive chunking, computes 384-dim embeddings via FastEmbed, and stores into Supabase pgvector.
    """
    try:
        # 1. AST / Boundary-Aware Semantic Chunking
        chunks = semantic_chunk(payload.content, max_chars=600, overlap=120)
        if not chunks:
            raise HTTPException(status_code=400, detail="Document content was empty.")

        # 2. Batch FastEmbed ONNX Generation
        embeddings = get_embeddings_batch(chunks)

        # 3. Prepare database records (Safely handling optional week_number as 0 if None)
        effective_week = payload.week_number if payload.week_number is not None else 0
        effective_course = payload.course_id or "General"
        effective_topic = payload.topic or "General Academic"

        records = []
        for idx, (chunk_text, emb) in enumerate(zip(chunks, embeddings)):
            records.append({
                "content": chunk_text,
                "embedding": emb,
                "file_url": payload.file_url,
                "file_name": payload.file_name,
                "course_id": effective_course,
                "week_number": effective_week,
                "topic": effective_topic,
                "chunk_index": idx,
                "metadata": {
                    "total_chunks": len(chunks),
                    "chunk_size": len(chunk_text)
                }
            })

        # 4. Insert into Supabase
        inserted = insert_note_chunks(records)
        week_label = f"Week {effective_week}" if effective_week > 0 else "General Tag"
        return {
            "success": True,
            "message": f"Successfully indexed {len(records)} note chunks for {effective_course} ({effective_topic} - {week_label})",
            "inserted_count": len(inserted) if inserted else len(records)
        }
    except Exception as e:
        logger.error(f"Error during note confirmation: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@app.post("/api/query")
def query_rag(payload: QueryRequest):
    """
    Bilingual Agentic RAG: Decomposes query, executes multi-hop vector retrieval,
    grades relevance, and synthesizes bilingual (English / Roman Urdu) grounded answer.
    """
    try:
        result = run_agentic_rag(
            query=payload.query,
            week_number=payload.week_number,
            course_id=payload.course_id,
            history=payload.history
        )
        return result
    except Exception as e:
        logger.error(f"Error executing Agentic RAG query: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.post("/api/query/stream")
async def query_rag_stream(payload: QueryRequest):
    """
    Streaming query endpoint with Server-Sent Events (SSE) for real-time bilingual token rendering.
    """
    return StreamingResponse(
        stream_agentic_rag(payload.query, payload.week_number, payload.course_id, history=payload.history),
        media_type="text/event-stream"
    )


@app.get("/api/seed")
@app.post("/api/seed")
def seed_notes():
    """
    Seeds Supabase with high-yield university peer notes for live demos.
    """
    from services.seed_service import seed_database
    return seed_database()

@app.get("/api/notes")
def get_notes_for_week(
    course_id: str = Query("CSE-212"),
    week_number: int = Query(...)
):
    """Lists distinct uploaded note files for the selected week."""
    client = get_supabase_client()
    if not client:
        return []
    try:
        response = client.table("notes").select("file_name, file_url, topic, created_at").eq("course_id", course_id).eq("week_number", week_number).execute()
        # Deduplicate by file_name
        seen = set()
        deduped = []
        for row in response.data or []:
            fn = row.get("file_name")
            if fn and fn not in seen:
                seen.add(fn)
                deduped.append(row)
        return deduped
    except Exception as e:
        logger.error(f"Error fetching notes: {e}")
        return []

@app.get("/api/notes/content")
def get_note_full_content(file_name: str = Query(...)):
    """
    Returns the complete text content and metadata for a note file.
    Reconstructs from seed repository or database chunk records.
    """
    from services.supabase_service import get_full_note_by_filename
    note = get_full_note_by_filename(file_name)
    if not note:
        raise HTTPException(status_code=404, detail=f"Note file '{file_name}' not found.")
    return note

@app.get("/api/notes/raw/{file_name}")
def get_note_raw_file(file_name: str):
    """
    Returns the raw plain text file content for direct viewing or downloading.
    """
    from services.supabase_service import get_full_note_by_filename
    note = get_full_note_by_filename(file_name)
    if not note:
        raise HTTPException(status_code=404, detail=f"Note file '{file_name}' not found.")
    return PlainTextResponse(content=note.get("content", ""), media_type="text/plain; charset=utf-8")
