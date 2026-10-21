# Product intent

## User problem

A lab assistant needs a small HTTP API that records support requests during a class session. Each request has a title, a description, and a status the assistant can move from open, to in progress, to resolved.

The API exists so students can practice changing a real, tested codebase. It is a teaching example. It is a complete application for that lesson, and it is intentionally small.

## Supported behavior

- Create a ticket. The API assigns an id and stores the ticket as `open`.
- List every ticket currently in memory.
- Retrieve one ticket by id.
- Change a ticket's status to `open`, `in_progress`, or `resolved`.
- Reject invalid request data with HTTP 422 and `{"detail": "<message>"}`.
- Reject a missing ticket with HTTP 404 and `{"detail": "Ticket not found."}`.

Titles and descriptions are required, trimmed, and limited in length. A blank value is invalid.

## Product principles

- The public HTTP behavior is the product. Callers depend on status codes and the `detail` error field.
- One module owns storage, one owns models, and one owns routes.
- A change that adds a behavior also adds a success test and a failure test.
- The repository stays understandable in about five minutes.

## Invariants

- New tickets start as `open`.
- Ids are positive integers assigned by the repository, in creation order.
- The response fields are `id`, `title`, `description`, and `status`.
- Unknown ticket ids return 404. Invalid bodies and path parameters return 422.
- Error responses use `{"detail": "<message>"}`.
- Storage is memory inside one process. Restarting the process clears every ticket.
- Tests start from an empty repository.
- Any of the three statuses may follow any of the three statuses. Restricting transitions is lab task 4, and it is not current behavior.

## Non-goals

The product does not include:

- Authentication
- Authorization
- Analytics
- Billing
- Persistent storage
- Notifications
- External integrations
- Multi-tenant behavior

A database, login form, metrics endpoint, or background worker can be implemented cleanly and still be the wrong change. Technical correctness is not enough when the change leaves this intent. Add a behavior when a task or a person asks for it, and leave the other lab tasks unimplemented.
