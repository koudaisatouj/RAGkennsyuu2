"""FastAPI entrypoint for the RAG question answering backend."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .document_loader import SUPPORTED_EXTENSIONS
from .models import (
    AnswerResponse,
    HealthResponse,
    IngestRequest,
    IngestResponse,
    QuestionRequest,
    SourceDocument,
)
from .rag_service import RAGService, RetrievedDocument

app = FastAPI(title="RAG問合せ応答システム", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_service = RAGService()


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Simple health check endpoint."""
    return HealthResponse(status="ok", environment=settings.environment_name)


@app.post("/ingest", response_model=IngestResponse)
async def ingest_documents(payload: IngestRequest) -> IngestResponse:
    """Trigger ingestion for all supported documents or the provided subset."""
    stats = rag_service.ingest(payload.paths)
    detail = f"{stats['ingested_chunks']} chunks stored from {stats['ingested_files']} files."
    return IngestResponse(detail=detail, **stats)


@app.post("/query", response_model=AnswerResponse)
async def ask_question(payload: QuestionRequest) -> AnswerResponse:
    """Answer a user question and return supporting citations."""
    try:
        result = rag_service.query(payload.question, payload.top_k)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    sources = [
        SourceDocument(
            id=doc.id,
            content=doc.content,
            metadata=doc.metadata,
            score=doc.score,
        )
        for doc in result["sources"]
    ]
    return AnswerResponse(
        question=result["question"],
        answer=result["answer"],
        prompt=result["prompt"],
        sources=sources,
    )


@app.post("/documents/upload", response_model=IngestResponse)
async def upload_document(file: UploadFile = File(...)) -> IngestResponse:
    """Upload a new document and ingest it immediately."""
    extension = Path(file.filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400, detail=f"Unsupported file type: {extension}. Allowed: {', '.join(SUPPORTED_EXTENSIONS)}"
        )
    contents = await file.read()
    size_limit = settings.allow_upload_size_mb * 1024 * 1024
    if len(contents) > size_limit:
        raise HTTPException(status_code=400, detail="File is too large.")
    destination = settings.source_dir / Path(file.filename).name
    destination.write_bytes(contents)
    stats = rag_service.ingest([str(destination)])
    detail = f"Uploaded {file.filename} and stored {stats['ingested_chunks']} chunks."
    return IngestResponse(detail=detail, **stats)
