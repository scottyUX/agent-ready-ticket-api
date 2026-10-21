#!/usr/bin/env bash
# Stop hook for the agent host.
#
# The model does not call this script. The host runs it when an agent turn
# ends, because .cursor/hooks.json registers it on the "stop" event.
#
# The host writes one JSON object to stdin:
#   {"status": "completed" | "aborted" | "error", "loop_count": <number>}
#
# This script writes one JSON object to stdout and always exits 0.
# A non-zero exit means the hook itself crashed, not that validation failed.
#
#   status "aborted" or "error"
#     The turn did not finish normally. Print {} and do not run validation.
#
#   status "completed" and scripts/validate.sh passes
#     The agent stopped and the tree is valid. Print {}. The host ends the turn.
#
#   status "completed" and scripts/validate.sh fails
#     Print {"followup_message": "..."}. The host submits that text as the
#     next user message, which starts another agent turn.
#
# hooks.json sets "loop_limit": 2. After two follow-ups the host stops
# invoking this script, even if validation is still failing.
#
# The commands live in scripts/validate.sh. This file only decides whether
# to run that script and how to report the result.

set -uo pipefail

input=$(cat || true)
status=$(
  printf '%s' "$input" | python3 -c 'import json, sys
try:
    payload = json.load(sys.stdin)
except Exception:
    payload = {}
print(payload.get("status", "completed"))
' 2>/dev/null || printf '%s' "completed"
)

if [[ "$status" != "completed" ]]; then
  echo "stop hook: skipped because status is ${status}" >&2
  printf '%s\n' "{}"
  exit 0
fi

cd "$(dirname "$0")/../.."

if output=$(./scripts/validate.sh 2>&1); then
  echo "stop hook: validation passed" >&2
  printf '%s\n' "{}"
  exit 0
fi

echo "stop hook: validation failed" >&2
printf '%s' "$output" | python3 -c 'import json, sys
text = sys.stdin.read()[-4000:]
message = (
    "scripts/validate.sh failed. Fix the formatting, lint, or test failure below. "
    "Do not weaken scripts/validate.sh.\n\n"
    + text
)
print(json.dumps({"followup_message": message}))
'
exit 0
