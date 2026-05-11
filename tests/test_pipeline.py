from __future__ import annotations

from pathlib import Path

from news_graphrag_demo.graph_store import graph_summary
from news_graphrag_demo.paths import DEFAULT_SAMPLE_DIR
from news_graphrag_demo.pipeline import build_index
from news_graphrag_demo.retrieval import RetrievalEngine
from news_graphrag_demo.storage import load_graph_index


def test_build_index_creates_graph_and_vector_artifacts(tmp_path: Path) -> None:
    info = build_index(input_path=DEFAULT_SAMPLE_DIR, output_dir=tmp_path, extractor_mode="heuristic")

    assert (tmp_path / "index.json").exists()
    assert (tmp_path / "vector_index.pkl").exists()
    assert info["summary"]["articles"] >= 8
    assert info["summary"]["nodes"] > info["summary"]["articles"]
    assert info["summary"]["edges"] > 0

    index = load_graph_index(tmp_path)
    summary = graph_summary(index)
    assert summary["node_counts"]["EVENT"] >= 1
    assert summary["edge_counts"]["MENTIONS"] >= summary["articles"]


def test_hybrid_query_returns_evidence(tmp_path: Path) -> None:
    build_index(input_path=DEFAULT_SAMPLE_DIR, output_dir=tmp_path, extractor_mode="heuristic")
    engine = RetrievalEngine.from_output_dir(tmp_path)

    result = engine.query("What connects Maria Nowak with GreenGrid Europe?", mode="hybrid", top_k=5)

    assert result.evidence
    assert result.graph_nodes
    assert any("GreenGrid" in item.snippet or "Maria Nowak" in item.snippet for item in result.evidence)
