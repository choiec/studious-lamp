"""Static RED gates for the owner-local T003 architecture boundary."""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "src" / "studious_lamp"
INWARD_SOURCES = (
    SOURCE_ROOT / "domain" / "models.py",
    SOURCE_ROOT / "domain" / "policy.py",
    SOURCE_ROOT / "application" / "ports.py",
)

SIBLING_IMPORT_ROOTS = {
    "automatic",
    "automatic_disco",
    "ocis_runtime",
    "shared_ocis",
    "studious_core",
    "symmetrical_umbrella",
    "upgraded",
}
SHARED_OCIS_IMPORT_ROOTS = {"ocis", "ocis_runtime", "shared_ocis"}
DIRECT_STORAGE_IMPORT_ROOTS = {
    "apsw",
    "duckdb",
    "duckdbd",
    "pathlib",
    "peewee",
    "repositoryd",
    "sqlite3",
    "sqlalchemy",
}
INWARD_OUTER_IMPORT_ROOTS = {
    "boto3",
    "duckdb",
    "duckdbd",
    "fastapi",
    "http",
    "mcp",
    "ocis",
    "ocis_runtime",
    "pathlib",
    "repositoryd",
    "requests",
    "sqlite3",
    "sqlalchemy",
}


def _owner_sources() -> tuple[Path, ...]:
    missing = [path.relative_to(ROOT).as_posix() for path in INWARD_SOURCES if not path.is_file()]
    assert not missing, (
        "T002 RED (expected until T003): owner-local inward source files are missing: "
        f"{', '.join(missing)}. T003 must create these files before this gate can pass."
    )
    return INWARD_SOURCES


def _tree(path: Path) -> ast.AST:
    return ast.parse(path.read_text(encoding="utf-8"), filename=path.as_posix())


def _imports(tree: ast.AST) -> tuple[str, ...]:
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return tuple(names)


def _root(module: str) -> str:
    return module.split(".", maxsplit=1)[0]


def _definitions(tree: ast.AST) -> set[str]:
    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    }


def _qualified_name(node: ast.Call) -> str:
    function = node.func
    if isinstance(function, ast.Name):
        return function.id
    if isinstance(function, ast.Attribute):
        return function.attr
    return ""


def test_inward_dependencies_are_owner_local() -> None:
    """Domain/application ports must not depend on outer technology adapters."""

    violations: list[str] = []
    for path in _owner_sources():
        tree = _tree(path)
        for module in _imports(tree):
            if _root(module) in INWARD_OUTER_IMPORT_ROOTS:
                violations.append(f"{path.relative_to(ROOT)} imports {module}")
            if path.parent.name == "domain" and module.startswith("studious_lamp.application"):
                violations.append(f"{path.relative_to(ROOT)} imports inward layer {module}")
            if module.startswith(("studious_lamp.adapters", "studious_lamp.delivery")):
                violations.append(f"{path.relative_to(ROOT)} imports outer layer {module}")

    assert not violations, (
        "T002 RED (expected until T003): inward dependency violations found; "
        "domain and application ports must depend only on owner-local inward policy: "
        + "; ".join(violations)
    )


def test_sibling_implementations_are_not_imported() -> None:
    """Studious source must not import Automatic, Upgraded, or Umbrella implementations."""

    violations = [
        f"{path.relative_to(ROOT)} imports {module}"
        for path in _owner_sources()
        for module in _imports(_tree(path))
        if _root(module) in SIBLING_IMPORT_ROOTS
    ]
    assert not violations, (
        "T002 RED (expected until T003): sibling implementation imports are forbidden: "
        + "; ".join(violations)
    )


def test_shared_ocis_runtime_is_not_an_inward_dependency() -> None:
    """Technology-neutral ports must not import or define a shared first-party oCIS runtime."""

    _owner_sources()
    ports = SOURCE_ROOT / "application" / "ports.py"
    tree = _tree(ports)
    import_violations = [module for module in _imports(tree) if _root(module) in SHARED_OCIS_IMPORT_ROOTS]
    name_violations = [
        name
        for name in _definitions(tree)
        if "ocis" in name.lower()
    ]
    runtime_paths = [
        path.relative_to(ROOT).as_posix()
        for path in (SOURCE_ROOT / "ocis.py", SOURCE_ROOT / "ocis")
        if path.exists()
    ]
    assert not (import_violations or name_violations or runtime_paths), (
        "T002 RED (expected until T003): shared oCIS runtime boundary detected; "
        "keep oCIS in an outer adapter and keep inward ports technology-neutral. "
        f"imports={import_violations}, names={name_violations}, paths={runtime_paths}"
    )


def test_inward_layers_do_not_open_storage_directly() -> None:
    """Domain and application ports must not open Core, repositoryd, or DuckDB storage."""

    violations: list[str] = []
    for path in _owner_sources():
        tree = _tree(path)
        for module in _imports(tree):
            if _root(module) in DIRECT_STORAGE_IMPORT_ROOTS:
                violations.append(f"{path.relative_to(ROOT)} imports {module}")
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and _qualified_name(node) in {"connect", "execute", "open"}:
                violations.append(f"{path.relative_to(ROOT)} calls {_qualified_name(node)}()")

    assert not violations, (
        "T002 RED (expected until T003): direct storage access in inward layers is forbidden; "
        "use technology-neutral ports and outer adapters: " + "; ".join(violations)
    )


def test_post_admission_paths_cannot_read_ocis() -> None:
    """Post-admission authority must be Core-owned ports, never a renewed oCIS read."""

    _owner_sources()
    ports = SOURCE_ROOT / "application" / "ports.py"
    tree = _tree(ports)
    definitions = _definitions(tree)
    required = {"CandidateIntakePort", "SnapshotCustodyPort"}
    missing = sorted(required - definitions)
    oCIS_references = sorted(
        {
            value
            for node in ast.walk(tree)
            if isinstance(node, (ast.Name, ast.Attribute))
            for value in [node.id if isinstance(node, ast.Name) else node.attr]
            if "ocis" in value.lower()
        }
    )
    assert not missing, (
        "T002 RED (expected until T003): T003 must expose separate "
        f"CandidateIntakePort and SnapshotCustodyPort boundaries; missing={missing}"
    )
    assert not oCIS_references, (
        "T002 RED (expected until T003): post-admission oCIS references are forbidden in "
        f"technology-neutral ports: {oCIS_references}"
    )


def test_repositoryd_and_duckdbd_are_separate_ports() -> None:
    """The repositoryd writer and duckdbd state boundary must not call each other."""

    _owner_sources()
    ports = SOURCE_ROOT / "application" / "ports.py"
    tree = _tree(ports)
    definitions = _definitions(tree)
    required = {"CanonicalPublicationPort", "ProductStatePort"}
    missing = sorted(required - definitions)
    cross_boundary_references = sorted(
        {
            value
            for node in ast.walk(tree)
            if isinstance(node, (ast.Name, ast.Attribute))
            for value in [node.id if isinstance(node, ast.Name) else node.attr]
            if value.lower() in {"repositoryd", "duckdbd"}
        }
    )
    import_violations = [
        module
        for module in _imports(tree)
        if _root(module) in {"repositoryd", "duckdbd"}
    ]
    assert not missing, (
        "T002 RED (expected until T003): T003 must expose separate "
        f"CanonicalPublicationPort and ProductStatePort boundaries; missing={missing}"
    )
    assert not (cross_boundary_references or import_violations), (
        "T002 RED (expected until T003): repositoryd-to-duckdbd coupling is forbidden in "
        "application ports; "
        f"references={cross_boundary_references}, imports={import_violations}"
    )
