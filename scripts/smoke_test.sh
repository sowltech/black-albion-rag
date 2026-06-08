#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

BASE_URL="${BLACK_ALBION_BASE_URL:-http://127.0.0.1:8000}"

curl -fsS "$BASE_URL/health"
printf '\n'
curl -fsS -X POST "$BASE_URL/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Why has the Winchcombe corridor remained important for thousands of years?",
    "k": 3,
    "include_tiers": ["I", "II", "III"],
    "generate_answer": true
  }'
printf '\n'
