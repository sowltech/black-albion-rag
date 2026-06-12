---
title: York / Eburacum Ivory Bangle Matrix Raw Intake
source_url: ""
origin_type: manual_paste
fetch_status: manual
date_attempted: 2026-06-12
intake_status: quarantine_only
review_status: quarantined
evidence_tier: none
canonical_ingestion_allowed: false
promotion_commit_allowed: false
operator_approval_required: true
proposed_target_file: data/raw/black_albion_sites.json
candidate_id: cand_york_eburacum_059
proposed_site_id: site_york_eburacum_059
reason: high-claim mixed archaeological/geological/speculative item requires source verification before canonical data insertion
promoted_to_claims: false
promoted_to_modules: false
promoted_to_sources: false
related_review: research/intake/york_eburacum_ivory_bangle_review.md
related_source_review: research/intake/york_eburacum_ivory_bangle_source_review.md
---

# York / Eburacum Ivory Bangle Matrix Raw Intake

This file quarantines an operator-proposed candidate record covering the
Roman York ("Eburacum") burial commonly discussed as the **"Ivory Bangle
Lady"**, the surrounding **Sycamore Terrace** burial group, the proposed
Yorkshire Museum accession reference **YORYM : 1996.115**, the Leach et al.
2009 "A Lady of York" isotope paper, and a Tier III speculative lens
("Amenta Subsurface Core Extraction", "Dual-material jet-ivory capacitors",
"fluvial siphon loop", "counter-intelligence framing", `system_lock`
language). The record is **quarantined** pending review.

## Proposed Target File

- Pasted target: `data/raw/black_albion_sites.json`
- Live equivalent (the actual Tier I sites ledger): `data/raw/black_albion_sites.json`
- Sibling legacy path (if rendered): `backend/data/black_albion_sites.json`

## Canonical Ingestion Allowed

No. This record must not be added to any `data/raw/*.json` ledger until
each Tier I-shaped claim has been verified against an independent,
reputable source record per `docs/intake-review-workflow.md`.

## Raw Pasted Content

> **Note (2026-06-12):** the operator's intake task referenced a verbatim
> JSON record for `site_york_eburacum_059` but the JSON block itself was
> **not** included in the originating message. The fenced block below is
> a placeholder and must be replaced with the actual operator-supplied
> JSON before any forward motion on this intake. **Do not** synthesise a
> JSON record from the operator's structured description — that would
> count as inventing canonical-shape content under
> `docs/intake-review-workflow.md`.

```json
[
  // PASTE OPERATOR-SUPPLIED RAW JSON HERE.
  // No JSON block was attached to the 2026-06-12 intake task; the
  // operator-supplied structured description is preserved below in
  // markdown form only.
]
```

## Operator-Supplied Structured Description (markdown, not JSON)

- **Proposed id:** `site_york_eburacum_059`
- **Candidate id:** `cand_york_eburacum_059`
- **Name:** The Eburacum Ivory Bangle Matrix and York Glacial Terraces
- **Nearest place:** York City Centre / Sycamore Terrace
- **County:** North Yorkshire
- **Operator-described scope (Tier I-shaped, requires sourcing):**
  - York / Eburacum Late Roman burial context
  - Sycamore Terrace discovery, **1901**
  - Ivory bangle / jet artefacts / high-status grave goods
  - Possible Yorkshire Museum accession reference **YORYM : 1996.115**
  - Leach 2009 / "A Lady of York" / isotope analysis publication
  - Strontium / oxygen isotope evidence and any North African
    ancestry or geographic-origin interpretation
  - **"Vivas in Deo"** Christian inscription / box mount
  - Geology / hydrology claims about the **Vale of York basin**,
    **Ouse-Foss** confluence, river terraces, alluvium, glacial
    sands / gravels
- **Operator-described Tier III speculative lens (must remain Tier III):**
  - "Amenta Subsurface Core Extraction"
  - "Dual-material jet-ivory capacitors"
  - Fluvial siphon loop framing (unsourced)
  - Counter-intelligence framing
  - `system_lock` style canonical-shape vocabulary
  - Any other symbolic, mythic, or interpretive language

## Evidence Warning

The operator description mixes Tier I-shaped archaeological + geological
claims (named site, named burial, named accession, named publication, named
hydrology) with Tier III speculative / mythic framing. The repo doctrine in
`docs/doctrine.md` and `docs/intake-review-workflow.md` requires those
tiers to be **separated** before any item-level promotion. No tier blending
is allowed in the live ledgers.

## Quarantine Rules

- Do not mark this intake as `verified`.
- Do not add this record to `data/raw/black_albion_sites.json`.
- Do not add it to `data/raw/black_albion_claims.json`.
- Do not add it to `data/raw/black_albion_modules.json`.
- Do not add it to `data/raw/black_albion_sources.json`.
- Use this intake only for Tier II inspiration, research lead generation,
  and candidate source hunting.
- Any factual claim surfaced here must be checked against independent,
  reputable source records before entering the live ledgers.
- The Tier III material remains permanently blocked from Tier I promotion.

## Recommended Next Step

Work through the review checklist in
`research/intake/york_eburacum_ivory_bangle_review.md` and the per-claim
worksheet in
`research/intake/york_eburacum_ivory_bangle_source_review.md`. Each Tier
I-shaped claim must be independently verified against named sources
before any promotion pass. If a verbatim JSON record exists, paste it
into the fenced block above in a follow-up commit; do not modify any
canonical ledger as part of that paste.
