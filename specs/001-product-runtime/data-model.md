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

## Semantic Content Wire Model (T042 authority)

These are Studious-normalized JSON records, not official QTI JSON names. Their implementation
belongs inside `contracts/candidate-content/semantic-content.schema.json.$defs`; there is one
Resource shape, one Item shape and exactly twelve interaction branches. No new artifact is added.
All fields listed below are required unless marked `?`; every object, including metadata,
references, targets and nested payload records, is closed. Optional metadata containers may be
empty. IDs are opaque 1–128 character tokens matching `[A-Za-z0-9][A-Za-z0-9._-]{0,127}`;
revisions, language tags, type/role labels and strategy references are nonempty strings. Numeric
measurements/scores are finite; confidence is in [0,1], max_score is nonnegative.

```text
SemanticContent {schema="semantic-content.schema.json", resources: Resource[], items: Item[]}
Resource {resource_id, revision, resource_type, language, content_blocks: Block[], assets: Asset[],
          standard_metadata: StandardMetadata, extensions: ResourceExtensions, provenance_refs: ID[]}
Block {block_id, type, segments: Segment[]}
Segment {segment_id, type, text: nonempty string, source_anchor?: SourceAnchor}
SourceAnchor {provenance_ref, page: positive integer, block: block_id}
Asset {asset_id, payload_path: normalized Candidate payload path, media_type}
Item {item_id, revision, resource_refs: ResourceRef[], task: Task, content_parts: ContentPart[],
      overlays: Overlay[], interaction: Interaction, response_declarations: ResponseDeclaration[],
      scoring: Scoring, standard_metadata: StandardMetadata, extensions: ItemExtensions,
      provenance_refs: ID[]}
ResourceRef {resource_id, usage}
Task {taxonomy_id, type, skill}
Scoring {strategy, max_score: number}
ContentPart {part_id, role, content: Content, analysis_target: {egp: boolean, evp: boolean}}
Content = {kind="inline_text", language, text: nonempty string}
        | {kind="resource_segments", resource_id, segment_ids: ID[1..]}
```

Top-level arrays may be empty (a resource-only or Item-only transfer is representable). Resource
content_blocks/assets may be empty individually; Item content_parts/response_declarations and
provenance_refs are nonempty. Every interaction collection below is nonempty. Resource type is
exactly passage/shared_stimulus/table/chart/notice/image/audio/mixed; block and segment types are
subject-neutral labels, not hidden source layout. The synthetic fixture uses paragraph/sentence.
taxonomy_id/type/skill identify a pinned subject taxonomy without encoding a CSAT-only common Item.

### Identity, custody and disclosure-safe anchors

Resource IDs and Item IDs are unique in the document. Blocks/segments/assets are unique within
their Resource (segments are Resource-wide, not block-local); parts, overlays, options, slots,
tokens, responses, gaps, entries and edit targets are unique within their respective Item/kind.
Revisions bind immutable content. Reuse references the existing Resource/segment, never a revised
copy with blanks, marks, insertions or edits. A stimulus part matching declared Resource text
must use resource_segments, not a second authoritative inline_text copy. Unrelated Item-only
questions/options are separate text, not rejected merely for a coincidental substring match.

`source_anchor` is optional but, when present, contains all three requested fields. `page` is a
one-based page index in a disclosure-reviewed public rendition, **not the private original page
number**; `block` is the public Block.block_id, not a source coordinate or source block name.
`provenance_ref` resolves to an opaque disclosure-safe projection identity. Thus the requested
source relationship is preserved by a public projection; raw-source coordinates are deliberately
not represented. If that projection cannot be made safely, omit the whole optional anchor and
retain stable Resource/block/segment identity; do not invent a page or publish private geometry.
The private-to-public mapping remains producer-private. There are no paths, URLs, source names,
bounding boxes or raw provenance in anchors. Schema acceptance cannot establish that real values
were reviewed or authorize publication.

For this four-artifact revision, every provenance_refs/anchor.provenance_ref resolves to the one
opaque `candidate.provenance.value` projection identity already supported by provenance.schema.json.
The fixture uses `provenance-synthetic-1`. This narrows the use of that existing nonempty string;
it neither expands the provenance schema nor invents an embedded provenance registry. Multiple
projection records would need a separately coordinated contract change. Assets bind existing
Candidate payload paths/media types; actual bytes and projection bindings are Core validation.

### Standard metadata versus producer-specific extensions

```text
StandardMetadata {ieee_lom?: {educational?: {difficulty?: Difficulty}},
                  oneedtech_common_cartridge?: {textComplexity?: Measurement[]}}
Difficulty {source="LOMv1.0", value: enum[very easy, easy, medium, difficult, very difficult]}
Measurement {scheme, version, source, scale, score: number, unit}
ResourceExtensions {automatic_disco: {target_audience: ID[], language_profile: LanguageProfile}}
LanguageProfile {cefr?: {level, method, confidence: number}, egp_mappings: EgpRef[], evp_mappings: EvpRef[]}
EgpRef {scheme, version, source, grammar_id, relationship: enum[exact, partial, supplemental],
        review_status: enum[unreviewed, confirmed, rejected]}
EvpRef {scheme, version, source, profile_entry_id, sense, pos}
ItemExtensions {automatic_disco: {difficulty_evidence: DifficultyEvidence}}
DifficultyEvidence {language_profile_refs: {resource_id}[], reasoning_feature_refs: Reference[],
                    usage_data_refs: Reference[]}
Reference {scheme, version, entry_id, source}
```

scheme/version/source/entry values are opaque reference identities, not URLs or copied definitions.
CEFR is omitted when inapplicable (for example, a non-language Resource); mappings may be empty.
CEFR level is Pre-A1/A1/A2/B1/B2/C1/C2; method is a nonempty procedure reference. A language_profile
reference resolves to the named Resource's revision-bound profile. EGP grammar_id and EVP
profile_entry_id identify reference entries; EVP sense/POS disambiguate that reference. Nothing
copies complete EGP/EVP definitions. Korean instruction parts have egp=false and evp=false.
English question, correct/incorrect option, given sentence, summary, gap context, token and edit
parts can be analyzed independently; resource_segments inherits language from its Resource.

Difficulty is a qualitative judgment, not a CEFR appearance-level conversion. Lexile-like and
other scale/score/unit records coexist in textComplexity with no CEFR-only measurement enum.
Synthetic score 800 L is a fixture value, not an empirical Lexile claim. language_profile,
reasoning_feature and usage_data references inform Item difficulty separately; response rates,
IRT and Rasch remain versioned referenced records, never mutable accumulating Item fields.
No Usage Data, IRT or Rasch record store, calibration, or exporter is implemented here.
`educational_measurements` and unknown extension namespaces/fields are forbidden.

### Overlay targets and immutable text binding

```text
Target = {resource_id, segment_id, start: integer>=0, end: integer>=0, text_sha256}
       | {part_id, start: integer>=0, end: integer>=0, text_sha256}
Overlay = {overlay_id, operation: enum[blank, mark, insert_slot, editable], target: Target}
        | {overlay_id, operation="replace", target: Target, replacement_part_ref}
```

Resource targets bind one segment in a declared Resource; Item targets bind exactly one inline_text
part, not a concatenation of resource_segments. Both identify immutable text before using offsets.
Offsets count Unicode scalar values (Python code points excluding surrogates), zero-based,
half-open [start,end), never UTF-8 bytes, UTF-16 units or grapheme clusters. text_sha256 is lowercase
hex SHA-256 of the **entire exact original segment.text or inline_text.text** encoded UTF-8,
without BOM, normalization, trimming or newline conversion. It is not a digest of the selected
substring or the rendered/modified result. Applying overlays never mutates that source text.
All overlays address the same pre-overlay text, not cascading transformed offsets.

Core verifies digest agreement and 0 <= start <= end <= original length; insert_slot requires
start=end and other operations require start<end. Replacement text is another inline part via
replacement_part_ref, not duplicated inside the overlay. Part/Resource existence, original
custody, range ordering/bounds and operation-target compatibility are T017/T018 obligations.
JSON Schema validates integer/nonnegative/hex shapes and the exclusive owner shape only.

### Exactly twelve discriminated interaction payloads

| type | Required payload beyond type | Correct-response domain |
|---|---|---|
| choice | response_id, options: Option[] | option_id |
| reference_choice | response_id, reference_refs: SegmentRef[], options: Option[] | option_id |
| inline_mark_choice | response_id, mark_refs: overlay_id[] | mark overlay_id |
| sentence_mark_choice | response_id, sentence_refs: SentenceOption[] | sentence option_id |
| blank_choice | response_id, blank_ref: overlay_id, options: Option[] | option_id |
| order_choice | response_id, unit_refs: part_id[], order_options: OrderOption[] | order option_id |
| position_choice | response_id, given_part_ref, slots: Slot[] | slot_id |
| summary_pair_choice | response_id, summary_part_ref, gaps: SummaryGap[], pair_options: PairOption[] | pair option_id |
| inline_choice_set | gaps: ChoiceGap[] | one option_id per gap response |
| token_order | response_id, tokens: Token[], allow_reuse: boolean | ordered token_id list |
| text_entry | entries: Entry[] | one string per entry response |
| edit_response | response_id, editable_part_ref, edit_targets: EditTarget[], allowed_operations | structured edit record |

```text
Option {option_id, part_ref}
SegmentRef {resource_id, segment_id}
SentenceOption {option_id, resource_id, segment_id}
OrderOption {option_id, unit_refs: part_id[1..]}
Slot {slot_id, target_ref: overlay_id}
SummaryGap {gap_id, target_ref: overlay_id}
PairOption {option_id, values: {gap_id, part_ref}[1..]}
ChoiceGap {gap_id, target_ref: overlay_id, response_id, options: Option[1..]}
Token {token_id, part_ref}
Entry {entry_id, target_ref: overlay_id, response_id, expected_length: integer>=1}
EditTarget {target_id, target_ref: overlay_id}
allowed_operations = enum[insert, delete, replace][1..]
```

All part refs resolve in the same Item; Resource segment refs resolve through resource_refs.
Options and pair values point to separate inline option parts, given/summary/edit refs point to
their Item-only inline parts, units may reference resource_segments or inline parts. Slots target
insert_slot overlays; gaps/blank_ref/entries target blank overlays; mark_refs target mark overlays;
edit targets point to editable overlays on editable_part_ref. Each order option is a permutation
of unit_refs. Every pair option binds every summary gap exactly once. A non-reusable token answer
contains no repeats; every answer token exists. These relational rules are Core responsibilities.

### Answers, entry normalization and structured edits

```text
ResponseDeclaration = {response_id, cardinality="single", base_type="identifier", correct_response: ID}
                    | {response_id, cardinality="ordered", base_type="identifier", correct_response: ID[1..]}
                    | {response_id, cardinality="single", base_type="string", correct_response: nonempty string}
                    | {response_id, cardinality="single", base_type="record", correct_response: {edits: Edit[1..]}}
Edit {target_id, operation: enum[insert, delete, replace], text: string}
```

The first eight selections use single/identifier. Each inline-choice gap owns a separate
single/identifier response. Token ordering uses ordered/identifier. Text entries use single/string.
One declaration exists per interaction response_id, with no duplicates or orphan declarations;
its correct_response targets only that response's options/slots/tokens/targets. Interaction
payloads cannot carry answers. Choosing the right declaration kind for an interaction across
arrays is runtime work; the four declaration local shapes are schema work.

Text-entry comparison first converts CRLF and lone CR to LF, then normalizes Unicode NFC; it does
not strip/collapse whitespace, casefold, remove punctuation or accept synonyms. correct_response
is stored in this normalized form. expected_length counts normalized Unicode scalar values and
must match that response's correct_response length; submitted text is compared exactly after the
same transformation. Tests freeze these rules, not a runtime normalization/scoring engine.
This response-only transformation never changes the original text/digest/offset binding.

The internal edit response is single/record, not a text string: edits bind target_id, an allowed
operation and replacement/insert text (empty for delete). Targets resolve to the declared
editable part through editable overlays; operation membership and overlap/conflict rejection
are runtime duties. Replace substitutes the target range, delete removes it, and insert adds
text at target.start without deleting the allowed editable range. All edits use the same original
coordinates; inserted text is exact and is not implicitly normalized. Conflicting edits on the
same range are rejected, not sequentially reinterpreted. An eventual QTI textual export would be a separate adapter representation,
not a second authoritative answer or an alias accepted here.

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
