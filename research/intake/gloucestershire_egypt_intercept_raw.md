---
title: Gloucestershire Egyptian Intercept Raw Intake
source_url: ""
origin_type: manual_paste
fetch_status: manual
date_attempted: 2026-06-09
intake_status: quarantine_only
evidence_tier: none
proposed_target_file: backend/data/black_albion_sites.json
canonical_ingestion_allowed: false
promoted_to_claims: false
promoted_to_modules: false
promoted_to_sources: false
related_review: research/intake/gloucestershire_egypt_intercept_review.md
---

# Gloucestershire Egyptian Intercept Raw Intake

This file preserves a pasted JSON record proposed for the live Tier I sites
ledger. The pasted comment header asked for it to be added directly to
`backend/data/black_albion_sites.json`. That path does not exist in the current
repo (the live path is `data/raw/black_albion_sites.json`, which is the
hand-curated Tier I sites ledger), and the content has not been independently
sourced, so the record is **quarantined** pending review.

## Proposed Target File

- Pasted target: `backend/data/black_albion_sites.json`
- Live equivalent (the actual Tier I sites ledger): `data/raw/black_albion_sites.json`

## Canonical Ingestion Allowed

No. This record must not be added to any `data/raw/*.json` ledger until each
Tier I-shaped claim has been verified against an independent, reputable
source record per `docs/intake-review-workflow.md`.

## Raw Pasted Content

```json
[
  {
    "id": "site_gloucestershire_egypt_058",
    "name": "The Gloucestershire Egyptian Intercept and Alexandria Back-Badge Vector",
    "region": "Trans-Continental Maritime Axis / Severn-to-Nile Conduits",
    "nearest_place": "Gloucester Docks Repository / Alexandria Waterfront / Suez Passages",
    "county": "Gloucestershire",
    "period": ["1801 CE Napoleonic Campaign", "1884 CE Mahdist War Phase", "WWI Yeomanry Mounted Operations", "WWII Armoured Western Desert Intercept"],
    "layer_0_geology": {
      "fault_lines": "Nile Delta Structural Subsidence Lines / Cotswold Escarpment Boundary Thrusts",
      "mineral_strata": "Alluvial Desert Sands, Marine Limestone Strata, Tertiary Deltaic Silts, Cotswold Oolitic Formations",
      "hydrology_metrics": "Tidal Severn Estuary Discharges, Nile Fluvial Siphon Corridors, Suez Maritime Siphon Gates"
    },
    "tier_i_enclosure_evidence": {
      "administrative_fencing": "War Office Statutory Despatch Registries, Regimental Uniform Dress Codes, Imperial Battle Honour Charters, Scheduled Museum Archive Gating",
      "structural_caging": "Conversion of Horse Yeomanry to Mechanized Armoured Tank Hulls, Institutional Storage of Memorial Banners inside Cathedral Vaults, Strategic Military Securitization of Suez Logistics",
      "target_records": ["1801 Great Britain War Department Campaign Despatches", "1884 London Gazette Victoria Cross Citations for Percival Marling", "Official Operational War Diaries of the 21st Royal Gloucestershire Hussars"]
    },
    "tier_iii_speculative_logic": {
      "retrieval_mode": "Amenta Subsurface Core Extraction",
      "mapping_priority": "Prioritize Continuous Dual-Facing Back-Badge Sensory Vectors, Red Sea Desert Overland Marches, and Western Desert Mechanized Armour Anchors Over Modern Holiday Travel Curation, Cairo Real Estate Demarcations, and Local Regimental Museum Souvenir Displays",
      "counter_intelligence_flag": "Isolate and Eliminate Whimsical Uniform Romance and Romanticized 'Desert Adventure' Imperial Folklore Fabricated to Mask the Heavy Resource-Gating, Strategic Choke-Point Policing, and Systemic Human Capital Extraction of the Trans-Continental Grid"
    },
    "system_lock": "Chapter_48_Gloucestershire_Egypt_Core_Ingestion_Complete"
  }
]
```

## Evidence Warning

The pasted record mixes Tier I-shaped historical claims (named regiments,
dated campaigns, specific London Gazette VC citations, named war diaries) with
Tier III speculative / mythic framing (Amenta subsurface extraction, back-badge
sensory vector, trans-continental grid, counter-intelligence flag).

The repo doctrine in `docs/intake-review-workflow.md` requires those two
tiers to be **separated** before any item-level promotion. No tier blending is
allowed in the live ledgers.

## Quarantine Rules

- Do not mark this intake as `verified`.
- Do not add this record to `data/raw/black_albion_sites.json`.
- Do not add it to `data/raw/black_albion_claims.json`.
- Do not add it to `data/raw/black_albion_modules.json`.
- Do not add it to `data/raw/black_albion_sources.json`.
- Use this intake only for Tier II inspiration, research lead generation, and
  candidate source hunting.
- Any factual claim surfaced here must be checked against independent,
  reputable source records before entering the live ledgers.

## Recommended Next Step

Work through the review checklist in
`research/intake/gloucestershire_egypt_intercept_review.md`. Each Tier I-shaped
claim must be independently verified against named sources before any
promotion pass.
