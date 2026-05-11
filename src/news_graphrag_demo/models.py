from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class Article:
    id: str
    title: str
    text: str
    source: str = ""
    published_at: str = ""
    author: str = ""
    path_or_url: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Chunk:
    id: str
    article_id: str
    title: str
    text: str
    chunk_index: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Entity:
    id: str
    name: str
    type: str
    aliases: list[str] = field(default_factory=list)
    source_doc_ids: list[str] = field(default_factory=list)
    snippets: list[str] = field(default_factory=list)
    confidence: float = 0.6

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Relation:
    id: str
    source: str
    target: str
    type: str
    description: str
    doc_id: str
    snippet: str
    confidence: float = 0.6

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class GraphIndex:
    articles: list[Article]
    chunks: list[Chunk]
    entities: list[Entity]
    relations: list[Relation]

    def to_dict(self) -> dict[str, Any]:
        return {
            "articles": [item.to_dict() for item in self.articles],
            "chunks": [item.to_dict() for item in self.chunks],
            "entities": [item.to_dict() for item in self.entities],
            "relations": [item.to_dict() for item in self.relations],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GraphIndex":
        return cls(
            articles=[Article(**item) for item in data.get("articles", [])],
            chunks=[Chunk(**item) for item in data.get("chunks", [])],
            entities=[Entity(**item) for item in data.get("entities", [])],
            relations=[Relation(**item) for item in data.get("relations", [])],
        )


@dataclass(slots=True)
class Evidence:
    doc_id: str
    title: str
    snippet: str
    score: float
    source: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class QueryResult:
    question: str
    mode: str
    answer: str
    evidence: list[Evidence]
    graph_nodes: list[dict[str, Any]]
    graph_edges: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "mode": self.mode,
            "answer": self.answer,
            "evidence": [item.to_dict() for item in self.evidence],
            "graph_nodes": self.graph_nodes,
            "graph_edges": self.graph_edges,
        }
