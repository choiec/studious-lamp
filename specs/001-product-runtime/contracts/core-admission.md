# Owner Contract Plan: Core Admission and Product Effects

**Owner**: Studious Lamp

**Release identity**: `UNESTABLISHED` pending the first owner contract implementation task

**Current status**: Contract, implementation, release candidate, publication, and runtime `NOT RUN`

## Public Contract Sources

```text
contracts/core-admission/openapi.yaml
contracts/core-admission/handoff-reference.schema.json
contracts/core-admission/conformance/positive.json
contracts/core-admission/conformance/negative.json
contracts/repositoryd/openapi.yaml
contracts/duckdbd/openapi.yaml
```

The Core Admission API and Handoff Reference form one independently versioned control-plane
release. The repositoryd and duckdbd service contracts are separate internal owner boundaries and
are not Candidate-content artifacts.

## Handoff Reference Semantics

The exact serialized contract must bind:

```text
handoff_reference_contract_version
handoff_reference_contract_sha256
environment_id
space_id
manifest_resource_id
remote_manifest_precondition { version_id, readback_size_bytes, readback_sha256 }
candidate_id
candidate_contract_release_id
candidate_contract_release_manifest_sha256
candidate_manifest_sha256
export_receipt_id
```

The remote readback SHA-256 equals the Candidate-manifest SHA-256. Stable environment, Space,
manifest-resource, and strong version/readback evidence are mandatory. A path, timestamp, ACL,
owner, upload, sync state, producer assertion, or weak/absent precondition cannot substitute.

Credentials, oCIS principal, Core caller principal, binding name, display-only locator, local/sync
path, mutable selector, private profile, raw provenance, and unrelated internal fields are
forbidden.

## Admission Request and Ordering

The exact request binds an authenticated Core context, operation `admit_candidate`, stable
submission/idempotency identity, expected Candidate/release/manifest digests, and one Handoff
Reference.

Core processes:

1. request bounds and syntax;
2. caller authentication independent of oCIS;
3. exact Handoff contract validation;
4. idempotency binding;
5. operation/resource authorization;
6. independent conditional intake through the Core reader port;
7. manifest/inventory/payload size and digest verification;
8. contract validation and concurrent-mutation detection;
9. wire-to-owner-model mapping;
10. Core-controlled immutable snapshot persistence/readback; and
11. admission decision only.

Authorization denial leaves retrieval and all effects `NOT_ATTEMPTED`. Any missing, extra,
duplicate, unsafe, malformed, changed, unsupported, or mismatched value rejects acceptance.

## Lifecycle Contracts

These operations are independent:

```text
assign_product_identity
publish_product_object
adopt_product
update_projection
```

Each has its own authentication, authorization, idempotency key, prerequisites, request digest,
outcome, and reconciliation. Absence of a request means `NOT_ATTEMPTED`; timeout after dispatch
means `UNCERTAIN`, followed by owner-interface readback before retry.

Canonical publication uses only the Core snapshot through repositoryd. Adoption/projection uses
Core records through duckdbd. repositoryd never invokes duckdbd, duckdbd never invokes
repositoryd, Core never opens their storage directly, and later effects never re-read oCIS.

## Delivery Contracts

```text
src/studious_lamp/delivery/http.py
src/studious_lamp/delivery/mcp.py
src/studious_lamp/delivery/agent_plugin.py
tests/delivery/test_interfaces.py
```

All three adapters map into the same application authentication, authorization, admission, and
lifecycle use cases. Exact protocol versions, paths/methods, authentication mechanism, reason-code
vocabulary, and bounds are selected and pinned in the implementation task; no endpoint or runtime
binding is guessed by this plan.

## Conformance and Failure Cases

```text
tests/contracts/test_core_admission.py
tests/core/test_authorization.py
tests/core/test_handoff_mapping.py
tests/core/test_admission.py
tests/core/test_lifecycle.py
tests/core/test_replay.py
tests/core/test_response_loss.py
tests/integration/test_ocis_intake.py
tests/integration/test_repositoryd.py
tests/integration/test_duckdbd.py
```

Required cases include unsupported/mismatched version or digest; missing/weak remote precondition;
forbidden Handoff fields; exact and conflicting replay; authorization denial; remote mutation;
snapshot failure; accepted admission with later effects `NOT_ATTEMPTED`; repositoryd-only
publication; duckdbd-only adoption/projection; independent partial outcomes; lost response;
post-admission oCIS denial; direct-storage denial; and zero repositoryd-to-duckdbd path.

## Deterministic Release Candidate

```text
tools/build_core_admission_release.py
tools/verify_release.py
build/releases/core-admission/manifest.json
build/releases/core-admission/checksums.sha256
build/releases/core-admission/provenance.json
```

The first contract task selects the exact pre-1.0 version/tag and complete release inventory in
the contract/build sources. Local candidate verification requires exact inventory, byte-identical
rebuild, positive/negative conformance, implementation agreement, checksums/provenance, tracked
Apache-2.0, and exact distributable/third-party/NOTICE checks. Publication and remote readback are
separate and initially `NOT RUN`.

## Evidence Outputs

```text
docs/evidence/umbrella-001/T012-core-admission-api.json
docs/evidence/umbrella-001/T013-release-readback.json
docs/evidence/umbrella-001/T017-independent-intake.json
docs/evidence/umbrella-001/T018-core-lifecycle.json
docs/evidence/umbrella-001/T019-persistence-boundaries.json
docs/evidence/umbrella-001/T020-core-public-interface.json
docs/evidence/umbrella-001/alpha/AT-009-handoff-integrity-negative.json
docs/evidence/umbrella-001/alpha/AT-010-core-authorization.json
docs/evidence/umbrella-001/alpha/AT-011-admission-separation.json
docs/evidence/umbrella-001/alpha/AT-012-repository-publication.json
docs/evidence/umbrella-001/alpha/AT-013-duckdb-adoption.json
docs/evidence/umbrella-001/alpha/AT-015-exact-conflicting-replay.json
docs/evidence/umbrella-001/alpha/AT-016-lost-response.json
```

Owner acceptance evidence may report only its exact source/test scope. Alpha files remain
`NOT RUN` until separate entry and execution authorization; no T004 artifact creates those files.
