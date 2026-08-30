# Tasks: Studious Product Runtime

**Input**: Design documents in `specs/001-product-runtime/`

**Current state**: Owner plan only. All tasks below are unchecked; source, tests, contracts,
release candidates, publication, runtime, E2E, Alpha, and recovery are not implemented or run.

**ID scope**: These are Studious owner-local task IDs. Each ID is one fresh task branch, one
verified Conventional Commit with its task trailer, and one local `--no-ff` merge. Never combine
two IDs in one commit.

**Execution**: Tasks are listed in dependency order and intentionally use no `[P]` marker. Tests
are written and observed failing before their implementation task. Every task names literal paths.

## Phase 1: Setup and Foundational Boundaries

- [X] T001 Create the minimal Python 3.14.4 package and exact uv dependency/test lock in `.python-version`, `pyproject.toml`, and `uv.lock`; record the deterministic commands `uv sync --locked --dev` and `uv run --locked pytest -q` without adding unrelated lint/type/CI tooling.
- [ ] T002 Add failing inward-dependency, sibling-import, shared-oCIS, direct-storage, post-admission-oCIS, and repositoryd-to-duckdbd architecture checks in `tests/test_architecture.py`.
- [ ] T003 Implement the minimum owner-local domain models, policy, and technology-neutral port responsibilities required to pass T002 in `src/studious_lamp/domain/models.py`, `src/studious_lamp/domain/policy.py`, and `src/studious_lamp/application/ports.py`.
- [ ] T004 Add redacted capability-only configuration examples with no real endpoint, credential, identity, resource ID, or storage binding in `config/core.example.toml`, `config/repositoryd.example.toml`, `config/duckdbd.example.toml`, and `config/quack.example.toml`.

**Checkpoint**: Package commands are locked and the inward architecture is executable; no public
contract or runtime behavior is yet claimed.

## Phase 2: User Story 1 — Independent Public Contract Releases (Priority: P1)

**Goal**: Implement and locally verify exactly four Candidate-content schemas and an independently
versioned Core Admission API/Handoff release.

**Independent test**: Build each local candidate twice, compare exact bytes, run positive/negative
conformance, verify exact inventories/checksums/provenance/license/distribution inputs, and retain
publication/readback as `NOT RUN`.

- [ ] T005 [US1] Add failing exact-four, JSON Schema 2020-12, disclosure, unsafe-path, mutable-selector, fifth-artifact, evidence-classification, and retired-Extractor-Protocol cases in `tests/contracts/test_candidate_content.py`, `contracts/candidate-content/conformance/positive.json`, and `contracts/candidate-content/conformance/negative.json`.
- [ ] T006 [US1] Implement the four and only four normative Candidate-content schemas needed to pass T005 in `contracts/candidate-content/candidate.schema.json`, `contracts/candidate-content/semantic-content.schema.json`, `contracts/candidate-content/provenance.schema.json`, and `contracts/candidate-content/processing-profile.schema.json`.
- [ ] T007 [US1] Implement deterministic Candidate-content generation and exact-byte verification in `tools/build_candidate_content_release.py` and `tools/verify_release.py`, producing only `build/releases/candidate-content/0.1.0/candidate.schema.json`, `build/releases/candidate-content/0.1.0/semantic-content.schema.json`, `build/releases/candidate-content/0.1.0/provenance.schema.json`, `build/releases/candidate-content/0.1.0/processing-profile.schema.json`, `build/releases/candidate-content/0.1.0/candidate-content.manifest.json`, `build/releases/candidate-content/0.1.0/candidate-content.conformance.jsonl`, `build/releases/candidate-content/0.1.0/candidate-content.provenance.intoto.jsonl`, and `build/releases/candidate-content/0.1.0/SHA256SUMS`.
- [ ] T008 [US1] Run `uv run --locked pytest -q tests/contracts/test_candidate_content.py` and write exact-four source/conformance status, commands, revision, digests, and limitations to `docs/evidence/umbrella-001/T010-four-content-contracts.json` without claiming a release candidate or publication.
- [ ] T009 [US1] Run `uv run --locked python tools/build_candidate_content_release.py` twice plus `uv run --locked python tools/verify_release.py --release build/releases/candidate-content/0.1.0`, verify tracked `LICENSE`, exact distributable inventory, and applicable third-party/NOTICE inputs, and write the local-candidate-only result with `publication=NOT RUN` to `docs/evidence/umbrella-001/T011-content-release-candidate.json`.
- [ ] T010 [US1] Add failing Core Admission/Handoff required-field, forbidden-field, independent-version, weak-precondition, release-mismatch, exact/conflicting-replay, and implementation-agreement cases in `tests/contracts/test_core_admission.py`, `contracts/core-admission/conformance/positive.json`, and `contracts/core-admission/conformance/negative.json`.
- [ ] T011 [US1] Select one independent pre-1.0 Core API/Handoff release version and tag, then implement the exact request/Handoff, repositoryd, and duckdbd service contracts needed to pass T010 in `contracts/core-admission/openapi.yaml`, `contracts/core-admission/handoff-reference.schema.json`, `contracts/repositoryd/openapi.yaml`, and `contracts/duckdbd/openapi.yaml`; do not reuse or infer the Candidate-content version/tag.
- [ ] T012 [US1] Implement deterministic Core API/Handoff release generation in `tools/build_core_admission_release.py` and extend exact verification in `tools/verify_release.py`, producing the independently identified outputs `build/releases/core-admission/manifest.json`, `build/releases/core-admission/checksums.sha256`, and `build/releases/core-admission/provenance.json` with no Candidate-content bundle or alias.
- [ ] T013 [US1] Run `uv run --locked pytest -q tests/contracts/test_core_admission.py`, build twice with `uv run --locked python tools/build_core_admission_release.py`, verify with `uv run --locked python tools/verify_release.py --release build/releases/core-admission`, verify tracked `LICENSE`, exact distributable inventory, and applicable third-party/NOTICE inputs, and write source/identity/conformance/replay/implementation-agreement/local-candidate results to `docs/evidence/umbrella-001/T012-core-admission-api.json` without claiming publication.
- [ ] T014 [US1] Create two independent publication/readback result slots—Candidate content and Core API/Handoff—with exact per-release prerequisites and initial `NOT RUN`/`UNESTABLISHED` results in `docs/evidence/umbrella-001/T013-release-readback.json`; perform no tag, publication, or remote readback.

**Checkpoint**: Both local contract lines are independently testable and evidence-bounded; immutable
publication and consumer activation remain separate.

## Phase 3: User Story 2 — Independent Candidate Intake (Priority: P1)

**Goal**: Authenticate and authorize admission, independently verify every Handoff byte, and retain
a Core-controlled snapshot before acceptance.

**Independent test**: Denial performs no intake; every integrity/mutation case rejects; acceptance
requires snapshot readback; later behavior works with oCIS unavailable.

- [ ] T015 [US2] Add failing authentication/authorization-before-intake and Export-Receipt-to-released-request mapping cases in `tests/core/test_authorization.py`, `tests/core/test_handoff_mapping.py`, and `tests/fixtures/synthetic/handoff-reference.json`.
- [ ] T016 [US2] Implement owner-local request authentication, operation-specific authorization, and authorized receipt-value mapping needed to pass T015 in `src/studious_lamp/application/authentication.py`, `src/studious_lamp/application/authorization.py`, and `src/studious_lamp/application/handoff.py`.
- [ ] T017 [US2] Add failing conditional manifest, before/after inventory, size/digest, missing/extra/duplicate/unsafe/malformed/mutation, snapshot failure/readback, exact/conflicting replay, and no-post-admission-oCIS cases in `tests/core/test_admission.py` and `tests/integration/test_ocis_intake.py`.
- [ ] T018 [US2] Implement the independent Core oCIS intake adapter, immutable snapshot adapter, and admission use case needed to pass T017 in `src/studious_lamp/adapters/ocis.py`, `src/studious_lamp/adapters/snapshot.py`, and `src/studious_lamp/application/admission.py`.
- [ ] T019 [US2] Run `uv run --locked pytest -q tests/core/test_authorization.py tests/core/test_handoff_mapping.py tests/core/test_admission.py tests/integration/test_ocis_intake.py` and write exact independent-reader, full-verification, mutation, snapshot, denial, mapping, replay, and no-post-admission-read results to `docs/evidence/umbrella-001/T017-independent-intake.json` without claiming live oCIS, deployed intake, or E2E PASS.

**Checkpoint**: Controlled synthetic tests can establish intake behavior only; live Handoff and
runtime readiness remain `NOT RUN`.

## Phase 4: User Story 3 — Explicit Lifecycle and Persistence Effects (Priority: P1)

**Goal**: Keep identity, repositoryd publication, duckdbd adoption/projection, replay, and uncertain
poststate as separate Core-owned effects.

**Independent test**: Later effects begin `NOT_ATTEMPTED`; exact replay produces one result;
conflict rejects; lost response reconciles; repositoryd and duckdbd outcomes remain independent.

- [ ] T020 [US3] Add failing lifecycle separation, exact/conflicting replay, independent partial outcome, and response-loss reconciliation cases in `tests/core/test_lifecycle.py`, `tests/core/test_replay.py`, and `tests/core/test_response_loss.py`.
- [ ] T021 [US3] Implement explicit identity/publication/adoption/projection requests, idempotency bindings, independent outcomes, and uncertain-poststate reconciliation needed to pass T020 in `src/studious_lamp/application/lifecycle.py`.
- [ ] T022 [US3] Add failing repositoryd-only canonical publication, sole-writer, exact replay, conflict, readback, and lost-response cases in `tests/integration/test_repositoryd.py`.
- [ ] T023 [US3] Implement the repositoryd client adapter and canonical service needed to pass T022 in `src/studious_lamp/adapters/repositoryd.py` and `src/studious_lamp/repositoryd/service.py`, with no duckdbd call or direct Core storage fallback.
- [ ] T024 [US3] Add failing duckdbd-only adoption/projection, sole writable opener, exact replay, conflict, readback, lost-response, and no-repositoryd-call cases in `tests/integration/test_duckdbd.py`.
- [ ] T025 [US3] Implement the duckdbd client adapter, service, and initial schema needed to pass T024 in `src/studious_lamp/adapters/duckdbd.py`, `src/studious_lamp/duckdbd/service.py`, and `src/studious_lamp/duckdbd/migrations/001_initial.sql`, with no direct Core DuckDB open or repositoryd dependency.
- [ ] T026 [US3] Run `uv run --locked pytest -q tests/core/test_lifecycle.py tests/core/test_replay.py tests/core/test_response_loss.py` and write authentication/authorization, effect separation, replay, uncertain-poststate, reconciliation, and no-post-admission-oCIS results to `docs/evidence/umbrella-001/T018-core-lifecycle.json` without widening to runtime or E2E PASS.
- [ ] T027 [US3] Run `uv run --locked pytest -q tests/integration/test_repositoryd.py tests/integration/test_duckdbd.py tests/test_architecture.py` and write separate-port, sole-writer/opener, partial/uncertain outcome, direct-storage denial, and zero repositoryd-to-duckdbd results to `docs/evidence/umbrella-001/T019-persistence-boundaries.json` without claiming deployed storage.

**Checkpoint**: Controlled source/integration behavior is evidence-bounded; deployed persistence,
backup, restart, and recovery remain `NOT RUN`.

## Phase 5: User Story 4 — Core Public Interfaces (Priority: P2)

**Goal**: Expose the same Core use cases through HTTP, MCP, and Agent Plugin delivery adapters.

**Independent test**: Each interface applies its exact shape/bounds and the same authentication,
authorization, idempotency, reason-code, and no-effect-on-denial semantics.

- [ ] T028 [US4] Add failing HTTP, MCP, and Agent Plugin contract/bounds/authentication/authorization/idempotency/reason-code/no-effect cases in `tests/delivery/test_interfaces.py`.
- [ ] T029 [US4] Implement the three delivery adapters and composition root needed to pass T028 in `src/studious_lamp/delivery/http.py`, `src/studious_lamp/delivery/mcp.py`, `src/studious_lamp/delivery/agent_plugin.py`, and `src/studious_lamp/composition.py`, without a generic plugin framework or direct storage/oCIS bypass.
- [ ] T030 [US4] Run `uv run --locked pytest -q tests/delivery/test_interfaces.py tests/test_architecture.py` and write exact Core-only interface, dependency, authorization, idempotency, bounds, reason-code, and denial results to `docs/evidence/umbrella-001/T020-core-public-interface.json` without claiming public exposure or deployed endpoints.

**Checkpoint**: Delivery contracts are source-tested; Cloudflare, CT routing, runtime listeners, and
public reachability remain Upgraded or operational evidence.

## Phase 6: User Story 5 — Synthetic Fixtures and Evidence (Priority: P2)

**Goal**: Freeze exact synthetic inputs and commands for Studious owner acceptance and Alpha work
without executing protected or operational scenarios.

**Independent test**: Every fixture is deterministic and synthetic-only; every command and output
path is literal; every unexecuted result stays `NOT RUN` or `UNESTABLISHED`.

- [ ] T031 [US5] Freeze disclosure-reviewed synthetic contract/Handoff/Core/storage fixtures in `tests/fixtures/synthetic/candidate.json`, `tests/fixtures/synthetic/semantic-content.json`, `tests/fixtures/synthetic/provenance.json`, `tests/fixtures/synthetic/processing-profile.json`, and `tests/fixtures/synthetic/handoff-reference.json`, then write exact digests, commands, limitations, and `NOT RUN` Alpha status to `docs/evidence/umbrella-001/T030-alpha-fixtures.json`.

## Phase 7: Separately Authorized Immutable Publication and Readback

**Gate**: These tasks are not executable from this plan alone. Each requires separate explicit
authorization naming the exact release candidate and publication effect.

- [ ] T032 [US1] After separate Candidate-content publication authorization and T009 PASS, publish only the exact approved `build/releases/candidate-content/0.1.0/` bytes through the owner-selected immutable mechanism, independently read back every asset, and update only the Candidate-content slot in `docs/evidence/umbrella-001/T013-release-readback.json`; leave the Core API/Handoff slot unchanged.
- [ ] T033 [US1] After separate Core API/Handoff publication authorization and T013 PASS, publish only the exact approved `build/releases/core-admission/` bytes through its independently selected immutable mechanism, independently read back every asset, and update only the Core API/Handoff slot in `docs/evidence/umbrella-001/T013-release-readback.json`; leave the Candidate-content slot unchanged.

## Phase 8: Separately Authorized Studious Alpha Scenarios

**Gate**: Every task below requires Umbrella T033 entry `MET`, exact frozen revisions/releases/
fixtures/environment bindings, and separate Alpha execution authorization. Unit or controlled local
integration PASS does not establish deployed E2E, recovery, or production readiness.

- [ ] T034 [US5] Execute `uv run --locked pytest -q tests/contracts/test_candidate_content.py tests/contracts/test_core_admission.py` against `tests/fixtures/synthetic/candidate.json` and `tests/fixtures/synthetic/handoff-reference.json`, then write the immutable-release-scoped `AT-003 PUBLIC-CONTRACT` result to `docs/evidence/umbrella-001/alpha/AT-003-public-contract.json`.
- [ ] T035 [US5] Execute `uv run --locked pytest -q tests/integration/test_ocis_intake.py::test_handoff_integrity_negative_catalog` against `contracts/core-admission/conformance/negative.json`, then write `AT-009 HANDOFF-INTEGRITY-NEGATIVE` to `docs/evidence/umbrella-001/alpha/AT-009-handoff-integrity-negative.json`.
- [ ] T036 [US5] Execute `uv run --locked pytest -q tests/core/test_authorization.py::test_denial_performs_no_intake_or_effect` against `tests/fixtures/synthetic/handoff-reference.json`, then write `AT-010 CORE-AUTHORIZATION` to `docs/evidence/umbrella-001/alpha/AT-010-core-authorization.json`.
- [ ] T037 [US5] Execute `uv run --locked pytest -q tests/core/test_admission.py::test_acceptance_stops_after_snapshot` against `tests/fixtures/synthetic/candidate.json`, then write `AT-011 ADMISSION-SEPARATION` to `docs/evidence/umbrella-001/alpha/AT-011-admission-separation.json`.
- [ ] T038 [US5] Execute `uv run --locked pytest -q tests/integration/test_repositoryd.py::test_publication_uses_repositoryd_only` against `tests/fixtures/synthetic/candidate.json`, then write `AT-012 REPOSITORY-PUBLICATION` to `docs/evidence/umbrella-001/alpha/AT-012-repository-publication.json`.
- [ ] T039 [US5] Execute `uv run --locked pytest -q tests/integration/test_duckdbd.py::test_adoption_uses_duckdbd_only` against `tests/fixtures/synthetic/candidate.json`, then write `AT-013 DUCKDB-ADOPTION` to `docs/evidence/umbrella-001/alpha/AT-013-duckdb-adoption.json`.
- [ ] T040 [US5] Execute `uv run --locked pytest -q tests/core/test_replay.py::test_exact_and_conflicting_replay` against `tests/fixtures/synthetic/handoff-reference.json`, then write `AT-015 EXACT-CONFLICTING-REPLAY` to `docs/evidence/umbrella-001/alpha/AT-015-exact-conflicting-replay.json`.
- [ ] T041 [US5] Execute `uv run --locked pytest -q tests/core/test_response_loss.py::test_lost_response_reconciles_before_retry` against `tests/fixtures/synthetic/candidate.json`, then write `AT-016 LOST-RESPONSE` to `docs/evidence/umbrella-001/alpha/AT-016-lost-response.json`.

## Dependencies and Execution Order

1. T001 → T002 → T003 → T004 establishes the package and architecture boundary.
2. T005 → T006 → T007 → T008 → T009 completes Candidate-content source and local-candidate evidence.
3. T010 → T011 → T012 → T013 → T014 completes the independent Core API/Handoff source and initializes the two publication slots.
4. T015 → T016 → T017 → T018 → T019 completes controlled independent intake evidence.
5. T020 → T021 → T022 → T023 → T024 → T025 → T026 → T027 completes lifecycle and persistence evidence.
6. T028 → T029 → T030 completes Core delivery-interface evidence.
7. T031 freezes synthetic fixtures and exact scenario commands.
8. T032 and T033 are independently authorized publication operations; one does not require the other, but both must be resolved as required by the selected Alpha baseline before T034.
9. T034 → T035 → T036 → T037 → T038 → T039 → T040 → T041 follows the Umbrella Alpha scenario order after entry and execution authorization.

No task may skip an unmet dependency, infer a missing release/binding, or execute publication,
runtime, Alpha, restore, deployment, or deletion from a planning result.

## Coverage Map

| Umbrella acceptance work | Owner-local tasks | Exact evidence output |
|---|---|---|
| T010 four contracts | T005–T008 | `docs/evidence/umbrella-001/T010-four-content-contracts.json` |
| T011 Candidate local candidate | T007, T009 | `docs/evidence/umbrella-001/T011-content-release-candidate.json` |
| T012 Core API/Handoff | T010–T013 | `docs/evidence/umbrella-001/T012-core-admission-api.json` |
| T013 two publication slots | T014, gated T032–T033 | `docs/evidence/umbrella-001/T013-release-readback.json` |
| T017 independent intake | T015–T019 | `docs/evidence/umbrella-001/T017-independent-intake.json` |
| T018 Core lifecycle | T020–T021, T026 | `docs/evidence/umbrella-001/T018-core-lifecycle.json` |
| T019 persistence boundaries | T022–T025, T027 | `docs/evidence/umbrella-001/T019-persistence-boundaries.json` |
| T020 Core interfaces | T028–T030 | `docs/evidence/umbrella-001/T020-core-public-interface.json` |
| T030 synthetic fixtures | T031 | `docs/evidence/umbrella-001/T030-alpha-fixtures.json` |
| AT-003, AT-009–013, AT-015–016 | T034–T041 | `docs/evidence/umbrella-001/alpha/*.json` exact paths above |

## Completion Rules for Each Task

- Reverify root, branch, base revision/tree, index/worktree, instructions, and literal path scope.
- Stop for overlap, suspected secret/private content, unexpected base movement, failed required
  validation, merge conflict, or required unauthorized effect.
- Run the smallest deterministic checks covering the task and `git diff --check`.
- Stage literal task-owned paths only; inspect the full staged diff and secret-oriented patterns.
- Commit one Conventional Commit with the owner-local task trailer; never bypass hooks.
- Reverify unchanged base, merge locally with `--no-ff`, retain the task branch, and report
  `push: NOT RUN` unless push is separately requested.

## Planned Task Totals

- Setup/foundational: 4
- US1 contract and publication work: 12 (including two separately authorized publication tasks)
- US2 intake work: 5
- US3 lifecycle/persistence work: 8
- US4 delivery work: 3
- US5 fixture/Alpha work: 9 (including eight separately authorized Alpha tasks)
- Total owner-local tasks: 41

Suggested first executable increment after T004: T001 only. No source task is complete in this
planning commit.
