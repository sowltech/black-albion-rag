# Black Albion RAG

Local-first, source-tier-aware FastAPI service for querying the Black Albion
evidence corpus.

The corpus is curated by hand under `data/raw/`. Every record carries a `tier`
field so the API can keep archival fact, scholarly interpretation, and
speculative / mythic reading visibly separate.

## Purpose

- Run a small, deterministic research API against a hand-curated evidence
  ledger of Albion + Erin sites, claims, timeline entries, and public-domain
  sources.
- Preserve the source-tier boundary at every layer of the stack
  (storage, retrieval, prompt, answer).
- Stay fully local-first: no paid API keys are required to run, test, or
  serve the default build.

## Layout

```text
black-albion-rag/
├── backend/
│   └── app/
│       ├── main.py               # FastAPI app: GET /health, POST /query
│       ├── models.py             # Pydantic request/response models
│       ├── retriever.py          # Deterministic token-overlap retriever
│       ├── prompt_builder.py     # Tier-aware prompt assembly
│       ├── answer_generator.py   # Deterministic grounded answer
│       ├── macritchie_ingest.py  # Public-domain source registration
│       └── vector_ingest.py      # Optional ChromaDB vector pass
├── data/
│   ├── raw/                      # Committed JSON / YAML source ledgers
│   ├── processed/                # Generated intermediates (gitignored)
│   └── index/                    # Generated indexes / caches (gitignored)
├── docs/
│   ├── RAG_BLACK_ALBION.md       # Operator manual
│   └── doctrine.md               # Source-tier doctrine + no-hallucinate policy
├── research/                     # Captured conversations, source pointers
├── scripts/                      # run_dev.sh, smoke_test.sh
└── tests/                        # pytest smoke tests (local-only)
```

## Install

```bash
cd black-albion-rag
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

Copy the env template if you want to customise defaults:

```bash
cp .env.example .env
```

## Run

```bash
scripts/run_dev.sh
# -> http://127.0.0.1:8000/docs
```

The API loads JSON ledgers from `data/raw/` by default. Override with:

```bash
BLACK_ALBION_DATA_DIR=/path/to/raw scripts/run_dev.sh
```

You can also colon-separate multiple directories (e.g.
`data/raw:data/processed`).

## API

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

## Tests

```bash
python3 -m pytest -q
python3 -m compileall backend
```

## Source-tier doctrine

Every record in `data/raw/*.json` carries a `tier` field. The classification
rules live in `data/raw/classification_rules.yaml` and the full doctrine in
`docs/doctrine.md`. In short:

| Tier | Label | What it means |
|---|---|---|
| **I** | Archival evidence | Primary archival records, archaeological surveys, statutes, court judgments, government inventories, well-documented geological / topographic baselines. Treat as load-bearing fact and cite the record id. |
| **II** | Scholarly interpretation | Peer-reviewed or otherwise attributable scholarly readings of the Tier I record. Always attribute the scholar / school and frame as interpretation, not fact. |
| **III** | Speculative / mythic lens | Geomythological, esoteric, alchemical, or operator-authored interpretive lenses (e.g. the Bobby Hemmit framework). Surface only with an explicit speculative caveat. Never present as historical fact. |

The retriever supports a per-request `include_tiers` filter so callers can
restrict an answer to archival-only material when the use case requires it.

## No hallucinated claims policy

This service must never invent historical claims. Concretely:

1. Answers are generated **only** from records retrieved out of the local
   corpus. If retrieval finds nothing, the answer says so explicitly and
   returns no citations.
2. Tier II sentences in the assembled answer are prefixed with "Scholars
   argue that" and attribute to a source record.
3. Tier III sentences are prefixed with "Speculatively," and never blended
   into Tier I sentences.
4. Dates, place names, NHLE numbers, coordinates, and archival record IDs are
   only ever surfaced if they appear verbatim in the underlying ledger.
5. The default `generate_answer` path is deterministic (no external LLM call).
   If a downstream LLM step is wired in later, it must continue to honour the
   same doctrine; the prompt builder already encodes the rules in the system
   prompt.

## Operating rules

- Keep `.env` local. Never commit secrets.
- Commit source ledgers under `data/raw/`.
- Never commit `data/index/`, `data/processed/`, `__pycache__/`, `.venv/`,
  or generated caches. The `.gitignore` enforces this.
- Preserve tier labels at every layer.
