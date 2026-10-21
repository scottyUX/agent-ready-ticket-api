# 0001. Store tickets in memory

## Context

This repository is a one-hour lab about agent-ready project structure. Students need a working API with create, read, list, and status-update behavior, plus tests that can return the process to a known state.

A database would add a service, credentials, and migrations. Those topics are outside the lesson.

## Decision

`TicketRepository` stores tickets in a process-local dictionary. The module exposes one `ticket_repository` instance. Tests call `reset()` before every test. Stopping the process discards the data.

## Benefits

- The application runs after a virtual environment install. No database server is required.
- Storage code fits on one screen, so the walkthrough can reach rules, skills, and hooks.
- `reset()` gives tests an explicit, reliable starting state.
- The repository boundary is still visible: routes ask the repository for tickets, and tests do not poke the dictionary.

## Consequences

- Tickets disappear on restart and are not shared across processes.
- The singleton is shared by every request in the process. Tests must reset it.
- Concurrent writes are outside the lab's guarantees.

## Revisit this decision when

- Tickets must survive a process restart.
- More than one process must share the same tickets.
- The course moves from repository structure to persistence, transactions, or deployment.

Until then, adding a database is a product-intent violation even if the HTTP tests still pass.
