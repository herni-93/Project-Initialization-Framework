"""Initialization metrics computed from the state and the event log."""

from __future__ import annotations

from datetime import datetime

from .uncertainty import READY_THRESHOLD, assess
from .workspace import ProjectState

TARGETS = (
    # metric, comparison, target, meaning
    ("clarity_final", ">=", READY_THRESHOLD, "the project was understood before the PRD"),
    ("questions_answered", "<=", 10, "discovery did not overload the user"),
    ("summary_rejections", "<=", 1, "the summary reflected what the user meant"),
    ("prd_rejections", "<=", 1, "the PRD reflected the validated summary"),
    ("module_errors", "==", 0, "no module failed"),
)


def _seconds_between(start, end):
    if not start or not end:
        return None
    return int((datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds())


def _first(events, event_type):
    return next((e["ts"] for e in events if e["type"] == event_type), None)


def build_report(state: ProjectState, events: list) -> dict:
    assessment = assess(state.fields)
    counters = state.counters
    questions = counters.get("questions_answered", 0)
    initial = state.initial_clarity if state.initial_clarity is not None else 0
    started = _first(events, "request_received")
    report = {
        "project": state.name,
        "state": state.state,
        "project_type": state.project_type,
        "clarity_initial": initial,
        "clarity_final": assessment.clarity,
        "questions_answered": questions,
        "clarity_gain_per_question": round((assessment.clarity - initial) / questions, 1) if questions else 0,
        "discovery_skipped": not any(h["to"] == "discovery" for h in state.history),
        "validation_rounds": counters.get("validation_rounds", 0),
        "summary_rejections": counters.get("summary_rejections", 0),
        "prd_generations": counters.get("prd_generations", 0),
        "prd_rejections": counters.get("prd_rejections", 0),
        "module_errors": sum(1 for e in events if e["type"] == "module_error"),
        "seconds_to_first_prd": _seconds_between(started, _first(events, "prd_generated")),
        "seconds_to_completion": _seconds_between(started, _first(events, "initialization_completed")),
        "knowledge_status": state.knowledge.get("status"),
        "knowledge_sources": len(state.knowledge.get("sources") or []),
        "resources_selected": len(state.knowledge.get("selected_resources") or []),
    }
    checks = []
    for metric, op, target, meaning in TARGETS:
        value = report[metric]
        ok = {">=": value >= target, "<=": value <= target, "==": value == target}[op]
        checks.append({"metric": metric, "value": value, "target": f"{op} {target}", "ok": ok, "meaning": meaning})
    report["checks"] = checks
    return report


def report_to_markdown(report: dict) -> str:
    lines = [f"# Initialization metrics - {report['project']}", ""]
    lines += ["| Metric | Value |", "| --- | --- |"]
    for key, value in report.items():
        if key != "checks":
            lines.append(f"| {key} | {value} |")
    lines += ["", "## Targets", "", "| Metric | Value | Target | OK |", "| --- | --- | --- | --- |"]
    for c in report["checks"]:
        lines.append(f"| {c['metric']} | {c['value']} | {c['target']} | {'yes' if c['ok'] else 'no'} |")
    return "\n".join(lines) + "\n"
