"""Project Bootstrapper: classifies the request, connects existing knowledge,
delegates discovery to the Discovery Engine and generates the PRD.

It never changes the project state and never continues the workflow on its own:
every method returns control to the Project Orchestrator.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

from .discovery import DiscoveryEngine
from .documents import render_prd
from .errors import GuardError
from .knowledge import KnowledgeConnector, sources_from_path
from .questions import detect_project_type, extract_terms, is_no, is_yes
from .uncertainty import assess
from .workspace import ProjectState


class Bootstrapper:
    def __init__(self, discovery: Optional[DiscoveryEngine] = None, templates_dir=None):
        self.templates_dir = templates_dir
        self.discovery = discovery or DiscoveryEngine(templates_dir=templates_dir)

    # -- bootstrap -----------------------------------------------------------
    def bootstrap(self, state: ProjectState, request: str, knowledge_paths: Iterable = (),
                  auto_detect: bool = True, knowledge_config=None, home=None) -> dict:
        state.project_type = detect_project_type(request)
        if request.strip():
            state.fields.setdefault("objective", request.strip())
        state.initial_clarity = assess(state.fields).clarity

        connector, disabled = KnowledgeConnector.discover(
            explicit_paths=knowledge_paths,
            config_path=knowledge_config,
            auto_detect=auto_detect,
            home=home,
        )
        knowledge = state.knowledge
        if disabled:
            knowledge["status"] = "disabled"
        elif connector.sources:
            knowledge["sources"] = [s.spec() for s in connector.sources]
            knowledge["status"] = "pending_consent" if connector.needs_consent else "connected"
        else:
            knowledge["status"] = "pending_source"
        return {"project_type": state.project_type, "clarity": state.initial_clarity,
                "knowledge_status": knowledge["status"]}

    @staticmethod
    def knowledge_pending(state: ProjectState) -> bool:
        return state.knowledge.get("status") in ("pending_consent", "pending_source")

    def resolve_knowledge(self, state: ProjectState, field: str, answer: str) -> str:
        knowledge = state.knowledge
        answer = (answer or "").strip()
        if field == "knowledge_consent":
            if knowledge.get("status") != "pending_consent":
                raise GuardError("No knowledge consent question is pending.")
            if is_yes(answer):
                knowledge["status"] = "connected"
            elif is_no(answer):
                knowledge["status"] = "declined"
                knowledge["sources"] = []
            else:
                raise GuardError("Answer 'yes' or 'no'.")
        elif field == "knowledge_source":
            if knowledge.get("status") != "pending_source":
                raise GuardError("No knowledge source question is pending.")
            if not answer or is_no(answer):
                knowledge["status"] = "none"
            else:
                sources = sources_from_path(Path(answer).expanduser(), "explicit")
                if not sources:
                    raise GuardError(
                        f"No knowledge base found at '{answer}'. Give another path or answer 'no'."
                    )
                knowledge["sources"] = [s.spec() for s in sources]
                knowledge["status"] = "connected"
        else:
            raise GuardError(f"Unknown knowledge question '{field}'.")
        return knowledge["status"]

    # -- discovery (delegated) ----------------------------------------------
    def record_answer(self, state: ProjectState, field: str, value: str) -> None:
        self.discovery.record_answer(state, field, value)

    def summarize(self, state: ProjectState) -> str:
        self._select_knowledge(state)
        return self.discovery.summarize(state)

    # -- PRD -----------------------------------------------------------------
    def generate_prd(self, state: ProjectState) -> str:
        return render_prd(state, self.templates_dir)

    def _select_knowledge(self, state: ProjectState) -> None:
        knowledge = state.knowledge
        if knowledge.get("status") != "connected":
            return
        connector = KnowledgeConnector.from_specs(knowledge.get("sources", []))
        text = " ".join([state.project_type] + [str(v) for v in state.fields.values()])
        terms = extract_terms(text)
        knowledge["selected_resources"] = connector.select_resources(terms)
        knowledge["snippets"] = [
            {"title": s.title, "path": s.path, "excerpt": s.excerpt, "score": s.score}
            for s in connector.query(terms, limit=5)
        ]
