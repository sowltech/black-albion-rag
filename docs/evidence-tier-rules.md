# Evidence Tier Rules

Black Albion RAG separates evidence from interpretation and speculation at
storage, retrieval, prompt, and answer time.

## Tier I: Verified / Source-Backed Evidence

Tier I is for archaeological, geological, hydrological, archival, statutory,
cartographic, and documentary evidence. A Tier I claim is only strong when the
record includes sources. If the current ledger names a place or feature without
attached source records, mark it as `source_status: needs_verification`.

Safe wording:

- "The module inventory includes Tewkesbury Abbey and Severn Ham; source records
  still need to be attached."
- "The local corpus currently marks this claim as needing verification."
- "This is a Tier I evidence slot, not yet a fully sourced claim."

Unsafe wording:

- "This proves the site was used for..."
- "Historic England confirms..." unless that specific source is in the record.
- "The coordinates are..." unless coordinates are present and verified.

## Tier II: Interpretation / Analysis

Tier II is for scholarly or operator landscape interpretation built on Tier I
evidence. It can discuss route logic, enclosure logic, frontier analysis, and
regional patterning, but must not pretend to be direct evidence.

Safe wording:

- "As an interpretive landscape reading, the Severn Ham module functions as a
  confluence and floodplain node."
- "This is analysis, not a primary historical claim."

Unsafe wording:

- "The ancient builders intended this corridor to..."
- "The frontier system was deliberately designed as..." without a source.

## Tier III: Speculative / Mythic / Creative Layer

Tier III is for symbolic, mythic, esoteric, creative-worldbuilding, and
geomythological readings. It must always be labelled as speculative. Tier III is
never verified history, archaeology, geology, hydrology, or science.

Safe wording:

- "Speculatively, the module can be read as a symbolic river-gate."
- "In the creative layer, the Forest of Dean scowles may function as an
  underworld threshold motif."

Unsafe wording:

- "The caves were built as an underworld system."
- "The river-gate proves an ancient control grid existed."
- "The symbolic reading is the hidden factual history."

## Response Rules

1. Start with the evidence mode where useful:
   - Tier I: verified / source-backed evidence.
   - Tier II: interpretation / analysis.
   - Tier III: speculative / mythic / creative layer.
2. Use Tier I for factual claims only when sources exist.
3. Mark unsourced Tier I records as needing verification.
4. Prefix Tier II with interpretive language.
5. Prefix Tier III with speculative language.
6. Do not invent citations, NHLE numbers, excavation dates, coordinates, or
   archival references.
7. If evidence is thin, say so plainly.
8. If the user asks for "ancient secrets", return:
   - plain historical summary;
   - sites and periods;
   - landscape logic;
   - evidence confidence;
   - optional Tier III symbolic reading, clearly labelled.
9. If the user asks for RAG/build/data status, return:
   - files changed;
   - data records added;
   - validation run;
   - tests passed;
   - unresolved source gaps.
