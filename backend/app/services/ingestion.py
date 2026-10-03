import os
import uuid
import datetime
from sqlalchemy.orm import Session
from app.config import settings
from app.database import SessionLocal
from app.models import DocumentDB, DocumentChunkDB
from app.parsers import DocumentParser, chunk_text
from app.vector_store import vector_store

def process_document_ingestion(document_id: str, file_path: str, filename: str, file_type: str, file_size: int, db: Session):
    doc_record = db.query(DocumentDB).filter(DocumentDB.id == document_id).first()
    if not doc_record:
        return

    try:
        page_count = 0
        chunks_to_insert = []
        qdrant_chunks = []
        
        # Parse page by page
        for page in DocumentParser.parse_file(file_path, file_type):
            page_count = max(page_count, page.page_number)
            text_chunks = chunk_text(page.text, chunk_size=400, overlap=80)
            
            for sub_idx, chunk_content in enumerate(text_chunks, start=1):
                chunk_id = f"p{page.page_number}_c{sub_idx}_{uuid.uuid4().hex[:6]}"
                
                # DB Chunk model
                db_chunk = DocumentChunkDB(
                    id=str(uuid.uuid4()),
                    document_id=document_id,
                    chunk_id=chunk_id,
                    page_number=page.page_number,
                    content=chunk_content
                )
                chunks_to_insert.append(db_chunk)
                
                # Payload for Qdrant
                qdrant_chunks.append({
                    "chunk_id": chunk_id,
                    "page_number": page.page_number,
                    "content": chunk_content
                })

        if not chunks_to_insert:
            doc_record.status = "error"
            doc_record.error_message = "No readable text content extracted from file."
            db.commit()
            return

        # Insert chunks into Relational DB
        db.bulk_save_objects(chunks_to_insert)
        
        # Update Document record
        doc_record.status = "indexed"
        doc_record.page_count = page_count
        doc_record.chunk_count = len(chunks_to_insert)
        db.commit()
        
        # Upsert into Qdrant Vector Store
        vector_store.upsert_chunks(
            document_id=document_id,
            filename=filename,
            chunks_data=qdrant_chunks
        )

    except Exception as e:
        db.rollback()
        doc_record = db.query(DocumentDB).filter(DocumentDB.id == document_id).first()
        if doc_record:
            doc_record.status = "error"
            doc_record.error_message = str(e)
            db.commit()
        print(f"[IngestionError] Failed to process document {document_id}: {e}")
