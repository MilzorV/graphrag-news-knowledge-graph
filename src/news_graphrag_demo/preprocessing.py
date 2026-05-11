from __future__ import annotations

import re

from .models import Article, Chunk


BOILERPLATE_LINES = {
    "subscribe to our newsletter",
    "all rights reserved",
    "advertisement",
}


def clean_text(text: str) -> str:
    lines: list[str] = []
    for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        line = re.sub(r"[ \t]+", " ", line).strip()
        if not line:
            lines.append("")
            continue
        if line.lower() in BOILERPLATE_LINES:
            continue
        lines.append(line)
    cleaned = "\n".join(lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def chunk_articles(
    articles: list[Article],
    *,
    max_chars: int = 1200,
    overlap_chars: int = 160,
) -> list[Chunk]:
    chunks: list[Chunk] = []
    for article in articles:
        paragraphs = [p.strip() for p in clean_text(article.text).split("\n\n") if p.strip()]
        if not paragraphs:
            continue
        buffer = ""
        chunk_index = 0
        for paragraph in paragraphs:
            next_buffer = f"{buffer}\n\n{paragraph}".strip() if buffer else paragraph
            if len(next_buffer) <= max_chars:
                buffer = next_buffer
                continue
            if buffer:
                chunks.append(_make_chunk(article, buffer, chunk_index))
                chunk_index += 1
                buffer = _overlap_tail(buffer, overlap_chars)
            buffer = f"{buffer}\n\n{paragraph}".strip() if buffer else paragraph
            while len(buffer) > max_chars:
                head = buffer[:max_chars]
                chunks.append(_make_chunk(article, head, chunk_index))
                chunk_index += 1
                buffer = _overlap_tail(head, overlap_chars) + buffer[max_chars:]
        if buffer:
            chunks.append(_make_chunk(article, buffer, chunk_index))
    return chunks


def _make_chunk(article: Article, text: str, chunk_index: int) -> Chunk:
    return Chunk(
        id=f"{article.id}::chunk-{chunk_index:03d}",
        article_id=article.id,
        title=article.title,
        text=text.strip(),
        chunk_index=chunk_index,
    )


def _overlap_tail(text: str, overlap_chars: int) -> str:
    if overlap_chars <= 0 or len(text) <= overlap_chars:
        return ""
    return text[-overlap_chars:].split(" ", 1)[-1].strip()
