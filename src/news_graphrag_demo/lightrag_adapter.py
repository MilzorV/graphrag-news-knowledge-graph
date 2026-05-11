from __future__ import annotations

import asyncio
import importlib.util
from pathlib import Path

import numpy as np

from .models import Article
from .paths import DEFAULT_LIGHTRAG_DIR, ensure_dir


def is_lightrag_installed() -> bool:
    return importlib.util.find_spec("lightrag") is not None


def build_lightrag_index(
    articles: list[Article],
    *,
    working_dir: Path = DEFAULT_LIGHTRAG_DIR,
    llm_model: str = "llama3.1:8b",
    embed_model: str = "nomic-embed-text",
) -> str:
    if not is_lightrag_installed():
        raise RuntimeError("LightRAG is not installed. Run `uv sync --extra lightrag --extra dev`.")

    from lightrag import LightRAG  # type: ignore
    from lightrag.llm.ollama import ollama_embed, ollama_model_complete  # type: ignore
    from lightrag.utils import wrap_embedding_func_with_attrs  # type: ignore

    ensure_dir(working_dir)

    @wrap_embedding_func_with_attrs(embedding_dim=768, max_token_size=8192)
    async def embedding_func(texts: list[str]) -> np.ndarray:
        return await ollama_embed.func(texts, embed_model=embed_model)

    rag = LightRAG(
        working_dir=str(working_dir),
        llm_model_func=ollama_model_complete,
        llm_model_name=llm_model,
        llm_model_kwargs={"options": {"num_ctx": 32768}},
        embedding_func=embedding_func,
    )
    _initialize_if_needed(rag)
    rag.insert([_article_text(article) for article in articles])
    return str(working_dir)


def query_lightrag(
    question: str,
    *,
    working_dir: Path = DEFAULT_LIGHTRAG_DIR,
    mode: str = "hybrid",
    llm_model: str = "llama3.1:8b",
    embed_model: str = "nomic-embed-text",
) -> str:
    if not is_lightrag_installed():
        raise RuntimeError("LightRAG is not installed. Run `uv sync --extra lightrag --extra dev`.")

    from lightrag import LightRAG, QueryParam  # type: ignore
    from lightrag.llm.ollama import ollama_embed, ollama_model_complete  # type: ignore
    from lightrag.utils import wrap_embedding_func_with_attrs  # type: ignore

    @wrap_embedding_func_with_attrs(embedding_dim=768, max_token_size=8192)
    async def embedding_func(texts: list[str]) -> np.ndarray:
        return await ollama_embed.func(texts, embed_model=embed_model)

    rag = LightRAG(
        working_dir=str(working_dir),
        llm_model_func=ollama_model_complete,
        llm_model_name=llm_model,
        llm_model_kwargs={"options": {"num_ctx": 32768}},
        embedding_func=embedding_func,
    )
    _initialize_if_needed(rag)
    return str(rag.query(question, param=QueryParam(mode=mode)))


def _initialize_if_needed(rag: object) -> None:
    initializer = getattr(rag, "initialize_storages", None)
    if initializer is not None:
        maybe_coro = initializer()
        if asyncio.iscoroutine(maybe_coro):
            asyncio.run(maybe_coro)


def _article_text(article: Article) -> str:
    metadata = [article.title]
    if article.source:
        metadata.append(f"Source: {article.source}")
    if article.published_at:
        metadata.append(f"Date: {article.published_at}")
    return "\n".join(metadata) + "\n\n" + article.text
