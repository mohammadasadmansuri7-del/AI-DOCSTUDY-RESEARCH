import re
from typing import List, Dict, Any
from app.vector_store import vector_store

def parse_questions_from_prompt(prompt: str) -> List[str]:
    """
    Extracts individual questions if user sends numbered or multi-line questions.
    Fallback: returns full prompt if single question.
    """
    text = prompt.strip()
    if not text:
        return []
    
    # Try splitting by numbered patterns like '1.', '2)', 'Q1:'
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    questions = []
    
    pattern = re.compile(r'^(?:\d+[\.\)]|Q\d+:?|\*|\-)\s*(.+)', re.IGNORECASE)
    
    for line in lines:
        match = pattern.match(line)
        if match:
            q = match.group(1).strip()
            if q:
                questions.append(q)
        elif len(lines) > 1 and line.endswith('?'):
            questions.append(line)

    if not questions:
        questions = [text]

    return questions

def retrieve_evidence_for_question(
    question: str,
    document_ids: List[str],
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Performs vector search across document_ids for a single question.
    Returns list of chunks with keys:
    document_id, filename, page_number, chunk_id, content, score
    """
    chunks = vector_store.search_relevant_chunks(
        query=question,
        document_ids=document_ids,
        top_k=top_k,
        score_threshold=0.15
    )
    return chunks
