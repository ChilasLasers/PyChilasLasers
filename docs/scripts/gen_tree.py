from __future__ import annotations
import ast, sys
from pathlib import Path
import mkdocs_gen_files  # only if you’re using mkdocs-gen-files

# Things to skip
SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    ".vscode",
    ".github",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    "site",
    "dist",
    "build",
    "docs",
    "examples",
    "tests",
    ".env",
}
SKIP_EXTS = {".egg-info", ".deb", ".pyc", ".secrets"}  # treat as dirs too
SKIP_FILES = {"uv.lock", ".env"}

EMOJI_DIR = "📁 "
INDENT = "│   "
ELBOW = "└── "
TEE = "├── "


def first_docline(pyfile: Path) -> str | None:
    if pyfile.suffix != ".py":
        return None
    try:
        ds = ast.get_docstring(
            ast.parse(pyfile.read_text(encoding="utf-8", errors="ignore"))
        )
        return ds.strip().splitlines()[0].strip() if ds else None
    except Exception:
        return None


def annotate(path: Path) -> str:
    line = first_docline(path)
    return f"  # {line}" if line else ""


def build_tree(root: Path, max_depth: int = 10) -> list[str]:
    lines = [f"{EMOJI_DIR}{root.name}/"]

    def walk(d: Path, prefix: str, depth: int):
        if depth < 0:
            return
        entries = []
        for e in d.iterdir():
            if e.name in SKIP_FILES:
                continue
            if e.is_dir():
                if (
                    e.name in SKIP_DIRS
                    or e.suffix in SKIP_EXTS
                    or e.name.endswith(".egg-info")
                ):
                    continue
            entries.append(e)

        entries.sort(key=lambda x: (x.is_file(), x.name.lower()))

        for i, e in enumerate(entries):
            connector = ELBOW if i == len(entries) - 1 else TEE
            if e.is_dir():
                lines.append(f"{prefix}{connector} {EMOJI_DIR}{e.name}/")
                walk(
                    e, prefix + (INDENT if i != len(entries) - 1 else "    "), depth - 1
                )
            else:
                lines.append(f"{prefix}{connector} {e.name}{annotate(e)}")

    walk(root, "", max_depth)
    return lines


# Example: print to stdout (standalone)
if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    print("```\n" + "\n".join(build_tree(root)) + "\n```")
else:
    content = (
        "```\n"
        + "\n".join(build_tree(Path(__file__).resolve().parents[2].joinpath()))
        + "\n```"
    )
    with mkdocs_gen_files.open("index.md", mode="a", encoding="UTF-8") as f:
        f.write(content)
