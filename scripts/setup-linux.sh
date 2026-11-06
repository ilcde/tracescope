#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m venv --system-site-packages .venv
.venv/bin/python -m pip install -r requirements.txt
npm ci
npm run build
.venv/bin/python -m tracescope doctor
