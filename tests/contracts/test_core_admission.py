"""T010 RED: static contract sources and finite synthetic vectors, never Core runtime.

Authority: specs/001-product-runtime/{data-model.md,contracts/core-admission.md}.
T011 owns the four absent normative files and exact release/auth/path/bounds choices.
No test imports a future admission use case or treats a fixture verdict as enforcement.
JSON-compatible OpenAPI can be read with the locked stdlib; other YAML needs a
separately authorized parser. This is not a general OpenAPI/JSON Schema validator.
"""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import re
from pathlib import Path

import pytest
import rfc8785

# Reuse the frozen, fail-closed test subset; no Candidate source or oracle edits.
from test_candidate_content import _accepts, _mutate

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "contracts/core-admission"
HANDOFF = "contracts/core-admission/handoff-reference.schema.json"
CORE_API = "contracts/core-admission/openapi.yaml"
NORMATIVE = (HANDOFF, CORE_API, "contracts/repositoryd/openapi.yaml", "contracts/duckdbd/openapi.yaml")
HANDOFF_FIELDS = (
    "handoff_reference_contract_version", "handoff_reference_contract_sha256",
    "environment_id", "space_id", "manifest_resource_id", "remote_manifest_precondition",
    "candidate_id", "candidate_contract_release_id", "candidate_contract_release_manifest_sha256",
    "candidate_manifest_sha256", "export_receipt_id",
)
PRECONDITION_FIELDS = ("version_id", "readback_size_bytes", "readback_sha256")
REQUEST_FIELDS = (
    "submission_id", "idempotency_key", "authenticated_request_context_id", "operation",
    "handoff_reference", "expected_candidate_id", "expected_candidate_manifest_sha256",
    "expected_candidate_contract_release_id", "requested_at",
)


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result, f"Duplicate JSON member: {key}"
        result[key] = value
    return result


def _read_json(path):
    def non_json_number(value):
        raise AssertionError(f"Non-JSON number: {value}")

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object,
                      parse_constant=non_json_number)


POSITIVE = _read_json(CONTRACT / "conformance/positive.json")
NEGATIVE = _read_json(CONTRACT / "conformance/negative.json")
SHAPES = NEGATIVE["shape_cases"]
RELATIONS = NEGATIVE["semantic_cases"]
VERSIONS = NEGATIVE["version_cases"]
REPLAYS = POSITIVE["replay_cases"] + NEGATIVE["replay_cases"]


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _source(path):
    file = ROOT / path
    assert file.is_file(), f"T010 RED: T011 normative source absent: {path}"
    try:
        value = _read_json(file)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"Cannot inspect {path} with the locked JSON reader: {exc}. "
            "Non-JSON YAML needs separately authorized locked tooling; no text-match fallback."
        ) from exc
    assert isinstance(value, dict), f"Contract must be an object: {path}"
    return value


def _expand(node, document, path, seen=()):
    """Resolve only exact local contract refs; no network, sibling or Candidate loader.

    The reused evaluator accepts only its documented schema subset. Cycles or new
    keywords fail explicitly instead of silently passing implementation agreement.
    """
    if isinstance(node, list):
        return [_expand(value, document, path, seen) for value in node]
    if not isinstance(node, dict):
        return node
    siblings = {key: _expand(value, document, path, seen) for key, value in node.items() if key != "$ref"}
    if "$ref" not in node:
        return siblings
    ref = node["$ref"]
    filename, _, fragment = ref.partition("#")
    target_path = path
    target_document = document
    if filename:
        candidate = (ROOT / path).parent / filename
        assert candidate.resolve() == (ROOT / HANDOFF).resolve(), f"Unsupported contract ref: {ref}"
        target_path, target_document = HANDOFF, _source(HANDOFF)
    assert not fragment or fragment.startswith("/"), f"Unsupported anchor: {ref}"
    identity = (target_path, fragment)
    assert identity not in seen, f"Cyclic contract ref: {identity}"
    target = target_document
    for part in fragment.split("/")[1:]:
        target = target[part.replace("~1", "/").replace("~0", "~")]
    expanded = _expand(target, target_document, target_path, (*seen, identity))
    return {"allOf": [expanded, siblings]} if siblings else expanded


def _handoff_schema():
    source = _source(HANDOFF)
    return _expand(source, source, HANDOFF)


def _exact_version(schema):
    """Inspect the selected source value; never select a release in this test."""
    prop = schema["properties"]["handoff_reference_contract_version"]
    value = prop.get("const")
    if value is None and len(prop.get("enum", [])) == 1:
        value = prop["enum"][0]
    assert isinstance(value, str) and re.fullmatch(r"0\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?", value), (
        "T011 must select one exact independent pre-1.0 Handoff version in its schema"
    )
    return value


def _candidate_version():
    schema = _read_json(ROOT / "contracts/candidate-content/candidate.schema.json")
    prop = schema["properties"]["contract"]["properties"]["version"]
    return prop["const"] if "const" in prop else prop["enum"][0]


def _request_for(schema):
    request = copy.deepcopy(POSITIVE["binding"]["request"])
    # Only source-version and raw-source-digest substitution. This is a local
    # contract input, not a released-byte digest or a supported production pin.
    request["handoff_reference"]["handoff_reference_contract_version"] = _exact_version(schema)
    request["handoff_reference"]["handoff_reference_contract_sha256"] = _sha((ROOT / HANDOFF).read_bytes())
    return request


def _openapi(path):
    api = _source(path)
    assert isinstance(api.get("openapi"), str) and api["openapi"].startswith("3."), path
    assert isinstance(api.get("info", {}).get("version"), str) and api["info"]["version"], path
    assert isinstance(api.get("paths"), dict) and api["paths"], path
    return api


def _admission_contract():
    """Discover the admission body by its semantic fields, without guessing a route."""
    api = _openapi(CORE_API)
    matches = []
    for path_item in api["paths"].values():
        for method, operation in path_item.items():
            if method not in {"get", "put", "post", "delete", "options", "head", "patch", "trace"}:
                continue
            body = _expand(operation.get("requestBody", {}), api, CORE_API)
            for media in body.get("content", {}).values():
                schema = _expand(media.get("schema", {}), api, CORE_API)
                if "handoff_reference" in schema.get("properties", {}):
                    matches.append((operation, body, schema))
    assert len(matches) == 1, "T011 must expose one exact admission request contract with one Handoff"
    operation, body, request = matches[0]
    assert body.get("required") is True
    return api, operation, request


def _service_handoff_locations(node, path=()):
    """Inspect schema/parameter structure and refs, never descriptive prose."""
    if isinstance(node, list):
        return [location for index, child in enumerate(node)
                for location in _service_handoff_locations(child, (*path, index))]
    if not isinstance(node, dict):
        return []
    properties = node.get("properties", {})
    ref = node.get("$ref", "")
    filename, _, fragment = ref.partition("#")
    target = filename.rsplit("/", 1)[-1] if filename else fragment.rsplit("/", 1)[-1]
    is_handoff = ("handoff_reference" in properties or set(HANDOFF_FIELDS) <= properties.keys()
                  or target in {"handoff-reference.schema.json", "HandoffReference", "handoff_reference"}
                  or (node.get("name") == "handoff_reference" and "in" in node))
    locations = [path] if is_handoff else []
    return locations + [location for key, child in node.items()
                        if key not in {"description", "summary", "example", "examples"} or path[-1:] in {("properties",), ("$defs",), ("schemas",)}
                        for location in _service_handoff_locations(child, (*path, key))]


def _fixture_binding_violations(request, pins):
    """Finite expected-binding oracle, NOT a Core acceptance implementation."""
    ref = request["handoff_reference"]
    comparisons = {
        "handoff-version": (ref["handoff_reference_contract_version"], pins["handoff_reference_contract_version"]),
        "handoff-contract-digest": (ref["handoff_reference_contract_sha256"], pins["handoff_reference_contract_sha256"]),
        "candidate-release-id": (ref["candidate_contract_release_id"], pins["candidate_contract_release_id"]),
        "candidate-release-manifest": (ref["candidate_contract_release_manifest_sha256"], pins["candidate_contract_release_manifest_sha256"]),
        "readback-manifest-digest": (ref["remote_manifest_precondition"]["readback_sha256"], ref["candidate_manifest_sha256"]),
        "expected-candidate-id": (request["expected_candidate_id"], ref["candidate_id"]),
        "expected-candidate-manifest": (request["expected_candidate_manifest_sha256"], ref["candidate_manifest_sha256"]),
        "expected-candidate-release-id": (request["expected_candidate_contract_release_id"], ref["candidate_contract_release_id"]),
    }
    return {label for label, (actual, expected) in comparisons.items() if actual != expected}


def _fixture_replay_digest(binding):
    """JCS comparison of the specified semantic binding, no replay store or dispatch.

    Submission/key equality is checked separately. Timestamp and authentication
    context are not treated as authorization or proof of exact replay.
    """
    request = binding["request"]
    fields = ("operation", "handoff_reference", "expected_candidate_id",
              "expected_candidate_manifest_sha256", "expected_candidate_contract_release_id")
    return _sha(rfc8785.dumps({**{key: request[key] for key in fields}, "policy_revision": binding["policy_revision"]}))


def _replay_pair(case, request=None):
    original = copy.deepcopy(POSITIVE["binding"])
    if request is not None:
        original["request"] = request
    replay = _mutate(original, case["operations"])
    if case["id"] == "conflicting-handoff_reference_contract_version":
        # A synthetic negative must not reserve the future owner's chosen value.
        ref = replay["request"]["handoff_reference"]
        if ref["handoff_reference_contract_version"] == original["request"]["handoff_reference"]["handoff_reference_contract_version"]:
            ref["handoff_reference_contract_version"] += ".unsupported"
    if case.get("reverse_object_order"):
        replay["request"]["handoff_reference"] = dict(reversed(replay["request"]["handoff_reference"].items()))
    return original, replay


def test_t010_fixture_scope_and_owner_field_order():
    for document in (POSITIVE, NEGATIVE):
        assert document["synthetic_only"] is True
        assert document["current_core_release_identity"] == "UNESTABLISHED"
        assert document["runtime_enforcement"] == "NOT RUN"
        assert "http://" not in json.dumps(document) and "https://" not in json.dumps(document)
    request = POSITIVE["binding"]["request"]
    ref = request["handoff_reference"]
    assert tuple(request) == REQUEST_FIELDS
    assert tuple(ref) == HANDOFF_FIELDS
    assert tuple(ref["remote_manifest_precondition"]) == PRECONDITION_FIELDS
    assert POSITIVE["pins"]["handoff_reference_contract_version"] != POSITIVE["pins"]["candidate_content_version"]
    assert not _fixture_binding_violations(request, POSITIVE["pins"])
    raw = POSITIVE["synthetic_bytes"]
    assert ref["handoff_reference_contract_sha256"] == _sha(raw["handoff_contract"].encode())
    assert ref["candidate_contract_release_manifest_sha256"] == _sha(raw["candidate_release_manifest"].encode())
    assert ref["candidate_manifest_sha256"] == _sha(raw["candidate_manifest"].encode())
    assert ref["remote_manifest_precondition"]["readback_size_bytes"] == len(raw["candidate_manifest"].encode())


def test_t010_fixture_matrix_is_complete_and_mutations_are_effective():
    cases = SHAPES + RELATIONS + VERSIONS + REPLAYS
    assert len({case["id"] for case in cases}) == len(cases)
    missing = {case["id"] for case in SHAPES if case["category"] == "required-field"}
    assert missing == ({"missing-" + key for key in HANDOFF_FIELDS}
                       | {"missing-precondition-" + key for key in PRECONDITION_FIELDS}
                       | {"missing-request-" + key for key in REQUEST_FIELDS})
    assert {case["category"] for case in SHAPES} == {
        "required-field", "forbidden-field", "weak-precondition", "stable-identity",
        "malformed-digest", "mutable-selector", "operation",
    }
    request = POSITIVE["binding"]["request"]
    for case in SHAPES:
        original = request if case["target"] == "request" else request["handoff_reference"]
        assert _mutate(original, case["operations"]) != original, case["id"]


def test_t010_strict_reader_and_reused_oracle_fail_closed(tmp_path):
    path = tmp_path / "synthetic.json"
    for raw, message in [('{"a":1,"a":2}', "Duplicate JSON"), ('{"a":NaN}', "Non-JSON")]:
        path.write_text(raw)
        with pytest.raises(AssertionError, match=message):
            _read_json(path)
    schema = {"type": "object", "required": ["size"], "additionalProperties": False,
              "properties": {"size": {"type": "integer", "minimum": 0}}}
    assert _accepts({"size": 1}, schema)
    for value in ({}, {"size": True}, {"size": -1}, {"size": 1, "principal": "synthetic"}):
        assert not _accepts(value, schema)
    with pytest.raises(AssertionError, match="Unsupported oracle"):
        _accepts({}, {"unevaluatedProperties": False})
    with pytest.raises(AssertionError, match="Unsupported contract ref"):
        _expand({"$ref": "unavailable.schema.json"}, {}, CORE_API)


def test_t010_source_oracle_does_not_select_a_version_or_api_path(monkeypatch):
    """Small source-reader check, not an alternative normative contract."""
    assert _candidate_version() == "0.1.0"
    for version_property, expected in (({"const": "0.2.7"}, "0.2.7"), ({"enum": ["0.8.3-preview.2"]}, "0.8.3-preview.2")):
        schema = {"properties": {"handoff_reference_contract_version": version_property}}
        assert _exact_version(schema) == expected
    for route, scheme_name in (("/synthetic-a", "SyntheticAuthA"), ("/synthetic-b", "SyntheticAuthB")):
        api = {"openapi": "3.1.0", "info": {"version": "0.2.7"}, "paths": {route: {"post": {
            "security": [{scheme_name: []}], "requestBody": {"required": True, "content": {
                "application/json": {"schema": {"$ref": "#/components/schemas/SyntheticRequest"}}
            }}
        }}}, "components": {"schemas": {"SyntheticRequest": {"properties": {"handoff_reference": {}}}}}}
        monkeypatch.setattr(__name__ + "._source", lambda path: api)
        observed, operation, body = _admission_contract()
        assert observed is api and operation["security"] == [{scheme_name: []}]
        assert set(body["properties"]) == {"handoff_reference"}


def test_t010_service_boundary_oracle_ignores_prose_but_rejects_handoff_schema():
    description = "This service does not accept handoff_reference; use Core snapshot records."
    assert not _service_handoff_locations({"description": description, "properties": {"snapshot_id": {"type": "string"}}})
    for schema in (
        {"properties": {"handoff_reference": {}}},
        {"properties": {field: {} for field in HANDOFF_FIELDS}},
        {"$ref": "../core-admission/handoff-reference.schema.json"},
        {"$ref": "../core-admission/handoff-reference.schema.json#/$defs/remote_manifest_precondition"},
        {"$ref": "#/components/schemas/HandoffReference"},
        {"properties": {"description": {"properties": {"handoff_reference": {}}}}},
        {"name": "handoff_reference", "in": "query"},
    ):
        api = {"description": description, "paths": {"/synthetic": {"post": {
            "requestBody": {"content": {"application/json": {"schema": schema}}}
        }}}}
        assert _service_handoff_locations(api)


@pytest.mark.parametrize("case", RELATIONS, ids=lambda case: case["id"])
def test_t010_fixture_release_and_digest_relations(case):
    request = copy.deepcopy(POSITIVE["binding"]["request"])
    request["handoff_reference"] = _mutate(request["handoff_reference"], case["operations"])
    assert _fixture_binding_violations(request, POSITIVE["pins"]) == set(case["violations"])


@pytest.mark.parametrize("case", VERSIONS, ids=lambda case: case["id"])
def test_t010_fixture_independent_version(case):
    request = copy.deepcopy(POSITIVE["binding"]["request"])
    request["handoff_reference"]["handoff_reference_contract_version"] = case["value"]
    assert _fixture_binding_violations(request, POSITIVE["pins"]) == {"handoff-version"}


@pytest.mark.parametrize("case", REPLAYS, ids=lambda case: case["id"])
def test_t010_fixture_exact_and_conflicting_replay(case):
    original, replay = _replay_pair(case)
    for key in ("submission_id", "idempotency_key"):
        assert original["request"][key] == replay["request"][key]
    same = _fixture_replay_digest(original) == _fixture_replay_digest(replay)
    assert same == (case["expected"] == "return-or-reconcile-original")
    if case.get("reverse_object_order"):
        assert json.dumps(original) != json.dumps(replay)


@pytest.mark.parametrize("path", NORMATIVE)
def test_t010_normative_sources_exist(path):
    _source(path)


def test_t010_contract_handoff_required_closed_shape():
    schema = _handoff_schema()
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["type"] == "object" and schema["additionalProperties"] is False
    assert set(schema["required"]) == set(schema["properties"]) == set(HANDOFF_FIELDS)
    precondition = schema["properties"]["remote_manifest_precondition"]
    assert precondition["type"] == "object" and precondition["additionalProperties"] is False
    assert set(precondition["required"]) == set(precondition["properties"]) == set(PRECONDITION_FIELDS)
    assert _accepts(_request_for(schema)["handoff_reference"], schema)


@pytest.mark.parametrize("case", SHAPES, ids=lambda case: case["id"])
def test_t010_contract_required_forbidden_and_weak_inputs(case):
    handoff = _handoff_schema()
    request = _request_for(handoff)
    schema = _admission_contract()[2] if case["target"] == "request" else handoff
    baseline = request if case["target"] == "request" else request["handoff_reference"]
    assert _accepts(baseline, schema), "Positive contract input must pass before testing rejection"
    assert not _accepts(_mutate(baseline, case["operations"]), schema), case["id"]


def test_t010_contract_independent_version_source_agreement():
    handoff = _handoff_schema()
    version = _exact_version(handoff)
    api = _openapi(CORE_API)
    # Candidate version is read only for independence; never borrowed as a Core default.
    assert version == api["info"]["version"]
    assert version != _candidate_version()


@pytest.mark.parametrize("case", VERSIONS, ids=lambda case: case["id"])
def test_t010_contract_unsupported_and_coupled_versions(case):
    schema = _handoff_schema()
    ref = _request_for(schema)["handoff_reference"]
    assert _accepts(ref, schema)
    value = case["value"]
    if case["id"] == "coupled-candidate-version":
        value = _candidate_version()
    if value == ref["handoff_reference_contract_version"]:
        # Synthetic examples never reserve a T011 version. Materialize a different
        # exact version for this negative without changing the frozen fixture.
        value = "0.0.0-synthetic.unsupported" if value != "0.0.0-synthetic.unsupported" else "0.0.1-synthetic.unsupported"
    ref["handoff_reference_contract_version"] = value
    assert not _accepts(ref, schema)


@pytest.mark.parametrize("case", RELATIONS, ids=lambda case: case["id"])
def test_t010_contract_shape_valid_release_mismatches(case):
    """Cross-field equality/pin enforcement belongs to Core, not a shape-only schema."""
    schema = _handoff_schema()
    request = _request_for(schema)
    pins = {**POSITIVE["pins"], **{key: request["handoff_reference"][key] for key in (
        "handoff_reference_contract_version", "handoff_reference_contract_sha256")}}
    assert _accepts(request["handoff_reference"], schema)
    request["handoff_reference"] = _mutate(request["handoff_reference"], case["operations"])
    assert _accepts(request["handoff_reference"], schema), "Well-shaped mismatch is a future Core obligation"
    assert _fixture_binding_violations(request, pins) == set(case["violations"])


@pytest.mark.parametrize("case", REPLAYS, ids=lambda case: case["id"])
def test_t010_contract_replay_inputs(case):
    """Exercise source request shape and binding changes, not replay execution."""
    handoff = _handoff_schema()
    _, _, request_schema = _admission_contract()
    original, replay = _replay_pair(case, _request_for(handoff))
    assert _accepts(original["request"], request_schema)
    assert _accepts(replay["request"], request_schema) == (case.get("request_shape", "accept") == "accept")
    same = _fixture_replay_digest(original) == _fixture_replay_digest(replay)
    assert same == (case["expected"] == "return-or-reconcile-original")


def test_t010_contract_implementation_agreement():
    """Actual OpenAPI/Handoff/domain-policy source agreement, not fixture flags.

    Runtime DTO mapping, auth, replay store, dispatch ordering and reconciliation
    remain T015+ obligations even after this static check passes.
    """
    handoff = _handoff_schema()
    api, operation, request_schema = _admission_contract()
    assert set(request_schema["required"]) == set(request_schema["properties"]) == set(REQUEST_FIELDS)
    assert request_schema["type"] == "object" and request_schema["additionalProperties"] is False
    security = operation.get("security", api.get("security"))
    assert isinstance(security, list) and security and all(isinstance(item, dict) and item for item in security), (
        "Admission must require an explicit authentication scheme; no anonymous alternative"
    )
    schemes = api.get("components", {}).get("securitySchemes", {})
    assert all(name in schemes and schemes[name].get("type") for alternative in security for name in alternative)
    policy = ast.parse((ROOT / "src/studious_lamp/domain/policy.py").read_text())
    operation_enum = next(node for node in policy.body if isinstance(node, ast.ClassDef) and node.name == "Operation")
    policy_values = {ast.literal_eval(node.value) for node in operation_enum.body if isinstance(node, ast.Assign)}
    wire_operation = request_schema["properties"]["operation"]
    assert _accepts("admit_candidate", wire_operation) and "admit_candidate" in policy_values
    assert all(not _accepts(value, wire_operation) for value in policy_values - {"admit_candidate"})
    baseline = _request_for(handoff)
    assert _accepts(baseline, request_schema)
    # A copied embedded Handoff must agree behaviorally with the standalone source
    # for every finite positive/negative vector; a direct $ref resolves the same bytes.
    references = [baseline["handoff_reference"]]
    references.extend(_mutate(references[0], case["operations"]) for case in SHAPES if case["target"] == "handoff")
    references.extend(_mutate(references[0], case["operations"]) for case in RELATIONS)
    for ref in references:
        assert _accepts(ref, handoff) == _accepts({**baseline, "handoff_reference": ref}, request_schema)


@pytest.mark.parametrize("path", NORMATIVE[2:])
def test_t010_contract_service_boundaries_have_separate_sources(path):
    api = _openapi(path)
    assert api != _openapi(CORE_API), "A service contract must not be an alias of the Core API"
    assert not _service_handoff_locations(api), "Service effects use Core snapshot/records, not Handoff intake"
