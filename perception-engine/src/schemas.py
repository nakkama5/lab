"""Pydantic v2 schemas for all pipeline artifacts."""
from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field


class Signal(BaseModel):
    id: str
    observation: str
    tag: str = "INTERNAL"


class Metric(BaseModel):
    num: str
    label: str


class SignalMap(BaseModel):
    product_name: str
    sector: str
    product_core: str
    signals: list[Signal]
    metrics: list[Metric]
    tensions: list[str]
    catalysts: list[str]
    strategic_intent: str


class ResearchQuestion(BaseModel):
    id: str
    dimension: Literal["market", "technology", "narrative", "regulatory", "adoption", "validation"]
    question: str
    queries: list[str]


class ResearchPlan(BaseModel):
    questions: list[ResearchQuestion]


class EvidenceCard(BaseModel):
    id: str
    dimension: str
    claim: str
    source_title: str
    url: str
    tag: Literal["SECTORAL", "TECH"]
    question_id: str


class EvidenceCards(BaseModel):
    cards: list[EvidenceCard]


class Taglines(BaseModel):
    outcome: str = ""
    visionary: str = ""
    punchy: str = ""


class JargonRow(BaseModel):
    feature: str = ""
    capability: str = ""
    benefit: str = ""
    kpi: str = ""


class SWOT(BaseModel):
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    threats: list[str] = Field(default_factory=list)


class Metaphor(BaseModel):
    statement: str = ""
    rationale: str = ""


class TonePillar(BaseModel):
    name: str = ""
    do_say: str = ""
    dont_say: str = ""


class VocabItem(BaseModel):
    from_: str = Field(default="", alias="from")
    to: str = ""

    model_config = {"populate_by_name": True}


class RoadmapPhase(BaseModel):
    phase: str = ""
    name: str = ""
    when: str = ""
    points: list[str] = Field(default_factory=list)


class GrapevineItem(BaseModel):
    title: str = ""
    desc: str = ""


class DeckSpec(BaseModel):
    product: str
    taglines: Taglines
    micro: str = ""
    elevator: str = ""
    metrics: list[Metric] = Field(default_factory=list)
    legacy: list[str] = Field(default_factory=list)
    evolution: list[str] = Field(default_factory=list)
    jargon_rows: list[JargonRow] = Field(default_factory=list)
    swot: SWOT = Field(default_factory=SWOT)
    metaphor: Metaphor = Field(default_factory=Metaphor)
    pillars: list[TonePillar] = Field(default_factory=list)
    vocab: list[VocabItem] = Field(default_factory=list)
    manifesto: str = ""
    grapevine: list[GrapevineItem] = Field(default_factory=list)
    roadmap: list[RoadmapPhase] = Field(default_factory=list)


class PaletteColor(BaseModel):
    hex: str
    role: str
    why: str


class Typography(BaseModel):
    display: str = "Georgia"
    body: str = "Calibri"


class BrandTokens(BaseModel):
    palette: dict[str, PaletteColor]
    type: Typography
    rules: str
    motif: str
