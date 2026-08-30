# Owner Contract Plan: Candidate Content

**Owner**: Studious Lamp

**Target**: `0.1.0` / `contract-v0.1.0`

**Current status**: T042 requirements/design and intentional RED; T043 GREEN/T077, regenerated
T009 candidate, publication and readback are not established. Prior completion evidence is historical.

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

No schema contains extraction behavior, protected source layout, raw provenance, private profile content,
credentials, binding names, local/sync paths, runtime endpoints, or oCIS principal identity.

## Semantic-Content Hard Cut (T042)

FR-027–FR-039 in `specs/001-product-runtime/spec.md` and the Semantic Content Wire Model in
`specs/001-product-runtime/data-model.md` fix the exact required fields, optional fields, types,
identity scopes, metadata records, overlay targets, twelve payloads and declaration alternatives.
They are the T043 implementation authority. The new root is
`{"schema":"semantic-content.schema.json","resources":[],"items":[]}`; the old schema/value
form is rejection-only. `$defs.resource`, `$defs.item`, `$defs.content_part`,
`$defs.response_declaration`, `$defs.interaction` reside in that schema. Exactly one Resource
shape, one Item shape and twelve discriminated interaction.oneOf alternatives are permitted.
Every object is closed; no resource.schema.json, item.schema.json, fifth artifact, legacy reader
or compatibility alias is introduced. These names/JSON metadata are Studious's normalized
contract, not official QTI JSON field names. XML/PCI/export adapters are not implemented.

Resource originals are immutable; Item-owned overlays and segment references avoid edited or
duplicated authoritative Resource copies. Public source_anchor carries provenance_ref/page/block
only as a reviewed public-rendition projection, never the private original page/geometry/name.
When safe projection is unavailable, the optional anchor is absent, not a fabricated locator.
Stable Resource/block/segment identities remain. The one existing candidate.provenance.value
is used as an opaque public projection ID; no provenance shape change is needed. None of these
schema shapes grants authority to publish actual private values.

LOMv1.0 five-value difficulty is qualitative. textComplexity retains separate scale/score/unit
measurements, not a CEFR-only measurement enum. Automatic language/EGP/EVP references live under
Resource extensions; Item difficulty_evidence references profiles/reasoning/usage records and
does not derive difficulty from EGP CEFR appearance. educational_measurements is forbidden.
Usage Data, response-rate, IRT and Rasch stores remain separate unimplemented work.

### Validation ownership and conformance matrix

| Surface | Positive oracle | Rejection/limitation | Owner |
|---|---|---|---|
| Root / five `$defs` / closed objects | resources/items and exact four schemas | schema/value, missing fields, unknown keys/types | T043 |
| choice, reference_choice | separate option parts and declarations | missing response/reference payload, embedded answers | T043 shape; T017/T018 links |
| inline_mark_choice, sentence_mark_choice | mark/segment identity choices | unsupported payload and dangling refs | T043 shape; T017/T018 links |
| blank_choice, order_choice | gap overlay; unit/order options | missing blank/unit fields; invalid permutation | T043 shape; T017/T018 relationships |
| position_choice, summary_pair_choice | given sentence, slots, summary gaps and pair values | missing fields; invalid slot/gap correspondence | T043 shape; T017/T018 relationships |
| inline_choice_set, token_order | per-gap declarations; ordered token IDs | missing fields; missing/reused answer targets | T043 shape; T017/T018 correspondence |
| text_entry, edit_response | single/string and single/record | wrong declaration value shape; normalization/target mismatch | T043 shape; T017/T018 semantics |
| Metadata/extensions | five LOM values, Lexile and other scales, EGP/EVP refs | educational_measurements, wrong source/level/relationship/confidence, copied definitions | T043 local shape; disclosure review separately |
| Source anchors and overlays | public projection; original-text targets/digests | private locator/geometry keys; wrong digest/range or missing owner | T043 shape; T017/T018 binding and disclosure |
| Resource originals / responses | one Resource, twelve Items, one declaration per response | duplicate IDs, authoritative inline copies, dangling IDs | T017/T018; Automatic independently validates production |

`positive.json.candidate.semantic_content` contains a single shared synthetic Resource and exactly
one Item per interaction type, including non-ASCII original text to disambiguate code-point
offsets from UTF-8/UTF-16 units. Top-level text_entry_normalization_examples freeze NFC/LF without
trimming, casefolding or punctuation changes. `negative.json.semantic_content_cases` contains
50 schema-rejection and 28 future-Core-rejection mutation records:
`id`, `owner`, `schema_expected`, optional `runtime_expected`, and `operations`. Each operation
has `op` (add/replace/remove/copy), a typed path array, and value/from as applicable. These records
are test data, not normative schemas. Existing negative `cases` retain the earlier boundary
catalog. New cases have no real source data, URLs, private values or runtime bindings.

Schema-owned rows must reject only after the unmodified positive baseline is accepted. Core-owned
rows have schema_expected=accept and runtime_expected=reject: the schema oracle only confirms
their local shapes, never executes or certifies runtime rejection. The test-only evaluator's
supported subset and commands are fixed in `plan.md`; unsupported keywords fail closed. Original
text/digest/range bindings are checked on the finite synthetic baseline, not implemented as a
general Core validator. No full-suite PASS may be reported while T042 remains RED.

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

Positive inputs cover one complete exact-four Candidate with the T042 semantic hard-cut shape.
Negative inputs cover missing/fifth/
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

These are release-byte rules, not permission to rewrite the frozen raw source files. Bind each
raw schema/conformance input to its exact source revision and raw-byte SHA-256, and independently
verify the deterministic transformation to canonical released bytes with their own sizes and
SHA-256 values. Raw-source and canonical-output digests are distinct; output equality with the
pretty-printed T043 source is not required. The full twelve-file tracked input inventory and
mode/hash/path LF source-tree algorithm are declared in `plan.md`, following Umbrella §5.4.

The manifest records target version/tag, schema dialect, serialization, source revision/tree,
generation tool, compatibility policy, Apache-2.0, exactly four artifact entries, conformance
identity, and retired forms. It contains no Core API/Handoff component or invented remote value.

T044 must independently enforce all required bindings from Umbrella
`specs/001-product-compute-boundaries/contracts/public-contract-release.md` §3.3, including
`manifest_format_version`, `digest_algorithm` and the exact release/artifact/conformance identity.
The acyclic order is source → canonical schemas/conformance → manifest → provenance →
SHA256SUMS: provenance binds the exact manifest, schemas, vectors, builder/build definition,
source revision and full source-tree digest (§5.5); the manifest does not digest downstream
provenance. Checksums bind all seven other output files. An unconditional `reproducible: true`
is not evidence and must not be emitted before the actual second-environment result. Record that
result in T009 owner evidence without changing the compared deterministic bundle.

## Release Gates

Local release-candidate `PASS` requires:

- exact clean source revision, complete tracked source-tree digest, and separate raw-source and
  canonical-output byte bindings;
- T044 tooling/regression PASS followed by two byte-identical builds of all eight files from
  that same exact revision in two owner-selected clean environments (§5.5), with actual source
  roots, environment/tool identities, commands and results recorded by T009; two builds in one
  checkout/venv do not qualify, and an absent second-environment result cannot be PASS;
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
docs/evidence/umbrella-001/T077-semantic-content-hard-cut.json
docs/evidence/umbrella-001/T011-content-release-candidate.json
docs/evidence/umbrella-001/T013-release-readback.json
docs/evidence/umbrella-001/alpha/AT-003-public-contract.json
```

T010 and T011 may report `PASS` only for their exact verified source/local-candidate scope. T013
starts with publication/readback `NOT RUN`; AT-003 remains `NOT RUN` until separately authorized
Alpha execution against immutable releases.

T042 writes no evidence JSON. T043 later writes the new central T077 acceptance input with exact
Studious revision, schema/conformance digests, commands/results and the schema/runtime split.
Historical T010 evidence is valid only for its original revision, not this redesign. The sequence
is T042 RED → T043 GREEN/T077 → T044 release-tooling GREEN → T009 regenerated local candidate
with the second-clean-environment gate → separately authorized T032 publication/readback.
T044 corrects T007 tooling without changing frozen T043 inputs, existing dirty generated outputs,
or historical T010/T077 evidence and immutable releases.
