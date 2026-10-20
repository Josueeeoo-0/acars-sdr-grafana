#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$project_root/data/acars"
exec docker compose --project-directory "$project_root" \
  --file "$project_root/config/compose.yaml" "$@"
