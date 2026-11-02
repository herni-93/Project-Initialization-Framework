"""Command line interface.

Step-by-step commands print JSON so an AI agent can drive the initialization
while it talks to the user. ``pif run`` is an interactive mode for humans.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Callable, Optional

from .documents import check_prd
from .errors import PifError
from .knowledge import KnowledgeConnector
from .metrics import build_report, report_to_markdown
from .orchestrator import Orchestrator
from .questions import extract_terms, is_no, is_yes
from .workspace import PRD_FILE, SUMMARY_FILE, Workspace


def _print(data) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def _parse_fields(pairs) -> dict:
    fields = {}
    for pair in pairs or []:
        if "=" not in pair:
            raise PifError(f"Use FIELD=VALUE for --field (got '{pair}').")
        key, value = pair.split("=", 1)
        fields[key.strip()] = value.strip()
    return fields


def _start_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("request")
    p.add_argument("--name")
    p.add_argument("--field", action="append", default=[], metavar="FIELD=VALUE",
                   help="Information already present in the request. Repeatable.")
    _knowledge_args(p)


def _knowledge_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--knowledge", action="append", default=[], metavar="PATH",
                   help="Path to an existing knowledge base (folder or graph JSON). Repeatable.")
    p.add_argument("--knowledge-config", metavar="FILE", help="Knowledge connector config file.")
    p.add_argument("--no-auto-detect", action="store_true",
                   help="Do not look for knowledge bases in common folders.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pif", description="Project Initialization Framework")
    parser.add_argument("--dir", default=".pif", help="Workspace directory (default: .pif)")
    parser.add_argument("--templates", default=None, help="Templates directory (default: repo templates/)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("start", help="Start an initialization from a request")
    _start_args(p)

    sub.add_parser("status", help="Show state, clarity score and next action")
    sub.add_parser("next", help="Show only the next question")

    p = sub.add_parser("answer", help="Record the user's answer for a field")
    p.add_argument("field")
    p.add_argument("value", nargs="+")

    sub.add_parser("summary", help="Close discovery and produce the executive summary")
    sub.add_parser("approve", help="Approve the summary (validation) or the PRD (prd_review)")

    p = sub.add_parser("reject", help="Reject the summary or the PRD")
    p.add_argument("--reason", required=True)

    p = sub.add_parser("cancel", help="Cancel the initialization")
    p.add_argument("--reason", default="cancelled by the user")

    sub.add_parser("resume", help="Resume from the last valid state after an error")

    p = sub.add_parser("check-prd", help="Run the PRD quality gate on a file")
    p.add_argument("file", nargs="?")

    p = sub.add_parser("metrics", help="Initialization metrics")
    p.add_argument("--format", choices=("json", "md"), default="json")

    p = sub.add_parser("knowledge", help="Inspect existing knowledge bases (read-only)")
    ksub = p.add_subparsers(dest="knowledge_command", required=True)
    kp = ksub.add_parser("scan", help="Detect sources and list their resources")
    _knowledge_args(kp)
    kp = ksub.add_parser("query", help="Search the detected sources")
    kp.add_argument("terms", nargs="+")
    kp.add_argument("--limit", type=int, default=10)
    _knowledge_args(kp)

    p = sub.add_parser("run", help="Interactive initialization in the terminal")
    _start_args(p)
    return parser


def run_interactive(orch: Orchestrator, args, input_fn: Callable[[str], str] = input,
                    out: Callable[[str], None] = print) -> Optional[dict]:
    status = orch.start(args.request, name=args.name, knowledge_paths=args.knowledge,
                        auto_detect=not args.no_auto_detect, knowledge_config=args.knowledge_config,
                        fields=_parse_fields(args.field))
    out(f"Project type: {status['project_type']} | clarity: {status['clarity']}/100")
    out("Commands: ':done' closes discovery, ':cancel' stops.")
    while True:
        state = status["state"]
        if state in ("bootstrap", "discovery"):
            question = status["next_question"]
            if question is None:
                status = orch.summary()
                continue
            out(f"\n[{question['field']}] {question['text']}")
            answer = input_fn("> ").strip()
            if answer == ":cancel":
                orch.cancel()
                out("Cancelled.")
                return None
            if answer == ":done" and state == "discovery":
                status = orch.summary()
                continue
            if not answer:
                continue
            try:
                status = orch.answer(question["field"], answer)
            except PifError as exc:
                out(str(exc))
            out(f"clarity: {status['clarity']}/100")
        elif state in ("validation", "prd_review"):
            document = SUMMARY_FILE if state == "validation" else PRD_FILE
            out("\n" + orch.ws.read(document))
            answer = input_fn(f"Approve {document}? [yes / no] > ").strip()
            if is_yes(answer):
                try:
                    status = orch.approve()
                except PifError as exc:
                    out(str(exc))
                continue
            if not is_no(answer):
                continue
            field = input_fn("Which field should change? > ").strip()
            value = input_fn("New value > ").strip()
            try:
                orch.reject(f"change {field}")
                status = orch.answer(field, value)
            except PifError as exc:
                out(str(exc))
                status = orch.status()
        elif state == "completed":
            out(f"\nInitialization completed. PRD: {status['artifacts'].get(PRD_FILE)}")
            out(report_to_markdown(build_report(orch.ws.load(), orch.ws.events())))
            return status
        else:
            out(f"Stopped in state '{state}'. {status.get('error') or ''}")
            return status


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    orch = Orchestrator(Workspace(args.dir), templates_dir=args.templates)
    try:
        command = args.command
        if command == "start":
            _print(orch.start(args.request, name=args.name, knowledge_paths=args.knowledge,
                              auto_detect=not args.no_auto_detect,
                              knowledge_config=args.knowledge_config,
                              fields=_parse_fields(args.field)))
        elif command == "status":
            _print(orch.status())
        elif command == "next":
            _print(orch.status().get("next_question"))
        elif command == "answer":
            _print(orch.answer(args.field, " ".join(args.value)))
        elif command == "summary":
            status = orch.summary()
            print(orch.ws.read(SUMMARY_FILE))
            _print({"state": status["state"], "next_action": status["next_action"]})
        elif command == "approve":
            _print(orch.approve())
        elif command == "reject":
            _print(orch.reject(args.reason))
        elif command == "cancel":
            _print(orch.cancel(args.reason))
        elif command == "resume":
            _print(orch.resume())
        elif command == "check-prd":
            path = args.file or str(orch.ws.path(PRD_FILE))
            with open(path, encoding="utf-8") as fh:
                issues = check_prd(fh.read())
            _print({"file": path, "passed": not issues, "issues": issues})
            return 0 if not issues else 3
        elif command == "metrics":
            report = build_report(orch.ws.load(), orch.ws.events())
            print(report_to_markdown(report)) if args.format == "md" else _print(report)
        elif command == "knowledge":
            connector, disabled = KnowledgeConnector.discover(
                explicit_paths=args.knowledge, config_path=args.knowledge_config,
                auto_detect=not args.no_auto_detect)
            if disabled:
                _print({"status": "disabled"})
            elif args.knowledge_command == "scan":
                _print({"status": "found" if connector.sources else "none", **connector.scan()})
            else:
                terms = extract_terms(" ".join(args.terms)) or args.terms
                _print([s.__dict__ for s in connector.query(terms, args.limit)])
        elif command == "run":
            run_interactive(orch, args)
        return 0
    except PifError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
