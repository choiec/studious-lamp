#!/usr/bin/env python3
"""Verify a deterministic local Studious release candidate."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import build_candidate_content_release as release


def _safe_release_file_names(release_dir: Path) -> tuple[str, ...]:
    if release_dir.is_symlink() or not release_dir.is_dir():
        raise release.ReleaseError("release path is missing or unsafe")
    names = []
    for child in release_dir.iterdir():
        if child.is_symlink() or not child.is_file():
            raise release.ReleaseError(f"release contains an unsafe entry: {child.name!r}")
        if child.name in (".", "..") or "/" in child.name or "\\" in child.name:
            raise release.ReleaseError(f"unsafe release artifact name: {child.name!r}")
        names.append(child.name)
    return tuple(sorted(names))


def _read_release_files(release_dir: Path) -> dict[str, bytes]:
    actual_names = _safe_release_file_names(release_dir)
    expected_names = tuple(sorted(release.OUTPUT_NAMES))
    if actual_names != expected_names:
        raise release.ReleaseError(
            f"release inventory mismatch: expected {expected_names!r}, got {actual_names!r}"
        )
    return {
        name: release._read_regular(release_dir / name, label=f"release {name}")
        for name in release.OUTPUT_NAMES
    }


def _validate_recorded_source(manifest: dict[str, object], source: dict[str, bytes]) -> dict[str, str]:
    source_record = manifest.get("source")
    if not isinstance(source_record, dict):
        raise release.ReleaseError("manifest source record is missing")
    revision = source_record.get("revision")
    tree = source_record.get("tree")
    tree_sha256 = source_record.get("tree_sha256")
    if (
        not isinstance(revision, str)
        or not release.REVISION.fullmatch(revision)
        or not isinstance(tree, str)
        or not release.REVISION.fullmatch(tree)
        or not isinstance(tree_sha256, str)
        or not release.HEX_DIGEST.fullmatch(tree_sha256)
    ):
        raise release.ReleaseError("manifest source identity is malformed")
    if tree_sha256 != release.named_bytes_digest(source):
        raise release.ReleaseError("manifest source digest does not match T006 schema bytes")
    if release._git("rev-parse", f"{revision}^{{commit}}") != revision:
        raise release.ReleaseError("manifest source revision is not a commit")
    if release.git_tree(revision) != tree:
        raise release.ReleaseError("manifest source revision/tree binding does not match Git")
    for name in release.SCHEMA_NAMES:
        raw = release.git_file_bytes(revision, f"contracts/candidate-content/{name}")
        if raw != source[name]:
            raise release.ReleaseError(f"source revision bytes differ for {name}")
    return {"revision": revision, "tree": tree, "tree_sha256": tree_sha256}


def _validate_checksum_file(files: dict[str, bytes]) -> None:
    checksum_raw = files["SHA256SUMS"]
    if checksum_raw.startswith(b"\xef\xbb\xbf") or not checksum_raw.endswith(b"\n"):
        raise release.ReleaseError("SHA256SUMS is not UTF-8 LF canonical")
    lines = checksum_raw.splitlines(keepends=True)
    expected_names = sorted(name for name in release.OUTPUT_NAMES if name != "SHA256SUMS")
    seen: list[str] = []
    for line, expected_name in zip(lines, expected_names, strict=False):
        if not line.endswith(b"\n"):
            raise release.ReleaseError("SHA256SUMS has a malformed line ending")
        body = line[:-1]
        try:
            digest, name = body.split(b"  ", 1)
            name_text = name.decode("utf-8")
            digest_text = digest.decode("ascii")
        except (ValueError, UnicodeDecodeError) as exc:
            raise release.ReleaseError("SHA256SUMS has a malformed line") from exc
        if name_text != expected_name or not release.HEX_DIGEST.fullmatch(digest_text):
            raise release.ReleaseError("SHA256SUMS has an unsafe, duplicate, or unordered name")
        if name_text == "SHA256SUMS" or "/" in name_text or "\\" in name_text:
            raise release.ReleaseError("SHA256SUMS contains an unsafe path")
        if digest_text != release.sha256_bytes(files[name_text]):
            raise release.ReleaseError(f"SHA256SUMS digest mismatch for {name_text}")
        seen.append(name_text)
    if len(lines) != len(expected_names) or seen != expected_names:
        raise release.ReleaseError("SHA256SUMS has missing or duplicate entries")


def verify_release(release_dir: Path) -> None:
    files = _read_release_files(release_dir)
    source = release.source_files()
    manifest_value = release.parse_json_bytes(
        files["candidate-content.manifest.json"], label="release manifest"
    )
    if not isinstance(manifest_value, dict):
        raise release.ReleaseError("release manifest is not a JSON object")
    if release.canonical_json_bytes(manifest_value) != files["candidate-content.manifest.json"]:
        raise release.ReleaseError("release manifest is not canonical JCS JSON")
    context = _validate_recorded_source(manifest_value, source)
    expected = release.expected_release_files(source, context)

    if files != expected:
        changed = [name for name in release.OUTPUT_NAMES if files[name] != expected[name]]
        raise release.ReleaseError("release bytes differ for: " + ", ".join(changed))

    # Re-parse the generated evidence even after the exact-byte comparison so a future
    # generator change cannot accidentally make malformed JSONL verification pass.
    release.parse_json_bytes(files["candidate-content.manifest.json"], label="release manifest")
    lines = files["candidate-content.conformance.jsonl"].splitlines(keepends=True)
    if not lines or any(not line.endswith(b"\n") for line in lines):
        raise release.ReleaseError("conformance evidence is not LF JSONL")
    for index, line in enumerate(lines, start=1):
        value = release.parse_json_bytes(line[:-1], label=f"conformance record {index}")
        if release.canonical_json_bytes(value) != line[:-1]:
            raise release.ReleaseError(f"conformance record {index} is not canonical JCS JSON")
    provenance_lines = files["candidate-content.provenance.intoto.jsonl"].splitlines(keepends=True)
    if len(provenance_lines) != 1 or not provenance_lines[0].endswith(b"\n"):
        raise release.ReleaseError("provenance evidence must contain one LF-terminated record")
    provenance_value = release.parse_json_bytes(
        provenance_lines[0][:-1], label="provenance record"
    )
    if release.canonical_json_bytes(provenance_value) != provenance_lines[0][:-1]:
        raise release.ReleaseError("provenance record is not canonical JCS JSON")
    _validate_checksum_file(files)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", required=True, type=Path)
    args = parser.parse_args()
    try:
        verify_release(args.release)
    except (OSError, release.ReleaseError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print("PASS: Candidate-content 0.1.0 release verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
