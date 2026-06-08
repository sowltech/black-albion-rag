# Black Albion RAG Operator Manual

## Purpose

Black Albion RAG is a local-first forensic research API. It indexes the Black Albion evidence corpus, retrieves grounded passages, builds a prompt, and returns a cited answer when possible.

The active backend layout is `backend/app`, not the retired `backend/rag`
package. Committed source ledgers live under `data/raw`, not `backend/data`.

## Correct `.gitignore`

```text
.env
backend/.env
__pycache__/
*.py[cod]
.pytest_cache/
.venv/
env/
data/index/
data/processed/*
!data/processed/.gitkeep
```

## Run Command

```bash
python3 -m uvicorn backend.app.main:app --reload
```

## Test API

```bash
curl -fsS http://localhost:8000/health

curl -fsS -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Why has the Winchcombe corridor remained important for thousands of years?",
    "k": 3,
    "include_tiers": ["I", "II", "III"],
    "generate_answer": true
  }'
```

## Operating Rule

- Keep `.env` local.
- Keep committed evidence ledger JSON files under `data/raw/`.
- Do not commit generated cache files.
- Add tests before extending retrieval or response logic.

## Evidence Example

Add records directly to a source ledger such as
`data/raw/black_albion_claims.json`:

```json
[
  {
    "id": "claim_rurikid_lineage_bogolyubsky_001",
    "title": "Andrey Bogolyubsky and Rurikid-Cuman Ethnogenesis",
    "region": "Vladimir-Suzdal / Rus",
    "period": ["12th Century", "Medieval"],
    "themes": ["rurikid", "cuman", "architecture", "vladimir-suzdal", "lineage"],
    "summary": "Grand Prince Andrey Bogolyubsky possessed Varangian-Slavic paternal ancestry and a Cuman (Turkic) maternal line. Modern alternative internet descriptions of him as a 'Black Viking' are historically unfounded and stem from a misinterpretation of nomadic political color-coding.",
    "evidence_type": "historical_forensic_record",
    "confidence": "high",
    "source_url": "https://www.british-history.ac.uk/",
    "tier": "I"
  }
]
```
