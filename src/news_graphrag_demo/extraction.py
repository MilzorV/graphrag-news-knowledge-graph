from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from .models import Article, Chunk, Entity, Relation
from .ollama_client import DEFAULT_CHAT_MODEL, DEFAULT_OLLAMA_HOST, chat_json, get_status
from .text_utils import article_node_id, canonical_key, compact_snippet, entity_id, normalize_name, stable_id


ENTITY_TYPES = {"PERSON", "ORGANIZATION", "LOCATION", "EVENT", "DATE_TIME", "OBJECT", "TOPIC"}
RELATION_TYPES = {
    "MENTIONS",
    "PARTICIPATED_IN",
    "INVOLVED_IN",
    "LOCATED_IN",
    "OCCURRED_AT",
    "OCCURRED_ON",
    "AFFILIATED_WITH",
    "RELATED_TO",
    "SUPPORTED_BY",
    "SAME_AS",
}

DATE_RE = re.compile(
    r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|"
    r"Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},\s+\d{4}\b"
    r"|\b\d{4}-\d{2}-\d{2}\b"
)
CAPITALIZED_RE = re.compile(
    r"\b(?:[A-Z][a-z]+|[A-Z]{2,})(?:\s+(?:[A-Z][a-z]+|[A-Z]{2,}|of|and|for|the|&)){0,5}\b"
)

ORG_HINTS = {
    "agency",
    "analytics",
    "authority",
    "committee",
    "company",
    "corp",
    "directorate",
    "europe",
    "forum",
    "grid",
    "group",
    "ministry",
    "nordicgrid",
    "university",
}
EVENT_HINTS = {
    "agreement",
    "conference",
    "demo",
    "drill",
    "flood response",
    "hearing",
    "meeting",
    "procurement review",
    "review",
    "summit",
    "talks",
    "test",
}
KNOWN_LOCATIONS = {
    "warsaw",
    "gdansk",
    "krakow",
    "vilnius",
    "poland",
    "lithuania",
    "vístula",
    "vistula",
    "baltic",
}
STOP_CANDIDATES = {
    "No",
    "The",
    "A",
    "An",
    "May",
    "April",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
}


@dataclass(slots=True)
class ExtractionConfig:
    mode: str = "auto"
    ollama_model: str = DEFAULT_CHAT_MODEL
    ollama_host: str = DEFAULT_OLLAMA_HOST


def extract_knowledge(
    articles: list[Article],
    chunks: list[Chunk],
    config: ExtractionConfig | None = None,
) -> tuple[list[Entity], list[Relation]]:
    config = config or ExtractionConfig()
    if config.mode == "ollama" or (config.mode == "auto" and _ollama_ready(config)):
        try:
            return _extract_with_ollama(articles, chunks, config)
        except Exception:
            if config.mode == "ollama":
                raise
    return _extract_with_heuristics(articles, chunks)


def _ollama_ready(config: ExtractionConfig) -> bool:
    status = get_status(config.ollama_host)
    return status.available and config.ollama_model in status.models


def _extract_with_heuristics(articles: list[Article], chunks: list[Chunk]) -> tuple[list[Entity], list[Relation]]:
    article_by_id = {article.id: article for article in articles}
    entities: dict[str, Entity] = {}
    relations: dict[str, Relation] = {}

    for article in articles:
        event_name = _event_from_title(article.title)
        event = _upsert_entity(entities, event_name, "EVENT", article.id, article.text, confidence=0.7)
        relation = _make_relation(
            article_node_id(article.id),
            event.id,
            "MENTIONS",
            f"Article mentions event {event.name}.",
            article.id,
            article.text,
            confidence=0.75,
        )
        relations[relation.id] = relation

    for chunk in chunks:
        article = article_by_id[chunk.article_id]
        event = entities[entity_id("EVENT", _event_from_title(article.title))]
        candidates = _heuristic_entities(chunk.text, article.title)
        chunk_entities: list[Entity] = []

        for name, entity_type, confidence in candidates:
            entity = _upsert_entity(entities, name, entity_type, chunk.article_id, chunk.text, confidence=confidence)
            chunk_entities.append(entity)
            relation = _make_relation(
                article_node_id(chunk.article_id),
                entity.id,
                "MENTIONS",
                f"Article mentions {entity.name}.",
                chunk.article_id,
                chunk.text,
                confidence=confidence,
            )
            relations[relation.id] = relation

            event_relation_type = _event_relation_type(entity.type)
            relation = _make_relation(
                entity.id if event_relation_type in {"PARTICIPATED_IN", "INVOLVED_IN"} else event.id,
                event.id if event_relation_type in {"PARTICIPATED_IN", "INVOLVED_IN"} else entity.id,
                event_relation_type,
                _describe_event_relation(entity, event, event_relation_type),
                chunk.article_id,
                chunk.text,
                confidence=max(0.5, confidence - 0.05),
            )
            relations[relation.id] = relation

        for source, target in _cooccurring_pairs(chunk_entities):
            if source.type == "DATE_TIME" or target.type == "DATE_TIME":
                continue
            relation = _make_relation(
                source.id,
                target.id,
                "RELATED_TO",
                f"{source.name} and {target.name} are mentioned in the same news context.",
                chunk.article_id,
                chunk.text,
                confidence=0.45,
            )
            relations[relation.id] = relation

    return _merge_aliases(list(entities.values())), list(relations.values())


def _extract_with_ollama(
    articles: list[Article],
    chunks: list[Chunk],
    config: ExtractionConfig,
) -> tuple[list[Entity], list[Relation]]:
    article_by_id = {article.id: article for article in articles}
    entities: dict[str, Entity] = {}
    relations: dict[str, Relation] = {}

    for article in articles:
        event = _upsert_entity(entities, _event_from_title(article.title), "EVENT", article.id, article.text, 0.7)
        relation = _make_relation(
            article_node_id(article.id),
            event.id,
            "MENTIONS",
            f"Article mentions event {event.name}.",
            article.id,
            article.text,
            confidence=0.75,
        )
        relations[relation.id] = relation

    for chunk in chunks:
        extracted = _call_ollama_for_chunk(chunk, config)
        if not extracted:
            continue
        fallback_candidates = _heuristic_entities(chunk.text, chunk.title)
        for name, entity_type, confidence in fallback_candidates:
            _upsert_entity(entities, name, entity_type, chunk.article_id, chunk.text, confidence=confidence)

        name_to_id: dict[str, str] = {}
        for row in extracted.get("entities", []):
            name = normalize_name(str(row.get("name", "")))
            entity_type = str(row.get("type", "TOPIC")).upper().replace("/", "_").replace(" ", "_")
            if not name or entity_type not in ENTITY_TYPES:
                continue
            confidence = float(row.get("confidence") or 0.7)
            entity = _upsert_entity(entities, name, entity_type, chunk.article_id, chunk.text, confidence)
            name_to_id[canonical_key(name)] = entity.id
            mention = _make_relation(
                article_node_id(chunk.article_id),
                entity.id,
                "MENTIONS",
                f"Article mentions {entity.name}.",
                chunk.article_id,
                chunk.text,
                confidence=confidence,
            )
            relations[mention.id] = mention

        article_event = entities[entity_id("EVENT", _event_from_title(article_by_id[chunk.article_id].title))]
        for row in extracted.get("relations", []):
            source_name = normalize_name(str(row.get("source", "")))
            target_name = normalize_name(str(row.get("target", "")))
            relation_type = str(row.get("type", "RELATED_TO")).upper().replace(" ", "_")
            if relation_type not in RELATION_TYPES:
                relation_type = "RELATED_TO"
            source_id = name_to_id.get(canonical_key(source_name))
            target_id = name_to_id.get(canonical_key(target_name))
            if not source_id or not target_id:
                continue
            relation = _make_relation(
                source_id,
                target_id,
                relation_type,
                str(row.get("description") or f"{source_name} {relation_type} {target_name}."),
                chunk.article_id,
                chunk.text,
                confidence=float(row.get("confidence") or 0.65),
            )
            relations[relation.id] = relation

        for entity in list(entities.values()):
            if chunk.article_id not in entity.source_doc_ids:
                continue
            event_relation_type = _event_relation_type(entity.type)
            relation = _make_relation(
                entity.id if event_relation_type in {"PARTICIPATED_IN", "INVOLVED_IN"} else article_event.id,
                article_event.id if event_relation_type in {"PARTICIPATED_IN", "INVOLVED_IN"} else entity.id,
                event_relation_type,
                _describe_event_relation(entity, article_event, event_relation_type),
                chunk.article_id,
                chunk.text,
                confidence=0.55,
            )
            relations.setdefault(relation.id, relation)

    return _merge_aliases(list(entities.values())), list(relations.values())


def _call_ollama_for_chunk(chunk: Chunk, config: ExtractionConfig) -> dict[str, Any]:
    messages = [
        {
            "role": "system",
            "content": (
                "Extract a compact news knowledge graph. Return only JSON with keys entities and relations. "
                f"Entity type must be one of {sorted(ENTITY_TYPES)}. Relation type must be one of {sorted(RELATION_TYPES)}."
            ),
        },
        {
            "role": "user",
            "content": (
                "Article title: "
                + chunk.title
                + "\n\nText:\n"
                + chunk.text
                + "\n\nReturn JSON like "
                + json.dumps(
                    {
                        "entities": [{"name": "Example Person", "type": "PERSON", "confidence": 0.8}],
                        "relations": [
                            {
                                "source": "Example Person",
                                "target": "Example Event",
                                "type": "PARTICIPATED_IN",
                                "description": "short evidence-based description",
                                "confidence": 0.7,
                            }
                        ],
                    }
                )
            ),
        },
    ]
    return chat_json(messages, model=config.ollama_model, host=config.ollama_host)


def _heuristic_entities(text: str, title: str) -> list[tuple[str, str, float]]:
    candidates: dict[tuple[str, str], float] = {}

    for match in DATE_RE.finditer(text):
        candidates[(match.group(0), "DATE_TIME")] = 0.82

    for phrase in _title_event_phrases(title):
        candidates[(phrase, "EVENT")] = 0.72

    for match in CAPITALIZED_RE.finditer(text):
        name = normalize_name(match.group(0))
        if not name or name in STOP_CANDIDATES or len(name) < 3:
            continue
        lowered = canonical_key(name)
        if lowered in {"the", "a", "an"}:
            continue
        entity_type = _classify_capitalized(name)
        candidates[(name, entity_type)] = max(candidates.get((name, entity_type), 0), 0.62)

    for phrase in _event_mentions(text):
        candidates[(phrase, "EVENT")] = max(candidates.get((phrase, "EVENT"), 0), 0.68)

    return [(name, entity_type, confidence) for (name, entity_type), confidence in candidates.items()]


def _classify_capitalized(name: str) -> str:
    key = canonical_key(name)
    words = key.split()
    if any(hint in key for hint in EVENT_HINTS):
        return "EVENT"
    if key in KNOWN_LOCATIONS or any(word in KNOWN_LOCATIONS for word in words):
        return "LOCATION"
    if any(hint in key for hint in ORG_HINTS):
        return "ORGANIZATION"
    if len(words) >= 2 and all(word[:1].isalpha() for word in words):
        return "PERSON"
    return "TOPIC"


def _event_mentions(text: str) -> list[str]:
    found: list[str] = []
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        lowered = canonical_key(sentence)
        if not any(hint in lowered for hint in EVENT_HINTS):
            continue
        match = CAPITALIZED_RE.search(sentence)
        if match:
            phrase = normalize_name(match.group(0))
            if len(phrase.split()) >= 2:
                found.append(phrase)
    return found


def _title_event_phrases(title: str) -> list[str]:
    phrase = _event_from_title(title)
    return [phrase] if phrase else []


def _event_from_title(title: str) -> str:
    title = normalize_name(title)
    for sep in (" Opens ", " Draws ", " Reviews ", " Questions ", " Publishes ", " Tests ", " Begins "):
        if sep in title:
            return title.split(sep, 1)[0].strip()
    return title


def _upsert_entity(
    entities: dict[str, Entity],
    name: str,
    entity_type: str,
    doc_id: str,
    snippet: str,
    confidence: float,
) -> Entity:
    name = normalize_name(name)
    entity_type = entity_type.upper()
    ent_id = entity_id(entity_type, name)
    if ent_id not in entities:
        entities[ent_id] = Entity(
            id=ent_id,
            name=name,
            type=entity_type,
            source_doc_ids=[],
            snippets=[],
            confidence=confidence,
        )
    entity = entities[ent_id]
    if doc_id not in entity.source_doc_ids:
        entity.source_doc_ids.append(doc_id)
    snippet_value = compact_snippet(snippet)
    if snippet_value and snippet_value not in entity.snippets[:5]:
        entity.snippets.append(snippet_value)
    entity.confidence = max(entity.confidence, confidence)
    return entity


def _make_relation(
    source: str,
    target: str,
    relation_type: str,
    description: str,
    doc_id: str,
    snippet: str,
    confidence: float,
) -> Relation:
    relation_type = relation_type.upper()
    return Relation(
        id=stable_id("rel", source, target, relation_type, doc_id),
        source=source,
        target=target,
        type=relation_type,
        description=description,
        doc_id=doc_id,
        snippet=compact_snippet(snippet),
        confidence=confidence,
    )


def _event_relation_type(entity_type: str) -> str:
    if entity_type == "PERSON":
        return "PARTICIPATED_IN"
    if entity_type == "ORGANIZATION":
        return "INVOLVED_IN"
    if entity_type == "LOCATION":
        return "OCCURRED_AT"
    if entity_type == "DATE_TIME":
        return "OCCURRED_ON"
    return "RELATED_TO"


def _describe_event_relation(entity: Entity, event: Entity, relation_type: str) -> str:
    if relation_type == "PARTICIPATED_IN":
        return f"{entity.name} is mentioned as a participant or actor in {event.name}."
    if relation_type == "INVOLVED_IN":
        return f"{entity.name} is mentioned as an organization involved in {event.name}."
    if relation_type == "OCCURRED_AT":
        return f"{event.name} is associated with location {entity.name}."
    if relation_type == "OCCURRED_ON":
        return f"{event.name} is associated with date {entity.name}."
    return f"{entity.name} is related to {event.name}."


def _cooccurring_pairs(entities: list[Entity]) -> list[tuple[Entity, Entity]]:
    deduped = list({entity.id: entity for entity in entities}.values())
    pairs: list[tuple[Entity, Entity]] = []
    for i, source in enumerate(deduped):
        for target in deduped[i + 1 :]:
            if source.id == target.id:
                continue
            pairs.append((source, target))
    return pairs[:32]


def _merge_aliases(entities: list[Entity]) -> list[Entity]:
    by_tail: dict[str, list[Entity]] = defaultdict(list)
    for entity in entities:
        if entity.type in {"PERSON", "ORGANIZATION"}:
            words = canonical_key(entity.name).split()
            if words:
                by_tail[f"{entity.type}:{words[-1]}"].append(entity)

    for group in by_tail.values():
        if len(group) < 2:
            continue
        canonical = max(group, key=lambda item: len(item.name))
        for entity in group:
            if entity.id == canonical.id:
                continue
            if entity.name not in canonical.aliases:
                canonical.aliases.append(entity.name)
    return entities
