import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from datetime import datetime
from pathlib import Path

from app.main import app
from app.database import Base, get_db
from app.model import get_answer

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite://"  
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

TEST_UPLOAD_DIR = "test_uploads"
if not os.path.exists(TEST_UPLOAD_DIR):
    os.makedirs(TEST_UPLOAD_DIR)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def mock_get_answer(file_path: str, question: str) -> str:
    return f"Mocked answer for question: {question}"

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides["app.model.get_answer"] = mock_get_answer

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

def test_create_document():
    # Create a test file
    test_file_path = Path(TEST_UPLOAD_DIR) / "test.docx"
    test_file_path.write_text("Test content")
    
    with open(test_file_path, "rb") as f:
        response = client.post(
            "/documents/",
            data={
                "title": "Test Document",
                "description": "Test Description"
            },
            files={"file": ("test.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Document"
    assert data["description"] == "Test Description"
    assert "id" in data
    assert "file_path" in data
    assert "created_at" in data

def test_get_documents():
    response = client.get("/documents/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "id" in data[0]
        assert "title" in data[0]

def test_get_document():
    # First create a document
    test_file_path = Path(TEST_UPLOAD_DIR) / "test2.docx"
    test_file_path.write_text("Test content")
    
    with open(test_file_path, "rb") as f:
        create_response = client.post(
            "/documents/",
            data={
                "title": "Test Document 2",
                "description": "Test Description 2"
            },
            files={"file": ("test2.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        )
    
    document_id = create_response.json()["id"]
    
    # Then get it
    response = client.get(f"/documents/{document_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == document_id
    assert data["title"] == "Test Document 2"

def test_delete_document():
    # First create a document
    test_file_path = Path(TEST_UPLOAD_DIR) / "test3.docx"
    test_file_path.write_text("Test content")
    
    with open(test_file_path, "rb") as f:
        create_response = client.post(
            "/documents/",
            data={
                "title": "Test Document 3",
                "description": "Test Description 3"
            },
            files={"file": ("test3.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        )
    
    document_id = create_response.json()["id"]
    
    # Then delete it
    response = client.delete(f"/documents/{document_id}")
    assert response.status_code == 200
    
    # Verify it's deleted
    get_response = client.get(f"/documents/{document_id}")
    assert get_response.status_code == 404

def test_ask_question():
    # First create a document
    test_file_path = Path(TEST_UPLOAD_DIR) / "test4.docx"
    test_file_path.write_text("Test content")
    
    with open(test_file_path, "rb") as f:
        create_response = client.post(
            "/documents/",
            data={
                "title": "Test Document 4",
                "description": "Test Description 4"
            },
            files={"file": ("test4.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        )
    
    document_id = create_response.json()["id"]
    
    # Then ask a question
    response = client.post(
        f"/documents/{document_id}/ask",
        data={"question": "What is this document about?"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == "What is this document about?"
    assert "answer" in data
    assert data["document_id"] == document_id

def test_get_questions():
    response = client.get("/questions/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "id" in data[0]
        assert "question" in data[0]
        assert "answer" in data[0]

def test_get_stats():
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_documents" in data
    assert "total_questions" in data
    assert "last_24h_questions" in data

def test_document_not_found():
    response = client.get("/documents/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"

def test_question_not_found():
    response = client.get("/questions/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Question not found"

# Cleanup after tests
def teardown_module(module):
    import shutil
    if os.path.exists(TEST_UPLOAD_DIR):
        shutil.rmtree(TEST_UPLOAD_DIR) 