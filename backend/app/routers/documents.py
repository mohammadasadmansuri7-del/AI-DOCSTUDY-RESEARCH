import os
import uuid
import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import DocumentDB
from app.schemas import DocumentResponse
from app.services.ingestion import process_document_ingestion
from app.vector_store import vector_store

router = APIRouter(prefix="/api/documents", tags=["Documents"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".pptx", ".ppt", ".txt", ".md", ".markdown"}

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing.")

    # Sanitize filename & check extension
    filename = os.path.basename(file.filename)
    _, ext = os.path.splitext(filename)
    ext = ext.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Read content length and check maximum file size (200 MB)
    doc_id = str(uuid.uuid4())
    safe_filename = f"{doc_id}_{filename}"
    file_path = os.path.join(settings.STORAGE_DIR, safe_filename)

    file_size = 0
    with open(file_path, "wb") as buffer:
        while chunk := await file.read(1024 * 1024): # 1MB chunks
            file_size += len(chunk)
            if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
                buffer.close()
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise HTTPException(
                    status_code=400,
                    detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB} MB."
                )
            buffer.write(chunk)

    # Create Document record in DB
    db_doc = DocumentDB(
        id=doc_id,
        filename=filename,
        file_path=file_path,
        file_type=ext,
        file_size_bytes=file_size,
        status="processing",
        created_at=datetime.datetime.utcnow()
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)

    # Trigger background ingestion processing
    background_tasks.add_task(
        process_document_ingestion,
        document_id=doc_id,
        file_path=file_path,
        filename=filename,
        file_type=ext,
        file_size=file_size,
        db=SessionLocal_for_bg()
    )

    return db_doc

def SessionLocal_for_bg():
    from app.database import SessionLocal
    return SessionLocal()

@router.get("", response_model=List[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(DocumentDB).order_by(DocumentDB.created_at.desc()).all()
    # Format iso string for response
    result = []
    for d in docs:
        result.append(DocumentResponse(
            id=d.id,
            filename=d.filename,
            file_type=d.file_type,
            file_size_bytes=file_size_bytes_to_int(d.file_size_bytes),
            status=d.status,
            error_message=d.error_message,
            chunk_count=d.chunk_count,
            page_count=d.page_count,
            created_at=d.created_at.isoformat() if d.created_at else ""
        ))
    return result

def file_size_bytes_to_int(val):
    return int(val) if val is not None else 0

@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(DocumentDB).filter(DocumentDB.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return DocumentResponse(
        id=doc.id,
        filename=doc.filename,
        file_type=doc.file_type,
        file_size_bytes=doc.file_size_bytes,
        status=doc.status,
        error_message=doc.error_message,
        chunk_count=doc.chunk_count,
        page_count=doc.page_count,
        created_at=doc.created_at.isoformat() if doc.created_at else ""
    )

@router.delete("/{doc_id}")
def delete_document(doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(DocumentDB).filter(DocumentDB.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    # Remove storage file
    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception as e:
            print(f"[Storage] Remove file error: {e}")

    # Remove vector store vectors
    vector_store.delete_document_chunks(doc_id)

    # Delete DB records
    db.delete(doc)
    db.commit()

    return {"message": "Document deleted successfully."}
