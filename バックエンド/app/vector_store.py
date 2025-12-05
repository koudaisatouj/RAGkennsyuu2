"""Wrapper around ChromaDB for persisting embeddings and running similarity search."""

from __future__ import annotations

import uuid
from typing import Dict, Iterable, List, Sequence

import chromadb
from chromadb.api import ClientAPI
from chromadb.api.types import Documents, EmbeddingFunction
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions

from .document_loader import DocumentChunk


class VectorStore:
    """Encapsulates the ChromaDB collection operations."""

    def __init__(
        self,
        persist_directory,
        collection_name: str,
        embedding_model: str,
    ) -> None:
        self.persist_directory = str(persist_directory)
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.client: ClientAPI = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.collection = self._init_collection()

    def _init_collection(self):
        embedding_fn: EmbeddingFunction = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=self.embedding_model
        )
        return self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=embedding_fn,
        )

    def add_chunks(self, chunks: Iterable[DocumentChunk]) -> int:
        """Store chunks inside the collection."""
        documents: Documents = []
        metadatas: List[Dict[str, str]] = []
        ids: List[str] = []
        for chunk in chunks:
            documents.append(chunk.content)
            metadatas.append(chunk.metadata)
            ids.append(str(uuid.uuid4()))
        if not documents:
            return 0
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )
        return len(documents)

    def similarity_search(self, query: str, top_k: int) -> List[Dict]:
        """Run a similarity search and return normalized results."""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
        )
        normalized: List[Dict] = []
        if not results or not results.get("documents"):
            return normalized
        docs: Sequence[Sequence[str]] = results["documents"]
        metadatas: Sequence[Sequence[Dict]] = results.get("metadatas", [])
        distances: Sequence[Sequence[float]] = results.get("distances", [])
        ids: Sequence[Sequence[str]] = results.get("ids", [])
        for index, document in enumerate(docs[0]):
            normalized.append(
                {
                    "id": ids[0][index] if ids else "",
                    "content": document,
                    "metadata": metadatas[0][index] if metadatas else {},
                    "score": distances[0][index] if distances else None,
                }
            )
        return normalized
