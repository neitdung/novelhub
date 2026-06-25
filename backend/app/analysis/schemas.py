from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ExtractionType(StrEnum):
    CHARACTER = "character"
    LOCATION = "location"
    ORGANIZATION = "organization"
    EVENT = "event"
    RELATIONSHIP = "relationship"
    DIALOGUE = "dialogue"
    EMOTION = "emotion"
    THEME = "theme"
    PLOT_POINT = "plot_point"
    WORLD_BUILDING = "world_building"
    SYMBOL = "symbol"


@dataclass
class ExtractedEntity:
    name: str
    entity_type: ExtractionType
    aliases: list[str] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)
    source_chapter: int = 0
    confidence: float = 1.0


@dataclass
class ExtractedFact:
    subject: str
    predicate: str
    object: str
    fact_type: ExtractionType
    source_chapter: int = 0
    confidence: float = 1.0
    context: str = ""


@dataclass
class ChapterExtraction:
    chapter_number: int
    entities: list[ExtractedEntity] = field(default_factory=list)
    facts: list[ExtractedFact] = field(default_factory=list)
    summary: str = ""
    raw_response: str = ""


EXTRACTION_PROMPT = """Analyze the following chapter and extract structured information.

Return a JSON object with:
- "entities": list of objects with name, type, aliases, attributes
- "facts": list of objects with subject, predicate, object, type
- "summary": brief chapter summary

Chapter {chapter_number}:
{chapter_text}

Return ONLY valid JSON, no other text."""


def build_extraction_prompt(chapter_number: int, chapter_text: str) -> str:
    return EXTRACTION_PROMPT.format(
        chapter_number=chapter_number,
        chapter_text=chapter_text[:8000],
    )


def parse_extraction_response(response: str) -> ChapterExtraction | None:
    json_match = re.search(r"\{[\s\S]*\}", response)
    if not json_match:
        return None

    try:
        data = json.loads(json_match.group())
    except json.JSONDecodeError:
        return None

    entities = []
    for e in data.get("entities", []):
        try:
            entity_type = ExtractionType(e.get("type", "character"))
        except ValueError:
            entity_type = ExtractionType.CHARACTER
        entities.append(
            ExtractedEntity(
                name=e.get("name", ""),
                entity_type=entity_type,
                aliases=e.get("aliases", []),
                attributes=e.get("attributes", {}),
            )
        )

    facts = []
    for f in data.get("facts", []):
        try:
            fact_type = ExtractionType(f.get("type", "character"))
        except ValueError:
            fact_type = ExtractionType.CHARACTER
        facts.append(
            ExtractedFact(
                subject=f.get("subject", ""),
                predicate=f.get("predicate", ""),
                object=f.get("object", ""),
                fact_type=fact_type,
            )
        )

    return ChapterExtraction(
        chapter_number=0,
        entities=entities,
        facts=facts,
        summary=data.get("summary", ""),
        raw_response=response,
    )
