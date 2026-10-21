#!/usr/bin/env bash
set -euo pipefail

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "This directory is not a Git repository. Initialize or clone it first." >&2
  exit 1
fi

git config core.hooksPath .githooks
echo "This clone now runs Git hooks from .githooks/."
echo "Only this repository's local configuration changed."
