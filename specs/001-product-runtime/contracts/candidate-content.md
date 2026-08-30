# Owner Contract Plan: Candidate Content

**Owner**: Studious Lamp

**Target**: `0.1.0` / `contract-v0.1.0`

**Current status**: Source, local release candidate, publication, and readback `NOT RUN`

## Normative Source Inventory

Exactly these four JSON Schema 2020-12 files are normative Candidate-content contracts:

```text
contracts/candidate-content/candidate.schema.json
contracts/candidate-content/semantic-content.schema.json
contracts/candidate-content/provenance.schema.json
contracts/candidate-content/processing-profile.schema.json
```

`candidate.schema.json` binds Candidate ID, exact release/manifest identity, normalized payload
paths, media types, byte sizes/digests, semantic content, disclosure-safe provenance, opaque
processing-profile reference, and representation inventory.

`semantic-content.schema.json` contains product-facing transferred meaning only.
`provenance.schema.json` contains the disclosure-safe projection only.
`processing-profile.schema.json` contains an opaque producer-scoped reference only.

No schema contains extraction behavior, source layout, raw provenance, private profile content,
credentials, binding names, local/sync paths, runtime endpoints, or oCIS principal identity.

## Conformance Inputs

```text
contracts/candidate-content/conformance/positive.json
contracts/candidate-content/conformance/negative.json
tests/fixtures/synthetic/candidate.json
tests/fixtures/synthetic/semantic-content.json
tests/fixtures/synthetic/provenance.json
tests/fixtures/synthetic/processing-profile.json
tests/contracts/test_candidate_content.py
```

Positive inputs cover one complete exact-four Candidate. Negative inputs cover missing/fifth/
unknown schemas, the retired Extractor Protocol, wrong dialect/version/size/digest, mutable
selector, unsafe/duplicate/missing/extra payload paths, malformed bytes, private-field leakage, and
evidence misclassified as a content contract.

## Deterministic Release Candidate

Builder and verifier:

```text
tools/build_candidate_content_release.py
tools/verify_release.py
```

Generated local output:

```text
build/releases/candidate-content/0.1.0/candidate.schema.json
build/releases/candidate-content/0.1.0/semantic-content.schema.json
build/releases/candidate-content/0.1.0/provenance.schema.json
build/releases/candidate-content/0.1.0/processing-profile.schema.json
build/releases/candidate-content/0.1.0/candidate-content.manifest.json
build/releases/candidate-content/0.1.0/candidate-content.conformance.jsonl
build/releases/candidate-content/0.1.0/candidate-content.provenance.intoto.jsonl
build/releases/candidate-content/0.1.0/SHA256SUMS
```

JSON uses UTF-8 RFC 8785 JCS with no BOM, insignificant whitespace, or trailing newline. JSONL
uses one JCS object plus LF per record. `SHA256SUMS` contains lowercase SHA-256, two spaces, a safe
relative filename, LF, unsigned UTF-8 filename order, and no self-entry.

The manifest records target version/tag, schema dialect, serialization, source revision/tree,
generation tool, compatibility policy, Apache-2.0, exactly four artifact entries, conformance
identity, and retired forms. It contains no Core API/Handoff component or invented remote value.

## Release Gates

Local release-candidate `PASS` requires:

- exact clean source revision and deterministic source-tree digest;
- two byte-identical builds;
- exact-four source and output inventories;
- positive and negative conformance;
- checksums and verified provenance;
- tracked Apache-2.0 declaration;
- exact distributable inventory and applicable third-party/NOTICE checks; and
- zero active Extractor Protocol, fifth contract, private value, mutable selector, or alias.

Tag, immutable publication, and remote readback are separate per-release effects. They are not
authorized or executed by the owner implementation tasks that create the local candidate.

## Evidence Outputs

```text
docs/evidence/umbrella-001/T010-four-content-contracts.json
docs/evidence/umbrella-001/T011-content-release-candidate.json
docs/evidence/umbrella-001/T013-release-readback.json
docs/evidence/umbrella-001/alpha/AT-003-public-contract.json
```

T010 and T011 may report `PASS` only for their exact verified source/local-candidate scope. T013
starts with publication/readback `NOT RUN`; AT-003 remains `NOT RUN` until separately authorized
Alpha execution against immutable releases.
