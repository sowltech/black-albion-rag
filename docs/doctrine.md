# Source-tier doctrine

This document is the authoritative source for the tier semantics used by
`backend/app/*` and `data/raw/classification_rules.yaml`. It must be kept in
sync with both.

## Tiers

### Tier I — Archival evidence

Primary archival records, archaeological surveys, statutes, court judgments,
government inventories, and well-documented geological / topographic
baselines.

- Treat as load-bearing fact.
- Cite the record id whenever invoked.
- Examples:
  - 1086 Domesday Book entries (The National Archives)
  - NHLE List Entry numbers (Historic England)
  - Belfast Court of Appeal 1897 judgments
  - British Geological Survey memoirs

### Tier II — Scholarly interpretation

Peer-reviewed or otherwise attributable scholarly readings of the Tier I
record.

- Always attribute the scholar or school.
- Frame as interpretation, not fact.
- The assembled answer prefixes Tier II sentences with **"Scholars argue
  that "** so the attribution is unmissable.
- Examples:
  - MacRitchie's 1890 euhemeristic reading of fairy folklore
  - Enclosure historiography (E. P. Thompson, J. M. Neeson)

### Tier III — Speculative / mythic lens

Geomythological, esoteric, alchemical, or operator-authored interpretive
lenses. The Bobby Hemmit framework captured in
`research/2026-06-07_gemini_screwworms_to_albion_engine.md` is the canonical
Tier III source for this repo.

- Surface only with an explicit speculative caveat.
- Never assert as historical fact.
- The assembled answer prefixes Tier III sentences with **"Speculatively,"**
  and renders them in a clearly separated section.

## Answer guardrails

1. If a query mixes Tier I and Tier III content, the answer must visually
   separate the two sections.
2. Every Tier III sentence in an answer must begin with a caveat such as
   "Speculatively," or "In the Bobby Hemmit framework,".
3. Never invent geographic coordinates, dates, NHLE numbers, or archival
   record ids that are not present in the ledgers.
4. If no Tier I evidence is retrieved, the answer should say so plainly
   before showing any Tier II or Tier III material.

## Retrieval policy

The default retriever (`backend/app/retriever.py`) is a deterministic
token-overlap scorer with a phrase bonus. It runs entirely on the local
machine and does not call any external service. This means:

- No API keys are required to run the default build.
- Reproducibility: the same corpus + query always returns the same ranking.
- A vector backend (ChromaDB) is available behind
  `backend/app/vector_ingest.py` but is opt-in.

If a downstream LLM step is added later, it must continue to honour this
doctrine. The system prompt produced by `backend/app/prompt_builder.py`
already encodes the rules.
