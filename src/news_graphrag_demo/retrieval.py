from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from typing import Iterable

import networkx as nx

from .generation import generate_answer
from .graph_store import build_networkx, subgraph_payload
from .models import Chunk, Evidence, GraphIndex, QueryResult
from .storage import load_graph_index, load_pickle
from .text_utils import article_node_id, canonical_key
from .vector_index import VectorIndex


WORD_RE = re.compile(r"[a-z0-9]{3,}")


class RetrievalEngine:
    def __init__(self, index: GraphIndex, vector_index: VectorIndex | None = None):
        self.index = index
        self.vector_index = vector_index
        self.graph = build_networkx(index)
        self.articles_by_id = {article.id: article for article in index.articles}
        self.chunks_by_id = {chunk.id: chunk for chunk in index.chunks}
        self.chunks_by_article = _group_chunks_by_article(index.chunks)
        self.entities_by_id = {entity.id: entity for entity in index.entities}

    @classmethod
    def from_output_dir(cls, output_dir: Path) -> "RetrievalEngine":
        index = load_graph_index(output_dir)
        try:
            vector_index = load_pickle(output_dir)
        except FileNotFoundError:
            vector_index = None
        return cls(index, vector_index)

    def query(
        self,
        question: str,
        *,
        mode: str = "hybrid",
        top_k: int = 5,
        use_ollama: bool = False,
        ollama_model: str = "llama3.1:8b",
    ) -> QueryResult:
        mode = mode.lower()
        if mode == "keyword":
            evidence, nodes = self._keyword(question, top_k=top_k)
        elif mode == "vector":
            evidence, nodes = self._vector(question, top_k=top_k)
        elif mode == "graph":
            evidence, nodes = self._graph(question, top_k=top_k)
        elif mode == "hybrid":
            evidence, nodes = self._hybrid(question, top_k=top_k)
        else:
            raise ValueError(f"Unknown retrieval mode: {mode}")
        graph_nodes, graph_edges = subgraph_payload(self.graph, nodes)
        answer = generate_answer(question, evidence, mode=mode, use_ollama=use_ollama, ollama_model=ollama_model)
        return QueryResult(
            question=question,
            mode=mode,
            answer=answer,
            evidence=evidence,
            graph_nodes=graph_nodes,
            graph_edges=graph_edges,
        )

    def _keyword(self, question: str, *, top_k: int) -> tuple[list[Evidence], set[str]]:
        query_terms = set(_terms(question))
        scored: list[tuple[Chunk, float]] = []
        for chunk in self.index.chunks:
            text_terms = _terms(f"{chunk.title} {chunk.text}")
            overlap = query_terms & set(text_terms)
            if overlap:
                scored.append((chunk, len(overlap) / max(1, len(query_terms))))
        scored.sort(key=lambda item: item[1], reverse=True)
        return self._evidence_from_chunks(scored[:top_k], "keyword")

    def _vector(self, question: str, *, top_k: int) -> tuple[list[Evidence], set[str]]:
        if not self.vector_index:
            return [], set()
        scored = self.vector_index.search(question, self.chunks_by_id, top_k=top_k)
        return self._evidence_from_chunks(scored, "vector")

    def _graph(self, question: str, *, top_k: int) -> tuple[list[Evidence], set[str]]:
        seeds = self._match_entities(question)
        if not seeds:
            return self._keyword(question, top_k=top_k)

        nodes: set[str] = set(seeds)
        relation_scores: dict[str, float] = defaultdict(float)
        for seed in seeds:
            if seed not in self.graph:
                continue
            for source, target, key, attrs in self._walk_edges(seed, hops=2):
                nodes.update({source, target})
                relation_scores[key] = max(
                    relation_scores[key],
                    _relation_weight(attrs.get("type", "RELATED_TO"), question) + float(attrs.get("confidence", 0.5)),
                )

        evidence = self._evidence_from_relations(relation_scores, top_k=top_k, source="graph")
        return evidence, nodes

    def _hybrid(self, question: str, *, top_k: int) -> tuple[list[Evidence], set[str]]:
        graph_evidence, graph_nodes = self._graph(question, top_k=top_k)
        vector_evidence, vector_nodes = self._vector(question, top_k=top_k)
        keyword_evidence, keyword_nodes = self._keyword(question, top_k=max(2, top_k // 2))
        merged = _merge_evidence([graph_evidence, vector_evidence, keyword_evidence], top_k=top_k)
        return merged, graph_nodes | vector_nodes | keyword_nodes

    def _match_entities(self, question: str) -> list[str]:
        q_key = canonical_key(question)
        matches: list[tuple[str, int]] = []
        for entity in self.index.entities:
            names = [entity.name, *entity.aliases]
            for name in names:
                key = canonical_key(name)
                if not key:
                    continue
                if key in q_key:
                    matches.append((entity.id, len(key)))
                    break
                words = key.split()
                if len(words) > 1 and any(word in q_key.split() for word in words):
                    matches.append((entity.id, len(key) // 2))
                    break
        matches.sort(key=lambda item: item[1], reverse=True)
        return [entity_id for entity_id, _ in matches[:8]]

    def _walk_edges(self, seed: str, *, hops: int) -> Iterable[tuple[str, str, str, dict]]:
        frontier = {seed}
        seen = {seed}
        for _ in range(hops):
            next_frontier: set[str] = set()
            for node_id in frontier:
                for source, target, key, attrs in self.graph.out_edges(node_id, keys=True, data=True):
                    yield source, target, key, attrs
                    if target not in seen:
                        seen.add(target)
                        next_frontier.add(target)
                for source, target, key, attrs in self.graph.in_edges(node_id, keys=True, data=True):
                    yield source, target, key, attrs
                    if source not in seen:
                        seen.add(source)
                        next_frontier.add(source)
            frontier = next_frontier

    def _evidence_from_chunks(self, scored: list[tuple[Chunk, float]], source: str) -> tuple[list[Evidence], set[str]]:
        evidence: list[Evidence] = []
        nodes: set[str] = set()
        for chunk, score in scored:
            article = self.articles_by_id.get(chunk.article_id)
            if not article:
                continue
            nodes.add(article_node_id(article.id))
            evidence.append(
                Evidence(
                    doc_id=article.id,
                    title=article.title,
                    snippet=chunk.text,
                    score=float(score),
                    source=source,
                )
            )
        return evidence, nodes

    def _evidence_from_relations(self, relation_scores: dict[str, float], *, top_k: int, source: str) -> list[Evidence]:
        relation_by_id = {relation.id: relation for relation in self.index.relations}
        rows = sorted(relation_scores.items(), key=lambda item: item[1], reverse=True)
        evidence: list[Evidence] = []
        seen_docs: set[tuple[str, str]] = set()
        for relation_id, score in rows:
            relation = relation_by_id.get(relation_id)
            if not relation:
                continue
            article = self.articles_by_id.get(relation.doc_id)
            if not article:
                continue
            key = (article.id, relation.snippet)
            if key in seen_docs:
                continue
            seen_docs.add(key)
            evidence.append(
                Evidence(
                    doc_id=article.id,
                    title=article.title,
                    snippet=f"{relation.description} Evidence: {relation.snippet}",
                    score=float(score),
                    source=source,
                )
            )
            if len(evidence) >= top_k:
                break
        return evidence


def _group_chunks_by_article(chunks: list[Chunk]) -> dict[str, list[Chunk]]:
    grouped: dict[str, list[Chunk]] = defaultdict(list)
    for chunk in chunks:
        grouped[chunk.article_id].append(chunk)
    return dict(grouped)


def _terms(text: str) -> list[str]:
    return WORD_RE.findall(canonical_key(text))


def _merge_evidence(groups: list[list[Evidence]], *, top_k: int) -> list[Evidence]:
    merged: dict[tuple[str, str], Evidence] = {}
    for weight, group in zip([1.35, 1.0, 0.75], groups, strict=False):
        for item in group:
            key = (item.doc_id, item.snippet[:120])
            score = item.score * weight
            if key not in merged or score > merged[key].score:
                merged[key] = Evidence(
                    doc_id=item.doc_id,
                    title=item.title,
                    snippet=item.snippet,
                    score=score,
                    source=item.source,
                )
    return sorted(merged.values(), key=lambda item: item.score, reverse=True)[:top_k]


def _relation_weight(relation_type: str, question: str) -> float:
    q_terms = set(_terms(question))
    relation_type = relation_type.upper()
    if {"where", "location", "place"} & q_terms and relation_type in {"OCCURRED_AT", "LOCATED_IN"}:
        return 4.0
    if {"when", "date", "time"} & q_terms and relation_type == "OCCURRED_ON":
        return 4.0
    if {"who", "people", "person", "participants"} & q_terms and relation_type in {"PARTICIPATED_IN", "INVOLVED_IN"}:
        return 3.2
    if {"connects", "connected", "connection", "between", "linked"} & q_terms and relation_type in {
        "RELATED_TO",
        "PARTICIPATED_IN",
        "INVOLVED_IN",
        "AFFILIATED_WITH",
    }:
        return 2.8
    if relation_type == "MENTIONS":
        return 0.4
    if relation_type == "RELATED_TO":
        return 1.0
    return 1.8
