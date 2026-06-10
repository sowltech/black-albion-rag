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

#### Claim 1 — Source attachment pass (2026-06-09)

- **source_attachments**:
  - **National Army Museum — 28th (North Gloucestershire) Regiment of Foot**
    (<https://www.nam.ac.uk/explore/28th-north-gloucestershire-regiment-foot>).
    Institutional page. Quoted phrasing: the regiment "landed in Egypt in
    1801"; explicit reference to "The Battle of Alexandria, 1801" with the
    dated framing "Battle of Alexandria, 21 March 1801"; tactical
    description that the regiment "simultaneously beat off cavalry attacks
    on both sides of its line at Alexandria"; back-badge origin stated as
    "This feat earned the unit the distinction of wearing a cap badge on
    the front and the Egyptian sphinx on the back of its headdress". Page
    also records regimental lineage: raised 1694, designated 28th
    Regiment of Foot 1751, territorial association granted 1782, merged
    with the 61st (South Gloucestershire) Regiment of Foot in 1881 to
    form The Gloucestershire Regiment.
  - **Imperial War Museums — Gloucestershire Regiment back badge object
    record, IWM accession `INS 5713`**
    (<https://www.iwm.org.uk/collections/item/object/30076245>).
    Institutional object record. Quoted phrasing: badge commemorates
    "the Battle of Alexandria, 21 March 1801"; both parent regiments
    "had been awarded the Sphinx distinction for their service in Egypt
    in 1801-2"; inscriptions on the badge are "Egypt" and
    "Gloucestershire".
  - **Soldiers of Gloucestershire Museum — The Gloucestershire Regiment
    page** (<https://soldiersofglos.com/the-gloucestershire-regiment/>).
    Institutional museum page. Quoted phrasing: "an honour won by the
    28th Regiment when it fought in two ranks back to back at the Battle
    of Alexandria in 1801"; back-badge "unique privilege in the British
    Army of wearing a badge on the back of its headdress as well as the
    front"; tradition passed to The Rifles in 2007.
- **source_quality**: three independent institutional sources (NAM, IWM,
  Soldiers of Gloucestershire Museum). All three agree on the unit
  (28th (North Gloucestershire) Regiment of Foot), the date and place
  (Battle of Alexandria, 21 March 1801), and the back-badge origin. IWM
  object record provides a citeable accession number (`INS 5713`).
- **citation_notes**:
  - Cite the NAM page as the regimental-history overview.
  - Cite the IWM object record with the accession `INS 5713` for the
    badge artefact and the "Egypt" / "Gloucestershire" inscription.
  - Cite the Soldiers of Gloucestershire Museum page for the back-to-back
    formation phrasing and the back-badge inheritance through Glos Regt
    → RGBW → The Rifles.
  - Do not cite Wikipedia or the GCCC (cricket-club) Heritage Trust page
    as primary; the cricket-club page describes 2006 club adoption of
    the symbol, not the military origin.
- **remaining_gaps**:
  - No primary archival despatch or general-order has been attached
    (e.g. The National Archives WO 1 / WO 28 series or General Orders
    of 1801) — institutional sources are sufficient for the candidate
    claim but the operator may want a TNA reference before any Tier I
    promotion.
  - The formal-approval year for the back-badge as a War Office
    distinction is not fixed by a single sourced statement here; the
    institutional consensus is that the distinction post-dates Alexandria
    and was later regularised, but a precise War Office order reference
    is still required if that level of detail is promoted.
- **promotion_readiness**: nearly_ready. Three institutional sources
  align on the core facts (unit, date, place, back-badge origin) and
  one provides a citeable artefact accession. Operator approval still
  required, and a TNA primary-source citation would tighten the case
  before any Tier I write.

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

#### Claim 2 — Source attachment pass (2026-06-09)

- **source_attachments**:
  - **The London Gazette — Issue `25356`, page `2278`, published
    21 May 1884**
    (<https://www.thegazette.co.uk/London/issue/25356/page/2278>).
    Primary state-published record. Confirmed by direct The Gazette
    notice-search lookup against the 21 May 1884 publication date.
    The Gazette notice-search excerpt for this page returns text
    matching the recognised Marling VC citation, including the
    fragment "Morley, Royal Sussex Regiment, who, having been shot,
    was lifted and placed in front of Lieutenant Marling on his
    horse." The full notice body sits in The Gazette's PDF/image
    layer rather than the HTML; operator approval is recommended
    before quoting the full citation text in any canonical ledger.
  - **britishempire.co.uk — Lieutenant Percival S Marling VC, King's
    Royal Rifle Corps**
    (<https://www.britishempire.co.uk/forces/armyunits/britishinfantry/krrcmarling.htm>).
    Reputable secondary regimental-history source. Quoted phrasing:
    VC action "13th March 1884" at "the battle of Tamai in the
    Sudan"; regiment "3rd Battalion King's Royal Rifle Corps"; life
    dates born "6th Mar 1861", died "29th May 1936"; Gloucestershire
    connection: born "at King's Stanley, Stroud in Gloucestershire",
    later "appointed High Sheriff of The County of Gloucester in
    1928", died "at Stanley Park, Stroud".
  - **victoriacross.org.uk — KRRC Victoria Cross page**
    (<http://www.victoriacross.org.uk/cckrrc.htm>). Reputable VC roll
    source. Records Marling as "Colonel Sir Percival Scrope Marling
    Bt, VC CB", regiment "60th Rifles (King's Royal Rifle Corps)",
    and identifies the medal as held at the "Lord Ashcroft Gallery,
    Imperial War Museum".
  - **Victoria Cross and George Cross Association — Percival Scrope
    Marling profile**
    (<https://vcgca.org/our-people/profile/1264/Percival-Scrope-MARLING>).
    Institutional VC association roll entry confirming identity and
    VC status; biographical fields not extracted in this pass.
- **source_quality**: one primary record (The London Gazette issue
  `25356`, page `2278`, 21 May 1884), one reputable regimental-history
  page (britishempire.co.uk) with the dated action and regiment, one
  VC-roll source (victoriacross.org.uk) corroborating the KRRC
  affiliation under its historical "60th Rifles" name, and one
  institutional VC-association entry. Together these are sufficient to
  pin: date of action (13 March 1884), place (Battle of Tamai, Sudan),
  Marling's regiment (King's Royal Rifle Corps / 3rd Battalion / "60th
  Rifles"), Gazette issue and page (25356 / 2278 / 21 May 1884), and
  the saved soldier (Private Morley, Royal Sussex Regiment).
- **correction_notes**:
  - The pasted record framed the Marling VC as a Gloucestershire
    regimental honour. **The corrected position is that Marling was a
    King's Royal Rifle Corps officer at the time of the VC act.**
    Any Gloucestershire connection is **familial / territorial** —
    Marling baronetcy of Stanley Park and Sedbury Park in the County
    of Gloucester, plus Deputy Lieutenant / High Sheriff roles for
    the county — not regimental.
  - The pasted record dated the event as "1884 CE Mahdist War Phase"
    in a broad way. The dated action is **13 March 1884 at the Battle
    of Tamai, Sudan**, with the **London Gazette citation published
    21 May 1884 (Issue 25356, page 2278)**.
  - The soldier saved by Marling was **Private Morley, Royal Sussex
    Regiment**, not a Gloucestershire soldier.
- **citation_notes**:
  - Cite The London Gazette **issue 25356, page 2278, 21 May 1884**
    as the primary record. Direct quotation of the citation text into
    any canonical ledger should be confirmed against the Gazette PDF
    image rather than the HTML notice excerpt.
  - Cite the britishempire.co.uk page as a reputable regimental-history
    secondary source for the dated action, place, regiment, and life
    dates.
  - Cite victoriacross.org.uk as the VC-roll source identifying the
    regiment as "60th Rifles (King's Royal Rifle Corps)".
  - Cite the VCGCA institutional roll entry for VC status confirmation.
  - **Do not** cite Wikipedia as primary.
  - **Do not** treat the pasted record's framing as historical
    authority — it must be rewritten before any Tier I promotion.
- **remaining_gaps**:
  - The full verbatim VC citation text is in The Gazette page
    `25356/2278` PDF/image layer; only a search-snippet fragment was
    confirmable in this pass. Operator approval should follow a fetch
    of the PDF if the verbatim citation is to be quoted in any
    canonical ledger.
  - A minor sub-fact discrepancy on the date of Marling's High
    Sheriff appointment for Gloucestershire was surfaced across
    sources: the British Empire page gives "1928" while an earlier
    Wikipedia-derived summary surfaced in the prior review pass gave
    "1923". This sub-fact is not load-bearing for the VC claim but
    must be resolved against a primary source (e.g. London Gazette
    appointment notice) before any Gloucestershire-county Tier I
    statement quotes a specific year.
  - The exact battalion identifier ("3rd Battalion King's Royal Rifle
    Corps") is confirmed only by the britishempire.co.uk page; cross
    confirmation from a regimental archive (Royal Green Jackets
    Museum or equivalent) would tighten the case.
  - No National Archives WO-series catalogue reference attached.
- **original_claim_status**: requires_correction
- **corrected_claim_text** (draft only; not promoted; for operator
  review only):
  > "Lieutenant Percival Scrope Marling, 3rd Battalion King's Royal
  > Rifle Corps, was awarded the Victoria Cross for an act on
  > 13 March 1884 at the Battle of Tamai (Sudan) during the Mahdist
  > War. The award was gazetted in The London Gazette of 21 May 1884
  > (Issue 25356, page 2278). The Gloucestershire connection is
  > territorial / familial (Marling baronetcy of Stanley Park and
  > Sedbury Park in the County of Gloucester; later Deputy Lieutenant
  > and High Sheriff of Gloucestershire), not regimental."
- **promotion_readiness**: nearly_ready (subject to operator-approved
  rewrite of the original claim text to the corrected version above
  and operator-led confirmation of the Gazette PDF citation text).

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

#### Claim 3 — Source attachment pass (2026-06-10)

- **source_attachments**:
  - **Soldiers of Gloucestershire Museum — From Saddles to Steel:
    The Legacy of the Royal Gloucestershire Hussars**
    (<https://soldiersofglos.com/from-saddles-to-steel-the-legacy-of-the-royal-gloucestershire-hussars/>).
    Institutional museum page. Uses the title **"Royal Gloucestershire
    Hussars (RGH)"** consistently; no "21st" prefix anywhere on the
    page. Formation year **1795**. WWI: "deployed to Egypt"; Sinai and
    Palestine campaigns including "Gaza", "Beersheba", "Jerusalem".
    WWII: regiment served under "the 8th Army" in the "Western Desert
    Campaign"; tank types named — "Crusader tanks" and "Sherman tanks";
    "Operation Crusader" and "El Alamein" referenced. Post-war: "In
    1967, they became part of the Royal Wessex Yeomanry". Museum
    location: "Soldiers of Gloucestershire Museum" in "Gloucester
    Docks"; "Crusader tank 'Gypsy'" described as "striking centrepiece".
  - **Royal Wessex Yeomanry — Gloucestershire Yeomanry / RGH page**
    (<https://www.wessexyeomanry.org/index.php/gloucestershire-yeomanry-2/>).
    Institutional parent-regiment page. Uses the title **"Royal
    Gloucestershire Hussars"** with no "21st" prefix; records that
    "Queen Victoria granted the Regiment the title of 'Royal' in 1841"
    and the unit "was restyled the Royal Gloucestershire Hussars in
    1847". Formation: the "first Troop ... was raised in Cheltenham" in
    1795; troops amalgamated 1834. WWI: "mobilised in August 1914",
    deployed to "Alexandria in 1915", landed at "Gallipoli to operate
    as Infantry"; "suffered losses at Katia in the Sinai Desert" and
    fought at the "Battle of Romani"; subsequently a "key element in
    the subsequent advance on Jerusalem, Damascus and Aleppo";
    returned to UK August 1919. WWII: "2RGH deployed to Libya in 1941
    as part of the 7th Armoured Division"; crewed "Crusader tanks" at
    Bir El Gubi (November 1941); "re-equipped with Grant and Stuart
    tanks in early 1942" and fought at the "Battle of Gazala" and
    "Battle of El Alamein". Modern role: continues today as "C (RGH)
    Squadron" within the Royal Wessex Yeomanry (formed 1971 per this
    page).
  - **The Long, Long Trail — Gloucestershire Yeomanry (Royal
    Gloucestershire Hussars)**
    (<https://www.longlongtrail.co.uk/army/regiments-and-corps/the-british-yeomanry-regiments-of-1914-1918/gloucestershire-yeomanry-royal-gloucestershire-hussars/>).
    Reputable WWI orbat reference. Uses the title **"Gloucestershire
    Yeomanry (Royal Gloucestershire Hussars)"** with no "21st" prefix.
    Records the 1/1st Battalion formation moves through "1st South
    Midland Mounted Brigade", "1st Mounted Division", "5th Mounted
    Brigade" (January 1916), "Imperial Mounted Division" (February
    1917), "Australian Mounted Division" (June 1917), and "13th Cavalry
    Brigade" within "5th Cavalry Division" (August 1918). Deployment
    chronology: "moved to Egypt, arriving Alexandria 24 April" (1915);
    "landed at Gallipoli ... on 18 August" (1915); named WWI
    engagement quoted is the "attack on Chocolate Hill and Hill 112 on
    21 August".
  - **The National Archives — Discovery catalogue entry: Papers
    relating to the Royal Goucestershire Hussars**
    (<https://discovery.nationalarchives.gov.uk/details/r/7cb82d6b-edd8-4298-94c7-2aec01eb12f5>).
    Listed as a candidate primary-source pointer. Page body was not
    extractable on direct fetch in this pass; attached here as a
    candidate TNA reference for a later operator-led primary-source
    confirmation, not as a quoted source.
- **source_quality**: three institutional or reputable sources (Soldiers
  of Gloucestershire Museum, Royal Wessex Yeomanry, The Long Long Trail)
  all use the title **"Royal Gloucestershire Hussars"** (or
  "Gloucestershire Yeomanry (Royal Gloucestershire Hussars)") with no
  "21st" prefix. Together they corroborate WWI deployment to Egypt and
  Gallipoli (1915), Sinai/Palestine operations including Katia, Romani,
  Gaza, Beersheba, and the advance on Jerusalem, Damascus and Aleppo;
  WWII service in the Western Desert / Libya as part of the 7th
  Armoured Division, with named engagements at Bir El Gubi, Gazala and
  El Alamein, and named tank types Crusader, Grant, Stuart, Sherman.
  TNA Discovery candidate reference attached for later primary-source
  confirmation.
- **correction_notes**:
  - **"21st" prefix is unsupported** by any of the three institutional
    or reputable sources surfaced in this pass. The pasted record's
    "21st Royal Gloucestershire Hussars" wording must be dropped before
    any Tier I promotion.
  - The institutional title is **Royal Gloucestershire Hussars** (RGH),
    and the WWI-era orbat name is **Gloucestershire Yeomanry (Royal
    Gloucestershire Hussars)**. The The Long Long Trail page records the
    unit number as the **1/1st Battalion** (with separate 2/1st and 3/1st
    second-line battalions), which is the only numbering that any source
    attached here uses for the WWI regiment.
  - Sub-fact discrepancy: the Soldiers of Gloucestershire Museum page
    gives **1967** for the merger into the Royal Wessex Yeomanry, while
    the RWY page gives **1971** for the formation of the RWY. Both years
    can be true (the RGH may have first amalgamated into a predecessor
    unit in 1967 and then into the RWY in 1971), but the year(s)
    surfaced here are not load-bearing for the WWI/WWII campaign claims
    and must be resolved against an institutional source before any
    post-war year is promoted.
- **citation_notes**:
  - Cite the Soldiers of Gloucestershire Museum RGH page as the
    institutional museum source for the consistent title, formation
    year, and the named WWII tank types / campaign anchors.
  - Cite the Royal Wessex Yeomanry RGH page as the institutional
    parent-regiment source for the title-grant chronology (1841, 1847),
    the WWI Sinai/Palestine engagement names (Katia, Romani, advance on
    Jerusalem/Damascus/Aleppo), and the WWII 7th Armoured Division /
    Bir El Gubi / Crusader / Grant / Stuart / Gazala / El Alamein
    chronology.
  - Cite The Long Long Trail RGH page as the WWI orbat / brigade and
    division assignments reference, and for the dated arrival at
    Alexandria (24 April 1915) and Gallipoli (18 August 1915).
  - Add The National Archives Discovery catalogue entry as a candidate
    primary-source pointer; do not quote text from it until the page
    body is confirmable on a later fetch.
  - Do not cite Wikipedia as primary.
- **remaining_gaps**:
  - No directly attached National Archives WO-series war-diary catalogue
    reference number; the TNA Discovery entry is attached as a candidate
    pointer but the page body was not extractable on direct fetch in
    this pass.
  - The post-war merger year (RGH into a Royal Wessex Yeomanry
    predecessor / the RWY itself) shows a 1967 vs 1971 discrepancy
    across the two institutional sources surfaced here and would need
    a precise institutional date before being promoted.
  - The Imperial War Museums collection has not been queried directly
    for an RGH war-diary or photograph object record in this pass; a
    later pass could attach an IWM accession for a specific item
    (similar to the IWM `INS 5713` reference attached for Claim 1).
- **original_claim_status**: requires_correction
- **corrected_claim_text** (draft only; not promoted; for operator
  review only):
  > "The Royal Gloucestershire Hussars (RGH), a Gloucestershire-raised
  > yeomanry regiment formed in 1795 and granted the 'Royal' title in
  > 1841, served in the First World War as the 1/1st Battalion
  > Gloucestershire Yeomanry (Royal Gloucestershire Hussars), arriving
  > at Alexandria on 24 April 1915, landing at Gallipoli on 18 August
  > 1915 to operate as infantry, and subsequently fighting in the
  > Sinai and Palestine campaigns at named engagements including
  > Katia, Romani, Gaza, Beersheba, and the advance on Jerusalem,
  > Damascus and Aleppo, before returning to the UK in August 1919.
  > In the Second World War, the 2nd Royal Gloucestershire Hussars
  > deployed to Libya in 1941 as part of the 7th Armoured Division
  > and fought in the Western Desert campaign at Bir El Gubi in
  > November 1941, the Battle of Gazala in 1942, and the Battle of
  > El Alamein, crewing Crusader, M3 Grant, M3 Stuart and Sherman
  > tanks. The regiment continues today as C (RGH) Squadron within
  > the Royal Wessex Yeomanry. There is no contemporary or
  > institutional source for a '21st Royal Gloucestershire Hussars'
  > designation; that prefix from the original intake must be
  > dropped."
- **promotion_readiness**: nearly_ready for the **WWI deployment dates
  and Gallipoli/Sinai/Palestine campaign chronology** and for the
  **WWII Western Desert / 7th Armoured Division / Bir El Gubi /
  Gazala / El Alamein / Crusader-Grant-Stuart-Sherman** chronology
  (subject to operator-approved rewrite to the corrected version above).
  not_ready for any statement that relies on the "21st" prefix or on
  a specific TNA war-diary catalogue reference until a primary TNA
  reference is attached.

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

#### Claim 5 — Source attachment pass (2026-06-09)

- **source_attachments**:
  - **Soldiers of Gloucestershire Museum — Presentation of New Colours
    1976 announcement**
    (<https://soldiersofglos.com/announcement/presentation-of-new-colours-1976/>).
    Institutional museum source. Records that on Sunday 25 April 1976
    the old Colours of the 1st Battalion The Gloucestershire Regiment
    were "laid up in Gloucester Cathedral" and placed "on the Altar",
    and that the new Colours were presented on 26 April 1976 in
    Gloucester Park. Quoted phrasing: "These consecrated Colours,
    formerly carried on the service of the Queen and Commonwealth, I
    now deliver into your hands for safe custody". Confirms the
    institutional vocabulary "laid up" rather than "stored in a vault".
  - **National Army Museum — 28th (North Gloucestershire) Regiment of
    Foot** (<https://www.nam.ac.uk/explore/28th-north-gloucestershire-regiment-foot>)
    and **Imperial War Museums — Gloucestershire Regiment back badge,
    accession `INS 5713`**
    (<https://www.iwm.org.uk/collections/item/object/30076245>).
    Institutional context for the regiments (28th and 61st of Foot,
    later Gloucestershire Regiment) whose Colours are laid up at
    Gloucester Cathedral.
- **source_quality**: one direct institutional source (Soldiers of
  Gloucestershire Museum) provides the "laid up" language and a dated
  1976 ceremony at Gloucester Cathedral; supporting institutional
  context from NAM and IWM. A Gloucester Cathedral page or Cathedral
  guidebook describing the precise location of the laid-up Colours
  (e.g. North Ambulatory / St Edmund's Chapel) was not directly
  attached in this pass and remains a remaining gap.
- **citation_notes**:
  - Cite the Soldiers of Gloucestershire Museum 1976 announcement as
    the institutional source for the "laid up" language and a dated
    cathedral ceremony.
  - When the cathedral page can be attached, cite Gloucester Cathedral
    directly for the location within the building (the precise chapel
    / ambulatory) rather than relying on a paraphrase.
  - Do not cite Wikipedia as primary.
  - Do not cite the pasted record's "stored in a vault" language; use
    the institutional "laid up" wording.
- **remaining_gaps**:
  - No directly attached Gloucester Cathedral institutional page for
    the precise location of the laid-up Colours within the cathedral
    (e.g. North Ambulatory / St Edmund's Chapel / County War Memorial
    Chapel). One previously surfaced URL (Gloucester BID) returned
    HTTP 404 on direct fetch in this pass and is therefore not
    attached.
  - No directly attached primary source for the claim that the
    Gloucester Cathedral concentration is "the largest single
    concentration anywhere"; that phrasing was paraphrased in earlier
    discovery and is excluded from this pass until a direct
    institutional source is attached.
- **promotion_readiness**: nearly_ready. The "laid up" language is now
  source-backed against an institutional museum announcement with a
  dated ceremony. Cathedral-side location precision (chapel /
  ambulatory) is still missing. Operator approval still required, and
  the Cathedral institutional source is the recommended next attach.

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

## Source Attachment Pass — 2026-06-09

- Targeted attachment pass on the two cleanest candidates per operator
  instruction: Claim 1 and Claim 5.
- Claim 1 — three institutional sources attached (NAM regimental page,
  IWM object record `INS 5713`, Soldiers of Gloucestershire Museum
  regimental page). Promotion readiness: **nearly_ready**. Remaining
  gap: a TNA primary-source despatch / general-order reference would
  tighten the case if the operator chooses to demand primary-source
  citation before any Tier I write.
- Claim 5 — one direct institutional source attached (Soldiers of
  Gloucestershire Museum 1976 New Colours announcement) confirming
  the institutional "laid up" vocabulary and a dated cathedral
  ceremony (25 April 1976). Promotion readiness: **nearly_ready**.
  Remaining gap: a Gloucester Cathedral institutional page giving the
  precise location of the laid-up Colours (chapel / ambulatory).
- Claims 2, 3, 4, 6 — not touched in this attachment pass; their
  statuses remain as set in the original review pass above.
- Canonical ledgers (`data/raw/black_albion_sites.json`,
  `data/raw/black_albion_claims.json`,
  `data/raw/black_albion_modules.json`,
  `data/raw/black_albion_sources.json`) — unchanged.

## Source Attachment Pass — 2026-06-09 (Claim 2)

- Targeted attachment pass on Claim 2 (Percival Marling VC / London
  Gazette citation) per operator instruction.
- Primary state-published record attached: **The London Gazette,
  Issue `25356`, page `2278`, published 21 May 1884**, identified by
  direct The Gazette notice-search lookup against the 21 May 1884
  publication date. The Gazette HTML notice excerpt contains the
  recognised Marling VC citation fragment matching the historical
  record. Verbatim citation text sits in the Gazette PDF/image layer
  and is not auto-quoted into the worksheet; operator approval is
  recommended before any verbatim Tier I quotation.
- Three reputable secondary sources attached for regiment, date,
  place, life dates, and territorial / familial Gloucestershire
  connection (britishempire.co.uk KRRC page, victoriacross.org.uk
  KRRC roll, VCGCA roll profile).
- **Correction confirmed**: Marling was a King's Royal Rifle Corps
  officer at the time of the VC act (3rd Battalion KRRC / historical
  "60th Rifles"). The Gloucestershire connection is **territorial /
  familial** (Marling baronetcy of Stanley Park and Sedbury Park in
  the County of Gloucester; later Deputy Lieutenant and High Sheriff
  of Gloucestershire), not regimental.
- **original_claim_status**: requires_correction. A
  `corrected_claim_text` draft has been recorded in the Claim 2
  section above as operator-review material only.
- Promotion readiness: **nearly_ready** (subject to operator-approved
  rewrite of the original claim text to the corrected version and a
  Gazette PDF confirmation of the verbatim citation text).
- Claims 1, 3, 4, 5, 6 — not touched in this pass; their statuses
  remain as set in the previous passes above.
- Canonical ledgers (`data/raw/black_albion_sites.json`,
  `data/raw/black_albion_claims.json`,
  `data/raw/black_albion_modules.json`,
  `data/raw/black_albion_sources.json`) — unchanged.

## Source Attachment Pass — 2026-06-10 (Claim 3)

- Targeted attachment pass on Claim 3 (Royal Gloucestershire Hussars
  WWI / WWII references) per operator instruction.
- Three institutional or reputable sources attached: Soldiers of
  Gloucestershire Museum RGH page (museum, Gloucester Docks); Royal
  Wessex Yeomanry RGH page (parent regiment); The Long Long Trail RGH
  WWI orbat page. The National Archives Discovery RGH papers entry
  attached as a candidate primary-source pointer only.
- **Correction confirmed**: the "21st" prefix in the pasted record
  is **not corroborated by any institutional or reputable source**
  surfaced in this pass. The institutional title is **Royal
  Gloucestershire Hussars** (RGH); the WWI orbat name is
  **Gloucestershire Yeomanry (Royal Gloucestershire Hussars)**, with
  the unit recorded as the **1/1st Battalion** (alongside 2/1st and
  3/1st second-line battalions).
- WWI service supported: Alexandria 24 April 1915; Gallipoli landing
  18 August 1915; Sinai (Katia); Palestine (Romani, Gaza, Beersheba,
  advance on Jerusalem / Damascus / Aleppo); return to UK August 1919.
- WWII service supported: 2RGH in Libya 1941 as part of the 7th
  Armoured Division; Bir El Gubi November 1941; re-equipped with M3
  Grant and M3 Stuart tanks in early 1942; Battle of Gazala (1942);
  Battle of El Alamein; Crusader and Sherman tanks named.
- **original_claim_status**: requires_correction. A
  `corrected_claim_text` draft has been recorded in the Claim 3
  section above as operator-review material only and explicitly
  drops the "21st" prefix.
- Promotion readiness: **nearly_ready** for the WWI deployment dates,
  Sinai/Palestine campaign chronology and WWII Western Desert /
  Bir El Gubi / Gazala / El Alamein / Crusader-Grant-Stuart-Sherman
  chronology (subject to operator-approved rewrite to the corrected
  version and operator approval). **not_ready** for any statement
  that relies on the "21st" prefix or on a specific TNA war-diary
  catalogue reference until a primary TNA reference is attached.
- Sub-fact note: the post-war merger year of the RGH into the Royal
  Wessex Yeomanry shows a 1967 vs 1971 discrepancy across the two
  institutional sources surfaced; not load-bearing for the WWI/WWII
  campaign claims but must be resolved against an institutional
  source before any post-war year is promoted.
- Claims 1, 2, 4, 5, 6 — not touched in this pass; their statuses
  remain as set in the previous passes above.
- Canonical ledgers (`data/raw/black_albion_sites.json`,
  `data/raw/black_albion_claims.json`,
  `data/raw/black_albion_modules.json`,
  `data/raw/black_albion_sources.json`) — unchanged.

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
