#!/bin/zsh
set -eu
cd -- "$(dirname -- "$0")"

if [[ ! -x .venv/bin/python ]]; then
  print -u2 "The Python environment is missing. Create .venv and install requirements.txt first."
  exit 1
fi

.venv/bin/python scripts/start_server.py
open 'http://127.0.0.1:8000/atmosphere'
