# Black Albion Module Expansion

This document records the expanded regional module layer added to the local
Black Albion RAG system.

The new module data lives in `data/raw/black_albion_modules.json`. Each module
keeps Tier I, Tier II, and Tier III fields separate. Tier I inventory claims are
upgraded only when source records are attached. If a source supports only part
of a module inventory, the claim remains `partial`.

## Module Table

| Module ID | Site ID | Region | Main sites | Tier I summary | Tier II summary | Tier III status | Source gaps |
|---|---|---|---|---|---|---|---|
| UK-RAG-MOD-043 | site_southwestern_mercian_border_matrix | Severn-Avon-Bath frontier | Avon Gorge; Bristol/Hotwells; Bath; Mendip geothermal circuit | Inventory added; source-backed detail required. | Southwestern Mercian/Hwicce frontier, thermal, river, and limestone analysis. | Speculative thermal gate reading only. | Hwicce frontier, Bath hydrothermal, Mendip circuit sources. |
| UK-RAG-MOD-044 | site_cotswold_way_jurassic_escarpment_ridge_line | Cotswold escarpment spine | Chipping Campden; Cotswold Way; Belas Knap; Bath | Inventory added; source-backed detail required. | Ridge-line route linking Jurassic escarpment, monuments, Severn edges, and Bath. | Speculative limestone spine reading only. | Route, geology, Belas Knap, Bath terminal sources. |
| UK-RAG-MOD-045 | site_severn_ham_alluvial_convergence | Tewkesbury river confluence | Severn Ham; Avon-Severn confluence; Healings Mill; Abbey Mill | Inventory added; source-backed detail required. | Floodplain/common-land/SSSI and mill-confluence analysis. | Speculative river-gate reading only. | SSSI/common land, mills, floodplain records. |
| UK-RAG-MOD-046 | site_stroud_frome_valley_radials | Stroud valleys and Cotswold scarp | Woodchester; Orpheus Mosaic; Uley Bury; West Hill; Nympsfield; Painswick | Inventory added; source-backed detail required. | Valley radial reading across villas, temples, long barrows, and hillforts. | Speculative ritual-route spokes only. | Monument, villa, temple, hillfort, and valley sources. |
| UK-RAG-MOD-047 | site_trans_severn_frontier_forest_of_dean_karst_scowles | Forest of Dean and Wye/Severn edge | Lydney Park; Clearwell Caves; Puzzlewood; Highnam; Ross-on-Wye; Lady's Well | Inventory added; source-backed detail required. | Karst, mining, Roman cult, and trans-Severn frontier analysis. | Speculative underworld/threshold reading only. | Temple, cave, hoard, mining, Wye-edge sources. |
| UK-RAG-MOD-048 | site_mercian_lattice_central_sandstone_cavity_complex | West Midlands to central cave corridor | Metchley; Staffordshire Hoard; Wren's Nest; Kinver; Wroxeter; Old Oswestry; Creswell; Nottingham caves | Inventory added; source-backed detail required. | Central Mercian lattice of forts, hoard, caves, hillforts, and sandstone dwellings. | Speculative central lattice reading only. | Site-by-site archaeology/geology sources. |
| UK-RAG-MOD-049 | site_tamensis_basin_upper_cretaceous_chalk_corridors | Thames basin and chalk corridors | Londinium; Walbrook; Mithraeum; Oxford; Port Meadow; Ridgeway; Wayland's Smithy; Uffington | Inventory added; source-backed detail required. | Thames/chalk corridor between city, meadow, and Ridgeway monuments. | Speculative chalk-water corridor reading only. | Roman London, Oxford, Ridgeway, chalk, floodplain sources. |
| UK-RAG-MOD-050 | site_fenland_basin_east_anglian_chalk_escarpments | Fenland and East Anglian chalk edge | Ely; Peterborough; Car Dyke; Fen-edge villas; timber settlements; Devil's Dyke; Bedford Level | Inventory added; source-backed detail required. | Water-management/enclosure basin linking Roman engineering, wetland archaeology, and drainage. | Speculative drained-water-archive reading only. | Fen drainage, Car Dyke, villa, dyke, wetland settlement sources. |
| UK-RAG-MOD-051 | site_north_wessex_chalk_gateway_ridgeway_corridor | North Wessex Downs and Ridgeway | Swindon; Barbury; Liddington; Wanborough; Coate Water; Avebury; Silbury; West Kennet | Inventory added; source-backed detail required. | Chalk gateway linking Ridgeway, hillforts, Roman roadside settlement, and monuments. | Speculative chalk gateway reading only. | Hillfort, Wanborough, Avebury/Silbury, Coate Water sources. |
| UK-RAG-MOD-052 | site_corinium_dobunnorum_palimpsest | Cirencester and upper Thames/Cotswold basin | Corinium; Bagendon; Chedworth; amphitheatre; Roman walls; Rodmarton; Cirencester Abbey | Inventory added; source-backed detail required. | Dobunnic/Roman/prehistoric/medieval palimpsest analysis. | Speculative memory-node reading only. | Corinium, Bagendon, villa, mutatio, abbey, church sources. |
| UK-RAG-MOD-053A | site_tewkesbury_severn_avon_river_gate | Tewkesbury and lower Avon-Severn crossing | Tewkesbury; Oldbury; Abbey; Severn Ham; Bloody Meadow; Deerhurst; Bredon Hill | Inventory added; source-backed detail required. | River-gate convergence of confluence, battlefield, monastic, and settlement layers. | Speculative threshold-node reading only. | Battlefield, abbey, chapel, Roman settlement, floodplain sources. |
| UK-RAG-MOD-053B | site_hereford_western_marches_corridor | Herefordshire and western marches | Cathedral; Mappa Mundi; Wye crossing; Rotherwas; Dinedor; Sutton Walls; Kenchester; Arthur's Stone | Inventory added; source-backed detail required. | Western marches corridor linking archive, river crossing, Roman town, monuments, and castles. | Speculative memory-map reading only. | Cathedral, Roman, hillfort, monument, castle, Wye sources. |
| UK-RAG-MOD-055 | site_gloucester_southern_radials_witcombe_scarp_intercept | Gloucester southern vale and Cotswold scarp | Hardwicke; Framilode; Cooper's Hill; Witcombe; Great Witcombe Villa; Innsworth; reservoirs | Inventory added; source-backed detail required. | Scarp-vale radial analysis across villa, reservoirs, brook corridors, and military overlays. | Speculative controlled radial gate reading only. | Villa, hydrology, military overlay, reservoir sources. |
| UK-RAG-MOD-056 | site_deerhurst_apperley_monastic_axis | Severn meander north of Gloucester | Deerhurst; Apperley; Odda's Chapel; St Mary's Priory; Severn meander; Domesday estate | Inventory added; source-backed detail required. | Monastic axis linking pre-Conquest architecture, Severn meander terrain, and estate records. | Speculative memory-anchor reading only. | Domesday, Westminster Abbey estate, ecclesiastical, geology sources. |

## Node 053 Collision

The source material used `UK-RAG-MOD-053` for both Tewkesbury and Hereford.
This repo resolves the collision as:

- `UK-RAG-MOD-053A`: Tewkesbury Severn-Avon River-Gate.
- `UK-RAG-MOD-053B`: Hereford Western Marches Corridor.

There is no active `UK-RAG-MOD-053` module record.

## Retrieval Examples

- `Show me all Gloucestershire modules`
- `What connects Stroud, Cirencester, Tewkesbury and Gloucester?`
- `Give me Tier I only for Tewkesbury`
- `Give me the speculative layer only for the Forest of Dean`
- `Map the Cotswold Way spine into the Severn and Bath systems`
- `Find all modules involving Roman villas`
- `Find all spring / hydrology / confluence sites`
- `Show all nodes with oolitic limestone`
- `Show all modules connected to the Ridgeway`

API examples:

```bash
curl -fsS 'http://127.0.0.1:8000/modules'
curl -fsS 'http://127.0.0.1:8000/modules/UK-RAG-MOD-053A'
curl -fsS 'http://127.0.0.1:8000/search?q=Tewkesbury&tier=I'
curl -fsS 'http://127.0.0.1:8000/claims?module_id=UK-RAG-MOD-053B&tier=III'
curl -fsS 'http://127.0.0.1:8000/map/layers'
```

## Validation Commands

Use these commands after editing the module layer:

```bash
python3 -m json.tool data/raw/black_albion_sites.json
python3 -m json.tool data/raw/black_albion_modules.json
python3 -m json.tool data/raw/black_albion_claims.json
python3 -m json.tool data/raw/black_albion_timeline.json
python3 -m json.tool data/raw/black_albion_sources.json
python3 -m pytest -q
python3 -m compileall backend
git diff --check
```

## Current Source Gaps

Tier I source enrichment is incomplete. The next data work should add public,
citable records for named monuments, geology, hydrology, route records,
conservation statuses, and historical documents not covered by the current
source ledger.

## Tier I Source Enrichment Pass 001

Pass 001 enriched only six target modules:

- `UK-RAG-MOD-053A` — Tewkesbury Severn-Avon River-Gate.
- `UK-RAG-MOD-053B` — Hereford Western Marches Corridor.
- `UK-RAG-MOD-046` — Stroud Frome Valley Radials.
- `UK-RAG-MOD-052` — Corinium Dobunnorum Palimpsest.
- `UK-RAG-MOD-047` — Trans-Severn Frontier and Forest of Dean Karst Scowles.
- `UK-RAG-MOD-044` — Cotswold Way Jurassic Escarpment Ridge Line.

### Claims Upgraded

The following Tier I inventory claims were upgraded from `needs_verification`
to `partial`:

- `claim_053a_inventory`
- `claim_053b_inventory`
- `claim_046_inventory`
- `claim_052_inventory`
- `claim_047_inventory`
- `claim_044_inventory`

No target claim was upgraded to `verified` in this pass. Each claim covers a
multi-site inventory, and the attached sources support strong factual parts of
the inventory but not every named site or landscape detail.

### Sources Added

Pass 001 added 18 source records to `data/raw/black_albion_sources.json`:

- `src_he_tewkesbury_battlefield_1000039`
- `src_he_tewkesbury_abbey_1201159`
- `src_mappa_mundi_hereford_cathedral`
- `src_he_dinedor_camp_1001758`
- `src_he_arthurs_stone_dorstone`
- `src_he_woodchester_villa_1004839`
- `src_he_uley_long_barrow_hetty_pegler`
- `src_he_west_hill_uley_metalworking_1987`
- `src_he_severn_vale_nmp_uley_bury`
- `src_corinium_museum_collection`
- `src_eh_cirencester_amphitheatre_history`
- `src_nt_chedworth_roman_villa_collection`
- `src_vch_gloucestershire_bagendon`
- `src_he_lydney_nodens_1017373`
- `src_he_clearwell_farm_villa_1406971`
- `src_he_forest_of_dean_research_framework_2017`
- `src_cotswold_way_official`
- `src_eh_belas_knap_long_barrow`

### Unresolved Gaps

Remaining direct-source gaps include:

- Tewkesbury: Oldbury Roman settlement, Deerhurst/Odda, Bredon/Kemerton,
  Ashchurch, Walton Cardiff, and Carrant Brook.
- Hereford: Castle Green, River Wye crossing, Rotherwas Ribbon, Sutton Walls,
  Kenchester/Magnis, Golden Valley, Leominster, Weobley, Goodrich Castle,
  Wigmore, Ledbury, and Bromyard.
- Stroud: Nympsfield Long Barrow and Painswick Beacon/Kimsbury Camp.
- Corinium: Roman walls, A417 mutatio, Rodmarton/Windmill Tump, Cirencester
  Abbey, and St John Baptist Church.
- Forest of Dean: Clearwell Caves, Puzzlewood Roman coin hoard, Highnam,
  Ross-on-Wye, Hempsted/Lady's Well, ochre detail, and direct iron-mining
  source records beyond Lydney/Clearwell context.
- Cotswold Way: direct geological source for Jurassic / oolitic limestone
  escarpment framing.

### Validation Commands Run

```bash
python3 -m json.tool data/raw/black_albion_sources.json
python3 -m json.tool data/raw/black_albion_claims.json
python3 -m pytest -q
python3 -m compileall backend
git diff --check
git diff --cached --check
scripts/smoke_test.sh
```

## Item-Level Tier I Source Pass 001

This pass added narrow item-level Tier I claims for the highest-value remaining
source gaps in four partially sourced regional modules:

- `UK-RAG-MOD-048` — Mercian Lattice and Central Sandstone Cavity Complex.
- `UK-RAG-MOD-051` — North Wessex Chalk Gateway and Ridgeway Corridor.
- `UK-RAG-MOD-055` — Gloucester Southern Radials and Witcombe Scarp Intercept.
- `UK-RAG-MOD-056` — Deerhurst / Apperley Monastic Axis.

The broad regional inventory claims remain `partial`; this pass does not claim
that every named inventory item in those modules is fully verified.

### Item-Level Claims Added

Added 27 item-level Tier I claims:

- `claim_048_staffordshire_hoard`
- `claim_048_wroxeter_viroconium`
- `claim_048_lunt_roman_fort`
- `claim_048_wrens_nest`
- `claim_048_old_oswestry`
- `claim_048_kinver_rock_houses`
- `claim_048_creswell_crags`
- `claim_048_nottingham_city_of_caves`
- `claim_048_borough_hill`
- `claim_051_avebury`
- `claim_051_silbury_hill`
- `claim_051_west_kennet_long_barrow`
- `claim_051_barbury_castle`
- `claim_051_liddington_castle`
- `claim_051_wanborough_durocornovium`
- `claim_051_uffington_white_horse`
- `claim_051_ridgeway_national_trail`
- `claim_055_great_witcombe_villa`
- `claim_055_horsbere_brook`
- `claim_055_coopers_hill_nature_reserve`
- `claim_055_framilode_frome_mouth`
- `claim_055_innsworth_arrc`
- `claim_056_oddas_chapel`
- `claim_056_st_mary_deerhurst`
- `claim_056_deerhurst_monastic_site`
- `claim_056_westminster_abbey_estate_link`
- `claim_056_mercia_mudstone_context`

### Sources Added

Added 14 source records:

- `src_nt_kinver_edge_rock_houses`
- `src_creswell_crags_rock_art_discovery`
- `src_national_justice_museum_city_of_caves`
- `src_he_borough_hill_1010696`
- `src_he_barbury_castle_1014557`
- `src_he_liddington_castle_1016312`
- `src_he_wanborough_roman_town_1004684`
- `src_ridgeway_national_trail_official`
- `src_visit_cheltenham_coopers_hill_nature_reserve`
- `src_vch_fretherne_saul_framilode`
- `src_govuk_arrc_innsworth_relocation`
- `src_he_deerhurst_st_mary_1151998`
- `src_he_deerhurst_monastic_site_1018632`
- `src_bgs_mercia_mudstone_group`

Existing source records were also linked to new item-level claims where they
already directly supported the named item.

### Claims Marked `verified`

The following item-level claims were marked `verified` because their attached
source records directly support the specific named item:

- `claim_048_staffordshire_hoard`
- `claim_048_wroxeter_viroconium`
- `claim_048_lunt_roman_fort`
- `claim_048_wrens_nest`
- `claim_048_old_oswestry`
- `claim_048_kinver_rock_houses`
- `claim_048_nottingham_city_of_caves`
- `claim_048_borough_hill`
- `claim_051_avebury`
- `claim_051_silbury_hill`
- `claim_051_west_kennet_long_barrow`
- `claim_051_barbury_castle`
- `claim_051_liddington_castle`
- `claim_051_uffington_white_horse`
- `claim_051_ridgeway_national_trail`
- `claim_055_great_witcombe_villa`
- `claim_055_horsbere_brook`
- `claim_055_innsworth_arrc`
- `claim_056_oddas_chapel`
- `claim_056_st_mary_deerhurst`
- `claim_056_deerhurst_monastic_site`

### Claims Marked `partial`

The following item-level claims remain `partial` because source support is
strong enough to anchor the named site or context, but not strong enough to
verify every implied detail:

- `claim_048_creswell_crags`
- `claim_051_wanborough_durocornovium`
- `claim_055_coopers_hill_nature_reserve`
- `claim_055_framilode_frome_mouth`
- `claim_056_westminster_abbey_estate_link`
- `claim_056_mercia_mudstone_context`

### Gaps Left Unresolved

Remaining item-level gaps include:

- `UK-RAG-MOD-048`: Birmingham / Metchley Roman Fort and Wolverhampton Cross.
- `UK-RAG-MOD-051`: Swindon as a wider gateway, Coate Water, and exact
  Durocornovium identification beyond the Wanborough scheduled Roman-town
  record.
- `UK-RAG-MOD-055`: Hardwicke, Hawkesbury, Brockworth, Witcombe reservoirs,
  and a stronger primary source for Cooper's Hill archaeological detail.
- `UK-RAG-MOD-056`: Apperley, exact Domesday estate entries, site-specific
  Severn river terrace / alluvial clay evidence, and map-specific
  Deerhurst / Apperley Mercia Mudstone confirmation.

### Validation Commands Run

```bash
python3 -m json.tool data/raw/black_albion_sources.json
python3 -m json.tool data/raw/black_albion_claims.json
python3 -m pytest -q
python3 -m compileall backend
git diff --check
git diff --cached --check
scripts/smoke_test.sh
```

## Tier I Source Enrichment Pass 002

Pass 002 enriched the remaining eight regional inventory modules that were
still marked `needs_verification` after Pass 001:

- `UK-RAG-MOD-043` — Southwestern Mercian Border Matrix.
- `UK-RAG-MOD-045` — Severn Ham Alluvial Convergence.
- `UK-RAG-MOD-048` — Mercian Lattice and Central Sandstone Cavity Complex.
- `UK-RAG-MOD-049` — Tamensis Basin and Upper Cretaceous Chalk Corridors.
- `UK-RAG-MOD-050` — Fenland Basin and East Anglian Chalk Escarpments.
- `UK-RAG-MOD-051` — North Wessex Chalk Gateway and Ridgeway Corridor.
- `UK-RAG-MOD-055` — Gloucester Southern Radials and Witcombe Scarp Intercept.
- `UK-RAG-MOD-056` — Deerhurst / Apperley Monastic Axis.

### Claims Upgraded

The following Tier I inventory claims were upgraded from `needs_verification`
to `partial`:

- `claim_043_inventory`
- `claim_045_inventory`
- `claim_048_inventory`
- `claim_049_inventory`
- `claim_050_inventory`
- `claim_051_inventory`
- `claim_055_inventory`
- `claim_056_inventory`

No claim was upgraded to `verified` in this pass. Each inventory claim covers a
multi-site module, and the source records support major named sites or core
landscape facts but do not yet support every listed item at item level.

After this pass, all 14 regional module inventory claims are at least
`partial`.

### Sources Added

Pass 002 added 26 source records to `data/raw/black_albion_sources.json`:

- `src_roman_baths_sacred_spring`
- `src_bgs_bath_hot_springs_geology_2006`
- `src_geoguide_avon_gorge_hotwells_limestone`
- `src_tewkesbury_town_severn_ham_sssi`
- `src_tewkesbury_borough_healings_mill`
- `src_birmingham_museums_staffordshire_hoard`
- `src_he_staffordshire_hoard_research`
- `src_eh_wroxeter_roman_city_history`
- `src_he_old_oswestry_1014899`
- `src_dudley_wrens_nest_geology`
- `src_lunt_roman_fort_official`
- `src_london_museum_mithraeum_walbrook`
- `src_oxford_city_port_meadow`
- `src_oxford_dorchester_on_thames_archaeology`
- `src_eh_waylands_smithy_history`
- `src_nt_white_horse_hill_uffington`
- `src_he_car_dyke_1009999`
- `src_cambridge_must_farm_project`
- `src_wildlife_bcn_fleam_dyke`
- `src_he_cambridgeshire_dykes_bran_context_1410907`
- `src_nt_avebury_stone_circles_henge`
- `src_eh_avebury_world_heritage_site`
- `src_he_west_kennet_long_barrow_1010628`
- `src_he_great_witcombe_villa_1014826`
- `src_gloucester_horsbere_brook_fas`
- `src_eh_oddas_chapel_history`

### Claims Left `needs_verification`

No regional module inventory claims remain `needs_verification` after Pass 002.
Non-inventory or future item-level claims may still need separate sourcing.

### Unresolved Gaps

Remaining direct-source gaps include:

- Southwestern Mercian Border Matrix: Bristol harbour, Hotwells built
  environment, and Hwicce frontier framing.
- Severn Ham Alluvial Convergence: Abbey Mill history, common-land title
  detail, and fuller floodplain-management sourcing.
- Mercian Lattice: Birmingham / Metchley, Wolverhampton Cross, Kinver Rock
  Houses, Creswell Crags, Nottingham City of Caves, and Borough Hill.
- Tamensis Basin: wider Londinium / London Wall, Oxford city archaeology, and
  detailed chalk-corridor geology.
- Fenland Basin: Ely, Peterborough, Fen-edge villas, Bedford Level drainage /
  enclosure, and full Bronze Age timber-settlement detail.
- North Wessex Chalk Gateway: Swindon, Barbury Castle, Liddington Castle,
  Wanborough / Durocornovium, Coate Water, Ridgeway route detail, and Vale of
  White Horse.
- Gloucester Southern Radials: Hardwicke, Framilode / Frome mouth, Hawkesbury,
  Brockworth, Cooper's Hill, Witcombe reservoirs, Innsworth, and public NATO /
  military overlays.
- Deerhurst / Apperley: Apperley, separate St Mary's Priory Church records,
  Domesday estate detail, Severn meander, river terrace / alluvial clay, and
  Triassic Mercia Mudstone context.

### Validation Commands Run

```bash
python3 -m json.tool data/raw/black_albion_sources.json
python3 -m json.tool data/raw/black_albion_claims.json
python3 -m pytest -q
python3 -m compileall backend
git diff --check
git diff --cached --check
scripts/smoke_test.sh
```
