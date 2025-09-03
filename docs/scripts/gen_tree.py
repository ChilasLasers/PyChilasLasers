#!/usr/bin/env python3
"""
Generate a pretty Markdown tree (like your example) with optional annotations:
- Skips common junk (venv, __pycache__, .git, build artifacts)
- Adds the first line of a module/package docstring as a comment (when available)
- Lets you cap depth and choose roots
"""
from __future__ import annotations
import ast, os, sys
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".mypy_cache", ".ruff_cache", ".pytest_cache", "site", "dist", "build", "docs/_build"}
SKIP_FILES = {"uv.lock"}
EMOJI_DIR = "📁 "
INDENT = "│   "
ELBOW  = "└── "
TEE    = "├── "

def first_docline(pyfile: Path) -> str | None:
    try:
        text = pyfile.read_text(encoding="utf-8", errors="ignore")
        mod = ast.parse(text)
        ds = ast.get_docstring(mod)
        if ds:
            line = ds.strip().splitlines()[0].strip()
            return line
    except Exception:
        pass
    return None

def annotate(path: Path) -> str:
    if path.suffix == ".py":
        line = first_docline(path)
        if line:
            return f"  # {line}"
    return ""

def tree(root: Path, max_depth: int = 6) -> list[str]:
    lines: list[str] = []
    def walk(dir: Path, prefix: str, depth: int):
        if depth < 0: return
        entries = [e for e in dir.iterdir() if not (e.name in SKIP_FILES or e.name in SKIP_DIRS or e.name.startswith(".")) ]
        entries.sort(key=lambda p: (p.is_file(), p.name.lower()))
        for i, e in enumerate(entries):
            connector = ELBOW if i == len(entries)-1 else TEE
            if e.is_dir():
                lines.append(f"{prefix}{connector} {EMOJI_DIR}{e.name}/")
                walk(e, prefix + (INDENT if i != len(entries)-1 else "    "), depth-1)
            else:
                comment = annotate(e)
                lines.append(f"{prefix}{connector} {e.name}{comment}")
    lines.append(f"{EMOJI_DIR}{root.name}/")
    walk(root, "", max_depth)
    return lines

def main():
    start = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    max_depth = int(os.environ.get("TREE_DEPTH", "10"))
    lines = tree(start.resolve(), max_depth=max_depth)
    # Wrap in fenced block
    print("```\n" + "\n".join(lines) + "\n```")

if __name__ == "__main__":
    main()
