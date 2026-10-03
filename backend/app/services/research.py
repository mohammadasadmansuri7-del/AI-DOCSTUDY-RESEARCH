import httpx
from typing import List, Dict, Any
from app.config import settings
from app.schemas import Citation, SingleQuestionAnswer
from app.services.retrieval import parse_questions_from_prompt, retrieve_evidence_for_question

async def query_nvidia_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Calls NVIDIA API endpoint (OpenAI compatible chat completions format).
    """
    if not settings.NVIDIA_API_KEY or not settings.NVIDIA_API_KEY.strip():
        raise ValueError("NVIDIA_API_KEY is not configured on server.")

    headers = {
        "Authorization": f"Bearer {settings.NVIDIA_API_KEY.strip()}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": settings.NVIDIA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 1024
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        url = f"{settings.NVIDIA_BASE_URL.rstrip('/')}/chat/completions"
        resp = await client.post(url, headers=headers, json=payload)
        if resp.status_code != 200:
            raise RuntimeError(f"NVIDIA API Error {resp.status_code}: {resp.text}")
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()

async def process_document_research(prompt: str, document_ids: List[str]) -> List[SingleQuestionAnswer]:
    questions = parse_questions_from_prompt(prompt)
    results: List[SingleQuestionAnswer] = []

    for q in questions:
        chunks = retrieve_evidence_for_question(q, document_ids, top_k=5)

        # Strict evidence check
        if not chunks:
            results.append(SingleQuestionAnswer(
                question=q,
                answer="Not found in document.",
                sources=[],
                found_in_document=False
            ))
            continue

        # Format context evidence string with metadata
        context_parts = []
        citations_map: Dict[str, Citation] = {}
        for c in chunks:
            cit = Citation(
                document_id=c["document_id"],
                filename=c["filename"],
                page_number=c["page_number"],
                chunk_id=c["chunk_id"],
                content=c["content"]
            )
            citations_map[c["chunk_id"]] = cit
            context_parts.append(
                f"[Source: {c['filename']}, Page {c['page_number']}, Chunk {c['chunk_id']}]\n{c['content']}"
            )

        context_str = "\n\n".join(context_parts)

        system_prompt = (
            "You are an elite, highly precise Document Research AI assistant.\n"
            "Your mission is to provide complete, educational, and human-readable answers strictly grounded in the provided DOCUMENT EVIDENCE.\n\n"
            "STRICT BEHAVIOR GUIDELINES:\n"
            "1. STRICT GROUNDING:\n"
            "   - Rely strictly on the retrieved document context. Never invent outside facts, software packages, or commands.\n"
            "   - If the answer to the question cannot be found directly in the evidence, you MUST respond EXACTLY with:\n"
            "     Not found in document.\n"
            "   - Do NOT use outside knowledge or assumptions. Do NOT invent sources or citations.\n\n"
            "2. COMPLETENESS & CONTEXTUAL LEAD-IN:\n"
            "   - Do NOT output bare, naked terminal commands or raw code by themselves.\n"
            "   - Always provide a complete, cohesive answer starting with a helpful opening sentence grounded in the context (e.g., stating what the document explains or provides).\n"
            "   - If the document contains incomplete steps or partial info, state clearly: 'According to the document, the following steps are provided:' rather than outputting truncated text.\n\n"
            "3. CODE & COMMANDS FORMATTING:\n"
            "   - Whenever the answer contains commands, file paths, terminal instructions, or code syntax, ALWAYS wrap them in clean Markdown code blocks (e.g. ```bash ... ```) and explain what each step does based on the text.\n\n"
            "4. ACCURACY:\n"
            "   - Answer ONLY the specific question asked using the document evidence."
        )

        user_prompt = (
            f"QUESTION:\n{q}\n\n"
            f"DOCUMENT EVIDENCE:\n{context_str}\n\n"
            "Remember:\n"
            "- Start with a clear introductory sentence grounded in the context.\n"
            "- Format any commands or code in Markdown code blocks (e.g. ```bash ... ```) with explanations.\n"
            "- If the evidence does not contain the answer, reply EXACTLY with 'Not found in document.'"
        )

        try:
            answer = await query_nvidia_llm(system_prompt, user_prompt)
            
            # Check if answer indicates not found
            if "Not found in document" in answer or answer.strip() == "Not found in document.":
                results.append(SingleQuestionAnswer(
                    question=q,
                    answer="Not found in document.",
                    sources=[],
                    found_in_document=False
                ))
            else:
                # Include valid sources
                valid_sources = list(citations_map.values())
                results.append(SingleQuestionAnswer(
                    question=q,
                    answer=answer,
                    sources=valid_sources,
                    found_in_document=True
                ))
        except Exception as e:
            print(f"[NVIDIA Error] {e}")
            # Fallback when NVIDIA API fails or key missing: evaluate evidence locally
            # If evidence is strong, extract key sentence, otherwise return Not found in document.
            lowered_q_words = set(q.lower().split())
            matched = False
            extracted_text = ""
            for c in chunks:
                words_in_chunk = set(c["content"].lower().split())
                overlap = len(lowered_q_words.intersection(words_in_chunk))
                if overlap >= 2:
                    matched = True
                    extracted_text = c["content"]
                    break
            
            if matched:
                results.append(SingleQuestionAnswer(
                    question=q,
                    answer=f"According to the document, the following information is provided:\n\n{extracted_text}",
                    sources=list(citations_map.values()),
                    found_in_document=True
                ))
            else:
                results.append(SingleQuestionAnswer(
                    question=q,
                    answer="Not found in document.",
                    sources=[],
                    found_in_document=False
                ))

    return results
