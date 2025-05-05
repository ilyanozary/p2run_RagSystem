from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from datetime import datetime, timedelta

from app.model import get_answer
from app.database import get_db, Document, Question
from app.schemas import DocumentCreate, Document as DocumentSchema
from app.schemas import QuestionCreate, Question as QuestionSchema
from app.schemas import SystemStats

app = FastAPI(title="Document QA API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.post("/documents/", response_model=DocumentSchema)
async def create_document(
    title: str = Form(...),
    description: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Save file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create document in database
    db_document = Document(
        title=title,
        description=description,
        file_path=file_path
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return db_document

@app.get("/documents/", response_model=List[DocumentSchema])
def get_documents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    documents = db.query(Document).offset(skip).limit(limit).all()
    return documents

@app.get("/documents/{document_id}", response_model=DocumentSchema)
def get_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@app.delete("/documents/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    # Delete from database
    db.delete(document)
    db.commit()
    return {"message": "Document deleted"}

@app.post("/documents/{document_id}/ask", response_model=QuestionSchema)
async def ask_question(
    document_id: int,
    question: str = Form(...),
    db: Session = Depends(get_db)
):
    document = db.query(Document).filter(Document.id == document_id).first()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    # Get answer using the model
    answer = get_answer(document.file_path, question)
    
    # Save question and answer
    db_question = Question(
        question=question,
        answer=answer,
        document_id=document_id
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    
    return db_question

@app.get("/questions/", response_model=List[QuestionSchema])
def get_questions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    questions = db.query(Question).offset(skip).limit(limit).all()
    return questions

@app.get("/questions/{question_id}", response_model=QuestionSchema)
def get_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return question

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.get("/stats", response_model=SystemStats)
def get_stats(db: Session = Depends(get_db)):
    total_documents = db.query(Document).count()
    total_questions = db.query(Question).count()
    last_24h = datetime.utcnow() - timedelta(days=1)
    last_24h_questions = db.query(Question).filter(Question.created_at >= last_24h).count()
    
    return SystemStats(
        total_documents=total_documents,
        total_questions=total_questions,
        last_24h_questions=last_24h_questions
    )
