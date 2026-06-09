---
title: Gloucestershire Egyptian Intercept Source Review Worksheet
candidate_id: cand_gloucestershire_egypt_058
status: source_review_started
canonical_ingestion_allowed: false
raw_artifact: research/intake/gloucestershire_egypt_intercept_raw.md
review_note: research/intake/gloucestershire_egypt_intercept_review.md
ledger_entry: data/raw/black_albion_candidate_claims.json
date_started: 2026-06-09
reviewer: Claude Code (lightweight source discovery via WebSearch)
---

# Gloucestershire Egyptian Intercept — Source Review Worksheet

## Purpose

This worksheet runs item-level source review against the six candidate claims
itemised in `data/raw/black_albion_candidate_claims.json` for
`cand_gloucestershire_egypt_058`.

This is **source review only**. No canonical ledger is modified. Each Tier I
candidate claim is checked against publicly available institutional or
official sources; each finding is recorded as a candidate source URL, not as
a promoted fact. Tier III speculative material is preserved as labelled
speculative only.

## Promotion gate

Promotion blocked until every Tier I candidate claim is either:

- supported by a named, dated, reputable source record (institutional or
  official preferred); or
- rejected with a stated reason; and
- explicitly approved by the operator in a separate later commit.

No Tier III material is eligible for Tier I promotion under any circumstance.

---

### Claim 1 — 1801 Egypt campaign / Gloucestershire unit connection

- **claim_id**: `cand_claim_glos_egypt_001`
- **claim_text**: A Gloucestershire-raised unit took part in the 1801
  British campaign against Napoleonic forces in Egypt.
- **current_status**: supported
- **source_needed**: identification of the specific Gloucestershire-raised
  regiment that fought in the 1801 Egypt campaign and the dated engagement(s)
  in which it served.
- **candidate_sources_to_check**:
  - National Army Museum — 28th (North Gloucestershire) Regiment of Foot
    overview page: <https://www.nam.ac.uk/explore/28th-north-gloucestershire-regiment-foot>
  - Wikipedia — 28th (North Gloucestershire) Regiment of Foot:
    <https://en.wikipedia.org/wiki/28th_(North_Gloucestershire)_Regiment_of_Foot>
  - GCCC Heritage Trust — The History of Gloucestershire's Back Badge:
    <https://gcccheritagetrust.org/the-history-of-glucestershires-back-badge/>
  - Imperial War Museums — Gloucestershire Regiment back badge object record:
    <https://www.iwm.org.uk/collections/item/object/30076245>
  - National Army Museum — Gloucestershire Regiment cap badge object record:
    <https://collection.nam.ac.uk/detail.php?acc=2008-12-211-6>
- **evidence_found** (lightweight discovery only — to be confirmed against
  the named sources during a later verification pass):
  - Multiple institutional sources (National Army Museum, IWM, GCCC
    Heritage Trust) describe the 28th (North Gloucestershire) Regiment of
    Foot at the Battle of Alexandria, 21 March 1801, in which the regiment
    is reported to have stood back-to-back after being attacked from front
    and rear, earning a distinction worn on the back of the headdress.
  - The "back badge" distinction is reported by the GCCC Heritage Trust to
    have received formal approval in May 1830, with informal wear earlier.
  - The Sphinx / "EGYPT" device on the regiment's badge is reported as a
    distinction for service in Egypt 1801-2.
- **evidence_gap**:
  - Need to attach the primary regimental record (e.g. National Archives
    WO series despatch / general orders) and a dated regimental history page
    citation rather than relying on secondary summaries.
- **promotion_recommendation**: Tier I-candidate; promotion blocked until
  source-backed by a named primary or institutional record. Independent
  source hunting may proceed; do **not** write to
  `data/raw/black_albion_sites.json` or
  `data/raw/black_albion_claims.json` in this pass.
- **notes**: The pasted record framed the connection at the level of
  "Gloucestershire" generally. Any promoted Tier I claim must instead name
  the specific antecedent regiment (28th (North Gloucestershire) Regiment of
  Foot, later Gloucestershire Regiment) and the dated engagement.

---

### Claim 2 — Percival Marling VC / London Gazette citation

- **claim_id**: `cand_claim_glos_egypt_002`
- **claim_text**: Percival Marling received a Victoria Cross announced in
  the London Gazette in connection with the 1880s Sudan / Mahdist War.
- **current_status**: partially_supported
- **source_needed**: exact London Gazette issue number, date, and page for
  the Marling VC citation; confirmation of regimental affiliation at the
  time of the act; theatre and engagement.
- **candidate_sources_to_check**:
  - Wikipedia — Percival Marling:
    <https://en.wikipedia.org/wiki/Percival_Marling>
  - victoriacrossonline.co.uk — Sir Percival Scrope Marling VC CB DL:
    <https://victoriacrossonline.co.uk/sir-percival-scrope-marling-vc-cb-dl/>
  - memorialstovalour.co.uk — Sir Percival Scrope Marling:
    <http://www.memorialstovalour.co.uk/vc401.html>
  - britishempire.co.uk — Lieutenant Percival S Marling VC:
    <https://www.britishempire.co.uk/forces/armyunits/britishinfantry/krrcmarling.htm>
  - The National Archives Discovery — The Marling Family:
    <https://discovery.nationalarchives.gov.uk/details/r/a324c074-0013-4ff7-b8ee-9a870bc25354>
  - Wikipedia — Marling baronets:
    <https://en.wikipedia.org/wiki/Marling_baronets>
  - The London Gazette online archive (primary record, to be cited by issue
    and page once confirmed): <https://www.thegazette.co.uk/>
- **evidence_found** (lightweight discovery only):
  - Reported act: Battle of Tamai, Sudan, **13 March 1884** during the
    Mahdist War.
  - Reported gazette date: **21 May 1884**.
  - Reported regiment at the time of the act: **King's Royal Rifle Corps
    (KRRC)**, not a Gloucestershire regiment.
  - Reported Gloucestershire connection: **familial / county**, not
    regimental — Marling baronetcy of Stanley Park and Sedbury Park in the
    County of Gloucester (created 1882); Marling was later appointed Deputy
    Lieutenant of Gloucestershire (1903) and High Sheriff of Gloucestershire
    (1923).
- **evidence_gap**:
  - The pasted record framed Marling's VC as part of a "Gloucestershire /
    Egypt back-badge vector". On the evidence surfaced so far, the VC was
    earned with the KRRC, and the Gloucestershire connection is a baronetcy
    / county role, not regimental.
  - The exact London Gazette issue number and page for the citation is not
    yet attached.
- **promotion_recommendation**: Tier I-candidate; promotion blocked until
  the London Gazette citation is attached and the wording explicitly
  distinguishes the regimental affiliation (KRRC) from the Gloucestershire
  baronetcy / county role. Do not write to canonical ledgers.
- **notes**: Surface-level finding suggests a factual correction is required
  before any promotion: Marling was a KRRC officer at the time of the VC act
  and held a Gloucestershire baronetcy. Conflating those into a single
  "Gloucestershire regimental VC" statement would be a Tier I error.

---

### Claim 3 — Royal Gloucestershire Hussars WWI/WWII war diary references

- **claim_id**: `cand_claim_glos_egypt_003`
- **claim_text**: The 21st Royal Gloucestershire Hussars existed as a named
  formation with WWI mounted yeomanry and WWII Western Desert mechanised
  operational history.
- **current_status**: partially_supported (with naming correction)
- **source_needed**: confirmation of the regiment's exact title; named WWI
  and WWII campaign references; National Archives WO war diary catalogue
  reference numbers.
- **candidate_sources_to_check**:
  - Wikipedia — Royal Gloucestershire Hussars:
    <https://en.wikipedia.org/wiki/Royal_Gloucestershire_Hussars>
  - Soldiers of Gloucestershire Museum — Royal Gloucestershire Hussars
    history: <https://soldiersofglos.com/from-saddles-to-steel-the-legacy-of-the-royal-gloucestershire-hussars/>
  - Royal Wessex Yeomanry — Gloucestershire Yeomanry page:
    <https://www.wessexyeomanry.org/index.php/gloucestershire-yeomanry-2/>
  - The National Archives Discovery — Papers relating to the Royal
    Gloucestershire Hussars:
    <https://discovery.nationalarchives.gov.uk/details/r/7cb82d6b-edd8-4298-94c7-2aec01eb12f5>
  - The Long, Long Trail — Gloucestershire Yeomanry (Royal Gloucestershire
    Hussars):
    <https://www.longlongtrail.co.uk/army/regiments-and-corps/the-british-yeomanry-regiments-of-1914-1918/gloucestershire-yeomanry-royal-gloucestershire-hussars/>
  - Gloucestershire Archives catalogue — RGH papers:
    <https://catalogue.gloucestershire.gov.uk/records/D4920>
  - Internet Archive — Frank Fox, *The History of the Royal Gloucestershire
    Hussars Yeomanry 1898-1922*:
    <https://archive.org/details/r-gloucester-hussars-yeomanry>
- **evidence_found** (lightweight discovery only):
  - The regiment is reported as the **Royal Gloucestershire Hussars** (RGH),
    formed 1795 — the pasted record's "**21st** Royal Gloucestershire
    Hussars" prefix is **not corroborated** by the institutional sources
    above and appears to be incorrect.
  - WWI: reported deployment to Egypt as part of the Territorial Force; the
    first-line unit reported to have served as infantry at Gallipoli, and
    as cavalry in the Sinai and Palestine Campaign from the Suez Canal to
    Aleppo.
  - WWII: reported losses in Operation Crusader and the Battle of Gazala,
    use of Crusader / M3 Stuart / M3 Grant tanks, action at El Alamein,
    and later attachment of surviving squadrons to the 4th Hussars, 8th
    Hussars and Royal Wiltshire Yeomanry.
- **evidence_gap**:
  - Specific TNA WO war diary catalogue references not yet attached.
  - The "21st" prefix in the pasted record is not supported by any source
    surfaced so far and likely needs to be dropped before any promotion.
- **promotion_recommendation**: Tier I-candidate; promotion blocked until
  the correct regimental title is confirmed against primary sources and at
  least one named TNA war diary reference is attached. Do not promote with
  the "21st" prefix.
- **notes**: The pasted record's "21st Royal Gloucestershire Hussars"
  prefix is the most likely Tier I error in this batch. The RGH yeomanry
  designation should be used in any future promoted claim.

---

### Claim 4 — Gloucester Docks / Alexandria / Suez operational connection

- **claim_id**: `cand_claim_glos_egypt_004`
- **claim_text**: Gloucester Docks, Alexandria, and the Suez corridor were
  used by named Gloucestershire formations on dated operations.
- **current_status**: partially_supported
- **source_needed**: an institutional reference for "Gloucester Docks
  Repository" (likely the Soldiers of Gloucestershire Museum in the Custom
  House at Gloucester Docks); dated war diary entries naming Alexandria or
  the Suez corridor.
- **candidate_sources_to_check**:
  - Wikipedia — Soldiers of Gloucestershire Museum:
    <https://en.wikipedia.org/wiki/Soldiers_of_Gloucestershire_Museum>
  - Soldiers of Gloucestershire Museum (homepage):
    <https://soldiersofglos.com/>
  - Soldiers of Gloucestershire Museum — The Gloucestershire Regiment:
    <https://soldiersofglos.com/the-gloucestershire-regiment/>
  - Royal Gloucestershire Hussars Yeomanry Association — History page:
    <http://www.rghya.org.uk/history.html>
  - National Army Museum — 28th (North Gloucestershire) Regiment of Foot:
    <https://www.nam.ac.uk/explore/28th-north-gloucestershire-regiment-foot>
- **evidence_found** (lightweight discovery only):
  - "Gloucester Docks Repository" in the pasted record is plausibly a
    paraphrase of the **Soldiers of Gloucestershire Museum**, housed in the
    Custom House within the historic Gloucester Docks and reported to have
    previously served as the headquarters of the Gloucestershire Regiment.
  - Alexandria: connected by the 1801 Egypt campaign and the 28th (North
    Gloucestershire) Regiment of Foot — see Claim 1.
  - Suez corridor: connected by the WWI Sinai and Palestine campaign of
    the RGH (Suez Canal to Aleppo) — see Claim 3.
- **evidence_gap**:
  - "Gloucester Docks Repository" is not an institutional name used by the
    museum itself. Any promoted claim must name the museum directly.
  - Dated war-diary citations for Alexandria and Suez references not yet
    attached.
- **promotion_recommendation**: Tier I-candidate; promotion blocked until
  the museum is named correctly and dated war-diary citations are attached.
- **notes**: The geographic linkage between Gloucester Docks (museum),
  Alexandria (1801 campaign), and Suez (WWI Sinai/Palestine campaign) is
  plausible at the level of regimental history but must be sourced
  per-operation, not aggregated.

---

### Claim 5 — Cathedral memorial banners / museum archive references

- **claim_id**: `cand_claim_glos_egypt_005`
- **claim_text**: Memorial banners associated with a Gloucestershire
  regiment are stored in a cathedral vault.
- **current_status**: supported
- **source_needed**: a named cathedral, the location within the cathedral,
  and the regiment(s) whose colours are laid up there.
- **candidate_sources_to_check**:
  - Gloucester BID — Gloucestershire Regimental Colours at Gloucester
    Cathedral:
    <https://www.gloucesterbid.uk/news/gloucestershire-regimental-colours-at-gloucester-cathedral-celebrate-a-little-known-anniversary/>
  - Soldiers of Gloucestershire Museum — Presentation of New Colours 1976:
    <https://soldiersofglos.com/announcement/presentation-of-new-colours-1976/>
  - Soldiers of Gloucestershire Museum — Remembrance in Gloucestershire:
    <https://soldiersofglos.com/remembrance-in-gloucestershire-how-the-countys-regiments-shaped-britains-military-history/>
- **evidence_found** (lightweight discovery only):
  - Reported: two sets of Colours plus seven Standards laid up in
    **Gloucester Cathedral's North Ambulatory**, adjacent to the County War
    Memorial Chapel, attributed to the 28th and 61st Gloucestershire
    Regiments — described in the surfaced source as "believed to be the
    largest single concentration anywhere".
- **evidence_gap**:
  - The pasted record used the framing "memorial banners ... stored in a
    cathedral vault". Surfaced sources describe colours **laid up** in a
    public ambulatory, not stored in a vault. Any promoted Tier I claim
    must match the institutional language and location.
- **promotion_recommendation**: Tier I-candidate; promotion blocked until
  the cathedral location is named directly and the wording "laid up"
  replaces "stored in a vault" if the institutional source is correct.
- **notes**: This is the most cleanly supported Tier I-candidate item, but
  language fidelity matters before promotion.

---

### Claim 6 — Tier III speculative lens separation

- **claim_id**: `cand_claim_glos_egypt_006`
- **speculative_text**: Symbolic framing of a 'Back-Badge Sensory Vector',
  'Amenta Subsurface Core Extraction', and 'Trans-Continental Grid'
  counter-intelligence narrative.
- **current_status**: preserved_as_speculative_only
- **canonical_data_allowed**: false
- **allowed_location**: Tier III notes only, in an explicitly labelled Tier
  III block, walled off from any Tier I evidence per `docs/doctrine.md`.
- **promotion_recommendation**: do_not_promote_to_Tier_I
- **notes**: This material is an interpretive lens, not historical fact.
  Even if every Tier I-candidate claim above is fully sourced and promoted
  in a later pass, the Tier III framing here must continue to live in a
  separate, explicitly Tier III container and may not be presented as
  archival fact, geological fact, or institutional fact. The pasted record
  also bundled this Tier III language inside fields named
  `layer_0_geology`, `tier_i_enclosure_evidence`, and others — that
  bundling itself must not be carried into the canonical ledger; the Tier I
  block, if a record is ever created, must contain only sourced material.

---

## Summary Of This Pass

- 5 of 5 Tier I-candidate claims now have at least preliminary candidate
  sources identified.
- 2 of 5 Tier I-candidate claims required factual corrections to the pasted
  framing before any promotion would be safe:
  - Claim 2 — Marling's VC regimental affiliation is KRRC, not a
    Gloucestershire regiment.
  - Claim 3 — "21st" Royal Gloucestershire Hussars prefix is not
    corroborated; the correct designation is Royal Gloucestershire Hussars.
- 1 of 5 Tier I-candidate claims (Claim 5 — cathedral colours) requires a
  language correction from "stored in a vault" to "laid up" before
  promotion.
- 0 claims promoted. 0 canonical ledgers modified.
- Tier III speculative material remains explicitly Tier III; no Tier I
  promotion under any circumstance.

## Operator Approval Required For

- Each Tier I-candidate promotion (per-claim).
- Any consolidated record creation in `data/raw/black_albion_sites.json`
  that combines multiple verified items.
- Any direct quoting of institutional source pages into the live ledgers.

## Hard Rules Still In Force

- No write to `data/raw/black_albion_sites.json`.
- No write to `data/raw/black_albion_claims.json`.
- No write to `data/raw/black_albion_modules.json`.
- No write to `data/raw/black_albion_sources.json`.
- AI-generated text (this worksheet included) is not source authority and
  may not become Tier I on its own.
- Tier III material is never eligible for Tier I promotion.
