"""Discovery Engine: reduces uncertainty, one question at a time, then summarizes.

It never generates the PRD, never changes the project state and never
continues the workflow: it returns to the Project Bootstrapper.
"""

from __future__ import annotations

from typing import Optional

from .documents import render_summary
from .errors import GuardError
from .questions import (
    KNOWLEDGE_CONSENT_QUESTION,
    KNOWLEDGE_SOURCE_QUESTION,
    follow_up_for,
    question_for,
)
from .uncertainty import FIELD_MAP, MAX_QUESTIONS, assess, field_score, is_na
from .workspace import ProjectState


class DiscoveryEngine:
    def __init__(self, templates_dir=None, max_questions: int = MAX_QUESTIONS):
        self.templates_dir = templates_dir
        self.max_questions = max_questions

    def next_question(self, state: ProjectState) -> Optional[dict]:
        """The single most valuable question to ask now, or None when discovery is done."""
        knowledge = state.knowledge
        if knowledge.get("status") == "pending_consent":
            locations = ", ".join(s["location"] for s in knowledge.get("sources", []))
            return {
                "field": "knowledge_consent",
                "kind": "knowledge",
                "text": KNOWLEDGE_CONSENT_QUESTION.format(sources=locations),
            }
        if knowledge.get("status") == "pending_source":
            return {"field": "knowledge_source", "kind": "knowledge", "text": KNOWLEDGE_SOURCE_QUESTION}

        assessment = assess(state.fields)
        if assessment.ready or state.counters.get("questions_answered", 0) >= self.max_questions:
            return None
        for name in assessment.ordered_gaps:
            if name in assessment.partial:
                return {"field": name, "kind": "follow_up", "text": follow_up_for(name)}
            return {"field": name, "kind": "field", "text": question_for(name, state.project_type)}
        return None

    def record_answer(self, state: ProjectState, field: str, value: str) -> None:
        if field not in FIELD_MAP:
            raise GuardError(f"Unknown field '{field}'. Valid fields: {', '.join(FIELD_MAP)}.")
        value = (value or "").strip()
        if not value:
            raise GuardError("Empty answer. Ask the question again or answer 'none' for optional fields.")
        previous = state.fields.get(field)
        # A follow-up adds detail to a partial answer instead of replacing it.
        if previous and not is_na(previous) and field_score(field, previous) == 0.5:
            state.fields[field] = f"{previous}; {value}"
        else:
            state.fields[field] = value

    def summarize(self, state: ProjectState) -> str:
        return render_summary(state, self.templates_dir)
