---
id: knowledge-connector
name: Knowledge Connector
version: 2.1.0
type: connector
status: stable
description: >
  Connects, read-only, to a knowledge system the user already has on this
  machine (second brain, notes vault, graph database, system prompts, skills,
  workflows). If none exists, it is ignored completely. It never creates one.
invoked_by:
  - project-bootstrapper
delegates_to: []
inputs:
  - Optional paths or config given by the user
  - Project terms (objective, deliverables, project type) for selection
outputs:
  - Knowledge status
  - Inventory of available resources
  - Proposed resources with reasons
  - Relevant notes (short excerpts with their paths)
---

# Knowledge Connector

## Purpose

Many users already keep their knowledge in one place: a second brain, an
Obsidian vault, a graph database, a folder with system prompts, skills and workflows.
When it exists, use it so the project starts from what the user already knows and
from how the user already works. When it does not exist, ignore this module completely.

You never build a new knowledge base, never write into an existing one and never
copy it into the project.

## Detection order

Stop at the first step that finds something. Steps 1-3 are trusted, step 4 needs consent.

1. **Explicit**: paths the user gave (`--knowledge PATH` or the answer to the survey question).
2. **Config**: `./pif.knowledge.json` or `~/.config/pif/knowledge.json`
   (see `templates/knowledge.config.example.json`).
3. **Environment**: `PIF_KNOWLEDGE_PATH` (paths separated by `:` on Unix, `;` on Windows).
4. **Auto-detection**: these folders under the home directory, only if they look
   like a knowledge base (an index file, `.obsidian/`, `CLAUDE.md`/`AGENTS.md`, or
   folders such as `skills/`, `system-prompts/`, `workflows/`, `knowledge/`):
   `~/.claude`, `~/brain`, `~/Brain`, `~/second-brain`, `~/SecondBrain`, `~/knowledge`,
   `~/Knowledge`, `~/notes`, `~/Obsidian`, `~/Documents/brain`, `~/Documents/Obsidian`.

`PIF_KNOWLEDGE=off` or `"enabled": false` in the config disables the connector.
If you are an AI agent with your own memory or knowledge tools (an MCP server for a
graph, a notes connector), treat them as an additional source and apply the same rules.

## Survey question (asked once, during bootstrap)

- Sources found by auto-detection:
  "I found these knowledge sources on this machine: {list}. May I consult them
  read-only for this project? (yes/no)"
- Nothing found:
  "Do you already have a knowledge base I should consult for this project (a second
  brain, a notes vault, a graph database, a folder with system prompts or skills)?
  Give its path, or answer 'no'."

If the answer is "no", set the status to `none` (or `declined`) and never mention
knowledge sources again in this initialization.

## Supported sources

| Type | What it is | How to read it |
| --- | --- | --- |
| `markdown` | Folder of notes: second brain, Obsidian vault, `~/.claude` | Read the index first (`INDEX.md`, `index.md`, `README.md`). Then list categories. Open individual notes only when relevant. |
| `json-graph` | JSON file with `nodes` and `edges` (or `links`) | Search node labels, text and tags; include the labels of neighbour nodes. |
| `neo4j` | Neo4j database over its HTTP API | Read-only Cypher queries with credentials from environment variables. |

## What to extract

| Resource kind | Recognised by | Use |
| --- | --- | --- |
| `system_prompt` | `CLAUDE.md`, `AGENTS.md`, `SYSTEM.md` at the root; `system-prompts/`, `prompts/` | Global working instructions: always proposed. |
| `skill` | `skills/<name>/SKILL.md` | Ways of working the user already uses. |
| `workflow` | `workflows/` | Step-by-step processes to reuse. |
| `agent` | `agents/` | Existing agent definitions. |
| `template`, `reference`, `script`, `plugin`, `command` | Folders with those names | Reusable material. |
| `knowledge` | `knowledge/`, `notes/`, `wiki/`, graph nodes of that type | Facts and decisions about the domain. |

## Selection

Before the executive summary, match the project terms (objective, problem,
deliverables, project type) against each resource name and description.
Propose only the resources that match, plus the global working instructions.
Present them as a table:

| Resource | Type | Reason | Priority | Status |
| --- | --- | --- | --- | --- |

Status starts as `proposed`. It becomes `approved` when the user approves the summary.
Also attach up to five relevant notes as short excerpts with their paths.

## Rules

- Read-only. Never write, move or delete anything in a knowledge source.
- Context efficiency: index first, inventory second, individual notes only when needed.
  Scan at most 2,000 files and read at most the first 4 KB of each.
- Quote short excerpts with their path. Never copy whole notes into project artifacts.
- Never copy credentials, tokens or personal data found in notes.
- An unreachable source is skipped silently; it never blocks the initialization.
- Knowledge informs questions and the PRD; it never replaces the user's approval.
  A value found in the knowledge base is proposed to the user, not assumed.

## Return

Return the status, the sources, the proposed resources and the relevant notes to
the Project Bootstrapper. Then stop.

## Tooling

`python -m pif knowledge scan [--knowledge PATH]` lists sources and resources.
`python -m pif knowledge query TERMS... [--knowledge PATH]` searches them.
