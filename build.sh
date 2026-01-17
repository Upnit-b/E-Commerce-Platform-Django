#!/usr/bin/env bash
set -euo pipefail

# # Always use pip via the active python (works in venv/buildpacks)
# python -m pip install --upgrade pip
# python -m pip install -r requirements.txt

python src/manage.py collectstatic --noinput
python src/manage.py migrate --noinput
