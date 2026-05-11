from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .models import Chunk


@dataclass(slots=True)
class VectorIndex:
    vectorizer: TfidfVectorizer
    matrix: object
    chunk_ids: list[str]

    @classmethod
    def build(cls, chunks: list[Chunk]) -> "VectorIndex":
        texts = [_chunk_text(chunk) for chunk in chunks]
        vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
            max_features=12000,
        )
        matrix = vectorizer.fit_transform(texts)
        return cls(vectorizer=vectorizer, matrix=matrix, chunk_ids=[chunk.id for chunk in chunks])

    def search(self, query: str, chunks_by_id: dict[str, Chunk], *, top_k: int = 5) -> list[tuple[Chunk, float]]:
        if not self.chunk_ids:
            return []
        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.matrix).ravel()
        top_indices = np.argsort(scores)[::-1][:top_k]
        results: list[tuple[Chunk, float]] = []
        for idx in top_indices:
            score = float(scores[idx])
            if score <= 0:
                continue
            chunk = chunks_by_id.get(self.chunk_ids[idx])
            if chunk:
                results.append((chunk, score))
        return results


def _chunk_text(chunk: Chunk) -> str:
    return f"{chunk.title}\n\n{chunk.text}"
