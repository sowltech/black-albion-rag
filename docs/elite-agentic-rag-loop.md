# Elite Governed Agentic RAG Loop

Status: Phase 1 implemented

## Phase 1 implementation status

**Implemented** (`backend/app/agentic_loop/`, tests in `tests/agentic_loop/`,
239 tests total including full existing-suite regression):

- Typed request/result/receipt contracts (`models.py`), including the
  `LoopState` state machine with an explicit transition table and typed
  `InvalidTransitionError` / `TerminalStateError` on misuse.
- Mode presets (fast/deep/proof), hard budget ceilings that clamp any
  caller-supplied override, and the evidence-scoring and information-gain
  weight tables (`policy.py`).
- Deterministic query planning, normalisation, and repeated-query detection
  (`planner.py`) via a configuration-driven `StaticPlanner` test double.
- A read-only `Retriever` protocol plus a deterministic in-memory test
  double (`retriever.py`); no network or vector-database calls anywhere in
  Phase 1.
- Evidence scoring from documented weights and deduplication that preserves
  independent corroboration (`scorer.py`).
- Structural gap detection over subquestions/evidence/contradictions
  (`gap_detector.py`) -- no generative semantic judgement.
- Contradiction lifecycle: structural pairing from evidence
  `supports_claims`/`opposes_claims`, materiality classification, and
  explicit reasoned resolution (never automatic from a score comparison)
  (`contradiction.py`).
- The information-gain formula and the single authoritative
  continue/synthesise/stop/escalate governor covering every mandatory stop
  rule (`governor.py`).
- Hash-chained, tamper-evident iteration receipts with a documented
  canonical-serialisation and verification routine (`receipts.py`).
- Deterministic, non-generative synthesis that runs with no LLM present
  (`synthesiser.py`).
- The orchestration service wiring all of the above into the state machine,
  with typed-error and unexpected-exception boundaries mapped to
  `INTERNAL_ERROR` (`service.py`).
- Direct test coverage for every terminal outcome:
  `ANSWERED`, `PARTIAL_EVIDENCE`, `INSUFFICIENT_EVIDENCE`,
  `CONTRADICTION_UNRESOLVED`, `BUDGET_EXHAUSTED`, `NO_INFORMATION_GAIN`,
  `REPEATED_QUERY`, `OPERATOR_REVIEW_REQUIRED`, `POLICY_BLOCKED`.

**Designed, not yet wired** (this document's contract, ahead of adapter work):

- The exact `/agentic-query` API surface below (request/response shape is
  stable; the FastAPI route itself is Phase 3).

**Deferred to later phases** (see "Delivery phases" below):

1. A read-only adapter from `Retriever` onto the real Black Albion ledgers
   (`backend/app/retriever.py`, `data/raw/*.json`). Phase 1 runs entirely
   against `InMemoryRetriever` fixtures.
2. Semantic (as opposed to structural) contradiction and gap detection once
   real ledger content is available to reason over.
3. `/agentic-query` and run-inspection API endpoints, dashboard visibility,
   and proof-bundle export.
4. Stable SCROLLMIND / Brain API contract and local/remote model routing.
5. Governed candidate proposals behind explicit operator approval.

## Safety boundaries confirmed by Phase 1

- **Canonical / candidate writes**: nothing in `backend/app/agentic_loop/`
  imports or calls any ledger-write path. `policy.forbid_canonical_write`
  and `errors.CanonicalWriteDeniedError` exist specifically so this
  invariant is a concrete, raisable, testable assertion rather than only a
  comment.
- **Automatic promotion**: there is no code path from a `TerminalOutcome`
  to a canonical write. `ANSWERED` is a returned `AgenticResult`, nothing
  more.
- **Tier mutation**: `scorer.score_evidence` only ever updates
  `overall_score`; it never touches `EvidenceItem.tier`. Tier III material
  cannot become Tier I evidence anywhere in this package.
- **Contradiction preservation**: contradictions are never deleted, and are
  never resolved except through an explicit, reasoned call to
  `contradiction.resolve_partially` / `resolve_fully` / `escalate` supplying
  a non-empty reason and evidence IDs that are actually part of the
  contradiction. The orchestration loop itself never calls these -- Phase 1
  has no automatic resolution path.

## Purpose

Build a bounded retrieval loop that plans, retrieves, scores, detects gaps, resolves contradictions, verifies claims, and stops for an explicit reason. It must improve retrieval without weakening Black Albion's evidence tiers or operator-controlled promotion.

This is a governed inquiry engine, not an autonomous truth writer.

## Invariants

1. Canonical ledgers stay read-only during loop execution.
2. Candidate material remains quarantined until a separate operator-approved promotion commit.
3. Every generated claim references evidence IDs or is labelled unsupported.
4. Tier III material never becomes Tier I evidence.
5. Every iteration emits an immutable receipt.
6. Continued iterations require measurable evidence gain or a targeted contradiction-resolution attempt.
7. Equivalent repeated queries trigger a stop.
8. Budget exhaustion returns a bounded partial result, never an invented conclusion.
9. Durable knowledge writes are denied by default.
10. All model and retrieval behaviour must support deterministic test doubles.

## State machine

As implemented in `models.py` (`LoopState`, `TRANSITIONS`,
`validate_transition`):

```text
RECEIVED -> DECOMPOSING -> PLANNING -> RETRIEVING -> SCORING
  -> ASSESSING_GAPS -> ASSESSING_CONTRADICTIONS -> GOVERNING
GOVERNING -> PLANNING            (continue: budgets remain, gap addressable)
GOVERNING -> SYNTHESISING        (every other governor decision)
SYNTHESISING -> COMPLETED        (outcome == ANSWERED)
SYNTHESISING -> STOPPED          (every other outcome)
<any non-terminal state> -> FAILED   (unexpected error; INTERNAL_ERROR)
```

`COMPLETED`, `STOPPED`, and `FAILED` are terminal: `validate_transition`
raises `TerminalStateError` if asked to leave one, and
`InvalidTransitionError` for any edge not listed above (including skipping a
state). One iteration's receipt is emitted per full pass through
`GOVERNING`.

Terminal outcomes:

- `ANSWERED`
- `PARTIAL_EVIDENCE`
- `INSUFFICIENT_EVIDENCE`
- `CONTRADICTION_UNRESOLVED`
- `BUDGET_EXHAUSTED`
- `NO_INFORMATION_GAIN`
- `REPEATED_QUERY`
- `POLICY_BLOCKED`
- `OPERATOR_REVIEW_REQUIRED`
- `INTERNAL_ERROR`

## Request contract

```json
{
  "question": "string",
  "mode": "fast|deep|proof",
  "include_tiers": ["I", "II"],
  "max_iterations": 5,
  "max_retrieval_calls": 12,
  "max_evidence_items": 50,
  "minimum_answer_confidence": 0.80,
  "minimum_iteration_gain": 0.05,
  "require_primary_sources": false,
  "allow_external_retrieval": false,
  "operator_id": "optional-string"
}
```

## Evidence model

Each evidence item records stable IDs, content hash, source locator, tier, source type, retrieval time, and decomposed scores for relevance, authority, freshness, provenance, consistency, and independence.

Initial combined score:

```text
0.30 relevance + 0.20 authority + 0.15 provenance +
0.10 freshness + 0.15 consistency + 0.10 independence
```

A high score never overrides tier policy.

## Evidence gain

Evidence gain is derived from observable changes, not model self-report:

```text
0.35 new subquestion coverage +
0.25 new high-quality evidence ratio +
0.20 contradiction reduction +
0.10 source independence gain +
0.10 confidence delta
```

Continue only when gain clears the configured threshold, a material contradiction has a targeted next query, or proof mode still lacks a mandatory source class.

## Contradictions

Contradictions must preserve the normalised proposition, supporting evidence IDs, opposing evidence IDs, materiality, resolution status, and resolution basis. The synthesiser may not silently average incompatible claims. Unresolved material contradictions remain visible in the final result.

## Loop governor

Default budgets:

| Mode | Iterations | Retrieval calls | Evidence items |
|---|---:|---:|---:|
| fast | 2 | 4 | 15 |
| deep | 5 | 12 | 50 |
| proof | 7 | 20 | 80 |

Hard stops:

- iteration, retrieval-call, or evidence-item budget reached
- repeated equivalent query
- two consecutive iterations below minimum gain
- no addressable material gap remains
- policy violation
- operator review requirement

## Output contract

Every final response contains:

- answer
- supported claims with evidence IDs
- unsupported or weak claims
- contradictions
- decomposed confidence
- terminal outcome and stop reason
- iteration count
- receipt-chain hash
- operator-review recommendation

No response is marked `ANSWERED` while a required subquestion remains unsupported.

## Memory policy

Automatically allowed: run manifests, receipts, query hashes, evidence references, scores, stop reasons, and final response artifacts.

Automatically denied: canonical promotion, source-ledger mutation, tier changes, deletion of contradictory evidence, and rewriting existing historical claims.

Candidate proposals may be added later only through quarantine plus explicit operator approval.

## Package structure

```text
backend/app/agentic_loop/       # Phase 1: implemented, listed in delivery order
  errors.py
  models.py
  policy.py
  planner.py
  retriever.py
  scorer.py
  gap_detector.py
  contradiction.py
  governor.py
  receipts.py
  synthesiser.py
  service.py

tests/agentic_loop/             # 114 tests, plus 125 pre-existing (239 total)
  test_models.py
  test_policy.py
  test_planner.py
  test_scorer.py
  test_gap_detector.py
  test_contradiction.py
  test_governor.py
  test_receipts.py
  test_service.py
```

Claim verification against evidence is not a separate module: it is the
combined result of `scorer.py` (decomposed, tier-aware scores),
`contradiction.py` (never silently averaging incompatible claims), and
`synthesiser.py` (a subquestion is only reported supported when Tier I/II
evidence backs it and no unresolved contradiction touches that evidence).
`test_api.py` moves to Phase 3 once `/agentic-query` exists to test against.

## API boundary

```text
POST /agentic-query
GET  /agentic-runs/{run_id}
GET  /agentic-runs/{run_id}/receipts
```

The first release remains read-only with respect to canonical ledgers.

## Delivery phases

1. Deterministic loop kernel, policy, budgets, receipts, hashes, and stop-condition tests.
2. Read-only adapter over existing Black Albion canonical and candidate ledgers.
3. API endpoints, run inspection, dashboard visibility, and proof-bundle export.
4. Stable SCROLLMIND / Brain API contract and local-model routing interface.
5. Optional governed candidate proposals behind operator approval.

## Required tests

- repeated-query stop
- two no-gain iterations stop
- each budget stop independently
- Tier III non-elevation
- unresolved contradiction visibility
- deterministic receipt hashes
- partial result rather than fabricated evidence
- automatic canonical-write rejection
- provenance preservation
- crash-safe reconstruction
- duplicate evidence detection by content hash
- proof-mode primary-source requirement
- unsupported claim visibility
- explicit terminal outcome on every path
- existing Black Albion validation remains green

## Definition of elite

Bounded, explainable, deterministic under test, provenance-preserving, contradiction-aware, tier-safe, crash-reconstructable, budget-controlled, operator-governed, and exposed through a stable API.
