# Black Albion Module Expansion

This document records the expanded regional module layer added to the local
Black Albion RAG system.

The new module data lives in `data/raw/black_albion_modules.json`. Each module
keeps Tier I, Tier II, and Tier III fields separate. Most Tier I inventories are
currently marked `needs_verification` because the supplied module list names
sites and landscape features but does not yet attach item-level source records.

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

All newly added Tier I module inventory claims are currently marked
`needs_verification` unless future source records are attached. The next data
work should add public, citable records for the named monuments, geology,
hydrology, route records, conservation statuses, and historical documents.
