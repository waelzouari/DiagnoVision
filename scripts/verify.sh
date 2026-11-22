#!/bin/sh
set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

cd "$repo_dir/backend"
ruff check .
pytest

cd "$repo_dir/frontend"
npm run lint
npm run typecheck
npm run test -- --run
npm run build

cd "$repo_dir"
docker compose config --quiet

