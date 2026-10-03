import uuid
import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import StudyNoteDB
from app.schemas import AIStudyNotesRequest, StudyNotesResponse
from app.services.notes import generate_ai_study_notes

router = APIRouter(prefix="/api/notes", tags=["AI Study Notes"])

@router.post("/ai", response_model=StudyNotesResponse)
async def create_ai_notes(payload: AIStudyNotesRequest, db: Session = Depends(get_db)):
    if not payload.topic or not payload.topic.strip():
        raise HTTPException(status_code=400, detail="Topic or question cannot be empty.")

    topic_str = payload.topic.strip()
    notes_data = await generate_ai_study_notes(prompt_or_topic=topic_str)

    note_record = StudyNoteDB(
        id=str(uuid.uuid4()),
        mode="ai",
        title=notes_data.get("title", f"AI Notes: {topic_str[:50]}"),
        topic_or_doc_ids=topic_str,
        sections=notes_data.get("sections", {}),
        created_at=datetime.datetime.utcnow()
    )
    db.add(note_record)
    db.commit()
    db.refresh(note_record)

    return StudyNotesResponse(
        id=note_record.id,
        mode=note_record.mode,
        title=note_record.title,
        topic_or_doc_ids=note_record.topic_or_doc_ids,
        sections=note_record.sections,
        created_at=note_record.created_at.isoformat() if note_record.created_at else ""
    )

@router.get("", response_model=List[StudyNotesResponse])
def list_study_notes(db: Session = Depends(get_db)):
    notes = db.query(StudyNoteDB).order_by(StudyNoteDB.created_at.desc()).all()
    result = []
    for n in notes:
        result.append(StudyNotesResponse(
            id=n.id,
            mode=n.mode,
            title=n.title,
            topic_or_doc_ids=n.topic_or_doc_ids,
            sections=n.sections,
            created_at=n.created_at.isoformat() if n.created_at else ""
        ))
    return result

@router.delete("/{note_id}")
def delete_study_note(note_id: str, db: Session = Depends(get_db)):
    note = db.query(StudyNoteDB).filter(StudyNoteDB.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Study note not found.")
    db.delete(note)
    db.commit()
    return {"message": "Study note deleted successfully."}
