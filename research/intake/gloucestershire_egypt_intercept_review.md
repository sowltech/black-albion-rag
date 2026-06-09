---
title: Gloucestershire Egyptian Intercept Intake Review
status: quarantine_review
review_required: true
canonical_ingestion_allowed: false
raw_content_artifact: research/intake/gloucestershire_egypt_intercept_raw.md
proposed_target_file: backend/data/black_albion_sites.json
date_reviewed: 2026-06-09
risk_level: high_for_tier_i
reason: high-claim mixed historical/speculative entry requires source verification before canonical data insertion
---

# Gloucestershire Egyptian Intercept Intake Review

## Status

Quarantined. Raw pasted content is preserved at
`research/intake/gloucestershire_egypt_intercept_raw.md` and **must not** be
written to any live ledger until the source review checklist below is
completed, item by item, against independent reputable records.

## Why Quarantined

The pasted record mixes two tiers in a single object:

- **Tier I-shaped material** — named regiments, dated military campaigns,
  specific decorations, named war diaries, specific archive locations.
  These look like archival fact but carry no attached source records and
  have not been independently verified.
- **Tier III-shaped material** — "Amenta Subsurface Core Extraction",
  "Back-Badge Sensory Vector", "Trans-Continental Grid",
  "counter-intelligence flag". This is interpretive / speculative framing
  and must remain explicitly labelled Tier III.

The repo doctrine in `docs/intake-review-workflow.md` requires those tiers to
be separated **before** anything is added to a live ledger, and forbids
AI-generated or pasted material from becoming Tier I evidence on its own
authority.

## Tier Classification Of The Pasted Content

### Tier I candidate (requires independent verification before promotion)

Each item below must be checked against named, reputable, dated archival
records before any of it is treated as fact.

- The 1801 British military campaign in Egypt against Napoleonic forces and
  any Gloucestershire-raised unit's role in it.
- Percival Marling's Victoria Cross citation (claimed by the pasted record
  as a 1884 London Gazette entry tied to the Mahdist War period).
- The 21st Royal Gloucestershire Hussars as a named formation with WWI
  yeomanry / WWII Western Desert operational history, and the existence and
  whereabouts of their official operational war diaries.
- "Gloucester Docks Repository" — whether a documented archive of that name
  exists, and whether it holds material relevant to the above claims.
- Memorial banners stored in cathedral vaults attributable to a named
  Gloucestershire regiment.
- Use of Alexandria, the Red Sea, and the Suez corridor by named
  Gloucestershire formations on dated operations.

### Tier III (preserve as labelled speculative only, do not promote as fact)

- `retrieval_mode: Amenta Subsurface Core Extraction`.
- `mapping_priority: Continuous Dual-Facing Back-Badge Sensory Vectors`,
  `Trans-Continental Grid` framing, etc.
- `counter_intelligence_flag` text about "uniform romance",
  "desert adventure folklore", "systemic human capital extraction".

This material may live in an explicitly Tier III block of a future record if
- and only if - a separate Tier I evidence block carrying real source
records is created in the same record, with the two tiers clearly walled off
per `docs/doctrine.md`.

### Layer 0 geology fields

The `fault_lines`, `mineral_strata`, and `hydrology_metrics` strings in the
pasted record are stylistic and not sourced to BGS or any other geological
survey. They must not be treated as a Layer 0 baseline without a separate
BGS / Historic England / equivalent reference.

## Source Review Checklist

Each item is `unverified` until an independent reputable source record is
attached. Verification means a dated reference to a named primary or
secondary record, not paraphrase of AI-generated text.

- [ ] Verify the 1801 Gloucestershire / Egypt campaign connection against
      War Office despatches in The National Archives (WO series) and a
      regimental history of the relevant Gloucestershire formation.
- [ ] Verify Percival Marling's London Gazette Victoria Cross citation:
      exact London Gazette issue, date, and page; confirm campaign context.
- [ ] Verify the existence and lineage of the 21st Royal Gloucestershire
      Hussars and any WWII Western Desert references against regimental
      histories and TNA WO war diaries.
- [ ] Verify the "Gloucester Docks Repository" reference: identify the actual
      archival institution (e.g. Gloucestershire Archives, Soldiers of
      Gloucestershire Museum) and the catalogue reference for any material
      cited.
- [ ] Verify the Alexandria / Suez operational references with named war
      diary entries or campaign histories.
- [ ] Verify any cathedral banner / regimental colour claim against
      Gloucester Cathedral records or equivalent.
- [ ] Confirm separation: documented military history (Tier I) must be
      written in plain, sourced language. The symbolic / speculative
      "back-badge vector", "Amenta", "trans-continental grid",
      "counter-intelligence" wording must stay in an explicitly Tier III
      block and must not be presented as historical fact.

## Allowed Use

- Tier II inspiration.
- Research lead generation.
- Candidate source hunting against the checklist above.
- Identifying named regiments, decorations, archives, and dates worth
  verifying independently.

## Forbidden Use

- Direct Tier I sourcing.
- Verified claim creation from the pasted text alone.
- Claim promotion without independent reputable source records.
- Treating speculative or symbolic material as historical fact.
- Mixing Tier I and Tier III content inside a single live record.
- Writing the record to `backend/data/black_albion_sites.json`,
  `data/raw/black_albion_sites.json`, `data/raw/black_albion_claims.json`,
  `data/raw/black_albion_modules.json`, or
  `data/raw/black_albion_sources.json`.

## Promotion Gate

Promotion of any item out of this intake requires:

- a completed checklist item with a named, dated, reputable source record;
- item-level claim wording that is narrower than the pasted broad statement;
- separation of Tier I evidence from Tier II interpretation and Tier III
  speculative framing;
- an explicit operator approval and a separate commit that states which
  candidate item was promoted, with the attached source reference.

## Recommended Next Step

Work the Source Review Checklist top-to-bottom. Open Tier I source hunting
in a future review pass that does not modify any live ledger until each
item has at least one independent reputable source attached. Keep all of
the Tier III framing labelled Tier III.
