# Implementation Plan: Studious Product Runtime

**Feature Directory**: `specs/001-product-runtime/` | **Date**: 2026-08-30 | **Spec**: [spec.md](spec.md)

**Planning Branch**: `codex/T004-studious-owner-plan`

## Summary

Build the Studious-owned product boundary in causal increments: initialize a locked Python
project; implement and locally verify two independent public contract release lines; establish
owner-local domain/application ports; implement independently verified Candidate intake and Core
snapshot custody; keep identity, repositoryd publication, and duckdbd adoption/projection as
separate authorized effects; expose those use cases through Core-owned HTTP, MCP, and Agent Plugin
adapters; then freeze synthetic fixtures and bounded evidence for the Umbrella acceptance gates.

This plan is documentation only. It creates no source, dependency lock, release candidate,
publication, runtime process, Handoff, E2E, Alpha, recovery, or operational result.

**T042 update**: The original T004 planning statements describe that historical increment.
T001–T008 are now complete at their recorded revisions. This update freezes semantic-content
requirements and a deliberately failing test oracle only; it does not implement the hard-cut
schema, run the release builder, write central T077 evidence or implement Core validation.

## Technical Context

**Language/Version**: Python 3.14.4 selected by the T001 survey

**Package Manager**: uv with the existing T001 `pyproject.toml`/`uv.lock`; T042 adds no dependencies.

**Primary Dependencies**: Python standard library first; JSON Schema, HTTP, MCP, Agent Plugin,
oCIS, repositoryd, DuckDB, and Quack libraries must be selected and exact-pinned only by their
own implementation tasks

**Storage**: Core-controlled snapshot/lifecycle storage, repositoryd canonical storage, and
duckdbd-owned DuckDB storage are separate owner boundaries; physical paths and deployed bindings
remain `UNESTABLISHED`

**Testing**: Existing locked pytest and standard-library, test-only schema/oracle checks;
deterministic release and structured-evidence work remains in the tasks named in `tasks.md`.

**Target Platform**: Python package and services for the Umbrella six-CT target; deployment,
systemd units, endpoints, TLS, identities, mounts, and startup belong to Upgraded and are not
implemented here

**Project Type**: One Python project containing Core, repositoryd, and duckdbd runtimes with
separate inward ports and outer adapters

**Performance Goals**: `UNESTABLISHED`; correctness, fail-closed behavior, and evidence precede
numeric latency/capacity targets

**Constraints**: Exactly four Candidate-content schemas; independent Core API/Handoff release;
one-user oCIS limitation; no sibling implementation import; no shared oCIS runtime; no direct Core
storage; no repositoryd-to-duckdbd call; no post-admission oCIS read; synthetic fixtures only;
pre-1.0 hard cut

**Scale/Scope**: One owner repository, two public release lines, five owner-local application port
responsibilities, three delivery adapters, and the exact Studious acceptance/evidence outputs
routed by Umbrella Feature 001

## Constitution Check

| Gate | Plan evidence | Status |
|---|---|---|
| Studious is the sole product/runtime owner | All source, contracts, runtime, and evidence paths are local to this repository; Automatic and Upgraded implementation are non-goals | `PASS` for planning |
| Dependencies point inward | `src/studious_lamp/application/ports.py` owns technology-neutral ports; all external systems map in `adapters/` or `delivery/` | `PASS` for planning |
| Contract lines remain independent | Candidate content and Core API/Handoff have separate sources, build tools, manifests, checksums, conformance, evidence, and later publication gates | `PASS` for planning |
| Lifecycle effects remain explicit | Admission, identity, publication, adoption, and projection have separate use cases, requests, authorization, idempotency, outcomes, and tests | `PASS` for planning |
| Evidence bounds claims | Owner tasks write only scoped JSON evidence with four-status vocabulary and retain remote/operational results as `NOT RUN` or `UNESTABLISHED` | `PASS` for planning |
| Pre-1.0 hard cut | Tasks reject the Extractor Protocol, fifth schema, shared release/version, compatibility shims, direct storage, repository chain, and post-admission oCIS reads | `PASS` for planning |
| Local task integration | Every future owner task is one ordered Spec Kit ID and exact literal path set; branch/commit/no-ff merge occurs per task | `PASS` for planning |

No waiver or compatibility bridge is planned. These statuses validate the plan text, not any
implementation or runtime claim.

## Architecture

### Dependency Direction

```text
src/studious_lamp/delivery/* + src/studious_lamp/adapters/* + composition.py
                                   |
                                   v
             src/studious_lamp/application/* + application/ports.py
                                   |
                                   v
                       src/studious_lamp/domain/*
```

Wire values are validated at the boundary and mapped into owner-local models. External failures
become typed application outcomes. No vendor type, credential, path, transport exception, or
sibling implementation crosses inward.

### Owner-Local Port Set

| Port responsibility | Owner path | Outer adapter path | Prohibited path |
|---|---|---|---|
| Candidate intake reader | `src/studious_lamp/application/ports.py` | `src/studious_lamp/adapters/ocis.py` | Automatic model/adapter import or sync-folder read |
| Verified snapshot custody | `src/studious_lamp/application/ports.py` | `src/studious_lamp/adapters/snapshot.py` | oCIS as retained authority |
| Canonical publication | `src/studious_lamp/application/ports.py` | `src/studious_lamp/adapters/repositoryd.py` | Core filesystem write or duckdbd trigger |
| Product state | `src/studious_lamp/application/ports.py` | `src/studious_lamp/adapters/duckdbd.py` | Direct DuckDB open or repositoryd chain |
| Authentication/delivery | `src/studious_lamp/application/authentication.py` | `src/studious_lamp/delivery/http.py`, `src/studious_lamp/delivery/mcp.py`, `src/studious_lamp/delivery/agent_plugin.py` | Transport identity as domain authorization |

### Contract Release Lines

Candidate content uses the exact four sources under `contracts/candidate-content/`, target
`0.1.0` / `contract-v0.1.0`, and deterministic evidence under
`build/releases/candidate-content/0.1.0/`. The normative release-evidence filenames required by the
Umbrella contract are `candidate-content.manifest.json`, `candidate-content.conformance.jsonl`,
`candidate-content.provenance.intoto.jsonl`, and `SHA256SUMS`; the T001 generic planned output names
are not retained as parallel aliases.

T044 repairs the existing tooling against Umbrella
`specs/001-product-compute-boundaries/contracts/public-contract-release.md` §§3.3, 5.1–5.5 and
7.1 without changing that contract or the frozen T043 inputs. Tracked schema bytes are raw source
inputs: retain their exact Git revision, mode, path and SHA-256, then parse and deterministically
serialize the released schemas as RFC 8785 JCS. Released sizes/digests bind those canonical output
bytes, not the raw-source digest. Verification independently checks both bindings and the
source-to-output transformation; raw source/output byte equality is not an acceptance condition.

The declared tracked release-input inventory is exactly these twelve files:

```text
.python-version
LICENSE
pyproject.toml
uv.lock
tools/build_candidate_content_release.py
tools/verify_release.py
contracts/candidate-content/candidate.schema.json
contracts/candidate-content/semantic-content.schema.json
contracts/candidate-content/provenance.schema.json
contracts/candidate-content/processing-profile.schema.json
contracts/candidate-content/conformance/positive.json
contracts/candidate-content/conformance/negative.json
```

For the exact source revision, hash the concatenation of
`<git-mode> <sha256(exact raw bytes)> <normalized POSIX relative path><LF>` records sorted by
unsigned UTF-8 path bytes. Verify every declared input against Git, including locks, tools,
LICENSE and both complete conformance sources; reject missing, extra, unsafe, untracked or dirty
inputs and mode changes. Reject undeclared generation inputs, not unrelated repository documents.
Outputs, VCS metadata, caches, timestamps and environment-local paths are not source records or
byte-affecting inputs. Frozen test/oracle files remain validation inputs, not generation inputs.

The binding order is raw sources → canonical schemas/conformance → manifest → provenance →
SHA256SUMS. Enforce every §3.3 manifest binding, including `manifest_format_version`,
`digest_algorithm`, release identity, exactly four artifacts and conformance. The manifest may
name the provenance file but must not hash its downstream bytes; provenance binds the exact
manifest, schema and conformance bytes, builder/build definition and full source identity.
Checksums cover all seven preceding files. Neither builder nor provenance may assert
`reproducible: true` before the second-clean-environment gate; T009 records the observed gate
result outside the deterministic eight-file bundle, avoiding a digest cycle or environment-
dependent artifact mutation.

Core Admission uses `contracts/core-admission/openapi.yaml` and
`contracts/core-admission/handoff-reference.schema.json`, with the complete two conformance
documents. T011 selected `core-admission-0.2.0`, version `0.2.0`, tag target
`core-admission-v0.2.0`; these are source metadata, not an actual tag or publication. Its
`openapi.yaml` `x-release` fixes exactly two normative artifacts, five evidence files and LICENSE
under `build/releases/core-admission/`; the complete literal inventory is in
[core-admission.md](contracts/core-admission.md#deterministic-release-candidate).
`contracts/repositoryd/openapi.yaml` and `contracts/duckdbd/openapi.yaml` are internal service
contracts, excluded from the public Core and Candidate-content assets and normative counts.

#### Core release tooling and candidate boundary (T012/T013)

T012 is tooling GREEN only: `tools/build_core_admission_release.py`, `tools/verify_release.py`,
new `tests/contracts/test_core_admission_release.py`, and its own completion/current fields in
`specs/001-product-runtime/tasks.md`. Build/verify only temporary synthetic Git sources and
outputs. It must not generate owner `build/releases/core-admission/` bytes or write
`docs/evidence/umbrella-001/T012-core-admission-api.json`. Newly uncommitted tooling cannot
authenticate itself as an accepted clean owner revision; T012 must first pass and receive its
own verified commit and local no-fast-forward integration before T013 selects that source.

Declare this eleven-file raw source inventory in the Core build sources (unsigned UTF-8 path
order); the count follows the actual inputs, not Candidate's twelve-file fixture:

```text
.python-version
LICENSE
contracts/core-admission/conformance/negative.json
contracts/core-admission/conformance/positive.json
contracts/core-admission/handoff-reference.schema.json
contracts/core-admission/openapi.yaml
pyproject.toml
tools/build_candidate_content_release.py
tools/build_core_admission_release.py
tools/verify_release.py
uv.lock
```

The existing verifier imports `tools/build_candidate_content_release.py` for common parsing and
verification support, so its exact raw bytes are an input, never a distributed Candidate asset.
Retain that bounded reuse without monkeypatching Candidate builder globals or introducing a new
framework/helper file. Any further genuinely imported byte-affecting helper must be declared and
authenticated before GREEN; no hidden input or arbitrary fixed count is acceptable. Keep existing
Candidate verifier behavior and its isolated twelve-input regression fixture working without a
Core tool in that fixture; load Core-specific tooling only in the Core release path. Existing
locked `rfc8785==0.1.4` suffices; no dependency or lock change is needed.

Hash each selected source's exact raw Git bytes using
`<git-mode> <sha256> <normalized POSIX relative path><LF>`, sorted by unsigned UTF-8 path bytes.
`source_tree_sha256` is SHA-256 of the concatenation of those complete records.
Authenticate the exact revision/tree, full inventory, index, bytes, modes, executing builder,
verifier and imported helpers; reject missing/extra/unsafe/untracked/dirty inputs and source/output
overlap, symlinks or shared hardlinks that could alter source or retained bytes. Outputs, caches,
VCS metadata, host identities and timestamps are not generation inputs. Frozen tests and internal
service contracts are validation-only inputs: if referenced in acceptance evidence, bind them
separately by revision/path/mode/hash, never as public assets.

All released JSON, including JSON-compatible `openapi.yaml`, uses RFC 8785 JCS UTF-8, no BOM and
no trailing LF; LICENSE is the exact tracked Apache-2.0 raw file. Raw source hashes and canonical
distribution sizes/hashes remain distinct. The acyclic order is normative artifacts, complete
vectors and LICENSE → manifest → provenance → checksums. Manifest binds independent identity,
exact two-artifact classification, vectors, license, declared distribution and source/tool inputs;
it may name but must not hash downstream provenance. Provenance binds the build definition,
builder, exact raw inputs, manifest and preceding outputs. `checksums.sha256` has exactly seven
records, sorted by unsigned UTF-8 relative filename, lowercase SHA-256, two spaces and LF, with no
self-entry. Do not invent recursive Handoff hashes, manifest/provenance cycles, volatile release
fields or unsupported self-asserted reproducibility proofs. T011 source status metadata stays
source-scoped; observed two-environment results belong only in owner acceptance evidence.

T012 requires unchanged 422 frozen checks plus independent release regressions all GREEN before
its single commit/merge. Tests cover JCS numbers/Unicode keys and raw/canonical distinctions;
the selected full source inventory, modes, paths, revision, dirty inputs and executing-tool
authentication; all eight outputs/two normative artifacts and both complete frozen vector
documents; independent version/tag and exclusion of Candidate/internal assets; semantic manifest,
provenance and checksum binding even after tampering and resealing checksums; safe source/output
separation; and rejection of unsupported reproducibility claims. Expected bytes and verdicts must
not come solely from builder output lists or manifest-generation logic. Use the existing isolated
environment for `uv run --locked --offline pytest -q -p no:cacheprovider`; no separate RED commit.

T013 selects one exact clean integrated revision containing T012 GREEN, then records two
owner-selected fresh independent source clones, venvs and output directories at that same
revision. Install locked dependencies only through the existing normal cache/approval path;
no alternate cache, mirror, configuration change or bypass. Both environments build and verify
all eight files with their own authenticated tools, run contract and full tests, and compare
every output byte. Two invocations in one checkout/venv are insufficient; a same-host result
must state that cross-host/platform reproduction is unestablished. T012 supplies explicit
`--source-root`/`--output` builder and `--source-root`/`--release` verifier selection; T013 records
the actual absolute roots and exact commands, revisions, modes, raw/source-tree hashes and
canonical output sizes/hashes separately.

Only after all gates PASS, including tracked root Apache-2.0 LICENSE, exact distributable and
applicable third-party/NOTICE review, T013 materializes the entire eight-file inventory in
`build/releases/core-admission/` and writes `docs/evidence/umbrella-001/T012-core-admission-api.json`
plus its own completion/current task fields. Source/schema, finite conformance, replay-binding
and implementation-agreement results are limited to the implemented source/tooling and test
scope; they do not establish live authentication, replay/CAS, intake, snapshot/storage or runtime.
Preserve Candidate's eight files and historical evidence at source
`5f19a7d2ac2510c38c48c9aba0c6213cf89ee4a1`, manifest SHA-256
`67aca6754c610d48df25836a7fd9dbef90f9a8966741aaeee5cdca0ca7c3685f`.
Preservation uses byte comparisons and the original verifier in the pinned clean Candidate
source, never the modified current verifier pretending to have historical tool identity.
Tag, publication, remote readback, consumer activation and Alpha stay `NOT RUN`; immutable
locator stays `UNESTABLISHED`. T014's two publication slots and T032/T033 stay separate and
unchanged; no `1.0.0` promotion is authorized.

### Candidate Intake and Effects

T042/FR-027–FR-039 replace the semantic-content schema/value wrapper with resources/items and
the wire model in [data-model.md](data-model.md#semantic-content-wire-model-t042-authority).
All five principal definitions and their closed nested records remain in the existing semantic
schema. Candidate's existing external `$ref` already reaches it; provenance.value remains one
opaque projection identity and processing-profile stays opaque. No other normative schema needs
a shape change for T042. If later requirements exceed that projection boundary, coordinate a
separate contract change instead of widening this task.

The implementation sequence is T042 intentional RED → T043 schema GREEN plus central T077 input
→ T044 release-tooling GREEN → T009 regenerated local release candidate in two clean environments
using the repaired T007 tooling → separately authorized T032
publication/readback. T043 must retain the frozen oracle; no GREEN-by-weakening fixtures/checks.
Historical T010 evidence applies only to its recorded revision and cannot establish this redesign.

T017/T018 later validate Resource/segment/part/option/slot/token/overlay/response identities,
declaration-to-interaction correspondence, original-text ownership, digest and offset semantics,
and typed operation/reference relationships **within the existing Core admission validation
step**, after authorization and byte verification and before accepted snapshot custody. Automatic
performs its own producer validation with its independent private model. No shared model import,
new adapter authority, later product effect, or post-admission read is introduced.

```text
released Admission Request/Handoff
  -> delivery authentication
  -> operation-specific authorization
  -> independent oCIS intake and remote precondition
  -> complete byte/schema/inventory and Core reference verification
  -> Core-controlled snapshot write/readback
  -> admission record only

later explicit requests
  -> identity assignment
  -> repositoryd publication/readback/reconciliation
  -> duckdbd adoption/projection/readback/reconciliation
```

After accepted admission, every path starts from the Core snapshot and Core records. There is no
post-admission oCIS read, direct canonical-root or DuckDB-file access, or repositoryd-to-duckdbd
call.

## Project Structure

### Documentation

```text
specs/001-product-runtime/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── tasks.md
├── contracts/
│   ├── candidate-content.md
│   └── core-admission.md
└── checklists/
    └── requirements.md
```

### Package, Contracts, Source, Tests, Configuration, and Evidence

```text
.python-version
pyproject.toml
uv.lock

contracts/
├── candidate-content/
│   ├── candidate.schema.json
│   ├── semantic-content.schema.json
│   ├── provenance.schema.json
│   ├── processing-profile.schema.json
│   └── conformance/
│       ├── positive.json
│       └── negative.json
├── core-admission/
│   ├── openapi.yaml
│   ├── handoff-reference.schema.json
│   └── conformance/
│       ├── positive.json
│       └── negative.json
├── repositoryd/openapi.yaml
└── duckdbd/openapi.yaml

tools/
├── build_candidate_content_release.py
├── build_core_admission_release.py
└── verify_release.py

src/studious_lamp/
├── domain/
│   ├── models.py
│   └── policy.py
├── application/
│   ├── ports.py
│   ├── authentication.py
│   ├── authorization.py
│   ├── handoff.py
│   ├── admission.py
│   └── lifecycle.py
├── adapters/
│   ├── ocis.py
│   ├── snapshot.py
│   ├── repositoryd.py
│   └── duckdbd.py
├── delivery/
│   ├── http.py
│   ├── mcp.py
│   └── agent_plugin.py
├── repositoryd/service.py
├── duckdbd/service.py
├── duckdbd/migrations/001_initial.sql
└── composition.py

tests/
├── test_architecture.py
├── contracts/
│   ├── test_candidate_content.py
│   └── test_core_admission.py
├── core/
│   ├── test_authorization.py
│   ├── test_handoff_mapping.py
│   ├── test_admission.py
│   ├── test_lifecycle.py
│   ├── test_replay.py
│   └── test_response_loss.py
├── integration/
│   ├── test_ocis_intake.py
│   ├── test_repositoryd.py
│   └── test_duckdbd.py
├── delivery/test_interfaces.py
└── fixtures/synthetic/
    ├── candidate.json
    ├── semantic-content.json
    ├── provenance.json
    ├── processing-profile.json
    └── handoff-reference.json

config/
├── core.example.toml
├── repositoryd.example.toml
├── duckdbd.example.toml
└── quack.example.toml

docs/evidence/umbrella-001/
├── T010-four-content-contracts.json
├── T011-content-release-candidate.json
├── T012-core-admission-api.json
├── T013-release-readback.json
├── T017-independent-intake.json
├── T018-core-lifecycle.json
├── T019-persistence-boundaries.json
├── T020-core-public-interface.json
├── T030-alpha-fixtures.json
└── alpha/
    ├── AT-003-public-contract.json
    ├── AT-009-handoff-integrity-negative.json
    ├── AT-010-core-authorization.json
    ├── AT-011-admission-separation.json
    ├── AT-012-repository-publication.json
    ├── AT-013-duckdb-adoption.json
    ├── AT-015-exact-conflicting-replay.json
    └── AT-016-lost-response.json
```

Build outputs are generated and verified by future tasks; they are not created by T004. The
`.gitignore` already excludes `/build/`, so later release-candidate evidence must record exact
output digests without confusing ignored local output with publication.

## Delivery Phases and Gates

1. **Setup and dependency lock**: create the minimal package, exact Python/dependency lock, and
   deterministic test command. No network-dependent task starts without separate permission.
2. **Candidate-content source and conformance**: implement four schemas, positive/negative vectors,
   deterministic build, disclosure checks, exact inventory, and retired-form rejection.
3. **Core API and service contracts**: select the independent Core release identity, implement the
   Handoff/API and repositoryd/duckdbd service contracts, and add conformance/replay checks.
4. **Domain/application foundation**: implement owner-local models, policy, ports, authentication,
   authorization, Handoff mapping, idempotency, and effect states.
5. **Independent intake and snapshot**: implement Core oCIS intake, full verification, mutation
   detection, snapshot custody/readback, authorization denial, replay, and post-admission no-read.
6. **Separate persistence effects**: implement Core adapters and the repositoryd/duckdbd runtimes
   with independent outcomes, sole-writer/open rules, partial failure, and uncertainty.
7. **Delivery interfaces**: implement HTTP, MCP, and Agent Plugin adapters over the same use cases
   and denial semantics.
8. **Local release candidates and owner evidence**: build/verify both local candidates, licensing
   and distribution inputs, write T010–T012/T017–T020 evidence, and initialize T013 publication
   slots as `NOT RUN`/`UNESTABLISHED` only.
9. **Synthetic Alpha inputs**: freeze fixtures and exact commands/evidence slots for T030 and the
   Studious-owned AT scenarios without executing Alpha.

Each phase is decomposed into one-task branch/commit/no-ff units in `tasks.md`. Publication,
runtime, E2E, Alpha, restore, deployment, and production remain outside this implementation plan's
automatic effects.

## Validation Strategy

### T042 bounded RED oracle

`tests/contracts/test_candidate_content.py` reads the two existing conformance JSON files. The
positive Candidate has one shared synthetic Resource and twelve Items. Schema-negative records
mutate a valid baseline; baseline acceptance must succeed before any rejection can count, so an
unimplemented schema cannot obtain a false negative-vector PASS. Runtime-negative records are
required to remain schema-valid after T043, but record Core rejection as a future obligation;
they do not run a Core validator. The matrix and finite fixture sanity checks are not a runtime
implementation or public-release conformance certificate.

Because no JSON Schema dependency is locked, a small test-only, fail-closed evaluator covers only
the explicitly supported keywords used by these schemas. It permits exact-four local file refs
and local `$defs`, never network resolution. Unknown validation keywords fail the check rather
than silently passing. Self-tests exercise rejection independently of the missing hard-cut
schema. T043 must keep within that evaluated subset or coordinate a separately authorized locked
validator dependency; this helper is not a complete Draft 2020-12 implementation or production
validator. JSON `format` is annotation-only in this oracle.

Supported assertions are type (one type per node), properties/required/additionalProperties
(boolean), items/minItems/maxItems/uniqueItems, enum/const, oneOf/anyOf/allOf/not,
minLength/maxLength/pattern, minimum/maximum, and the exact local references described above.
Annotations are $schema/$id/$defs/$comment/title/description/format. There is no implicit support
for conditional, unevaluated, pattern-property or remote-reference vocabularies.

Run from the T042 worktree, using the existing offline cache and isolated environment:

```bash
UV_PROJECT_ENVIRONMENT=/tmp/studious-t042-venv UV_CACHE_DIR=/home/choi-eunchang/.cache/uv uv run --locked --offline pytest -q -p no:cacheprovider --tb=no
UV_PROJECT_ENVIRONMENT=/tmp/studious-t042-venv UV_CACHE_DIR=/home/choi-eunchang/.cache/uv uv run --locked --offline pytest -q -p no:cacheprovider -k 'not t042_schema' --tb=short
git diff --check
```

T042 completion is the observed intentional RED plus unrelated checks PASS, not full-suite PASS.
Any failure outside the named `t042_schema` group blocks integration. T043 must make the complete
suite GREEN; T009 independently builds/verifies new bytes. No T042 command creates release bytes,
T077 evidence, runtime state, or remote effects. XML/QTI/LOM/Common Cartridge exporters, PCI,
Usage Data stores, IRT and Rasch are excluded.

### Subsequent owner-task validation

T044 is one GREEN repair, with no separate RED commit. Keep the 114 frozen checks unchanged and
add independent release regressions in `tests/contracts/test_candidate_content_release.py`:
RFC 8785 canonical JSON/JSONL bytes (including number and Unicode-key cases), all twelve
mode/hash/path source records, revision/raw-source/canonical-output/provenance bindings, §3.3
manifest fields, and missing/extra/dirty source, checksum and inventory rejection. Expected bytes
and negative verdicts must not come solely from the builder's `expected_release_files` helper.
Build/verify only task-owned temporary outputs; preserve the five existing dirty T009 outputs.
Current Python 3.14.4 `json.dumps` emits `1.0` and sorts keys by code point rather than JCS UTF-16
order; the installed locked environment has no JCS package. T044 may select and exact-pin one
standards-conforming JCS dependency in `pyproject.toml`/`uv.lock` after verifying suitability;
package/version selection remains `UNESTABLISHED` here. Do not hand-roll a general canonicalizer,
weaken JCS, or alter frozen sources/tests/fixtures to obtain GREEN. Only full required PASS allows
T044 integration. T009 then materializes the same exact integrated source revision in two
owner-selected clean source/environment roots, records their identities and actual commands,
compares all eight output bytes, and verifies both raw-source and canonical-output digests.
Two runs in one checkout/venv or a builder assertion cannot establish this gate; absent the
second environment result, candidate PASS is prohibited. Publication remains `NOT RUN`.

- parse all JSON and TOML/YAML where a local parser is locked;
- run `uv run --locked pytest -q` after setup exists;
- run `uv run --locked python tools/verify_release.py` for deterministic local release candidates;
- assert the exact four Candidate-content source and release inventories;
- assert independent release identities and zero shared manifest/version inference;
- reject retired forms, unsafe paths, private fields, mutable selectors, weak preconditions,
  missing/extra/changed bytes, exact/conflicting replay, and lost response without reconciliation;
- inspect imports/call graphs for inward dependencies, sibling imports, direct storage, shared oCIS,
  repositoryd-to-duckdbd, and post-admission oCIS reads;
- validate evidence JSON statuses and literal paths;
- run the Umbrella offline structured-evidence validator from its verified checkout for each
  coordination evidence change; and
- review staged content for secrets, PII, private profiles, raw provenance, credential-bearing
  URLs, and operational bindings.

## Status Ledger

| Claim | Current status | Reason |
|---|---|---|
| Spec Kit 1.0.1 project initialization | `PASS` | Bundled offline init, healthy Codex integration, managed hashes/syntax verified |
| Owner feature planning | `PASS` only when T004 evidence validates | This document and its task graph are T004 outputs |
| T001–T008 lock/source/tests/contracts | Historical task-scoped results | See unchanged completion rows/evidence; no semantic hard-cut claim |
| T042 semantic-content schema | Intentional `FAIL` (RED) | Requirements/oracle fixed; unchanged schema is missing the hard cut |
| T043 GREEN / T077 input | `NOT RUN` | Subsequent owner-local task |
| Post-hard-cut Candidate-content local release candidate | `NOT RUN` | T009 must regenerate after T043; historical bytes remain untouched |
| Core API/Handoff identity and source | `PASS` for T011 source selection/static checks | `core-admission-0.2.0` / `0.2.0` / tag target `core-admission-v0.2.0`; no tag created; frozen 422 checks PASS |
| Core API/Handoff local release candidate | `NOT RUN` | T012 tooling GREEN must integrate before T013 builds/verifies two clean environments and materializes all eight files |
| Publication/remote readback | `NOT RUN` | Separately authorized per release |
| Intake/lifecycle/persistence/interfaces | `NOT RUN` | No source/runtime execution exists |
| Quack production readiness | `UNESTABLISHED` | Exact versions and required gates absent |
| E2E/Alpha/recovery/production | `NOT RUN` | Not authorized by T004 |

## Complexity Tracking

No exception is accepted. The two release lines are real independent public surfaces; the five
application port responsibilities are real policy/technology boundaries; repositoryd and duckdbd
remain distinct effects. No framework hierarchy, plugin registry, shared adapter library,
compatibility layer, generic repository abstraction, or speculative recommendation subsystem is
planned.
