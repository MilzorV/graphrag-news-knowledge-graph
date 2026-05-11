from __future__ import annotations

import re

from .models import Evidence
from .ollama_client import DEFAULT_CHAT_MODEL, DEFAULT_OLLAMA_HOST, chat_text, get_status


def generate_answer(
    question: str,
    evidence: list[Evidence],
    *,
    mode: str,
    use_ollama: bool = False,
    ollama_model: str = DEFAULT_CHAT_MODEL,
    ollama_host: str = DEFAULT_OLLAMA_HOST,
) -> str:
    if use_ollama and _model_ready(ollama_model, ollama_host):
        try:
            return _generate_with_ollama(question, evidence, mode, ollama_model, ollama_host)
        except Exception:
            pass
    return _generate_template(question, evidence, mode)


def _model_ready(model: str, host: str) -> bool:
    status = get_status(host)
    return status.available and model in status.models


def _generate_with_ollama(question: str, evidence: list[Evidence], mode: str, model: str, host: str) -> str:
    context = "\n\n".join(
        f"[{idx}] {item.title} ({item.doc_id}, score={item.score:.2f})\n{item.snippet}"
        for idx, item in enumerate(evidence, start=1)
    )
    messages = [
        {
            "role": "system",
            "content": (
                "Answer news-analysis questions using only the supplied evidence. "
                "Mention uncertainty when evidence is incomplete. Keep the answer concise and include source titles."
            ),
        },
        {"role": "user", "content": f"Mode: {mode}\nQuestion: {question}\n\nEvidence:\n{context}"},
    ]
    return chat_text(messages, model=model, host=host)


def _generate_template(question: str, evidence: list[Evidence], mode: str) -> str:
    if not evidence:
        return f"No supporting evidence was found for: {question}"

    direct = _direct_answer_from_evidence(question, evidence)
    if direct:
        return direct

    lead = f"{mode.title()} retrieval found {len(evidence)} supporting source"
    if len(evidence) != 1:
        lead += "s"
    best = evidence[0]
    source_titles = []
    for item in evidence[:4]:
        if item.title not in source_titles:
            source_titles.append(item.title)
    return (
        f"{lead}. The strongest match is `{best.title}`. "
        f"Relevant sources: {', '.join(source_titles)}. "
        "Open the evidence list for the exact snippets and provenance."
    )


def _direct_answer_from_evidence(question: str, evidence: list[Evidence]) -> str:
    question_key = question.lower()
    snippets = [item.snippet for item in evidence]
    if question_key.startswith("where") or " where " in f" {question_key} ":
        for item in evidence:
            match = re.search(r"associated with location ([^.]+)\.", item.snippet)
            if match:
                return f"The evidence points to {match.group(1)}. Strongest source: `{item.title}`."
        for item in evidence:
            match = re.search(r"\bin ([A-Z][A-Za-z]+)\b", item.snippet)
            if match:
                return f"The evidence points to {match.group(1)}. Strongest source: `{item.title}`."
    if question_key.startswith("when") or " date " in question_key:
        for item in evidence:
            match = re.search(r"associated with date ([^.]+)\.", item.snippet)
            if match:
                return f"The evidence points to {match.group(1)}. Strongest source: `{item.title}`."
    if "which articles" in question_key:
        titles = []
        for item in evidence:
            if item.title not in titles:
                titles.append(item.title)
        return "Relevant articles: " + "; ".join(titles[:6]) + "."
    if question_key.startswith("who"):
        people = []
        for snippet in snippets:
            for match in re.finditer(r"([A-Z][a-z]+ [A-Z][a-z]+) is mentioned as", snippet):
                if match.group(1) not in people:
                    people.append(match.group(1))
        if people:
            return "People or actors found in the graph evidence: " + ", ".join(people[:8]) + "."
    return ""
