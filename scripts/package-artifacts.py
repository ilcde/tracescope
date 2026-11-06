"""Archive distributable files, excluding local sessions and build caches."""
import hashlib, json, runpy, zipfile, subprocess
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
names=['TraceScope-Windows.zip','TraceScope-debug.apk','TraceScope-source.zip']
names+=sorted(p.name for p in (root/'packages').iterdir() if p.is_file() and (p.suffix in ('.rpm','.deb') or p.name.endswith('.tar.gz')))
for name in names:
    path=root/'packages'/name
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):digest.update(chunk)
    results.append({'file':name,'bytes':path.stat().st_size,'sha256':digest.hexdigest()})
(root/'packages/artifacts.json').write_text(json.dumps(results,indent=2))
(root/'packages/SHA256SUMS').write_text(''.join(item['sha256']+'  '+item['file']+'\n' for item in results))
(root/'packages/release-manifest.json').write_text(json.dumps({'sourceCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'artifacts':results},indent=2))
print(json.dumps(results,indent=2))
