# Data Model: Studious Product Runtime

**Status**: Logical owner model; physical schemas and runtime state `NOT RUN`

## Modeling Rules

1. Studious is the sole semantic owner of every entity in this document.
2. Public wire values are boundary DTOs and are mapped into owner-local models.
3. oCIS transfer state is non-authoritative; accepted bytes live in Core-controlled custody.
4. Admission, identity, publication, adoption, and projection are independent effects.
5. repositoryd owns canonical bytes; duckdbd owns persistent relational state.
6. Every ambiguous dispatch records `UNCERTAIN` and is reconciled before retry.

## Contract Release Entities

### CandidateContentRelease

One exact public release with:

```text
release_version = 0.1.0
release_tag = contract-v0.1.0
source_revision
source_tree_sha256
manifest_sha256
artifact[4] { name, contract_version, media_type, byte_size, sha256, locator }
conformance/provenance/checksum evidence
license/distribution evidence
publication_result = PASS | FAIL | NOT RUN | UNESTABLISHED
```

Invariants: exactly four named schemas; no Core API/Handoff component; no Extractor Protocol;
evidence files are not schemas; local candidate and immutable publication are separate results.

### CoreAdmissionRelease

An independently versioned public release with:

```text
release_id + version + tag
source_revision + source_tree_sha256
manifest/checksum/provenance/conformance identities
Core Admission API component identity/digest
Handoff Reference component identity/digest
publication_result = PASS | FAIL | NOT RUN | UNESTABLISHED
```

Its version and tag remain `UNESTABLISHED` until the owner contract task completes. No field is
inferred from Candidate content.

### HandoffReference

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

The readback SHA-256 equals the Candidate-manifest SHA-256. Credentials, principals, bindings,
display paths, local paths, mutable selectors, private profiles, and raw provenance are forbidden.

## Admission Entities

### AdmissionRequest

```text
submission_id
idempotency_key
authenticated_request_context_id
operation = admit_candidate
handoff_reference
expected_candidate_id
expected_candidate_manifest_sha256
expected_candidate_contract_release_id
requested_at
```

The idempotency binding covers operation, reference, expected bytes, and policy revision. A changed
binding under the same key is a conflict.

### AuthorizationRecord

```text
authorization_record_id
request_context_id
operation
resource_binding_sha256
policy_revision
decision = ALLOWED | DENIED
reason_code
decided_at
```

The record is Core-created. The oCIS user, edge identity, or caller-supplied decision cannot replace
it. Denial leaves intake and every later effect `NOT_ATTEMPTED`.

### CandidateRetrievalEvidence

```text
admission_request_id
handoff_reference_sha256
remote_precondition_before + remote_precondition_after
retrieved_manifest_bytes + recomputed_sha256
received_inventory[] { normalized_path, byte_size, sha256 }
contract_validation_result
findings[]
terminal_status
```

State:

```text
NOT_ATTEMPTED
  -> RETRIEVING
  -> REMOTE_PRECONDITION_VERIFIED
  -> MANIFEST_VERIFIED
  -> PAYLOADS_VERIFIED
  -> CONTRACTS_VALIDATED
  -> SNAPSHOT_RECORDED
  -> REJECTED_<REASON>
```

Missing, extra, duplicate, unsafe, malformed, changed, or mismatched content rejects before
acceptance.

### VerifiedCandidateSnapshot

```text
snapshot_id
admission_request_id
retrieval_evidence_id
manifest_exact_bytes + sha256
payload_inventory[] + exact retained bytes
candidate_contract_release_id + release_manifest_sha256
snapshot_sha256
created_at
readback_evidence
recovery_reference
```

The snapshot is immutable Core custody, not repositoryd publication. Failure to persist or read it
back blocks acceptance.

### AdmissionRecord

```text
RECEIVED
  -> AUTHORIZATION_DENIED
  -> AUTHORIZED
  -> RETRIEVING
  -> BYTES_VERIFIED
  -> CONTRACTS_VALIDATED
  -> SNAPSHOT_RECORDED
  -> ACCEPTED | REJECTED
```

An accepted record links one request, authorization, retrieval evidence, snapshot, contract pins,
and replay result. It creates no later request.

## Product Lifecycle Entities

### LifecycleEffectRequest

One request for exactly one operation:

```text
assign_product_identity
publish_product_object
adopt_product
update_projection
```

Each request includes its own authenticated context, authorization record, idempotency identity,
policy revision, prerequisite Core record IDs/digests, and requested input digest.

### LifecycleEffectOutcome

```text
NOT_ATTEMPTED
  -> REQUESTED
  -> AUTHORIZATION_DENIED
  -> STARTED
  -> SUCCEEDED | FAILED | UNCERTAIN
  -> RECONCILED
```

Every outcome records attempt IDs, exact input digest, owner interface, result/poststate digest,
times, and reconciliation evidence. No outcome auto-creates another request.

### ProductIdentity

Studious-assigned identity linked to an accepted AdmissionRecord and VerifiedCandidateSnapshot.
Automatic Candidate ID is evidence, not product identity.

### CanonicalPublication

repositoryd-owned immutable bytes/manifests created only through the Core Canonical Publication
Port. The record binds product identity, snapshot digest, idempotency key, repositoryd result, and
owner-interface readback.

### ProductStateRecord

duckdbd-owned authoritative relations/events created only through the Core Product State Port.
Only duckdbd opens or writes the persistent DuckDB file. Adoption and projection remain separate
requests/outcomes.

## Delivery and Evidence Entities

### DeliveryRequestContext

A transport-specific authenticated context mapped into the owner-local request context. HTTP, MCP,
and Agent Plugin request/response details remain outside domain/application models.

### OwnerEvidenceRecord

```text
task_or_scenario_id
status = PASS | FAIL | NOT RUN | UNESTABLISHED
owner_repository
source_revision + source_tree
command_or_method
fixture/input identities
started_at + finished_at
evidence_locator + sha256
limitations
```

An evidence record never embeds secrets, PII, real educational content, private profiles, raw
provenance, or credential-bearing URLs.

### PublicationReadbackSlots

T013 contains two independent slots:

```text
candidate_content { authorization, publication, immutable_readback, status }
core_api_handoff { authorization, publication, immutable_readback, status }
```

One slot may pass while the other remains `NOT RUN` or `UNESTABLISHED`; neither depends on the
other.

## Relationships and Ownership

```text
CandidateContentRelease ---- validated by ----> CandidateRetrievalEvidence
CoreAdmissionRelease ------ shapes ----------> AdmissionRequest/HandoffReference
AdmissionRequest ---------- authorized by ---> AuthorizationRecord
CandidateRetrievalEvidence -> retained as ----> VerifiedCandidateSnapshot
VerifiedCandidateSnapshot -> accepted by ----> AdmissionRecord
AdmissionRecord ---------- prerequisite of --> ProductIdentity
ProductIdentity + Snapshot -> publication ----> CanonicalPublication (repositoryd)
ProductIdentity + Publication -> adoption ----> ProductStateRecord (duckdbd)
ProductStateRecord + CanonicalPublication -> projection through duckdbd
```

There is no Automatic model import, repositoryd-to-duckdbd edge, direct Core storage edge, or
post-admission oCIS edge.

## Recovery Classification

| Class | Authority | Recovery source | Required readback |
|---|---|---|---|
| Verified snapshots/admission/effects | Core | Core-consistent backup | request/snapshot/contract/digest links |
| Canonical product objects | repositoryd | repositoryd-consistent backup | object/manifest digest through repositoryd |
| Authoritative product state | duckdbd | duckdbd-consistent backup | schema/migration/relation readback through duckdbd |
| Projections | Rebuildable Studious state | canonical objects plus product records | comparison after rebuild |

Recovery implementation and execution are not T004 effects. No admitted state may be reconstructed
by silently re-reading oCIS.
