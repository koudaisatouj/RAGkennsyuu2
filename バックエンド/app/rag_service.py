"""Core orchestration layer that ties together loading, vector search, and answer generation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from openai import OpenAI

from .config import settings
from .document_loader import DocumentLoader, discover_documents
from .vector_store import VectorStore


PROMPT_TEMPLATE = """You are an AI assistant that answers corporate knowledge base questions.
Use ONLY the context sections to answer. If the answer is not contained in the context, say you do not know.
Return the answer in Japanese and cite references in square brackets using the format [source:chunk].

Context:
{context}

Question:
{question}

Answer:
"""


@dataclass
class RetrievedDocument:
    """Normalized representation for API responses."""

    id: str
    content: str
    metadata: Dict[str, str]
    score: Optional[float]


class LLMClient:
    """Thin wrapper over the OpenAI chat completion API."""

    def __init__(self, api_key: str, model: str, temperature: float, max_tokens: int) -> None:
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = OpenAI(api_key=api_key)

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            messages=[
                {"role": "system", "content": "You are a helpful assistant for enterprise knowledge bases."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content or ""


class RAGService:
    """Provides ingestion and question answering capabilities."""

    def __init__(self) -> None:
        self.settings = settings
        self.loader = DocumentLoader(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
        )
        self.vector_store = VectorStore(
            persist_directory=self.settings.vector_store_dir,
            collection_name="documents",
            embedding_model=self.settings.embedding_model,
        )
        self.llm_client: Optional[LLMClient] = None
        if self.settings.openai_api_key:
            self.llm_client = LLMClient(
                api_key=self.settings.openai_api_key,
                model=self.settings.openai_model,
                temperature=self.settings.temperature,
                max_tokens=self.settings.max_answer_tokens,
            )

    def reload_llm(self) -> None:
        """Instantiate the OpenAI client if the key became available later."""
        if not self.settings.openai_api_key:
            raise ValueError("OpenAI API key is not configured")
        self.llm_client = LLMClient(
            api_key=self.settings.openai_api_key,
            model=self.settings.openai_model,
            temperature=self.settings.temperature,
            max_tokens=self.settings.max_answer_tokens,
        )

    def _resolve_targets(self, requested: Optional[Iterable[str]]) -> List[Path]:
        if not requested:
            return discover_documents(self.settings.source_dir)
        resolved_paths: List[Path] = []
        for raw_path in requested:
            candidate = Path(raw_path)
            if not candidate.is_absolute():
                candidate = (self.settings.source_dir / candidate).resolve()
            if candidate.is_file():
                resolved_paths.append(candidate)
        return resolved_paths

    def ingest(self, requested_paths: Optional[Iterable[str]] = None) -> Dict[str, int]:
        """Load documents, chunk, and store them into the vector database."""
        requested_list = list(requested_paths) if requested_paths else None
        targets = self._resolve_targets(requested_list)
        chunks = self.loader.load(targets)
        stored = self.vector_store.add_chunks(chunks)
        return {
            "ingested_files": len(targets),
            "ingested_chunks": stored,
            "skipped_files": max(len(requested_list or []) - len(targets), 0),
        }

    def query(self, question: str, top_k: Optional[int] = None) -> Dict:
        """Answer a user question by retrieving supporting documents and generating an answer."""
        if not question.strip():
            raise ValueError("question must not be empty")
        if not self.llm_client:
            raise RuntimeError("OpenAI API key is not configured")
        k = top_k or self.settings.top_k
        retrieved = self.vector_store.similarity_search(question, k)
        if not retrieved:
            return {
                "question": question,
                "answer": "関連する文書を見つけられませんでした。",
                "prompt": "",
                "sources": [],
            }
        context_lines = []
        normalized_sources: List[RetrievedDocument] = []
        for item in retrieved:
            metadata = item.get("metadata") or {}
            label = f"{metadata.get('source')}:{metadata.get('chunk_index')}"
            context_lines.append(f"[{label}] {item['content']}")
            normalized_sources.append(
                RetrievedDocument(
                    id=item.get("id", ""),
                    content=item["content"],
                    metadata=metadata,
                    score=item.get("score"),
                )
            )
        context_block = "\n".join(context_lines)
        prompt = PROMPT_TEMPLATE.format(context=context_block, question=question)
        answer = self.llm_client.generate(prompt)
        return {
            "question": question,
            "answer": answer.strip(),
            "prompt": prompt,
            "sources": normalized_sources,
        }
