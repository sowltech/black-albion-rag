---
title: York / Eburacum Ivory Bangle Matrix Intake Review
status: quarantine_review
review_required: true
canonical_ingestion_allowed: false
raw_content_artifact: research/intake/york_eburacum_ivory_bangle_raw.md
source_review_file: research/intake/york_eburacum_ivory_bangle_source_review.md
proposed_target_file: data/raw/black_albion_sites.json
candidate_id: cand_york_eburacum_059
proposed_site_id: site_york_eburacum_059
date_reviewed: 2026-06-12
risk_level: high_for_tier_i
reason: high-claim mixed archaeological/geological/speculative item requires source verification before canonical data insertion
---

> Source review pending. See
> [`york_eburacum_ivory_bangle_source_review.md`](york_eburacum_ivory_bangle_source_review.md)
> for per-claim findings, candidate sources, factual corrections required
> before promotion, and the standing promotion gate. No canonical ledger
> has been modified.
>
> Claim 1 source attachment pass started 2026-06-12. The worksheet now
> attaches York Museums Trust / Yorkshire Museum and Our Migration Story
> evidence for the Sycamore Terrace 1901 / Ivory Bangle Lady burial frame.
> The claim remains unpromoted and canonical ingestion remains blocked.

# York / Eburacum Ivory Bangle Matrix Intake Review

## Status

Quarantined. The raw artifact lives at
`research/intake/york_eburacum_ivory_bangle_raw.md`. **No** canonical
ledger has been modified and no item-level promotion has occurred. The
operator's structured description must be source-checked claim by claim
before any forward motion.

## Why Quarantined

The intake mixes two tiers in a single proposed record:

- **Tier I-shaped material** — named Roman city ("Eburacum" / York),
  named site (Sycamore Terrace), dated discovery (1901), named
  artefacts (ivory bangle, jet bracelet, related grave goods), named
  scholarly publication (Leach et al. 2009 — "A Lady of York"), named
  Yorkshire Museum accession (`YORYM : 1996.115`), named Christian
  inscription (`Vivas in Deo`), and named hydrology/geology
  (Vale of York, Ouse-Foss, glacial terraces, alluvium). These look
  like archival/archaeological/scientific facts but carry **no
  attached primary or institutional source records** in this intake
  and have not been independently verified.
- **Tier III-shaped material** — "Amenta Subsurface Core
  Extraction", "Dual-material jet-ivory capacitors", "fluvial siphon
  loop", "counter-intelligence" framing, and `system_lock`
  vocabulary. This is interpretive / speculative framing and must
  remain explicitly labelled Tier III per `docs/doctrine.md`.

The repo doctrine in `docs/intake-review-workflow.md` requires those
tiers to be separated **before** anything is added to a live ledger,
and forbids AI-generated or pasted material from becoming Tier I
evidence on its own authority.

## Tier Classification Of The Pasted Content

### Tier I-candidate (requires independent verification before promotion)

Each item below must be checked against named, reputable, dated
records before any of it is treated as fact.

- York / Eburacum Late Roman burial context for the "Ivory Bangle
  Lady" discovery.
- Sycamore Terrace, York, as the discovery location, with a stated
  discovery year of **1901**.
- Identification of ivory bangle / jet artefacts / other high-status
  grave goods associated with the burial.
- Yorkshire Museum accession reference **YORYM : 1996.115** (or
  equivalent York Museums Trust catalogue identifier).
- Hella Eckardt / Stephany Leach et al. **"A Lady of York"** (2009),
  *Antiquity* / equivalent publication of the isotope analysis.
- Strontium / oxygen isotope results and any conclusions about
  North-African / Mediterranean ancestry or geographic origin.
- The Christian inscription **"Vivas in Deo"** ("May you live in
  God") on a box mount or grave-related object, and its attribution
  to the same burial assemblage or context.
- Vale of York basin / Ouse–Foss confluence / glacial terrace /
  alluvium / glacial sand-and-gravel claims, sourced to British
  Geological Survey memoirs or equivalent institutional geology.

### Tier III (preserve as labelled speculative only, do not promote as fact)

- `retrieval_mode: Amenta Subsurface Core Extraction` and similar
  Bobby Hemmit-style lens vocabulary.
- "Dual-material jet-ivory capacitors" and any interpretive
  energetic/material-capacitor framing.
- "Fluvial siphon loop" framing applied to the Ouse–Foss when not
  sourced to an institutional hydrology record.
- "Counter-intelligence" / state-suppression framing of an academic
  finding.
- `system_lock` and any other canonical-shape vocabulary copied from
  the Bobby Hemmit framework.

This material may live in an explicitly Tier III block of a future
record if — and only if — a separate Tier I evidence block carrying
real source records is created in the same record, with the two
tiers clearly walled off per `docs/doctrine.md`.

### Layer 0 geology fields

Any "fault_lines", "mineral_strata", or "hydrology_metrics" prose
that uses Bobby Hemmit-style vocabulary must not be treated as a
Layer 0 baseline without a separate British Geological Survey /
Historic England / equivalent reference.

## Source Review Checklist

Each item is `unverified` until an independent reputable source
record is attached. Verification means a dated reference to a named
primary, scholarly, or institutional record, not paraphrase of
AI-generated text.

- [ ] Verify Yorkshire Museum / York Museums Trust catalogue entry
      `YORYM : 1996.115` (or whichever accession is correct) for the
      Ivory Bangle Lady and the Sycamore Terrace burial.
- [ ] Verify Archaeology Data Service (ADS) record(s) for the
      Sycamore Terrace burial group and the 1901 discovery context.
- [ ] Verify **Leach, S., Eckardt, H., Chenery, C., Müldner, G., &
      Lewis, M. 2009. "A Lady of York: migration, ethnicity and
      identity in Roman Britain", *Antiquity*** (or whichever the
      exact citation is) for the isotope analysis and the
      ancestry/origin discussion.
- [ ] Verify the strontium / oxygen isotope interpretation against
      the published methodology and any follow-up commentary, not
      AI summary.
- [ ] Verify the **"Vivas in Deo"** inscription against the museum
      object record / Roman Inscriptions of Britain (RIB) entry or
      equivalent published epigraphic record.
- [ ] Verify Vale of York / Ouse–Foss / glacial terrace / alluvium
      claims against the British Geological Survey memoir for the
      York area (Sheet 63 York and any associated Quaternary
      mapping).
- [ ] Verify York Archaeology / York Archaeological Trust reporting
      on the burial group and any subsequent excavations or
      reinterpretations.
- [ ] Verify Historic England / National Heritage List for England
      entries for the relevant scheduled monument, listed building,
      or archaeological constraint (if any).
- [ ] Confirm separation: documented archaeological / geological
      history (Tier I) must be written in plain, sourced language.
      The symbolic / speculative "Amenta Subsurface Core",
      "Dual-material jet-ivory capacitors", "fluvial siphon loop",
      "counter-intelligence", and `system_lock` wording must stay in
      an explicitly Tier III block and must not be presented as
      historical or scientific fact.

## Allowed Use

- Tier II inspiration.
- Research lead generation.
- Candidate source hunting against the checklist above.
- Identifying named museums, accessions, publications, sites and
  dates worth verifying independently.

## Forbidden Use

- Direct Tier I sourcing.
- Verified claim creation from the pasted text alone.
- Claim promotion without independent reputable source records.
- Treating speculative or symbolic material as historical or
  scientific fact.
- Mixing Tier I and Tier III content inside a single live record.
- Writing the record to `backend/data/black_albion_sites.json` (if
  it exists), `data/raw/black_albion_sites.json`,
  `data/raw/black_albion_claims.json`,
  `data/raw/black_albion_modules.json`, or
  `data/raw/black_albion_sources.json`.

## Promotion Gate

Promotion of any item out of this intake requires:

- a completed checklist item with a named, dated, reputable source
  record;
- item-level claim wording that is narrower than the pasted broad
  statement;
- separation of Tier I evidence from Tier II interpretation and
  Tier III speculative framing;
- an explicit operator approval and a separate commit that states
  which candidate item was promoted, with the attached source
  reference.

## Recommended Next Step

Work the Source Review Checklist top-to-bottom and complete the
per-claim worksheet in
`research/intake/york_eburacum_ivory_bangle_source_review.md`. Keep
all of the Tier III framing labelled Tier III. Do not modify any
canonical ledger as part of the review pass; promotion happens in a
separate, explicit, operator-approved commit only.
