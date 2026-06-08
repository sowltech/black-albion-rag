"""Local lexical retriever over Black Albion JSON evidence ledgers.

Local-first: no network calls, no paid APIs. Uses BM25-lite token overlap +
phrase bonus so the repo runs out-of-the-box without external dependencies.
A vector backend can be layered on top via ``vector_ingest.py`` when wanted.
"""
from __future__ import annotations

import json
import pickle
import re
from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

WORD_RE = re.compile(r"[A-Za-z0-9']+")

# Default tier when a record does not explicitly declare one.
DEFAULT_TIER = "I"
VALID_TIERS = {"I", "II", "III"}


@dataclass(frozen=True)
class RetrievedEvidence:
    """A retrieved evidence record with provenance + tier."""

    source_file: str
    record_id: Optional[str]
    title: str
    tier: str
    score: float
    excerpt: str
    metadata: Dict[str, Any] = field(default_factory=dict)


def _tokens(text: str) -> set[str]:
    return {token.lower() for token in WORD_RE.findall(text)}


def _coerce_tier(value: Any) -> str:
    if isinstance(value, str):
        upper = value.strip().upper()
        if upper in VALID_TIERS:
            return upper
        # Allow legacy tier names from earlier ledgers.
        mapping = {
            "ARCHIVAL_LEDGER": "I",
            "ARCHIVAL_BASELINE": "I",
            "SCHOLARLY": "II",
            "INTERPRETATION": "II",
            "SPECULATIVE": "III",
            "MYTHIC": "III",
        }
        if upper in mapping:
            return mapping[upper]
    return DEFAULT_TIER


def _first_present(record: Dict[str, Any], keys: Sequence[str]) -> str:
    for key in keys:
        value = record.get(key)
        if value not in (None, ""):
            return str(value)
    return ""


def _field_contains(value: Any, needle: str) -> bool:
    needle = needle.lower()
    if isinstance(value, str):
        return needle in value.lower()
    if isinstance(value, list):
        return any(_field_contains(item, needle) for item in value)
    if isinstance(value, dict):
        return any(_field_contains(item, needle) for item in value.values())
    if value is None:
        return False
    return needle in str(value).lower()


def _module_tier_text(record: Dict[str, Any], tier: str) -> str:
    if tier == "I":
        return _record_text(
            {
                "name": record.get("name"),
                "module_id": record.get("module_id"),
                "site_id": record.get("site_id"),
                "region": record.get("region"),
                "nearest_place": record.get("nearest_place"),
                "county": record.get("county"),
                "period": record.get("period"),
                "layer_0_geology": record.get("layer_0_geology"),
                "tier_i_evidence": record.get("tier_i_evidence"),
                "routing": record.get("routing"),
            }
        )
    if tier == "II":
        return _record_text(
            {
                "name": record.get("name"),
                "module_id": record.get("module_id"),
                "site_id": record.get("site_id"),
                "region": record.get("region"),
                "nearest_place": record.get("nearest_place"),
                "county": record.get("county"),
                "period": record.get("period"),
                "tier_ii_interpretation": record.get("tier_ii_interpretation"),
                "routing": record.get("routing"),
            }
        )
    return _record_text(
        {
            "name": record.get("name"),
            "module_id": record.get("module_id"),
            "site_id": record.get("site_id"),
            "region": record.get("region"),
            "nearest_place": record.get("nearest_place"),
            "county": record.get("county"),
            "period": record.get("period"),
            "tier_iii_speculative_logic": record.get("tier_iii_speculative_logic"),
            "routing": record.get("routing"),
        }
    )


def _record_text(record: Dict[str, Any]) -> str:
    """Flatten a record into a single text blob for lexical scoring."""
    pieces: List[str] = []

    def _walk(value: Any) -> None:
        if isinstance(value, str):
            stripped = value.strip()
            if stripped:
                pieces.append(stripped)
        elif isinstance(value, list):
            for item in value:
                _walk(item)
        elif isinstance(value, dict):
            for sub in value.values():
                _walk(sub)
        elif value is not None:
            pieces.append(str(value))

    for key in (
        "title",
        "name",
        "module_id",
        "site_id",
        "claim_id",
        "claim_text",
        "summary",
        "description",
        "region",
        "nearest_place",
        "county",
        "period",
        "themes",
        "claims",
        "routing",
        "layer_0_geology",
        "tier_i_evidence",
        "tier_ii_interpretation",
        "tier_i_enclosure_evidence",
        "tier_iii_speculative",
        "tier_iii_speculative_logic",
        "source",
        "endpoint",
    ):
        if key in record:
            _walk(record[key])

    # Fall back to a full walk for unknown shapes.
    if not pieces:
        _walk(record)

    return " ".join(pieces)


class BlackAlbionRetriever:
    """Loads JSON ledgers from one or more data directories and ranks records."""

    def __init__(
        self,
        data_dirs: Sequence[Path],
        cache_path: Optional[Path] = None,
    ) -> None:
        self.data_dirs = [Path(d) for d in data_dirs]
        self.cache_path = Path(cache_path) if cache_path else None
        self.documents: List[Dict[str, Any]] = []
        self._load_documents()
        if self.cache_path is not None:
            self._refresh_cache()

    # ----- Loading -----------------------------------------------------------

    def _load_documents(self) -> None:
        self.documents = []
        for data_dir in self.data_dirs:
            if not data_dir.exists() or not data_dir.is_dir():
                continue
            for json_path in sorted(data_dir.glob("*.json")):
                try:
                    payload = json.loads(json_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                self._ingest_payload(json_path, payload)

    def _ingest_payload(self, source_path: Path, payload: Any) -> None:
        records: Iterable[Dict[str, Any]]
        if isinstance(payload, list):
            records = (r for r in payload if isinstance(r, dict))
        elif isinstance(payload, dict):
            # Allow {"records": [...]} or {"sites": [...]} envelopes.
            for key in ("records", "sites", "claims", "sources", "timeline", "items"):
                inner = payload.get(key)
                if isinstance(inner, list):
                    records = (r for r in inner if isinstance(r, dict))
                    break
            else:
                records = [payload]
        else:
            return

        for record in records:
            if record.get("module_id") and record.get("tier_i_evidence"):
                self._ingest_module_record(source_path, record)
                continue
            text = _record_text(record)
            if not text:
                continue
            tier = _coerce_tier(record.get("tier") or record.get("source_tier"))
            self.documents.append(
                {
                    "source_file": str(source_path),
                    "record_id": _first_present(record, ("id", "claim_id", "module_id", "site_id")),
                    "tier": tier,
                    "text": text,
                    "metadata": record,
                }
            )

    def _ingest_module_record(self, source_path: Path, record: Dict[str, Any]) -> None:
        for tier in ("I", "II", "III"):
            text = _module_tier_text(record, tier)
            if not text:
                continue
            metadata = dict(record)
            metadata["retrieved_tier"] = tier
            self.documents.append(
                {
                    "source_file": str(source_path),
                    "record_id": str(record.get("module_id") or ""),
                    "tier": tier,
                    "text": text,
                    "metadata": metadata,
                }
            )

    # ----- Cache -------------------------------------------------------------

    def _signature(self) -> str:
        payload = [(d["source_file"], d["text"]) for d in self.documents]
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        return sha256(raw).hexdigest()

    def _refresh_cache(self) -> None:
        assert self.cache_path is not None
        signature = self._signature()
        if self.cache_path.exists():
            try:
                cached = pickle.loads(self.cache_path.read_bytes())
                if cached.get("signature") == signature:
                    return
            except (OSError, pickle.UnpicklingError, EOFError):
                pass
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_bytes(
            pickle.dumps({"signature": signature, "documents": self.documents})
        )

    def rebuild_cache(self) -> None:
        self._load_documents()
        if self.cache_path is not None:
            self._refresh_cache()

    # ----- Search ------------------------------------------------------------

    def search(
        self,
        query: str,
        k: int = 5,
        include_tiers: Optional[Sequence[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievedEvidence]:
        query = (query or "").strip()
        if not query:
            return []

        tier_filter = {t.upper() for t in include_tiers} if include_tiers else set(VALID_TIERS)
        query_tokens = _tokens(query)
        if not query_tokens:
            return []

        scored: List[RetrievedEvidence] = []
        query_lower = query.lower()
        for doc in self.documents:
            if doc["tier"] not in tier_filter:
                continue
            if filters and not self._matches_filters(doc, filters):
                continue
            text = doc["text"]
            overlap = len(query_tokens & _tokens(text))
            if overlap == 0 and query_lower not in text.lower():
                continue
            phrase_bonus = 1.5 if query_lower in text.lower() else 0.0
            score = float(overlap) + phrase_bonus
            if score <= 0:
                continue
            metadata = doc["metadata"]
            title = str(
                metadata.get("title")
                or metadata.get("name")
                or metadata.get("source")
                or metadata.get("id")
                or "Untitled"
            )
            scored.append(
                RetrievedEvidence(
                    source_file=doc["source_file"],
                    record_id=doc["record_id"] or None,
                    title=title,
                    tier=doc["tier"],
                    score=score,
                    excerpt=text[:320],
                    metadata=metadata,
                )
            )

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:k]

    def _matches_filters(self, doc: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        metadata = doc["metadata"]
        field_map = {
            "module_id": metadata.get("module_id"),
            "site_id": metadata.get("site_id") or metadata.get("id"),
            "county": metadata.get("county"),
            "nearest_place": metadata.get("nearest_place"),
            "period": metadata.get("period"),
            "tier": doc.get("tier"),
            "theme": metadata.get("themes") or (metadata.get("routing") or {}).get("themes"),
            "geology": metadata.get("layer_0_geology"),
            "hydrology": metadata.get("layer_0_geology", {}).get("hydrology_metrics")
            or metadata.get("layer_0_geology", {}).get("hydrology"),
            "route": metadata.get("routing"),
            "place": metadata.get("routing", {}).get("places")
            or metadata.get("nearest_place")
            or metadata.get("name"),
        }
        for key, expected in filters.items():
            if expected in (None, "", []):
                continue
            field_value = field_map.get(key)
            values = expected if isinstance(expected, list) else [expected]
            if not any(_field_contains(field_value, str(value)) for value in values):
                return False
        return True

    def modules(self) -> List[Dict[str, Any]]:
        seen: set[str] = set()
        modules: List[Dict[str, Any]] = []
        for doc in self.documents:
            metadata = doc["metadata"]
            module_id = metadata.get("module_id")
            if not module_id or module_id in seen:
                continue
            seen.add(str(module_id))
            modules.append(metadata)
        return sorted(modules, key=lambda item: str(item.get("module_id", "")))

    def sites(self) -> List[Dict[str, Any]]:
        seen: set[str] = set()
        sites: List[Dict[str, Any]] = []
        for doc in self.documents:
            metadata = doc["metadata"]
            if str(metadata.get("claim_id") or metadata.get("id") or "").startswith("claim_"):
                continue
            site_id = metadata.get("site_id") or metadata.get("id")
            if not site_id or str(site_id) in seen:
                continue
            seen.add(str(site_id))
            sites.append(metadata)
        return sorted(sites, key=lambda item: str(item.get("site_id") or item.get("id") or ""))

    def claims(self, module_id: Optional[str] = None, tier: Optional[str] = None) -> List[Dict[str, Any]]:
        claims: List[Dict[str, Any]] = []
        seen: set[str] = set()
        tier_filter = tier.upper() if tier else None
        for doc in self.documents:
            metadata = doc["metadata"]
            claim_id = metadata.get("claim_id") or metadata.get("id")
            if not claim_id or not str(claim_id).startswith("claim_"):
                continue
            if str(claim_id) in seen:
                continue
            if module_id and metadata.get("module_id") != module_id:
                continue
            if tier_filter and _coerce_tier(metadata.get("tier")) != tier_filter:
                continue
            seen.add(str(claim_id))
            claims.append(metadata)
        return sorted(claims, key=lambda item: str(item.get("claim_id") or item.get("id") or ""))
