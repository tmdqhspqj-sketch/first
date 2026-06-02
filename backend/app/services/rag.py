import hashlib
from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.services.ollama import ollama_client
from app.settings import settings

COLLECTION_NAME = "documents"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 80


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    text = text.strip()
    if not text:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = end - overlap
    return chunks


class RagStore:
    def __init__(self) -> None:
        settings.chroma_dir.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(
            path=str(settings.chroma_dir),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    @property
    def count(self) -> int:
        return self._collection.count()

    async def ingest_text(self, text: str, source: str = "upload") -> int:
        chunks = _chunk_text(text)
        if not chunks:
            return 0
        ids: list[str] = []
        embeddings: list[list[float]] = []
        documents: list[str] = []
        metadatas: list[dict[str, str]] = []

        for i, chunk in enumerate(chunks):
            doc_id = hashlib.sha256(f"{source}:{i}:{chunk[:64]}".encode()).hexdigest()[:32]
            emb = await ollama_client.embed(chunk)
            ids.append(doc_id)
            embeddings.append(emb)
            documents.append(chunk)
            metadatas.append({"source": source, "chunk_index": str(i)})

        self._collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        return len(chunks)

    async def ingest_file(self, path: Path) -> int:
        text = path.read_text(encoding="utf-8", errors="replace")
        return await self.ingest_text(text, source=path.name)

    async def search(self, query: str, k: int = 4) -> list[dict[str, Any]]:
        if self.count == 0:
            return []
        query_emb = await ollama_client.embed(query)
        result = self._collection.query(
            query_embeddings=[query_emb],
            n_results=min(k, self.count),
            include=["documents", "metadatas", "distances"],
        )
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        dists = result.get("distances", [[]])[0]
        hits: list[dict[str, Any]] = []
        for doc, meta, dist in zip(docs, metas, dists):
            hits.append(
                {
                    "content": doc,
                    "metadata": meta or {},
                    "distance": dist,
                }
            )
        return hits


rag_store = RagStore()
