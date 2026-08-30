"""Historical contract gates and T042 semantic-content RED, never runtime validation."""

from __future__ import annotations

import copy
import hashlib
import json
import math
import re
import unicodedata
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_DIR = ROOT / "contracts" / "candidate-content"
VECTOR_DIR = CONTRACT_DIR / "conformance"
SCHEMA_NAMES = (
    "candidate.schema.json",
    "semantic-content.schema.json",
    "provenance.schema.json",
    "processing-profile.schema.json",
)
SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"


def _read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _require_t006_schemas() -> dict[str, dict[str, object]]:
    expected = {CONTRACT_DIR / name for name in SCHEMA_NAMES}
    missing = sorted(path.relative_to(ROOT).as_posix() for path in expected if not path.is_file())
    assert not missing, (
        "T006 RED (expected): normative Candidate-content schemas are not implemented yet: "
        + ", ".join(missing)
    )

    actual = {
        path
        for path in CONTRACT_DIR.glob("*.schema.json")
        if path.is_file()
    }
    extras = sorted(path.relative_to(ROOT).as_posix() for path in actual - expected)
    assert not extras, "T006 RED: Candidate-content has extra normative schemas: " + ", ".join(extras)
    return {name: _read_json(CONTRACT_DIR / name) for name in SCHEMA_NAMES}


def _vectors(name: str) -> dict[str, object]:
    value = _read_json(VECTOR_DIR / name)
    assert isinstance(value, dict)
    return value


def test_candidate_content_has_exactly_four_normative_schemas() -> None:
    assert tuple(_require_t006_schemas()) == SCHEMA_NAMES


def test_candidate_content_schemas_use_json_schema_2020_12() -> None:
    schemas = _require_t006_schemas()
    assert all(schema.get("$schema") == SCHEMA_DIALECT for schema in schemas.values())


def test_positive_vector_describes_one_complete_exact_four_candidate() -> None:
    _require_t006_schemas()
    positive = _vectors("positive.json")
    assert positive["expected"] == "accept"
    assert positive["normative_schemas"] == list(SCHEMA_NAMES)
    assert positive["candidate"]["candidate_id"] == "candidate-synthetic-001"
    assert positive["candidate"]["contract"]["version"] == "0.1.0"
    assert positive["candidate"]["contract"]["tag"] == "contract-v0.1.0"


def test_disclosure_vectors_reject_private_and_raw_values() -> None:
    _require_t006_schemas()
    negative = _vectors("negative.json")
    cases = {case["id"]: case for case in negative["cases"]}
    for case_id in ("private-profile", "raw-provenance", "credential-field"):
        assert cases[case_id]["expected"] == "reject"


def test_path_vectors_reject_unsafe_missing_absolute_escaping_and_non_normalized_paths() -> None:
    _require_t006_schemas()
    cases = {case["id"]: case for case in _vectors("negative.json")["cases"]}
    for case_id in (
        "unsafe-backslash-path",
        "missing-payload-path",
        "absolute-payload-path",
        "escaping-payload-path",
        "non-normalized-payload-path",
    ):
        assert cases[case_id]["expected"] == "reject"


def test_selector_vectors_reject_mutable_latest_and_range_selectors() -> None:
    _require_t006_schemas()
    cases = {case["id"]: case for case in _vectors("negative.json")["cases"]}
    for case_id in ("mutable-selector", "latest-selector", "range-selector"):
        assert cases[case_id]["expected"] == "reject"


def test_artifact_vectors_reject_missing_extra_duplicate_and_fifth_artifacts() -> None:
    _require_t006_schemas()
    cases = {case["id"]: case for case in _vectors("negative.json")["cases"]}
    for case_id in (
        "missing-artifact",
        "extra-artifact",
        "duplicate-artifact",
        "fifth-normative-artifact",
    ):
        assert cases[case_id]["expected"] == "reject"


def test_evidence_is_rejected_as_a_normative_content_artifact() -> None:
    _require_t006_schemas()
    cases = {case["id"]: case for case in _vectors("negative.json")["cases"]}
    assert cases["evidence-as-content"]["expected"] == "reject"


def test_retired_extractor_protocol_forms_are_rejected() -> None:
    _require_t006_schemas()
    cases = {case["id"]: case for case in _vectors("negative.json")["cases"]}
    for case_id in ("retired-extractor-protocol", "retired-extractor-form"):
        assert cases[case_id]["expected"] == "reject"


def test_conformance_catalog_is_synthetic_and_has_no_network_or_private_values() -> None:
    positive = _vectors("positive.json")
    negative = _vectors("negative.json")
    assert positive["synthetic_only"] is True
    assert negative["synthetic_only"] is True
    serialized = json.dumps((positive, negative), sort_keys=True).replace(SCHEMA_DIALECT, "")
    for forbidden in ("http://", "https://", "DATA_ROOT", "ownCloud", "password", "secret"):
        assert forbidden not in serialized


INTERACTION_FIELDS = {
    "choice": {"response_id", "options"},
    "reference_choice": {"response_id", "reference_refs", "options"},
    "inline_mark_choice": {"response_id", "mark_refs"},
    "sentence_mark_choice": {"response_id", "sentence_refs"},
    "blank_choice": {"response_id", "blank_ref", "options"},
    "order_choice": {"response_id", "unit_refs", "order_options"},
    "position_choice": {"response_id", "given_part_ref", "slots"},
    "summary_pair_choice": {"response_id", "summary_part_ref", "gaps", "pair_options"},
    "inline_choice_set": {"gaps"},
    "token_order": {"response_id", "tokens", "allow_reuse"},
    "text_entry": {"entries"},
    "edit_response": {"response_id", "editable_part_ref", "edit_targets", "allowed_operations"},
}
SEMANTIC = _vectors("positive.json")["candidate"]["semantic_content"]
SEMANTIC_CASES = _vectors("negative.json")["semantic_content_cases"]


def _at(document, path):
    for key in path:
        document = document[key]
    return document


def _mutate(document, operations):
    """Apply typed-path fixture edits, not a production patch protocol."""
    document = copy.deepcopy(document)
    for operation in operations:
        path, op = operation["path"], operation["op"]
        if not path:
            assert op == "replace"
            document = copy.deepcopy(operation["value"])
            continue
        parent, key = _at(document, path[:-1]), path[-1]
        if op == "remove":
            del parent[key]
        else:
            assert op in {"add", "replace", "copy"}
            value = copy.deepcopy(_at(document, operation["from"]) if op == "copy" else operation["value"])
            if isinstance(parent, list) and op in {"add", "copy"}:
                parent.insert(key, value)
            else:
                if op == "replace":
                    assert key in parent if isinstance(parent, dict) else 0 <= key < len(parent)
                else:
                    assert key not in parent
                parent[key] = value
    return document


def _objects(value, path=()):
    if isinstance(value, dict):
        yield path, value
        for key, child in value.items():
            yield from _objects(child, (*path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _objects(child, (*path, index))


def _same_json(left, right):
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is type(right) and left == right
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(_same_json(left[k], right[k]) for k in left)
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(_same_json(a, b) for a, b in zip(left, right))
    return left == right


def _accepts(value, schema, root=None):
    """Test-only supported subset; unknown assertions error, no network or runtime refs.

    Not a general Draft 2020-12 implementation. format is annotation-only. T043
    may use this evaluated subset, not silently introduce unsupported keywords.
    """
    if isinstance(schema, bool):
        return schema
    root = schema if root is None else root
    supported = {
        "$schema", "$id", "$ref", "$defs", "$comment", "title", "description", "format",
        "type", "properties", "required", "additionalProperties", "items", "minItems",
        "maxItems", "uniqueItems", "enum", "const", "oneOf", "anyOf", "allOf", "not",
        "minLength", "maxLength", "pattern", "minimum", "maximum",
    }
    assert not set(schema) - supported, f"Unsupported oracle keywords: {set(schema) - supported}"
    if "$ref" in schema:
        ref = schema["$ref"]
        if ref.startswith("#/$defs/"):
            target, target_root = root["$defs"][ref.removeprefix("#/$defs/")], root
        else:
            assert ref in SCHEMA_NAMES, f"Nonlocal or unsupported schema ref: {ref}"
            target = target_root = _read_json(CONTRACT_DIR / ref)
        if not _accepts(value, target, target_root):
            return False
    kinds = {
        "object": isinstance(value, dict), "array": isinstance(value, list),
        "string": isinstance(value, str), "boolean": isinstance(value, bool),
        "integer": type(value) in (int, float) and math.isfinite(value) and value == int(value),
        "number": type(value) in (int, float) and math.isfinite(value), "null": value is None,
    }
    if "type" in schema:
        assert isinstance(schema["type"], str) and schema["type"] in kinds, "Unsupported type union"
        if not kinds[schema["type"]]:
            return False
    if "const" in schema and not _same_json(value, schema["const"]):
        return False
    if "enum" in schema and not any(_same_json(value, candidate) for candidate in schema["enum"]):
        return False
    for keyword in ("oneOf", "anyOf", "allOf"):
        if keyword in schema:
            results = [_accepts(value, branch, root) for branch in schema[keyword]]
            if not {"oneOf": sum(results) == 1, "anyOf": any(results), "allOf": all(results)}[keyword]:
                return False
    if "not" in schema and _accepts(value, schema["not"], root):
        return False
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        if not set(schema.get("required", ())) <= value.keys():
            return False
        if schema.get("additionalProperties") is False and value.keys() - properties.keys():
            return False
        assert isinstance(schema.get("additionalProperties", True), bool), "Unsupported map schema"
        if any(not _accepts(child, properties[key], root) for key, child in value.items() if key in properties):
            return False
    if isinstance(value, list):
        if not schema.get("minItems", 0) <= len(value) <= schema.get("maxItems", math.inf):
            return False
        # ponytail: quadratic equality is bounded to small synthetic arrays, not runtime input.
        if schema.get("uniqueItems") and any(_same_json(v, other) for i, v in enumerate(value) for other in value[:i]):
            return False
        if "items" in schema and any(not _accepts(child, schema["items"], root) for child in value):
            return False
    if isinstance(value, str):
        if not schema.get("minLength", 0) <= len(value) <= schema.get("maxLength", math.inf):
            return False
        if "pattern" in schema and not re.search(schema["pattern"], value):
            return False
    if type(value) in (int, float):
        if not math.isfinite(value) or not schema.get("minimum", -math.inf) <= value <= schema.get("maximum", math.inf):
            return False
    return True


def _hard_cut_schema():
    schema = _require_t006_schemas()["semantic-content.schema.json"]
    assert _accepts(SEMANTIC, schema), "T042 RED: unchanged semantic-content schema rejects the hard-cut positive baseline"
    return schema


def test_t042_oracle_self_check():
    schema = {"type": "object", "required": ["mode", "values"], "additionalProperties": False,
              "properties": {"mode": {"enum": ["sample"]}, "values": {"type": "array", "minItems": 1,
                  "items": {"$ref": "#/$defs/bounded"}}},
              "$defs": {"bounded": {"type": "integer", "minimum": 0, "maximum": 2}}}
    assert _accepts({"mode": "sample", "values": [1]}, schema)
    for value in ({}, {"mode": "other", "values": [1]}, {"mode": "sample", "values": []},
                  {"mode": "sample", "values": [True]}, {"mode": "sample", "values": [3]},
                  {"mode": "sample", "values": [1], "extra": 0}):
        assert not _accepts(value, schema)
    assert _accepts("aa", {"type": "string", "pattern": "^a+$", "minLength": 2, "maxLength": 3})
    assert not _accepts("a", {"minLength": 2})
    assert not _accepts("bbb", {"pattern": "^a+$"})
    assert not _accepts(1, {"oneOf": [{"type": "integer"}, {"type": "number"}]})
    assert _accepts("a", {"oneOf": [{"const": "a"}, {"const": "b"}]})
    assert not _accepts(float("nan"), {"type": "number"})
    assert not _accepts([1, 1], {"uniqueItems": True})
    assert not _accepts([1, 1.0], {"uniqueItems": True})
    assert _accepts([True, 1], {"uniqueItems": True})
    assert _accepts(1.0, {"type": "integer"})
    assert not _accepts(True, {"enum": [1]})
    assert not _accepts(True, {"const": 1})
    assert not _accepts([1, 2], {"maxItems": 1})
    assert _accepts(1, {"allOf": [{"minimum": 0}, {"maximum": 1}]})
    assert not _accepts(2, {"allOf": [{"minimum": 0}, {"maximum": 1}]})
    assert _accepts("a", {"anyOf": [{"const": "a"}, {"const": "b"}]})
    assert not _accepts("c", {"anyOf": [{"const": "a"}, {"const": "b"}]})
    assert not _accepts("a", {"not": {"const": "a"}})
    with pytest.raises(AssertionError, match="Unsupported oracle"):
        _accepts({}, {"unevaluatedProperties": False})
    with pytest.raises(AssertionError, match="Nonlocal"):
        _accepts({}, {"$ref": "unavailable.schema.json"})


def test_t042_catalog_integrity():
    assert set(SEMANTIC) == {"schema", "resources", "items"}
    assert len(SEMANTIC["resources"]) == 1
    assert [item["interaction"]["type"] for item in SEMANTIC["items"]] == list(INTERACTION_FIELDS)
    assert len({case["id"] for case in SEMANTIC_CASES}) == len(SEMANTIC_CASES)
    for case in SEMANTIC_CASES:
        assert case["owner"] in {"schema", "core"}
        assert case["schema_expected"] == ("reject" if case["owner"] == "schema" else "accept")
        if case["owner"] == "core":
            assert case["runtime_expected"] == "reject"
        assert _mutate(SEMANTIC, case["operations"]) != SEMANTIC, case["id"]
    for item in SEMANTIC["items"]:
        interaction = item["interaction"]
        assert set(interaction) == {"type"} | INTERACTION_FIELDS[interaction["type"]]
        for part in item["content_parts"]:
            assert set(part) == {"part_id", "role", "content", "analysis_target"}
            assert "educational_measurements" not in part
            english = part["content"].get("language", "en") == "en"
            assert part["analysis_target"] == {"egp": english, "evp": english}
    for example in _vectors("positive.json")["text_entry_normalization_examples"]:
        normalized = unicodedata.normalize("NFC", example["input"].replace("\r\n", "\n").replace("\r", "\n"))
        assert normalized == example["normalized"]


def test_t042_finite_fixture_original_text_and_answers():
    """Audit this fixed synthetic example, not arbitrary Candidate runtime integrity."""
    resource = SEMANTIC["resources"][0]
    segments = resource["content_blocks"][0]["segments"]
    assert [s["text"] for s in segments] == ["Alpha beta.", "Gamma delta.", "Aé😀e\u0301Z"]
    assert len(segments[2]["text"]) == 6 and segments[2]["text"][2:3] == "😀"
    assert len(segments[2]["text"].encode("utf-8")) == 11
    assert resource["provenance_refs"] == [_vectors("positive.json")["candidate"]["provenance"]["value"]]
    for item in SEMANTIC["items"]:
        parts = {p["part_id"]: p for p in item["content_parts"]}
        assert len(parts) == len(item["content_parts"])
        assert item["resource_refs"] == [{"resource_id": resource["resource_id"], "usage": "stimulus"}]
        for part in parts.values():
            if part["content"]["kind"] == "resource_segments":
                assert part["content"]["resource_id"] == resource["resource_id"]
                assert set(part["content"]["segment_ids"]) <= {s["segment_id"] for s in segments}
        for overlay in item["overlays"]:
            target = overlay["target"]
            if "resource_id" in target:
                assert target["resource_id"] == resource["resource_id"]
                original = next(s["text"] for s in segments if s["segment_id"] == target["segment_id"])
            else:
                assert parts[target["part_id"]]["content"]["kind"] == "inline_text"
                original = parts[target["part_id"]]["content"]["text"]
            assert target["text_sha256"] == hashlib.sha256(original.encode("utf-8")).hexdigest()
            assert 0 <= target["start"] <= target["end"] <= len(original)
            assert (target["start"] == target["end"]) == (overlay["operation"] == "insert_slot")
        interaction = item["interaction"]
        rows = interaction.get("entries", interaction.get("gaps", [interaction]))
        response_ids = [row["response_id"] for row in rows if "response_id" in row]
        if "response_id" in interaction:
            response_ids = [interaction["response_id"]]
        assert response_ids == [d["response_id"] for d in item["response_declarations"]]
        overlays = {o["overlay_id"]: o for o in item["overlays"]}
        options = interaction.get("options", []) + [o for gap in interaction.get("gaps", []) for o in gap.get("options", [])]
        for option in options:
            assert option["part_ref"] in parts
        for ref in interaction.get("reference_refs", []) + interaction.get("sentence_refs", []):
            assert ref["resource_id"] == resource["resource_id"]
            assert ref["segment_id"] in {s["segment_id"] for s in segments}
        for row in interaction.get("gaps", []) + interaction.get("entries", []) + interaction.get("slots", []) + interaction.get("edit_targets", []):
            assert row["target_ref"] in overlays
        for field in ("given_part_ref", "summary_part_ref", "editable_part_ref"):
            if field in interaction:
                assert interaction[field] in parts
        answer_domains = {
            "choice": {o["option_id"] for o in options},
            "reference_choice": {o["option_id"] for o in options},
            "blank_choice": {o["option_id"] for o in options},
            "inline_mark_choice": set(interaction.get("mark_refs", [])),
            "sentence_mark_choice": {o["option_id"] for o in interaction.get("sentence_refs", [])},
            "order_choice": {o["option_id"] for o in interaction.get("order_options", [])},
            "position_choice": {s["slot_id"] for s in interaction.get("slots", [])},
            "summary_pair_choice": {p["option_id"] for p in interaction.get("pair_options", [])},
        }
        kind = interaction["type"]
        if kind in answer_domains:
            assert item["response_declarations"][0]["correct_response"] in answer_domains[kind]
        if kind == "inline_choice_set":
            for gap, declaration in zip(interaction["gaps"], item["response_declarations"], strict=True):
                assert declaration["correct_response"] in {o["option_id"] for o in gap["options"]}
        if kind == "token_order":
            assert item["response_declarations"][0]["correct_response"] == [t["token_id"] for t in interaction["tokens"]]
        if kind == "edit_response":
            assert item["response_declarations"][0]["correct_response"]["edits"][0]["target_id"] == interaction["edit_targets"][0]["target_id"]
    entry = SEMANTIC["items"][10]
    assert entry["interaction"]["entries"][0]["expected_length"] == len(entry["response_declarations"][0]["correct_response"])


def test_t042_schema_definition_inventory():
    schema = _require_t006_schemas()["semantic-content.schema.json"]
    assert set(schema.get("required", [])) == {"schema", "resources", "items"}, "T042 RED: old schema/value root"
    assert {"resource", "item", "content_part", "response_declaration", "interaction"} <= schema.get("$defs", {}).keys()
    branches = schema["$defs"]["interaction"]["oneOf"]
    assert len(branches) == 12
    types = []
    for branch in branches:
        if "$ref" in branch:
            branch = schema["$defs"][branch["$ref"].removeprefix("#/$defs/")]
        discriminator = branch["properties"]["type"]
        types.append(discriminator.get("const", discriminator.get("enum", [None])[0]))
        assert "type" in branch["required"]
    assert set(types) == set(INTERACTION_FIELDS)
    for path, node in _objects(schema):
        if node.get("type") == "object":
            assert node.get("additionalProperties") is False, path


@pytest.mark.parametrize("item", SEMANTIC["items"], ids=lambda item: item["interaction"]["type"])
def test_t042_schema_positive(item):
    document = {**SEMANTIC, "items": [item]}
    schema = _require_t006_schemas()["semantic-content.schema.json"]
    assert _accepts(document, schema), f"T042 RED: missing hard-cut shape for {item['interaction']['type']}"


@pytest.mark.parametrize("case", [c for c in SEMANTIC_CASES if c["owner"] == "schema"], ids=lambda c: c["id"])
def test_t042_schema_negative(case):
    schema = _hard_cut_schema()  # A schema rejecting everything cannot pass the negative oracle.
    assert not _accepts(_mutate(SEMANTIC, case["operations"]), schema), case["id"]


@pytest.mark.parametrize("case", [c for c in SEMANTIC_CASES if c["owner"] == "core"], ids=lambda c: c["id"])
def test_t042_schema_runtime_case_local_shape_only(case):
    schema = _hard_cut_schema()
    assert _accepts(_mutate(SEMANTIC, case["operations"]), schema), case["id"]
    # The expected Core rejection is a frozen obligation, NOT a runtime test result.


def test_t042_schema_all_objects_closed():
    schema = _hard_cut_schema()
    for path, _ in _objects(SEMANTIC):
        for key in ("unsupported_field", "educational_measurements"):
            invalid = _mutate(SEMANTIC, [{"op": "add", "path": [*path, key], "value": "synthetic"}])
            assert not _accepts(invalid, schema), (path, key)


def test_t042_schema_common_fields_required():
    schema = _hard_cut_schema()
    optional_containers = {"standard_metadata", "ieee_lom", "educational", "oneedtech_common_cartridge"}
    for path, node in _objects(SEMANTIC):
        if path and path[-1] in optional_containers:
            continue
        for field in node:
            if field == "source_anchor" or (path and path[-1] == "language_profile" and field == "cefr"):
                continue
            invalid = _mutate(SEMANTIC, [{"op": "remove", "path": [*path, field]}])
            assert not _accepts(invalid, schema), (path, field)


def test_t042_schema_required_collections_nonempty():
    schema = _hard_cut_schema()
    paths = [("resources", 0, "provenance_refs")]
    for index, item in enumerate(SEMANTIC["items"]):
        paths.extend(("items", index, field) for field in ("content_parts", "response_declarations", "provenance_refs"))
        interaction = item["interaction"]
        paths.extend(("items", index, "interaction", key) for key, value in interaction.items() if isinstance(value, list))
        for gap_index, gap in enumerate(interaction.get("gaps", [])):
            if "options" in gap:
                paths.append(("items", index, "interaction", "gaps", gap_index, "options"))
        for pair_index, _ in enumerate(interaction.get("pair_options", [])):
            paths.append(("items", index, "interaction", "pair_options", pair_index, "values"))
    for path in paths:
        invalid = _mutate(SEMANTIC, [{"op": "replace", "path": list(path), "value": []}])
        assert not _accepts(invalid, schema), path


def test_t042_schema_metadata_and_subject_variants():
    schema = _hard_cut_schema()
    for difficulty in ("very easy", "easy", "medium", "difficult", "very difficult"):
        value = copy.deepcopy(SEMANTIC)
        for owner in (value["resources"][0], value["items"][0]):
            owner["standard_metadata"]["ieee_lom"]["educational"]["difficulty"]["value"] = difficulty
        assert _accepts(value, schema), difficulty
    for kind in ("passage", "shared_stimulus", "table", "chart", "notice", "image", "audio", "mixed"):
        value = copy.deepcopy(SEMANTIC)
        value["resources"][0]["resource_type"] = kind
        value["items"][0]["task"]["taxonomy_id"] = "synthetic-mathematics-v1"
        measurement = value["resources"][0]["standard_metadata"]["oneedtech_common_cartridge"]["textComplexity"][0]
        measurement.update(scale="synthetic-other-scale", score=2.5, unit="synthetic-unit")
        assert _accepts(value, schema), kind
    value = copy.deepcopy(SEMANTIC)
    value["resources"][0]["standard_metadata"] = {}
    value["resources"][0]["content_blocks"][0]["segments"][0].pop("source_anchor")
    value["resources"][0]["extensions"]["automatic_disco"]["language_profile"].pop("cefr")
    assert _accepts(value, schema)
    assert _accepts({"schema": "semantic-content.schema.json", "resources": [], "items": []}, schema)
