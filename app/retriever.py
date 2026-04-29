from dataclasses import dataclass
from typing import List
from uuid import uuid4

import chromadb
from sklearn.feature_extraction.text import HashingVectorizer

from app.config import settings


@dataclass
class DocumentChunk:
    title: str
    source: str
    chunk: str


class Retriever:
    def __init__(self) -> None:
        self._client = chromadb.PersistentClient(path=settings.chroma_path)
        self._collection = self._client.get_or_create_collection(name=settings.chroma_collection)
        self._vectorizer = HashingVectorizer(
            n_features=384,
            alternate_sign=False,
            norm="l2",
            stop_words="english",
        )

    @staticmethod
    def _chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> List[str]:
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            if end == len(text):
                break
            start = max(0, end - overlap)
        return chunks

    def ingest(self, title: str, source: str, content: str) -> int:
        chunks = self._chunk_text(content)
        embeddings = self._vectorizer.transform(chunks).toarray().tolist()
        ids = [str(uuid4()) for _ in chunks]
        metadatas = [{"title": title, "source": source} for _ in chunks]
        self._collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        return len(chunks)

    def retrieve(self, query: str, top_k: int) -> List[dict]:
        if self._collection.count() == 0:
            return []
        query_embedding = self._vectorizer.transform([query]).toarray().tolist()[0]
        raw = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )
        docs = raw.get("documents", [[]])[0]
        metas = raw.get("metadatas", [[]])[0]
        distances = raw.get("distances", [[]])[0]

        results = []
        for doc, meta, dist in zip(docs, metas, distances):
            similarity = 1.0 / (1.0 + float(dist))
            results.append(
                {
                    "title": meta.get("title", "unknown"),
                    "source": meta.get("source", "unknown"),
                    "chunk": doc,
                    "score": similarity,
                }
            )
        return results
