#!/bin/sh
set -eu

url=${1:?usage: wait-for-http.sh URL [timeout-seconds]}
timeout=${2:-120}
elapsed=0

while [ "$elapsed" -lt "$timeout" ]; do
  if curl --fail --silent --show-error --max-time 3 "$url" >/dev/null 2>&1; then
    echo "Service is ready: $url"
    exit 0
  fi
  sleep 2
  elapsed=$((elapsed + 2))
done

echo "Timed out after ${timeout}s waiting for $url" >&2
exit 1

