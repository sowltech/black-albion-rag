#!/usr/bin/env python3
"""List quarantined Black Albion candidate claim records."""
from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_LEDGER = PROJECT_ROOT / "data" / "raw" / "black_albion_candidate_claims.json"


def load_candidates() -> list[dict[str, object]]:
    if not CANDIDATE_LEDGER.exists():
        raise FileNotFoundError(f"missing candidate ledger: {CANDIDATE_LEDGER}")
    try:
        data = json.loads(CANDIDATE_LEDGER.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"malformed candidate ledger: {exc}") from exc
    if not isinstance(data, list):
        raise ValueError("candidate ledger must be a JSON array")
    return data


def main() -> int:
    try:
        candidates = load_candidates()
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    for candidate in candidates:
        print(
            "\t".join(
                str(candidate.get(key, ""))
                for key in (
                    "candidate_id",
                    "review_status",
                    "risk_level",
                    "origin_type",
                    "origin_url",
                )
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
