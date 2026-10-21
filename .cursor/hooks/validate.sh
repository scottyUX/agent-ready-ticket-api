#!/usr/bin/env bash
# Cursor stop hook. Rules and skills guide the agent. This script checks the
# result by delegating to scripts/validate.sh.

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
