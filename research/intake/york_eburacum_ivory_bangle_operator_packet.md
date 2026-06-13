---
candidate_id: cand_york_eburacum_059
proposed_site_id: site_york_eburacum_059
title: York/Eburacum Ivory Bangle Matrix Operator Review Packet
status: operator_review_packet
canonical_ingestion_allowed: false
promotion_commit_allowed: false
operator_approval_required: true
generated_from_claims: 1-8
canonical_ledger_counts: sites 8 / claims 90 / modules 14 / sources 71
---

# York/Eburacum Ivory Bangle Matrix Operator Review Packet

## Executive Summary

This packet summarises the quarantined source-review work for
`cand_york_eburacum_059`. It is read-only and does not approve or perform
canonical ingestion.

- Claims 1-4 are broadly source-attached and nearly_ready for careful
  operator review.
- Claim 5 remains not_ready because `YORYM : 1996.115` / direct accession
  ID is unverified.
- Claim 6 remains not_ready for exact Latin / RIB / accession evidence,
  but has partial source support for the English rendering and object
  description.
- Claim 7 is nearly_ready only for corrected BGS-supported geology
  wording; unsupported hydrology / fault phrases must be dropped.
- Claim 8 remains Tier III speculative-only and has no Tier I promotion
  path.

## Canonical Ledger Protection

The following canonical ledgers remain untouched by this packet:

- `data/raw/black_albion_sites.json`
- `data/raw/black_albion_claims.json`
- `data/raw/black_albion_modules.json`
- `data/raw/black_albion_sources.json`

## Claim-By-Claim Readiness Table

| Claim | Short claim title | Current source_status | Promotion readiness | Strongest source type | Supported elements | Unresolved gaps | Operator recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Sycamore Terrace 1901 / Roman York burial | partial_sources_attached | nearly_ready | Yorkshire Museum institutional page; Our Migration Story academic public-history article | Ivory Bangle Lady name, 1901 near/in Sycamore Terrace discovery, late fourth-century Roman York burial, high-status framing | Contemporary 1901 report, ADS record, object-level catalogue, exact cemetery-group relationship | Review corrected wording; require operator approval before any separate promotion commit |
| 2 | Ivory bangles / high-status grave goods | partial_sources_attached | nearly_ready | Yorkshire Museum institutional page | Jet and elephant ivory bracelets, earrings, pendants, beads, blue glass jug, glass mirror, high-status interpretation | Object-level catalogue records, ADS object records, peer-reviewed grave-goods table | Review broad grave-goods wording; do not promote accession-level detail |
| 3 | Isotope testing / strontium / oxygen evidence | partial_sources_attached | nearly_ready | Leach et al. citation target; Yorkshire Museum; Our Migration Story | Bioarchaeological isotope-testing frame and mobility/origin discussion | Full Leach et al. text, DOI/page metadata, exact methodology, isotope values | Review cautious mobility wording; do not infer exact birthplace |
| 4 | African or North African ancestry/origin interpretation | partial_sources_attached | nearly_ready | Yorkshire Museum institutional interpretation; Our Migration Story; Leach et al. citation target | Interpretation discusses African / North African ancestry or origin possibilities using combined evidence | Exact Leach et al. full-text wording, DOI/page metadata, methodological cautions, any follow-up critique | Review with sensitive wording; avoid modern race certainty or exact birthplace claims |
| 5 | YORYM / accession verification | partial_sources_attached | not_ready | Yorkshire Museum institutional page; York Museums Trust catalogue search attempt | Museum display / custody context for skeleton and grave goods | `YORYM : 1996.115`, direct accession record, ADS / York Archaeology archive id, object-level catalogue page | Keep blocked; do not use candidate identifier in canonical data |
| 6 | "Vivas in Deo" / inscription / bone mount verification | partial_sources_attached | not_ready | Yorkshire Museum institutional page; Our Migration Story | English rendering "Hail, sister, may you live in God"; rectangular openwork bone mount; possible/probable box or casket context | Exact Latin text, RIB id, accession/object id, object-level catalogue, Leach et al. object table | Keep blocked for exact Latin/RIB/accession; use only cautious English rendering if later approved |
| 7 | Vale of York / Ouse-Foss / geology/hydrology verification | partial_sources_attached | nearly_ready for corrected BGS wording only | British Geological Survey institutional pages | Sherwood Sandstone Group, Mercia Mudstone Group, Quaternary glacial/glaciofluvial deposits, alluvium, river terrace deposits | City of York / Environment Agency hydrology quotes, BGS memoir/sheet reference, aquifer framing, unsupported fault/hydrology phrases | Promote only corrected BGS-supported geology wording in a separate operator-approved commit |
| 8 | Tier III speculative lens containment | speculative_lens_only | no Tier I path | None required; containment only | Speculative vocabulary identified and isolated | None for Tier I because promotion is forbidden | Preserve as Tier III only; do not promote or blend into Claims 1-7 |

## Corrected Canonical Candidate Wording

**Draft only - not promoted.**

The following wording is a cautious candidate for a future separate
operator-approved promotion commit. It must not be copied into canonical
ledgers until the operator completes an approval template and confirms the
target ledger.

> The Ivory Bangle Lady is a high-status late Roman burial from York /
> Eburacum, found in or near Sycamore Terrace in 1901 according to the
> current Yorkshire Museum and Our Migration Story source review. The
> Yorkshire Museum summary describes the burial as including jet and
> elephant ivory bracelets, earrings, pendants, beads, a blue glass jug
> and a glass mirror.
>
> Published and institutional interpretation discusses the individual in
> relation to bioarchaeological isotope testing and mobility/origin
> analysis. This does not prove an exact birthplace. Yorkshire Museum and
> Our Migration Story present a cautious African / North African ancestry
> or origin interpretation, but exact wording from Leach et al. must be
> reviewed before canonical promotion.
>
> Yorkshire Museum identifies a rectangular openwork bone mount from the
> burial and gives the English rendering "Hail, sister, may you live in
> God"; Our Migration Story similarly describes a bone mount probably
> once decorating a box. Exact Latin text, RIB id and object accession
> remain unresolved and must not be promoted.
>
> For landscape context, BGS-supported wording should refer to York
> within the Vale of York lowland, with Triassic Sherwood Sandstone Group
> bedrock overlain by Mercia Mudstone Group and Quaternary glacial /
> glaciofluvial cover including tills, sands, gravels, laminated
> lacustrine clays, alluvium and river terrace deposits.

Excluded from this draft:

- Vale of York Fault Flexures
- Howardian Hills Fault Margin
- Ouse-Foss fluvial siphon loop
- Vale of York Basin unless independently sourced as a formal
  institutional label
- subsurface aquifer saturated clays unless independently sourced
- exact `YORYM : 1996.115` accession unless verified
- exact Latin inscription unless verified

## Pre-Promotion Blockers

- Exact Leach et al. full-text wording / DOI / page metadata needed for
  Claim 4.
- `YORYM : 1996.115` remains unverified.
- Exact Latin / RIB ID unresolved for Claim 6.
- Object-level York Museums Trust catalogue record unresolved.
- ADS / York Archaeology archive identifiers unresolved.
- Unsupported geology / hydrology phrases must be removed or remain Tier
  III.
- Claim 8 must remain Tier III only.

## Tier III Containment

- Claim 8 is `speculative_lens_only`.
- `canonical_data_allowed: false`.
- `tier_i_promotion_allowed: false`.
- `promotion_path: none`.
- Claim 8 must not contaminate Claims 1-7.
- "Amenta Subsurface Core Extraction", "jet-ivory capacitors",
  "fluvial siphon loop", "counter-intelligence framing", and
  "system_lock" vocabulary remain non-canonical interpretive material
  only.

## Operator Decision Block

- final_decision: pending_operator_review
- approve_corrected_claims_for_promotion: false
- require_more_sources: true
- canonical_ingestion_allowed: false
- promotion_commit_allowed: false
- operator_signature:
- review_date:
