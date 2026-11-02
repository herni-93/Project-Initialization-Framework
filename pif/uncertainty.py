"""Uncertainty measurement.

Every discovery field has a weight. The clarity score (0-100) is the weighted
sum of how complete each field is; uncertainty is ``100 - clarity``. Discovery
stops when clarity reaches READY_THRESHOLD and every critical field is complete.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Mapping, Optional


@dataclass(frozen=True)
class Field:
    name: str
    label: str
    weight: int
    critical: bool = False


FIELDS = (
    Field("objective", "Objective", 20, critical=True),
    Field("problem", "Problem", 15),
    Field("deliverables", "Deliverables", 15, critical=True),
    Field("success_criteria", "Success criteria", 20, critical=True),
    Field("expected_result", "Expected result", 10),
    Field("constraints", "Constraints", 10),
    Field("context", "Context", 5),
    Field("risks", "Risks", 5),
    # Detected when possible, never asked for on its own.
    Field("dependencies", "Dependencies", 0),
)
FIELD_MAP = {f.name: f for f in FIELDS}

READY_THRESHOLD = 80
MAX_QUESTIONS = 12
MIN_ANSWER_CHARS = 8

NA_TOKENS = {
    "none", "n/a", "na", "no", "nothing", "not applicable", "-",
    "ninguno", "ninguna", "nada", "no aplica", "no hay",
}

MEASURABLE = re.compile(
    r"\d|%|\b(at least|at most|less than|more than|fewer than|before|after|within|per|"
    r"al menos|como m[aá]ximo|menos de|m[aá]s de|antes de|despu[eé]s de|dentro de|por)\b",
    re.IGNORECASE,
)


def is_na(value: str) -> bool:
    return value.strip().lower().rstrip(".") in NA_TOKENS


def is_measurable(value: str) -> bool:
    return bool(MEASURABLE.search(value or ""))


def field_score(name: str, value: Optional[str]) -> float:
    """1.0 complete, 0.5 needs more detail, 0.0 missing."""
    spec = FIELD_MAP[name]
    if value is None or not str(value).strip():
        return 0.0
    text = str(value).strip()
    if is_na(text):
        return 0.0 if spec.critical else 1.0
    if len(text) < MIN_ANSWER_CHARS:
        return 0.5
    if name == "success_criteria" and not is_measurable(text):
        return 0.5
    return 1.0


@dataclass
class Assessment:
    clarity: int
    uncertainty: int
    level: str
    ready: bool
    critical_complete: bool
    missing: list = field(default_factory=list)
    partial: list = field(default_factory=list)

    @property
    def ordered_gaps(self) -> list:
        """Fields to ask about, most valuable first (critical, then weight)."""
        gaps = [FIELD_MAP[n] for n in self.missing + self.partial]
        order = {f.name: i for i, f in enumerate(FIELDS)}
        gaps.sort(key=lambda f: (not f.critical, -f.weight, order[f.name]))
        return [f.name for f in gaps]

    def to_dict(self) -> dict:
        return {
            "clarity": self.clarity,
            "uncertainty": self.uncertainty,
            "uncertainty_level": self.level,
            "ready": self.ready,
            "critical_complete": self.critical_complete,
            "missing": self.missing,
            "needs_detail": self.partial,
        }


def assess(fields: Mapping[str, str]) -> Assessment:
    scores = {f.name: field_score(f.name, fields.get(f.name)) for f in FIELDS}
    clarity = round(sum(f.weight * scores[f.name] for f in FIELDS))
    uncertainty = 100 - clarity
    critical_complete = all(scores[f.name] == 1.0 for f in FIELDS if f.critical)
    if uncertainty <= 20:
        level = "low"
    elif uncertainty <= 50:
        level = "medium"
    else:
        level = "high"
    return Assessment(
        clarity=clarity,
        uncertainty=uncertainty,
        level=level,
        ready=clarity >= READY_THRESHOLD and critical_complete,
        critical_complete=critical_complete,
        missing=[f.name for f in FIELDS if f.weight and scores[f.name] == 0.0],
        partial=[f.name for f in FIELDS if f.weight and scores[f.name] == 0.5],
    )
