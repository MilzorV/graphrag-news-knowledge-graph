from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .models import Article
from .text_utils import slugify


SUPPORTED_SUFFIXES = {".txt", ".md", ".json", ".csv"}


def load_articles(path: Path) -> list[Article]:
    path = path.expanduser().resolve()
    if path.is_file():
        files = [path]
    else:
        files = sorted(item for item in path.rglob("*") if item.suffix.lower() in SUPPORTED_SUFFIXES)

    articles: list[Article] = []
    for file_path in files:
        suffix = file_path.suffix.lower()
        if suffix in {".txt", ".md"}:
            articles.extend(_load_text_file(file_path))
        elif suffix == ".json":
            articles.extend(_load_json_file(file_path))
        elif suffix == ".csv":
            articles.extend(_load_csv_file(file_path))

    seen: dict[str, int] = {}
    for article in articles:
        base_id = slugify(article.id or article.title or article.path_or_url)
        count = seen.get(base_id, 0)
        seen[base_id] = count + 1
        article.id = base_id if count == 0 else f"{base_id}-{count + 1}"
    return articles


def _load_text_file(path: Path) -> list[Article]:
    text = path.read_text(encoding="utf-8")
    title = _title_from_text(text) or path.stem.replace("_", " ").replace("-", " ").title()
    if path.suffix.lower() == ".md":
        text = "\n".join(line for line in text.splitlines() if not line.strip().startswith("# "))
    return [
        Article(
            id=path.stem,
            title=title,
            text=text.strip(),
            source="local file",
            path_or_url=str(path),
        )
    ]


def _load_json_file(path: Path) -> list[Article]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "articles" in data:
        rows = data["articles"]
    elif isinstance(data, list):
        rows = data
    elif isinstance(data, dict):
        rows = [data]
    else:
        raise ValueError(f"Unsupported JSON article shape in {path}")
    return [_article_from_mapping(row, path) for row in rows]


def _load_csv_file(path: Path) -> list[Article]:
    rows: list[Article] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            rows.append(_article_from_mapping(row, path))
    return rows


def _article_from_mapping(row: dict[str, Any], path: Path) -> Article:
    text = str(row.get("text") or row.get("body") or row.get("content") or row.get("abstract") or "").strip()
    title = str(row.get("title") or _title_from_text(text) or path.stem).strip()
    article_id = str(row.get("id") or row.get("document_id") or title or path.stem)
    return Article(
        id=article_id,
        title=title,
        text=text,
        source=str(row.get("source") or row.get("publisher") or "local file"),
        published_at=str(row.get("published_at") or row.get("date") or ""),
        author=str(row.get("author") or ""),
        path_or_url=str(row.get("url") or path),
    )


def _title_from_text(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            return line.lstrip("#").strip()
        if len(line) <= 120:
            return line
        return ""
    return ""
