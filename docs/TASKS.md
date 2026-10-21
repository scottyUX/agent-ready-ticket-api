# Student tasks

Each task takes about 20–30 minutes. The base API is complete and passing without them. Implement one task at a time, and leave the others unchanged.

Every task needs behavioral tests for the success case and at least one failure case. Run `./scripts/validate.sh` before stopping.

Use the planner subagent before editing. Use `add-endpoint` for tasks 1–3 and `fix-bug` for task 4. Use the reviewer subagent on the finished diff.

## 1. Add ticket priority

Callers need to mark a ticket as `low`, `normal`, or `high`.

### Acceptance criteria

- A created ticket includes `priority`.
- Omitting `priority` stores `normal`, so existing create requests keep working.
- `low`, `normal`, and `high` are accepted.
- The list and get responses include the stored priority.
- `priority` value `urgent` returns HTTP 422 and `{"detail": "<message>"}`.
- The message names `priority` and does not include a traceback.

### Failure case

Create a ticket with `"priority": "urgent"` and assert HTTP 422.

### Stay inside the task

Do not add filtering, a close endpoint, or a status-transition rule.

## 2. Filter the ticket list by status

Callers need the list endpoint to return tickets of one status.

### Acceptance criteria

- `GET /tickets` still returns every ticket.
- `GET /tickets?status=open` returns only tickets whose status is `open`.
- The same query works for `in_progress` and `resolved`.
- A status that matches nothing returns HTTP 200 and `[]`.
- `GET /tickets?status=closed` returns HTTP 422 and `{"detail": "<message>"}`.

### Failure case

Request `GET /tickets?status=closed` and assert HTTP 422.

### Stay inside the task

Do not add priority, a close endpoint, or a status-transition rule.

## 3. Add a close-ticket endpoint

Callers need a single action that marks a ticket resolved.

### Acceptance criteria

- `POST /tickets/{ticket_id}/close` takes no body.
- For an existing ticket, the response is HTTP 200 and the ticket status is `resolved`.
- A second close of the same ticket returns HTTP 200 with status `resolved`.
- A missing ticket returns HTTP 404 and `{"detail": "Ticket not found."}`.
- Closing does not change the title or description.

### Failure case

Close ticket id `99` when it does not exist and assert HTTP 404 with the exact not-found body.

### Stay inside the task

Do not add a new status value, priority, or list filtering. Do not reject transitions away from `resolved`; that is task 4.

## 4. Reject invalid status transitions

### Current edge case

`PATCH /tickets/{ticket_id}` accepts any status in `open`, `in_progress`, and `resolved`. Reproduce the gap with the running API:

1. Create a ticket.
2. `PATCH` it to `resolved`.
3. `PATCH` it to `open`.

The third request currently returns HTTP 200, and the ticket is `open` again. A resolved ticket should stay resolved unless the caller sets `resolved` again.

### Acceptance criteria

- `open` to `in_progress`, `open` to `resolved`, and `in_progress` to `open` still return HTTP 200.
- `PATCH` of a resolved ticket to `resolved` returns HTTP 200.
- `PATCH` of a resolved ticket to `open` or `in_progress` returns HTTP 409 and `{"detail": "A resolved ticket cannot change status."}`.
- After a rejected change, `GET` shows the ticket is still `resolved`.
- Update the status invariant in `intent.md` so it matches this rule.

### Failure case

Resolve a ticket, patch it to `open`, and assert HTTP 409, the exact detail, and that the stored status is still `resolved`.

### Stay inside the task

Do not add priority, filtering, or a close endpoint. Fix the transition rule in the repository or the route. Leave unrelated refactors out.
