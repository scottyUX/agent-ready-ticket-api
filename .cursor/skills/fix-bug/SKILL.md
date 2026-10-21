---
name: fix-bug
description: Reproduce a ticket API defect, add a failing regression test, and apply the smallest root-cause fix. Use when a test fails, an endpoint returns the wrong status or body, or the user reports a bug.
---

# Fix a bug

Follow this order. Use it for task 4 in `docs/TASKS.md` and for any defect in the ticket API.

1. Reproduce the bug with the API or with a focused pytest command. Record the status code and body you observe.
2. Add a failing regression test that states the correct behavior. Put it in `tests/test_tickets.py` and cover the failure case from the report.
3. Run the new test and confirm it fails because of the bug:

   ```bash
   pytest tests/test_tickets.py::test_name
   ```

   Stop and correct the test when the failure is a typo, an import error, or an assertion that does not match the reported bug.
4. Identify the root cause in the route, model, or repository. Name the function that produces the wrong result.
5. Implement the smallest fix at that cause. Leave reformatting of unrelated code, new features, and the other lab tasks unchanged.
6. Re-run the regression test, then the neighboring ticket tests:

   ```bash
   pytest tests/test_tickets.py
   ```

7. Run complete validation:

   ```bash
   ./scripts/validate.sh
   ```

8. Report the result in this shape, with the command output that supports it:

   ```text
   Cause:
   Fix:
   Evidence:
   Remaining risk:
   ```

A green validation run is evidence that formatting, lint, and tests passed. It is not evidence that an untested behavior is fixed.
