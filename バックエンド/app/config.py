"""Configuration management for the RAG system."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or defaults."""

    base_dir: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parents[1],
        description="Base directory for the backend project.",
    )
    source_dir: Path = Field(
        default_factory=lambda: Path("data/source_documents"),
        description="Directory that stores raw documents to ingest.",
    )
    vector_store_dir: Path = Field(
        default_factory=lambda: Path("data/vector_store"),
        description="Directory for persistent Chroma collections.",
    )
    embedding_model: str = Field(
        default="intfloat/multilingual-e5-small",
        description="SentenceTransformers model used to embed text.",
    )
    openai_api_key: Optional[str] = Field(
        default=None,
        description="API key for OpenAI. Required for answer generation.",
    )
    openai_model: str = Field(
        default="gpt-4o-mini",
        description="Chat completion model to use for answer generation.",
    )
    temperature: float = Field(
        default=0.2,
        description="Sampling temperature passed to the LLM.",
    )
    max_answer_tokens: int = Field(
        default=512,
        description="Maximum number of tokens to request from the LLM.",
    )
    chunk_size: int = Field(
        default=800,
        description="Maximum number of characters per chunk.",
    )
    chunk_overlap: int = Field(
        default=200,
        description="Overlap size between adjacent chunks.",
    )
    top_k: int = Field(
        default=5,
        description="Number of documents to retrieve during similarity search.",
    )
    allow_upload_size_mb: int = Field(
        default=15,
        description="Maximum upload size for a single document through the API.",
    )
    environment_name: str = Field(
        default="development",
        description="Environment identifier for observability.",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="RAG_",
        extra="ignore",
    )

    def resolve_paths(self) -> None:
        """Ensure directories exist and convert relative paths to absolute ones."""
        self.source_dir = self._resolve_and_prepare(self.source_dir)
        self.vector_store_dir = self._resolve_and_prepare(self.vector_store_dir)

    def _resolve_and_prepare(self, path_value: Path) -> Path:
        resolved = path_value
        if not resolved.is_absolute():
            resolved = (self.base_dir / resolved).resolve()
        resolved.mkdir(parents=True, exist_ok=True)
        return resolved


settings = Settings()
settings.resolve_paths()
