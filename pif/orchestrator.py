"""Project Orchestrator: single entry point, sole owner of the project state.

It delegates every piece of work to the Project Bootstrapper, validates the
result, and only then moves the state machine forward.
"""

from __future__ import annotations

import json
import re
import unicodedata
from typing import Iterable, Optional

from . import __version__
from .bootstrapper import Bootstrapper
from .documents import check_prd, mark_prd_approved
from .errors import GuardError, InvalidTransition
from .metrics import build_report
from .states import State, ensure_transition
from .uncertainty import FIELD_MAP, MAX_QUESTIONS, assess
from .workspace import (
    HANDOFF_FILE,
    PRD_FILE,
    SUMMARY_FILE,
    ProjectState,
    Workspace,
    now,
)

KNOWLEDGE_FIELDS = ("knowledge_source", "knowledge_consent")


def _slug(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    words = re.findall(r"[a-z0-9]+", ascii_text.lower())[:6]
    return "-".join(words) or "project"


class Orchestrator:
    def __init__(self, workspace: Workspace, bootstrapper: Optional[Bootstrapper] = None,
                 templates_dir=None):
        self.ws = workspace
        self.bootstrapper = bootstrapper or Bootstrapper(templates_dir=templates_dir)

    # -- internals -----------------------------------------------------------
    def _transition(self, st: ProjectState, dst: State, reason: str = "") -> None:
        src = State(st.state)
        ensure_transition(src, dst)
        st.history.append({"from": src.value, "to": dst.value, "at": now(), "reason": reason})
        st.state = dst.value
        if dst not in (State.ERROR, State.CANCELLED):
            st.last_valid_state = dst.value
        self.ws.log("state_transition", **{"from": src.value, "to": dst.value, "reason": reason})

    def _run(self, st: ProjectState, operation) -> dict:
        try:
            operation()
        except (GuardError, InvalidTransition):
            self.ws.save(st)
            raise
        except Exception as exc:
            st.error = f"{type(exc).__name__}: {exc}"
            if State(st.state) not in (State.ERROR, State.COMPLETED, State.CANCELLED):
                self._transition(st, State.ERROR, st.error)
            self.ws.log("module_error", error=st.error)
            self.ws.save(st)
            raise
        self.ws.save(st)
        return self.status(st)

    def _load(self) -> ProjectState:
        if not self.ws.exists():
            raise GuardError("No initialization in progress. Run `pif start \"<request>\"` first.")
        return self.ws.load()

    def _enter_validation(self, st: ProjectState) -> None:
        summary = self.bootstrapper.summarize(st)
        self.ws.write(SUMMARY_FILE, summary)
        st.counters["validation_rounds"] += 1
        self.ws.log("summary_presented", clarity=assess(st.fields).clarity)

    def _finish_bootstrap(self, st: ProjectState) -> None:
        if self.bootstrapper.knowledge_pending(st):
            return  # stay in bootstrap until the knowledge question is answered
        if assess(st.fields).ready:
            self._transition(st, State.VALIDATION, "enough information: discovery not required")
            self._enter_validation(st)
        else:
            self._transition(st, State.DISCOVERY, "uncertainty too high: discovery required")

    def _generate_prd(self, st: ProjectState) -> None:
        st.counters["prd_generations"] += 1
        prd = self.bootstrapper.generate_prd(st)
        self.ws.write(PRD_FILE, prd)
        issues = check_prd(prd)
        self.ws.log("prd_generated", version=st.counters["prd_generations"], issues=issues)
        if issues:
            raise RuntimeError("PRD quality gate failed: " + "; ".join(issues))
        self._transition(st, State.PRD_REVIEW, "PRD generated and passed the quality gate")

    # -- public API ----------------------------------------------------------
    def start(self, request: str, name: Optional[str] = None, knowledge_paths: Iterable = (),
              auto_detect: bool = True, knowledge_config=None, home=None,
              fields: Optional[dict] = None) -> dict:
        """Start an initialization.

        ``fields`` holds information already present in the request (extracted by
        the agent), so discovery does not ask for it again.
        """
        if not request or not request.strip():
            raise GuardError("The initial request is empty.")
        unknown = sorted(set(fields or {}) - set(FIELD_MAP))
        if unknown:
            raise GuardError(f"Unknown fields: {', '.join(unknown)}. Valid fields: {', '.join(FIELD_MAP)}.")
        if self.ws.exists():
            previous = self.ws.load()
            if State(previous.state) not in (State.COMPLETED, State.CANCELLED):
                raise GuardError(
                    f"An initialization is already in progress (state: {previous.state}). "
                    "Use `pif status`, `pif resume` or `pif cancel`."
                )
            self.ws.archive(f"{previous.id}-{now().replace(':', '')}")
        created = now()
        st = ProjectState(
            id=f"{_slug(name or request)}-{created[:10]}",
            name=name or request.strip()[:80],
            request=request.strip(),
            created=created,
            fields={k: str(v).strip() for k, v in (fields or {}).items() if str(v).strip()},
        )
        self.ws.log("request_received", request=st.request, framework_version=__version__)

        def operation():
            self._transition(st, State.BOOTSTRAP, "request received")
            result = self.bootstrapper.bootstrap(
                st, request, knowledge_paths, auto_detect, knowledge_config, home
            )
            self.ws.log("bootstrap_assessment", **result)
            self._finish_bootstrap(st)

        return self._run(st, operation)

    def answer(self, field: str, value: str) -> dict:
        st = self._load()

        def operation():
            current = State(st.state)
            if field in KNOWLEDGE_FIELDS:
                if current is not State.BOOTSTRAP:
                    raise GuardError("Knowledge questions are answered only during bootstrap.")
                status = self.bootstrapper.resolve_knowledge(st, field, value)
                self.ws.log("knowledge_resolved", field=field, status=status,
                            sources=[s["location"] for s in st.knowledge.get("sources", [])])
                self._finish_bootstrap(st)
                return
            if field not in FIELD_MAP:
                raise GuardError(f"Unknown field '{field}'. Valid fields: {', '.join(FIELD_MAP)}.")
            if current is State.BOOTSTRAP:
                raise GuardError("Answer the pending knowledge question first (see `pif next`).")
            if current in (State.VALIDATION, State.PRD_REVIEW):
                self._transition(st, State.DISCOVERY, f"user changed {field}")
            elif current is not State.DISCOVERY:
                raise GuardError(f"Answers cannot be recorded in state '{current.value}'.")
            before = assess(st.fields).clarity
            self.bootstrapper.record_answer(st, field, value)
            after = assess(st.fields)
            st.counters["questions_answered"] += 1
            self.ws.log("answer_recorded", field=field, clarity_before=before, clarity_after=after.clarity)
            if after.ready:
                self._transition(st, State.VALIDATION, "uncertainty low enough")
                self._enter_validation(st)
            elif st.counters["questions_answered"] >= MAX_QUESTIONS:
                self._transition(st, State.VALIDATION, "question budget reached")
                self._enter_validation(st)

        return self._run(st, operation)

    def summary(self) -> dict:
        st = self._load()

        def operation():
            current = State(st.state)
            if current is State.DISCOVERY:
                self._transition(st, State.VALIDATION, "summary requested")
            elif current is not State.VALIDATION:
                raise GuardError(f"A summary cannot be produced in state '{current.value}'.")
            self._enter_validation(st)

        return self._run(st, operation)

    def approve(self) -> dict:
        st = self._load()

        def operation():
            current = State(st.state)
            if current is State.VALIDATION:
                assessment = assess(st.fields)
                if not assessment.critical_complete:
                    gaps = [n for n in assessment.ordered_gaps if FIELD_MAP[n].critical]
                    raise GuardError(
                        "The summary cannot be approved: critical fields are incomplete: "
                        + ", ".join(gaps) + ". Record them with `pif answer FIELD VALUE`."
                    )
                for resource in st.knowledge.get("selected_resources") or []:
                    resource["status"] = "approved"
                self.ws.log("summary_approved", clarity=assessment.clarity)
                self._transition(st, State.PRD_GENERATION, "summary approved by the user")
                self._generate_prd(st)
            elif current is State.PRD_GENERATION:
                self._generate_prd(st)  # retry after `pif resume`
            elif current is State.PRD_REVIEW:
                prd = self.ws.read(PRD_FILE)
                issues = check_prd(prd)
                if issues:
                    raise GuardError("The PRD does not pass the quality gate: " + "; ".join(issues))
                self.ws.write(PRD_FILE, mark_prd_approved(prd))
                self.ws.log("prd_approved")
                self._transition(st, State.COMPLETED, "PRD approved by the user")
                self.ws.log("initialization_completed")
                self.ws.write(HANDOFF_FILE, json.dumps(self._handoff(st), indent=2, ensure_ascii=False) + "\n")
            else:
                raise GuardError(f"Nothing to approve in state '{current.value}'.")

        return self._run(st, operation)

    def reject(self, reason: str) -> dict:
        st = self._load()

        def operation():
            current = State(st.state)
            if current is State.VALIDATION:
                st.counters["summary_rejections"] += 1
                event = "summary_rejected"
            elif current is State.PRD_REVIEW:
                st.counters["prd_rejections"] += 1
                event = "prd_rejected"
            else:
                raise GuardError(f"Nothing to reject in state '{current.value}'.")
            st.notes.append({"at": now(), "stage": current.value, "reason": reason})
            self.ws.log(event, reason=reason)
            self._transition(st, State.DISCOVERY, f"rejected: {reason}")

        return self._run(st, operation)

    def cancel(self, reason: str = "cancelled by the user") -> dict:
        st = self._load()
        return self._run(st, lambda: self._transition(st, State.CANCELLED, reason))

    def resume(self) -> dict:
        st = self._load()

        def operation():
            if State(st.state) is not State.ERROR:
                raise GuardError(f"Nothing to resume: the state is '{st.state}'.")
            target = st.last_valid_state
            st.history.append({"from": "error", "to": target, "at": now(), "reason": "resumed"})
            self.ws.log("state_transition", **{"from": "error", "to": target, "reason": "resumed"})
            st.state = target
            st.error = None

        return self._run(st, operation)

    # -- read-only -----------------------------------------------------------
    def status(self, st: Optional[ProjectState] = None) -> dict:
        if st is None:
            if not self.ws.exists():
                return {"state": State.WAITING.value, "next_action": 'Run: pif start "<request>"'}
            st = self.ws.load()
        assessment = assess(st.fields)
        question = None
        if State(st.state) in (State.BOOTSTRAP, State.DISCOVERY):
            question = self.bootstrapper.discovery.next_question(st)
        artifacts = {
            name: str(self.ws.path(name))
            for name in (SUMMARY_FILE, PRD_FILE, HANDOFF_FILE)
            if self.ws.path(name).exists()
        }
        return {
            "project": st.name,
            "id": st.id,
            "state": st.state,
            "project_type": st.project_type,
            **assessment.to_dict(),
            "questions_answered": st.counters.get("questions_answered", 0),
            "question_budget": MAX_QUESTIONS,
            "next_question": question,
            "next_action": self._next_action(st, question),
            "knowledge": {
                "status": st.knowledge.get("status"),
                "sources": [s["location"] for s in st.knowledge.get("sources", [])],
                "selected_resources": len(st.knowledge.get("selected_resources") or []),
            },
            "artifacts": artifacts,
            "error": st.error,
        }

    @staticmethod
    def _next_action(st: ProjectState, question: Optional[dict]) -> str:
        current = State(st.state)
        if current in (State.BOOTSTRAP, State.DISCOVERY) and question:
            return f"Ask the user the next question, then run: pif answer {question['field']} \"<answer>\""
        return {
            State.WAITING: 'Run: pif start "<request>"',
            State.DISCOVERY: "Run: pif summary (or record requested changes with: pif answer FIELD VALUE)",
            State.VALIDATION: (
                "Show executive-summary.md to the user. Approved: pif approve. "
                "Changes: pif answer FIELD VALUE. Rejected: pif reject --reason \"...\""
            ),
            State.PRD_GENERATION: "Run: pif approve (generates the PRD again after a resumed error)",
            State.PRD_REVIEW: (
                "Show PRD.md to the user. Approved: pif approve. "
                "Changes: pif reject --reason \"...\" then pif answer FIELD VALUE"
            ),
            State.COMPLETED: "Initialization complete. Hand handoff.json and PRD.md to the next execution layer.",
            State.CANCELLED: 'Cancelled. Start again with: pif start "<request>"',
            State.ERROR: "Fix the reported error, then run: pif resume",
        }[current]

    def _handoff(self, st: ProjectState) -> dict:
        assessment = assess(st.fields)
        report = build_report(st, self.ws.events())
        return {
            "framework": "project-initialization-framework",
            "framework_version": __version__,
            "project": {"id": st.id, "name": st.name, "type": st.project_type},
            "state": st.state,
            "prd": str(self.ws.path(PRD_FILE)),
            "executive_summary": str(self.ws.path(SUMMARY_FILE)),
            "clarity": assessment.clarity,
            "open_questions": assessment.ordered_gaps,
            "knowledge": {
                "status": st.knowledge.get("status"),
                "sources": [s["location"] for s in st.knowledge.get("sources", [])],
                "selected_resources": st.knowledge.get("selected_resources") or [],
            },
            "metrics": {k: v for k, v in report.items() if k != "checks"},
            "completed_at": now(),
        }
