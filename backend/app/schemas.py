from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# Document Schemas
class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size_bytes: int
    status: str
    error_message: Optional[str] = None
    chunk_count: int
    page_count: int
    created_at: Any

    class Config:
        from_attributes = True

# Citation Schema
class Citation(BaseModel):
    document_id: str
    filename: str
    page_number: int
    chunk_id: str
    content: str

# Research Schemas
class ResearchRequest(BaseModel):
    question: str = Field(..., description="Single or multi-question prompt from user")
    document_ids: List[str] = Field(..., description="List of document IDs to query across")

class SingleQuestionAnswer(BaseModel):
    question: str
    answer: str
    sources: List[Citation]
    found_in_document: bool

class ResearchResponse(BaseModel):
    results: List[SingleQuestionAnswer]

# AI Study Notes Schemas
class AIStudyNotesRequest(BaseModel):
    topic: str = Field(..., description="Topic or question for AI study notes")

class NoteSection(BaseModel):
    title: str
    content: List[str] | str

class StudyNotesResponse(BaseModel):
    id: str
    mode: str
    title: str
    topic_or_doc_ids: str
    sections: Dict[str, Any]
    created_at: Any

    class Config:
        from_attributes = True
