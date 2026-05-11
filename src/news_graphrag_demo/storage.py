from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any

from .models import GraphIndex
from .paths import ensure_dir


INDEX_FILE = "index.json"
VECTOR_FILE = "vector_index.pkl"
RUN_INFO_FILE = "run_info.json"


def save_graph_index(index: GraphIndex, output_dir: Path) -> Path:
    ensure_dir(output_dir)
    path = output_dir / INDEX_FILE
    path.write_text(json.dumps(index.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def load_graph_index(output_dir: Path) -> GraphIndex:
    path = output_dir / INDEX_FILE
    return GraphIndex.from_dict(json.loads(path.read_text(encoding="utf-8")))


def save_pickle(value: Any, output_dir: Path, filename: str = VECTOR_FILE) -> Path:
    ensure_dir(output_dir)
    path = output_dir / filename
    with path.open("wb") as handle:
        pickle.dump(value, handle)
    return path


def load_pickle(output_dir: Path, filename: str = VECTOR_FILE) -> Any:
    with (output_dir / filename).open("rb") as handle:
        return pickle.load(handle)


def save_run_info(info: dict[str, Any], output_dir: Path) -> Path:
    ensure_dir(output_dir)
    path = output_dir / RUN_INFO_FILE
    path.write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
