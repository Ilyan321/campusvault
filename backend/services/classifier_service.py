import os
import json
import logging
from typing import Dict, Any, List, Optional
from config import GROQ_API_KEY, GROQ_CLASSIFIER_MODEL

logger = logging.getLogger("campusvault.classifier")

_syllabus_data: Optional[List[Dict[str, Any]]] = None

def load_syllabus() -> List[Dict[str, Any]]:
    global _syllabus_data
    if _syllabus_data is None:
        syllabus_path = os.path.join(os.path.dirname(__file__), "..", "utils", "syllabus.json")
        try:
            with open(syllabus_path, "r", encoding="utf-8") as f:
                _syllabus_data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load syllabus JSON: {e}")
            _syllabus_data = []
    return _syllabus_data

def heuristic_classify(text: str, course_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Keyword scoring heuristic based on syllabus grounding keywords.
    """
    syllabi = load_syllabus()
    text_lower = text.lower()
    
    best_match = {
        "course_id": course_id or (syllabi[0]["course_id"] if syllabi else "CSE-212"),
        "assigned_week": 1,
        "topic": "General Engineering Concepts",
        "confidence": 0.5,
        "reasoning": "Default heuristic match based on keyword frequency."
    }
    
    max_score = 0
    
    for course in syllabi:
        if course_id and course["course_id"] != course_id:
            continue
        for week_info in course.get("syllabus_timeline", []):
            score = 0
            for kw in week_info.get("grounding_keywords", []):
                score += text_lower.count(kw.lower()) * 2
            if week_info.get("core_topic", "").lower() in text_lower:
                score += 5
            
            if score > max_score:
                max_score = score
                best_match = {
                    "course_id": course["course_id"],
                    "assigned_week": week_info["week"],
                    "topic": week_info["core_topic"],
                    "confidence": min(0.95, 0.4 + (score * 0.05)),
                    "reasoning": f"Matched {score} topic-specific grounding keywords in text."
                }
                
    return best_match

def classify_syllabus_week(text: str, course_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Classifies raw extracted text into corresponding course syllabus week using Groq Llama-3.1-8b-instant.
    """
    syllabi = load_syllabus()
    
    if not GROQ_API_KEY:
        logger.info("GROQ_API_KEY not set. Using keyword-based heuristic classification.")
        return heuristic_classify(text, course_id)
        
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        
        # Build prompt with syllabus context
        syllabus_summary = []
        for course in syllabi:
            if course_id and course["course_id"] != course_id:
                continue
            for week_info in course.get("syllabus_timeline", []):
                syllabus_summary.append({
                    "course_id": course["course_id"],
                    "course_name": course["course_name"],
                    "week": week_info["week"],
                    "core_topic": week_info["core_topic"],
                    "keywords": week_info.get("grounding_keywords", [])
                })
                
        # Truncate text sample to save tokens and avoid rate limits
        text_sample = text[:3000]
        
        system_prompt = (
            "You are an academic curriculum classifier for university engineering courses. "
            "Given a sample of student notes or lab code, determine which syllabus week and topic it maps to. "
            "Respond ONLY with valid JSON in this exact structure:\n"
            "{\n"
            '  "course_id": "CSE-212",\n'
            '  "assigned_week": 5,\n'
            '  "topic": "Queue Data Structure & Circular Implementations",\n'
            '  "confidence": 0.95,\n'
            '  "reasoning": "Concise 1-sentence explanation under 20 words"\n'
            "}"
        )
        
        user_message = f"Syllabus Timeline:\n{json.dumps(syllabus_summary, indent=2)}\n\nDocument Content:\n{text_sample}"
        
        response = client.chat.completions.create(
            model=GROQ_CLASSIFIER_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=600
        )
        
        content = response.choices[0].message.content
        result = json.loads(content)
        return result
    except Exception as e:
        logger.error(f"Groq classification failed: {e}. Falling back to heuristic.")
        return heuristic_classify(text, course_id)
