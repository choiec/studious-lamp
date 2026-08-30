# Feature Specification: Studious Product Runtime

**Feature Directory**: `specs/001-product-runtime/`

**Planning Branch**: `codex/T004-studious-owner-plan`

**Created**: 2026-08-30

**Status**: T042 requirements/design and intentional RED checkpoint; semantic-content GREEN,
new release bytes, publication, runtime, Alpha, and recovery are not established by this change.
T001–T008 completion evidence remains scoped to its recorded historical revisions.

**Input**: Umbrella Feature 001 routes all Studious-owned public-contract and product-runtime work
to this owner-local feature at the literal paths established by T001.

## Purpose and Scope

Studious Lamp is the sole product/runtime owner. This feature defines the owner-local work needed
to release exactly four Candidate-content schemas, independently release the Core Admission API
and Handoff Reference, admit independently verified Candidates into Core-controlled custody, and
perform product lifecycle effects through separate repositoryd and duckdbd boundaries.

The feature also defines the Core-owned HTTP, MCP, and Agent Plugin interfaces and the synthetic
fixtures and evidence required by Umbrella Feature 001. It does not implement Automatic private
compute, oCIS deployment, six-CT systemd mechanisms, public exposure, publication, live runtime,
Alpha execution, restore, or any destructive effect.

## User Scenarios & Testing

### User Story 1 — Release the two Studious contract lines independently (Priority: P1)

As a contract maintainer, I can build and verify one Candidate-content release containing exactly
four schemas and a separate Core Admission API/Handoff release, so consumers pin only the public
surface they actually use.

**Why this priority**: Every producer, intake, and lifecycle path depends on exact owner-controlled
contracts, and the two release lines must not acquire an implied shared identity.

**Independent Test**: Build each local release candidate twice from the same clean source,
byte-compare the outputs, verify its exact inventory and checksums, run positive and negative
conformance, and confirm publication/readback remains `NOT RUN`.

**Acceptance Scenarios**:

1. **Given** the Candidate-content source set, **When** its local release candidate is verified,
   **Then** the normative inventory is exactly `candidate.schema.json`,
   `semantic-content.schema.json`, `provenance.schema.json`, and
   `processing-profile.schema.json` at target `0.1.0` / `contract-v0.1.0`.
2. **Given** release manifests, conformance vectors, provenance, and checksums, **When** the
   Candidate-content inventory is counted, **Then** those files are evidence and not a fifth
   Candidate-content contract.
3. **Given** the Core Admission API/Handoff release, **When** its identity and inventory are
   inspected, **Then** it has its own exact version, tag, manifest, conformance, checksums, and
   release-candidate result without inheriting the Candidate-content version or tag.
4. **Given** any retired public Extractor Protocol, shared release bundle, mutable selector,
   compatibility shim, or private field, **When** conformance runs, **Then** it is rejected.
5. **Given** a local release candidate, **When** evidence is recorded, **Then** tracked Apache-2.0,
   exact distributable inventory, and applicable third-party/NOTICE checks are scoped separately
   from publication and remote readback.
6. **Given** the T042 semantic-content fixtures, **When** T043 validates local shapes, **Then**
   one common Resource and Item model admits all twelve interaction payloads and rejects the
   old `schema`/`value` wrapper, unknown fields/types, embedded answers, and
   `educational_measurements`; exactly four normative artifacts remain.
7. **Given** shape-valid content with a dangling/duplicate identity or invalid overlay binding,
   **When** Core later validates admission, **Then** T017/T018 reject it independently of producer
   claims; schema-level conformance alone never proves reference integrity or publication safety.

---

### User Story 2 — Admit only independently verified Candidate bytes (Priority: P1)

As a Core operator, I can submit an authenticated and authorized Handoff Reference and have Core
independently retrieve, verify, and retain the exact Candidate bytes before admission.

**Why this priority**: oCIS is a non-authoritative transfer surface using one shared real user; Core
must establish integrity and custody independently.

**Independent Test**: Exercise an allowed request, an authorization denial, every missing/extra/
duplicate/malformed/unsafe/changed-byte case, concurrent remote mutation, snapshot failure, exact
replay, and conflicting replay against synthetic fixtures.

**Acceptance Scenarios**:

1. **Given** a valid released Handoff Reference, **When** Core processes admission, **Then** it
   authenticates and authorizes before intake, verifies the exact reference and Candidate-content
   releases, recomputes every size and digest, detects mutation, and reads back an immutable
   Core-controlled snapshot before accepting.
2. **Given** authorization denial, **When** the request is processed, **Then** retrieval and every
   later effect remain `NOT_ATTEMPTED`.
3. **Given** missing stable environment, Space, manifest-resource, or remote version/readback
   evidence, **When** intake starts, **Then** it fails closed.
4. **Given** missing, extra, duplicate, malformed, unsafe, changed, or mismatched bytes, **When**
   verification runs, **Then** admission is rejected and no product effect occurs.
5. **Given** accepted admission, **When** oCIS becomes unavailable, **Then** every later effect,
   retry, restart, and recovery path uses Core-owned records without a renewed oCIS read.

---

### User Story 3 — Keep product lifecycle and storage effects separate (Priority: P1)

As a product operator, I can request identity assignment, canonical publication, adoption, and
projection separately and reconcile uncertain outcomes without duplicate effects.

**Why this priority**: Explicit effects preserve authorization, idempotency, partial failure, and
recovery semantics across Core, repositoryd, and duckdbd.

**Independent Test**: Start from an accepted synthetic admission; verify later effects begin
`NOT_ATTEMPTED`, run each request separately, force an independently scoped failure and a lost
response at each storage boundary, and reconcile by idempotency identity before retry.

**Acceptance Scenarios**:

1. **Given** accepted admission, **When** no later request exists, **Then** identity, publication,
   adoption, and projection remain `NOT_ATTEMPTED`.
2. **Given** a publication request, **When** it succeeds, **Then** repositoryd alone writes the
   canonical immutable product object and no duckdbd request is created.
3. **Given** an adoption or projection request, **When** it succeeds, **Then** duckdbd alone opens
   or writes the persistent DuckDB state and repositoryd is not invoked.
4. **Given** an exact retry, **When** the original binding is unchanged, **Then** one logical result
   is returned or reconciled; a changed binding under the same key is rejected.
5. **Given** a lost response, **When** poststate is unknown, **Then** Core records an uncertain state
   and queries the owning interface before any retry.

---

### User Story 4 — Expose only Core-owned product interfaces (Priority: P2)

As an authorized client maintainer, I can use versioned Core HTTP, MCP, or Agent Plugin interfaces
without gaining access to Automatic internals or product storage.

**Why this priority**: Delivery adapters must expose the same Core authorization and lifecycle
semantics without becoming new authorities.

**Independent Test**: Run interface contract tests for allowed health/readiness and lifecycle
operations, then verify authentication, authorization, reason codes, idempotency bindings, size
bounds, and every direct/bypass denial.

**Acceptance Scenarios**:

1. **Given** any supported delivery interface, **When** it invokes a Core operation, **Then** it
   maps into the same owner-local application use case and operation-specific authorization.
2. **Given** an interface request, **When** it is denied or malformed, **Then** no oCIS,
   repositoryd, or duckdbd effect is performed.
3. **Given** external and internal interfaces, **When** dependencies are inspected, **Then** no
   transport, vendor SDK, credential, or storage type enters the domain/application boundary.

---

### User Story 5 — Freeze safe owner evidence and Alpha fixtures (Priority: P2)

As the Studious Alpha owner, I can freeze exact synthetic fixtures, commands, and evidence slots
for the Studious-owned Umbrella acceptance tests without claiming they have run.

**Why this priority**: Later Alpha work needs literal, reproducible inputs and honest status before
protected or operational execution can be authorized.

**Independent Test**: Validate every fixture and evidence record for exact path, digest, synthetic-
only content, allowed status vocabulary, required owner/revision/command fields, and absence of
secret, credential, private profile, raw provenance, or real educational content.

**Acceptance Scenarios**:

1. **Given** the fixture inventory, **When** disclosure review runs, **Then** it contains synthetic
   content only and no prohibited private or credential-bearing value.
2. **Given** an unexecuted owner acceptance or Alpha scenario, **When** its evidence slot is
   inspected, **Then** its result is `NOT RUN` or `UNESTABLISHED`, never an inferred `PASS`.
3. **Given** Studious-owned Alpha scenarios, **When** the plan is inspected, **Then** each has an
   exact command, fixture/input path, output evidence path, prerequisite, and stopped-operation
   boundary before execution can be authorized.

### Edge Cases

- A Candidate-content release contains three or five normative schemas.
- The Core API/Handoff release reuses `0.1.0`, `contract-v0.1.0`, or the Candidate-content manifest
  without an independent owner decision.
- A Handoff contains a username, token, credential binding, display path, local sync path, mutable
  selector, or weak/absent remote precondition.
- The remote Candidate changes between manifest reads or inventory enumerations.
- Snapshot persistence or readback fails after all remote bytes were verified.
- An exact idempotency key is reused with different operation, prerequisites, bytes, or policy.
- repositoryd succeeds while duckdbd fails, or either response is lost after dispatch.
- oCIS is unavailable after accepted admission.
- A fixture contains real educational content, PII, credentials, raw provenance, or private profile
  instructions.

## Requirements

### Functional Requirements

- **FR-001**: Studious Lamp MUST remain the sole owner of product semantics, Core, repositoryd,
  duckdbd, the Candidate-content contracts, and the Core Admission API/Handoff Reference.
- **FR-002**: Domain and application code MUST depend only inward; transport, oCIS, repositoryd,
  duckdbd/Quack, filesystem, credentials, and delivery frameworks MUST remain outer adapters.
- **FR-003**: Studious MUST NOT import Automatic or Upgraded implementation, publish a shared
  first-party oCIS runtime package, or copy their private models.
- **FR-004**: The Candidate-content release MUST contain exactly the four named JSON Schema 2020-12
  artifacts at target `0.1.0` / `contract-v0.1.0` and no fifth content contract.
- **FR-005**: Candidate-content release evidence MUST be deterministic, exact-byte bound, and kept
  distinct from normative schemas, immutable publication, and remote readback.
- **FR-006**: The public Extractor Protocol and every alias, fallback, reader, negotiation path,
  fixture, example, or compatibility shim MUST be absent from active paths and rejected where
  observable.
- **FR-007**: The Core Admission API/Handoff Reference MUST use an independently selected release
  identity, manifest, checksums, conformance, provenance, publication result, and consumer pin.
- **FR-008**: The Handoff Reference MUST bind its contract version/digest, environment, stable
  Space and manifest-resource identities, mandatory remote version/readback precondition,
  Candidate ID, Candidate-content release identity/manifest digest, Candidate-manifest digest, and
  Export Receipt ID.
- **FR-009**: The Handoff Reference MUST exclude credentials, oCIS principal, binding name, display-
  only locator, local/sync path, mutable selector, private profile, and raw provenance.
- **FR-010**: The Studious admission client MUST map an explicitly selected Automatic Export
  Receipt into the exact released Core request contract only after caller authorization; export
  MUST NOT auto-submit.
- **FR-011**: Core MUST authenticate and authorize `admit_candidate` before any oCIS retrieval and
  MUST leave retrieval and later effects `NOT_ATTEMPTED` on denial.
- **FR-012**: The Candidate intake port MUST be technology-neutral and implemented by a Studious-
  owned oCIS adapter independent of Automatic.
- **FR-013**: Core MUST conditionally retrieve and re-read the manifest, enumerate the full scope,
  retrieve every declared byte, recompute sizes/digests, validate exact pinned contracts, and
  reject all incomplete, extra, duplicate, unsafe, malformed, changed, or mismatched content.
- **FR-014**: Core MUST persist and read back an immutable verified Candidate snapshot under Core-
  controlled custody before accepting admission.
- **FR-015**: No identity, publication, adoption, projection, retry, restart, or recovery behavior
  after accepted admission MAY read oCIS again.
- **FR-016**: Admission, identity assignment, publication, adoption, and projection MUST be
  separately requested, authenticated, authorized, recorded, and retried.
- **FR-017**: Every mutating operation MUST bind one stable idempotency identity to the operation,
  prerequisites, requested bytes, and policy revision; conflicting reuse MUST be rejected.
- **FR-018**: A lost response MUST produce an explicit uncertain poststate and owner-interface
  reconciliation before retry.
- **FR-019**: Core MUST use distinct application ports for repositoryd canonical publication and
  duckdbd adoption/projection; success or failure at one MUST NOT trigger the other.
- **FR-020**: repositoryd MUST be the sole canonical-object writer, and duckdbd MUST be the sole
  writable DuckDB opener; Core MUST have no direct storage fallback and repositoryd MUST NOT invoke
  duckdbd.
- **FR-021**: Core HTTP, MCP, and Agent Plugin delivery MUST map into the same Core-owned use cases,
  authorization, idempotency, bounds, reason codes, and evidence semantics.
- **FR-022**: Configuration examples MUST contain capability names and redacted placeholders only;
  real endpoints, credentials, identities, resource IDs, or secret values MUST remain outside Git.
- **FR-023**: All owner evidence MUST use only `PASS`, `FAIL`, `NOT RUN`, or `UNESTABLISHED`, bind
  exact scope/revision/method/time/locator/digest/limitations, and never widen a narrower result.
- **FR-024**: Studious Alpha fixtures MUST be synthetic-only and freeze exact commands, paths,
  digests, expected states, and evidence outputs for the Studious-owned acceptance scenarios.
- **FR-025**: This feature MUST perform no tag, publication, remote readback, runtime startup,
  deployment, Alpha execution, restore, migration, deletion, or production promotion.
- **FR-026**: Pre-1.0 implementation MUST be a hard cut with no legacy reader, alias, fallback,
  dual path, version negotiation, or speculative abstraction.
- **FR-027**: Semantic content MUST hard-cut to
  `{"schema":"semantic-content.schema.json","resources":[],"items":[]}`. Resource, Item,
  content_part, response_declaration, and interaction are internal `$defs` in that existing
  artifact, not new schemas. Every data object MUST be closed with `additionalProperties: false`.
- **FR-028**: Resources MUST retain resource_id, revision, resource_type, language, content_blocks,
  assets, standard_metadata, extensions, and provenance_refs. resource_type is exactly passage,
  shared_stimulus, table, chart, notice, image, audio, or mixed. Stable block_id and segment_id
  identify typed blocks and typed text segments. Original Resource text/identity is immutable and
  stored once; Item changes MUST be overlays, never edited Resource copies or offset-only identity.
- **FR-029**: Optional source_anchor MUST preserve provenance_ref/page/block semantics only as a
  disclosure-reviewed public-rendition projection, as defined in data-model.md. A private source
  page, name, URL, path, geometry, or raw provenance MUST NOT be exported. If no safe projection
  exists, omit the optional anchor, retain segment identity, and retain private mapping outside
  this contract. Schema acceptance is not approval to publish real source values.
- **FR-030**: Resource and Item qualitative difficulty MUST use
  standard_metadata.ieee_lom.educational.difficulty with source `LOMv1.0` and exactly `very easy`,
  `easy`, `medium`, `difficult`, `very difficult`. Scale/score/unit measurements (including synthetic
  Lexile examples and other scales) MUST be separate in
  standard_metadata.oneedtech_common_cartridge.textComplexity, not LOM difficulty or a CEFR-only
  measurement field. `educational_measurements` is forbidden everywhere.
- **FR-031**: extensions.automatic_disco MUST separate Resource target_audience/language_profile
  from Item difficulty_evidence. Profiles retain CEFR level/method/confidence and reference-only
  EGP/EVP mappings: EGP grammar_id, exact/partial/supplemental relationship and review_status; EVP
  profile_entry_id, sense and POS; both retain scheme/version/source identity without copying full
  definitions. An EGP CEFR appearance level MUST NOT be converted directly to Item difficulty.
- **FR-032**: Every Item MUST retain item_id, revision, resource_refs (resource_id/usage), task
  (taxonomy_id/type/skill), content_parts, overlays, interaction, response_declarations, scoring
  (strategy/max_score), standard_metadata, extensions.automatic_disco.difficulty_evidence, and
  provenance_refs. The common model MUST remain subject-neutral; CSAT taxonomies are references,
  not alternative common structures.
- **FR-033**: Each content_part MUST have part_id, role, content and analysis_target.egp/evp.
  content.kind is exactly inline_text or resource_segments. Item-only questions, options, given
  sentences, summaries, tokens and edits use inline_text; reused Resource text uses segment refs.
  Korean instructions disable both analysis flags. English questions, given sentences, correct
  and incorrect options, summaries and gap contexts MUST be independently addressable.
- **FR-034**: Overlays MUST use blank, mark, insert_slot, editable, or replace with stable targets.
  Resource targets bind Resource/segment identity; Item-only targets bind inline part identity.
  Offsets are zero-based Unicode scalar positions in half-open [start,end) ranges; text_sha256
  binds the complete exact immutable target text encoded as UTF-8 without normalization. Bounds,
  digest agreement, empty insertion ranges and nonempty other ranges are runtime obligations.
- **FR-035**: interaction.oneOf MUST have exactly twelve type-discriminated payloads: choice,
  reference_choice, inline_mark_choice, sentence_mark_choice, blank_choice, order_choice,
  position_choice, summary_pair_choice, inline_choice_set, token_order, text_entry, edit_response.
  Exact fields, nested records and response types are fixed in data-model.md and the contract
  oracle matrix; no thirteenth payload or generic fallback is permitted.
- **FR-036**: Answers MUST exist only in response_declarations with response_id/cardinality/
  base_type/correct_response. Selection is single/identifier, each inline gap has its own response,
  token order is ordered/identifier, entry is single/string, and internal structured edit is
  single/record. Text-entry normalization is the fixed NFC/LF rule in data-model.md, not an
  implicit trim/casefold or an exporter rule.
- **FR-037**: Every referenced Resource, segment, part, option, slot, token, overlay and answer
  target MUST exist in its defined scope. Every interaction response_id has exactly one
  declaration and no orphan declaration. No duplicate identities or duplicate authoritative
  Resource/inline-text representation are permitted. T043 owns schema-enforceable local shapes;
  later Core T017/T018 independently own cross-array integrity at the current admission boundary.
  Automatic owns its independent private model and producer-side validation, not Core acceptance.
- **FR-038**: Item difficulty_evidence MUST reference language profiles, reasoning features and
  usage data separately. Empirical response rates, IRT and Rasch belong to separately referenced
  records, never accumulating mutable fields on immutable Items. Their stores are not implemented.
- **FR-039**: The twelve type names and JSON metadata are Studious-normalized contract fields,
  not official QTI JSON field names. QTI/LOM/Common Cartridge correspondence is design context
  only; XML exporters, PCI, Usage Data storage, IRT and Rasch implementations are out of scope.

The exact T042 wire definitions and validation split below are design authority for T043, not
a claim that the unchanged semantic-content schema already enforces FR-027–FR-039.

### Key Entities

- **Candidate-content release**: One exact four-schema public release and its separate evidence
  envelope.
- **Core API/Handoff release**: An independently versioned control-plane release containing the
  Core Admission API and Handoff Reference.
- **Admission request**: An authenticated, authorized, idempotently bound request carrying one
  released Handoff Reference.
- **Verified Candidate snapshot**: Core-controlled immutable custody of every independently
  verified manifest and payload byte.
- **Lifecycle effect request/outcome**: One explicit identity, publication, adoption, or projection
  request and its terminal or uncertain result.
- **Owner evidence record**: A status-bounded record with exact source, method, locator, digest,
  time, and limitations.

## Success Criteria

### Measurable Outcomes

- **SC-001**: The Candidate-content normative inventory contains exactly four named schemas and
  zero active Extractor Protocol or fifth-contract paths.
- **SC-002**: The Candidate-content and Core API/Handoff local release candidates build byte-
  identically twice and pass their independent inventory, checksum, provenance, and conformance
  checks before either can be considered publishable.
- **SC-003**: All missing, extra, duplicate, unsafe, malformed, mutable, mismatched, private-field,
  and retired-form contract vectors are rejected.
- **SC-004**: Authorization-denied admission produces zero intake, snapshot, repositoryd, or
  duckdbd calls.
- **SC-005**: Every accepted admission has one read-back verified Core snapshot whose inventory,
  sizes, and digests match the independently retrieved Candidate bytes.
- **SC-006**: Exact replay yields one logical result, conflicting replay is rejected, and response-
  loss tests show reconciliation before retry with zero duplicate authoritative effects.
- **SC-007**: Dependency tests find zero sibling implementation imports, zero technology types in
  inward ports, zero Core direct storage paths, and zero repositoryd-to-duckdbd calls.
- **SC-008**: Publication and adoption/projection tests demonstrate two independent port calls and
  separately reported partial/uncertain outcomes.
- **SC-009**: HTTP, MCP, and Agent Plugin contract tests apply the same authorization, idempotency,
  bounds, reason-code, and no-effect-on-denial rules.
- **SC-010**: Fixture and staged-diff review finds zero real educational content, PII, credentials,
  private profiles, raw provenance, credential-bearing URLs, or secret values.
- **SC-011**: Every planned owner acceptance and Alpha task names exact literal commands, fixtures,
  inputs, outputs, prerequisites, and result ceilings before it becomes executable.
- **SC-012**: T004 evidence reports planning and static validation only; implementation, release,
  publication, runtime, E2E, Alpha, and recovery remain `NOT RUN` or `UNESTABLISHED`.
- **SC-013**: T042 freezes twelve synthetic forms and a schema/runtime negative matrix; all new
  schema-dependent failures are attributable to the missing hard cut and unrelated checks pass.
  T043 must make those schema tests GREEN without weakening the oracle. T077 must bind new exact
  source/conformance digests; historical T010 evidence does not prove this redesign.

## Assumptions and Dependencies

- The authoritative Umbrella baseline is revision
  `eba6fd909b3d2c3a65ec79483654be9e6a6e9f0b`, tree
  `163e2696ffa59a312a2f7a77bf57502b113d153e`, whose Feature 001 artifact digests match the T001
  survey.
- T001 is integrated in Studious at task commit `79a1d3c07e3fdaabb9342a76c20d8467d15910f8`
  and merge `38e6aea278db9fda98ff887b94658efcc92585a6`; its literal path map is binding for this plan.
- Python 3.14.4 and the existing uv lock are retained. T001–T008 source/tests/tooling are historical
  completed increments; T042 adds no dependencies and does not regenerate their release bytes.
- The Core API/Handoff release version, tag, immutable locator, and digests remain
  `UNESTABLISHED`; the plan must create a task for an explicit owner decision rather than guess.
- Exact Quack/DuckDB versions and production readiness remain `UNESTABLISHED`; no direct-file
  fallback is allowed.
- Exactly one real remotely usable oCIS user is an environment constraint, not a Core principal or
  evidence of Automatic/Core isolation.

## Non-Goals

- Automatic private acquisition, extraction, profile, provenance, Candidate build, or export
  implementation.
- Upgraded six-CT systemd, network, TLS, identity, storage, backup, restore, or deployment work.
- Contract publication, tag creation, immutable remote readback, consumer activation, runtime
  startup, live Handoff, E2E, Alpha, failure injection, restore, deletion, or promotion.
- Recommendation, ranking, embedding, DPP, calibration, clustering, PageRank, Thompson Sampling,
  Phoenix, CLIP, or behavior-sequence features.
- XML/QTI/LOM/Common Cartridge export adapters, PCI, Usage Data record stores, IRT and Rasch.
