#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
python3 enterprise-gpt-os/scripts/validate_manifest.py
python3 enterprise-gpt-os/scripts/run_evals.py
