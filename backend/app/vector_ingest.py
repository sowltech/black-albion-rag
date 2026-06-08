"""Optional vector-store ingestion using ChromaDB.

This module is deliberately import-light: it only imports ``chromadb`` inside
the entrypoint so the rest of the backend continues to work without the
optional dependency installed. Run it manually with::

    python -m backend.app.vector_ingest

Designed for a fully local, source-tier-preserving embedding pass: each
record is flattened into a semantic chunk and stored with ``tier`` metadata
so a downstream retriever can honour the same tier filter as the lexical
retriever in ``retriever.py``.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .retriever import VALID_TIERS, _coerce_tier, _record_text


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = REPO_ROOT / "data" / "raw"
DEFAULT_INDEX_DIR = REPO_ROOT / "data" / "index" / "chroma"
COLLECTION_NAME = "black_albion_grid"


def iter_records(data_dir: Path) -> Iterable[tuple[Path, Dict[str, Any]]]:
    """Yield ``(source_path, record)`` tuples from every JSON ledger."""
    for json_path in sorted(data_dir.glob("*.json")):
        try:
            payload = json.loads(json_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[skip] {json_path.name}: {exc}", file=sys.stderr)
            continue

        records: List[Dict[str, Any]] = []
        if isinstance(payload, list):
            records = [r for r in payload if isinstance(r, dict)]
        elif isinstance(payload, dict):
            for key in ("records", "sites", "claims", "sources", "timeline", "items"):
                inner = payload.get(key)
                if isinstance(inner, list):
                    records = [r for r in inner if isinstance(r, dict)]
                    break

        for record in records:
            yield json_path, record


def build_chunks(data_dir: Path) -> tuple[List[str], List[Dict[str, Any]], List[str]]:
    """Return ``(documents, metadatas, ids)`` ready for ``collection.upsert``."""
    documents: List[str] = []
    metadatas: List[Dict[str, Any]] = []
    ids: List[str] = []

    for source_path, record in iter_records(data_dir):
        text = _record_text(record)
        if not text:
            continue
        tier = _coerce_tier(record.get("tier") or record.get("source_tier"))
        if tier not in VALID_TIERS:
            tier = "I"
        record_id = (
            str(record.get("id"))
            or str(record.get("name") or "")
            or f"{source_path.stem}_{len(ids)}"
        )
        ids.append(record_id)
        documents.append(text)
        metadatas.append(
            {
                "source_file": source_path.name,
                "tier": tier,
                "title": str(record.get("title") or record.get("name") or record_id),
            }
        )
    return documents, metadatas, ids


def ingest(
    data_dir: Path = DEFAULT_DATA_DIR,
    index_dir: Path = DEFAULT_INDEX_DIR,
    collection_name: str = COLLECTION_NAME,
) -> int:
    """Upsert every record into a persistent local ChromaDB collection.

    Returns the number of records indexed. Raises ``RuntimeError`` with a
    helpful hint if ``chromadb`` is not installed.
    """
    try:
        import chromadb  # type: ignore
        from chromadb.utils import embedding_functions  # type: ignore
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError(
            "chromadb is not installed. Install with: pip install chromadb"
        ) from exc

    documents, metadatas, ids = build_chunks(data_dir)
    if not documents:
        print(f"[warn] no records found under {data_dir}", file=sys.stderr)
        return 0

    index_dir.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(index_dir))
    default_ef = embedding_functions.DefaultEmbeddingFunction()
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=default_ef,
    )
    collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
    return len(documents)


def main() -> int:
    count = ingest()
    print(f"[ok] vector_ingest: upserted {count} records into {DEFAULT_INDEX_DIR}")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    sys.exit(main())
