#!/usr/bin/env python3
"""Convert a small MIND news subset into the project's article JSON format.

MIND small train split is available from:
  https://msnews.github.io/

Example usage (after downloading MINDsmall_train/news.tsv and MINDsmall_train/behaviors.tsv):

  python scripts/prepare_mind_subset.py \\
    --news MINDsmall_train/news.tsv \\
    --behaviors MINDsmall_train/behaviors.tsv \\
    --output data/corpus_v1/mind_subset.json \\
    --limit 20

This script is optional; the bundled corpus_v1 uses synthetic interconnected articles.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def load_news_rows(news_path: Path) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    with news_path.open(encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            rows[row["News ID"]] = row
    return rows


def pick_news_ids(behaviors_path: Path, limit: int) -> list[str]:
    seen: list[str] = []
    with behaviors_path.open(encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            for news_id in row.get("News", "").split():
                if news_id not in seen:
                    seen.append(news_id)
                if len(seen) >= limit:
                    return seen
    return seen


def to_article(news_id: str, row: dict[str, str]) -> dict[str, str]:
    title = row.get("Title", "").strip()
    abstract = row.get("Abstract", "").strip()
    category = row.get("Category", "").strip()
    body = abstract
    if category:
        body = f"{abstract}\n\nCategory: {category}".strip()
    return {
        "id": news_id,
        "title": title or news_id,
        "source": "MIND",
        "published_at": "",
        "author": "",
        "text": body,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a MIND subset for news-graphrag ingest.")
    parser.add_argument("--news", type=Path, required=True, help="Path to MIND news.tsv")
    parser.add_argument("--behaviors", type=Path, required=True, help="Path to MIND behaviors.tsv")
    parser.add_argument("--output", type=Path, required=True, help="Output JSON file")
    parser.add_argument("--limit", type=int, default=20, help="Maximum number of articles")
    args = parser.parse_args()

    news_rows = load_news_rows(args.news)
    news_ids = pick_news_ids(args.behaviors, args.limit)
    articles = [to_article(news_id, news_rows[news_id]) for news_id in news_ids if news_id in news_rows]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(articles, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(articles)} articles to {args.output}")


if __name__ == "__main__":
    main()
