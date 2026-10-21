# Agent guide

This repository is a one-hour lab. It shows how repository context, product intent, scoped rules, skills, subagents, a validation script, and hooks work together. The application is a small in-memory support-ticket API.

## Stack

- Python 3.12
- FastAPI
- Pydantic
- pytest
- Ruff
- In-memory storage

## Directory map

| Path | Responsibility |
| --- | --- |
| `app/main.py` | Create the FastAPI application |
| `app/models.py` | Request, response, and domain models |
| `app/repository.py` | In-memory ticket storage |
| `app/routes/tickets.py` | HTTP behavior |
| `tests/test_tickets.py` | Behavioral API tests |
| `docs/` | Architecture, decisions, and lab tasks |
| `.cursor/rules/` | File-scoped constraints |
| `.cursor/skills/` | Repeatable procedures |
| `.cursor/agents/` | Planner and reviewer subagents |
| `.cursor/hooks.json` | Deterministic check after an agent turn |
| `scripts/validate.sh` | Single validation entry point |

## Read first

1. [intent.md](intent.md)
2. [docs/architecture.md](docs/architecture.md)
3. [docs/decisions/0001-in-memory-storage.md](docs/decisions/0001-in-memory-storage.md)
4. `app/models.py`, `app/repository.py`, `app/routes/tickets.py`, `app/main.py`
5. `tests/test_tickets.py`
6. The assigned task in [docs/TASKS.md](docs/TASKS.md)

Endpoint and bug-fix procedures live in skills:

- [.cursor/skills/add-endpoint/SKILL.md](.cursor/skills/add-endpoint/SKILL.md)
- [.cursor/skills/fix-bug/SKILL.md](.cursor/skills/fix-bug/SKILL.md)

File-scoped constraints:

- [.cursor/rules/api.mdc](.cursor/rules/api.mdc)
- [.cursor/rules/tests.mdc](.cursor/rules/tests.mdc)

Planning and review:

- [.cursor/agents/planner.md](.cursor/agents/planner.md)
- [.cursor/agents/reviewer.md](.cursor/agents/reviewer.md)

## Commands

Run these from the repository root with the virtual environment active.

Install:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Run the API:

```bash
uvicorn app.main:app --reload
```

Targeted tests:

```bash
pytest tests/test_tickets.py
```

Complete validation:

```bash
./scripts/validate.sh
```

Install the local Git hook:

```bash
./scripts/install-hooks.sh
```

## Change workflow

1. Read the task, `intent.md`, and `docs/architecture.md`.
2. Ask the planner subagent for an implementation plan before a multi-file change.
3. Follow the `add-endpoint` or `fix-bug` skill for the procedure.
4. Run the targeted pytest command while iterating.
5. Run `./scripts/validate.sh` before stopping.
6. Ask the reviewer subagent to review the diff.

## Invariants

- A new ticket has status `open` and a positive integer id.
- Stored fields are `id`, `title`, `description`, and `status`.
- Status values are `open`, `in_progress`, and `resolved`.
- A missing ticket returns HTTP 404 and `{"detail": "Ticket not found."}`.
- Invalid input returns HTTP 422 and `{"detail": "<message>"}`.
- Error bodies contain a message. They do not contain tracebacks or exception class names.
- Ticket data lives in process memory and disappears when the process stops.
- Tests call `ticket_repository.reset()` before each test.
- The base API accepts any valid status after any other valid status. Task 4 in `docs/TASKS.md` is the exercise that adds a transition rule.

## Safe commands

- `./scripts/validate.sh`
- `pytest` and `pytest tests/test_tickets.py`
- `ruff format --check .`
- `ruff check .`
- `uvicorn app.main:app --reload`

## Ask a person before

- Adding authentication, persistence, notifications, or any other non-goal in `intent.md`
- Changing `scripts/validate.sh` so a failing check is skipped
- Adding a dependency
- Pushing, force-pushing, or rewriting Git history
- Editing product non-goals

## Leave these files as delegators

- `.cursor/hooks/validate.sh` calls `scripts/validate.sh`. When the checks themselves should change, edit `scripts/validate.sh`.
- `.githooks/pre-commit` calls `scripts/validate.sh`. Keep that delegation.

## Written guidance and executed checks

`AGENTS.md`, `intent.md`, rules, and skills tell the agent what to do. `scripts/validate.sh`, the Git pre-commit hook, and the Cursor stop hook run the checks.
