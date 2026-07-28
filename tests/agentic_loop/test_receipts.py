import pytest

from backend.app.agentic_loop.errors import ReceiptChainError
from backend.app.agentic_loop.models import BudgetSnapshot, GovernorAction, IterationReceipt
from backend.app.agentic_loop.receipts import GENESIS_HASH, seal_receipt, verify_chain


def _budget(remaining=5):
    return BudgetSnapshot(
        iterations_remaining=remaining,
        retrieval_calls_remaining=remaining,
        evidence_items_remaining=remaining,
    )


def _raw_receipt(iteration, previous_hash, timestamp="2026-01-01T00:00:00Z"):
    return IterationReceipt(
        run_id="run-1",
        iteration=iteration,
        state_before="PLANNING",
        queries_issued=[f"q-{iteration}"],
        evidence_seen=[f"ev-{iteration}"],
        new_evidence_ids=[f"ev-{iteration}"],
        duplicate_evidence_ids=[],
        coverage_before=0.0,
        coverage_after=0.5,
        confidence_before=0.0,
        confidence_after=0.5,
        evidence_gain=0.3,
        contradictions_opened=[],
        contradictions_resolved=[],
        budget_before=_budget(5),
        budget_after=_budget(4),
        decision=GovernorAction.CONTINUE,
        decision_reason="CONTINUE_ITERATING: budgets remain",
        previous_receipt_hash=previous_hash,
        receipt_hash="",
        timestamp=timestamp,
    )


def _chain(n):
    receipts = []
    previous = GENESIS_HASH
    for i in range(1, n + 1):
        sealed = seal_receipt(_raw_receipt(i, previous))
        receipts.append(sealed)
        previous = sealed.receipt_hash
    return receipts


def test_valid_chain_verifies():
    receipts = _chain(3)
    verify_chain(receipts)  # must not raise


def test_first_receipt_uses_genesis_hash():
    receipts = _chain(1)
    assert receipts[0].previous_receipt_hash == GENESIS_HASH


def test_same_logical_payload_same_hash_regardless_of_timestamp():
    a = seal_receipt(_raw_receipt(1, GENESIS_HASH, timestamp="2026-01-01T00:00:00Z"))
    b = seal_receipt(_raw_receipt(1, GENESIS_HASH, timestamp="2099-12-31T23:59:59Z"))
    assert a.receipt_hash == b.receipt_hash


def test_different_payload_different_hash():
    a = seal_receipt(_raw_receipt(1, GENESIS_HASH))
    b = seal_receipt(_raw_receipt(1, GENESIS_HASH))
    b = b.model_copy(update={"evidence_gain": 0.9})
    assert compute_hash_differs(a, b)


def compute_hash_differs(a, b):
    from backend.app.agentic_loop.receipts import compute_receipt_hash

    return compute_receipt_hash(a) != compute_receipt_hash(b)


def test_modified_receipt_detected():
    receipts = _chain(2)
    tampered = receipts[1].model_copy(update={"evidence_gain": 0.999})
    with pytest.raises(ReceiptChainError):
        verify_chain([receipts[0], tampered])


def test_missing_receipt_detected():
    receipts = _chain(3)
    with pytest.raises(ReceiptChainError):
        verify_chain([receipts[0], receipts[2]])


def test_reordered_receipts_detected():
    receipts = _chain(3)
    with pytest.raises(ReceiptChainError):
        verify_chain([receipts[1], receipts[0], receipts[2]])


def test_broken_genesis_detected():
    bad_first = seal_receipt(_raw_receipt(1, "not-the-genesis-hash".ljust(64, "0")))
    with pytest.raises(ReceiptChainError):
        verify_chain([bad_first])


def test_empty_chain_rejected():
    with pytest.raises(ReceiptChainError):
        verify_chain([])
