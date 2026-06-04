"""Pydantic v2 schemas for all pipeline artifacts."""
from __future__ import annotations
from pydantic import BaseModel, Field

_VALID_DIMENSIONS = {"market", "technology", "narrative", "regulatory", "adoption", "validation"}


class Signal(BaseModel):
    model_config = {"extra": "ignore"}
    id: str = ""
    observation: str = ""
    tag: str = "INTERNAL"


class Metric(BaseModel):
    model_config = {"extra": "ignore"}
    num: str = ""
    label: str = ""


class SignalMap(BaseModel):
    model_config = {"extra": "ignore"}
    product_name: str = ""
    sector: str = ""
    product_core: str = ""
    signals: list[Signal] = Field(default_factory=list)
    metrics: list[Metric] = Field(default_factory=list)
    tensions: list[str] = Field(default_factory=list)
    catalysts: list[str] = Field(default_factory=list)
    strategic_intent: str = ""

    @classmethod
    def model_validate(cls, obj, *, strict=None, from_attributes=None, context=None):
        if isinstance(obj, dict):
            # singular → plural aliases
            for s, p in [("tension","tensions"),("catalyst","catalysts"),("signal","signals"),("metric","metrics")]:
                if s in obj and p not in obj:
                    obj = {**obj, p: obj.pop(s)}
            # bare strings → single-item lists
            for f in ("tensions", "catalysts"):
                if isinstance(obj.get(f), str):
                    obj = {**obj, f: [obj[f]] if obj[f] else []}
            # dict → list coercion for signals and metrics
            # (LLM sometimes returns {"key": {observation:..}, ...} instead of [{...},...])
            for f in ("signals", "metrics"):
                v = obj.get(f)
                if isinstance(v, dict):
                    items = []
                    for key, val in v.items():
                        if isinstance(val, dict):
                            # use key as id if not present
                            entry = {"id": key, **val}
                            # for metrics, try to pull num/label from nested keys
                            if f == "metrics" and "num" not in entry and "label" not in entry:
                                entry = {"num": key, "label": str(list(val.values())[0]) if val else key}
                        else:
                            entry = {"id": key, "observation": str(val)} if f == "signals" else {"num": key, "label": str(val)}
                        items.append(entry)
                    obj = {**obj, f: items}
        return super().model_validate(obj, strict=strict, from_attributes=from_attributes, context=context)


class ResearchQuestion(BaseModel):
    model_config = {"extra": "ignore"}
    id: str = ""
    dimension: str = "market"
    question: str = ""
    queries: list[str] = Field(default_factory=list)

    @classmethod
    def model_validate(cls, obj, *, strict=None, from_attributes=None, context=None):
        if isinstance(obj, dict) and obj.get("dimension") not in _VALID_DIMENSIONS:
            obj = {**obj, "dimension": "market"}
        return super().model_validate(obj, strict=strict, from_attributes=from_attributes, context=context)


class ResearchPlan(BaseModel):
    model_config = {"extra": "ignore"}
    questions: list[ResearchQuestion] = Field(default_factory=list)


class EvidenceCard(BaseModel):
    model_config = {"extra": "ignore"}
    id: str = ""
    dimension: str = ""
    claim: str = ""
    source_title: str = ""
    url: str = ""
    tag: str = "SECTORAL"
    question_id: str = ""


class EvidenceCards(BaseModel):
    model_config = {"extra": "ignore"}
    cards: list[EvidenceCard] = Field(default_factory=list)


class Taglines(BaseModel):
    model_config = {"extra": "ignore"}
    outcome: str = ""
    visionary: str = ""
    punchy: str = ""


class JargonRow(BaseModel):
    model_config = {"extra": "ignore"}
    feature: str = ""
    capability: str = ""
    benefit: str = ""
    kpi: str = ""


class SWOT(BaseModel):
    model_config = {"extra": "ignore"}
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    threats: list[str] = Field(default_factory=list)


class Metaphor(BaseModel):
    model_config = {"extra": "ignore"}
    statement: str = ""
    rationale: str = ""


class TonePillar(BaseModel):
    model_config = {"extra": "ignore"}
    name: str = ""
    do_say: str = ""
    dont_say: str = ""


class VocabItem(BaseModel):
    model_config = {"populate_by_name": True, "extra": "ignore"}
    from_: str = Field(default="", alias="from")
    to: str = ""


class RoadmapPhase(BaseModel):
    model_config = {"extra": "ignore"}
    phase: str = ""
    name: str = ""
    when: str = ""
    points: list[str] = Field(default_factory=list)


class GrapevineItem(BaseModel):
    model_config = {"extra": "ignore"}
    title: str = ""
    desc: str = ""


class DeckSpec(BaseModel):
    model_config = {"extra": "ignore"}
    product: str = ""
    taglines: Taglines = Field(default_factory=Taglines)
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
    model_config = {"extra": "ignore"}
    hex: str = "000000"
    role: str = ""
    why: str = ""


class Typography(BaseModel):
    display: str = "Georgia"
    body: str = "Calibri"


class BrandTokens(BaseModel):
    model_config = {"extra": "ignore"}
    palette: dict[str, PaletteColor] = Field(default_factory=dict)
    type: Typography = Field(default_factory=Typography)
    rules: str = ""
    motif: str = ""
