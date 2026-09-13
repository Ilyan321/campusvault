import logging
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_SERVICE_KEY

logger = logging.getLogger("campusvault.supabase")

_client: Optional[Client] = None

def get_supabase_client() -> Optional[Client]:
    global _client
    if _client is None:
        if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
            logger.warning("SUPABASE_URL or SUPABASE_SERVICE_KEY not set in environment.")
            return None
        try:
            _client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            return None
    return _client

def upload_file_to_storage(bucket_name: str, file_path: str, file_bytes: bytes, content_type: str) -> str:
    """
    Uploads a file to Supabase storage bucket and returns the public URL.
    """
    client = get_supabase_client()
    if not client:
        return f"/storage/{bucket_name}/{file_path}"
    try:
        client.storage.from_(bucket_name).upload(
            path=file_path,
            file=file_bytes,
            file_options={"content-type": content_type, "upsert": "true"}
        )
        public_url_resp = client.storage.from_(bucket_name).get_public_url(file_path)
        return public_url_resp
    except Exception as e:
        logger.error(f"Error uploading file to Supabase storage: {e}")
        return f"/storage/{bucket_name}/{file_path}"

def insert_note_chunks(chunks: List[Dict[str, Any]], batch_size: int = 25) -> List[Dict[str, Any]]:
    """
    Inserts note chunks into the 'notes' table in safe batches to prevent payload/timeout limits.
    """
    client = get_supabase_client()
    if not client:
        logger.info(f"Supabase not connected. Stored {len(chunks)} chunks in local memory.")
        return chunks
    try:
        all_inserted = []
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            response = client.table("notes").insert(batch).execute()
            if response.data:
                all_inserted.extend(response.data)
        return all_inserted
    except Exception as e:
        logger.error(f"Error inserting note chunks: {e}")
        raise e

def search_similar_notes(
    query_embedding: List[float],
    filter_week: Optional[int] = None,
    filter_course: Optional[str] = None,
    match_threshold: float = 0.35,
    match_count: int = 5
) -> List[Dict[str, Any]]:
    """
    Calls the Supabase 'match_notes' RPC function with pgvector HNSW search.
    """
    client = get_supabase_client()
    if not client:
        return []
    try:
        params = {
            "query_embedding": query_embedding,
            "match_threshold": match_threshold,
            "match_count": match_count,
            "filter_week": filter_week,
            "filter_course": filter_course
        }
        response = client.rpc("match_notes", params).execute()
        return response.data or []
    except Exception as e:
        logger.error(f"Error performing match_notes RPC: {e}")
        return []

def search_notes_lexical(
    keywords: List[str],
    filter_week: Optional[int] = None,
    filter_course: Optional[str] = None,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Performs keyword matching query against 'notes' content for hybrid retrieval.
    Builds a fresh query per keyword to avoid chaining AND parameters.
    """
    client = get_supabase_client()
    if not client or not keywords:
        return []
    try:
        results = []
        for kw in keywords[:3]:
            # Sanitize PostgreSQL LIKE wildcards
            clean_kw = kw.strip().replace("%", "").replace("_", "")
            if len(clean_kw) < 2:
                continue
            
            query = client.table("notes").select("id, content, file_url, file_name, week_number, course_id, topic")
            if filter_week is not None and filter_week > 0:
                query = query.eq("week_number", filter_week)
            if filter_course is not None and filter_course != "UNIVERSAL":
                query = query.eq("course_id", filter_course)
            
            res = query.ilike("content", f"%{clean_kw}%").limit(limit).execute()
            if res.data:
                results.extend(res.data)
        
        deduped = []
        seen = set()
        for r in results:
            rid = r.get("id") or f"{r.get('file_name')}_{r.get('content')[:30]}"
            if rid not in seen:
                seen.add(rid)
                deduped.append(r)
        return deduped
    except Exception as e:
        logger.error(f"Error performing lexical search: {e}")
        return []

def get_full_note_by_filename(file_name: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves full note document by matching file_name, either from SEED_NOTES or by stitching chunks from Supabase.
    """
    try:
        from services.seed_service import SEED_NOTES
        for note in SEED_NOTES:
            if note.get("file_name") == file_name:
                return {
                    "file_name": note["file_name"],
                    "topic": note.get("topic", "General"),
                    "course_id": note.get("course_id", "General"),
                    "week_number": note.get("week_number"),
                    "content": note.get("content", ""),
                    "is_seed": True
                }
    except Exception as e:
        logger.error(f"Error checking seed notes: {e}")

    client = get_supabase_client()
    if not client:
        return None
    try:
        response = client.table("notes").select("file_name, topic, course_id, week_number, content, chunk_index").eq("file_name", file_name).order("chunk_index").execute()
        if not response.data:
            return None
        chunks = response.data
        first = chunks[0]
        stitched_content = "\n\n".join([c.get("content", "") for c in chunks if c.get("content")])
        return {
            "file_name": first.get("file_name"),
            "topic": first.get("topic", "General"),
            "course_id": first.get("course_id", "General"),
            "week_number": first.get("week_number"),
            "content": stitched_content,
            "is_seed": False
        }
    except Exception as e:
        logger.error(f"Error retrieving full note for {file_name}: {e}")
        return None

