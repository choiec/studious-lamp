#!/usr/bin/env python3
"""Build deterministic Core API/Handoff bytes; no candidate or publication verdict."""

from __future__ import annotations

import argparse
import importlib.metadata
import os
import platform
import stat
import subprocess
import tomllib
from pathlib import Path

import build_candidate_content_release as common

ROOT = Path(__file__).resolve().parents[1]
BUILDER = "tools/build_core_admission_release.py"
VERIFIER = "tools/verify_release.py"
HELPER = "tools/build_candidate_content_release.py"
CONTRACT_PATH = "contracts/core-admission/"
NORMATIVE = ("openapi.yaml", "handoff-reference.schema.json")
VECTORS = ("conformance/negative.json", "conformance/positive.json")
OUTPUT_NAMES = ("LICENSE", "checksums.sha256", *VECTORS,
                "handoff-reference.schema.json", "manifest.json", "openapi.yaml", "provenance.json")
SOURCE_PATHS = tuple(sorted((
    ".python-version", "LICENSE", "pyproject.toml", "uv.lock", HELPER, BUILDER, VERIFIER,
    *(CONTRACT_PATH + name for name in (*NORMATIVE, *VECTORS)),
), key=lambda name: name.encode("utf-8")))
IDENTITY = {"release_name": "core-admission", "release_id": "core-admission-0.2.0",
            "release_version": "0.2.0", "release_tag": "core-admission-v0.2.0"}
SERIALIZATION = {
    "json": "RFC 8785 JCS; UTF-8; no BOM; no trailing newline",
    "license": "exact tracked bytes",
    "checksums": "lowercase SHA-256, two spaces, unsigned UTF-8 filename order, LF",
}
ReleaseError = common.ReleaseError


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReleaseError(message)


def git(root: Path, *args: str) -> bytes:
    # Select this root's actual HEAD/index, never an environment override or replace ref.
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    try:
        return subprocess.run(["git", "--no-replace-objects", "--no-optional-locks",
                               "-c", "core.fsmonitor=false", *args], cwd=root, env=env,
                              capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ReleaseError("cannot resolve exact Core Git source") from exc


def read_regular(path: Path) -> bytes:
    common.check_no_symlinks(path.absolute())
    info = path.stat()
    require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1,
            "missing/unsafe file or shared hardlink")
    return path.read_bytes()


def inventory(directory: Path) -> set[str]:
    """Include directories too: extra empty directories are not release inputs/assets."""
    common.check_no_symlinks(directory.absolute())
    require(directory.is_dir(), "missing inventory directory")
    names = set()
    for path in directory.rglob("*"):
        common.check_no_symlinks(path)
        name = path.relative_to(directory).as_posix()
        common.safe_path(name)
        if path.is_dir():
            names.add(name + "/")
        else:
            read_regular(path)
            names.add(name)
    return names


def source_snapshot(root: Path) -> tuple[dict[str, bytes], dict]:
    root = root.absolute()
    common.check_no_symlinks(root)
    require(Path(os.fsdecode(git(root, "rev-parse", "--show-toplevel")).strip()) == root,
            "source-root is not the Git root")
    revision = git(root, "rev-parse", "HEAD").decode("ascii").strip()
    require(common.REVISION.fullmatch(revision) is not None, "source revision is not exact")
    tree = git(root, "rev-parse", revision + "^{tree}").decode("ascii").strip()
    entries = {}
    for entry in git(root, "ls-tree", "-rz", "--full-tree", revision).split(b"\0"):
        if entry:
            header, raw_path = entry.split(b"\t", 1)
            path = raw_path.decode("utf-8", errors="surrogateescape")
            entries[path] = header.decode("ascii").split()
    contract_paths = {CONTRACT_PATH + n for n in (*NORMATIVE, *VECTORS)}
    tool_paths = {BUILDER, VERIFIER, HELPER}
    for prefix, expected in ((CONTRACT_PATH, contract_paths), ("tools/", tool_paths)):
        require({p for p in entries if p.startswith(prefix)} == expected,
                "tracked Core source/tool inventory is not exact")
        indexed = git(root, "ls-files", "-z", "--", prefix).split(b"\0")[:-1]
        require(indexed == [p.encode() for p in sorted(expected)],
                "Core source/tool index inventory is not exact")
    require(inventory(root / CONTRACT_PATH) == {*NORMATIVE, *VECTORS, "conformance/"},
            "working Core input inventory is not exact")
    # No undeclared local Python helper/package can participate in imports. Bytecode
    # caches are not sources; T013 separately requires clean locked environments.
    for directory in {root / "tools", ROOT / "tools", Path(common.__file__).absolute().parent}:
        common.check_no_symlinks(directory)
        require({p.name for p in directory.iterdir() if p.name != "__pycache__"}
                == {Path(p).name for p in (BUILDER, VERIFIER, HELPER)},
                "undeclared tooling input")
    source, records = {}, []
    for path in SOURCE_PATHS:
        common.safe_path(path)
        mode, kind, oid = entries.get(path, (None, None, None))
        require(mode in ("100644", "100755") and kind == "blob", "missing/unsafe tracked Core input")
        require(git(root, "ls-files", "--stage", "-z", "--", path)
                == f"{mode} {oid} 0\t{path}\0".encode(), "dirty/untracked Core index input")
        raw = read_regular(root / path)
        actual_mode = "100755" if (root / path).stat().st_mode & stat.S_IXUSR else "100644"
        require(mode == actual_mode and raw == git(root, "cat-file", "blob", oid),
                "dirty Core source bytes/mode")
        source[path] = raw
        records.append({"path": path, "git_mode": mode, "sha256": common.sha256_bytes(raw)})
    for name, executing in ((BUILDER, Path(__file__)), (VERIFIER, ROOT / VERIFIER),
                            (HELPER, Path(common.__file__))):
        require(source[name] == read_regular(executing), "executing Core tool/helper differs from source")
    require(common.sha256_bytes(source["LICENSE"]) == common.LICENSE_SHA256,
            "tracked Apache-2.0 LICENSE differs")
    try:
        project = tomllib.loads(source["pyproject.toml"].decode())["project"]
        lock = tomllib.loads(source["uv.lock"].decode())
        require(source[".python-version"].decode().strip() == platform.python_version() == "3.14.4"
                and project["requires-python"] == "==3.14.4"
                and project["dependencies"] == ["rfc8785==0.1.4"]
                and lock["requires-python"] == "==3.14.4"
                and [p["version"] for p in lock["package"] if p["name"] == "rfc8785"] == ["0.1.4"]
                and importlib.metadata.version("rfc8785") == "0.1.4", "Core Python/JCS lock mismatch")
    except (KeyError, TypeError, ValueError, UnicodeError) as exc:
        raise ReleaseError("invalid Core Python/configuration/lock") from exc
    framed = b"".join(f"{r['git_mode']} {r['sha256']} {r['path']}\n".encode() for r in records)
    return source, {"revision": revision, "git_tree": tree, "inputs": records,
                    "source_tree_sha256": common.sha256_bytes(framed)}


def source_documents(source: dict[str, bytes]) -> dict:
    docs = {n: common.parse_json_bytes(source[CONTRACT_PATH + n], label=n)
            for n in (*NORMATIVE, *VECTORS)}
    require(all(isinstance(v, dict) for v in docs.values()), "Core sources must be objects")
    api, handoff = docs["openapi.yaml"], docs["handoff-reference.schema.json"]
    meta = api.get("x-release")
    require(isinstance(meta, dict) and set(meta) == {
        "name", "release_id", "version", "tag_target", "selection_rationale", "status", "output_root",
        "normative_artifacts", "evidence_artifacts", "license_artifacts", "distributable_inventory",
        "excluded_internal_sources", "serialization", "binding_order", "isolation"},
        "missing/extra Core release selection fields or unsupported claim")
    for key, value in {"name": "core-admission", "release_id": "core-admission-0.2.0",
                       "version": "0.2.0", "tag_target": "core-admission-v0.2.0",
                       "output_root": "build/releases/core-admission",
                       "distributable_inventory": list(OUTPUT_NAMES),
                       "excluded_internal_sources": ["contracts/repositoryd/openapi.yaml",
                                                     "contracts/duckdbd/openapi.yaml"]}.items():
        require(meta.get(key) == value, "wrong Core source release selection")
    require(meta.get("normative_artifacts") == [
        {"path": "openapi.yaml", "source": CONTRACT_PATH + "openapi.yaml",
         "media_type": "application/vnd.oai.openapi+json"},
        {"path": "handoff-reference.schema.json", "source": CONTRACT_PATH + "handoff-reference.schema.json",
         "media_type": "application/schema+json"}], "wrong normative source classification")
    for key, paths in (("evidence_artifacts", ("conformance/positive.json", "conformance/negative.json",
                                             "manifest.json", "provenance.json", "checksums.sha256")),
                       ("license_artifacts", ("LICENSE",))):
        records = meta.get(key)
        require(isinstance(records, list) and len(records) == len(paths), "wrong source classification")
        for record, name in zip(records, paths, strict=True):
            expected = {"path", "role"} | ({"source"} if name in (*VECTORS, "LICENSE") else set())
            require(isinstance(record, dict) and set(record) == expected
                    and record.get("path") == name and isinstance(record.get("role"), str),
                    "wrong evidence/license source classification")
            if "source" in expected:
                require(record["source"] == ("LICENSE" if name == "LICENSE" else CONTRACT_PATH + name),
                        "wrong evidence/license source path")
    require(meta.get("status") == {"source_selection": "PASS", "local_candidate": "NOT RUN",
                                  "tag_creation": "NOT RUN", "publication": "NOT RUN",
                                  "remote_readback": "NOT RUN", "immutable_locator": "UNESTABLISHED"},
            "unsupported source release claim")
    require(api.get("openapi") == "3.1.1" and api.get("jsonSchemaDialect") == common.SCHEMA_DIALECT
            and isinstance(api.get("info"), dict) and api["info"].get("version") == "0.2.0"
            and handoff.get("$schema") == common.SCHEMA_DIALECT
            and handoff.get("$id") == "urn:studious-lamp:core-admission:0.2.0:handoff-reference",
            "wrong Core API/Handoff identity")
    for name in VECTORS:
        require(docs[name].get("synthetic_only") is True
                and docs[name].get("runtime_enforcement") == "NOT RUN"
                and docs[name].get("current_core_release_identity") == "UNESTABLISHED",
                "wrong frozen conformance scope")
    return docs


def expected_release_files(source: dict[str, bytes], context: dict) -> dict[str, bytes]:
    files = {n: common.canonical_json_bytes(v) for n, v in source_documents(source).items()}
    files["LICENSE"] = source["LICENSE"]
    tool = {**common.binding(BUILDER, source[BUILDER]), "canonicalizer": "rfc8785==0.1.4"}
    manifest = {
        "manifest_format_version": "1", **IDENTITY, "schema_dialect": common.SCHEMA_DIALECT,
        "serialization": SERIALIZATION, "digest_algorithm": "sha256", "license": "Apache-2.0",
        "compatibility_policy": "pre-1.0-hard-cut", "source_revision": context["revision"],
        "source_git_tree": context["git_tree"], "source_tree_sha256": context["source_tree_sha256"],
        "source_inputs": context["inputs"], "generation_tool_identity": tool,
        "distributable_inventory": list(OUTPUT_NAMES),
        "artifacts": [{**common.binding(n, files[n]), "classification": "normative",
                       "contract_version": "0.2.0", "media_type": media}
                      for n, media in zip(NORMATIVE, ("application/vnd.oai.openapi+json",
                                                     "application/schema+json"), strict=True)],
        "conformance": [{**common.binding(n, files[n]), "classification": "release_evidence",
                         "scope": "complete-source-vectors; execution-not-attested"} for n in VECTORS],
        "license_artifact": {**common.binding("LICENSE", files["LICENSE"]), "classification": "license"},
    }
    files["manifest.json"] = common.canonical_json_bytes(manifest)
    files["provenance.json"] = common.canonical_json_bytes({
        "_type": "https://in-toto.io/Statement/v1", "predicateType": "https://slsa.dev/provenance/v1",
        "subject": [{"name": n, "digest": {"sha256": common.sha256_bytes(files[n])}} for n in sorted(files)],
        "predicate": {
            "buildDefinition": {
                "buildType": "urn:studious-lamp:build:core-admission:v1",
                "externalParameters": {**IDENTITY, "source_revision": context["revision"],
                                       "source_git_tree": context["git_tree"],
                                       "source_tree_sha256": context["source_tree_sha256"]},
                "internalParameters": {"generation_tool_identity": tool},
                "resolvedDependencies": [{"name": r["path"], "git_mode": r["git_mode"],
                                          "digest": {"sha256": r["sha256"]}} for r in context["inputs"]],
            },
            "runDetails": {"builder": {"id": "urn:studious-lamp:builder:core-admission:v1"}},
        },
    })
    files["checksums.sha256"] = b"".join(
        f"{common.sha256_bytes(files[n])}  {n}\n".encode() for n in sorted(files))
    return files


def output_directory(output: Path, source_root: Path) -> Path:
    output, source_root = output.absolute(), source_root.absolute()
    common.check_no_symlinks(output)
    common.check_no_symlinks(source_root)
    output, source_root = output.resolve(), source_root.resolve()
    for executing_root in {ROOT, Path(common.__file__).resolve().parents[1]} - {source_root}:
        require(not output.is_relative_to(executing_root) and not executing_root.is_relative_to(output),
                "output overlaps executing tooling checkout")
    require(not source_root.is_relative_to(output), "output overlaps source root")
    if output.is_relative_to(source_root):
        # Permit only the owner-selected future materialization location. T012 itself
        # exercises temporary outputs; T013 owns actual owner output/evidence writes.
        require(output == source_root / "build/releases/core-admission", "output overlaps source tree")
        require(not git(source_root, "ls-files", "-z", "--", "build/releases/core-admission"),
                "output overlaps tracked source")
    if output.exists():
        require(inventory(output) <= {*OUTPUT_NAMES, "conformance/"}, "extra output entry")
    return output


def build_release(source_root: Path = ROOT, output: Path | None = None) -> dict[str, bytes]:
    if output is None:
        raise ReleaseError("an explicit --output directory is required")
    output = output_directory(output, source_root)
    source, context = source_snapshot(source_root)
    files = expected_release_files(source, context)
    require(set(files) == set(OUTPUT_NAMES), "incorrect Core output inventory")
    output.mkdir(parents=True, exist_ok=True)
    (output / "conformance").mkdir(exist_ok=True)
    for name in OUTPUT_NAMES:
        (output / name).write_bytes(files[name])
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        build_release(args.source_root, args.output)
    except (OSError, ReleaseError) as exc:
        parser.error(str(exc))
    print("PASS: Core release bytes built; second-environment/candidate gate NOT RUN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
