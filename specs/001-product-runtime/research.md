# Research: Studious Product Runtime

**Date**: 2026-08-30

**Status**: Owner-planning decisions only; implementation and runtime evidence `NOT RUN`

## Decision 1: Keep one Studious product package with separate runtime boundaries

**Decision**: Use one `studious_lamp` package for owner-local domain/application policy and outer
adapters, while repositoryd and duckdbd remain separate service modules, ports, persistence
owners, failure outcomes, and recovery interfaces.

**Rationale**: Studious is one cohesive product owner. Separate repositories or a generic service
framework would add release coupling without changing semantic ownership.

**Alternatives considered**: A multi-repository split, shared cross-project SDK, generic plugin
registry, and repositoryd-to-duckdbd pipeline were rejected.

## Decision 2: Use Python 3.14.4 and uv from the T001 survey

**Decision**: The setup task will record Python 3.14.4 in `.python-version`, define the minimum
package/test dependencies in `pyproject.toml`, and lock exact artifacts in `uv.lock`.

**Rationale**: These tools were observed by T001, match the repository's Python ignore policy, and
avoid inventing a second toolchain.

**Alternatives considered**: Adding a second language, package manager, build system, linter, type
checker, or CI service before an owner need is demonstrated was rejected.

## Decision 3: Use two independent deterministic release builders

**Decision**: `tools/build_candidate_content_release.py` and
`tools/build_core_admission_release.py` build distinct release trees, while
`tools/verify_release.py` applies common exact-byte, inventory, checksum, provenance, and
conformance checks without merging release identities.

**Rationale**: The two release lines share deterministic mechanics but not version, tag, manifest,
artifact inventory, publication, readback, or consumer activation.

**Alternatives considered**: One shared bundle, one version train, copying outputs between release
lines, and compatibility aliases were rejected.

## Decision 4: Hard-cut Candidate release-evidence filenames to the Umbrella contract

**Decision**: The generated Candidate-content evidence files are
`candidate-content.manifest.json`, `candidate-content.conformance.jsonl`,
`candidate-content.provenance.intoto.jsonl`, and `SHA256SUMS` under
`build/releases/candidate-content/0.1.0/`.

**Rationale**: These are the exact names in the authoritative public-release coordination
contract. The generic `manifest.json`, `checksums.sha256`, and `provenance.json` names in T001's
pre-implementation output survey are not retained as parallel aliases; the pre-1.0 hard cut favors
one active form.

**Alternatives considered**: Generate both name sets, preserve generic aliases, or weaken the
Umbrella contract to a conceptual label. Each would create two active release surfaces.

## Decision 5: Resolve the Core API/Handoff release identity in its first contract task

**Decision**: The Core API/Handoff contract task selects and records one independent pre-1.0
version and tag in the exact contract/release sources. Until that task is completed and verified,
the identity remains `UNESTABLISHED` and no consumer or publication task may proceed.

**Rationale**: Umbrella deliberately leaves this owner decision open. Guessing it in the T004 plan
would convert missing evidence into a false fact.

**Alternatives considered**: Reusing `0.1.0` / `contract-v0.1.0`, deriving the identity from the
Candidate release, or leaving implementation tasks with symbolic paths were rejected.

## Decision 6: Keep five application port responsibilities explicit

**Decision**: `src/studious_lamp/application/ports.py` owns Candidate intake, snapshot custody,
canonical publication, product state, and delivery authentication responsibilities. Concrete oCIS,
snapshot, repositoryd, duckdbd, HTTP, MCP, and Agent Plugin types stay outside those interfaces.

**Rationale**: Each port separates owner policy from one technology boundary. More granular one-
method interfaces or a generic repository/service abstraction would be speculative.

**Alternatives considered**: Shared oCIS code, direct filesystem/database access, one generic
storage port, and vendor DTOs in application code were rejected.

## Decision 7: Store admission and effect state in Core-owned custody

**Decision**: Core retains verified Candidate bytes and records authorization, admission,
idempotency, lifecycle, outcome, and reconciliation state behind the snapshot/application boundary.
Later effects consume those records and never renew an oCIS read.

**Rationale**: oCIS has one shared real user and is a non-authoritative transfer surface. Core
custody is required for integrity, retry, restart, and recovery semantics.

**Alternatives considered**: oCIS paths/ACLs as authority, producer readback as acceptance,
post-admission re-download, and direct repositoryd/DuckDB state as the admission record were
rejected.

## Decision 8: Keep repositoryd and duckdbd independently idempotent

**Decision**: Core makes separate explicit requests through `adapters/repositoryd.py` and
`adapters/duckdbd.py`. Each service owns its idempotency readback and uncertain-poststate
reconciliation. repositoryd never calls duckdbd, and duckdbd is the only writable DuckDB opener.

**Rationale**: Canonical byte publication and authoritative relational state have different
failure, backup, and recovery semantics.

**Alternatives considered**: A distributed transaction, repositoryd callback, direct Core DuckDB
open, or compensation presented as rollback was rejected.

## Decision 9: Share use cases, not delivery behavior

**Decision**: HTTP, MCP, and Agent Plugin modules validate their transport contracts and then call
the same application authentication, authorization, admission, and lifecycle use cases.

**Rationale**: This prevents each transport from inventing policy while keeping transport-specific
bounds and error mapping outside Core policy.

**Alternatives considered**: Separate business logic per interface and a generic plugin framework
were rejected.

## Decision 10: Freeze evidence before operational work

**Decision**: Owner evidence records use only `PASS`, `FAIL`, `NOT RUN`, or `UNESTABLISHED`, name
exact source revisions, commands, inputs, locators, digests, time, and limitations, and contain no
protected value. T013 contains two independent publication/readback slots and begins `NOT RUN` or
`UNESTABLISHED`; Alpha evidence files remain unexecuted until separately authorized.

**Rationale**: A local build, source test, or plan cannot establish immutable publication,
runtime, E2E, Alpha, recovery, or production readiness.

**Alternatives considered**: Boolean readiness, a combined release result, inferred PASS, or raw
operational evidence in Git were rejected.

## Remaining Evidence-Bound Decisions

- exact project dependencies and locked versions;
- Core API/Handoff version, tag, exact release inventory, and immutable publication mechanism;
- concrete snapshot persistence mechanism;
- exact HTTP, MCP, and Agent Plugin protocol revisions and authentication binding;
- exact oCIS, repositoryd, DuckDB, and Quack client versions;
- endpoints, credentials, resource identities, deployed service identities, storage roots, and
  runtime configuration;
- publication, remote readback, runtime, E2E, Alpha, recovery, performance, and production results.

Each item has a dependency-ordered task or remains explicitly outside this feature's authorized
effects.
