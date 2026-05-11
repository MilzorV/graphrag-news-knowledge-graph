from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from .extraction import ExtractionConfig, extract_knowledge
from .graph_store import graph_summary
from .loaders import load_articles
from .models import GraphIndex
from .paths import DEFAULT_OUTPUT_DIR, DEFAULT_SAMPLE_DIR, ensure_dir
from .preprocessing import chunk_articles
from .storage import save_graph_index, save_pickle, save_run_info
from .vector_index import VectorIndex


def build_index(
    *,
    input_path: Path = DEFAULT_SAMPLE_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    extractor_mode: str = "auto",
    ollama_model: str = "llama3.1:8b",
    max_chunk_chars: int = 1200,
    chunk_overlap_chars: int = 160,
) -> dict[str, Any]:
    started = time.perf_counter()
    ensure_dir(output_dir)

    articles = load_articles(input_path)
    if not articles:
        raise ValueError(f"No supported articles found under {input_path}")
    chunks = chunk_articles(articles, max_chars=max_chunk_chars, overlap_chars=chunk_overlap_chars)
    entities, relations = extract_knowledge(
        articles,
        chunks,
        ExtractionConfig(mode=extractor_mode, ollama_model=ollama_model),
    )
    index = GraphIndex(articles=articles, chunks=chunks, entities=entities, relations=relations)
    vector_index = VectorIndex.build(chunks)

    save_graph_index(index, output_dir)
    save_pickle(vector_index, output_dir)
    info = {
        "input_path": str(input_path),
        "output_dir": str(output_dir),
        "extractor_mode": extractor_mode,
        "ollama_model": ollama_model,
        "seconds": round(time.perf_counter() - started, 3),
        "summary": graph_summary(index),
    }
    save_run_info(info, output_dir)
    return info
