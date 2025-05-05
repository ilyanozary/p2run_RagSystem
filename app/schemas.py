from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class DocumentBase(BaseModel):
    title: str
    description: Optional[str] = None

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: int
    file_path: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class QuestionBase(BaseModel):
    question: str

class QuestionCreate(QuestionBase):
    document_id: int

class Question(QuestionBase):
    id: int
    document_id: int
    answer: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class SystemStats(BaseModel):
    total_documents: int
    total_questions: int
    last_24h_questions: int 