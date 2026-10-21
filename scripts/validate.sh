#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ -d .venv/bin ]]; then
  export PATH=".venv/bin:${PATH}"
fi

ruff format --check .
ruff check .
pytest
