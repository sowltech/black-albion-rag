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

Strings, integers, lists, and mappings for `enabled` are rejected. Values such as `"false"`, `"true"`, `"yes"`, `"no"`, `"1"`, `"0"`, `0`, and `1` cannot silently enable the canary.

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

## Recommendation Rules

- Aegis `Accepted` -> `recommend_promote`
- Aegis `Undecided` -> `recommend_hold`
- Aegis `Rejected` -> `recommend_reject`
- Aegis unavailable, timeout, malformed response, schema mismatch, missing decision ID, missing required audit reference, or unknown status -> `recommend_hold`

`recommend_promote` means the claim may proceed to the existing Black Albion operator review path. It is not a final promotion decision.

## Idempotency And History

The adapter derives a deterministic request fingerprint from:

- candidate claim ID;
- canonical claim text;
- sorted evidence IDs;
- sorted source IDs;
- evidence versions;
- adapter version;
- Aegis schema version.

Identical evidence snapshots reuse the existing history entry for that fingerprint. Changed evidence or claim text creates a new fingerprint and a new recommendation history row. The helper returns updated review data but does not write canonical ledgers.

## Rollback

Disable the feature flag and reload the service:

```yaml
aegis_canary:
  enabled: false
```

When disabled, Black Albion makes zero Aegis calls and the existing promotion readiness output remains unchanged. Historical recommendation rows remain inert review evidence.

