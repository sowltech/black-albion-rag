#!/usr/bin/env bash
# Live uvicorn smoke test: boots the FastAPI app, probes each public
# endpoint, then tears the server down cleanly.
#
# Defaults: 127.0.0.1:8765 (8000 is commonly taken by Docker on this host).
# Overrides:
#   BLACK_ALBION_PORT  — TCP port (default 8765)
#   BLACK_ALBION_HOST  — bind host (default 127.0.0.1)
#   PYTHON             — interpreter (default python3)
#   BOOT_TIMEOUT       — seconds to wait for /health (default 30)
#   STOP_TIMEOUT       — seconds to wait for graceful shutdown (default 10)
#
# Exit codes:
#   0  all checks passed
#   1  unexpected response from an endpoint
#   2  server failed to boot within BOOT_TIMEOUT
#   3  server failed to stop within STOP_TIMEOUT (escalated to SIGKILL)
#   4  port already in use
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

HOST="${BLACK_ALBION_HOST:-127.0.0.1}"
PORT="${BLACK_ALBION_PORT:-8765}"
PY="${PYTHON:-python3}"
BOOT_TIMEOUT="${BOOT_TIMEOUT:-30}"
STOP_TIMEOUT="${STOP_TIMEOUT:-10}"
BASE_URL="http://${HOST}:${PORT}"
LOG_FILE="$(mktemp -t black_albion_uvicorn.XXXXXX)"

if lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "[smoke] ERROR: port ${PORT} already in use" >&2
  lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN >&2
  exit 4
fi

cleanup() {
  local code=$?
  if [[ -n "${UVICORN_PID:-}" ]] && kill -0 "${UVICORN_PID}" 2>/dev/null; then
    echo "[smoke] stopping uvicorn pid=${UVICORN_PID}"
    kill -TERM "${UVICORN_PID}" 2>/dev/null || true
    local waited=0
    while kill -0 "${UVICORN_PID}" 2>/dev/null; do
      if (( waited >= STOP_TIMEOUT )); then
        echo "[smoke] WARN: SIGTERM ignored, escalating to SIGKILL" >&2
        kill -KILL "${UVICORN_PID}" 2>/dev/null || true
        code=3
        break
      fi
      sleep 1
      waited=$((waited + 1))
    done
    wait "${UVICORN_PID}" 2>/dev/null || true
    echo "[smoke] stopped"
  fi
  if [[ $code -ne 0 && -s "${LOG_FILE}" ]]; then
    echo "----- uvicorn log (tail) -----" >&2
    tail -50 "${LOG_FILE}" >&2 || true
    echo "------------------------------" >&2
  fi
  rm -f "${LOG_FILE}"
  exit $code
}
trap cleanup EXIT INT TERM

echo "[smoke] starting uvicorn on ${BASE_URL}"
"${PY}" -m uvicorn backend.app.main:app --host "${HOST}" --port "${PORT}" \
  --log-level warning >"${LOG_FILE}" 2>&1 &
UVICORN_PID=$!
echo "[smoke] uvicorn pid=${UVICORN_PID}"

# Wait for /health
waited=0
while true; do
  if curl -fsS -o /dev/null -m 2 "${BASE_URL}/health" 2>/dev/null; then
    break
  fi
  if ! kill -0 "${UVICORN_PID}" 2>/dev/null; then
    echo "[smoke] ERROR: uvicorn died during boot" >&2
    exit 2
  fi
  if (( waited >= BOOT_TIMEOUT )); then
    echo "[smoke] ERROR: /health did not respond within ${BOOT_TIMEOUT}s" >&2
    exit 2
  fi
  sleep 1
  waited=$((waited + 1))
done
echo "[smoke] boot ok in ${waited}s"

probe_get() {
  local label="$1" path="$2" expect="${3:-200}"
  local code
  code=$(curl -sS -o /tmp/black_albion_body.$$ -w '%{http_code}' -m 5 "${BASE_URL}${path}" || echo "000")
  if [[ "${code}" != "${expect}" ]]; then
    echo "[smoke] FAIL ${label} ${path} expected=${expect} got=${code}" >&2
    [[ -s /tmp/black_albion_body.$$ ]] && head -c 400 /tmp/black_albion_body.$$ >&2 && echo >&2
    rm -f /tmp/black_albion_body.$$
    return 1
  fi
  echo "[smoke] ok   ${label} ${path} -> ${code}"
  rm -f /tmp/black_albion_body.$$
}

probe_post() {
  local label="$1" path="$2" body="$3" expect="${4:-200}"
  local code
  code=$(curl -sS -o /tmp/black_albion_body.$$ -w '%{http_code}' -m 10 \
    -X POST -H "Content-Type: application/json" -d "${body}" \
    "${BASE_URL}${path}" || echo "000")
  if [[ "${code}" != "${expect}" ]]; then
    echo "[smoke] FAIL ${label} ${path} expected=${expect} got=${code}" >&2
    [[ -s /tmp/black_albion_body.$$ ]] && head -c 400 /tmp/black_albion_body.$$ >&2 && echo >&2
    rm -f /tmp/black_albion_body.$$
    return 1
  fi
  echo "[smoke] ok   ${label} ${path} -> ${code}"
  rm -f /tmp/black_albion_body.$$
}

# Probe a GET endpoint and require both the status code and a substring in the
# response body. Used for endpoints that return 200 with a status field
# (e.g. /modules/{unknown_id} -> 200 {"status":"not_found"}).
probe_get_body() {
  local label="$1" path="$2" expect_code="$3" expect_substr="$4"
  local tmp code
  tmp=$(mktemp -t black_albion_body.XXXXXX)
  code=$(curl -sS -o "${tmp}" -w '%{http_code}' -m 5 "${BASE_URL}${path}" || echo "000")
  if [[ "${code}" != "${expect_code}" ]]; then
    echo "[smoke] FAIL ${label} ${path} expected=${expect_code} got=${code}" >&2
    head -c 400 "${tmp}" >&2 && echo >&2
    rm -f "${tmp}"
    return 1
  fi
  if ! grep -q "${expect_substr}" "${tmp}"; then
    echo "[smoke] FAIL ${label} ${path} body missing substring '${expect_substr}'" >&2
    head -c 400 "${tmp}" >&2 && echo >&2
    rm -f "${tmp}"
    return 1
  fi
  echo "[smoke] ok   ${label} ${path} -> ${code} (body contains '${expect_substr}')"
  rm -f "${tmp}"
}

# Core endpoints
probe_get  "health" "/health" 200
probe_get  "modules" "/modules" 200
probe_get  "sites" "/sites" 200
probe_get  "map_layers" "/map/layers" 200
probe_get  "claims" "/claims" 200
probe_get  "export_modules" "/export/modules.json" 200
probe_get  "export_claims" "/export/claims.json" 200
probe_get  "search" "/search?q=Winchcombe" 200
probe_get  "openapi" "/openapi.json" 200
probe_get_body "dashboard" "/dashboard" 200 "Operator Dashboard"
probe_get_body "dashboard_release" "/dashboard" 200 "Governed Runtime Proof"
probe_get_body "dashboard_repo_estate" "/dashboard" 200 "Repo Estate"
probe_get_body "dashboard_repo_gold" "/dashboard" 200 "black-albion-rag"
probe_get_body "dashboard_source_intake" "/dashboard" 200 "Source / Intake Review"
probe_get_body "dashboard_source_read_only" "/dashboard" 200 "read-only"
probe_get_body "dashboard_system_checks" "/dashboard" 200 "System Checks"
probe_get_body "dashboard_governance_ci" "/dashboard" 200 "Enterprise GPT OS Validation"
probe_get_body "dashboard_runtime_ci" "/dashboard" 200 "Live Uvicorn Smoke"
probe_get_body "dashboard_search" "/dashboard?q=Winchcombe" 200 "Search Results"
probe_get_body "dashboard_query" "/dashboard?query=What%20is%20Winchcombe" 200 "Query Result"
probe_post "query" "/query" '{
    "question": "Why has the Winchcombe corridor remained important?",
    "k": 3,
    "include_tiers": ["I","II","III"],
    "generate_answer": true
  }' 200

# Negative path: unknown module id returns 200 with status "not_found"
# (design choice — the API surfaces miss state in the body, not via HTTP code)
probe_get_body "module_not_found" "/modules/__does_not_exist__" 200 '"not_found"'

echo "[smoke] all live endpoint probes passed"
