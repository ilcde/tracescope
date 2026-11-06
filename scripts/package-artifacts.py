"""Archive distributable files, excluding local sessions and build caches."""
import hashlib, json, runpy, zipfile
from pathlib import Path
root=Path(__file__).resolve().parent.parent
runpy.run_path(str(root/'scripts/package-source.py'))
package=root/'packages/TraceScope-Windows'
out=root/'packages/TraceScope-Windows.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
    for path in sorted(package.rglob('*')):
        relative=path.relative_to(package)
        if path.is_file() and not set(relative.parts).intersection({'.runs','.cache','__pycache__'}):
            archive.write(path,Path('TraceScope-Windows')/relative)
results=[]
for name in ('TraceScope-Windows.zip','TraceScope-debug.apk','TraceScope-source.zip'):
    path=root/'packages'/name
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):digest.update(chunk)
    results.append({'file':name,'bytes':path.stat().st_size,'sha256':digest.hexdigest()})
(root/'packages/artifacts.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
