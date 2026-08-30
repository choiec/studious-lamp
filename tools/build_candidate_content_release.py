#!/usr/bin/env python3
"""Build the deterministic local Candidate-content 0.1.0 release."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = ROOT / "contracts" / "candidate-content"
VECTOR_DIR = CONTRACT_DIR / "conformance"
RELEASE_DIR = ROOT / "build" / "releases" / "candidate-content" / "0.1.0"

SCHEMA_NAMES = (
    "candidate.schema.json",
    "semantic-content.schema.json",
    "provenance.schema.json",
    "processing-profile.schema.json",
)
SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"
RELEASE_VERSION = "0.1.0"
RELEASE_TAG = "contract-v0.1.0"

MEDIA_TYPES = {
    **{name: "application/schema+json" for name in SCHEMA_NAMES},
    "candidate-content.manifest.json": "application/json",
    "candidate-content.conformance.jsonl": "application/jsonl",
    "candidate-content.provenance.intoto.jsonl": "application/jsonl",
    "SHA256SUMS": "text/plain; charset=utf-8",
}
EVIDENCE_NAMES = (
    "candidate-content.manifest.json",
    "candidate-content.conformance.jsonl",
    "candidate-content.provenance.intoto.jsonl",
    "SHA256SUMS",
)
OUTPUT_NAMES = SCHEMA_NAMES + EVIDENCE_NAMES
NEGATIVE_CASE_IDS = (
    "private-profile",
    "raw-provenance",
    "credential-field",
    "unsafe-backslash-path",
    "missing-payload-path",
    "absolute-payload-path",
    "escaping-payload-path",
    "non-normalized-payload-path",
    "mutable-selector",
    "latest-selector",
    "range-selector",
    "missing-artifact",
    "extra-artifact",
    "duplicate-artifact",
    "fifth-normative-artifact",
    "evidence-as-content",
    "retired-extractor-protocol",
    "retired-extractor-form",
    "wrong-dialect",
    "wrong-version",
    "wrong-size",
    "wrong-digest",
    "malformed-bytes",
)
HEX_DIGEST = re.compile(r"^[0-9a-f]{64}$")
REVISION = re.compile(r"^[0-9a-f]{40,64}$")
FORBIDDEN_SCHEMA_TERMS = (
    "extractor",
    "private_profile",
    "raw_provenance",
    "credential",
    "selector",
    "latest",
    "local_path",
    "sync_path",
    "endpoint",
    "principal",
    "binding",
)


class ReleaseError(ValueError):
    """A fail-closed release input or output error."""


def _reject_constant(value: str) -> None:
    raise ReleaseError(f"non-standard JSON number {value!r}")


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ReleaseError(f"duplicate JSON object key {key!r}")
        result[key] = value
    return result


def parse_json_bytes(raw: bytes, *, label: str) -> Any:
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ReleaseError(f"{label} has a UTF-8 BOM")
    try:
        text = raw.decode("utf-8")
        return json.loads(
            text,
            object_pairs_hook=_unique_pairs,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReleaseError(f"{label} is not strict UTF-8 JSON: {exc}") from exc


def canonical_json_bytes(value: Any) -> bytes:
    try:
        text = json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        )
    except (TypeError, ValueError) as exc:
        raise ReleaseError(f"cannot serialize canonical JSON: {exc}") from exc
    return text.encode("utf-8")


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def named_bytes_digest(files: dict[str, bytes]) -> str:
    digest = hashlib.sha256()
    for name in sorted(files):
        encoded_name = name.encode("utf-8")
        digest.update(len(encoded_name).to_bytes(4, "big"))
        digest.update(encoded_name)
        digest.update(len(files[name]).to_bytes(8, "big"))
        digest.update(files[name])
    return digest.hexdigest()


def _git(*args: str, input_bytes: bytes | None = None) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            input=input_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ReleaseError(f"git command failed: {' '.join(args)}") from exc
    try:
        return result.stdout.decode("utf-8").strip()
    except UnicodeDecodeError as exc:
        raise ReleaseError(f"git command returned non-UTF-8 output: {' '.join(args)}") from exc


def git_file_bytes(revision: str, path: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", "show", f"{revision}:{path}"],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ReleaseError(f"git source file is unavailable: {path}") from exc
    return result.stdout


def git_revision() -> str:
    revision = _git("rev-parse", "HEAD")
    if not REVISION.fullmatch(revision):
        raise ReleaseError("source revision is not a commit digest")
    return revision


def git_tree(revision: str = "HEAD") -> str:
    tree = _git("rev-parse", f"{revision}^{{tree}}")
    if not REVISION.fullmatch(tree):
        raise ReleaseError("source tree is not a tree digest")
    return tree


def _read_regular(path: Path, *, label: str) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ReleaseError(f"{label} is missing or is not a regular file")
    try:
        return path.read_bytes()
    except OSError as exc:
        raise ReleaseError(f"cannot read {label}: {exc}") from exc


def _schema_has_forbidden_term(value: Any) -> bool:
    if isinstance(value, dict):
        return any(
            any(term in str(key).lower() for term in FORBIDDEN_SCHEMA_TERMS)
            or _schema_has_forbidden_term(child)
            for key, child in value.items()
        )
    if isinstance(value, list):
        return any(_schema_has_forbidden_term(child) for child in value)
    return isinstance(value, str) and any(term in value.lower() for term in FORBIDDEN_SCHEMA_TERMS)


def source_files() -> dict[str, bytes]:
    if not CONTRACT_DIR.is_dir() or CONTRACT_DIR.is_symlink():
        raise ReleaseError("Candidate-content contract directory is missing or unsafe")
    actual = tuple(sorted(path.name for path in CONTRACT_DIR.glob("*.schema.json") if path.is_file()))
    if actual != tuple(sorted(SCHEMA_NAMES)):
        raise ReleaseError(f"normative schema inventory is not exact: {actual!r}")

    files: dict[str, bytes] = {}
    for name in SCHEMA_NAMES:
        raw = _read_regular(CONTRACT_DIR / name, label=f"source {name}")
        schema = parse_json_bytes(raw, label=f"source {name}")
        if not isinstance(schema, dict):
            raise ReleaseError(f"source {name} is not a JSON object")
        if schema.get("$schema") != SCHEMA_DIALECT or schema.get("$id") != name:
            raise ReleaseError(f"source {name} has the wrong JSON Schema identity")
        if _schema_has_forbidden_term(schema):
            raise ReleaseError(f"source {name} contains a forbidden public or private form")
        files[name] = raw
    return files


def source_context(files: dict[str, bytes]) -> dict[str, str]:
    revision = git_revision()
    return {
        "revision": revision,
        "tree": git_tree(revision),
        "tree_sha256": named_bytes_digest(files),
    }


def _load_vectors() -> tuple[bytes, dict[str, Any], bytes, dict[str, Any]]:
    positive_raw = _read_regular(VECTOR_DIR / "positive.json", label="positive conformance vector")
    negative_raw = _read_regular(VECTOR_DIR / "negative.json", label="negative conformance vector")
    positive = parse_json_bytes(positive_raw, label="positive conformance vector")
    negative = parse_json_bytes(negative_raw, label="negative conformance vector")
    if not isinstance(positive, dict) or not isinstance(negative, dict):
        raise ReleaseError("conformance vectors must be JSON objects")
    if positive.get("expected") != "accept" or positive.get("normative_schemas") != list(SCHEMA_NAMES):
        raise ReleaseError("positive conformance vector is not the exact four-schema vector")
    if positive.get("synthetic_only") is not True:
        raise ReleaseError("positive conformance vector is not synthetic-only")
    candidate = positive.get("candidate")
    if not isinstance(candidate, dict) or candidate.get("contract") != {
        "version": RELEASE_VERSION,
        "tag": RELEASE_TAG,
        "dialect": SCHEMA_DIALECT,
    }:
        raise ReleaseError("positive conformance vector has the wrong contract identity")
    if negative.get("synthetic_only") is not True or negative.get("contract") != "candidate-content":
        raise ReleaseError("negative conformance vector is not synthetic-only Candidate content")
    cases = negative.get("cases")
    if not isinstance(cases, list) or tuple(case.get("id") for case in cases if isinstance(case, dict)) != NEGATIVE_CASE_IDS:
        raise ReleaseError("negative conformance catalog is incomplete or reordered")
    if any(not isinstance(case, dict) or case.get("expected") != "reject" for case in cases):
        raise ReleaseError("negative conformance catalog contains a non-reject case")
    return positive_raw, positive, negative_raw, negative


def conformance_bytes() -> tuple[bytes, dict[str, str]]:
    positive_raw, positive, negative_raw, negative = _load_vectors()
    records: list[dict[str, Any]] = [
        {
            "case_id": "positive",
            "source_file": "contracts/candidate-content/conformance/positive.json",
            "source_sha256": sha256_bytes(positive_raw),
            **positive,
        }
    ]
    negative_hash = sha256_bytes(negative_raw)
    for case in negative["cases"]:
        records.append(
            {
                "case_id": case["id"],
                "source_file": "contracts/candidate-content/conformance/negative.json",
                "source_sha256": negative_hash,
                **case,
            }
        )
    raw = b"".join(canonical_json_bytes(record) + b"\n" for record in records)
    return raw, {
        "positive_sha256": sha256_bytes(positive_raw),
        "negative_sha256": negative_hash,
        "record_count": str(len(records)),
    }


def provenance_bytes(files: dict[str, bytes], context: dict[str, str]) -> bytes:
    statement = {
        "_type": "https://in-toto.io/Statement/v1",
        "predicateType": "https://slsa.dev/provenance/v1",
        "subject": [
            {"name": name, "digest": {"sha256": sha256_bytes(files[name])}}
            for name in SCHEMA_NAMES
        ],
        "predicate": {
            "buildType": "studious-lamp/candidate-content-release",
            "builder": {"id": "studious-lamp/release-builder"},
            "license": "Apache-2.0",
            "release": {"version": RELEASE_VERSION, "tag": RELEASE_TAG},
            "source": {
                "revision": context["revision"],
                "tree": context["tree"],
                "tree_sha256": context["tree_sha256"],
            },
            "reproducible": True,
        },
    }
    return canonical_json_bytes(statement) + b"\n"


def _license_record() -> dict[str, Any]:
    tracked = _git("ls-files", "--error-unmatch", "LICENSE") == "LICENSE"
    if not tracked:
        raise ReleaseError("LICENSE is not tracked")
    raw = _read_regular(ROOT / "LICENSE", label="LICENSE")
    if b"Apache License" not in raw or b"Version 2.0" not in raw:
        raise ReleaseError("tracked LICENSE is not Apache-2.0")
    return {"file": "LICENSE", "spdx": "Apache-2.0", "sha256": sha256_bytes(raw)}


def artifact_records(files: dict[str, bytes]) -> list[dict[str, Any]]:
    return [
        {
            "name": name,
            "contract_version": RELEASE_VERSION,
            "media_type": MEDIA_TYPES[name],
            "size": len(files[name]),
            "sha256": sha256_bytes(files[name]),
        }
        for name in SCHEMA_NAMES
    ]


def manifest_bytes(
    files: dict[str, bytes],
    context: dict[str, str],
    conformance: bytes,
    conformance_identity: dict[str, str],
    provenance: bytes,
) -> bytes:
    manifest = {
        "contract": "candidate-content",
        "version": RELEASE_VERSION,
        "tag": RELEASE_TAG,
        "schema_dialect": SCHEMA_DIALECT,
        "serialization": {
            "json": "RFC 8785 JCS; UTF-8; no BOM; no trailing newline",
            "jsonl": "one RFC 8785 JCS object per line plus LF",
            "checksums": "lowercase SHA-256, two spaces, unsigned UTF-8 filename order, LF",
        },
        "source": {
            "revision": context["revision"],
            "tree": context["tree"],
            "tree_sha256": context["tree_sha256"],
            "schemas": list(SCHEMA_NAMES),
            "conformance_inputs": [
                {
                    "name": "contracts/candidate-content/conformance/positive.json",
                    "sha256": conformance_identity["positive_sha256"],
                },
                {
                    "name": "contracts/candidate-content/conformance/negative.json",
                    "sha256": conformance_identity["negative_sha256"],
                },
            ],
        },
        "generation_tool": "tools/build_candidate_content_release.py",
        "compatibility_policy": "pre-1.0-hard-cut",
        "license": _license_record(),
        "artifacts": artifact_records(files),
        "evidence": [
            {
                "name": "candidate-content.manifest.json",
                "classification": "release-control-evidence",
            },
            {
                "name": "candidate-content.conformance.jsonl",
                "classification": "conformance-evidence",
                "media_type": MEDIA_TYPES["candidate-content.conformance.jsonl"],
                "size": len(conformance),
                "sha256": sha256_bytes(conformance),
            },
            {
                "name": "candidate-content.provenance.intoto.jsonl",
                "classification": "provenance-evidence",
                "media_type": MEDIA_TYPES["candidate-content.provenance.intoto.jsonl"],
                "size": len(provenance),
                "sha256": sha256_bytes(provenance),
            },
            {"name": "SHA256SUMS", "classification": "integrity-evidence"},
        ],
        "conformance": {
            "output": "candidate-content.conformance.jsonl",
            "positive_sha256": conformance_identity["positive_sha256"],
            "negative_sha256": conformance_identity["negative_sha256"],
            "record_count": int(conformance_identity["record_count"]),
        },
        "retired_forms": [
            "retired-extractor-protocol",
            "retired-extractor-form",
            "mutable-selector",
            "range-selector",
        ],
        "classification": {
            "normative_artifacts": "exactly-four-content-schemas",
            "evidence": "not-normative-content",
        },
    }
    return canonical_json_bytes(manifest)


def checksum_bytes(files: dict[str, bytes]) -> bytes:
    names = sorted(files)
    return b"".join(
        f"{sha256_bytes(files[name])}  {name}\n".encode("utf-8") for name in names
    )


def expected_release_files(
    source: dict[str, bytes], context: dict[str, str]
) -> dict[str, bytes]:
    conformance, identity = conformance_bytes()
    provenance = provenance_bytes(source, context)
    manifest = manifest_bytes(source, context, conformance, identity, provenance)
    files = {
        **source,
        "candidate-content.manifest.json": manifest,
        "candidate-content.conformance.jsonl": conformance,
        "candidate-content.provenance.intoto.jsonl": provenance,
    }
    files["SHA256SUMS"] = checksum_bytes(files)
    return files


def _check_output_directory() -> None:
    if RELEASE_DIR.exists() and (RELEASE_DIR.is_symlink() or not RELEASE_DIR.is_dir()):
        raise ReleaseError("release directory is unsafe")
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    for child in RELEASE_DIR.iterdir():
        if child.name not in OUTPUT_NAMES:
            raise ReleaseError(f"release directory contains an extra artifact: {child.name!r}")
        if child.is_symlink() or not child.is_file():
            raise ReleaseError(f"release artifact is not a regular file: {child.name!r}")


def build_release() -> dict[str, bytes]:
    source = source_files()
    context = source_context(source)
    files = expected_release_files(source, context)
    if tuple(files) != OUTPUT_NAMES:
        raise ReleaseError("builder output inventory is not exact")
    _check_output_directory()
    for name in OUTPUT_NAMES:
        (RELEASE_DIR / name).write_bytes(files[name])
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    try:
        build_release()
    except ReleaseError as exc:
        parser.error(str(exc))
    print("PASS: built exact Candidate-content 0.1.0 local release")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
