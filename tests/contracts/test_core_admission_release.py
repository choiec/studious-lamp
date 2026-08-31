"""T012 temporary-source release regressions; no runtime or candidate acceptance."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import rfc8785

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import build_core_admission_release as builder
import verify_release as verifier

# Independent literal inventories. Do not ask the builder what to expect.
INPUTS = [
    ".python-version", "LICENSE", "contracts/core-admission/conformance/negative.json",
    "contracts/core-admission/conformance/positive.json",
    "contracts/core-admission/handoff-reference.schema.json", "contracts/core-admission/openapi.yaml",
    "pyproject.toml", "tools/build_candidate_content_release.py",
    "tools/build_core_admission_release.py", "tools/verify_release.py", "uv.lock",
]
OUTPUTS = ["LICENSE", "checksums.sha256", "conformance/negative.json", "conformance/positive.json",
           "handoff-reference.schema.json", "manifest.json", "openapi.yaml", "provenance.json"]
DOCUMENTS = ["conformance/negative.json", "conformance/positive.json",
             "handoff-reference.schema.json", "openapi.yaml"]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git(root, *args):
    return subprocess.check_output(["git", *args], cwd=root, stderr=subprocess.PIPE)


def commit_source(root):
    git(root, "add", "--all")
    git(root, "-c", "user.name=T012 synthetic fixture", "-c", "user.email=fixture@example.invalid",
        "commit", "-qm", "test: snapshot synthetic Core input")


@pytest.fixture
def source(tmp_path):
    root = tmp_path / "source"
    root.mkdir()
    git(root, "init", "-q")
    for name in INPUTS:
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    commit_source(root)
    return root


@pytest.fixture
def built(source, tmp_path):
    out = tmp_path / "output"
    builder.build_release(source, out)
    verifier.verify_release(out, source)
    return source, out


def read_json(out, name):
    return json.loads((out / name).read_bytes())


def write_json(out, name, value):
    (out / name).write_bytes(rfc8785.dumps(value))


def checksums(out):
    (out / "checksums.sha256").write_bytes(b"".join(
        f"{sha((out / n).read_bytes())}  {n}\n".encode() for n in OUTPUTS if n != "checksums.sha256"))


def reseal(out):
    """Rebind manifest and all outer hashes; semantic/source checks must still reject."""
    m = read_json(out, "manifest.json")
    for record in [*m.get("artifacts", []), *m.get("conformance", []), m.get("license_artifact", {})]:
        if isinstance(record, dict) and record.get("relative_locator") in OUTPUTS:
            raw = (out / record["relative_locator"]).read_bytes()
            record.update(byte_size=len(raw), sha256=sha(raw))
    write_json(out, "manifest.json", m)
    p = read_json(out, "provenance.json")
    p["subject"] = [{"name": n, "digest": {"sha256": sha((out / n).read_bytes())}}
                    for n in OUTPUTS if n not in ("checksums.sha256", "provenance.json")]
    write_json(out, "provenance.json", p)
    checksums(out)


def reject(out, source):
    with pytest.raises((builder.ReleaseError, OSError)):
        verifier.verify_release(out, source)


def test_complete_inventory_source_framing_and_acyclic_bindings(built):
    source, out = built
    assert sorted(str(p.relative_to(out)) for p in out.rglob('*') if p.is_file()) == OUTPUTS
    m, p = read_json(out, "manifest.json"), read_json(out, "provenance.json")
    records = [{"path": n, "git_mode": git(source, "ls-tree", "HEAD", "--", n).split()[0].decode(),
                "sha256": sha((source / n).read_bytes())} for n in INPUTS]
    framed = b"".join(f"{r['git_mode']} {r['sha256']} {r['path']}\n".encode() for r in records)
    assert len(records) == 11 and m['source_inputs'] == records
    assert m['source_tree_sha256'] == sha(framed)
    assert m['source_revision'] == git(source, 'rev-parse', 'HEAD').decode().strip()
    assert m['source_git_tree'] == git(source, 'rev-parse', 'HEAD^{tree}').decode().strip()
    assert [m[k] for k in ('release_name', 'release_id', 'release_version', 'release_tag')] == [
        'core-admission', 'core-admission-0.2.0', '0.2.0', 'core-admission-v0.2.0']
    assert m['distributable_inventory'] == OUTPUTS
    assert [(a['relative_locator'], a['classification']) for a in m['artifacts']] == [
        ('openapi.yaml', 'normative'), ('handoff-reference.schema.json', 'normative')]
    assert [a['relative_locator'] for a in m['conformance']] == DOCUMENTS[:2]
    assert all(a['scope'] == 'complete-source-vectors; execution-not-attested' for a in m['conformance'])
    assert (out / 'LICENSE').read_bytes() == (source / 'LICENSE').read_bytes()
    assert sha((out / 'LICENSE').read_bytes()) == 'cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30'
    assert [s['name'] for s in p['subject']] == [n for n in OUTPUTS if n not in ('checksums.sha256', 'provenance.json')]
    d = p['predicate']['buildDefinition']
    assert d['resolvedDependencies'] == [{"name": r['path'], "git_mode": r['git_mode'],
                                         "digest": {"sha256": r['sha256']}} for r in records]
    assert d['externalParameters']['source_tree_sha256'] == sha(framed)
    assert d['externalParameters']['source_git_tree'] == m['source_git_tree']
    for key in ('source_revision', 'release_id', 'release_version', 'release_tag'):
        assert d['externalParameters'][key] == m[key]
    for tool in (m['generation_tool_identity'], d['internalParameters']['generation_tool_identity']):
        assert tool == {'relative_locator': 'tools/build_core_admission_release.py',
                        'byte_size': len((source / 'tools/build_core_admission_release.py').read_bytes()),
                        'sha256': sha((source / 'tools/build_core_admission_release.py').read_bytes()),
                        'canonicalizer': 'rfc8785==0.1.4'}
    assert b'reproducible' not in (out / 'manifest.json').read_bytes()
    assert b'reproducible' not in (out / 'provenance.json').read_bytes()
    assert (out / 'checksums.sha256').read_bytes() == b''.join(
        f'{sha((out / n).read_bytes())}  {n}\n'.encode() for n in OUTPUTS if n != 'checksums.sha256')


def test_complete_frozen_documents_raw_vs_canonical(built):
    source, out = built
    # Frozen documents use integer numbers and ASCII object keys: stdlib compact
    # serialization is an independent byte oracle for this bounded source corpus.
    for name in DOCUMENTS:
        raw = (source / 'contracts/core-admission' / name).read_bytes()
        value = json.loads(raw)
        expected = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()
        assert (out / name).read_bytes() == expected != raw
        assert not expected.startswith(b'\xef\xbb\xbf') and not expected.endswith(b'\n')
    for name in DOCUMENTS[:2]:
        assert read_json(out, name) == read_json(source / 'contracts/core-admission', name)
        assert read_json(out, name)['runtime_enforcement'] == 'NOT RUN'
    assert len(read_json(out, 'conformance/negative.json')['shape_cases']) > 50


def test_jcs_numeric_unicode_golden_in_real_pipeline(source, tmp_path):
    path = source / 'contracts/core-admission/conformance/positive.json'
    value = json.loads(path.read_bytes())
    value['jcs_probe'] = {'\ue000': 'e\u0301', '\U0001f600': 'é', '\r': [1.0, 1e-7, 1e-6, -0.0, 1e23]}
    path.write_text(json.dumps(value, ensure_ascii=False))
    commit_source(source)
    out = tmp_path / 'out'
    builder.build_release(source, out)
    verifier.verify_release(out, source)
    assert '"jcs_probe":{"\\r":[1,1e-7,0.000001,0,1e+23],"😀":"é","\ue000":"e\u0301"}'.encode() in (out / DOCUMENTS[1]).read_bytes()


def test_determinism_and_cli_use_selected_roots(source, tmp_path):
    a, b = tmp_path / 'a', tmp_path / 'b'
    for out in (a, b):
        result = subprocess.run([sys.executable, '-B', str(source / 'tools/build_core_admission_release.py'),
                                 '--source-root', str(source), '--output', str(out)], capture_output=True)
        assert result.returncode == 0, result.stderr
        result = subprocess.run([sys.executable, '-B', str(source / 'tools/verify_release.py'),
                                 '--source-root', str(source), '--release', str(out)], capture_output=True)
        assert result.returncode == 0, result.stderr
        assert b'candidate gate NOT RUN' in result.stdout
    assert {n: (a/n).read_bytes() for n in OUTPUTS} == {n: (b/n).read_bytes() for n in OUTPUTS}
    result = subprocess.run([sys.executable, '-B', str(source / 'tools/build_core_admission_release.py')], capture_output=True)
    assert result.returncode != 0 and b'--output' in result.stderr
    assert not (source / 'build').exists()


@pytest.mark.parametrize('name', INPUTS)
@pytest.mark.parametrize('kind', ['dirty', 'staged', 'missing'])
def test_every_raw_input_authenticated(built, name, kind):
    source, out = built
    p = source / name
    if kind == 'missing':
        p.unlink()
    else:
        p.write_bytes(p.read_bytes() + b'\n')
        if kind == 'staged':
            git(source, 'add', '--', name)
    reject(out, source)
    with pytest.raises((builder.ReleaseError, OSError)):
        builder.build_release(source, out)


@pytest.mark.parametrize('kind', ['mode', 'index-mode', 'assume-unchanged', 'skip-worktree', 'untracked',
                                  'extra-contract', 'extra-tracked', 'extra-empty-directory', 'helper',
                                  'symlink', 'hardlink', 'untracked-helper', 'revision'])
def test_source_boundary_rejections(built, kind, tmp_path):
    source, out = built
    p = source / INPUTS[2]
    if kind == 'mode':
        p.chmod(0o755)
    elif kind == 'index-mode':
        git(source, 'update-index', '--chmod=+x', INPUTS[2])
    elif kind in ('assume-unchanged', 'skip-worktree'):
        git(source, 'update-index', '--' + kind, INPUTS[2])
        p.write_bytes(p.read_bytes() + b' ')
    elif kind == 'untracked':
        git(source, 'rm', '--cached', INPUTS[2])
    elif kind in ('extra-contract', 'extra-tracked'):
        (p.parent / 'extra.json').write_text('{}')
        if kind == 'extra-tracked':
            commit_source(source)
    elif kind == 'extra-empty-directory':
        (p.parent / 'empty').mkdir()
    elif kind == 'helper':
        h = source / 'tools/build_candidate_content_release.py'
        h.write_bytes(h.read_bytes() + b'\n# changed synthetic helper\n')
        commit_source(source)
    elif kind == 'untracked-helper':
        (source / 'tools/extra.py').write_text('value = 1\n')
    elif kind == 'symlink':
        target = tmp_path / 'linked'
        p.rename(target)
        p.symlink_to(target)
    elif kind == 'hardlink':
        os.link(p, tmp_path / 'alias')
    elif kind == 'revision':
        (source / 'unrelated.txt').write_text('new source revision')
        commit_source(source)
    reject(out, source)


@pytest.mark.parametrize('name', ['tools/build_core_admission_release.py', 'tools/verify_release.py'])
def test_committed_tool_must_match_executing_bytes(built, name):
    source, out = built
    p = source / name
    p.write_bytes(p.read_bytes() + b'\n# synthetic tool mutation\n')
    commit_source(source)
    reject(out, source)


@pytest.mark.parametrize('name', ['.python-version', 'LICENSE', 'pyproject.toml', 'uv.lock'])
def test_committed_wrong_toolchain_license(built, name):
    source, out = built
    p = source / name
    p.write_bytes(p.read_bytes().replace(b'3.14.4', b'3.13.0').replace(b'0.1.4', b'0.1.3') + b'\n')
    commit_source(source)
    reject(out, source)
    with pytest.raises(builder.ReleaseError):
        builder.build_release(source, out)


@pytest.mark.parametrize('target', ['release_id', 'version', 'tag_target', 'normative_artifacts',
                                    'distributable_inventory', 'status', 'evidence_artifacts'])
def test_committed_wrong_source_selection(source, tmp_path, target):
    p = source / 'contracts/core-admission/openapi.yaml'
    value = json.loads(p.read_bytes())
    value['x-release'][target] = [] if isinstance(value['x-release'][target], list) else 'wrong'
    p.write_text(json.dumps(value))
    commit_source(source)
    with pytest.raises(builder.ReleaseError):
        builder.build_release(source, tmp_path / 'out')


@pytest.mark.parametrize('name', DOCUMENTS)
@pytest.mark.parametrize('raw', [b'{"x":1,"x":2}', b'\xef\xbb\xbf{}', b'"\xff"', b'{"n":NaN}',
                                b'{"n":1e999}', b'{"s":"\\ud800"}', b'[]'])
def test_malformed_raw_source_rejected(source, tmp_path, name, raw):
    (source / 'contracts/core-admission' / name).write_bytes(raw)
    commit_source(source)
    with pytest.raises(builder.ReleaseError):
        builder.build_release(source, tmp_path / 'out')


@pytest.mark.parametrize('name', OUTPUTS)
def test_missing_output_rejected(built, name):
    source, out = built
    (out / name).unlink()
    reject(out, source)


@pytest.mark.parametrize('name', ['candidate.schema.json', 'repositoryd/openapi.yaml', 'duckdbd/openapi.yaml',
                                 'extra.json', 'conformance/extra.json', 'empty/'])
def test_extra_output_rejected(built, name):
    source, out = built
    p = out / name
    p.parent.mkdir(parents=True, exist_ok=True)
    if name.endswith('/'):
        p.mkdir()
    else:
        p.write_text('{}')
    reject(out, source)
    with pytest.raises(builder.ReleaseError):
        builder.build_release(source, out)


@pytest.mark.parametrize('name', [*DOCUMENTS, 'manifest.json', 'provenance.json'])
@pytest.mark.parametrize('alter', [lambda b: b + b'\n', lambda b: b'\xef\xbb\xbf' + b,
                                  lambda b: b' ' + b, lambda b: b'{"a":1,"a":2}'])
def test_resealed_noncanonical_output_rejected(built, name, alter):
    source, out = built
    p = out / name
    p.write_bytes(alter(p.read_bytes()))
    checksums(out)
    reject(out, source)


@pytest.mark.parametrize('name', DOCUMENTS)
def test_resealed_semantic_output_tamper(built, name):
    source, out = built
    value = read_json(out, name)
    value.pop(next(iter(value)))
    write_json(out, name, value)
    reseal(out)
    reject(out, source)


@pytest.mark.parametrize('field,value', [
    ('release_name', 'candidate-content'), ('release_id', 'core-admission-0.1.0'),
    ('release_version', '0.1.0'), ('release_tag', 'contract-v0.1.0'),
    ('manifest_format_version', 1), ('schema_dialect', 'wrong'), ('digest_algorithm', 'SHA256'),
    ('serialization', {}), ('compatibility_policy', 'compatible'), ('license', 'MIT'),
    ('source_revision', '0'*40), ('source_git_tree', '0'*40), ('source_tree_sha256', '0'*64),
    ('source_inputs', []), ('distributable_inventory', []), ('artifacts', []), ('conformance', []),
    ('license_artifact', {}), ('generation_tool_identity', {}), ('reproducible', True),
    ('provenance_sha256', '0'*64), ('sha256', '0'*64), ('published', True),
])
def test_resealed_manifest_semantics(built, field, value):
    source, out = built
    m = read_json(out, 'manifest.json')
    m[field] = value
    write_json(out, 'manifest.json', m)
    reseal(out)
    reject(out, source)


@pytest.mark.parametrize('kind', ['classification', 'duplicate', 'media', 'version', 'bool-size',
                                  'vector-scope', 'source-order', 'source-mode', 'source-hash',
                                  'source-path', 'missing-field', 'extra-field', 'license-class'])
def test_resealed_nested_manifest_tamper(built, kind):
    source, out = built
    m = read_json(out, 'manifest.json')
    if kind == 'classification': m['artifacts'][0]['classification'] = 'release_evidence'
    elif kind == 'duplicate': m['artifacts'][1] = copy.deepcopy(m['artifacts'][0])
    elif kind == 'media': m['artifacts'][0]['media_type'] = 'application/json'
    elif kind == 'version': m['artifacts'][0]['contract_version'] = '0.1.0'
    elif kind == 'bool-size': m['artifacts'][0]['byte_size'] = True
    elif kind == 'vector-scope': m['conformance'][0]['scope'] = 'runtime PASS'
    elif kind == 'source-order': m['source_inputs'].reverse()
    elif kind == 'source-mode': m['source_inputs'][0]['git_mode'] = '100755'
    elif kind == 'source-hash': m['source_inputs'][0]['sha256'] = '0'*64
    elif kind == 'source-path': m['source_inputs'][0]['path'] = '../.python-version'
    elif kind == 'missing-field': del m['artifacts'][0]['sha256']
    elif kind == 'extra-field': m['artifacts'][0]['reproducible'] = True
    elif kind == 'license-class': m['license_artifact']['classification'] = 'normative'
    write_json(out, 'manifest.json', m)
    # Preserve the targeted inner mutation while resealing only outer evidence.
    p = read_json(out, 'provenance.json')
    for s in p['subject']:
        if s['name'] == 'manifest.json': s['digest']['sha256'] = sha((out / 'manifest.json').read_bytes())
    write_json(out, 'provenance.json', p)
    checksums(out)
    reject(out, source)


@pytest.mark.parametrize('kind', ['type', 'predicate-type', 'subject-hash', 'subject-missing', 'self-subject',
                                  'builder', 'build-type', 'revision', 'tree', 'source-digest', 'release-id',
                                  'tool', 'dependencies', 'input-mode', 'input-hash', 'input-path',
                                  'reproducible', 'run-claim', 'extra-definition', 'manifest-subject'])
def test_resealed_provenance_semantics(built, kind):
    source, out = built
    p = read_json(out, 'provenance.json')
    d = p['predicate']['buildDefinition']
    if kind == 'type': p['_type'] = 'wrong'
    elif kind == 'predicate-type': p['predicateType'] = 'wrong'
    elif kind == 'subject-hash': p['subject'][0]['digest']['sha256'] = '0'*64
    elif kind == 'subject-missing': p['subject'].pop()
    elif kind == 'self-subject': p['subject'][0]['name'] = 'provenance.json'
    elif kind == 'builder': p['predicate']['runDetails']['builder']['id'] = 'wrong'
    elif kind == 'build-type': d['buildType'] = 'wrong'
    elif kind == 'revision': d['externalParameters']['source_revision'] = '0'*40
    elif kind == 'tree': d['externalParameters']['source_git_tree'] = '0'*40
    elif kind == 'source-digest': d['externalParameters']['source_tree_sha256'] = '0'*64
    elif kind == 'release-id': d['externalParameters']['release_id'] = 'candidate-content'
    elif kind == 'tool': d['internalParameters']['generation_tool_identity']['sha256'] = '0'*64
    elif kind == 'dependencies': d['resolvedDependencies'].pop()
    elif kind == 'input-mode': d['resolvedDependencies'][0]['git_mode'] = '100755'
    elif kind == 'input-hash': d['resolvedDependencies'][0]['digest']['sha256'] = '0'*64
    elif kind == 'input-path': d['resolvedDependencies'][0]['name'] = './.python-version'
    elif kind == 'reproducible': p['predicate']['reproducible'] = True
    elif kind == 'run-claim': p['predicate']['runDetails']['reproducible'] = True
    elif kind == 'extra-definition': d['reproducible'] = True
    elif kind == 'manifest-subject':
        next(s for s in p['subject'] if s['name'] == 'manifest.json')['digest']['sha256'] = '0'*64
    write_json(out, 'provenance.json', p)
    checksums(out)
    reject(out, source)


@pytest.mark.parametrize('kind', ['uppercase', 'space', 'crlf', 'no-lf', 'duplicate', 'reverse', 'self', 'escape'])
def test_checksum_framing(built, kind):
    source, out = built
    p = out / 'checksums.sha256'
    raw = p.read_bytes()
    if kind == 'uppercase': raw = raw.upper()
    elif kind == 'space': raw = raw.replace(b'  ', b' ')
    elif kind == 'crlf': raw = raw.replace(b'\n', b'\r\n')
    elif kind == 'no-lf': raw = raw[:-1]
    elif kind == 'duplicate': raw += raw.splitlines(keepends=True)[0]
    elif kind == 'reverse': raw = b''.join(reversed(raw.splitlines(keepends=True)))
    elif kind == 'self': raw += b'0'*64 + b'  checksums.sha256\n'
    elif kind == 'escape': raw = raw.replace(b'  LICENSE', b'  ../LICENSE')
    p.write_bytes(raw)
    reject(out, source)


@pytest.mark.parametrize('kind', ['file-symlink', 'dir-symlink', 'hardlink', 'fifo'])
def test_unsafe_output_rejected_without_writes(built, tmp_path, kind):
    source, out = built
    p = out / 'LICENSE'
    before = (source / 'LICENSE').read_bytes()
    if kind == 'file-symlink':
        p.unlink()
        p.symlink_to(source / 'LICENSE')
    elif kind == 'dir-symlink':
        target = tmp_path / 'vectors'
        (out / 'conformance').rename(target)
        (out / 'conformance').symlink_to(target, target_is_directory=True)
    elif kind == 'hardlink':
        p.unlink()
        os.link(source / 'LICENSE', p)
    elif kind == 'fifo':
        p.unlink()
        os.mkfifo(p)
    reject(out, source)
    with pytest.raises((builder.ReleaseError, OSError)):
        builder.build_release(source, out)
    assert (source / 'LICENSE').read_bytes() == before


@pytest.mark.parametrize('relative', ['.', '..', 'contracts', 'contracts/core-admission',
                                     'contracts/core-admission/output', 'tools/output', '.git/output', 'other'])
def test_output_cannot_overlap_source(source, relative):
    before = {n: (source / n).read_bytes() for n in INPUTS}
    with pytest.raises(builder.ReleaseError):
        builder.build_release(source, source / relative)
    assert before == {n: (source / n).read_bytes() for n in INPUTS}


def test_unrelated_docs_and_git_environment_are_not_inputs(built, monkeypatch, tmp_path):
    source, out = built
    (source / 'notes.md').write_text('unrelated and untracked')
    monkeypatch.setenv('GIT_INDEX_FILE', str(tmp_path / 'absent-index'))
    monkeypatch.setenv('GIT_WORK_TREE', str(tmp_path))
    verifier.verify_release(out, source)


def test_verifier_does_not_regenerate_manifest(built, monkeypatch):
    source, out = built
    def forbidden(*args):
        pytest.fail('independent verifier called manifest generator')
    monkeypatch.setattr(builder, 'expected_release_files', forbidden)
    verifier.verify_release(out, source)


@pytest.mark.parametrize('name', ['contracts/core-admission/extra.json', 'tools/extra.py'])
def test_staged_extra_even_if_removed_from_disk(built, name):
    source, out = built
    p = source / name
    p.write_text('{}')
    git(source, 'add', '--', name)
    p.unlink()
    reject(out, source)


def test_new_committed_source_mode_is_bound(source, tmp_path):
    # A legitimate mode in the selected revision is recorded, not hardcoded to 644.
    (source / INPUTS[2]).chmod(0o755)
    commit_source(source)
    out = tmp_path / 'mode-output'
    builder.build_release(source, out)
    verifier.verify_release(out, source)
    assert read_json(out, 'manifest.json')['source_inputs'][2]['git_mode'] == '100755'


def test_source_root_symlink_or_subdirectory_rejected(source, tmp_path):
    alias = tmp_path / 'source-alias'
    alias.symlink_to(source, target_is_directory=True)
    for root in (alias, source / 'contracts'):
        with pytest.raises(builder.ReleaseError):
            builder.build_release(root, tmp_path / 'out')


def test_untracked_or_dirty_selected_source_cannot_build_its_own_output(source):
    name = 'build/releases/core-admission'
    target = source / name
    target.mkdir(parents=True)
    (target / 'LICENSE').write_bytes((source / 'LICENSE').read_bytes())
    git(source, 'add', '--', name)
    with pytest.raises(builder.ReleaseError):
        builder.build_release(source, target)


def test_temporary_owner_output_location_is_supported(source):
    # This is a synthetic test Git root, never the real owner's build/releases.
    out = source / 'build/releases/core-admission'
    builder.build_release(source, out)
    verifier.verify_release(out, source)


def test_verifier_rejects_wrong_license_after_all_hashes_resealed(built):
    source, out = built
    (out / 'LICENSE').write_bytes(b'not the tracked license')
    reseal(out)
    reject(out, source)


@pytest.mark.parametrize('relative', ['contracts/core-admission', 'tools', '.', 'build/releases/core-admission'])
def test_output_cannot_overwrite_executing_checkout(source, relative):
    # Safety check only, with real writes prohibited by the guard being tested.
    with pytest.raises(builder.ReleaseError, match='executing tooling checkout'):
        builder.output_directory(ROOT / relative, source)


def test_source_metadata_cannot_self_attest_reproducibility(source, tmp_path):
    p = source / 'contracts/core-admission/openapi.yaml'
    value = json.loads(p.read_bytes())
    value['x-release']['reproducible'] = True
    p.write_text(json.dumps(value))
    commit_source(source)
    with pytest.raises(builder.ReleaseError, match='unsupported claim'):
        builder.build_release(source, tmp_path / 'out')
