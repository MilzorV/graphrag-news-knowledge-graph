from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

import httpx


DEFAULT_OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "llama3.1:8b")
DEFAULT_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")


@dataclass(slots=True)
class OllamaStatus:
    available: bool
    models: list[str]
    error: str = ""


def get_status(host: str = DEFAULT_OLLAMA_HOST, timeout: float = 2.0) -> OllamaStatus:
    try:
        response = httpx.get(f"{host.rstrip('/')}/api/tags", timeout=timeout)
        response.raise_for_status()
        data = response.json()
        models = [item.get("name", "") for item in data.get("models", []) if item.get("name")]
        return OllamaStatus(available=True, models=models)
    except Exception as exc:  # noqa: BLE001 - CLI diagnostics should surface any connection issue.
        return OllamaStatus(available=False, models=[], error=str(exc))


def has_model(model: str, host: str = DEFAULT_OLLAMA_HOST) -> bool:
    return model in get_status(host).models


def chat_json(
    messages: list[dict[str, str]],
    *,
    model: str = DEFAULT_CHAT_MODEL,
    host: str = DEFAULT_OLLAMA_HOST,
    timeout: float = 120.0,
) -> dict[str, Any]:
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0},
    }
    response = httpx.post(f"{host.rstrip('/')}/api/chat", json=payload, timeout=timeout)
    response.raise_for_status()
    content = response.json()["message"]["content"]
    return json.loads(content)


def chat_text(
    messages: list[dict[str, str]],
    *,
    model: str = DEFAULT_CHAT_MODEL,
    host: str = DEFAULT_OLLAMA_HOST,
    timeout: float = 120.0,
) -> str:
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.1},
    }
    response = httpx.post(f"{host.rstrip('/')}/api/chat", json=payload, timeout=timeout)
    response.raise_for_status()
    return response.json()["message"]["content"].strip()
