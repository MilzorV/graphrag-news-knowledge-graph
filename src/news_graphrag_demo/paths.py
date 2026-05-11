from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SAMPLE_DIR = PROJECT_ROOT / "data" / "sample_articles"
DEFAULT_QUESTIONS_PATH = PROJECT_ROOT / "data" / "sample_questions.json"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "demo_index"
DEFAULT_LIGHTRAG_DIR = PROJECT_ROOT / "outputs" / "lightrag"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path
