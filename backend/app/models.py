import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class DocumentDB(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False, index=True)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    status = Column(String, default="processing", nullable=False) # processing, indexed, error
    error_message = Column(Text, nullable=True)
    chunk_count = Column(Integer, default=0)
    page_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    chunks = relationship("DocumentChunkDB", back_populates="document", cascade="all, delete-orphan")

class DocumentChunkDB(Base):
    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_id = Column(String, nullable=False, index=True)
    page_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    document = relationship("DocumentDB", back_populates="chunks")

class StudyNoteDB(Base):
    __tablename__ = "study_notes"

    id = Column(String, primary_key=True, index=True)
    mode = Column(String, nullable=False) # 'document' or 'ai'
    title = Column(String, nullable=False)
    topic_or_doc_ids = Column(String, nullable=False)
    sections = Column(JSON, nullable=False) # Dict of section_name: content
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class ResearchSessionDB(Base):
    __tablename__ = "research_sessions"

    id = Column(String, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    selected_doc_ids = Column(JSON, nullable=False)
    answers = Column(JSON, nullable=False) # List of QA items with question, answer, citations
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
