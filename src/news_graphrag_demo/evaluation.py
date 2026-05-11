from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import pandas as pd

from .paths import DEFAULT_QUESTIONS_PATH
from .retrieval import RetrievalEngine


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
            rows.append(
                {
                    "id": item.get("id", ""),
                    "question": item["question"],
                    "mode": mode,
                    "expected": item.get("expected", ""),
                    "answer": result.answer,
                    "top_source": result.evidence[0].title if result.evidence else "",
                    "evidence_count": len(result.evidence),
                    "latency_ms": elapsed_ms,
                }
            )
    return pd.DataFrame(rows)


def save_evaluation(df: pd.DataFrame, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "evaluation.csv"
    df.to_csv(path, index=False)
    return path
