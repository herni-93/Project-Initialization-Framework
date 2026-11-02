"""Project state persistence and the event log (``.pif/`` by default)."""

from __future__ import annotations

import json
import shutil
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .states import State

STATE_FILE = "state.json"
EVENTS_FILE = "events.jsonl"
SUMMARY_FILE = "executive-summary.md"
PRD_FILE = "PRD.md"
HANDOFF_FILE = "handoff.json"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _default_knowledge() -> dict:
    return {"status": "unknown", "sources": [], "selected_resources": [], "snippets": []}


def _default_counters() -> dict:
    return {
        "questions_answered": 0,
        "validation_rounds": 0,
        "summary_rejections": 0,
        "prd_generations": 0,
        "prd_rejections": 0,
    }


@dataclass
class ProjectState:
    id: str = ""
    name: str = ""
    request: str = ""
    project_type: str = "general"
    state: str = State.WAITING.value
    last_valid_state: str = State.WAITING.value
    created: str = ""
    updated: str = ""
    fields: dict = field(default_factory=dict)
    knowledge: dict = field(default_factory=_default_knowledge)
    counters: dict = field(default_factory=_default_counters)
    notes: list = field(default_factory=list)
    history: list = field(default_factory=list)
    initial_clarity: Optional[int] = None
    error: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "ProjectState":
        known = set(cls.__dataclass_fields__)
        return cls(**{k: v for k, v in data.items() if k in known})

    def to_dict(self) -> dict:
        return asdict(self)


class Workspace:
    def __init__(self, root):
        self.root = Path(root)

    def path(self, name: str) -> Path:
        return self.root / name

    def exists(self) -> bool:
        return self.path(STATE_FILE).is_file()

    def load(self) -> ProjectState:
        with open(self.path(STATE_FILE), encoding="utf-8") as fh:
            return ProjectState.from_dict(json.load(fh))

    def save(self, state: ProjectState) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        state.updated = now()
        tmp = self.path(STATE_FILE + ".tmp")
        tmp.write_text(json.dumps(state.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(self.path(STATE_FILE))

    def log(self, event_type: str, **data) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        record = {"ts": now(), "type": event_type, **data}
        with open(self.path(EVENTS_FILE), "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    def events(self) -> list:
        if not self.path(EVENTS_FILE).is_file():
            return []
        with open(self.path(EVENTS_FILE), encoding="utf-8") as fh:
            return [json.loads(line) for line in fh if line.strip()]

    def write(self, name: str, text: str) -> Path:
        self.root.mkdir(parents=True, exist_ok=True)
        target = self.path(name)
        target.write_text(text, encoding="utf-8")
        return target

    def read(self, name: str) -> str:
        return self.path(name).read_text(encoding="utf-8")

    def archive(self, label: str) -> Optional[Path]:
        """Move a finished initialization to ``archive/<label>`` before a new one starts."""
        files = [self.path(n) for n in (STATE_FILE, EVENTS_FILE, SUMMARY_FILE, PRD_FILE, HANDOFF_FILE)]
        files = [f for f in files if f.exists()]
        if not files:
            return None
        target = self.root / "archive" / label
        target.mkdir(parents=True, exist_ok=True)
        for f in files:
            shutil.move(str(f), str(target / f.name))
        return target
