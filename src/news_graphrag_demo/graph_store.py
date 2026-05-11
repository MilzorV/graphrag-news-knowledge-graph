from __future__ import annotations

from collections import defaultdict
from typing import Any

import networkx as nx

from .models import GraphIndex
from .text_utils import article_node_id


def build_networkx(index: GraphIndex) -> nx.MultiDiGraph:
    graph = nx.MultiDiGraph()
    for article in index.articles:
        graph.add_node(
            article_node_id(article.id),
            id=article_node_id(article.id),
            label=article.title,
            type="Article",
            source=article.source,
            published_at=article.published_at,
        )
    for entity in index.entities:
        graph.add_node(
            entity.id,
            id=entity.id,
            label=entity.name,
            type=entity.type,
            aliases=", ".join(entity.aliases),
            source_doc_count=len(entity.source_doc_ids),
        )
    for relation in index.relations:
        graph.add_edge(
            relation.source,
            relation.target,
            key=relation.id,
            id=relation.id,
            type=relation.type,
            description=relation.description,
            doc_id=relation.doc_id,
            snippet=relation.snippet,
            confidence=relation.confidence,
        )
    return graph


def graph_summary(index: GraphIndex) -> dict[str, Any]:
    node_counts: dict[str, int] = defaultdict(int)
    edge_counts: dict[str, int] = defaultdict(int)
    for article in index.articles:
        node_counts["Article"] += 1
    for entity in index.entities:
        node_counts[entity.type] += 1
    for relation in index.relations:
        edge_counts[relation.type] += 1
    return {
        "articles": len(index.articles),
        "chunks": len(index.chunks),
        "nodes": len(index.articles) + len(index.entities),
        "edges": len(index.relations),
        "node_counts": dict(sorted(node_counts.items())),
        "edge_counts": dict(sorted(edge_counts.items())),
    }


def subgraph_payload(graph: nx.MultiDiGraph, node_ids: set[str], *, max_nodes: int = 80) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    selected = list(node_ids)[:max_nodes]
    selected_set = set(selected)
    nodes = [
        {
            "id": node_id,
            "label": graph.nodes[node_id].get("label", node_id),
            "type": graph.nodes[node_id].get("type", "Unknown"),
        }
        for node_id in selected
        if node_id in graph
    ]
    edges: list[dict[str, Any]] = []
    for source, target, key, attrs in graph.edges(keys=True, data=True):
        if source in selected_set and target in selected_set:
            edges.append(
                {
                    "id": key,
                    "source": source,
                    "target": target,
                    "type": attrs.get("type", "RELATED_TO"),
                    "description": attrs.get("description", ""),
                    "doc_id": attrs.get("doc_id", ""),
                }
            )
    return nodes, edges
