"""T005 RED gates for the four-file Candidate-content contract line."""

from __future__ import annotations

import json
from pathlib import Path


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
