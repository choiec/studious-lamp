#!/usr/bin/env python3
"""Build Candidate-content bytes; T009 separately establishes the candidate gate."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import re
import stat
import subprocess
import tomllib
from pathlib import Path
from typing import Any

import rfc8785

ROOT = Path(__file__).resolve().parents[1]
RELEASE_DIR = ROOT / "build/releases/candidate-content/0.1.0"
SCHEMA_NAMES = (
    "candidate.schema.json",
    "semantic-content.schema.json",
    "provenance.schema.json",
    "processing-profile.schema.json",
)
MANIFEST = "candidate-content.manifest.json"
CONFORMANCE = "candidate-content.conformance.jsonl"
PROVENANCE = "candidate-content.provenance.intoto.jsonl"
OUTPUT_NAMES = (*SCHEMA_NAMES, MANIFEST, CONFORMANCE, PROVENANCE, "SHA256SUMS")
CONTRACT_PATH = "contracts/candidate-content/"
VECTOR_PATHS = tuple(CONTRACT_PATH + "conformance/" + n for n in ("positive.json", "negative.json"))
BUILDER = "tools/build_candidate_content_release.py"
VERIFIER = "tools/verify_release.py"
# Generation inputs only; frozen tests are validation inputs, never release inputs.
SOURCE_PATHS = tuple(sorted((
    ".python-version", "LICENSE", "pyproject.toml", "uv.lock", BUILDER, VERIFIER,
    *(CONTRACT_PATH + name for name in SCHEMA_NAMES), *VECTOR_PATHS,
), key=lambda p: p.encode("utf-8")))
SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"
RELEASE_VERSION = "0.1.0"
RELEASE_TAG = "contract-v0.1.0"
SERIALIZATION = {
    "json": "RFC 8785 JCS; UTF-8; no BOM; no trailing newline",
    "jsonl": "one RFC 8785 JCS object per line plus LF",
    "checksums": "lowercase SHA-256, two spaces, unsigned UTF-8 filename order, LF",
}
RETIRED_FORMS = ["retired-extractor-protocol", "retired-extractor-form", "mutable-selector", "range-selector"]
LICENSE_SHA256 = "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"
REVISION = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")
FORBIDDEN_SCHEMA_TERMS = (
    "extractor", "private_profile", "raw_provenance", "credential", "selector",
    "latest", "local_path", "sync_path", "endpoint", "principal", "binding",
)


class ReleaseError(ValueError):
    """A fail-closed release input or output error."""


def _reject_constant(value: str) -> None:
    raise ReleaseError(f"non-standard JSON number {value!r}")


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ReleaseError(f"duplicate JSON object key {key!r}")
        result[key] = value
    return result


def parse_json_bytes(raw: bytes, *, label: str) -> Any:
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ReleaseError(f"{label} has a UTF-8 BOM")
    try:
        # JCS uses binary64 numbers. Keep small integers exact for sizes/counts,
        # but accept canonical integer spellings emitted from large JSON floats.
        return json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_pairs,
                          parse_constant=_reject_constant,
                          parse_int=lambda s: int(s) if abs(int(s)) < 2**53 else float(s))
    except (UnicodeDecodeError, ValueError) as exc:
        raise ReleaseError(f"{label} is not strict UTF-8 JSON") from exc


def canonical_json_bytes(value: Any) -> bytes:
    try:
        return rfc8785.dumps(value)
    except (ValueError, UnicodeError) as exc:
        raise ReleaseError("value is outside the supported JCS domain") from exc


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _git(root: Path, *args: str) -> bytes:
    try:
        return subprocess.run(["git", *args], cwd=root, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ReleaseError("cannot resolve exact Git source") from exc


def safe_path(path: str) -> None:
    if (not path or "\\" in path or any(c in path for c in "\x00\r\n")
            or any(part in ("", ".", "..") for part in path.split("/"))):
        raise ReleaseError(f"unsafe source path: {path!r}")
    try:
        path.encode("utf-8")
    except UnicodeError as exc:
        raise ReleaseError("source path is not UTF-8") from exc


def check_no_symlinks(path: Path) -> None:
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ReleaseError("symlink in source/output path")


def _read_regular(path: Path) -> bytes:
    check_no_symlinks(path)
    if not path.is_file():
        raise ReleaseError(f"missing or non-regular file: {path.name!r}")
    return path.read_bytes()


def source_snapshot(root: Path) -> tuple[dict[str, bytes], dict[str, Any]]:
    """Authenticate raw inputs against HEAD and index, without trusting status caches."""
    root = root.absolute()
    check_no_symlinks(root)
    revision = _git(root, "rev-parse", "HEAD").decode("ascii").strip()
    if not REVISION.fullmatch(revision):
        raise ReleaseError("source revision is not an exact commit")
    tree = _git(root, "rev-parse", f"{revision}^{{tree}}").decode("ascii").strip()
    entries = {}
    for entry in _git(root, "ls-tree", "-rz", "--full-tree", revision).split(b"\0"):
        if not entry:
            continue
        header, path_bytes = entry.split(b"\t", 1)
        path = path_bytes.decode("utf-8", errors="surrogateescape")
        mode, kind, oid = header.decode("ascii").split()
        entries[path] = (mode, kind, oid)
    contract_paths = {p for p in SOURCE_PATHS if p.startswith(CONTRACT_PATH)}
    if {p for p in entries if p.startswith(CONTRACT_PATH)} != contract_paths:
        raise ReleaseError("tracked contract input inventory is not exact")
    contract_dir = root / CONTRACT_PATH
    check_no_symlinks(contract_dir)
    disk_paths = set()
    for path in contract_dir.rglob("*"):
        check_no_symlinks(path)
        if not path.is_dir():
            disk_paths.add(path.relative_to(root).as_posix())
    if disk_paths != contract_paths:
        raise ReleaseError("working contract input inventory is not exact")
    files, records = {}, []
    for path in SOURCE_PATHS:
        safe_path(path)
        mode, kind, oid = entries.get(path, (None, None, None))
        if mode not in ("100644", "100755") or kind != "blob":
            raise ReleaseError(f"missing or unsafe tracked input: {path}")
        expected_index = f"{mode} {oid} 0\t{path}\0".encode("utf-8")
        if _git(root, "ls-files", "--stage", "-z", "--", path) != expected_index:
            raise ReleaseError(f"dirty or untracked index input: {path}")
        raw = _read_regular(root / path)
        file_mode = (root / path).stat().st_mode
        actual_mode = "100755" if file_mode & stat.S_IXUSR else "100644"
        if actual_mode != mode or raw != _git(root, "cat-file", "blob", oid):
            raise ReleaseError(f"dirty source bytes or mode: {path}")
        files[path] = raw
        records.append({"path": path, "git_mode": mode, "sha256": sha256_bytes(raw)})
    # Tool selection cannot claim another revision's program bytes.
    for path in (BUILDER, VERIFIER):
        if files[path] != _read_regular(ROOT / path):
            raise ReleaseError(f"executing tooling differs from selected source: {path}")
    if sha256_bytes(files["LICENSE"]) != LICENSE_SHA256:
        raise ReleaseError("tracked Apache-2.0 LICENSE bytes differ")
    try:
        project = tomllib.loads(files["pyproject.toml"].decode("utf-8"))["project"]
        lock = tomllib.loads(files["uv.lock"].decode("utf-8"))
        identity_matches = (
            files[".python-version"].decode().strip() == platform.python_version()
            and project["requires-python"] == "==" + platform.python_version()
            and "rfc8785==0.1.4" in project["dependencies"]
            and [p["version"] for p in lock["package"] if p["name"] == "rfc8785"] == ["0.1.4"]
            and importlib.metadata.version("rfc8785") == "0.1.4"
        )
    except (KeyError, TypeError, ValueError, UnicodeError) as exc:
        raise ReleaseError("malformed source tool configuration/lock") from exc
    if not identity_matches:
        raise ReleaseError("executing Python/JCS identity differs from source configuration/lock")
    framed = b"".join(f"{r['git_mode']} {r['sha256']} {r['path']}\n".encode("utf-8") for r in records)
    return files, {"revision": revision, "git_tree": tree,
                   "source_tree_sha256": sha256_bytes(framed), "inputs": records}


def _schema_has_forbidden_term(value: Any) -> bool:
    if isinstance(value, dict):
        return any(any(t in key.lower() for t in FORBIDDEN_SCHEMA_TERMS)
                   or _schema_has_forbidden_term(child) for key, child in value.items())
    if isinstance(value, list):
        return any(_schema_has_forbidden_term(child) for child in value)
    return isinstance(value, str) and any(t in value.lower() for t in FORBIDDEN_SCHEMA_TERMS)


def schema_bytes(source: dict[str, bytes]) -> dict[str, bytes]:
    files = {}
    for name in SCHEMA_NAMES:
        value = parse_json_bytes(source[CONTRACT_PATH + name], label=name)
        if (not isinstance(value, dict) or value.get("$schema") != SCHEMA_DIALECT
                or value.get("$id") != name or _schema_has_forbidden_term(value)):
            raise ReleaseError(f"wrong identity or forbidden form in {name}")
        files[name] = canonical_json_bytes(value)
    return files


def conformance_bytes(source: dict[str, bytes]) -> bytes:
    # Package BOTH complete documents, including T042's semantic cases and normalization
    # examples. This records vectors, not a schema/runtime execution verdict.
    records = []
    for path in VECTOR_PATHS:
        value = parse_json_bytes(source[path], label=path)
        if (not isinstance(value, dict) or value.get("contract") != "candidate-content"
                or value.get("synthetic_only") is not True):
            raise ReleaseError("conformance input is not synthetic Candidate content")
        records.append({"source_file": path, "source_sha256": sha256_bytes(source[path]),
                        "vectors": value})
    return b"".join(canonical_json_bytes(record) + b"\n" for record in records)


def binding(name: str, raw: bytes) -> dict[str, Any]:
    return {"relative_locator": name, "byte_size": len(raw), "sha256": sha256_bytes(raw)}


def generation_tool(source: dict[str, bytes]) -> dict[str, Any]:
    return {**binding(BUILDER, source[BUILDER]), "canonicalizer": "rfc8785==0.1.4"}


def expected_release_files(source: dict[str, bytes], context: dict[str, Any]) -> dict[str, bytes]:
    files = schema_bytes(source)
    files[CONFORMANCE] = conformance_bytes(source)
    manifest = {
        "manifest_format_version": "1", "release_name": "candidate-content",
        "release_version": RELEASE_VERSION, "release_tag": RELEASE_TAG,
        "schema_dialect": SCHEMA_DIALECT, "serialization": SERIALIZATION,
        "digest_algorithm": "sha256", "source_revision": context["revision"],
        "source_git_tree": context["git_tree"],
        "source_tree_sha256": context["source_tree_sha256"], "source_inputs": context["inputs"],
        "generation_tool_identity": generation_tool(source),
        "compatibility_policy": "pre-1.0-hard-cut", "license": "Apache-2.0",
        "license_source": binding("LICENSE", source["LICENSE"]),
        "artifacts": [{"contract_name": name.removesuffix(".schema.json"),
                       "contract_version": RELEASE_VERSION, "media_type": "application/schema+json",
                       **binding(name, files[name])} for name in SCHEMA_NAMES],
        "conformance": {**binding(CONFORMANCE, files[CONFORMANCE]), "record_count": 2,
                        "scope": "complete-source-vectors; execution-not-attested"},
        "retired_forms": RETIRED_FORMS,
    }
    files[MANIFEST] = canonical_json_bytes(manifest)
    # Unsigned SLSA v1 structure only: these owner-local URNs identify the byte
    # transformation and local builder, not a hosted platform, level or signer.
    statement = {
        "_type": "https://in-toto.io/Statement/v1",
        "predicateType": "https://slsa.dev/provenance/v1",
        "subject": [{"name": name, "digest": {"sha256": sha256_bytes(files[name])}}
                    for name in sorted(files)],
        "predicate": {
            "buildDefinition": {
                "buildType": "urn:studious-lamp:build:candidate-content:v1",
                "externalParameters": {
                    "release_name": "candidate-content", "release_version": RELEASE_VERSION,
                    "release_tag": RELEASE_TAG, "source_revision": context["revision"],
                    "source_tree_sha256": context["source_tree_sha256"],
                },
                "internalParameters": {"generation_tool_identity": generation_tool(source)},
                "resolvedDependencies": [{"name": r["path"], "digest": {"sha256": r["sha256"]}}
                                         for r in context["inputs"]],
            },
            "runDetails": {"builder": {"id": "urn:studious-lamp:builder:local-release:v1"}},
        },
    }
    files[PROVENANCE] = canonical_json_bytes(statement) + b"\n"
    files["SHA256SUMS"] = b"".join(
        f"{sha256_bytes(files[name])}  {name}\n".encode("ascii") for name in sorted(files)
    )
    return files


def build_release(source_root: Path = ROOT, output: Path = RELEASE_DIR) -> dict[str, bytes]:
    source, context = source_snapshot(source_root)
    files = expected_release_files(source, context)
    if set(files) != set(OUTPUT_NAMES):
        raise ReleaseError("builder output inventory is not exact")
    check_no_symlinks(output.absolute())
    output = output.resolve()
    source_root = source_root.resolve()
    # Never write inside the source inventory or overwrite a declared input.
    for path in SOURCE_PATHS:
        if (source_root / path).absolute().is_relative_to(output.absolute()):
            raise ReleaseError("output directory overlaps source inputs")
    if output.absolute().is_relative_to((source_root / CONTRACT_PATH).absolute()):
        raise ReleaseError("output directory is inside contract sources")
    if output.exists():
        if not output.is_dir():
            raise ReleaseError("output directory is not a directory")
        for child in output.iterdir():
            if child.name not in OUTPUT_NAMES:
                raise ReleaseError("output directory contains an extra file")
            _read_regular(child)
            if child.stat().st_nlink != 1:
                raise ReleaseError("output file has a shared hardlink")
    output.mkdir(parents=True, exist_ok=True)
    for name in OUTPUT_NAMES:
        (output / name).write_bytes(files[name])
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=RELEASE_DIR)
    args = parser.parse_args()
    try:
        build_release(args.source_root, args.output)
    except (OSError, ReleaseError) as exc:
        parser.error(str(exc))
    print("PASS: Candidate-content bytes built; second-environment/candidate gate NOT RUN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
