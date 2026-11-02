"""Question bank, project-type detection and small text helpers.

Questions are written in English. An AI agent using this framework asks them
in the user's language.
"""

from __future__ import annotations

import re

from .uncertainty import FIELD_MAP

BASE_QUESTIONS = {
    "objective": "What do you want to achieve with this project, in one or two sentences?",
    "problem": "What problem or situation does this project solve, and for whom?",
    "deliverables": (
        "What exactly do you expect to receive at the end "
        "(e.g. document, code, workflow, dashboard, MVP)?"
    ),
    "success_criteria": (
        "How will we know the project succeeded? Give at least one measurable "
        "criterion (a number, a percentage or a date)."
    ),
    "expected_result": "What should the final result look like when it is done?",
    "constraints": (
        "Are there constraints I must respect (time, budget, technology, security, "
        "privacy, language, infrastructure)? Answer 'none' if there are none."
    ),
    "context": "What already exists (material, previous work, data) and what is missing?",
    "risks": "Is there any risk that could block or derail the project? Answer 'none' if not.",
}

QUESTIONS_BY_TYPE = {
    "software": {
        "problem": "Who are the target users and what problem does the product solve for them?",
        "deliverables": "What is the MVP: which core features must the first version include?",
        "constraints": (
            "Are there technical or business constraints (stack, hosting, budget, "
            "deadline, compliance)? Answer 'none' if there are none."
        ),
    },
    "marketing": {
        "problem": "What product is being promoted and who is the target audience?",
        "deliverables": "Which channels and assets should the campaign include?",
        "success_criteria": (
            "Which KPIs define success (e.g. 500 sign-ups in 30 days, CPA under $20)?"
        ),
        "constraints": "What budget and timeline does the campaign have? Answer 'none' if not defined.",
    },
    "research": {
        "problem": (
            "What question should the research answer, and for which companies, "
            "industries or markets?"
        ),
        "deliverables": "What format should the final output have (report, dataset, presentation)?",
        "context": "Which sources and methodology should be used or avoided?",
        "success_criteria": (
            "What would make the research useful? Give a measurable criterion "
            "(e.g. 20 companies analysed, delivered before a date)."
        ),
    },
}

FOLLOW_UPS = {
    "success_criteria": (
        "The success criteria are not measurable yet. Can you add a number, a "
        "percentage or a date (e.g. 'reach 100 paying users within 60 days')?"
    ),
}

KNOWLEDGE_SOURCE_QUESTION = (
    "Do you already have a knowledge base I should consult for this project "
    "(a second brain, a notes vault, a graph database, a folder with system prompts "
    "or skills)? Give its path, or answer 'no'."
)

KNOWLEDGE_CONSENT_QUESTION = (
    "I found these knowledge sources on this machine: {sources}. "
    "May I consult them read-only for this project? (yes/no)"
)

TYPE_KEYWORDS = {
    "software": (
        "app", "application", "saas", "platform", "api", "website", "web", "software",
        "backend", "frontend", "mobile", "plataforma", "aplicación", "aplicacion",
        "sistema", "código", "codigo",
    ),
    "marketing": (
        "campaign", "launch", "brand", "ads", "marketing", "audience", "social",
        "campaña", "lanzamiento", "marca", "publicidad",
    ),
    "research": (
        "research", "investigate", "study", "analysis", "analyze", "survey",
        "investigar", "investigación", "investigacion", "estudio", "análisis", "analisis",
    ),
}

YES = {"yes", "y", "si", "sí", "s", "ok", "okay", "dale", "sure", "claro"}
NO = {"no", "n", "none", "nope", "skip", "ninguno", "ninguna", "nada", "no tengo"}

STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "have", "will", "want",
    "need", "into", "your", "about", "what", "which", "their", "there", "would",
    "should", "could", "build", "create", "make", "none", "project",
    "para", "como", "que", "una", "uno", "unos", "unas", "los", "las", "del",
    "con", "por", "más", "mas", "este", "esta", "esto", "quiero", "necesito",
    "sobre", "entre", "cuando", "donde", "proyecto", "tiene", "hacer",
}


def detect_project_type(text: str) -> str:
    words = set(re.findall(r"[\wáéíóúñü]+", (text or "").lower()))
    scores = {t: sum(1 for k in kws if k in words) for t, kws in TYPE_KEYWORDS.items()}
    best = max(scores, key=lambda t: scores[t])
    return best if scores[best] > 0 else "general"


def question_for(field: str, project_type: str = "general") -> str:
    return QUESTIONS_BY_TYPE.get(project_type, {}).get(field) or BASE_QUESTIONS[field]


def follow_up_for(field: str) -> str:
    return FOLLOW_UPS.get(field) or (
        f"Can you add a bit more detail about the {FIELD_MAP[field].label.lower()}?"
    )


def extract_terms(text: str, limit: int = 30) -> list:
    """Keywords used to query a knowledge base (lowercase, no stopwords)."""
    seen = []
    for word in re.findall(r"[a-záéíóúñü0-9][a-záéíóúñü0-9\-]{3,}", (text or "").lower()):
        if word not in STOPWORDS and word not in seen:
            seen.append(word)
        if len(seen) >= limit:
            break
    return seen


def is_yes(value: str) -> bool:
    return value.strip().lower().rstrip(".!") in YES


def is_no(value: str) -> bool:
    return value.strip().lower().rstrip(".!") in NO
