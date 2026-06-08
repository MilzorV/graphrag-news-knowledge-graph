from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from .paths import DEFAULT_QUESTIONS_PATH
from .retrieval import RetrievalEngine

_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "was",
    "were",
    "with",
}


def _tokenize(text: str) -> set[str]:
    tokens = {token.lower() for token in re.findall(r"[A-Za-z0-9']+", text)}
    return {token for token in tokens if len(token) > 2 and token not in _STOPWORDS}


def expected_overlap(expected: str, answer: str) -> float:
    """Share of expected content tokens present in the generated answer."""
    expected_tokens = _tokenize(expected)
    if not expected_tokens:
        return 0.0
    answer_tokens = _tokenize(answer)
    if not answer_tokens:
        return 0.0
    return len(expected_tokens & answer_tokens) / len(expected_tokens)


def load_questions(path: Path = DEFAULT_QUESTIONS_PATH) -> list[dict[str, str]]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_evaluation(
    engine: RetrievalEngine,
    *,
    questions_path: Path = DEFAULT_QUESTIONS_PATH,
    modes: list[str] | None = None,
    top_k: int = 5,
    use_ollama: bool = False,
    ollama_model: str = "llama3.1:8b",
) -> pd.DataFrame:
    modes = modes or ["keyword", "vector", "graph", "hybrid"]
    rows: list[dict[str, Any]] = []
    for item in load_questions(questions_path):
        for mode in modes:
            started = time.perf_counter()
            result = engine.query(
                item["question"],
                mode=mode,
                top_k=top_k,
                use_ollama=use_ollama,
                ollama_model=ollama_model,
            )
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            expected = item.get("expected", "")
            rows.append(
                {
                    "id": item.get("id", ""),
                    "question": item["question"],
                    "mode": mode,
                    "expected": expected,
                    "answer": result.answer,
                    "expected_overlap": round(expected_overlap(expected, result.answer), 3),
                    "top_source": result.evidence[0].title if result.evidence else "",
                    "evidence_count": len(result.evidence),
                    "latency_ms": elapsed_ms,
                }
            )
    return pd.DataFrame(rows)


def save_evaluation(df: pd.DataFrame, output_dir: Path, *, timestamped: bool = False) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    if timestamped:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = output_dir / f"evaluation_{stamp}.csv"
    else:
        path = output_dir / "evaluation.csv"
    df.to_csv(path, index=False)
    return path


def summarize_evaluation(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate evaluation metrics by retrieval mode."""
    grouped = (
        df.groupby("mode", as_index=False)
        .agg(
            questions=("id", "count"),
            avg_overlap=("expected_overlap", "mean"),
            avg_evidence=("evidence_count", "mean"),
            avg_latency_ms=("latency_ms", "mean"),
        )
        .sort_values("avg_overlap", ascending=False)
    )
    grouped["avg_overlap"] = grouped["avg_overlap"].round(3)
    grouped["avg_evidence"] = grouped["avg_evidence"].round(1)
    grouped["avg_latency_ms"] = grouped["avg_latency_ms"].round(0)
    return grouped
