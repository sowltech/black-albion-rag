# Black Albion RAG

Black Albion RAG is a local-first, evidence-tiered research and intake system
for historical, archaeological, geographic, and interpretive claims. It keeps
canonical source ledgers separate from quarantined candidate material, then
gives an operator a browser dashboard for review without allowing automatic
promotion into canonical data.

The current release is `v0.7.0 — Operator Decision Packet Engine`.

## What The System Does

Black Albion RAG provides:

- A deterministic FastAPI research API over local JSON ledgers.
- A read-only operator dashboard at `/dashboard`.
- Canonical ledgers for approved sites, claims, modules, and sources.
- Quarantine and review records for candidate material.
- Source strength scoring and per-claim source review.
- Promotion readiness classification.
- Operator decision labels for candidate claims.
- Strong safety boundaries between Tier I evidence, Tier II interpretation,
  and Tier III speculative / symbolic material.

The system does not automatically approve or promote candidate claims. Any
future canonical promotion requires a separate operator-approved commit.

## Core Pipeline

```text
Raw / candidate material
        |
        v
Candidate quarantine
        |
        v
Source verification
        |
        v
Per-claim source verification
        |
        v
Source strength summary
        |
        v
Promotion readiness classifier
        |
        v
Operator decision packets
        |
        v
Separate operator-approved promotion commit only
```

The canonical ledgers remain the source of truth:

- `data/raw/black_albion_sites.json`
- `data/raw/black_albion_claims.json`
- `data/raw/black_albion_modules.json`
- `data/raw/black_albion_sources.json`

Candidate and review material remains outside those ledgers until explicitly
approved through a future promotion commit.

Current canonical ledger counts:

| Ledger | Count |
|---|---:|
| Sites | 8 |
| Claims | 90 |
| Modules | 14 |
| Sources | 71 |

## Release Ladder

| Release | Theme |
|---|---|
| `v0.3.0` | Operator Dashboard |
| `v0.4.0` | Approval Queue |
| `v0.5.0` | Source Verification Engine |
| `v0.6.0` | Promotion Readiness Engine |
| `v0.7.0` | Operator Decision Packet Engine |

## Dashboard Panels

The read-only dashboard surfaces system and review state through these panels:

- Approval Queue
- Promotion Blockers
- Approval Evidence Links
- Source Verification
- Per-Claim Source Verification
- Source Strength Summary
- Promotion Readiness
- Operator Decision Packets
- Canonical Ledger Integrity
- System Checks

The dashboard is for visibility and review only. It has no approve, promote,
edit, delete, signature, or canonical write actions.

## Operator Decision Labels

The v0.7.0 decision layer recommends one label per reviewed claim:

- `approve_for_corrected_wording_review`
- `needs_more_source_work`
- `do_not_promote`
- `tier_iii_only`
- `ready_for_separate_promotion_commit`

Important safety rule: only `ready_for_separate_promotion_commit` may imply a
future promotion path, and even then only through a separate
operator-approved commit. The engine does not execute that decision.

## Safety Guarantees

- Dashboard governance is read-only.
- There is no automatic promotion.
- There are no canonical write endpoints.
- There are no approve/promote buttons.
- There are no dashboard mutation actions.
- Corrected wording review is not promotion.
- Decision labels are recommendations only.
- Tier III speculative material is contained and non-canonical.
- Tier III claims never become Tier I facts through the dashboard.
- Canonical promotion requires a separate operator-approved commit.
- Candidate material stays separate from canonical ledgers until explicitly
  promoted in a future commit.

## Current Candidate Examples

The candidate queue currently includes:

- `cand_gemini_share_002` — quarantined Gemini intake artifact with no extracted
  promotable facts.
- `cand_gloucestershire_egypt_058` — source-reviewed Gloucestershire/Egypt
  candidate with Tier III material contained.
- `cand_york_eburacum_059` — York/Eburacum Ivory Bangle candidate with
  claim-level source attachment, readiness classification, and an operator
  packet.

## Evidence Tiers

| Tier | Meaning | Handling |
|---|---|---|
| Tier I | Source-backed historical, archaeological, geological, or documentary evidence | Must be supported by named source records or marked as needing verification. |
| Tier II | Scholarly interpretation or landscape analysis | Must be framed as interpretation, not direct fact. |
| Tier III | Speculative, mythic, symbolic, or creative-worldbuilding layer | Must remain labelled speculative and must not enter Tier I canonical data. |

See `docs/evidence-tier-rules.md` and `docs/doctrine.md` for the full rules.

## Local Setup

```bash
cd black-albion-rag
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run The App

```bash
python3 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Open:

- API docs: `http://127.0.0.1:8000/docs`
- Dashboard: `http://127.0.0.1:8000/dashboard`
- Health: `http://127.0.0.1:8000/health`

If port `8000` is already occupied, use another local port:

```bash
python3 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8765
```

## Validation Commands

Run the standard local validation gates:

```bash
python3 -m json.tool data/raw/black_albion_candidate_claims.json
bash scripts/smoke_live_uvicorn.sh
bash scripts/validate_enterprise_gpt_os.sh
python3 -m pytest -q
python3 -m compileall -q backend
git diff --check
git diff --cached --check
```

The live smoke test boots the FastAPI app under uvicorn, probes the public API
and dashboard panels, then stops the server.

## API Examples

```bash
curl -fsS http://127.0.0.1:8000/health
```

```bash
curl -fsS -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Why has the Winchcombe corridor remained important?",
    "k": 5,
    "include_tiers": ["I", "II", "III"],
    "generate_answer": true
  }'
```

## Repository Rules

- Keep `.env` local and ignored.
- Never commit secrets.
- Do not commit generated caches, virtual environments, or local indexes.
- Preserve Tier I / Tier II / Tier III boundaries.
- Do not promote candidate material without explicit operator approval and a
  separate commit.
- Do not add dashboard write actions unless a future release explicitly designs
  and validates that capability.
