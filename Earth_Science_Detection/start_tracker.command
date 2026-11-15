#!/bin/zsh
set -eu
cd -- "$(dirname -- "$0")"

if [[ ! -x .venv/bin/python ]]; then
  print -u2 "The Python environment is missing. Create .venv and install requirements.txt first."
  exit 1
fi

if .venv/bin/python - <<'CHECK'
import json
from urllib.request import urlopen
try:
    with urlopen('http://127.0.0.1:8000/api/health', timeout=2) as response:
        status = json.load(response)
    raise SystemExit(0 if status.get('status') == 'ok' and 'local-only' in status.get('access', '') else 1)
except Exception:
    raise SystemExit(1)
CHECK
then
  print "Terra Tracker is already running: http://127.0.0.1:8000/atmosphere"
  open 'http://127.0.0.1:8000/atmosphere'
  exit 0
fi

print "Starting Terra Tracker. Keep this Terminal window open."
print "Open http://127.0.0.1:8000/atmosphere once startup completes."
exec .venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
