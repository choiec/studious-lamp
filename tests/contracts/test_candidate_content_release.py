"""T044 release-byte regressions, separate from the frozen schema/runtime oracle."""

from __future__ import annotations

import hashlib
import json
import shutil
import struct
import subprocess
import sys
from pathlib import Path

import pytest
import rfc8785

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import build_candidate_content_release as builder
import verify_release as verifier

# Literal contract inventory: do not obtain the oracle from builder.SOURCE_PATHS.
INPUTS = sorted([
    ".python-version", "LICENSE", "pyproject.toml", "uv.lock",
    "tools/build_candidate_content_release.py", "tools/verify_release.py",
    "contracts/candidate-content/candidate.schema.json",
    "contracts/candidate-content/semantic-content.schema.json",
    "contracts/candidate-content/provenance.schema.json",
    "contracts/candidate-content/processing-profile.schema.json",
    "contracts/candidate-content/conformance/positive.json",
    "contracts/candidate-content/conformance/negative.json",
])
SCHEMAS = ["candidate.schema.json", "semantic-content.schema.json",
           "provenance.schema.json", "processing-profile.schema.json"]
M = "candidate-content.manifest.json"
C = "candidate-content.conformance.jsonl"
P = "candidate-content.provenance.intoto.jsonl"
OUTPUTS = set(SCHEMAS + [M, C, P, "SHA256SUMS"])


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git(root, *args):
    return subprocess.check_output(["git", *args], cwd=root, stderr=subprocess.PIPE)


def commit_fixture(root):
    git(root, "add", "--all")
    git(root, "-c", "user.name=T044 synthetic fixture", "-c", "user.email=fixture@example.invalid",
        "commit", "-m", "test: snapshot synthetic release input")


@pytest.fixture
def source(tmp_path):
    root = tmp_path / "source"
    root.mkdir()
    # Only test-owned local Git; never touch the owner index or its dirty outputs.
    git(root, "init", "-q")
    for name in INPUTS:
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    commit_fixture(root)
    return root


@pytest.fixture
def built(source, tmp_path):
    output = tmp_path / "output"
    builder.build_release(source, output)
    verifier.verify_release(output, source)
    return source, output


def read_json(output, name):
    return json.loads((output / name).read_bytes())


def write_json(output, name, value):
    (output / name).write_bytes(rfc8785.dumps(value) + (b"\n" if name.endswith(".jsonl") else b""))


def reseal(output):
    """Repair outer hashes so mutations must be caught by independent semantic checks."""
    provenance = read_json(output, P)
    provenance["subject"] = [{"name": n, "digest": {"sha256": sha((output / n).read_bytes())}}
                             for n in sorted(SCHEMAS + [M, C])]
    write_json(output, P, provenance)
    checksums(output)


def checksums(output):
    (output / "SHA256SUMS").write_bytes(b"".join(
        (sha((output / n).read_bytes()) + "  " + n + "\n").encode()
        for n in sorted(OUTPUTS - {"SHA256SUMS"})
    ))


# RFC 8785 Appendix B samples: expected text is external to the implementation.
@pytest.mark.parametrize("bits,expected", [
    ("0000000000000000", b"0"), ("8000000000000000", b"0"),
    ("0000000000000001", b"5e-324"), ("8000000000000001", b"-5e-324"),
    ("7fefffffffffffff", b"1.7976931348623157e+308"),
    ("4340000000000000", b"9007199254740992"),
    ("4430000000000000", b"295147905179352830000"),
    ("44b52d02c7e14af5", b"9.999999999999997e+22"),
    ("44b52d02c7e14af6", b"1e+23"),
    ("444b1ae4d6e2ef50", b"1e+21"),
    ("3eb0c6f7a0b5ed8d", b"0.000001"),
    ("41b3de4355555555", b"333333333.3333333"),
])
def test_rfc8785_number_bytes(bits, expected):
    number = struct.unpack(">d", bytes.fromhex(bits))[0]
    assert builder.canonical_json_bytes(number) == expected
    parsed = builder.parse_json_bytes(expected, label="RFC canonical number")
    assert builder.canonical_json_bytes(parsed) == expected


def test_unicode_key_order_and_no_normalization():
    value = {"\ue000": "e\u0301", "\U0001f600": "é", "\r": "\x0f\n"}
    expected = '{"\\r":"\\u000f\\n","😀":"é","\ue000":"e\u0301"}'.encode()
    assert builder.canonical_json_bytes(value) == expected
    assert builder.canonical_json_bytes([1.0, 1e-7, 1e-6, -0.0]) == b"[1,1e-7,0.000001,0]"


@pytest.mark.parametrize("raw", [b'{"x":1,"x":2}', b'\xef\xbb\xbf{}', b'"\xff"', b'NaN', b'Infinity'])
def test_strict_json_rejection(raw):
    with pytest.raises(builder.ReleaseError):
        builder.parse_json_bytes(raw, label="synthetic")


@pytest.mark.parametrize("value", [float("nan"), float("inf"), "\ud800", {"\ud800": 1}, 2**53])
def test_jcs_rejects_nonrepresentable_values(value):
    with pytest.raises(builder.ReleaseError):
        builder.canonical_json_bytes(value)


@pytest.mark.parametrize("raw", [b"{}", b"{}\r\n", b"{}\n\n", b" {}\n", b"[]\n", b"{\n}\n", b"\xef\xbb\xbf{}\n"])
def test_jsonl_rejects_noncanonical_framing(raw):
    with pytest.raises(builder.ReleaseError):
        verifier.jsonl_records(raw)


def test_jsonl_preserves_unicode_line_separator():
    raw = '{"value":"first\u2028second"}\n'.encode()
    assert verifier.jsonl_records(raw) == [{"value": "first\u2028second"}]


def test_full_source_framing_and_bindings(built):
    source, output = built
    m = read_json(output, M)
    records, framed = [], b""
    for name in INPUTS:
        mode = git(source, "ls-tree", "HEAD", "--", name).split(b" ", 1)[0].decode()
        digest = sha((source / name).read_bytes())
        records.append({"path": name, "git_mode": mode, "sha256": digest})
        framed += f"{mode} {digest} {name}\n".encode()
    assert len(records) == 12 and m["source_inputs"] == records
    assert m["source_tree_sha256"] == sha(framed)
    assert m["source_revision"] == git(source, "rev-parse", "HEAD").decode().strip()
    assert m["source_git_tree"] == git(source, "rev-parse", "HEAD^{tree}").decode().strip()
    assert {p.name for p in output.iterdir()} == OUTPUTS
    assert {a["relative_locator"] for a in m["artifacts"]} == set(SCHEMAS)
    # Independently computed T009 diagnostic golden digests for the frozen T043
    # schemas, not values returned by the builder or its JCS dependency.
    expected_hashes = {
        "candidate.schema.json": "a8e76903a7404eebfd16238c47e4c430d62575a380fc6dfad3d7640449e1702e",
        "semantic-content.schema.json": "05970859f28fa81e6d01739f3677c54c71ef97fc0be456039f8f3eb87f8f4ec2",
        "provenance.schema.json": "6e023c1147ac4f13664fffe9ddd5c12401b7fc4cd0d4ae9d11215bf67935d1eb",
        "processing-profile.schema.json": "243a923340eaec7ba809ee45d0d12bcf328664eb9bef4e90bfbc8ba0cf0935bc",
    }
    for artifact in m["artifacts"]:
        name = artifact["relative_locator"]
        raw = (output / name).read_bytes()
        assert raw != (source / "contracts/candidate-content" / name).read_bytes()
        assert artifact["byte_size"] == len(raw) and artifact["sha256"] == sha(raw)
        assert sha(raw) == expected_hashes[name]
    assert m["license"] == "Apache-2.0"
    assert m["conformance"]["sha256"] == sha((output / C).read_bytes())
    assert m["generation_tool_identity"]["sha256"] == sha((source / "tools/build_candidate_content_release.py").read_bytes())
    assert "reproducible" not in (output / P).read_text()
    assert P not in {s["name"] for s in read_json(output, P)["subject"]}
    assert "sha256" not in m and "provenance_sha256" not in m


def test_full_current_conformance_documents_not_old_24_only(built):
    source, output = built
    records = [json.loads(line) for line in (output / C).read_bytes().split(b"\n")[:-1]]
    assert len(records) == 2
    positive, negative = [r["vectors"] for r in records]
    for record, kind in zip(records, ("positive", "negative")):
        path = f"contracts/candidate-content/conformance/{kind}.json"
        assert record["source_file"] == path
        assert record["source_sha256"] == sha((source / path).read_bytes())
        assert record["vectors"] == json.loads((source / path).read_bytes())
    assert len(positive["candidate"]["semantic_content"]["items"]) == 12
    assert len(positive["text_entry_normalization_examples"]) == 4
    assert len(negative["cases"]) == 23
    assert len(negative["semantic_content_cases"]) == 78
    assert sum(c["schema_expected"] == "reject" for c in negative["semantic_content_cases"]) == 50
    assert sum(c.get("runtime_expected") == "reject" for c in negative["semantic_content_cases"]) == 28
    assert read_json(output, M)["conformance"]["scope"] == "complete-source-vectors; execution-not-attested"


def test_end_to_end_canonical_numbers_and_unicode(source, tmp_path):
    path = source / "contracts/candidate-content/candidate.schema.json"
    schema = json.loads(path.read_bytes())
    schema["default"] = {"\ue000": -0.0, "\U0001f600": 1.0, "tiny": 1e-7, "large": 1e20}
    path.write_text(json.dumps(schema, ensure_ascii=False, indent=2))
    commit_fixture(source)
    output = tmp_path / "canonical"
    builder.build_release(source, output)
    assert '"default":{"large":100000000000000000000,"tiny":1e-7,"😀":1,"\ue000":0}'.encode() in (output / path.name).read_bytes()
    verifier.verify_release(output, source)


def test_verifier_never_calls_expected_builder_helpers(built, monkeypatch):
    source, output = built
    def forbidden(*args, **kwargs):
        pytest.fail("verification reused builder expected bytes")
    for name in ("expected_release_files", "schema_bytes", "conformance_bytes", "generation_tool", "binding"):
        monkeypatch.setattr(builder, name, forbidden)
    verifier.verify_release(output, source)
    m = read_json(output, M)
    m["source_tree_sha256"] = "0" * 64
    write_json(output, M, m)
    reseal(output)
    with pytest.raises(builder.ReleaseError):
        verifier.verify_release(output, source)


@pytest.mark.parametrize("path", INPUTS)
def test_dirty_each_of_twelve_inputs_rejected_by_both(built, path, tmp_path):
    source, output = built
    (source / path).write_bytes((source / path).read_bytes() + b"\n")
    with pytest.raises(builder.ReleaseError):
        builder.build_release(source, tmp_path / "must-not-build")
    with pytest.raises(builder.ReleaseError):
        verifier.verify_release(output, source)
    assert not (tmp_path / "must-not-build").exists()


@pytest.mark.parametrize("change", ["missing", "untracked", "staged", "index-only", "mode", "index-mode",
                                     "symlink", "parent-symlink", "tracked-symlink", "gitlink", "extra", "extra-tracked"])
def test_source_inventory_and_modes_reject(built, change, tmp_path):
    source, output = built
    path = source / "contracts/candidate-content/provenance.schema.json"
    relative = path.relative_to(source).as_posix()
    if change == "missing":
        path.unlink()
    elif change == "untracked":
        git(source, "rm", "--cached", "--", relative)
    elif change == "staged":
        path.write_bytes(path.read_bytes() + b"\n")
        git(source, "add", relative)
    elif change == "index-only":
        old = path.read_bytes()
        path.write_bytes(old + b"\n")
        git(source, "add", relative)
        path.write_bytes(old)
    elif change == "mode":
        path.chmod(0o755)
    elif change == "index-mode":
        git(source, "update-index", "--chmod=+x", relative)
    elif change in ("symlink", "tracked-symlink"):
        raw = path.read_bytes()
        target = tmp_path / "symlink-target"
        target.write_bytes(raw)
        path.unlink()
        path.symlink_to(target)
        if change == "tracked-symlink":
            commit_fixture(source)
    elif change == "parent-symlink":
        directory = source / "contracts/candidate-content/conformance"
        moved = tmp_path / "moved-vectors"
        directory.rename(moved)
        directory.symlink_to(moved, target_is_directory=True)
    elif change == "gitlink":
        git(source, "update-index", "--cacheinfo", "160000", git(source, "rev-parse", "HEAD").decode().strip(), relative)
        git(source, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-m", "test: gitlink")
    else:
        (path.parent / "fifth.schema.json").write_text("{}")
        if change == "extra-tracked":
            commit_fixture(source)
    with pytest.raises(builder.ReleaseError):
        builder.build_release(source, tmp_path / "rejected")
    with pytest.raises(builder.ReleaseError):
        verifier.verify_release(output, source)


@pytest.mark.parametrize("path", ["", "/x", "a//b", "a/./b", "../b", "a/../b", "a\\b", "a\nb", "a\rb", "a\0b", "\ud800"])
def test_source_record_unsafe_paths(path):
    with pytest.raises(builder.ReleaseError):
        builder.safe_path(path)


def test_clean_executable_mode_binds_and_unrelated_docs_do_not(built, tmp_path):
    source, output = built
    path = source / "contracts/candidate-content/provenance.schema.json"
    path.chmod(0o755)
    commit_fixture(source)
    other = tmp_path / "executable"
    builder.build_release(source, other)
    verifier.verify_release(other, source)
    before, after = read_json(output, M), read_json(other, M)
    assert before["source_tree_sha256"] != after["source_tree_sha256"]
    assert next(r for r in after["source_inputs"] if r["path"].endswith("/provenance.schema.json"))["git_mode"] == "100755"
    (source / "unrelated.md").write_text("Untracked non-generation document")
    verifier.verify_release(other, source)


MANIFEST_FIELDS = ["manifest_format_version", "release_name", "release_version", "release_tag",
                   "schema_dialect", "serialization", "digest_algorithm", "source_revision",
                   "source_tree_sha256", "generation_tool_identity", "compatibility_policy", "license",
                   "artifacts", "conformance", "retired_forms"]


@pytest.mark.parametrize("field", MANIFEST_FIELDS)
def test_every_required_manifest_field_rejected_when_missing(built, field):
    source, output = built
    m = read_json(output, M)
    del m[field]
    write_json(output, M, m)
    reseal(output)
    with pytest.raises(builder.ReleaseError):
        verifier.verify_release(output, source)


@pytest.mark.parametrize("change", ["revision", "tree", "tree-framing", "source-hash", "source-path", "source-mode",
                                     "source-missing", "source-extra", "source-duplicate", "source-order",
                                     "tool-hash", "artifact-hash", "artifact-size", "artifact-duplicate", "artifact-version",
                                     "artifact-locator", "conformance-hash", "conformance-size", "conformance-scope",
                                     "self-digest", "downstream-digest", "license"])
def test_manifest_semantic_tampering_rejected_after_resealing(built, change):
    source, output = built
    m = read_json(output, M)
    if change == "revision": m["source_revision"] = "0" * 40
    elif change == "tree": m["source_git_tree"] = "0" * 40
    elif change == "tree-framing": m["source_tree_sha256"] = sha(b"".join((source / p).read_bytes() for p in INPUTS))
    elif change == "source-hash": m["source_inputs"][0]["sha256"] = "0" * 64
    elif change == "source-path": m["source_inputs"][0]["path"] = "../escape"
    elif change == "source-mode": m["source_inputs"][0]["git_mode"] = "120000"
    elif change == "source-missing": m["source_inputs"].pop()
    elif change == "source-extra": m["source_inputs"].append({"path": "extra", "git_mode": "100644", "sha256": "0" * 64})
    elif change == "source-duplicate": m["source_inputs"][1] = m["source_inputs"][0]
    elif change == "source-order": m["source_inputs"].reverse()
    elif change == "tool-hash": m["generation_tool_identity"]["sha256"] = "0" * 64
    elif change == "artifact-hash": m["artifacts"][0]["sha256"] = "0" * 64
    elif change == "artifact-size": m["artifacts"][0]["byte_size"] += 1
    elif change == "artifact-duplicate": m["artifacts"][1] = m["artifacts"][0]
    elif change == "artifact-version": m["artifacts"][0]["contract_version"] = "latest"
    elif change == "artifact-locator": m["artifacts"][0]["relative_locator"] = "../escape"
    elif change == "conformance-hash": m["conformance"]["sha256"] = "0" * 64
    elif change == "conformance-size": m["conformance"]["byte_size"] += 1
    elif change == "conformance-scope": m["conformance"]["scope"] = "full-conformance-PASS"
    elif change == "self-digest": m["sha256"] = "0" * 64
    elif change == "downstream-digest": m["provenance_sha256"] = sha((output / P).read_bytes())
    elif change == "license": m["license"] = "UNESTABLISHED"
    write_json(output, M, m)
    reseal(output)
    with pytest.raises(builder.ReleaseError):
        verifier.verify_release(output, source)


@pytest.mark.parametrize("change", ["source-revision", "source-tree", "raw-source", "missing-input", "tool",
                                     "builder", "build-type", "missing-definition", "old-shape", "reproducible",
                                     "wrong-type", "missing-manifest", "subject-hash", "self-subject"])
def test_provenance_structure_and_bindings_reject(built, change):
    source, output = built
    p = read_json(output, P)
    definition = p["predicate"]["buildDefinition"]
    if change == "source-revision": definition["externalParameters"]["source_revision"] = "0" * 40
    elif change == "source-tree": definition["externalParameters"]["source_tree_sha256"] = "0" * 64
    elif change == "raw-source": definition["resolvedDependencies"][0]["digest"]["sha256"] = "0" * 64
    elif change == "missing-input": definition["resolvedDependencies"].pop()
    elif change == "tool": definition["internalParameters"]["generation_tool_identity"]["sha256"] = "0" * 64
    elif change == "builder": p["predicate"]["runDetails"]["builder"]["id"] = "unknown"
    elif change == "build-type": definition["buildType"] = "unknown"
    elif change == "missing-definition": del p["predicate"]["buildDefinition"]
    elif change == "old-shape": p["predicate"] = {"builder": {"id": "old"}, "source": {}, "reproducible": True}
    elif change == "reproducible": p["predicate"]["reproducible"] = True
    elif change == "wrong-type": p["predicateType"] = "https://slsa.dev/provenance/v0.2"
    elif change == "missing-manifest": p["subject"] = [s for s in p["subject"] if s["name"] != M]
    elif change == "subject-hash": p["subject"][0]["digest"]["sha256"] = "0" * 64
    elif change == "self-subject": p["subject"].append({"name": P, "digest": {"sha256": "0" * 64}})
    write_json(output, P, p)
    checksums(output)
    with pytest.raises(builder.ReleaseError):
        verifier.verify_release(output, source)


@pytest.mark.parametrize("change", ["schema-value", "schema-whitespace", "vector-omission", "vector-hash", "vector-path", "jsonl-crlf"])
def test_source_to_output_transform_cannot_be_forged(built, change):
    source, output = built
    if change.startswith("schema"):
        name = SCHEMAS[0]
        schema = read_json(output, name)
        schema["title"] = "changed synthetic title"
        raw = rfc8785.dumps(schema) if change == "schema-value" else (output / name).read_bytes() + b"\n"
    else:
        name = C
        lines = [json.loads(l) for l in (output / C).read_bytes().split(b"\n")[:-1]]
        if change == "vector-omission": del lines[1]["vectors"]["semantic_content_cases"]
        elif change == "vector-hash": lines[1]["source_sha256"] = "0" * 64
        elif change == "vector-path": lines[1]["source_file"] = "../escape"
        raw = b"".join(rfc8785.dumps(l) + (b"\r\n" if change == "jsonl-crlf" else b"\n") for l in lines)
    (output / name).write_bytes(raw)
    m = read_json(output, M)
    record = m["artifacts"][0] if name == SCHEMAS[0] else m["conformance"]
    record.update(byte_size=len(raw), sha256=sha(raw))
    write_json(output, M, m)
    reseal(output)
    with pytest.raises(builder.ReleaseError):
        verifier.verify_release(output, source)


@pytest.mark.parametrize("change", ["missing", "extra", "duplicate", "reverse", "self", "unsafe", "wrong-hash", "uppercase", "one-space", "crlf", "no-lf", "blank"])
def test_checksum_negatives(built, change):
    source, output = built
    path = output / "SHA256SUMS"
    lines = path.read_bytes().splitlines(keepends=True)
    if change == "missing": lines.pop()
    elif change == "extra": lines.append(b"0" * 64 + b"  extra\n")
    elif change == "duplicate": lines[1] = lines[0]
    elif change == "reverse": lines.reverse()
    elif change == "self": lines[0] = b"0" * 64 + b"  SHA256SUMS\n"
    elif change == "unsafe": lines[0] = b"0" * 64 + b"  ../escape\n"
    elif change == "wrong-hash": lines[0] = b"0" * 64 + lines[0][64:]
    elif change == "uppercase": lines[0] = lines[0][:64].upper() + lines[0][64:]
    elif change == "one-space": lines[0] = lines[0].replace(b"  ", b" ")
    elif change == "crlf": lines[0] = lines[0].replace(b"\n", b"\r\n")
    elif change == "no-lf": lines[-1] = lines[-1][:-1]
    elif change == "blank": lines.append(b"\n")
    path.write_bytes(b"".join(lines))
    with pytest.raises(builder.ReleaseError):
        verifier.verify_release(output, source)


@pytest.mark.parametrize("change", ["missing", "extra", "symlink", "directory"])
def test_output_inventory_rejection(built, change):
    source, output = built
    path = output / M
    if change == "extra": (output / "extra.json").write_text("{}")
    else:
        path.unlink()
        if change == "symlink": path.symlink_to(source / "pyproject.toml")
        elif change == "directory": path.mkdir()
    with pytest.raises(builder.ReleaseError):
        verifier.verify_release(output, source)


def test_builder_will_not_write_through_symlink_or_into_sources(source, tmp_path):
    target = tmp_path / "target"
    target.mkdir()
    link = tmp_path / "link"
    link.symlink_to(target, target_is_directory=True)
    for path in (link, link / "child", source, source / "contracts/candidate-content/generated"):
        with pytest.raises(builder.ReleaseError):
            builder.build_release(source, path)
    assert list(target.iterdir()) == []
    with pytest.raises(builder.ReleaseError):
        builder.build_release(source, source / "tools/../contracts/candidate-content/generated")
    raw_source = source / "contracts/candidate-content/candidate.schema.json"
    before = raw_source.read_bytes()
    (target / "candidate.schema.json").hardlink_to(raw_source)
    with pytest.raises(builder.ReleaseError, match="hardlink"):
        builder.build_release(source, target)
    assert raw_source.read_bytes() == before


def test_cli_selection_and_repeated_bytes_are_not_candidate_gate(source, tmp_path):
    outputs = [tmp_path / "first", tmp_path / "second"]
    for output in outputs:
        built = subprocess.run([sys.executable, str(ROOT / "tools/build_candidate_content_release.py"),
                                "--source-root", str(source), "--output", str(output)],
                               capture_output=True, text=True, check=True)
        verified = subprocess.run([sys.executable, str(ROOT / "tools/verify_release.py"),
                                   "--source-root", str(source), "--release", str(output)],
                                  capture_output=True, text=True, check=True)
        assert "candidate gate NOT RUN" in built.stdout and "candidate gate NOT RUN" in verified.stdout
    assert {p.name: p.read_bytes() for p in outputs[0].iterdir()} == {p.name: p.read_bytes() for p in outputs[1].iterdir()}


@pytest.mark.parametrize("change", ["python", "jcs-pin", "jcs-lock", "invalid-toml", "tool-source"])
def test_committed_source_environment_and_program_mismatch(source, tmp_path, change):
    if change == "python":
        (source / ".python-version").write_text("3.13.0\n")
    elif change == "jcs-pin":
        path = source / "pyproject.toml"
        path.write_text(path.read_text().replace("rfc8785==0.1.4", "rfc8785==0.1.3"))
    elif change == "jcs-lock":
        path = source / "uv.lock"
        path.write_text(path.read_text().replace('name = "rfc8785"\nversion = "0.1.4"',
                                                 'name = "rfc8785"\nversion = "0.1.3"'))
    elif change == "invalid-toml":
        (source / "pyproject.toml").write_text("[malformed")
    elif change == "tool-source":
        path = source / "tools/build_candidate_content_release.py"
        path.write_bytes(path.read_bytes() + b"\n# different program revision\n")
    commit_fixture(source)
    with pytest.raises(builder.ReleaseError):
        builder.build_release(source, tmp_path / "rejected")


def test_verification_after_evidence_commit_uses_pinned_source_clone(built, tmp_path):
    source, output = built
    pinned = tmp_path / "pinned-source"
    subprocess.run(["git", "clone", "--no-hardlinks", "--quiet", str(source), str(pinned)], check=True)
    revision = read_json(output, M)["source_revision"]
    (source / "evidence.md").write_text("Synthetic later evidence, not a generation input")
    commit_fixture(source)
    assert git(source, "rev-parse", "HEAD").decode().strip() != revision
    with pytest.raises(builder.ReleaseError, match="revision"):
        verifier.verify_release(output, source)
    result = subprocess.run([sys.executable, str(ROOT / "tools/verify_release.py"),
                             "--source-root", str(pinned), "--release", str(output)],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "candidate gate NOT RUN" in result.stdout
    assert read_json(output, M)["source_revision"] == revision
