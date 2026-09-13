import re
import time
import logging
from typing import Dict, Any, List, Optional, AsyncGenerator
from config import GROQ_API_KEY, GROQ_CHAT_MODEL
from services.embedder_service import get_embedding
from services.supabase_service import search_similar_notes

logger = logging.getLogger("campusvault.rag")

# In-memory query cache for rate-limit protection & instantaneous repeat responses
_query_cache: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 3600
MAX_CACHE_ENTRIES = 200

def _prune_cache_if_needed():
    """Prunes expired entries or limits cache size to prevent memory leakage."""
    now = time.time()
    if len(_query_cache) > MAX_CACHE_ENTRIES:
        expired = [k for k, v in _query_cache.items() if now - v.get("timestamp", 0) > CACHE_TTL_SECONDS]
        for k in expired:
            _query_cache.pop(k, None)
        if len(_query_cache) > MAX_CACHE_ENTRIES:
            oldest = sorted(_query_cache.keys(), key=lambda k: _query_cache[k].get("timestamp", 0))[:50]
            for k in oldest:
                _query_cache.pop(k, None)

def get_cache_key(query: str, week_number: int, course_id: Optional[str]) -> str:
    return f"{course_id or 'any'}_w{week_number}_{query.strip().lower()}"

def clean_llm_response(text: str) -> str:
    """Strips <think> tags or internal reasoning prefixes from output."""
    if not text:
        return ""
    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    return cleaned.strip()

def build_system_prompt() -> str:
    return (
        "You are 'Senior AI', a brilliant, friendly, and empathetic engineering senior at QUEST Nawabshah / MUET Jamshoro. "
        "Your mission is to help junior students ace their lab exams, assignments, and theory concepts by explaining things "
        "using their seniors' uploaded peer notes.\n\n"
        "Guidelines:\n"
        "1. Grounding: Answer based on the provided peer notes context. If the information isn't present, explain what is known from the notes and politely state what's missing.\n"
        "2. Language & Tone: Use a natural blend of Roman Urdu and technical English (code-switching like: 'Dekho bhai/behan...', 'Basically pointer rear reset tab hota hai jab...', 'Lab practical point of view se...'). Keep it warm, motivating, and crystal clear.\n"
        "3. Code & Technical Depth: When explaining code or algorithms, provide clean, well-commented code snippets with edge cases highlighted.\n"
        "4. Transparency: Reference which peer note or section the concept is drawn from.\n"
    )

def execute_rag_pipeline(
    query: str,
    week_number: int,
    course_id: Optional[str] = "CSE-212",
    match_threshold: float = 0.25,
    match_count: int = 4
) -> Dict[str, Any]:
    """
    Executes the full RAG pipeline: embedding, Supabase pgvector search, prompt construction, and Groq LLM inference.
    """
    cache_key = get_cache_key(query, week_number, course_id)
    now = time.time()
    if cache_key in _query_cache:
        cached_entry = _query_cache[cache_key]
        if now - cached_entry["timestamp"] < CACHE_TTL_SECONDS:
            logger.info(f"Returning cached RAG response for: {query}")
            return cached_entry["response"]

    # 1. Embed query
    query_vector = get_embedding(query)

    # 2. Vector search via pgvector
    sources = search_similar_notes(
        query_embedding=query_vector,
        filter_week=week_number,
        filter_course=course_id,
        match_threshold=match_threshold,
        match_count=match_count
    )

    # 3. Format Context Chunks
    if sources:
        context_parts = []
        for idx, src in enumerate(sources, 1):
            context_parts.append(
                f"--- [Peer Note {idx} | Source: {src.get('file_name', 'Senior_Note')} | Topic: {src.get('topic', 'General')} | Relevance: {src.get('similarity', 0):.2f}] ---\n"
                f"{src.get('content', '')}"
            )
        context_str = "\n\n".join(context_parts)
    else:
        context_str = "No specific peer notes found in the database for this specific week yet."

    user_prompt = (
        f"CONTEXT (Seniors' Uploaded Notes for Week {week_number} - {course_id}):\n"
        f"{context_str}\n\n"
        f"JUNIOR'S QUESTION:\n{query}\n\n"
        f"Provide a comprehensive, empathetic explanation with working code if applicable:"
    )

    # 4. Infer via Groq LPU
    if not GROQ_API_KEY:
        answer = (
            f"**[Demo Mode - GROQ_API_KEY not set]**\n\n"
            f"Bhai query receive hogayi: '{query}' for Week {week_number}.\n\n"
            f"Found {len(sources)} matching peer note chunks in database."
        )
    else:
        try:
            from groq import Groq
            client = Groq(api_key=GROQ_API_KEY)
            response = client.chat.completions.create(
                model=GROQ_CHAT_MODEL,
                messages=[
                    {"role": "system", "content": build_system_prompt()},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            raw_answer = response.choices[0].message.content or ""
            answer = clean_llm_response(raw_answer)
        except Exception as e:
            logger.error(f"Groq Chat inference error: {e}")
            answer = f"Hamara AI abhi thoda busy hai ya rate limit hit hui hai. Please try again in 5 seconds! (Error: {str(e)})"

    result = {
        "answer": answer,
        "week_number": week_number,
        "course_id": course_id,
        "sources": sources,
        "query": query
    }

    # Store in cache with size bounding
    _prune_cache_if_needed()
    _query_cache[cache_key] = {"response": result, "timestamp": now}
    return result

async def stream_rag_pipeline(
    query: str,
    week_number: int,
    course_id: Optional[str] = "CSE-212"
) -> AsyncGenerator[str, None]:
    """
    Streams tokens directly for real-time frontend typing experience.
    """
    query_vector = get_embedding(query)
    sources = search_similar_notes(
        query_embedding=query_vector,
        filter_week=week_number,
        filter_course=course_id,
        match_threshold=0.25,
        match_count=4
    )

    if sources:
        context_parts = [
            f"--- [Peer Note {i+1}: {s.get('file_name', 'Note')} - {s.get('topic', '')}] ---\n{s.get('content', '')}"
            for i, s in enumerate(sources)
        ]
        context_str = "\n\n".join(context_parts)
    else:
        context_str = "No specific peer notes found for this week yet."

    user_prompt = (
        f"CONTEXT (Seniors' Uploaded Notes for Week {week_number} - {course_id}):\n"
        f"{context_str}\n\n"
        f"JUNIOR'S QUESTION:\n{query}"
    )

    if not GROQ_API_KEY:
        yield "Demo stream: GROQ_API_KEY is not configured."
        return

    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)
    stream = client.chat.completions.create(
        model=GROQ_CHAT_MODEL,
        messages=[
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=1500,
        stream=True
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content or ""
        if delta:
            yield delta
