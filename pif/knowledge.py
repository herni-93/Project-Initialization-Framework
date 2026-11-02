"""Knowledge Connector.

Connects, read-only, to a knowledge system the user already has on this machine:
a second brain or notes vault (Markdown), a JSON knowledge graph, or a Neo4j
graph database. It never creates, modifies or copies a knowledge base. When no
source exists, the framework ignores this module completely.

Detection order:
1. Paths given explicitly (``--knowledge PATH`` or the user's answer).
2. A config file: ``./pif.knowledge.json`` or ``~/.config/pif/knowledge.json``.
3. The ``PIF_KNOWLEDGE_PATH`` environment variable (os.pathsep-separated).
4. Auto-detection in a few common folders under the home directory
   (only when nothing above was found; needs the user's consent).

Set ``PIF_KNOWLEDGE=off`` (or ``"enabled": false`` in the config) to disable it.
"""

from __future__ import annotations

import base64
import json
import os
import re
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Iterator, Optional

from .errors import GuardError

ENV_PATHS = "PIF_KNOWLEDGE_PATH"
ENV_SWITCH = "PIF_KNOWLEDGE"
LOCAL_CONFIG = "pif.knowledge.json"
USER_CONFIG = Path(".config") / "pif" / "knowledge.json"

AUTO_CANDIDATES = (
    ".claude",
    "brain",
    "Brain",
    "second-brain",
    "SecondBrain",
    "knowledge",
    "Knowledge",
    "notes",
    "Obsidian",
    "Documents/brain",
    "Documents/Obsidian",
)

INDEX_FILES = ("INDEX.md", "index.md", "Index.md", "README.md")
ROOT_PROMPT_FILES = ("CLAUDE.md", "AGENTS.md", "SYSTEM.md", "system-prompt.md", "GEMINI.md")
GRAPH_FILES = ("graph.json", "knowledge-graph.json")

CATEGORY_ALIASES = {
    "system_prompt": ("system-prompts", "system-prompt", "prompts", "prompt"),
    "skill": ("skills", "skill"),
    "workflow": ("workflows", "workflow"),
    "agent": ("agents", "agent"),
    "plugin": ("plugins", "plugin"),
    "script": ("scripts", "script"),
    "reference": ("references", "reference", "refs"),
    "template": ("templates", "template"),
    "knowledge": ("knowledge", "wiki", "notes", "note"),
    "command": ("commands", "command"),
}


def _norm(name: str) -> str:
    return re.sub(r"[\s_\-]+", "", name.lower())


CATEGORY_LOOKUP = {
    _norm(alias): kind for kind, aliases in CATEGORY_ALIASES.items() for alias in aliases
}
CATEGORY_LOOKUP.update({_norm(kind): kind for kind in CATEGORY_ALIASES})

TEXT_SUFFIXES = {".md", ".markdown", ".txt"}
RESOURCE_SUFFIXES = TEXT_SUFFIXES | {".json", ".yaml", ".yml", ".py", ".sh", ".js", ".ts"}
SKIP_DIRS = {"node_modules", "__pycache__", ".git", ".obsidian", ".trash", "archive"}
# Inside ~/.claude only configuration is knowledge; session data is not.
CLAUDE_HOME_SKIP = {
    "projects", "todos", "shell-snapshots", "statsig", "logs", "ide", "debug",
    "file-history", "session-env", "cache", "plans", "local", "downloads",
}

MAX_FILES_SCANNED = 2000
HEAD_CHARS = 4000


@dataclass
class Resource:
    kind: str
    name: str
    path: str
    description: str = ""
    source: str = ""


@dataclass
class Snippet:
    source: str
    title: str
    path: str
    excerpt: str
    score: int


def _read_head(path: Path, max_chars: int = HEAD_CHARS) -> str:
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            return fh.read(max_chars)
    except OSError:
        return ""


def _safe_iterdir(path: Path) -> list:
    try:
        return sorted(path.iterdir(), key=lambda p: p.name.lower())
    except OSError:
        return []


def describe(path: Path) -> str:
    """One-line description: frontmatter ``description`` or first text line."""
    head = _read_head(path, 2000)
    block = re.search(r"^description:\s*[>|]-?\s*\n[ \t]+(.+)$", head, re.M)
    if block:
        return block.group(1).strip()[:160]
    inline = re.search(r"^description:\s*(.+)$", head, re.M)
    if inline:
        return inline.group(1).strip().strip("\"'")[:160]
    body = head
    if head.startswith("---"):
        parts = head.split("---", 2)
        body = parts[2] if len(parts) == 3 else ""
    for line in body.splitlines():
        text = line.strip()
        if text and not text.startswith(("#", "---", "```", "|", ">", "<")):
            return text[:160]
    for line in body.splitlines():
        if line.strip().startswith("#"):
            return line.strip().lstrip("#").strip()[:160]
    return ""


def _title(path: Path, head: str) -> str:
    match = re.search(r"^#\s+(.+)$", head, re.M)
    return match.group(1).strip() if match else path.stem


def _excerpt(text: str, terms: Iterable[str], size: int = 240) -> str:
    lowered = [t.lower() for t in terms]
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    # Prefer body text, then a frontmatter description, then anything else.
    body = [l for l in lines if not l.startswith(("#", "---")) and not re.match(r"^\w+:\s", l)]
    descriptions = [m.group(1) for l in lines for m in [re.match(r"^description:\s*(.+)$", l)] if m]
    for line in body + descriptions + lines:
        if any(t in line.lower() for t in lowered):
            return line[:size]
    return " ".join(body or lines)[:size]


class MarkdownSource:
    """A folder of Markdown notes: second brain, Obsidian vault, prompts/skills folder."""

    kind = "markdown"

    def __init__(self, root, origin: str = "auto"):
        self.root = Path(root).expanduser()
        self.origin = origin

    @property
    def location(self) -> str:
        return str(self.root)

    def spec(self) -> dict:
        return {"type": self.kind, "location": self.location, "origin": self.origin}

    @staticmethod
    def looks_like_knowledge_base(path) -> bool:
        path = Path(path)
        if not path.is_dir():
            return False
        entries = _safe_iterdir(path)
        names = {e.name for e in entries}
        if names & set(INDEX_FILES) or names & set(ROOT_PROMPT_FILES) or ".obsidian" in names:
            return True
        return any(e.is_dir() and _norm(e.name) in CATEGORY_LOOKUP for e in entries)

    def index_excerpt(self, max_chars: int = HEAD_CHARS) -> str:
        """Read only the index first: it is the map of the knowledge base."""
        for name in INDEX_FILES:
            candidate = self.root / name
            if candidate.is_file():
                return _read_head(candidate, max_chars)
        return ""

    def _skip_dir(self, directory: Path, name: str) -> bool:
        if name.startswith(".") or name in SKIP_DIRS:
            return True
        return directory == self.root and self.root.name == ".claude" and name in CLAUDE_HOME_SKIP

    def inventory(self, per_category: int = 100) -> list:
        resources = []
        for name in ROOT_PROMPT_FILES:
            candidate = self.root / name
            if candidate.is_file():
                resources.append(
                    Resource("system_prompt", name, str(candidate), describe(candidate), self.location)
                )
        for child in _safe_iterdir(self.root):
            if not child.is_dir() or self._skip_dir(self.root, child.name):
                continue
            kind = CATEGORY_LOOKUP.get(_norm(child.name))
            if not kind:
                continue
            count = 0
            for entry in _safe_iterdir(child):
                if count >= per_category or entry.name.startswith("."):
                    continue
                doc: Optional[Path] = None
                if entry.is_dir():
                    for name in ("SKILL.md", "README.md", "INDEX.md", "index.md"):
                        if (entry / name).is_file():
                            doc = entry / name
                            break
                    label = entry.name
                elif entry.suffix.lower() in RESOURCE_SUFFIXES:
                    doc = entry
                    label = entry.stem
                else:
                    continue
                description = describe(doc) if doc and doc.suffix.lower() in TEXT_SUFFIXES else ""
                resources.append(
                    Resource(kind, label, str(doc or entry), description, self.location)
                )
                count += 1
        return resources

    def iter_documents(self, max_files: int = MAX_FILES_SCANNED) -> Iterator[Path]:
        seen = 0
        for dirpath, dirnames, filenames in os.walk(self.root):
            current = Path(dirpath)
            dirnames[:] = sorted(d for d in dirnames if not self._skip_dir(current, d))
            for filename in sorted(filenames):
                path = current / filename
                if path.suffix.lower() in TEXT_SUFFIXES:
                    yield path
                    seen += 1
                    if seen >= max_files:
                        return

    def query(self, terms: Iterable[str], limit: int = 10) -> list:
        terms = [t.lower() for t in terms if t]
        if not terms:
            return []
        scored = []
        for path in self.iter_documents():
            head = _read_head(path)
            haystack = head.lower()
            stem = path.stem.lower()
            score = sum(min(haystack.count(t), 5) for t in terms)
            score += sum(3 for t in terms if t in stem)
            if score:
                scored.append((score, path, head))
        scored.sort(key=lambda item: (-item[0], str(item[1])))
        return [
            Snippet(self.location, _title(path, head), str(path), _excerpt(head, terms), score)
            for score, path, head in scored[:limit]
        ]


class JsonGraphSource:
    """A JSON knowledge graph: ``{"nodes": [...], "edges": [...]}``.

    Nodes may use ``id``, ``label``/``name``/``title``, ``type``/``kind``,
    ``text``/``description``/``content`` and ``tags``. Edges (or ``links``) use
    ``source`` and ``target``.
    """

    kind = "json-graph"

    def __init__(self, path, origin: str = "auto"):
        self.path = Path(path).expanduser()
        self.origin = origin
        self._data: Optional[dict] = None

    @property
    def location(self) -> str:
        return str(self.path)

    def spec(self) -> dict:
        return {"type": self.kind, "location": self.location, "origin": self.origin}

    @staticmethod
    def looks_like_graph(path) -> bool:
        path = Path(path)
        if not path.is_file() or path.suffix.lower() != ".json":
            return False
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError):
            return False
        return isinstance(data, dict) and isinstance(data.get("nodes"), list)

    def _load(self) -> dict:
        if self._data is None:
            with open(self.path, encoding="utf-8") as fh:
                self._data = json.load(fh)
        return self._data

    @staticmethod
    def _label(node: dict) -> str:
        return str(node.get("label") or node.get("name") or node.get("title") or node.get("id"))

    @staticmethod
    def _text(node: dict) -> str:
        return str(
            node.get("text") or node.get("description") or node.get("content")
            or node.get("summary") or ""
        )

    def inventory(self) -> list:
        resources = []
        for node in self._load().get("nodes", []):
            kind = CATEGORY_LOOKUP.get(_norm(str(node.get("type") or node.get("kind") or "")))
            if kind:
                resources.append(
                    Resource(
                        kind,
                        self._label(node),
                        f"{self.location}#{node.get('id')}",
                        self._text(node)[:160],
                        self.location,
                    )
                )
        return resources

    def query(self, terms: Iterable[str], limit: int = 10) -> list:
        terms = [t.lower() for t in terms if t]
        data = self._load()
        nodes = data.get("nodes", [])
        labels = {str(n.get("id")): self._label(n) for n in nodes}
        neighbours: dict = {}
        for edge in data.get("edges") or data.get("links") or []:
            a, b = str(edge.get("source")), str(edge.get("target"))
            neighbours.setdefault(a, []).append(labels.get(b, b))
            neighbours.setdefault(b, []).append(labels.get(a, a))
        scored = []
        for node in nodes:
            label = self._label(node).lower()
            text = self._text(node).lower()
            tags = " ".join(str(t) for t in node.get("tags", [])).lower()
            score = sum(3 for t in terms if t in label)
            score += sum(min(text.count(t), 5) for t in terms)
            score += sum(2 for t in terms if t in tags)
            if score:
                scored.append((score, node))
        scored.sort(key=lambda item: -item[0])
        snippets = []
        for score, node in scored[:limit]:
            excerpt = _excerpt(self._text(node), terms, 200)
            related = neighbours.get(str(node.get("id")), [])
            if related:
                excerpt = f"{excerpt} | related: {', '.join(related[:5])}"
            snippets.append(
                Snippet(self.location, self._label(node), f"{self.location}#{node.get('id')}", excerpt, score)
            )
        return snippets


class Neo4jSource:
    """A Neo4j graph database reached through its HTTP API (read-only queries)."""

    kind = "neo4j"

    def __init__(self, url: str, database: str = "neo4j", user_env: str = "NEO4J_USER",
                 password_env: str = "NEO4J_PASSWORD", origin: str = "config", timeout: int = 5):
        self.url = url.rstrip("/")
        self.database = database
        self.user_env = user_env
        self.password_env = password_env
        self.origin = origin
        self.timeout = timeout

    @property
    def location(self) -> str:
        return self.url

    def spec(self) -> dict:
        return {
            "type": self.kind, "location": self.url, "database": self.database,
            "user_env": self.user_env, "password_env": self.password_env, "origin": self.origin,
        }

    def _run(self, statement: str, parameters: dict) -> list:
        body = json.dumps({"statements": [{"statement": statement, "parameters": parameters}]})
        request = urllib.request.Request(
            f"{self.url}/db/{self.database}/tx/commit",
            data=body.encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        user, password = os.environ.get(self.user_env), os.environ.get(self.password_env)
        if user and password:
            token = base64.b64encode(f"{user}:{password}".encode()).decode()
            request.add_header("Authorization", f"Basic {token}")
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            payload = json.load(response)
        if payload.get("errors"):
            raise RuntimeError(payload["errors"][0].get("message", "Neo4j error"))
        result = payload["results"][0]
        return [dict(zip(result["columns"], row["row"])) for row in result["data"]]

    def available(self) -> bool:
        try:
            self._run("RETURN 1 AS ok", {})
            return True
        except Exception:
            return False

    def inventory(self) -> list:
        rows = self._run(
            "MATCH (n) WHERE any(l IN labels(n) WHERE toLower(l) IN $kinds) "
            "RETURN labels(n) AS labels, coalesce(n.name, n.title, toString(id(n))) AS name, "
            "coalesce(n.description, n.summary, '') AS description LIMIT 300",
            {"kinds": sorted(CATEGORY_LOOKUP)},
        )
        resources = []
        for row in rows:
            kind = next(
                (CATEGORY_LOOKUP[_norm(l)] for l in row["labels"] if _norm(l) in CATEGORY_LOOKUP),
                "knowledge",
            )
            resources.append(
                Resource(kind, str(row["name"]), f"{self.url}#{row['name']}",
                         str(row["description"])[:160], self.url)
            )
        return resources

    def query(self, terms: Iterable[str], limit: int = 10) -> list:
        rows = self._run(
            "UNWIND $terms AS t MATCH (n) "
            "WHERE any(k IN keys(n) WHERE toLower(toString(n[k])) CONTAINS t) "
            "RETURN coalesce(n.name, n.title, toString(id(n))) AS name, "
            "coalesce(n.description, n.summary, n.text, '') AS text, count(t) AS score "
            "ORDER BY score DESC LIMIT $limit",
            {"terms": [t.lower() for t in terms], "limit": limit},
        )
        return [
            Snippet(self.url, str(r["name"]), f"{self.url}#{r['name']}", str(r["text"])[:240], int(r["score"]))
            for r in rows
        ]


def source_from_spec(spec: dict):
    kind = spec.get("type")
    origin = spec.get("origin", "config")
    location = os.path.expanduser(str(spec.get("location") or spec.get("path") or spec.get("url") or ""))
    if kind == "markdown":
        return MarkdownSource(location, origin)
    if kind == "json-graph":
        return JsonGraphSource(location, origin)
    if kind == "neo4j":
        return Neo4jSource(
            location,
            database=spec.get("database", "neo4j"),
            user_env=spec.get("user_env", "NEO4J_USER"),
            password_env=spec.get("password_env", "NEO4J_PASSWORD"),
            origin=origin,
        )
    raise ValueError(f"Unknown knowledge source type: {kind!r}")


def sources_from_path(path, origin: str) -> list:
    """Build sources for a path. Explicit paths are trusted; auto paths must look like a knowledge base."""
    path = Path(path).expanduser()
    if path.is_file():
        return [JsonGraphSource(path, origin)] if JsonGraphSource.looks_like_graph(path) else []
    if not path.is_dir():
        return []
    found = []
    if origin != "auto" or MarkdownSource.looks_like_knowledge_base(path):
        found.append(MarkdownSource(path, origin))
    for name in GRAPH_FILES:
        if JsonGraphSource.looks_like_graph(path / name):
            found.append(JsonGraphSource(path / name, origin))
    return found


class KnowledgeConnector:
    def __init__(self, sources: Optional[list] = None):
        self.sources = list(sources or [])

    @classmethod
    def from_specs(cls, specs: Iterable[dict]) -> "KnowledgeConnector":
        sources = []
        for spec in specs:
            try:
                sources.append(source_from_spec(spec))
            except ValueError:
                continue
        return cls(sources)

    @classmethod
    def discover(cls, explicit_paths: Iterable = (), config_path=None, auto_detect: bool = True,
                 home=None, cwd=None, env=None):
        """Return ``(connector, disabled)``."""
        env = os.environ if env is None else env
        if str(env.get(ENV_SWITCH, "")).lower() in {"off", "0", "false", "no"}:
            return cls(), True
        home = Path(home) if home else Path.home()
        cwd = Path(cwd) if cwd else Path.cwd()
        found = []

        for path in explicit_paths or ():
            sources = sources_from_path(path, "explicit")
            if not sources:
                raise GuardError(f"No knowledge base found at {path}.")
            found.extend(sources)

        if config_path:
            config_path = Path(config_path).expanduser()
            if not config_path.is_file():
                raise GuardError(f"Knowledge config not found: {config_path}")
            configs = [config_path]
        else:
            configs = [cwd / LOCAL_CONFIG, home / USER_CONFIG]
        for config in configs:
            if not config.is_file():
                continue
            with open(config, encoding="utf-8") as fh:
                data = json.load(fh)
            if data.get("enabled") is False:
                return cls(), True
            for spec in data.get("sources", []):
                spec = dict(spec)
                spec.setdefault("origin", "config")
                try:
                    source = source_from_spec(spec)
                except ValueError:
                    continue
                if isinstance(source, Neo4jSource):
                    if source.available():
                        found.append(source)
                elif Path(source.location).exists():
                    found.append(source)

        for path in str(env.get(ENV_PATHS, "")).split(os.pathsep):
            if path.strip():
                found.extend(sources_from_path(path.strip(), "env"))

        if auto_detect and not found:
            for candidate in AUTO_CANDIDATES:
                found.extend(sources_from_path(home / candidate, "auto"))

        unique, seen = [], set()
        for source in found:
            if source.location not in seen:
                seen.add(source.location)
                unique.append(source)
        return cls(unique), False

    @property
    def needs_consent(self) -> bool:
        return any(s.origin == "auto" for s in self.sources)

    def scan(self) -> dict:
        report = {"sources": [], "resources": []}
        for source in self.sources:
            entry = source.spec()
            try:
                inventory = source.inventory()
            except Exception as exc:  # an unreachable source is skipped, never fatal
                entry["error"] = str(exc)
                report["sources"].append(entry)
                continue
            by_kind: dict = {}
            for resource in inventory:
                by_kind[resource.kind] = by_kind.get(resource.kind, 0) + 1
            entry["resources"] = len(inventory)
            entry["by_kind"] = by_kind
            if isinstance(source, MarkdownSource):
                entry["has_index"] = bool(source.index_excerpt(200))
            report["sources"].append(entry)
            report["resources"].extend(asdict(r) for r in inventory)
        return report

    def query(self, terms: Iterable[str], limit: int = 10) -> list:
        terms = list(terms)
        snippets = []
        for source in self.sources:
            try:
                snippets.extend(source.query(terms, limit))
            except Exception:
                continue
        snippets.sort(key=lambda s: -s.score)
        return snippets[:limit]

    def select_resources(self, terms: Iterable[str], limit: int = 10) -> list:
        """Propose the resources worth loading for this project, with a reason for each."""
        terms = [t.lower() for t in terms]
        selected = []
        for source in self.sources:
            try:
                inventory = source.inventory()
            except Exception:
                continue
            for resource in inventory:
                if resource.kind == "system_prompt" and resource.name in ROOT_PROMPT_FILES:
                    selected.append((100, resource, "global working instructions of the user", "high"))
                    continue
                haystack = re.sub(r"[_\-/]+", " ", f"{resource.name} {resource.description}".lower())
                matched = [t for t in terms if t in haystack]
                if not matched:
                    continue
                score = len(matched)
                priority = "high" if score >= 3 else "medium" if score == 2 else "low"
                selected.append((score, resource, f"matches: {', '.join(matched[:5])}", priority))
        selected.sort(key=lambda item: (-item[0], item[1].name))
        unique, seen = [], set()
        for item in selected:  # the same resource may appear in several sources
            key = (item[1].kind, item[1].name.lower())
            if key not in seen:
                seen.add(key)
                unique.append(item)
        selected = unique
        return [
            {
                "resource": resource.name,
                "kind": resource.kind,
                "path": resource.path,
                "reason": reason,
                "priority": priority,
                "status": "proposed",
            }
            for _, resource, reason, priority in selected[:limit]
        ]
