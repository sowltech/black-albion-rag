# Aegis Consumer Canary

Black Albion can request a Sirius Nexus Aegis recommendation for candidate-claim review. This is a disabled-by-default canary and does not change the Black Albion authority model.

## Boundary

The canary is recommendation-only:

- it never promotes claims;
- it never changes evidence tiers;
- it never mutates source records;
- it never marks a claim verified;
- it never bypasses the existing operator review flow;
- it does not copy or reimplement Aegis reasoning;
- it does not read or write Aegis JSON state directly.

The narrow insertion point is:

```text
candidate claim review -> Aegis recommendation -> existing Black Albion human/operator decision
```

## Configuration

Default state is disabled. A missing config file or absent `aegis_canary.enabled` value is disabled. YAML `null` for `aegis_canary` or `enabled` is also disabled.

Only lowercase YAML booleans are accepted:

- `true` enables the canary.
- `false` disables the canary.

Accepted values:

```yaml
aegis_canary:
  enabled: false
```

```yaml
aegis_canary:
  enabled: true
  base_url: http://localhost:8055
  timeout_seconds: 2.0
  excerpt_limit: 500
  require_audit_reference: true
```

Strings, integers, lists, and mappings for `enabled` are rejected. Values such as `"false"`, `"true"`, `yes`, `no`, `on`, `off`, `True`, `False`, `TRUE`, `FALSE`, `"1"`, `"0"`, `0`, and `1` cannot silently enable the canary. The adapter uses a PyYAML SafeLoader variant whose boolean resolver is restricted to lowercase `true` and `false`.

Duplicate YAML mapping keys are rejected at every mapping depth. Ambiguous configuration such as repeating `aegis_canary` or repeating `enabled` fails closed before feature activation, makes zero Aegis calls, and creates no recommendation history.

## Mapping

| Black Albion field | Aegis field |
| --- | --- |
| `candidate_claim_id` / `claim_id` | claim metadata and deterministic claim ID |
| `claim_text` | Aegis claim statement |
| `tier_candidate` | evidence tier metadata and conservative score default |
| `attached_source_names` / `supporting_source_names` | supporting evidence |
| `opposing_source_names` / `contradicting_source_names` | attacking evidence |
| `source_artifact`, `source_review_file`, `operator_packet_file`, `review_note` | provenance references |
| `source_attachment_pass` / candidate `created_at` | evidence freshness signal |

Tier score defaults are adapter rules, not new Black Albion evidence tiers:

- Tier I: `0.95`
- Tier II: `0.70`
- Tier III: `0.35`
- missing or unknown: `0.50`

If required provenance is absent, the canary returns `recommend_hold`.

The adapter depends on `PyYAML>=6.0,<7`, matching the repository's minimum-bound style while preventing an unreviewed major-version jump.

## Recommendation Rules

- Aegis `Accepted` -> `recommend_promote`
- Aegis `Undecided` -> `recommend_hold`
- Aegis `Rejected` -> `recommend_reject`
- Aegis unavailable, timeout, malformed response, schema mismatch, missing decision ID, missing required audit reference, or unknown status -> `recommend_hold`

`recommend_promote` means the claim may proceed to the existing Black Albion operator review path. It is not a final promotion decision.

## Idempotency And History

The adapter derives a deterministic request fingerprint from a stable JSON payload using `sort_keys=True`, compact separators, NFC Unicode normalization, and whitespace collapse. The payload includes:

- candidate claim ID, canonical claim text, claim content hash, candidate status, module/domain, evidence tier, claim version, and provenance references;
- each evidence ID, canonical excerpt, excerpt content hash, source ID, source title, evidence tier, authority score, quality score, freshness timestamp, relationship polarity, evidence version, and provenance reference;
- sorted source IDs, source titles, source tiers, source authority scores, source versions, and source provenance references;
- adapter version, mapping-rule version, Aegis schema version, and canonicalization version.

Identical evidence snapshots reuse the existing history entry for that fingerprint. Shuffled evidence/source ordering, stable JSON key ordering, equivalent whitespace, and equivalent Unicode after NFC normalization do not change the fingerprint. Material changes to evidence text, source identity, source title, evidence tier, authority score, quality score, freshness, relationship polarity, provenance, claim text, claim/evidence version, adapter version, mapping version, or Aegis schema version create a new fingerprint and a new recommendation history row.

Recommendation history is returned as inert review data by the helper. It is not a persistent database claim unless a future Black Albion storage path explicitly writes it.

## Rollback

Disable the feature flag and reload the service:

```yaml
aegis_canary:
  enabled: false
```

When disabled, Black Albion makes zero Aegis calls and the existing promotion readiness output remains unchanged. Historical recommendation rows remain inert review evidence.
