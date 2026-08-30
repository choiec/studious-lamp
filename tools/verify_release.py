#!/usr/bin/env python3
"""Verify local release bindings, not publication, signatures or a SLSA level."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

import rfc8785

import build_candidate_content_release as release


def require(condition: bool, message: str) -> None:
    if not condition:
        raise release.ReleaseError(message)


def canonical_object(raw: bytes) -> dict:
    value = release.parse_json_bytes(raw, label="released JSON")
    require(isinstance(value, dict), "released record is not an object")
    try:
        require(rfc8785.dumps(value) == raw, "released JSON is not canonical JCS")
    except (ValueError, UnicodeError) as exc:
        raise release.ReleaseError("released JSON is outside JCS domain or noncanonical") from exc
    return value


def jsonl_records(raw: bytes) -> list[dict]:
    require(raw.endswith(b"\n") and b"\r" not in raw, "JSONL requires final LF and no CR")
    # Split only ASCII LF, not Unicode line separators inside JSON strings.
    return [canonical_object(line) for line in raw[:-1].split(b"\n")]


def _read_release_files(directory: Path) -> dict[str, bytes]:
    release.check_no_symlinks(directory.absolute())
    require(directory.is_dir(), "missing release directory")
    require({p.name for p in directory.iterdir()} == set(release.OUTPUT_NAMES),
            "release inventory is not exact")
    return {name: release._read_regular(directory / name) for name in release.OUTPUT_NAMES}


def _validate_checksum_file(files: dict[str, bytes]) -> None:
    raw = files["SHA256SUMS"]
    require(raw.endswith(b"\n"), "checksum inventory requires final LF")
    names = sorted(set(release.OUTPUT_NAMES) - {"SHA256SUMS"})
    lines = raw[:-1].split(b"\n")
    require(len(lines) == len(names), "checksum inventory length mismatch")
    for name, line in zip(names, lines, strict=True):
        match = re.fullmatch(rb"([0-9a-f]{64})  ([\x21-\x7e]+)", line)
        require(match is not None, "malformed checksum record")
        digest, recorded_name = match.groups()
        require(recorded_name == name.encode("ascii"), "unsafe/duplicate/unordered checksum name")
        require(digest.decode("ascii") == hashlib.sha256(files[name]).hexdigest(),
                "checksum mismatch")


def check_binding(record: dict, name: str, raw: bytes) -> None:
    require(isinstance(record, dict), "missing byte binding")
    require(record.get("relative_locator") == name, "wrong relative locator")
    require(type(record.get("byte_size")) is int and record["byte_size"] == len(raw),
            "wrong byte size")
    require(record.get("sha256") == hashlib.sha256(raw).hexdigest(), "wrong byte digest")


def check_manifest(manifest: dict, files: dict[str, bytes], source: dict[str, bytes], context: dict) -> None:
    # Deliberately validate the public fields and actual bytes, never regenerate a
    # manifest with the builder. A matching checksum cannot establish these bindings.
    fixed = {
        "manifest_format_version": "1", "release_name": "candidate-content",
        "release_version": "0.1.0", "release_tag": "contract-v0.1.0",
        "schema_dialect": "https://json-schema.org/draft/2020-12/schema",
        "digest_algorithm": "sha256", "compatibility_policy": "pre-1.0-hard-cut",
        "license": "Apache-2.0", "serialization": release.SERIALIZATION,
        "retired_forms": release.RETIRED_FORMS,
    }
    fields = set(fixed) | {"source_revision", "source_git_tree", "source_tree_sha256",
                          "source_inputs", "generation_tool_identity", "license_source",
                          "artifacts", "conformance"}
    require(set(manifest) == fields, "missing/extra manifest fields (or downstream/self binding)")
    for key, value in fixed.items():
        require(manifest[key] == value, f"wrong manifest {key}")
    require(manifest["source_revision"] == context["revision"], "source revision mismatch")
    require(manifest["source_git_tree"] == context["git_tree"], "source Git tree mismatch")
    require(manifest["source_inputs"] == context["inputs"], "source input records mismatch")
    # Recompute the contract framing independently of the builder's digest field.
    framed = bytearray()
    for record in manifest["source_inputs"]:
        path = record["path"]
        release.safe_path(path)
        framed.extend((record["git_mode"] + " " + hashlib.sha256(source[path]).hexdigest()
                       + " " + path + "\n").encode("utf-8"))
    require(manifest["source_tree_sha256"] == hashlib.sha256(framed).hexdigest(),
            "wrong source tree digest/framing")
    tool = manifest["generation_tool_identity"]
    check_binding(tool, release.BUILDER, source[release.BUILDER])
    require(set(tool) == {"relative_locator", "byte_size", "sha256", "canonicalizer"}
            and tool["canonicalizer"] == "rfc8785==0.1.4", "wrong generation tool identity")
    check_binding(manifest["license_source"], "LICENSE", source["LICENSE"])
    require(set(manifest["license_source"]) == {"relative_locator", "byte_size", "sha256"},
            "unexpected license fields")
    artifacts = manifest["artifacts"]
    require(isinstance(artifacts, list) and len(artifacts) == 4, "not exactly four artifacts")
    for name, record in zip(release.SCHEMA_NAMES, artifacts, strict=True):
        check_binding(record, name, files[name])
        require(set(record) == {"contract_name", "contract_version", "relative_locator",
                                "media_type", "byte_size", "sha256"}, "wrong artifact fields")
        require(record["contract_name"] == name.removesuffix(".schema.json")
                and record["contract_version"] == "0.1.0"
                and record["media_type"] == "application/schema+json", "wrong artifact identity")
    conformance = manifest["conformance"]
    check_binding(conformance, release.CONFORMANCE, files[release.CONFORMANCE])
    require(set(conformance) == {"relative_locator", "byte_size", "sha256", "record_count", "scope"}
            and type(conformance["record_count"]) is int and conformance["record_count"] == 2
            and conformance["scope"] == "complete-source-vectors; execution-not-attested",
            "wrong conformance scope")


def check_conformance(raw: bytes, source: dict[str, bytes]) -> None:
    records = jsonl_records(raw)
    require(len(records) == 2, "conformance must contain both complete source documents")
    for record, path in zip(records, release.VECTOR_PATHS, strict=True):
        require(set(record) == {"source_file", "source_sha256", "vectors"}, "wrong vector record fields")
        require(record["source_file"] == path, "wrong vector source path/order")
        require(record["source_sha256"] == hashlib.sha256(source[path]).hexdigest(),
                "wrong raw vector digest")
        original = release.parse_json_bytes(source[path], label=path)
        require(isinstance(original, dict) and original.get("synthetic_only") is True
                and original.get("contract") == "candidate-content", "wrong conformance source")
        # Full canonical value comparison also distinguishes bools from numbers.
        require(rfc8785.dumps(record["vectors"]) == rfc8785.dumps(original),
                "incomplete or changed conformance vectors")


def check_provenance(raw: bytes, files: dict[str, bytes], manifest: dict) -> None:
    records = jsonl_records(raw)
    require(len(records) == 1, "provenance requires one statement")
    statement = records[0]
    require(set(statement) == {"_type", "predicateType", "subject", "predicate"},
            "wrong in-toto statement fields")
    require(statement["_type"] == "https://in-toto.io/Statement/v1"
            and statement["predicateType"] == "https://slsa.dev/provenance/v1", "wrong provenance type")
    subjects = statement["subject"]
    names = sorted((*release.SCHEMA_NAMES, release.MANIFEST, release.CONFORMANCE))
    require(isinstance(subjects, list) and len(subjects) == len(names), "wrong provenance subjects")
    for name, subject in zip(names, subjects, strict=True):
        require(subject == {"name": name, "digest": {"sha256": hashlib.sha256(files[name]).hexdigest()}},
                "provenance subject binding mismatch")
    predicate = statement["predicate"]
    require(isinstance(predicate, dict) and set(predicate) == {"buildDefinition", "runDetails"},
            "wrong SLSA v1 predicate structure or unproved gate claim")
    require(predicate["runDetails"] == {"builder": {"id": "urn:studious-lamp:builder:local-release:v1"}},
            "unexpected builder/run claim")
    definition = predicate["buildDefinition"]
    require(isinstance(definition, dict) and set(definition) == {
        "buildType", "externalParameters", "internalParameters", "resolvedDependencies"
    }, "wrong SLSA v1 build definition")
    require(definition["buildType"] == "urn:studious-lamp:build:candidate-content:v1", "wrong build type")
    require(definition["externalParameters"] == {key: manifest[key] for key in (
        "release_name", "release_version", "release_tag", "source_revision", "source_tree_sha256"
    )}, "provenance source/release mismatch")
    require(definition["internalParameters"] == {"generation_tool_identity": manifest["generation_tool_identity"]},
            "provenance generation tool mismatch")
    dependencies = definition["resolvedDependencies"]
    require(isinstance(dependencies, list) and len(dependencies) == len(manifest["source_inputs"]),
            "incomplete provenance raw sources")
    for dependency, record in zip(dependencies, manifest["source_inputs"], strict=True):
        require(dependency == {"name": record["path"], "digest": {"sha256": record["sha256"]}},
                "provenance raw source binding mismatch")


def verify_release(release_dir: Path, source_root: Path = release.ROOT) -> None:
    files = _read_release_files(release_dir)
    _validate_checksum_file(files)
    source, context = release.source_snapshot(source_root)
    for name in release.SCHEMA_NAMES:
        schema = canonical_object(files[name])
        require(schema.get("$schema") == release.SCHEMA_DIALECT and schema.get("$id") == name
                and not release._schema_has_forbidden_term(schema), "wrong schema identity/form")
        original = release.parse_json_bytes(source[release.CONTRACT_PATH + name], label=name)
        require(files[name] == rfc8785.dumps(original), "schema differs from canonical raw source")
    manifest = canonical_object(files[release.MANIFEST])
    check_manifest(manifest, files, source, context)
    check_conformance(files[release.CONFORMANCE], source)
    check_provenance(files[release.PROVENANCE], files, manifest)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", required=True, type=Path)
    parser.add_argument("--source-root", type=Path, default=release.ROOT)
    args = parser.parse_args()
    try:
        verify_release(args.release, args.source_root)
    except (OSError, release.ReleaseError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print("PASS: byte/source/provenance bindings verified; second-environment/candidate gate NOT RUN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
