# tests/structure/test_naming_and_packages.py
from __future__ import annotations

from pathlib import Path
import re

# Roots to check (adjust if you want to include more)
CHECK_ROOTS = [
    Path("src/pychilaslasers"),
    Path("tests"),
    Path("examples"),
]

# Folders to skip entirely (anywhere in the path)
SKIP_DIR_PARTS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".ruff_cache",
    ".mypy_cache",
    ".pytest_cache",
    "build",
    "dist",
    ".eggs",
}

# Snake_case file name (with __init__.py and __main__.py allowed)
SNAKE_CASE_PY = re.compile(r"^(?:__init__|__main__|[a-z0-9_]+)\.py$")


def _is_skipped_dir(p: Path) -> bool:
    return any(part in SKIP_DIR_PARTS for part in p.parts)


def _iter_python_files(root: Path):
    if not root.exists():
        return
    for f in root.rglob("*.py"):
        if _is_skipped_dir(f):
            continue
        yield f


def _iter_python_dirs(root: Path):
    """Yield directories (under root) that contain at least one .py file."""
    if not root.exists():
        return
    for d in root.rglob("*"):
        if not d.is_dir() or _is_skipped_dir(d):
            continue
        # contains any non-hidden .py file?
        has_py = any(
            (f.suffix == ".py" and not f.name.startswith("."))
            for f in d.iterdir()
            if f.is_file()
        )
        if has_py:
            yield d


def test_python_filenames_are_snake_case():
    bad = []
    for root in CHECK_ROOTS:
        for f in _iter_python_files(root):
            if not SNAKE_CASE_PY.match(f.name):
                bad.append(str(f))
    assert not bad, (
        "Non-snake_case Python filenames found (allowed: __init__.py, __main__.py): "
        + ", ".join(bad)
    )


def test_python_dirs_have_init_py():
    """Enforce classic packages (no PEP 420 namespace pkgs):
    any dir containing .py files must have an __init__.py.
    """
    missing = []
    for root in CHECK_ROOTS:
        for d in _iter_python_dirs(root):
            if not (d / "__init__.py").exists():
                missing.append(str(d))
    assert not missing, (
        "Directories with Python files but missing __init__.py: " + ", ".join(missing)
    )
