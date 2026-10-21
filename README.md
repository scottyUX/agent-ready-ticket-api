# Agent-ready ticket API

A one-hour university lab. The application is a small support-ticket API. The repository around it shows how Cursor uses context, product intent, scoped rules, skills, subagents, a validation script, and hooks.

Open this directory as the Cursor workspace. Cursor discovers `.cursor/` from the workspace root. Opening the parent folder hides these project files from the IDE.

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

From this directory:

```bash
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

## Agent-readiness components

Each artifact has one job. The long procedures stay in the skills. The orientation stays in `AGENTS.md`.

| Component | What it does in this repo |
| --- | --- |
| Context (`AGENTS.md`) | Tells an unfamiliar agent where things are and which commands to run |
| Product intent (`intent.md`) | Defines the supported behavior and the non-goals |
| Scoped rules (`.cursor/rules/*.mdc`) | Load only when a matching file is in context |
| Skills (`.cursor/skills/*/SKILL.md`) | Give a repeatable procedure for adding an endpoint or fixing a bug |
| Subagents (`.cursor/agents/*.md`) | Plan or review in a separate context that does not edit files |
| Validation script (`scripts/validate.sh`) | Runs the same format, lint, and test commands every time |
| Hooks | Run that script on commit and after an agent turn |

Written guidance can be ignored by a model. A hook runs a program. Use a rule or a skill when the goal is to shape a change. Use a hook when the goal is to execute a check.

```text
Observed behavior                       Repository component
Agent finds the correct commands        AGENTS.md
Agent avoids out-of-scope features      intent.md
API constraints load with API files     Scoped Cursor rule
Agent follows a test-first procedure    Skill
Invalid completion is blocked           Hook
Implementation receives fresh review    Reviewer subagent
```

## Using the Cursor skills

Skills are procedures. Invoke one by naming it:

```text
Use the add-endpoint skill to add ticket priority from docs/TASKS.md task 1.
Use the fix-bug skill for the resolved-ticket transition in docs/TASKS.md task 4.
```

Cursor can also select a skill when the request matches its description. Tasks 1–3 match `add-endpoint`. Task 4 matches `fix-bug`.

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

This is the onboarding page Cursor discovers for an unfamiliar agent. It answers where to go and which command to run.

Question: Where does the nine-step endpoint procedure live, and why is it absent from this page?

### 4. `intent.md`

Show the supported behavior and the non-goals. Read the closing paragraph about a change that passes tests and still violates the product.

Product intent is the boundary. It tells the agent which working features are still the wrong work.

Question: The tests pass after an agent adds SQLite. Which document says that change is still out of scope?

### 5. Cursor rules

Open `.cursor/rules/api.mdc` and `.cursor/rules/tests.mdc`. Show `alwaysApply: false` and the `globs`. Open a route file and a test file and show which rule attaches. Then open `README.md` and show that neither rule is required there.

A scoped rule travels with the files it governs. The API rule stays out of an edit that never touches the API.

Question: What would go wrong in a documentation edit if the API rule used `alwaysApply: true`?

### 6. Cursor skills

Open `.cursor/skills/add-endpoint/SKILL.md`. Walk steps 4 through 8: failing test, confirm the failure, smallest change, targeted pytest, then `./scripts/validate.sh`.

A skill is a procedure the agent can repeat. The rule says what "good" looks like. The skill says what to do next.

Question: Which skill fits task 4, and which skill fits adding the close endpoint?

### 7. Validation script

Open `scripts/validate.sh` and run it. Show that the hook scripts and the skills call this file.

One script keeps formatting, lint, and tests from drifting into slightly different commands in every doc.

Question: Why do the skill and both hooks call this file instead of listing `ruff` and `pytest` themselves?

### 8. Git and Cursor hooks

Show `.githooks/pre-commit`, `scripts/install-hooks.sh`, `.cursor/hooks.json`, and `.cursor/hooks/validate.sh`. Point at `loop_limit` and at the hook printing `{}` or `followup_message`. Run `./scripts/install-hooks.sh` and say that it changes this clone only.

Rules and skills advise the model. The pre-commit hook refuses a commit when validation fails. The Cursor `stop` hook runs the same script after an agent turn and can send the failure back for another turn. `loop_limit` is `2`, so a failure that will not go green cannot loop forever.

Question: Why does the Cursor hook delegate to `scripts/validate.sh` instead of running `pytest` itself?

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

**Cursor does not show the rules, skills, or subagents.** Open `agent-ready-ticket-api` itself as the workspace, then restart Cursor if `.cursor/hooks.json` was just added.

**The stop hook never runs.** In Cursor settings, confirm project hooks are enabled. The Hooks output channel should show `stop hook: validation passed` after an agent turn. The script also runs from the terminal:

```bash
printf '%s' '{"status":"completed","loop_count":0}' | .cursor/hooks/validate.sh
```

A passing tree prints `{}`. Status `aborted` skips validation and still prints `{}`.

**The Git hook never runs.** Run `./scripts/install-hooks.sh` inside this clone. Check `git config --show-origin core.hooksPath` and confirm the origin is this repository's `.git/config`. `--no-verify` skips the hook on purpose. The lab should let the hook fail visibly instead.

**A commit is rejected.** Read the `ruff` or `pytest` output. Fix the code and commit again. Leave `scripts/validate.sh` in place.

**Validation fails twice and the agent stops anyway.** `loop_limit` is `2`. That cap is the point: a stuck failure must not create an infinite agent loop. Fix the failure by hand or start a new request.

## Before class

Confirm this Cursor build against the files in `.cursor/`:

- Project rules are `.mdc` files with `description`, `globs`, and `alwaysApply: false`.
- Skills live at `.cursor/skills/<name>/SKILL.md` and can be named in the prompt.
- Subagents live at `.cursor/agents/<name>.md`. Invoke them with `/planner` and `/reviewer`. Their `model` value is the unquoted word `inherit`.
- Hooks use schema version 1. The `stop` hook may return `{"followup_message": "..."}` and honors `loop_limit`.

Spend one minute in a scratch chat to see a scoped rule attach, `/planner` return the plan format, and the Hooks channel print `stop hook: validation passed`.
