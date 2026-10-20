#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
if ! command -v acarsdec >/dev/null 2>&1; then
  echo "No se encuentra acarsdec en esta terminal." >&2
  exit 1
fi
mkdir -p data/acars
exec acarsdec --rtlsdr "${RTL_DEVICE:-0}" \
  -i "${STATION_ID:-$(hostname)}" -g "${RTL_GAIN:-28}" \
  --statsd "host=${STATSD_HOST:-127.0.0.1},port=${STATSD_PORT:-8125}" \
  --output full:file \
  --output "json:file:path=$PWD/data/acars/acars.jsonl,rotate=daily" \
  "${ACARS_FREQ:-131.725}"
