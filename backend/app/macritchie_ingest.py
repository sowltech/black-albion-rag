"""MacRitchie public-domain source registration.

We do NOT download or scrape the source PDFs by default. This module simply
registers the canonical, operator-verified public-domain endpoints (Internet
Archive + Wikimedia Commons) into ``data/raw/macritchie_sources.json`` so
the retriever can surface them as Tier I archival references.

A future ingestion step (parse PDFs into text + chunk) can be layered on top.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCES_PATH = REPO_ROOT / "data" / "raw" / "macritchie_sources.json"


MACRITCHIE_PAYLOADS: List[Dict[str, Any]] = [
    {
        "id": "macritchie_ancient_and_modern_britons_v1",
        "tier": "I",
        "author": "David MacRitchie",
        "title": "Ancient and Modern Britons: A Retrospect (Volume I)",
        "year": 1884,
        "endpoint": "https://archive.org/download/ancientandmodernbritons/Ancient_and_Modern_Britons.pdf",
        "host": "Internet Archive",
        "license": "public-domain",
        "summary": (
            "Documents the explicit historical, linguistic, and heraldic "
            "evidence MacRitchie marshalled for dark-complexioned populations "
            "in early Britain (heraldry, surnames, royal municipal records)."
        ),
    },
    {
        "id": "macritchie_testimony_of_tradition",
        "tier": "I",
        "author": "David MacRitchie",
        "title": "The Testimony of Tradition",
        "year": 1890,
        "endpoint": (
            "https://archive.org/download/testimonyoftradi00macruoft/"
            "testimonyoftradi00macruoft.pdf"
        ),
        "host": "Internet Archive",
        "license": "public-domain",
        "summary": (
            "Euhemeristic mapping of British 'fairy hill' folklore to physical "
            "subterranean stone earth-houses and corbelled chambers."
        ),
    },
    {
        "id": "macritchie_gypsies_of_india",
        "tier": "I",
        "author": "David MacRitchie",
        "title": "Accounts of the Gypsies of India",
        "year": 1886,
        "endpoint": (
            "https://upload.wikimedia.org/wikipedia/commons/c/c9/"
            "Accounts_of_the_Gypsies_of_India_%28IA_cu31924023897634%29.pdf"
        ),
        "host": "Wikimedia Commons",
        "license": "public-domain",
        "summary": (
            "Comparative ethnographic mapping tracking migration routes and "
            "ancestral cross-references of nomadic lineages between India and "
            "the British Isles."
        ),
    },
    {
        "id": "macritchie_fians_fairies_and_picts",
        "tier": "I",
        "author": "David MacRitchie",
        "title": "Fians, Fairies and Picts",
        "year": 1893,
        "endpoint": "https://archive.org/details/fiansfairiesandp17926gut",
        "host": "Internet Archive (HTML + JPEG; convert locally for PDF)",
        "license": "public-domain",
        "summary": (
            "Detailed archaeological review of underground earth-houses, "
            "drystone corbelled huts, and the acoustic technology attributed "
            "to the historical Picts."
        ),
    },
]


def register(sources_path: Path = DEFAULT_SOURCES_PATH) -> int:
    """Write / refresh ``macritchie_sources.json`` and return record count."""
    sources_path.parent.mkdir(parents=True, exist_ok=True)
    sources_path.write_text(
        json.dumps(MACRITCHIE_PAYLOADS, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return len(MACRITCHIE_PAYLOADS)


def main() -> int:
    count = register()
    print(f"[ok] macritchie_ingest: registered {count} sources at {DEFAULT_SOURCES_PATH}")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    sys.exit(main())
