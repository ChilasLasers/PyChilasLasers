import mkdocs_gen_files
from pathlib import Path

files = [
    Path("LICENSE"),
    Path("README.md"),
]

for f in files:
    text = Path(f).read_text(encoding="utf-8")
    target = Path("") / f.name
    target = target.with_suffix(".md")
    with mkdocs_gen_files.open(target, "w", encoding="utf-8") as fd:
        fd.write(text)
