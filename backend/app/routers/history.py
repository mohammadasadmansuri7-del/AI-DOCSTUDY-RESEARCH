import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ResearchSessionDB, StudyNoteDB

router = APIRouter(prefix="/api/history", tags=["History"])

@router.get("")
def get_all_history(db: Session = Depends(get_db)):
    research_sessions = (
        db.query(ResearchSessionDB)
        .order_by(ResearchSessionDB.created_at.desc())
        .limit(50)
        .all()
    )
    study_notes = (
        db.query(StudyNoteDB)
        .order_by(StudyNoteDB.created_at.desc())
        .limit(50)
        .all()
    )

    research_data = []
    for r in research_sessions:
        research_data.append({
            "id": r.id,
            "type": "research",
            "question": r.question,
            "selected_doc_ids": r.selected_doc_ids or [],
            "answers": r.answers or [],
            "created_at": r.created_at.isoformat() if r.created_at else ""
        })

    notes_data = []
    for n in study_notes:
        notes_data.append({
            "id": n.id,
            "type": "note",
            "title": n.title,
            "topic": n.topic_or_doc_ids,
            "sections": n.sections or {},
            "created_at": n.created_at.isoformat() if n.created_at else ""
        })

    return {
        "research": research_data,
        "notes": notes_data
    }

@router.delete("/research/{session_id}")
def delete_research_history_item(session_id: str, db: Session = Depends(get_db)):
    item = db.query(ResearchSessionDB).filter(ResearchSessionDB.id == session_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Research history item not found.")
    db.delete(item)
    db.commit()
    return {"message": "Research history item deleted."}

@router.delete("/notes/{note_id}")
def delete_note_history_item(note_id: str, db: Session = Depends(get_db)):
    item = db.query(StudyNoteDB).filter(StudyNoteDB.id == note_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Study note history item not found.")
    db.delete(item)
    db.commit()
    return {"message": "Study note history item deleted."}

@router.delete("")
def clear_all_history(db: Session = Depends(get_db)):
    db.query(ResearchSessionDB).delete()
    db.query(StudyNoteDB).delete()
    db.commit()
    return {"message": "All history cleared successfully."}
