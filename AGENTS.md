# AGENTS.md - Project Initialization Framework

Instructions for AI agents (Claude Code, Codex, Cursor, GPT, Gemini or any other).
Human documentation lives in `README.md` and `docs/` (in Spanish).

## When to use this framework

Use it whenever the user asks to start, initialize, define or plan a **new** project,
or when execution is about to begin without a validated definition.
Do not use it for small, well-defined tasks.

Its job ends with an **approved PRD**. Planning and execution happen afterwards,
in whatever layer receives the handoff.

## Language

- These instructions, the modules and the templates are in English.
- Talk to the user in the user's language. Translate questions as you ask them.
- Write the summary and the PRD content in the user's language unless they ask otherwise.
  Keep section headings as in the templates so the quality gate can check them.

## How to coordinate the agents

The framework is a set of roles. Each role is a module file:

| Role | File | Talks to the user |
| --- | --- | --- |
| Project Orchestrator | `modules/project-orchestrator.md` | Yes (approvals) |
| Project Bootstrapper | `modules/project-bootstrapper.md` | No |
| Knowledge Connector | `modules/knowledge-connector.md` | Only the survey question |
| Discovery Engine | `modules/discovery-engine.md` | Yes (interview, summary) |

Delegation chain (control always returns to the caller):

```text
Orchestrator -> Bootstrapper -> Knowledge Connector -> Bootstrapper
             -> Bootstrapper -> Discovery Engine    -> Bootstrapper -> Orchestrator
```

Coordination rules:

1. **You are the Orchestrator.** Start by reading `modules/project-orchestrator.md`.
2. **One active role at a time.** Load a module file only when you enter that role
   (context efficiency). Leave the role when its step returns.
3. **Only the Orchestrator changes the state.** Other roles return results.
4. **Do not send the interview to a background subagent.** The Discovery Engine needs a
   live conversation with the user, so run it in the main conversation.
5. **Read-only work may be delegated.** If your host supports subagents, a subagent
   can run the Knowledge Connector scan and return a compact report (sources,
   resources, relevant excerpts). It must not write anything.
6. **Never skip validation**, never assume missing information, never continue
   after a rejection without recording the change.

## Protocol

Preferred: drive the reference implementation (Python 3.9+, standard library only).
It enforces the state machine, measures uncertainty and logs metrics.
Run the commands from the root of this repository (or after `pip install -e .`, use `pif`).
Keep the workspace in the user's project: `--dir <project>/.pif`.

```bash
# 1. Bootstrap. Pass every value already explicit in the request with --field.
python -m pif --dir .pif start "<user request>" \
  [--field deliverables="..."] [--field success_criteria="..."] [--knowledge <path>]

# 2. Loop: read next_question, ask it (in the user's language), record the answer.
python -m pif --dir .pif status
python -m pif --dir .pif answer <field> "<answer>"

# 3. Validation: show .pif/executive-summary.md to the user.
python -m pif --dir .pif approve                 # approved
python -m pif --dir .pif answer <field> "<new>"  # change one value (summary is rebuilt)
python -m pif --dir .pif reject --reason "..."   # rejected

# 4. PRD review: show .pif/PRD.md, then approve (or reject + answer).
python -m pif --dir .pif approve

# 5. Report.
python -m pif --dir .pif metrics --format md
```

Every command prints JSON with `state`, `clarity`, `next_question` and `next_action`.
Follow `next_action`. Exit code 2 means a framework rule blocked the action:
read the `error` message, fix the cause, do not force it.

Useful extras:

- `python -m pif --dir .pif summary`: close discovery early (user wants to stop).
- `python -m pif --dir .pif resume`: continue after an error from the last valid state.
- `python -m pif check-prd <file>`: run the PRD quality gate on any PRD.
- `python -m pif knowledge scan` / `knowledge query <terms>`: inspect knowledge sources.

Without Python, follow the same steps by hand: keep `.pif/state.json` with the shape of
`templates/project-state.schema.json`, apply the scoring table in
`modules/discovery-engine.md` and fill the templates in `templates/`.

## Hard rules

- Never execute or plan the project before the PRD is approved.
- Ask one question at a time. Stop asking as soon as discovery is done.
- Success criteria must be measurable (a number, a percentage or a date).
- Never write into the user's knowledge base. If none exists, do not mention it again.
- Never copy secrets or personal data from notes into project artifacts.
- Everything not answered goes to Open Questions. Nothing is invented.

## Files

| Path | Purpose |
| --- | --- |
| `modules/` | Role instructions (English) |
| `templates/prd.template.md` | PRD structure checked by the quality gate |
| `templates/executive-summary.template.md` | Summary shown for validation |
| `templates/project-state.schema.json` | State file format |
| `templates/knowledge.config.example.json` | Knowledge Connector config example |
| `pif/` | Reference implementation (CLI `python -m pif`) |
| `examples/` | Worked examples and a sample knowledge base |
