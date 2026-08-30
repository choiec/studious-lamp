#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
test -f "$REPO_ROOT/pyproject.toml"
test -f "$REPO_ROOT/uv.lock"
cd "$REPO_ROOT"
exec uv sync --locked --offline
