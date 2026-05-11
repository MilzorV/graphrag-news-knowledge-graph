from __future__ import annotations

import hashlib
import re
import unicodedata


WHITESPACE_RE = re.compile(r"[ \t]+")
NON_WORD_RE = re.compile(r"[^a-z0-9]+")


def stable_id(prefix: str, *parts: str) -> str:
    raw = "\u241f".join(parts)
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}:{digest}"


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = NON_WORD_RE.sub("-", normalized.lower()).strip("-")
    return slug or "item"


def normalize_name(value: str) -> str:
    value = WHITESPACE_RE.sub(" ", value.strip())
    value = re.sub(r"^[\"'`]+|[\"'`,.;:!?]+$", "", value)
    return value


def canonical_key(value: str) -> str:
    value = normalize_name(value)
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return NON_WORD_RE.sub(" ", normalized.lower()).strip()


def entity_id(entity_type: str, name: str) -> str:
    return f"{entity_type.lower()}:{slugify(canonical_key(name))}"


def article_node_id(article_id: str) -> str:
    return f"article:{slugify(article_id)}"


def compact_snippet(text: str, limit: int = 320) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rsplit(" ", 1)[0] + "..."
