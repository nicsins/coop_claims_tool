#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m pip install flake8 pytest

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example — set CLAIMS_API_KEY before exposing the API."
fi

echo "Setup complete. Run: python3 api_server.py"
