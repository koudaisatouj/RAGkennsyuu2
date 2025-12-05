"""Utilities for loading and chunking documents that will be embedded."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md", ".markdown"}


@dataclass
class DocumentChunk:
    """Represents a document chunk with metadata."""

    content: str
    metadata: Dict[str, str]


class DocumentLoader:
    """Loads and chunks text documents from disk."""

    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load(self, target_paths: Iterable[Path]) -> List[DocumentChunk]:
        """Load documents from the provided paths."""
        chunks: List[DocumentChunk] = []
        for file_path in target_paths:
            if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue
            text = self._read_file(file_path)
            if not text.strip():
                continue
            chunks.extend(self._chunk_document(text, file_path))
        return chunks

    def _read_file(self, file_path: Path) -> str:
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            return self._read_pdf(file_path)
        return file_path.read_text(encoding="utf-8")

    def _read_pdf(self, file_path: Path) -> str:
        reader = PdfReader(str(file_path))
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        return "\n".join(pages)

    def _chunk_document(self, text: str, file_path: Path) -> List[DocumentChunk]:
        normalized = " ".join(text.split())
        chunks: List[DocumentChunk] = []
        start = 0
        index = 0
        while start < len(normalized):
            end = min(len(normalized), start + self.chunk_size)
            chunk_text = normalized[start:end].strip()
            if chunk_text:
                metadata = {
                    "source": file_path.name,
                    "path": str(file_path),
                    "chunk_index": str(index),
                }
                chunks.append(DocumentChunk(content=chunk_text, metadata=metadata))
            index += 1
            start += self.chunk_size - self.chunk_overlap
            if self.chunk_size <= self.chunk_overlap:
                break
        return chunks


def discover_documents(root_dir: Path) -> List[Path]:
    """Return a sorted list of supported document files inside the directory."""
    files = []
    for path in root_dir.glob("**/*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(path)
    return sorted(files)
