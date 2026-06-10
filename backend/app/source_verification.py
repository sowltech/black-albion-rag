"""Deterministic source verification engine for Black Albion RAG.

Also exposes per-claim helpers for the v0.5.0 Per-Claim Source Verification
dashboard panel:

- ``extract_claim_sections_from_review(text)`` — splits the worksheet
  markdown into one section per ``### Claim N — …`` heading.
- ``summarize_per_claim_verification(candidate_row, review_text)`` —
  classifies each section's sources via the engine and returns one summary
  per claim.

These helpers stay read-only and never write canonical ledgers.

Classifies individual source references into the seven evidence tiers used by
the v0.5.0 Source Verification dashboard panel, and aggregates per-claim
verification summaries from a list of source references. This module is
read-only with respect to canonical data: it never writes ledger files, never
approves, and never promotes.

Public surface:

- ``SOURCE_TIERS`` — ordered tuple of the seven evidence tier names.
- ``SOURCE_TIER_WEIGHT`` — mapping each tier name to its integer weight
  (higher = stronger).
- ``classify_source_strength(name, url, notes)`` — classifies a single source
  and returns ``{source_tier, confidence, reason, promotion_weight,
  requires_operator_review}``.
- ``summarize_claim_verification(sources, blocked=False,
  requires_correction=False)`` — aggregates a list of sources into per-tier
  counts and a single ``verification_status``.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

# Tier names in ascending order of "strength". The promotion_weight is the
# zero-based index so a higher number always means a stronger source.
SOURCE_TIERS: Tuple[str, ...] = (
    "no_source",
    "speculative_only",
    "orientation_only",
    "weak_secondary_source",
    "reputable_secondary_source",
    "institutional_source",
    "primary_source",
)

SOURCE_TIER_WEIGHT: Dict[str, int] = {
    tier: weight for weight, tier in enumerate(SOURCE_TIERS)
}

# Host -> (tier, reason). Matched on exact host or a "*.host" suffix.
_HOST_RULES: List[Tuple[str, str, str]] = [
    (
        "thegazette.co.uk",
        "primary_source",
        "The London Gazette is a primary state-published record",
    ),
    (
        "nationalarchives.gov.uk",
        "institutional_source",
        "The National Archives Discovery catalogue is an institutional finding aid",
    ),
    (
        "iwm.org.uk",
        "institutional_source",
        "Imperial War Museums is an institutional heritage source",
    ),
    (
        "nam.ac.uk",
        "institutional_source",
        "National Army Museum is an institutional heritage source",
    ),
    (
        "historicengland.org.uk",
        "institutional_source",
        "Historic England is the official heritage agency for England",
    ),
    (
        "cadw.gov.wales",
        "institutional_source",
        "Cadw is the Welsh Government's historic environment service",
    ),
    (
        "archaeology.ie",
        "institutional_source",
        "National Monuments Service Ireland institutional source",
    ),
    (
        "bgs.ac.uk",
        "institutional_source",
        "British Geological Survey institutional source",
    ),
    (
        "soldiersofglos.com",
        "institutional_source",
        "Soldiers of Gloucestershire Museum institutional source",
    ),
    (
        "wessexyeomanry.org",
        "institutional_source",
        "Royal Wessex Yeomanry institutional parent-regiment source",
    ),
    (
        "armymuseums.org.uk",
        "institutional_source",
        "Army Museums Ogilby Trust sector-body listing",
    ),
    (
        "vcgca.org",
        "institutional_source",
        "Victoria Cross and George Cross Association institutional roll",
    ),
    (
        "longlongtrail.co.uk",
        "reputable_secondary_source",
        "The Long, Long Trail is a respected specialist WWI history site",
    ),
    (
        "britishempire.co.uk",
        "reputable_secondary_source",
        "britishempire.co.uk is a reputable secondary regimental-history source",
    ),
    (
        "victoriacross.org.uk",
        "reputable_secondary_source",
        "victoriacross.org.uk is a reputable VC-roll secondary source",
    ),
    (
        "victoriacrossonline.co.uk",
        "reputable_secondary_source",
        "victoriacrossonline.co.uk is a reputable VC-roll secondary source",
    ),
    (
        "memorialstovalour.co.uk",
        "reputable_secondary_source",
        "Memorials to Valour is a reputable VC-memorial secondary source",
    ),
    (
        "gcccheritagetrust.org",
        "weak_secondary_source",
        "GCCC Heritage Trust page is a weak secondary source",
    ),
    (
        "gloucesterbid.uk",
        "weak_secondary_source",
        "Gloucester Business Improvement District page is a weak secondary source",
    ),
    (
        "en.wikipedia.org",
        "orientation_only",
        "Wikipedia is orientation only",
    ),
    (
        "wikipedia.org",
        "orientation_only",
        "Wikipedia is orientation only",
    ),
    (
        "en-academic.com",
        "orientation_only",
        "Encyclopaedia mirror; orientation only",
    ),
    (
        "military-history.fandom.com",
        "weak_secondary_source",
        "Fandom Military Wiki is a weak secondary source",
    ),
    (
        "archive.org",
        "primary_source",
        "Internet Archive scans of public-domain primary works",
    ),
    (
        "upload.wikimedia.org",
        "primary_source",
        "Wikimedia Commons hosting of public-domain primary works",
    ),
]

# Name-based fallbacks used when no URL is provided or the host isn't matched.
_NAME_RULES: List[Tuple[str, str, str]] = [
    (
        "london gazette",
        "primary_source",
        "Named as The London Gazette (primary state record)",
    ),
    (
        "national archives",
        "institutional_source",
        "Named as The National Archives",
    ),
    (
        "tna ",
        "institutional_source",
        "Named as The National Archives (WO/Discovery)",
    ),
    (
        "war diary",
        "primary_source",
        "Named as a war diary (primary record)",
    ),
    (
        "war diaries",
        "primary_source",
        "Named as war diaries (primary records)",
    ),
    (
        "national army museum",
        "institutional_source",
        "Named as National Army Museum",
    ),
    (
        "imperial war museums",
        "institutional_source",
        "Named as Imperial War Museums",
    ),
    (
        "historic england",
        "institutional_source",
        "Named as Historic England",
    ),
    (
        "soldiers of gloucestershire museum",
        "institutional_source",
        "Named as Soldiers of Gloucestershire Museum",
    ),
    (
        "royal wessex yeomanry",
        "institutional_source",
        "Named as Royal Wessex Yeomanry",
    ),
    (
        "army museums ogilby trust",
        "institutional_source",
        "Named as Army Museums Ogilby Trust",
    ),
    (
        "the long, long trail",
        "reputable_secondary_source",
        "Named as The Long, Long Trail",
    ),
    (
        "long long trail",
        "reputable_secondary_source",
        "Named as The Long Long Trail",
    ),
    (
        "regimental history",
        "reputable_secondary_source",
        "Named as a regimental history (published secondary)",
    ),
    (
        "wikipedia",
        "orientation_only",
        "Named as Wikipedia",
    ),
]

# Tokens that mark Tier III / speculative / mythic interpretive material.
_SPECULATIVE_TOKENS: Tuple[str, ...] = (
    "amenta",
    "back-badge sensory vector",
    "back badge sensory vector",
    "trans-continental grid",
    "trans continental grid",
    "counter-intelligence",
    "tier iii",
    "tier_iii",
    "speculative_lens",
    "speculative lens",
    "symbolic framing",
)


def _result(
    tier: str,
    reason: str,
    *,
    confidence: str = "medium",
    requires_operator_review: bool = False,
) -> Dict[str, Any]:
    return {
        "source_tier": tier,
        "confidence": confidence,
        "reason": reason,
        "promotion_weight": SOURCE_TIER_WEIGHT[tier],
        "requires_operator_review": requires_operator_review,
    }


def _normalise_host(url: str) -> str:
    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        return ""
    if host.startswith("www."):
        host = host[4:]
    return host


def classify_source_strength(
    source_name: str = "",
    source_url: str = "",
    source_notes: str = "",
) -> Dict[str, Any]:
    """Classify a single source reference deterministically.

    Returns a dict with:
        source_tier             — one of SOURCE_TIERS
        confidence              — "low" / "medium" / "high"
        reason                  — short human-readable rationale
        promotion_weight        — int, higher = stronger
        requires_operator_review — bool
    """
    name = (source_name or "").strip()
    url = (source_url or "").strip()
    notes = (source_notes or "").strip()
    combined = " ".join((name, url, notes)).lower()

    # Speculative content wins over URL host classification.
    if any(token in combined for token in _SPECULATIVE_TOKENS):
        return _result(
            "speculative_only",
            "Surrounded by Tier III / speculative framing",
            confidence="high",
            requires_operator_review=True,
        )

    # URL host classification (exact host or '*.host' suffix).
    if url:
        host = _normalise_host(url)
        if host:
            for rule_host, rule_tier, rule_reason in _HOST_RULES:
                if host == rule_host or host.endswith("." + rule_host):
                    return _result(
                        rule_tier,
                        rule_reason,
                        confidence="high",
                        requires_operator_review=rule_tier
                        in {
                            "weak_secondary_source",
                            "orientation_only",
                            "speculative_only",
                        },
                    )

    # Name pattern fallback.
    if name:
        lower_name = name.lower()
        for pattern, rule_tier, rule_reason in _NAME_RULES:
            if pattern in lower_name:
                return _result(
                    rule_tier,
                    rule_reason,
                    confidence="medium",
                    requires_operator_review=rule_tier
                    in {
                        "weak_secondary_source",
                        "orientation_only",
                        "speculative_only",
                    },
                )

    # No URL and no recognised name => no_source.
    if not url and not name:
        return _result(
            "no_source",
            "no source name or URL provided",
            confidence="high",
            requires_operator_review=True,
        )

    # URL provided but host unknown => weak_secondary_source.
    if url:
        host = _normalise_host(url) or "unknown"
        return _result(
            "weak_secondary_source",
            f"Unrecognised host {host}",
            confidence="low",
            requires_operator_review=True,
        )

    # Name provided but unmatched => weak_secondary_source.
    return _result(
        "weak_secondary_source",
        "Unrecognised source name",
        confidence="low",
        requires_operator_review=True,
    )


# Status derivation precedence:
#   blocked / requires_correction (operator-driven) override automatic levels.
#   then strongest available tier:
#     primary_source >= 1   -> verified_primary
#     institutional >= 1    -> institutionally_supported
#     reputable_sec >= 1    -> partially_supported
#     orientation/weak >= 1 -> orientation_only
#     speculative_only >= 1 -> speculative_only
#     else                  -> unsourced
def summarize_claim_verification(
    sources: List[Dict[str, str]],
    *,
    blocked: bool = False,
    requires_correction: bool = False,
) -> Dict[str, Any]:
    """Aggregate per-source classifications into a single verification summary.

    Args:
        sources: list of dicts with optional ``name``, ``url``, ``notes`` keys.
        blocked: force ``verification_status`` to ``"blocked"`` (e.g. when the
            row carries a Tier I block such as ``claim_6_tier_i_allowed: false``).
        requires_correction: force ``verification_status`` to
            ``"requires_correction"``.
    """
    classifications = [
        classify_source_strength(
            s.get("name", ""),
            s.get("url", ""),
            s.get("notes", ""),
        )
        for s in sources
    ]
    counts = {tier: 0 for tier in SOURCE_TIERS}
    for cls in classifications:
        counts[cls["source_tier"]] += 1

    if classifications:
        strongest = max(classifications, key=lambda c: c["promotion_weight"])
        strongest_tier = strongest["source_tier"]
        strongest_weight = strongest["promotion_weight"]
    else:
        strongest_tier = "no_source"
        strongest_weight = SOURCE_TIER_WEIGHT["no_source"]

    if blocked:
        status = "blocked"
    elif requires_correction:
        status = "requires_correction"
    elif counts["primary_source"] >= 1:
        status = "verified_primary"
    elif counts["institutional_source"] >= 1:
        status = "institutionally_supported"
    elif counts["reputable_secondary_source"] >= 1:
        status = "partially_supported"
    elif counts["weak_secondary_source"] >= 1 or counts["orientation_only"] >= 1:
        status = "orientation_only"
    elif counts["speculative_only"] >= 1:
        status = "speculative_only"
    else:
        status = "unsourced"

    return {
        "strongest_source_tier": strongest_tier,
        "strongest_source_weight": strongest_weight,
        "source_count": len(classifications),
        "primary_source_count": counts["primary_source"],
        "institutional_source_count": counts["institutional_source"],
        "reputable_secondary_count": counts["reputable_secondary_source"],
        "weak_source_count": counts["weak_secondary_source"],
        "orientation_only_count": counts["orientation_only"],
        "speculative_only_count": counts["speculative_only"],
        "no_source_count": counts["no_source"],
        "verification_status": status,
        "classifications": classifications,
    }


# ----------------------------------------------------------------------
# Per-claim helpers (v0.5.0 Per-Claim Source Verification panel)
# ----------------------------------------------------------------------

# Top-level claim heading like:
#   "### Claim 2 — Percival Marling VC / London Gazette citation"
_CLAIM_HEADING_RE = re.compile(
    r"^###\s+Claim\s+(?P<number>\d+)\s*(?:[—\-:]\s*(?P<title>.+))?$",
    re.MULTILINE,
)

# Sub-heading patterns like "#### Claim 2 — Source attachment pass (2026-06-09)"
# stay inside the parent section: they do not start a new top-level claim.

# In-section URL extractor — kept here so the worksheet text never has to be
# re-loaded by main.py.
_PER_CLAIM_URL_RE = re.compile(r"https?://[^\s<>)\"']+")


def extract_claim_sections_from_review(text: str) -> List[Dict[str, Any]]:
    """Split a worksheet markdown into one section per ``### Claim N`` heading.

    Returns a list of dicts with:
        claim_number: int
        claim_title: str
        section_text: str   (the full text of the claim section)
    """
    if not text:
        return []
    matches = list(_CLAIM_HEADING_RE.finditer(text))
    if not matches:
        return []
    sections: List[Dict[str, Any]] = []
    for idx, match in enumerate(matches):
        number = int(match.group("number"))
        title = (match.group("title") or "").strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        section_text = text[start:end].strip()
        sections.append(
            {
                "claim_number": number,
                "claim_title": title,
                "section_text": section_text,
            }
        )
    # Deduplicate while keeping the first (top-level) occurrence per number.
    seen: Dict[int, Dict[str, Any]] = {}
    for section in sections:
        seen.setdefault(section["claim_number"], section)
    return sorted(seen.values(), key=lambda s: s["claim_number"])


def _extract_section_urls(section_text: str) -> List[str]:
    seen: Dict[str, None] = {}
    for match in _PER_CLAIM_URL_RE.finditer(section_text):
        url = match.group(0).rstrip(".,;:)]>")
        if url not in seen:
            seen[url] = None
    return list(seen.keys())


def summarize_source_strength_queue(
    per_candidate_items: List[Dict[str, Any]],
    per_claim_items: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Aggregate per-candidate + per-claim source verification rows.

    Used by the v0.5.0 Source Strength Summary dashboard panel. Per-tier
    counts are summed across the per-claim view (richer signal); the health
    summary fields are derived from the per-candidate view. The aggregator
    is pure and stateless: it never reads files, never approves, never
    promotes.
    """
    counts = {tier: 0 for tier in SOURCE_TIERS}
    requires_correction_count = 0
    blocked_count = 0
    blocked_candidate_ids: set = set()

    for claim in per_claim_items or []:
        counts["primary_source"] += int(claim.get("primary_source_count") or 0)
        counts["institutional_source"] += int(
            claim.get("institutional_source_count") or 0
        )
        counts["reputable_secondary_source"] += int(
            claim.get("reputable_secondary_count") or 0
        )
        counts["weak_secondary_source"] += int(claim.get("weak_source_count") or 0)
        counts["orientation_only"] += int(claim.get("orientation_only_count") or 0)
        counts["speculative_only"] += int(claim.get("speculative_only_count") or 0)
        counts["no_source"] += int(claim.get("no_source_count") or 0)
        if claim.get("requires_correction"):
            requires_correction_count += 1
        if str(claim.get("verification_status") or "").lower() == "blocked":
            blocked_count += 1
            blocked_candidate_ids.add(str(claim.get("candidate_id") or ""))

    candidates_with_primary = 0
    candidates_with_no_sources = 0
    candidates_with_speculative = 0
    for cand in per_candidate_items or []:
        if int(cand.get("primary_source_count") or 0) >= 1:
            candidates_with_primary += 1
        if str(cand.get("verification_status") or "").lower() == "unsourced":
            candidates_with_no_sources += 1
        elif (
            int(cand.get("source_count") or 0) == 0
            and str(cand.get("strongest_source_tier") or "") == "no_source"
        ):
            candidates_with_no_sources += 1
        if int(cand.get("speculative_only_count") or 0) >= 1:
            candidates_with_speculative += 1

    # Strongest available tier across the queue: walk SOURCE_TIERS from
    # strongest (primary_source) downward and pick the first tier with a
    # non-zero count.
    strongest_available = "no_source"
    for tier in reversed(SOURCE_TIERS):
        if counts.get(tier, 0) >= 1:
            strongest_available = tier
            break
    # Weakest detected tier: walk SOURCE_TIERS from weakest (no_source) up
    # and pick the first tier with a non-zero count.
    weakest_detected = "no_source"
    for tier in SOURCE_TIERS:
        if counts.get(tier, 0) >= 1:
            weakest_detected = tier
            break

    return {
        "total_candidates_reviewed": len(per_candidate_items or []),
        "total_claims_reviewed": len(per_claim_items or []),
        "primary_source_count": counts["primary_source"],
        "institutional_source_count": counts["institutional_source"],
        "reputable_secondary_count": counts["reputable_secondary_source"],
        "weak_secondary_count": counts["weak_secondary_source"],
        "orientation_only_count": counts["orientation_only"],
        "speculative_only_count": counts["speculative_only"],
        "no_source_count": counts["no_source"],
        "requires_correction_count": requires_correction_count,
        "blocked_count": blocked_count,
        "strongest_available_tier": strongest_available,
        "weakest_detected_tier": weakest_detected,
        "candidates_with_primary_sources": candidates_with_primary,
        "candidates_with_no_sources": candidates_with_no_sources,
        "candidates_with_speculative_only_material": candidates_with_speculative,
        "candidates_blocked_from_promotion": len(blocked_candidate_ids),
    }


def summarize_per_claim_verification(
    review_text: Optional[str],
    *,
    claim6_blocked: bool = False,
) -> List[Dict[str, Any]]:
    """Run the engine on each ``### Claim N`` section in a worksheet.

    For each section:
      - URLs are extracted and classified.
      - If the section text contains Tier III speculative tokens, a
        ``speculative_only`` source is added so the per-claim counters
        reflect the lens.
      - ``requires_correction`` is detected via the literal substring
        ``requires_correction`` (case-insensitive) inside the section.
      - For Claim 6 specifically, ``blocked=True`` is forced when
        ``claim6_blocked`` is set (e.g. when the candidate row carries
        ``claim_6_tier_i_allowed: false``).

    Returns one summary dict per claim, sorted by ``claim_number`` ascending.
    """
    sections = extract_claim_sections_from_review(review_text or "")
    summaries: List[Dict[str, Any]] = []
    for section in sections:
        urls = _extract_section_urls(section["section_text"])
        sources: List[Dict[str, str]] = [
            {"name": "", "url": url, "notes": ""} for url in urls
        ]
        section_lower = section["section_text"].lower()
        if any(token in section_lower for token in _SPECULATIVE_TOKENS):
            sources.append(
                {
                    "name": f"Claim {section['claim_number']} speculative lens",
                    "url": "",
                    "notes": "Tier III speculative_lens_only",
                }
            )
        requires_correction = "requires_correction" in section_lower
        is_blocked = bool(claim6_blocked) and section["claim_number"] == 6
        summary = summarize_claim_verification(
            sources,
            blocked=is_blocked,
            requires_correction=requires_correction and not is_blocked,
        )
        summary["claim_number"] = section["claim_number"]
        summary["claim_title"] = section["claim_title"]
        summary["requires_correction"] = requires_correction
        summaries.append(summary)
    return summaries
