# Quickstart: Validate the Studious Product Runtime

**Status**: Commands planned; implementation-dependent commands `NOT RUN`

This guide is a deterministic validation map, not a deployment or publication script. It performs
no tag, remote publication/readback, runtime startup, live Handoff, Alpha fault, restore, deletion,
or production effect.

## Result Vocabulary

| Status | Meaning |
|---|---|
| `PASS` | Current evidence satisfies the exact named check. |
| `FAIL` | Current evidence contradicts a required criterion. |
| `NOT RUN` | The check has not executed. |
| `UNESTABLISHED` | Required identity, dependency, binding, or evidence is missing or inconclusive. |

## 1. Planning Prerequisites

From the repository root:

```bash
specify --version
specify check
specify integration status
.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
```

Expected after T004: Spec Kit is `1.0.1`; Codex is available; integration status is healthy; the
feature directory resolves to `specs/001-product-runtime`; and all design documents plus
`tasks.md` are listed. This establishes planning only.

## 2. Owner Package Check

After the setup task creates and locks the package:

```bash
uv sync --locked --dev
uv run --locked pytest -q
```

Before that task, both commands are `NOT RUN`; missing `pyproject.toml` or `uv.lock` is not a T004
failure.

## 3. Candidate-Content Gate

```bash
uv run --locked pytest -q tests/contracts/test_candidate_content.py
uv run --locked python tools/build_candidate_content_release.py
uv run --locked python tools/verify_release.py --release build/releases/candidate-content/0.1.0
```

PASS requires exactly four source and output schemas, deterministic byte-identical rebuild,
positive/negative conformance, safe/disclosure-bounded content, the four exact release-evidence
files, checksums/provenance, tracked Apache-2.0, exact distributable inventory, applicable third-
party/NOTICE checks, and zero active Extractor Protocol or compatibility aliases.

The local candidate does not establish tag, immutable publication, remote readback, consumer
activation, or runtime readiness.

## 4. Core API/Handoff Gate

```bash
uv run --locked pytest -q tests/contracts/test_core_admission.py
uv run --locked pytest -q tests/core/test_handoff_mapping.py
uv run --locked python tools/build_core_admission_release.py
uv run --locked python tools/verify_release.py --release build/releases/core-admission
```

PASS requires one owner-selected independent pre-1.0 version/tag, mandatory Handoff semantics,
forbidden-field and weak-precondition rejection, exact/conflicting replay vectors, implementation
agreement, deterministic release evidence, and no implied Candidate-content version relationship.

## 5. Architecture and Authorization Gate

```bash
uv run --locked pytest -q tests/test_architecture.py
uv run --locked pytest -q tests/core/test_authorization.py
```

PASS requires inward dependencies, no sibling implementation import/shared oCIS runtime, no
technology type in application ports, authorization before intake/effects, and zero calls on
denial.

## 6. Independent Intake Gate

```bash
uv run --locked pytest -q tests/core/test_admission.py
uv run --locked pytest -q tests/integration/test_ocis_intake.py
```

PASS covers exact Handoff and Candidate pins, conditional manifest reads, before/after inventory,
all payload sizes/digests, missing/extra/duplicate/unsafe/malformed/mutated cases, owner-model
mapping, immutable snapshot write/readback, and no accepted admission without custody.

The integration fixture is synthetic and uses a fake/controlled adapter boundary; it must not
create an extra oCIS account or contact a protected runtime without separate authorization.

## 7. Lifecycle and Persistence Gates

```bash
uv run --locked pytest -q tests/core/test_lifecycle.py tests/core/test_replay.py tests/core/test_response_loss.py
uv run --locked pytest -q tests/integration/test_repositoryd.py
uv run --locked pytest -q tests/integration/test_duckdbd.py
```

PASS requires later effects initially `NOT_ATTEMPTED`, separate authorized requests, exact replay
without duplication, conflicting replay rejection, uncertain poststate plus reconciliation,
repositoryd-only canonical writes, duckdbd-only persistent opens/writes, independent partial
outcomes, and no repositoryd-to-duckdbd or post-admission oCIS call.

## 8. Delivery Interface Gate

```bash
uv run --locked pytest -q tests/delivery/test_interfaces.py
```

PASS requires HTTP, MCP, and Agent Plugin adapters to enforce their exact released shapes/bounds
and invoke the same Core authentication, authorization, idempotency, reason-code, and lifecycle
semantics. Malformed or denied requests perform no downstream effect.

## 9. Evidence Gate

Owner evidence files are JSON under `docs/evidence/umbrella-001/`. Validate locally with:

```bash
python3 -m json.tool docs/evidence/umbrella-001/T010-four-content-contracts.json
python3 -m json.tool docs/evidence/umbrella-001/T011-content-release-candidate.json
python3 -m json.tool docs/evidence/umbrella-001/T012-core-admission-api.json
python3 -m json.tool docs/evidence/umbrella-001/T013-release-readback.json
python3 -m json.tool docs/evidence/umbrella-001/T017-independent-intake.json
python3 -m json.tool docs/evidence/umbrella-001/T018-core-lifecycle.json
python3 -m json.tool docs/evidence/umbrella-001/T019-persistence-boundaries.json
python3 -m json.tool docs/evidence/umbrella-001/T020-core-public-interface.json
python3 -m json.tool docs/evidence/umbrella-001/T030-alpha-fixtures.json
```

Run the coordination validator from the exact verified Umbrella checkout:

```bash
UV_CACHE_DIR="$PWD/.tools/uv-cache" uv run --locked --offline python tools/validate_traceability.py
```

with working directory `/home/choi-eunchang/Documents/ChatGPT/symmetrical-umbrella`. A PASS validates
the current Umbrella registry, not the contents or runtime result of a child evidence file.

## 10. Frozen Studious Alpha Commands

These commands and outputs are planned/frozen but remain `NOT RUN` until Umbrella entry is `MET`
and separate Alpha execution authorization exists:

| Scenario | Exact command | Synthetic input | Git evidence output |
|---|---|---|---|
| `AT-003 PUBLIC-CONTRACT` | `uv run --locked pytest -q tests/contracts/test_candidate_content.py tests/contracts/test_core_admission.py` | `tests/fixtures/synthetic/candidate.json`, `tests/fixtures/synthetic/handoff-reference.json` | `docs/evidence/umbrella-001/alpha/AT-003-public-contract.json` |
| `AT-009 HANDOFF-INTEGRITY-NEGATIVE` | `uv run --locked pytest -q tests/integration/test_ocis_intake.py::test_handoff_integrity_negative_catalog` | `contracts/core-admission/conformance/negative.json` | `docs/evidence/umbrella-001/alpha/AT-009-handoff-integrity-negative.json` |
| `AT-010 CORE-AUTHORIZATION` | `uv run --locked pytest -q tests/core/test_authorization.py::test_denial_performs_no_intake_or_effect` | `tests/fixtures/synthetic/handoff-reference.json` | `docs/evidence/umbrella-001/alpha/AT-010-core-authorization.json` |
| `AT-011 ADMISSION-SEPARATION` | `uv run --locked pytest -q tests/core/test_admission.py::test_acceptance_stops_after_snapshot` | `tests/fixtures/synthetic/candidate.json` | `docs/evidence/umbrella-001/alpha/AT-011-admission-separation.json` |
| `AT-012 REPOSITORY-PUBLICATION` | `uv run --locked pytest -q tests/integration/test_repositoryd.py::test_publication_uses_repositoryd_only` | `tests/fixtures/synthetic/candidate.json` | `docs/evidence/umbrella-001/alpha/AT-012-repository-publication.json` |
| `AT-013 DUCKDB-ADOPTION` | `uv run --locked pytest -q tests/integration/test_duckdbd.py::test_adoption_uses_duckdbd_only` | `tests/fixtures/synthetic/candidate.json` | `docs/evidence/umbrella-001/alpha/AT-013-duckdb-adoption.json` |
| `AT-015 EXACT-CONFLICTING-REPLAY` | `uv run --locked pytest -q tests/core/test_replay.py::test_exact_and_conflicting_replay` | `tests/fixtures/synthetic/handoff-reference.json` | `docs/evidence/umbrella-001/alpha/AT-015-exact-conflicting-replay.json` |
| `AT-016 LOST-RESPONSE` | `uv run --locked pytest -q tests/core/test_response_loss.py::test_lost_response_reconciles_before_retry` | `tests/fixtures/synthetic/candidate.json` | `docs/evidence/umbrella-001/alpha/AT-016-lost-response.json` |

The owner tasks must create these exact test functions before any scenario is executable. Unit or
controlled integration results cannot by themselves establish deployed E2E, recovery, or
production readiness.

## 11. Secret and Scope Review

Before every owner commit:

```bash
git diff --cached --check
git diff --cached --name-status
git diff --cached
```

Review for tokens, passwords, private keys, credential-bearing URLs, real endpoints/resource IDs,
PII, real educational content, private profiles, raw provenance, broad sync paths, operational
bindings, and files outside the task's exact path set. Stop on any suspected secret or overlap.
