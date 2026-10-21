---
name: add-endpoint
description: Use when adding or changing a FastAPI endpoint, its request or response models, or its behavioral tests.
---

# Add or change an endpoint

Follow this order. The API rule and the test rule still apply to the files you edit.

1. Read `AGENTS.md`, `intent.md`, `docs/architecture.md`, and the relevant task in `docs/TASKS.md`.
2. Inspect the related route, models, repository code, and tests.
3. State the expected behavior and the files you expect to change. Keep the change inside the requested task.
4. Add or update a failing behavioral test in `tests/test_tickets.py`. Include a success case and a failure case.
5. Run that test and confirm it fails for the expected reason:

   ```bash
   pytest tests/test_tickets.py::test_name
   ```

   A collection error or an unexpected status code means the test is not ready. Fix the test before changing application code.
6. Implement the smallest application change that satisfies the behavior. Put fields in `app/models.py`, storage in `app/repository.py`, and HTTP behavior in `app/routes/tickets.py`.
7. Re-run the targeted test while iterating. Add neighboring tests from the same file when the change could affect them.
8. Run complete validation:

   ```bash
   ./scripts/validate.sh
   ```

   When it fails, fix the reported formatting, lint, or test failure and run the script again.
9. Summarize the work in this shape:

   ```text
   Behavior:
   Files:
   Tests:
   Validation:
   Remaining risk:
   ```

Leave authentication, persistence, and the other lab tasks out of the change unless that task is the one you were given.
