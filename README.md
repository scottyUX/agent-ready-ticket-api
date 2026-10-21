# Agent-ready ticket API

The application is a small support-ticket API. The repository around it shows how an agent uses context, product intent, scoped rules, skills, subagents, a validation script, and hooks.

Repository: https://github.com/scottyUX/agent-ready-ticket-api

Open this directory as the project workspace. Agent configuration under `.cursor/` is discovered from the workspace root. Opening the parent folder hides these project files.

The base API is complete. The exercises in `docs/TASKS.md` are intentionally not implemented.

## Five-minute map

| Question | Look here |
| --- | --- |
| What does the API do? | `app/routes/tickets.py` and `tests/test_tickets.py` |
| What must the agent leave alone? | `intent.md` |
| Which constraints load with API files? | `.cursor/rules/` |
| Which procedure should an agent follow? | `.cursor/skills/` |
| What actually runs the checks? | `scripts/validate.sh` |
| What blocks a bad finish or a bad commit? | `.cursor/hooks.json` and `.githooks/pre-commit` |

## Requirements

- Python 3.12
- Git, for the hook exercise

## Installation

Clone the assignment, then install from that directory:

```bash
git clone https://github.com/scottyUX/agent-ready-ticket-api.git
cd agent-ready-ticket-api
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Running the API

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

Create, list, and miss a ticket:

```bash
curl -s -X POST http://127.0.0.1:8000/tickets \
  -H 'content-type: application/json' \
  -d '{"title":"Printer jam","description":"The lab printer is jammed."}'

curl -s http://127.0.0.1:8000/tickets

curl -s http://127.0.0.1:8000/tickets/99
```

Tickets live in process memory. Restarting the server clears them.

## Running tests

```bash
pytest
pytest tests/test_tickets.py
pytest tests/test_tickets.py::test_get_missing_ticket_returns_not_found
```

## Running complete validation

```bash
./scripts/validate.sh
```

That script is the definition of a finished change. It checks formatting with Ruff, lints with Ruff, and runs pytest. Hooks, skills, and docs call this script.

## Installing the Git hook

```bash
./scripts/install-hooks.sh
```

The script sets `core.hooksPath` to `.githooks` for this clone. It does not change global Git configuration. After that, a commit runs `./scripts/validate.sh` and stops when formatting, lint, or tests fail.

Another clone does not inherit the setting. Each person runs the installer once.

## Repository structure

```text
agent-ready-ticket-api/
├── AGENTS.md
├── intent.md
├── README.md
├── pyproject.toml
├── app/
│   ├── main.py
│   ├── models.py
│   ├── repository.py
│   └── routes/tickets.py
├── tests/test_tickets.py
├── docs/
│   ├── architecture.md
│   ├── TASKS.md
│   └── decisions/0001-in-memory-storage.md
├── .cursor/
│   ├── rules/
│   ├── skills/
│   ├── agents/
│   ├── hooks.json
│   └── hooks/validate.sh
├── scripts/
│   ├── validate.sh
│   └── install-hooks.sh
└── .githooks/pre-commit
```

## Files the agent uses

An agent does not load every markdown file. Open these in order during the walkthrough.

### `AGENTS.md`

`AGENTS.md` is plain agent instructions. It is the simple alternative to `.cursor/rules`: no frontmatter, no globs. Agents that follow the `AGENTS.md` convention discover it in the project root and in subdirectories. A nested file combines with the parent files, and the nearer file wins when they disagree. This repository has one root file. It maps the directories, lists the commands, and links to the other documents. The long procedures stay out of it.

### `intent.md`

`intent.md` is not a special agent filename. The agent leaves it alone until something asks it to open the file. In this repository, `AGENTS.md` puts it first in the reading order. It states the supported ticket behavior and the non-goals, including authentication and persistent storage. A change can pass the tests and still violate this file.

### Rules — `.cursor/rules/`

Project rules are `.mdc` files with `description`, `globs`, and `alwaysApply`. A plain `.md` file in this folder is ignored. Both rules here use `alwaysApply: false` and file globs, so they apply only to matching files. The rule is added to the agent prompt when a matching file is in context.

| File | Loads with |
| --- | --- |
| `.cursor/rules/api.mdc` | `app/routes/**/*.py`, `app/models.py` |
| `.cursor/rules/tests.mdc` | `tests/**/*.py` |

`api.mdc` requires Pydantic models, explicit responses, stable error bodies, and tests for the behavior you change. `tests.mdc` requires public-API tests, arrange/act/assert, and a storage reset. Opening `README.md` loads neither rule.

### Skills — `.cursor/skills/`

A skill is a folder with `SKILL.md`. The agent discovers `.cursor/skills/` from the project and reads each skill's `name` and `description`. It applies a skill when the description matches the request. You can also attach one for a single message with `/add-endpoint` or `/fix-bug`.

| Skill | Use it for |
| --- | --- |
| `.cursor/skills/add-endpoint/SKILL.md` | A new or changed endpoint, its models, and its tests |
| `.cursor/skills/fix-bug/SKILL.md` | A defect, including task 4 |

These skills leave out `disable-model-invocation`, so the agent may select them automatically. The body is the procedure: failing test, smallest change, then `./scripts/validate.sh`.

### Hooks — `.cursor/hooks.json`

Rules and skills are text the model may follow. A hook is a program the agent host runs. The model does not choose to call it.

`.cursor/hooks.json` registers one event, `stop`. The host calls it when an agent turn ends, before the conversation is allowed to stay finished.

1. The turn ends. The host starts `.cursor/hooks/validate.sh` and writes one JSON object to the script's stdin: `{"status": "completed" | "aborted" | "error", "loop_count": 0}`.
2. `completed` means the agent stopped on its own. `aborted` means the turn was cancelled. `error` means the turn failed. `loop_count` is how many times this hook has already sent a follow-up in the conversation.
3. For `aborted` or `error`, the script skips validation and prints `{}`. The host does not start another turn.
4. For `completed`, the script runs `./scripts/validate.sh`. It does not repeat the Ruff or pytest commands.
5. When validation passes, stdout is `{}` and the turn stays finished.
6. When validation fails, stdout is `{"followup_message": "..."}` and the exit code is `0`. The host treats that message as the next user message and starts another agent turn so the agent can fix the failure.
7. `loop_limit` in `hooks.json` is `2`. After two follow-ups, the host stops calling the hook again even if validation is still failing.

Git calls a different hook. `.githooks/pre-commit` runs when `git commit` starts, calls the same validation script, and a non-zero exit blocks the commit. Install it with `./scripts/install-hooks.sh`. That setting applies only to this clone.

`hooks.json` is JSON, so the explanation of each step lives in `.cursor/hooks/validate.sh`.

### `docs/`

`docs/` is ordinary markdown. The agent has no special loader for that directory. It opens a file here when `AGENTS.md`, a skill, or your prompt names that file.

| File | What to say in the walkthrough |
| --- | --- |
| `docs/architecture.md` | Request path, and which module owns validation, HTTP, and storage |
| `docs/decisions/0001-in-memory-storage.md` | Why tickets live in a dictionary, and when to revisit that choice |
| `docs/TASKS.md` | Four lab tasks. The base API is complete without them |

### Subagents — `.cursor/agents/`

`.cursor/agents/planner.md` and `.cursor/agents/reviewer.md` are custom subagents. Each has its own context. Both set `readonly: true`, so they return a report and do not edit files. Invoke them with `/planner` and `/reviewer`.

| Component | What it does in this repo |
| --- | --- |
| `AGENTS.md` | Orientation an agent discovers from the project root |
| `intent.md` | Product boundary the agent reads because `AGENTS.md` points to it |
| `.cursor/rules/` | Instructions injected only for matching files |
| `.cursor/skills/` | Procedures the agent can select or you can invoke with `/` |
| `.cursor/hooks.json` | Script that runs after an agent turn |
| `docs/` | Reference the agent opens only when a task names it |
| `.cursor/agents/` | Separate planning and review passes |

```text
Observed behavior                       Repository component
Agent finds the correct commands        AGENTS.md
Agent avoids out-of-scope features      intent.md
API constraints load with API files     Scoped rule
Agent follows a test-first procedure    Skill
Invalid completion is blocked           Hook
Implementation receives fresh review    Reviewer subagent
```

## Using the skills

Skills are procedures. Invoke one by naming it:

```text
Use the add-endpoint skill to add ticket priority from docs/TASKS.md task 1.
Use the fix-bug skill for the resolved-ticket transition in docs/TASKS.md task 4.
```

The agent can also select a skill when the request matches its description. Tasks 1–3 match `add-endpoint`. Task 4 matches `fix-bug`.

The skill tells the agent to write a failing behavioral test, confirm the failure, make the smallest change, and run `./scripts/validate.sh`.

## Using the planner and reviewer

Both subagents are read-only. They return a report and leave the files unchanged.

Ask for a plan before editing:

```text
/planner Plan task 2 from docs/TASKS.md.
```

Ask for a review after the tests pass:

```text
/reviewer Review the current diff against task 2. Do not edit files.
```

You can also write "Use the planner subagent" or "Use the reviewer subagent". The reviewer must cite evidence and can return `REVISE`. A polite summary is not an approval.

The planner's report looks like this:

```text
Goal:
Expected behavior:
Affected files:
Implementation plan:
Tests:
Risks:
Validation:
```

The reviewer's report looks like this:

```text
Decision: ACCEPT | REVISE

Requirements checked:
Validation:
Findings:
Required changes:
Residual risks:
```

## Instructor Walkthrough

Keep the base application passing. Demonstrate one student task. Leave the implementation for the students.

### 1. Application code

Show `app/models.py`, `app/repository.py`, `app/routes/tickets.py`, and `app/main.py` in that order. Create a ticket in `/docs` or with curl, then restart the server and show that the ticket is gone.

The application is the behavior the other files protect. Students need to see a real request path before they see the agent files.

Question: Which file should change if a new request field needs a length limit, and which file should change if a missing ticket should stay a 404?

### 2. Tests

Show `test_create_ticket_returns_open_ticket`, `test_get_missing_ticket_returns_not_found`, and the `reset_ticket_storage` fixture. Run `pytest tests/test_tickets.py::test_create_ticket_returns_open_ticket` and then the whole file.

Tests state the HTTP contract and put the shared memory back to empty. Two tests can both expect the first id to be `1` because of that reset.

Question: What would two tests that both expect id `1` start doing if the reset fixture disappeared?

### 3. `AGENTS.md`

Show the directory map, the command block, the invariants, and the "ask a person" list. Point at the links instead of reading every procedure into this file.

This is the onboarding page an agent discovers for an unfamiliar repository. It answers where to go and which command to run.

Question: Where does the nine-step endpoint procedure live, and why is it absent from this page?

### 4. `intent.md`

Show the supported behavior and the non-goals. Read the closing paragraph about a change that passes tests and still violates the product.

Product intent is the boundary. It tells the agent which working features are still the wrong work.

Question: The tests pass after an agent adds SQLite. Which document says that change is still out of scope?

### 5. Rules

Open `.cursor/rules/api.mdc` and `.cursor/rules/tests.mdc`. Show `alwaysApply: false` and the `globs`. Open a route file and a test file and show which rule attaches. Then open `README.md` and show that neither rule is required there.

A scoped rule travels with the files it governs. The API rule stays out of an edit that never touches the API.

Question: What would go wrong in a documentation edit if the API rule used `alwaysApply: true`?

### 6. Skills

Open `.cursor/skills/add-endpoint/SKILL.md`. Walk steps 4 through 8: failing test, confirm the failure, smallest change, targeted pytest, then `./scripts/validate.sh`.

A skill is a procedure the agent can repeat. The rule says what "good" looks like. The skill says what to do next.

Question: Which skill fits task 4, and which skill fits adding the close endpoint?

### 7. Validation script

Open `scripts/validate.sh` and run it. Show that the hook scripts and the skills call this file.

One script keeps formatting, lint, and tests from drifting into slightly different commands in every doc.

Question: Why do the skill and both hooks call this file instead of listing `ruff` and `pytest` themselves?

### 8. Git and agent hooks

Show `.githooks/pre-commit`, `scripts/install-hooks.sh`, `.cursor/hooks.json`, and the comments in `.cursor/hooks/validate.sh`. Point at `loop_limit` and at the hook printing `{}` or `followup_message`. Run `./scripts/install-hooks.sh` and say that it changes this clone only.

Rules and skills advise the model. The pre-commit hook refuses a commit when validation fails. The `stop` hook runs the same script after an agent turn and can send the failure back for another turn. `loop_limit` is `2`, so a failure that will not go green cannot loop forever.

Question: Why does the agent hook delegate to `scripts/validate.sh` instead of running `pytest` itself?

### 9. Planner subagent

Open `.cursor/agents/planner.md`. Show `readonly: true` and the output headings. If time allows, run `/planner` on task 1 and show that the files did not change.

Planning happens in a fresh context and ends in a plan. The implementation conversation stays shorter because the search notes stay in the subagent.

Question: What should a student do with the planner's output before any file is edited?

### 10. Reviewer subagent

Open `.cursor/agents/reviewer.md`. Show the decision line and the instruction that a missing test or a missed validation run is `REVISE`.

The reviewer sees the diff without having written it. Approval depends on evidence from the task, the tests, and `./scripts/validate.sh`.

Question: The diff looks tidy and the author says the tests passed, but the review contains no command output. Which decision should the reviewer return?

### 11. One example student task

Open task 4 in `docs/TASKS.md`. Reproduce the current behavior: create a ticket, patch it to `resolved`, then patch it to `open`, and show the HTTP 200. Show the comment on `TicketRepository.update_status`. Leave the fix for the students, or pair on the first failing test if the hour allows.

The tasks are the lab. The shipped API is done without them, which keeps the walkthrough on a green test suite.

Question: Which skill starts task 4, and which command has to pass before the student stops?

## Troubleshooting

**`python3.12` is missing.** Install Python 3.12 and create the virtual environment again. The project declares `requires-python = ">=3.12"`.

**`ruff` or `pytest` is not found.** Activate `.venv`. `scripts/validate.sh` prepends `.venv/bin` to `PATH` when that directory exists, which is what the hooks rely on.

**Rules, skills, or subagents do not appear.** Open `agent-ready-ticket-api` itself as the workspace, then reload the window if `.cursor/hooks.json` was just added.

**The stop hook never runs.** Confirm project hooks are enabled. After a completed agent turn, the hook log should show `stop hook: validation passed`. The script also runs from the terminal:

```bash
printf '%s' '{"status":"completed","loop_count":0}' | .cursor/hooks/validate.sh
```

A passing tree prints `{}`. Status `aborted` skips validation and still prints `{}`.

**The Git hook never runs.** Run `./scripts/install-hooks.sh` inside this clone. Check `git config --show-origin core.hooksPath` and confirm the origin is this repository's `.git/config`. `--no-verify` skips the hook on purpose. The lab should let the hook fail visibly instead.

**A commit is rejected.** Read the `ruff` or `pytest` output. Fix the code and commit again. Leave `scripts/validate.sh` in place.

**Validation fails twice and the agent stops anyway.** `loop_limit` is `2`. That cap is the point: a stuck failure must not create an infinite agent loop. Fix the failure by hand or start a new request.

## Before class

Confirm the agent loads the files in `.cursor/`:

- Project rules are `.mdc` files with `description`, `globs`, and `alwaysApply: false`.
- Skills live at `.cursor/skills/<name>/SKILL.md` and can be named in the prompt.
- Subagents live at `.cursor/agents/<name>.md`. Invoke them with `/planner` and `/reviewer`. Their `model` value is the unquoted word `inherit`.
- The hook file uses schema version 1. The `stop` hook may return `{"followup_message": "..."}` and honors `loop_limit`.

Spend one minute in a scratch chat to see a scoped rule attach, `/planner` return the plan format, and the hook log print `stop hook: validation passed`.
