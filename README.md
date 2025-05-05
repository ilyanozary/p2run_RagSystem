# P2Run RAG System

A Question-Answering system built with FastAPI and LangChain that allows users to upload documents and ask questions about them.

## Features

- Document Management (Upload, List, Delete)
- Question & Answer using LLM (Llama 2)
- Document embedding and semantic search
- API-based architecture
- SQLite database for persistence
- Comprehensive test suite

## Tech Stack

- FastAPI
- LangChain
- Llama 2
- FAISS
- SQLAlchemy
- pytest

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ilyanozary/p2run_RagSystem.git
cd p2run_RagSystem
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
uvicorn app.main:app --reload
```

4. Access the API documentation:
```
http://localhost:8000/docs
```

## API Endpoints

### Documents
- `POST /documents/` - Upload a new document
- `GET /documents/` - List all documents
- `GET /documents/{id}` - Get document details
- `DELETE /documents/{id}` - Delete a document

### Questions
- `POST /documents/{id}/ask` - Ask a question about a document
- `GET /questions/` - List all questions
- `GET /questions/{id}` - Get question details

### System
- `GET /health` - Check system health
- `GET /stats` - Get system statistics

## Testing

Run tests with:
```bash
pytest tests/
```

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── model.py         # LLM and embedding models
│   ├── database.py      # Database models
│   └── schemas.py       # Pydantic schemas
├── tests/
│   ├── __init__.py
│   ├── test_main.py     # API tests
│   └── conftest.py      # Test configurations
├── requirements.txt
└── README.md
``` 