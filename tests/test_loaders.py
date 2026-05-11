from __future__ import annotations

from news_graphrag_demo.loaders import load_articles
from news_graphrag_demo.paths import DEFAULT_SAMPLE_DIR
from news_graphrag_demo.preprocessing import chunk_articles


def test_sample_articles_load_and_chunk() -> None:
    articles = load_articles(DEFAULT_SAMPLE_DIR)
    chunks = chunk_articles(articles, max_chars=500)

    assert len(articles) == 8
    assert all(article.id and article.title and article.text for article in articles)
    assert len(chunks) >= len(articles)
    assert all(chunk.article_id for chunk in chunks)
