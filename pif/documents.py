"""Rendering of the executive summary and the PRD, and the PRD quality gate."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

from . import __version__
from .uncertainty import FIELD_MAP, FIELDS, assess, is_measurable, is_na
from .workspace import ProjectState, now

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
SUMMARY_TEMPLATE = "executive-summary.template.md"
PRD_TEMPLATE = "prd.template.md"

OPEN_MARK = "_Open question - not answered yet._"
NONE_DECLARED = "None declared."
NO_DEPENDENCIES = "None identified."

REQUIRED_PRD_SECTIONS = (
    "objective", "problem", "context", "expected result", "deliverables",
    "success criteria", "constraints", "risks", "dependencies",
    "knowledge & resources", "open questions", "initialization metrics", "handoff",
)
CRITICAL_PRD_SECTIONS = ("objective", "deliverables", "success criteria")


def load_template(name: str, templates_dir=None) -> str:
    base = Path(templates_dir) if templates_dir else TEMPLATES_DIR
    return (base / name).read_text(encoding="utf-8")


def fill(template: str, values: dict) -> str:
    """Replace ``{{key}}`` placeholders. Unknown keys are left for the quality gate to catch."""
    return re.sub(
        r"\{\{\s*([a-z_]+)\s*\}\}",
        lambda m: str(values[m.group(1)]) if m.group(1) in values else m.group(0),
        template,
    )


def format_value(name: str, value: Optional[str]) -> str:
    if value is None or not str(value).strip():
        return NO_DEPENDENCIES if name == "dependencies" else OPEN_MARK
    text = str(value).strip()
    if is_na(text):
        return NONE_DECLARED
    parts = [p.strip() for p in re.split(r"\n|;", text) if p.strip()]
    if len(parts) > 1:
        return "\n".join(f"- {p.lstrip('- ').strip()}" for p in parts)
    return text


def _cell(text: str) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def _open_questions(assessment) -> str:
    lines = [
        f"- **{FIELD_MAP[n].label}**: {'missing' if n in assessment.missing else 'needs more detail'}"
        for n in assessment.ordered_gaps
    ]
    return "\n".join(lines) if lines else "None."


def _knowledge_section(state: ProjectState) -> str:
    knowledge = state.knowledge
    if knowledge.get("status") != "connected" or not knowledge.get("sources"):
        return "No external knowledge base was used."
    lines = ["Connected sources (read-only):"]
    lines += [f"- `{s['location']}` ({s['type']})" for s in knowledge["sources"]]
    snippets = knowledge.get("snippets") or []
    if snippets:
        lines += ["", "Relevant notes found:"]
        lines += [f"- **{s['title']}** (`{s['path']}`): {s['excerpt']}" for s in snippets]
    return "\n".join(lines)


def _resources_table(state: ProjectState) -> str:
    rows = state.knowledge.get("selected_resources") or []
    if not rows:
        return "No resources proposed."
    lines = [
        "| Resource | Type | Reason | Priority | Status |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        lines.append(
            f"| {_cell(r['resource'])} | {_cell(r['kind'])} | {_cell(r['reason'])} "
            f"| {_cell(r['priority'])} | {_cell(r['status'])} |"
        )
    return "\n".join(lines)


def build_values(state: ProjectState) -> dict:
    assessment = assess(state.fields)
    values = {f.name: format_value(f.name, state.fields.get(f.name)) for f in FIELDS}
    selected = state.knowledge.get("selected_resources") or []
    values.update(
        id=state.id,
        name=state.name,
        id_json=json.dumps(state.id, ensure_ascii=False),
        name_json=json.dumps(state.name, ensure_ascii=False),
        project_type=state.project_type,
        created=state.created,
        updated=now(),
        date=now()[:10],
        clarity=assessment.clarity,
        uncertainty=assessment.uncertainty,
        uncertainty_level=assessment.level,
        open_questions=_open_questions(assessment),
        knowledge_section=_knowledge_section(state),
        resources_table=_resources_table(state),
        resources_inline=json.dumps([r["resource"] for r in selected], ensure_ascii=False),
        prd_version=max(state.counters.get("prd_generations", 0), 1),
        questions_answered=state.counters.get("questions_answered", 0),
        clarity_initial=state.initial_clarity if state.initial_clarity is not None else "n/a",
        summary_rejections=state.counters.get("summary_rejections", 0),
        prd_rejections=state.counters.get("prd_rejections", 0),
        discovery_skipped="yes" if not any(h["to"] == "discovery" for h in state.history) else "no",
        framework_version=__version__,
    )
    return values


def render_summary(state: ProjectState, templates_dir=None) -> str:
    return fill(load_template(SUMMARY_TEMPLATE, templates_dir), build_values(state))


def render_prd(state: ProjectState, templates_dir=None) -> str:
    return fill(load_template(PRD_TEMPLATE, templates_dir), build_values(state))


def _sections(text: str) -> dict:
    sections, current = {}, None
    for line in text.splitlines():
        match = re.match(r"^##\s+(?:\d+\.\s*)?(.+?)\s*$", line)
        if match:
            current = match.group(1).strip().lower()
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return {k: "\n".join(v).strip() for k, v in sections.items()}


def check_prd(text: str) -> list:
    """PRD quality gate. Returns a list of issues; an empty list means it passes."""
    issues = []
    if not text.lstrip().startswith("---"):
        issues.append("Missing YAML frontmatter.")
    sections = _sections(text)
    for name in REQUIRED_PRD_SECTIONS:
        if name not in sections:
            issues.append(f"Missing section: {name}.")
    if "{{" in text:
        issues.append("Unresolved template placeholders ({{...}}).")
    for name in CRITICAL_PRD_SECTIONS:
        body = sections.get(name, "")
        if not body or OPEN_MARK in body or "TBD" in body:
            issues.append(f"Critical section is incomplete: {name}.")
    criteria = sections.get("success criteria", "")
    if criteria and OPEN_MARK not in criteria and not is_measurable(criteria):
        issues.append("Success criteria are not measurable (add a number, percentage or date).")
    return issues


def mark_prd_approved(text: str) -> str:
    return re.sub(r"^status:\s*draft\s*$", "status: approved", text, count=1, flags=re.M)
