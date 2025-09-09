import mkdocs_gen_files
from pathlib import Path

files = [
    Path("licence.md"),
    Path("readme.md"),
]

for f in files:
    text = Path(f).read_text(encoding="utf-8")
    target = Path("") / f.name
    with mkdocs_gen_files.open(target, "w", encoding="utf-8") as fd:
        fd.write(text)
