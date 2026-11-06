import zipfile
from pathlib import Path
root=Path(__file__).resolve().parent.parent;out=root/'packages/TraceScope-source.zip'
allowed=['src','tracescope','tests','scripts','docs','examples','android','.github']
files=[]
for directory in allowed:
    files += [p for p in (root/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
files += [p for p in root.iterdir() if p.is_file() and (p.suffix in ('.json','.md','.txt','.ts','.html','.spec') or p.name in ('.gitignore','.gitattributes')) and p.name!='tsconfig.tsbuildinfo']
# Include inspectable results, but never server logs containing session tokens.
# Execution records are private, including those created by local tests. CI
# publishes its separate, deterministic verification artifacts.
out.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as archive:
    for p in sorted(files):archive.write(p,Path('TraceScope')/p.relative_to(root))
print(out)
