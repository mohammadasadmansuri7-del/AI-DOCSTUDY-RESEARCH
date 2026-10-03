from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ResearchRequest, ResearchResponse
from app.services.research import process_document_research
from app.models import ResearchSessionDB, DocumentDB

router = APIRouter(prefix="/api/research", tags=["Document Research"])

@router.post("/query", response_model=ResearchResponse)
async def execute_document_research(payload: ResearchRequest, db: Session = Depends(get_db)):
    if not payload.question or not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question prompt cannot be empty.")

    if not payload.document_ids:
        raise HTTPException(status_code=400, detail="At least one document must be selected.")

    # Validate that selected documents exist
    existing_docs = db.query(DocumentDB).filter(DocumentDB.id.in_(payload.document_ids)).all()
    if not existing_docs:
        raise HTTPException(status_code=404, detail="Selected documents not found.")

    results = await process_document_research(
        prompt=payload.question,
        document_ids=payload.document_ids
    )

    # Save research query history
    try:
        session_rec = ResearchSessionDB(
            id=str(uuid_hex()),
            question=payload.question,
            selected_doc_ids=payload.document_ids,
            answers=[r.model_dump() for r in results]
        )
        db.add(session_rec)
        db.commit()
    except Exception as e:
        print(f"[ResearchDB] History save warning: {e}")

    return ResearchResponse(results=results)

def uuid_hex():
    import uuid
    return str(uuid.uuid4())
