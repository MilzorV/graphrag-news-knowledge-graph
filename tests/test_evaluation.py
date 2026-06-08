from __future__ import annotations

from news_graphrag_demo.evaluation import expected_overlap, summarize_evaluation
import pandas as pd


def test_expected_overlap_counts_shared_tokens() -> None:
    expected = "Maria Nowak met GreenGrid Europe at the Warsaw summit."
    answer = "Maria Nowak and GreenGrid Europe appeared at the Warsaw energy summit."
    score = expected_overlap(expected, answer)
    assert score > 0.5


def test_expected_overlap_empty_expected_returns_zero() -> None:
    assert expected_overlap("", "some answer") == 0.0


def test_summarize_evaluation_groups_by_mode() -> None:
    df = pd.DataFrame(
        [
            {"id": "q1", "mode": "graph", "expected_overlap": 0.4, "evidence_count": 5, "latency_ms": 10},
            {"id": "q2", "mode": "vector", "expected_overlap": 0.6, "evidence_count": 4, "latency_ms": 1},
        ]
    )
    summary = summarize_evaluation(df)
    assert set(summary["mode"]) == {"graph", "vector"}
    assert summary.loc[summary["mode"] == "vector", "avg_overlap"].iloc[0] == 0.6
