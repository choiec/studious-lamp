# Tasks: Studious Product Runtime

**Input**: Design documents in `specs/001-product-runtime/`

**Current state**: T001–T008 retain historical completion evidence. T042 RED and T043 schema
GREEN remain frozen: 108 contract and 114 full checks at T043. T044 release-tooling repair is
complete with 152 additional release regressions (266 total). T009 now completes the local
Candidate-content 0.1.0 gate from integrated source `5f19a7d2ac2510c38c48c9aba0c6213cf89ee4a1`:
two independent clean local clones and fresh venvs produced byte-identical eight-file bundles;
266 tests PASS in each environment. Twelve raw inputs, canonical outputs, full conformance
packaging, manifest/provenance/checksums, tracked Apache-2.0 and scoped NOTICE review PASS.
T010 is complete as an intentionally failing RED checkpoint under explicit human exception:
prepared tests/vectors are frozen; baseline 266 PASS, new 36 PASS/120 expected FAIL, full suite
302 PASS/120 expected FAIL. All failures name absent T011 normative sources; no unexpected errors.
T011 completes the independent Core API/Handoff 0.2.0 / core-admission-v0.2.0 source contract
(selection only, no tag): frozen Core 156 PASS, full 422 PASS, unchanged baseline 266 PASS.
T012 completes Core release tooling GREEN: unchanged 422 frozen checks plus 223 new release
regressions, full 645 PASS in the existing locked offline environment. Exact eleven raw inputs,
eight outputs/two normative artifacts, complete vectors, independent source/manifest/provenance
bindings and unsafe/resealed-input rejection PASS using temporary synthetic Git/source/output only.
T013 completes the independent Core API/Handoff 0.2.0 local candidate from clean integrated
source `e51661b1b6fdf25bb7461052afb793793ef0ea58`: two fresh source clones/venvs/output roots,
639 contract and 645 full checks PASS in each, all eight output bytes identical, raw-source/JCS/
manifest/provenance/checksums/LICENSE and scoped NOTICE review PASS. The verified bundle is
materialized with owner T012 evidence; source/vector historical NOT RUN fields remain unchanged.
T014 initializes two independent publication/readback slots with exact Candidate/Core source,
manifest, eight-file inventory, local-candidate evidence and scoped license/NOTICE pins. Local
readback and full locked offline suite (645 PASS) preserve both bundles; per-release authorization,
tag, publication and immutable remote readback remain NOT RUN, missing remote values UNESTABLISHED.
T015–T041 remain unchecked (17 complete, 27 unchecked, 44 total). Consumer activation, runtime
and Alpha remain NOT RUN; same-host reproduction only. T032/T033 require separate authorization.

The earlier T009 attempt remains historical FAIL in its retained temporary diagnosis. Its five
accounted generated changes were replaced only after both repaired clean builds passed. Raw T043
schemas, conformance sources, frozen tests and T010/T077 evidence remain unchanged. Canonical
released bytes have separate source/output digests; two complete conformance documents include
23 historical and 78 semantic cases (28 future-Core obligations remain unexecuted). T011 records
local-candidate evidence only. Same-host reproduction does not establish cross-platform behavior,
publication/readback, runtime, Core reference validation, Alpha or a SLSA level.

**ID scope**: These are Studious owner-local task IDs. Each ID is one fresh task branch, one
verified Conventional Commit with its task trailer, and one local `--no-ff` merge. Never combine
two IDs in one commit.

**Execution**: Tasks are listed in dependency order and intentionally use no `[P]` marker. Tests
are written and observed failing before their implementation task, except T044's regression and
repair form one GREEN-only integration unit. Every task names literal paths.
T012 likewise integrates its release regressions and tooling together only after GREEN.

## Phase 1: Setup and Foundational Boundaries

- [X] T001 Create the minimal Python 3.14.4 package and exact uv dependency/test lock in `.python-version`, `pyproject.toml`, and `uv.lock`; record the deterministic commands `uv sync --locked --dev` and `uv run --locked pytest -q` without adding unrelated lint/type/CI tooling.
- [X] T002 Add failing inward-dependency, sibling-import, shared-oCIS, direct-storage, post-admission-oCIS, and repositoryd-to-duckdbd architecture checks in `tests/test_architecture.py`. **RED checkpoint**: six expected assertion failures until T003 supplies the owner-local boundary modules; no implementation PASS is claimed.
- [X] T003 Implement the minimum owner-local domain models, policy, and technology-neutral port responsibilities required to pass T002 in `src/studious_lamp/domain/models.py`, `src/studious_lamp/domain/policy.py`, and `src/studious_lamp/application/ports.py`. **GREEN checkpoint**: all six T002 architecture tests pass; no adapters, runtime services, configuration, or operational evidence are claimed.
- [X] T004 Add redacted capability-only configuration examples with no real endpoint, credential, identity, resource ID, or storage binding in `config/core.example.toml`, `config/repositoryd.example.toml`, `config/duckdbd.example.toml`, and `config/quack.example.toml`. **Evidence**: TOML parsing, locked offline tests, and forbidden-value/static scope checks PASS; runtime, publication, and Alpha remain `NOT RUN`/`UNESTABLISHED`.

**Checkpoint**: Package commands are locked and the inward architecture is executable; no public
contract or runtime behavior is yet claimed.

## Phase 2: User Story 1 — Independent Public Contract Releases (Priority: P1)

**Goal**: Implement and locally verify exactly four Candidate-content schemas and an independently
versioned Core Admission API/Handoff release.

**Independent test**: Build each local candidate twice, compare exact bytes, run positive/negative
conformance, verify exact inventories/checksums/provenance/license/distribution inputs, and retain
publication/readback as `NOT RUN`.

- [X] T005 [US1] Add failing exact-four, JSON Schema 2020-12, disclosure, unsafe-path, mutable-selector, fifth-artifact, evidence-classification, and retired-Extractor-Protocol cases in `tests/contracts/test_candidate_content.py`, `contracts/candidate-content/conformance/positive.json`, and `contracts/candidate-content/conformance/negative.json`. — COMPLETED: intentional RED; 9 expected assertion failures in schema-dependent exact-four/conformance oracle tests, all caused by the four absent T006 schemas; T006 owns GREEN; all other required checks PASS.
- [X] T006 [US1] Implement the four and only four normative Candidate-content schemas needed to pass T005 in `contracts/candidate-content/candidate.schema.json`, `contracts/candidate-content/semantic-content.schema.json`, `contracts/candidate-content/provenance.schema.json`, and `contracts/candidate-content/processing-profile.schema.json`. — COMPLETED: four Draft 2020-12 schemas only; locked-offline full pytest 16 passed (T005 10, architecture 6), strict JSON/schema/reference/conformance/path/disclosure/scope checks PASS; release/publication/runtime/Alpha NOT RUN.
- [X] T007 [US1] Implement deterministic Candidate-content generation and exact-byte verification in `tools/build_candidate_content_release.py` and `tools/verify_release.py`, producing only `build/releases/candidate-content/0.1.0/candidate.schema.json`, `build/releases/candidate-content/0.1.0/semantic-content.schema.json`, `build/releases/candidate-content/0.1.0/provenance.schema.json`, `build/releases/candidate-content/0.1.0/processing-profile.schema.json`, `build/releases/candidate-content/0.1.0/candidate-content.manifest.json`, `build/releases/candidate-content/0.1.0/candidate-content.conformance.jsonl`, `build/releases/candidate-content/0.1.0/candidate-content.provenance.intoto.jsonl`, and `build/releases/candidate-content/0.1.0/SHA256SUMS`. — COMPLETED: local_candidate=PASS; tag=NOT RUN; publication=NOT RUN; readback=NOT RUN; runtime=NOT RUN; Alpha=NOT RUN; remote effects=NOT RUN.
- [X] T008 [US1] Run `uv run --locked pytest -q tests/contracts/test_candidate_content.py` and write exact-four source/conformance status, commands, revision, digests, and limitations to `docs/evidence/umbrella-001/T010-four-content-contracts.json` without claiming a release candidate or publication. — COMPLETED: exact-four source=PASS; synthetic conformance catalog=PASS; locked offline test=10 passed; release candidate/publication=NOT RUN.
- [X] T042 [US1] Make the semantic-content hard-cut requirements/design authority and intentional RED conformance one atomic change in `specs/001-product-runtime/spec.md`, `specs/001-product-runtime/plan.md`, `specs/001-product-runtime/data-model.md`, `specs/001-product-runtime/contracts/candidate-content.md`, `specs/001-product-runtime/tasks.md`, `tests/contracts/test_candidate_content.py`, `contracts/candidate-content/conformance/positive.json`, and `contracts/candidate-content/conformance/negative.json`: require top-level `resources[]` plus `items[]`; `$defs` for `resource`, `item`, `content_part`, `response_declaration`, and `interaction`; immutable Resource originals with Item overlays; standard Resource metadata separated from `extensions.automatic_disco`; no `educational_measurements`; the five controlled LOM difficulty values (`very easy`, `easy`, `medium`, `difficult`, `very difficult`) plus separate `textComplexity`; content kinds `inline_text` and `resource_segments`; exactly 12 interaction types (`choice`, `reference_choice`, `inline_mark_choice`, `sentence_mark_choice`, `blank_choice`, `order_choice`, `position_choice`, `summary_pair_choice`, `inline_choice_set`, `token_order`, `text_entry`, `edit_response`); separate `response_declarations`; `additionalProperties: false` on every object; and positive/negative conformance. **RED checkpoint**: the new cases fail only because the existing `semantic-content.schema.json` does not yet implement the hard cut. XML/QTI/LOM export adapters and Usage Data/IRT/Rasch storage remain out of scope for later separate tasks. — COMPLETED: requirements/design and synthetic oracle frozen; intentional RED: 95 expected schema-dependent assertion failures, 19 passing existing/oracle/fixture checks, zero unexpected failures; unchanged normative schema bytes remain at baseline `f532b79b26c46ff2cdaf8dac9bfd14d159fb9f0b`. T043 owns GREEN/T077; Core referential validation, release regeneration, publication, runtime and Alpha are NOT RUN.
- [X] T043 [US1] Implement only the semantic-content JSON Schema hard cut needed to pass T042 RED and perform schema-level validation in `contracts/candidate-content/semantic-content.schema.json`, `tests/contracts/test_candidate_content.py`, `contracts/candidate-content/conformance/positive.json`, `contracts/candidate-content/conformance/negative.json`, `specs/001-product-runtime/tasks.md`, and `docs/evidence/umbrella-001/T077-semantic-content-hard-cut.json`. The schema owns directly enforceable `required`, `enum`, `oneOf`, `additionalProperties: false`, and local-shape constraints only; cross-array Resource/segment/part/option/slot/token/response ID referential integrity belongs to the later Core validator in T017/T018. **GREEN/evidence checkpoint**: record the exact Studious revision, semantic-content schema and conformance digests, commands/results, the schema-level versus later referential-validation responsibility split, and the limitation that existing `docs/evidence/umbrella-001/T010-four-content-contracts.json` remains valid only for its historical revision; do not implement XML/QTI/LOM export adapters or Usage Data/IRT/Rasch storage. — COMPLETED: semantic-content schema GREEN; exact-four inventory, frozen contract tests (108 PASS), full pytest (114 PASS), local-shape/disclosure checks and focused review PASS. T077 binds the exact contract subtree and file digests with post-commit resolution; T010 stays historical. Core T017/T018 reference validation, T009 regeneration, publication, runtime and Alpha are NOT RUN.
- [X] T044 [US1] After T043 PASS, repair the existing Candidate-content tooling against Umbrella `specs/001-product-compute-boundaries/contracts/public-contract-release.md` §§3.3, 5.1–5.5 and 7.1 in exactly `tools/build_candidate_content_release.py`, `tools/verify_release.py`, new `tests/contracts/test_candidate_content_release.py`, and the T044 completion/current-summary fields of `specs/001-product-runtime/tasks.md`; additionally allow `pyproject.toml` and `uv.lock` only for the necessary exact-pinned standards-conforming JCS dependency identified by the survey in `plan.md` (package/version not yet selected). Preserve all frozen schemas, conformance sources, tests/fixtures, historical T010/T077 and existing five dirty generated outputs. Implement canonical released bytes separately from raw-source bindings; the exact twelve-file mode/hash/path LF inventory; independent §3.3 manifest and §5.5 provenance checks; acyclic schemas/conformance → manifest → provenance → checksums; and rejection of unproved `reproducible: true`. **GREEN-only acceptance**: unchanged 114 frozen checks plus independent release regressions all PASS, covering canonical bytes/numbers/Unicode keys, full source inventory/modes/paths, revision/raw-source/output/provenance binding, missing/extra/dirty sources, manifest fields, checksum/inventory negatives, and build/verify in task-owned temporary directories only. Do not derive the regression oracle solely from `expected_release_files`, hand-roll a general JCS algorithm, or create a separate intentional RED commit. Run `uv run --locked --offline pytest -q -p no:cacheprovider` in an isolated task environment; record exact commands and all results at completion. T044 supplies local source/output selection needed for isolated validation, but does not regenerate repository outputs, complete T009 or claim the second-environment gate. Full required PASS is mandatory before its own commit/merge. — COMPLETED: frozen 114 checks unchanged; 152 release regressions and full locked/offline suite (266 PASS) in new `/tmp/studious-t044-venv` using `UV_PROJECT_ENVIRONMENT=/tmp/studious-t044-venv UV_CACHE_DIR=/home/choi-eunchang/.cache/uv uv run --locked --offline pytest -q -p no:cacheprovider`. Exact twelve raw inputs, independent manifest/source/output/provenance checks, RFC 8785 golden bytes and rejection tests PASS; rfc8785==0.1.4 is the sole new dependency. Unsigned in-toto Statement v1/SLSA v1 structure is checked; no SLSA level, signer, reproducibility or candidate verdict is claimed. Source selection requires the recorded revision at the explicit source-root HEAD, including after a later evidence commit. All build/verify tests use task-owned temporary Git/source/output; five dirty outputs, schemas, conformance sources, frozen tests and T010/T077 remain unchanged. T009, second-clean-environment gate, publication/readback, runtime and Alpha NOT RUN.
- [X] T009 [US1] After T043 and T044 are integrated with required PASS, select and record one exact clean integrated source revision, then use the repaired `tools/build_candidate_content_release.py` and `tools/verify_release.py` to build/verify all eight `build/releases/candidate-content/0.1.0/` files named in T007 from that same revision in two owner-selected clean environments as specified below. Compare every output byte; bind the complete source inventory/raw-source digests and the deterministic canonical-output sizes/digests rather than requiring raw-source/output equality. Verify tracked `LICENSE`, exact distributable inventory and applicable third-party/NOTICE inputs; record actual environment identities, commands, comparison/checksum/provenance/conformance results and limitations in `docs/evidence/umbrella-001/T011-content-release-candidate.json`, with `publication=NOT RUN`. T009 alone regenerates those eight repository outputs and updates its completion/current-summary fields in `specs/001-product-runtime/tasks.md`; no PASS, completion or commit/merge without the actual second-clean-environment result and every §7.1 gate. — COMPLETED: two clean environments at source `5f19a7d2ac2510c38c48c9aba0c6213cf89ee4a1`, 8/8 byte-identical outputs, 266 tests PASS in each, independent canonical/source/provenance/inventory/LICENSE/NOTICE checks PASS. Canonical T011 evidence binds exact source and output digests; publication/readback, runtime, Core cross-array validation and Alpha NOT RUN.

T009 ephemeral method: before writing, resolve `<revision>` to the full selected commit hash and
confirm that `/tmp/studious-t009-repro-a-<revision>/` and
`/tmp/studious-t009-repro-b-<revision>/` are absent. In each root, create an independent local-only
Git copy under `source/` with `git clone --no-hardlinks --no-checkout` from the verified owner
repository, with no network fetch, then check out that exact revision detached. No `git worktree`
registration is required. Verify clean tracked inputs and no shared object alternates; materialize
separate `venv/` and `output/` paths under each root. Use `uv sync --locked --offline` with each
fresh venv selected by `UV_PROJECT_ENVIRONMENT` and the existing
`UV_CACHE_DIR=/home/choi-eunchang/.cache/uv`, reading the same exact-locked distribution bytes
through the normal approved access path (`require_escalated` if needed). Do not copy/mirror the
cache, create substitute caches, or change root/global cache structure. T044 resolves any needed
JCS dependency through normal selection/installation; T009 first verifies that its immutable
locked package inputs are ready offline.
Never reuse an existing root or environment. Record both source trees, Python/uv/dependency
identities, literal commands and byte-comparison results; exclude these ephemeral paths from
deterministic release bytes. This is same-host clean source/venv isolation, not cross-platform
reproducibility. Missing offline dependencies or an unexecuted environment keep the gate
`UNESTABLISHED`/`NOT RUN`, not PASS. Do not create these paths during T044 or this planning correction.
After both isolated builds pass, T009 may regenerate only its original repository-output scope
from the verified bytes; the pre-existing dirty outputs remain untouched until that task owns it.

- [X] T010 [US1] Add failing Core Admission/Handoff required-field, forbidden-field, independent-version, weak-precondition, release-mismatch, exact/conflicting-replay, and implementation-agreement cases in `tests/contracts/test_core_admission.py`, `contracts/core-admission/conformance/positive.json`, and `contracts/core-admission/conformance/negative.json`. — COMPLETED as the explicitly human-authorized intentional RED checkpoint: the three prepared file hashes remain unchanged; baseline 266 PASS, new 36 PASS plus 120 expected assertion FAIL, full suite 302 PASS plus 120 expected assertion FAIL (422 total), with zero unexpected failures, collection errors, skips or xfails. Every failure is `T010 RED: T011 normative source absent:` for the four T011 paths; no normative implementation was added. Independent Candidate verification preserves all eight bytes and owner T011 evidence. This exception permits only this T010 completion/commit/local no-fast-forward merge and does not label the required full suite PASS. Static fixture/source-conformance scope only; actual replay, authentication, intake and runtime enforcement remain NOT RUN. Exact commands, stdout and failure classification are retained in the local review record `/tmp/studious-t010-red-review/integration/`; T011 and publication remain unexecuted.
- [X] T011 [US1] Select one independent pre-1.0 Core API/Handoff release version and tag, then implement the exact request/Handoff, repositoryd, and duckdbd service contracts needed to pass T010 in `contracts/core-admission/openapi.yaml`, `contracts/core-admission/handoff-reference.schema.json`, `contracts/repositoryd/openapi.yaml`, and `contracts/duckdbd/openapi.yaml`; do not reuse or infer the Candidate-content version/tag. — COMPLETED: independently selected `core-admission-0.2.0` / `0.2.0` / tag target `core-admission-v0.2.0`; exactly two public normative artifacts plus five evidence files and LICENSE are pinned in the Core source, excluding both internal service APIs. Closed request/Handoff shapes, bounded authenticated interfaces, denial without effects, completed Core-held publication prerequisites for duckdbd, exact replay before new-effect projection CAS, and separate owner readback/uncertainty semantics are specified. Locked offline Core 156, full 422 and unchanged baseline 266 PASS, with no skip/xfail; all frozen T010 and Candidate bytes/evidence are preserved. Detailed local commands, structural/negative review and resolved findings: `/tmp/studious-t011-green/`. Source/static conformance only; authentication, pin/equality enforcement, intake, replay/CAS and service runtime remain NOT RUN. T012/T013, tag creation, publication and remote readback were not executed.
- [X] T012 [US1] Implement Core API/Handoff release tooling GREEN only in `tools/build_core_admission_release.py`, `tools/verify_release.py`, new `tests/contracts/test_core_admission_release.py`, and only T012 completion/current fields of `specs/001-product-runtime/tasks.md`. Follow T011 `x-release` identity/inventory and `plan.md` §Core release tooling and candidate boundary: declare/authenticate all eleven selected raw inputs (including the existing imported `tools/build_candidate_content_release.py` helper), plus any genuinely imported byte-affecting helper; retain Python/locks/LICENSE and existing `rfc8785==0.1.4` without new dependencies. Support explicit source/output selection, strict JCS, raw-source versus canonical-output bindings, all eight outputs/two normative artifacts, complete frozen vectors, independent version/tag, acyclic manifest/provenance/checksums and safe source/output separation. Preserve Candidate verifier behavior with per-release dispatch, no Candidate-global monkeypatching or unconditional Core-tool import into its isolated twelve-input fixture. Add independent regressions for JCS numbers/Unicode, exact source inventory/modes/paths/revision/dirty-state/executing-tool identity, excluded Candidate/internal assets, semantic bindings and resealed tampering, and unsupported reproducibility assertions; do not derive success solely from builder expected files or manifest generation. **GREEN-only acceptance**: unchanged 422 frozen checks plus new regressions all PASS with `uv run --locked --offline pytest -q -p no:cacheprovider` before this task's single verified commit/local no-ff merge. Build/verify temporary synthetic Git/source/output directories only; no owner `build/releases/core-admission/` generation, T012 Core candidate evidence, or second-environment claim. Preserve every frozen source/test/vector and historical Candidate output/evidence byte. — COMPLETED: Core tooling GREEN, 223 independent release regressions plus unchanged 422 frozen checks (645 PASS); focused source/output/tool-binding review and eight independent reviewer checks PASS after closing executing-checkout output overlap. Explicit --source-root/--output and --source-root/--release selection, eleven-input raw Git/mode/hash authentication, JCS output, full vectors, exact eight-file distribution, acyclic independently checked manifest/provenance/seven checksums, and resealed-tampering/unsafe-source/output rejection implemented. Candidate isolated twelve-input behavior and original-verifier historical preservation PASS; no dependency/lock/schema/vector change. Validation uses the existing /tmp/studious-t044-venv and normal uv cache; detailed local report is /tmp/studious-t012-release-tooling/REPORT.md. T013 candidate/two-environment gate, owner Core output/evidence generation, publication/readback, runtime, Alpha and consumer activation NOT RUN; immutable locator UNESTABLISHED.
- [X] T013 [US1] After T012 GREEN commit/local no-ff integration, select one exact clean integrated source revision and record two owner-selected fresh independent source clones, venvs and output directories at that revision; install locked dependencies only through the normal cache/approval path, with no alternate cache/mirror/configuration bypass. In both environments run `uv run --locked --offline pytest -q -p no:cacheprovider tests/contracts` and `uv run --locked --offline pytest -q -p no:cacheprovider`, build with `uv run --locked --offline python tools/build_core_admission_release.py` using explicit `--source-root`/`--output`, and verify with each clone's `uv run --locked --offline python tools/verify_release.py` using explicit `--source-root`/`--release`; record literal absolute roots/commands and compare every byte. Verify root tracked Apache-2.0 `LICENSE`, exact distributable inventory and applicable third-party/NOTICE inputs. Only after all gates PASS materialize exactly `build/releases/core-admission/LICENSE`, `build/releases/core-admission/checksums.sha256`, `build/releases/core-admission/conformance/negative.json`, `build/releases/core-admission/conformance/positive.json`, `build/releases/core-admission/handoff-reference.schema.json`, `build/releases/core-admission/manifest.json`, `build/releases/core-admission/openapi.yaml`, and `build/releases/core-admission/provenance.json`; write `docs/evidence/umbrella-001/T012-core-admission-api.json` and only T013 completion/current fields of `specs/001-product-runtime/tasks.md`. Follow the plan's raw inventory/hash/mode versus canonical distribution bindings and acyclic JCS/LICENSE/seven-checksum rules. Record two-environment observations outside deterministic release bytes and state the same-host limitation. Preserve Candidate's eight bytes/evidence using byte comparisons and the original verifier at pinned clean source, never current-tool substitution. Source/schema/finite-conformance/replay-binding/implementation-agreement PASS must not imply live authentication, replay/CAS, intake, snapshot/storage or runtime. Tag/publication/remote readback/consumer activation/Alpha remain `NOT RUN`, immutable locator `UNESTABLISHED`; T014 and T032/T033 remain unchanged. — COMPLETED: source `e51661b1b6fdf25bb7461052afb793793ef0ea58`, two fresh independent clean local clones/venvs/outputs, 639 contract and 645 full checks PASS per environment; 8/8 identical bytes, exact eleven raw bindings, canonical distribution, complete vectors, acyclic manifest/provenance/checksums and scoped LICENSE/NOTICE checks PASS. Owner bundle physically copied from verified A output and reverified using both original clean-source tools. Manifest SHA-256 `23e9e9a4cb2b15fb3e749c9b8aaf51f4b6cc417cae4aa8a7767856aab6289fcf`; exact commands, outputs, source/validation-only digests and limits in `docs/evidence/umbrella-001/T012-core-admission-api.json`. Candidate bytes/evidence and frozen source/tests preserved. Same host/system Python 3.14.4 only; live auth/replay-CAS/intake/snapshot/storage/runtime/Alpha, tag/publication/readback/activation NOT RUN; immutable locator UNESTABLISHED.
- [X] T014 [US1] Create two independent publication/readback result slots—Candidate content and Core API/Handoff—with exact per-release prerequisites and initial `NOT RUN`/`UNESTABLISHED` results in `docs/evidence/umbrella-001/T013-release-readback.json`; perform no tag, publication, or remote readback. — COMPLETED: exactly two independent slots bind each original candidate's identity/source, manifest, eight asset sizes/digests, local evidence and scoped Apache-2.0/NOTICE review. Direct local Git/raw-input/asset readback and original pinned-source verifiers PASS; full locked offline suite 645 PASS. Authorization, tag/publication/readback remain NOT RUN; mechanism/locator/approval identity/remote bytes and publication-time license delivery remain UNESTABLISHED. Candidate LICENSE stays source-bound outside its fixed eight assets; Core LICENSE remains one of eight. T032 updates Candidate only, T033 Core only; neither requires the other's PASS, and Automatic T005 requires only actual Candidate publication/readback PASS. Existing release bytes/evidence, other task rows and checklist remain unchanged; no operational effect.

**Checkpoint**: Both local contract lines are independently testable and evidence-bounded; immutable
publication and consumer activation remain separate.

## Phase 3: User Story 2 — Independent Candidate Intake (Priority: P1)

**Goal**: Authenticate and authorize admission, independently verify every Handoff byte, and retain
a Core-controlled snapshot before acceptance.

**Independent test**: Denial performs no intake; every integrity/mutation case rejects; acceptance
requires snapshot readback; later behavior works with oCIS unavailable.

- [ ] T015 [US2] Add failing authentication/authorization-before-intake and Export-Receipt-to-released-request mapping cases in `tests/core/test_authorization.py`, `tests/core/test_handoff_mapping.py`, and `tests/fixtures/synthetic/handoff-reference.json`.
- [ ] T016 [US2] Implement owner-local request authentication, operation-specific authorization, and authorized receipt-value mapping needed to pass T015 in `src/studious_lamp/application/authentication.py`, `src/studious_lamp/application/authorization.py`, and `src/studious_lamp/application/handoff.py`.
- [ ] T017 [US2] Add failing conditional manifest, before/after inventory, size/digest, missing/extra/duplicate/unsafe/malformed/mutation, snapshot failure/readback, exact/conflicting replay, no-post-admission-oCIS, and independent cross-array Resource/segment/part/option/slot/token/response ID referential-integrity cases in `tests/core/test_admission.py` and `tests/integration/test_ocis_intake.py`; retain the current admission boundary and require rejection before snapshot acceptance or any later product effect.
- [ ] T018 [US2] Implement the independent Core oCIS intake adapter, immutable snapshot adapter, and admission use case needed to pass T017 in `src/studious_lamp/adapters/ocis.py`, `src/studious_lamp/adapters/snapshot.py`, and `src/studious_lamp/application/admission.py`, including Core-owned Resource/segment/part/option/slot/token/response ID referential-integrity validation at the existing admission boundary before acceptance; do not move cross-array integrity into the JSON Schema or an adapter.
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

- [ ] T031 [US5] Freeze disclosure-reviewed synthetic contract/Handoff/Core/storage fixtures in `tests/fixtures/synthetic/candidate.json`, `tests/fixtures/synthetic/semantic-content.json`, `tests/fixtures/synthetic/provenance.json`, `tests/fixtures/synthetic/processing-profile.json`, and `tests/fixtures/synthetic/handoff-reference.json`, with the semantic-content fixture covering all 12 interaction types (`choice`, `reference_choice`, `inline_mark_choice`, `sentence_mark_choice`, `blank_choice`, `order_choice`, `position_choice`, `summary_pair_choice`, `inline_choice_set`, `token_order`, `text_entry`, `edit_response`), then write exact digests, commands, limitations, and `NOT RUN` Alpha status to `docs/evidence/umbrella-001/T030-alpha-fixtures.json`.

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
2. T005 → T006 → T007 → T008 → T042 → T043 → T044 → T009 completes Candidate-content source, the semantic-content hard cut, central T077 evidence, contract-compliant tooling, and regenerated local-candidate evidence including the second-clean-environment gate.
3. T010 → T011 → T012 → T013 → T014 completes the independent Core API/Handoff source and initializes the two publication slots.
4. T015 → T016 and T043 both precede T017; T017 → T018 → T019 completes controlled independent intake evidence, including Core-owned cross-array reference validation at the existing admission boundary.
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
| T077 semantic-content hard cut | T042–T043 | `docs/evidence/umbrella-001/T077-semantic-content-hard-cut.json` |
| T011 Candidate local candidate | T007, T043, T044, T009 | `docs/evidence/umbrella-001/T011-content-release-candidate.json` |
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
- US1 contract and publication work: 15 (including the semantic-content RED/GREEN hard cut, T044 GREEN release-tooling repair and two separately authorized publication tasks)
- US2 intake work: 5
- US3 lifecycle/persistence work: 8
- US4 delivery work: 3
- US5 fixture/Alpha work: 9 (including eight separately authorized Alpha tasks)
- Total owner-local tasks: 44

T043 re-observed T042's historical expected RED (95 failed / 19 passed) and the unrelated
19 PASS / 95 deselected before implementation, then made the unchanged complete oracle GREEN.
Commands, exact source/conformance digests and limitations are recorded in
`docs/evidence/umbrella-001/T077-semantic-content-hard-cut.json`; the supported test-only subset
remains fixed in `specs/001-product-runtime/plan.md`.
T009 local candidate is complete; the independent Core API/Handoff work beginning at T010
and separately authorized T032 publication/readback remain subsequent units. Neither is executed
by T009. Core cross-array validation remains owned by T017/T018; all other task definitions,
completion rows and publication dependencies are unchanged.
