"""Hash-chained iteration receipts.

Each iteration of the loop produces exactly one receipt. A receipt's hash
covers its full payload except ``receipt_hash`` itself (obviously) and
``timestamp`` (deliberately variable -- replaying the same logical iteration
at a different wall-clock time must produce the same hash). The hash also
folds in the previous receipt's hash, so the chain can prove nothing was
inserted, removed, reordered, or edited after the fact.

This is an audit trail, not a blockchain: small, deterministic, and only as
clever as it needs to be to catch tampering.
"""
from __future__ import annotations

import json
from hashlib import sha256
from typing import Sequence

from .errors import ReceiptChainError
from .models import IterationReceipt

#: Previous-hash value used by the first receipt in a chain.
GENESIS_HASH = "0" * 64


def canonical_json(receipt: IterationReceipt) -> str:
    """Deterministic JSON serialisation of everything that must be covered
    by the receipt hash. Same logical payload -> same string, always."""
    payload = receipt.model_dump(mode="json", exclude={"receipt_hash", "timestamp"})
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def compute_receipt_hash(receipt: IterationReceipt) -> str:
    """Hash of ``previous_receipt_hash + canonical_json(receipt)``. Computed
    from the receipt's own ``previous_receipt_hash`` field, so this is safe
    to call both when building a new receipt and when re-verifying one that
    already carries a ``receipt_hash``."""
    combined = receipt.previous_receipt_hash + canonical_json(receipt)
    return sha256(combined.encode("utf-8")).hexdigest()


def seal_receipt(receipt: IterationReceipt) -> IterationReceipt:
    """Return a copy of ``receipt`` with ``receipt_hash`` populated."""
    return receipt.model_copy(update={"receipt_hash": compute_receipt_hash(receipt)})


def verify_chain(receipts: Sequence[IterationReceipt]) -> None:
    """Raise ``ReceiptChainError`` if ``receipts`` is not a valid,
    unmodified, contiguous, correctly ordered hash chain starting from
    ``GENESIS_HASH``. Returns ``None`` on success."""
    if not receipts:
        raise ReceiptChainError("receipt chain is empty")

    expected_iterations = list(range(1, len(receipts) + 1))
    actual_iterations = [receipt.iteration for receipt in receipts]
    if actual_iterations != expected_iterations:
        raise ReceiptChainError(
            f"receipt iterations are missing or out of order: {actual_iterations}"
        )

    expected_previous = GENESIS_HASH
    for receipt in receipts:
        if receipt.previous_receipt_hash != expected_previous:
            raise ReceiptChainError(
                f"broken chain at iteration {receipt.iteration}: "
                f"expected previous hash {expected_previous}, "
                f"found {receipt.previous_receipt_hash}"
            )
        recomputed = compute_receipt_hash(receipt)
        if recomputed != receipt.receipt_hash:
            raise ReceiptChainError(
                f"receipt at iteration {receipt.iteration} has been modified "
                f"(hash mismatch)"
            )
        expected_previous = receipt.receipt_hash
