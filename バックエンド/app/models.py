"""Pydantic models for API request and response payloads."""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    environment: str


class IngestRequest(BaseModel):
    paths: Optional[List[str]] = Field(
        default=None,
        description="Specific document paths (relative to the source directory) to ingest.",
    )


class IngestResponse(BaseModel):
    ingested_files: int
    ingested_chunks: int
    skipped_files: int
    detail: str


class QuestionRequest(BaseModel):
    question: str = Field(..., description="User question in natural language.")
    top_k: Optional[int] = Field(
        default=None,
        description="Override for number of documents to retrieve.",
    )


class SourceDocument(BaseModel):
    id: str
    content: str
    metadata: Dict[str, str]
    score: Optional[float]


class AnswerResponse(BaseModel):
    question: str
    answer: str
    prompt: str
    sources: List[SourceDocument]
