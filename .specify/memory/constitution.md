# Studious Lamp Constitution

## Core Principles

### I. Studious Owns One Product Boundary

Studious Lamp is the sole product/runtime owner. It owns the Candidate-content contracts, Core
Admission API/Handoff Reference, Core policy and lifecycle, repositoryd, and duckdbd boundaries.
It must not copy Automatic private implementation or Upgraded deployment mechanisms.

### II. Dependencies Point Inward

Domain and application policy own technology-neutral ports. HTTP, MCP, Agent Plugin, oCIS,
repositoryd, duckdbd/Quack, filesystem, credentials, and other technologies remain outer adapters.
Sibling implementation imports and shared first-party oCIS runtime packages are prohibited.

### III. Contracts and Effects Stay Separate

The Candidate-content release contains exactly four schemas. The Core Admission API/Handoff
Reference is independently versioned. Admission, identity, publication, adoption, and projection
remain separately requested, authorized, idempotently recorded effects; uncertain poststates are
reconciled before retry.

### IV. Evidence Bounds Every Claim

Verification uses only `PASS`, `FAIL`, `NOT RUN`, or `UNESTABLISHED`. Evidence must bind exact
scope, source revision, method, time, locator, digest, and limitations. A design, local build,
upload, health check, or backup cannot establish publication, runtime, E2E, recovery, Alpha, or
production readiness.

### V. Pre-1.0 Changes Are Hard Cuts

Active paths retain no Extractor Protocol, fifth Candidate-content contract, compatibility alias,
legacy reader, fallback, dual path, version negotiation, post-admission oCIS read, direct Core
storage access, or repositoryd-to-duckdbd chain. Historical immutable releases, data, provenance,
backups, and recovery evidence remain preserved.

### VI. Tasks Are Local Integration Units

Each owner-local Spec Kit task is one fresh branch, one verified Conventional Commit, and one local
no-fast-forward merge. Push, tag, publication, deployment, startup, Alpha, restore, migration,
deletion, and promotion remain separately authorized effects.

## Security and Data Boundaries

- Credentials, real endpoints, protected resource identifiers, PII, private profiles, raw
  provenance, and real educational content stay outside Git and synthetic fixtures.
- Exactly one real remotely usable oCIS user is permitted by the coordinated profile; that user is
  not a Core principal or evidence of Automatic/Core isolation.
- Core independently verifies every Candidate byte and retains a durable snapshot before
  admission; later effects never re-read oCIS.
- repositoryd is the sole canonical-object writer and duckdbd the sole writable DuckDB opener.

## Development Workflow

Plans and tasks must cite literal repository paths and deterministic checks. Tests cover positive,
negative, replay, partial, uncertain, disclosure, dependency, and recovery-oriented behavior at
the scope being implemented. No task may widen its evidence or perform an unauthorized remote or
operational effect.

## Governance

The Symmetrical Umbrella Constitution 0.3.0 and its Feature 001 contracts govern cross-project
authority and compatibility. This local constitution may add stricter owner rules but cannot
weaken them. Amendments require explicit rationale, compatibility impact, validation updates, and
user approval. No agent may promote this or another governed first-party line to `1.0.0` without a
direct human request naming that line and promotion.

**Version**: 0.1.0 | **Ratified**: 2026-08-30 | **Last Amended**: 2026-08-30
