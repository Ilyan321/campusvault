import re
import time
import json
import logging
from typing import Dict, Any, List, Optional, Tuple, AsyncGenerator
from config import GROQ_API_KEY, GROQ_CHAT_MODEL
from services.embedder_service import get_embedding, get_embeddings_batch
from services.supabase_service import search_similar_notes
from services.classifier_service import load_syllabus, heuristic_classify

logger = logging.getLogger("campusvault.agentic_rag")

def clean_llm_text(text: str) -> str:
    """Strips <think> tags, unclosed think blocks, or internal reasoning prefixes."""
    if not text:
        return ""
    # Strip closed <think>...</think> blocks
    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    # Strip unclosed <think> block if token limit cutoff occurred
    if '<think>' in cleaned:
        cleaned = re.sub(r'<think>.*', '', cleaned, flags=re.DOTALL)
    return cleaned.strip()

# 1. BILINGUAL INTENT & AUTONOMOUS SYLLABUS ROUTER WITH MULTI-TURN MEMORY
def analyze_and_expand_query(
    query: str,
    active_week: Optional[int] = None,
    course_id: Optional[str] = None,
    history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Agent Planning Step:
    - Autonomously detects if the question belongs to a specific syllabus week/course or is a general query
    - Takes prior conversation history into account to reformulate follow-ups (e.g., 'explain step 2', 'do it in python')
    - Detects language style (English, Roman Urdu, or Code-Switch)
    - Generates targeted technical sub-queries for dense + lexical retrieval
    """
    syllabi = load_syllabus()
    
    # Filter courses if a specific course_id is active and not universal
    if course_id and course_id != "UNIVERSAL":
        syllabus_context = [
            {"course_id": c["course_id"], "week": w["week"], "topic": w["core_topic"], "keywords": w.get("grounding_keywords", [])}
            for c in syllabi if c["course_id"] == course_id for w in c.get("syllabus_timeline", [])
        ]
    else:
        syllabus_context = [
            {"course_id": c["course_id"], "week": w["week"], "topic": w["core_topic"], "keywords": w.get("grounding_keywords", [])}
            for c in syllabi for w in c.get("syllabus_timeline", [])
        ]
    
    auto_detected_week = active_week

    if not GROQ_API_KEY:
        return {
            "is_general": False if active_week else False,
            "language_mode": "english",
            "course_id": course_id,
            "target_weeks": [active_week] if active_week else [],
            "primary_week": active_week,
            "expanded_queries": [query],
            "reasoning": "Fallback"
        }
        
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        
        system_prompt = (
            "You are CampusVault's intelligent academic router and query planner.\n"
            "Analyze the student's question against the university syllabus catalog and recent conversation history.\n\n"
            "RULES:\n"
            "1. If the question matches an engineering/CS syllabus topic (e.g. data structures, subnetting, recursion, OS, graphs):\n"
            "   - Identify 'course_id', 'primary_week', and 'detected_topic'.\n"
            "   - Set 'is_general': false\n"
            "   - Generate 2-3 expanded technical English sub-queries for vector and keyword search. If the student question is a follow-up (e.g. 'explain step 3', 'write it in C++'), resolve pronouns using conversation history into fully explicit search terms.\n"
            "2. If the question is general knowledge, pop culture, history, greetings, or general non-syllabus discussion (e.g. 'what is batman', 'hello', 'who is alan turing'):\n"
            "   - Set 'is_general': true\n"
            "   - Set 'course_id': null, 'primary_week': null, 'detected_topic': null\n"
            "   - Set 'target_weeks': []\n"
            "   - 'expanded_queries': [question]\n\n"
            "Respond ONLY with a JSON object in this format:\n"
            "```json\n"
            "{\n"
            '  "is_general": false,\n'
            '  "course_id": "CSE-212" or null,\n'
            '  "primary_week": 5 or null,\n'
            '  "target_weeks": [5],\n'
            '  "detected_topic": "Topic Name" or null,\n'
            '  "expanded_queries": ["query 1", "query 2"],\n'
            '  "language_mode": "english" or "roman_urdu"\n'
            "}\n"
            "```"
        )
        
        history_context = ""
        if history and len(history) > 0:
            recent_turns = history[-4:] # Last 2 exchanges
            formatted_turns = []
            for h in recent_turns:
                role = "Student" if h.get("role") == "user" else "CampusVault"
                formatted_turns.append(f"{role}: {h.get('content', '')[:200]}")
            history_context = "\nRecent Conversation History:\n" + "\n".join(formatted_turns) + "\n"

        user_msg = (
            f"Active Scope Context: {course_id or 'UNIVERSAL (All Subjects)'}\n"
            f"User Active Week Context: {active_week or 'None (Auto-detect)'}\n"
            f"{history_context}"
            f"Syllabus Catalog: {json.dumps(syllabus_context)}\n"
            f"Student Question: {query}"
        )
        
        resp = client.chat.completions.create(
            model=GROQ_CHAT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.1,
            max_tokens=350
        )
        
        raw_text = resp.choices[0].message.content or ""
        cleaned = clean_llm_text(raw_text)
        
        json_match = re.search(r'\{.*?\}', cleaned, re.DOTALL)
        if json_match:
            plan = json.loads(json_match.group(0))
        else:
            plan = {
                "is_general": False,
                "language_mode": "english",
                "primary_week": auto_detected_week,
                "target_weeks": [auto_detected_week] if auto_detected_week else [],
                "expanded_queries": [query]
            }
            
        if not plan.get("expanded_queries"):
            plan["expanded_queries"] = [query]
            
        return plan
    except Exception as e:
        logger.error(f"Query analysis error: {e}")
        return {
            "is_general": False,
            "language_mode": "english",
            "primary_week": auto_detected_week,
            "target_weeks": [auto_detected_week] if auto_detected_week else [],
            "expanded_queries": [query]
        }

# 2. HYBRID RETRIEVAL (DENSE VECTOR + LEXICAL KEYWORD) + RECIPROCAL RANK FUSION (RRF)
def execute_rrf_retrieval(
    plan: Dict[str, Any],
    course_id: Optional[str] = None,
    match_threshold: float = 0.18,
    max_total_sources: int = 5,
    rrf_k: int = 60
) -> List[Dict[str, Any]]:
    """
    Hybrid Search Engine:
    1. Dense semantic search via FastEmbed (384-dim BGE-small).
    2. Lexical keyword search via Supabase ILIKE / text matching.
    3. Fuses both candidate rankings with Reciprocal Rank Fusion (RRF) for 100% technical keyword & symbol precision.
    """
    if plan.get("is_general"):
        return []

    target_weeks = plan.get("target_weeks", [])
    queries = plan.get("expanded_queries", [])
    if not queries:
        return []

    # Target course filter: use plan course_id if universal
    filter_course = course_id if (course_id and course_id != "UNIVERSAL") else plan.get("course_id")

    # Batch dense embedding
    query_vectors = get_embeddings_batch(queries)
    
    # Candidate pool: chunk_id -> (chunk_dict, rrf_score, max_sim)
    candidate_scores: Dict[str, Dict[str, Any]] = {}
    
    weeks_to_search = target_weeks if target_weeks else [None]

    # Step A: Dense Vector Retrieval
    for q_idx, q_vec in enumerate(query_vectors):
        for wk in weeks_to_search:
            results = search_similar_notes(
                query_embedding=q_vec,
                filter_week=wk,
                filter_course=filter_course,
                match_threshold=match_threshold,
                match_count=4
            )
            for rank, item in enumerate(results, start=1):
                chunk_id = f"{item.get('file_name')}_{item.get('content', '')[:50]}"
                rrf_increment = 1.0 / (rrf_k + rank)
                
                if chunk_id not in candidate_scores:
                    item_copy = dict(item)
                    candidate_scores[chunk_id] = {
                        "chunk": item_copy,
                        "rrf_score": rrf_increment,
                        "max_sim": item.get("similarity", 0)
                    }
                else:
                    candidate_scores[chunk_id]["rrf_score"] += rrf_increment
                    if item.get("similarity", 0) > candidate_scores[chunk_id]["max_sim"]:
                        candidate_scores[chunk_id]["max_sim"] = item.get("similarity", 0)

    # Step B: Lexical Keyword / Exact Symbol Matching (Hybrid Search)
    from services.supabase_service import search_notes_lexical
    for wk in weeks_to_search:
        lexical_results = search_notes_lexical(
            keywords=queries,
            filter_week=wk,
            filter_course=filter_course,
            limit=4
        )
        for rank, item in enumerate(lexical_results, start=1):
            chunk_id = f"{item.get('file_name')}_{item.get('content', '')[:50]}"
            # Bonus RRF boost for exact lexical symbol match
            rrf_increment = 1.2 / (rrf_k + rank)
            if chunk_id not in candidate_scores:
                item_copy = dict(item)
                candidate_scores[chunk_id] = {
                    "chunk": item_copy,
                    "rrf_score": rrf_increment,
                    "max_sim": 0.50 # Synthetic similarity for lexical match
                }
            else:
                candidate_scores[chunk_id]["rrf_score"] += rrf_increment
                candidate_scores[chunk_id]["max_sim"] = max(candidate_scores[chunk_id]["max_sim"], 0.50)
                        
    # Sort candidates by combined RRF score
    ranked = sorted(candidate_scores.values(), key=lambda x: x["rrf_score"], reverse=True)
    
    final_sources = []
    for entry in ranked[:max_total_sources]:
        chunk_obj = entry["chunk"]
        chunk_obj["similarity"] = round(entry["max_sim"], 3)
        chunk_obj["rrf_score"] = round(entry["rrf_score"], 4)
        final_sources.append(chunk_obj)
        
    return final_sources

# 3. SELF-RAG DOCUMENT RELEVANCE GRADER
def grade_retrieval_relevance(query: str, sources: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
    if not sources:
        return "EMPTY", []
    top_sim = sources[0].get("similarity", 0)
    if top_sim >= 0.40:
        return "HIGH", sources
    elif top_sim >= 0.22:
        return "PARTIAL", sources
    else:
        return "LOW", sources

# 4. BILINGUAL GROUNDED SYNTHESIS PROMPT BUILDER WITH CONVERSATION MEMORY
def build_bilingual_synthesis_prompt(
    query: str,
    plan: Dict[str, Any],
    sources: List[Dict[str, Any]],
    course_id: Optional[str] = None,
    history: Optional[List[Dict[str, str]]] = None
) -> Tuple[str, str]:
    language_mode = plan.get("language_mode", "english")
    primary_week = plan.get("primary_week")
    target_course = plan.get("course_id") or course_id or "Universal"
    
    if sources:
        context_parts = []
        for idx, src in enumerate(sources, 1):
            context_parts.append(
                f"--- [Peer Note {idx} | File: {src.get('file_name', 'Note')} | Week: {src.get('week_number', 'N/A')} | Topic: {src.get('topic', 'General')} | Relevance: {src.get('similarity', 0):.2f}] ---\n"
                f"{src.get('content', '')}"
            )
        context_str = "\n\n".join(context_parts)
    else:
        context_str = "No specific senior peer notes needed or found for this question."

    system_prompt = (
        "You are CampusVault, an advanced, developer-grade academic assistant and engineering mentor.\n"
        "Your mission is to deliver clear, precise, and directly helpful answers.\n\n"
        "RESPONSE GUIDELINES:\n"
        "- If the student asks a general question, general knowledge, or basic concept: Answer it directly, informatively, and politely. Never say 'your question is unrelated to course XYZ'.\n"
        "- If syllabus notes are provided: Ground your explanation in the verified peer notes, highlighting code examples, mathematical proofs, time/space complexity, and exam edge cases.\n"
        "- Multi-Turn Awareness: Seamlessly reference previous context from the chat when the user asks follow-up questions.\n"
        "- Tone: Professional, developer-grade, and concise.\n"
        "- Language: Default to clear technical English. Only use Roman Urdu if the student specifically asks in Roman Urdu.\n"
        "- Markdown Formatting: Always format answers in clean Markdown (use bolding **like this**, bullet lists, and fenced code blocks ```cpp ... ``` with syntax highlighting).\n"
        "- Mathematical & Scientific Notation: Format math formulas cleanly using standard LaTeX enclosed in $$ ... $$ for block/display equations or $ ... $ for inline expressions. Always ensure all equation brackets and matrix environments are properly opened and closed.\n"
        "- Completeness: Deliver a thorough, comprehensive response and always complete all sentences, sections, and formulas cleanly without cutting off."
    )

    meta_desc = f"Scope: {target_course}"
    if primary_week:
        meta_desc += f" | Week {primary_week}"
    if plan.get("detected_topic"):
        meta_desc += f" | Topic: {plan.get('detected_topic')}"

    history_str = ""
    if history and len(history) > 0:
        recent = history[-4:]
        h_lines = []
        for turn in recent:
            r = "Student" if turn.get("role") == "user" else "CampusVault"
            h_lines.append(f"{r}: {turn.get('content', '')}")
        history_str = "PREVIOUS CONVERSATION CONTEXT:\n" + "\n".join(h_lines) + "\n\n"

    user_prompt = (
        f"{history_str}"
        f"STUDENT QUESTION:\n{query}\n\n"
        f"ROUTER METADATA:\n{meta_desc}\n\n"
        f"GROUNDED CONTEXT:\n{context_str}\n\n"
        f"Provide a structured, well-formatted Markdown response:"
    )
    
    return system_prompt, user_prompt

# 5. MASTER AGENTIC PIPELINE (Sync & Stream)
def run_agentic_rag(
    query: str,
    week_number: Optional[int] = None,
    course_id: Optional[str] = None,
    history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    start_time = time.time()
    
    # Step 1: Autonomous Analysis & Week Discovery with Memory
    plan = analyze_and_expand_query(query, week_number, course_id, history=history)
    primary_week = plan.get("primary_week")
    detected_course = plan.get("course_id") or course_id
    
    # Step 2: Hybrid Dense + Lexical Retrieval with RRF Reranking
    sources = execute_rrf_retrieval(plan, detected_course)
    
    # Step 3: Self-RAG Document Grader
    grade, graded_sources = grade_retrieval_relevance(query, sources)
    
    # If low relevance and only 1 week searched, expand search to adjacent syllabus weeks if week is known
    if grade == "LOW" and primary_week and len(plan.get("target_weeks", [])) == 1:
        expanded = [primary_week]
        if primary_week > 1: expanded.append(primary_week - 1)
        if primary_week < 16: expanded.append(primary_week + 1)
        plan["target_weeks"] = expanded
        graded_sources = execute_rrf_retrieval(plan, detected_course, match_threshold=0.15)
        
    # Step 4: Synthesis
    sys_prompt, user_prompt = build_bilingual_synthesis_prompt(query, plan, graded_sources, detected_course, history=history)
    
    if not GROQ_API_KEY:
        answer = f"**CampusVault** received question: '{query}'."
    else:
        try:
            from groq import Groq
            client = Groq(api_key=GROQ_API_KEY)
            resp = client.chat.completions.create(
                model=GROQ_CHAT_MODEL,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.25,
                max_tokens=1500
            )
            raw_text = resp.choices[0].message.content or ""
            answer = clean_llm_text(raw_text)
        except Exception as e:
            logger.error(f"Agentic inference error: {e}")
            answer = f"Service temporarily busy. Please try again. (Details: {str(e)})"

    latency = time.time() - start_time
    
    return {
        "answer": answer,
        "week_number": primary_week,
        "course_id": detected_course,
        "sources": graded_sources,
        "query": query,
        "agentic_meta": {
            "auto_detected_week": primary_week,
            "detected_topic": plan.get("detected_topic"),
            "language_mode": plan.get("language_mode", "english"),
            "expanded_queries": plan.get("expanded_queries", [query]),
            "relevance_grade": grade,
            "latency_seconds": round(latency, 2)
        }
    }

async def stream_agentic_rag(
    query: str,
    week_number: Optional[int] = None,
    course_id: Optional[str] = None,
    history: Optional[List[Dict[str, str]]] = None
) -> AsyncGenerator[str, None]:
    """
    Streams Agentic RAG tokens with Server-Sent Events (SSE).
    """
    plan = analyze_and_expand_query(query, week_number, course_id, history=history)
    primary_week = plan.get("primary_week")
    detected_course = plan.get("course_id") or course_id
    sources = execute_rrf_retrieval(plan, detected_course)
    sys_prompt, user_prompt = build_bilingual_synthesis_prompt(query, plan, sources, detected_course, history=history)

    if not GROQ_API_KEY:
        yield f"data: {json.dumps({'type': 'token', 'content': 'GROQ_API_KEY not configured.'})}\n\n"
        return

    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)
    
    meta_event = {
        "type": "meta",
        "auto_detected_week": primary_week,
        "detected_topic": plan.get("detected_topic"),
        "language_mode": plan.get("language_mode", "english"),
        "sources": sources
    }
    yield f"data: {json.dumps(meta_event)}\n\n"

    try:
        stream = client.chat.completions.create(
            model=GROQ_CHAT_MODEL,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.25,
            max_tokens=1500,
            stream=True
        )
        
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                yield f"data: {json.dumps({'type': 'token', 'content': delta})}\n\n"
    except Exception as e:
        logger.error(f"Streaming error: {e}")
        yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

