"""Exercise the portable executable from an unrelated working directory."""
import json, runpy, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from tracescope.protocol import validate_trace
cases=runpy.run_path(str(ROOT/'tests/test_core.py'))['CASES']
exe=ROOT/'packages/TraceScope-Windows/TraceScope.exe'
results=[]
with tempfile.TemporaryDirectory(prefix='tracescope-package-') as work:
    for profile,(source,register) in cases.items():
        src=Path(work)/(profile+'.s');src.write_text(source)
        out=ROOT/'evidence'/('packaged-'+profile+'.json')
        proc=subprocess.run([str(exe),'trace',str(src),'--language','assembly','--profile',profile,'--out',str(out)],cwd=work,capture_output=True,text=True,timeout=60)
        assert proc.returncode==0,(profile,proc.stdout,proc.stderr)
        trace=json.loads(out.read_text(encoding='utf-8'));validate_trace(trace)
        events=trace['events']
        assert events[-1]['values'][register]['value']=='13',profile
        assert any(m['address']=='0x8000' and m['after'].startswith('0c') for e in events for m in e.get('memory',[])),profile
        assert any(e.get('reads') for e in events),profile
        assert all(e['instruction'] and e['before'] for e in events),profile
        results.append({'profile':profile,'status':'passed','events':len(events),'finalRegister':register,'finalValue':'13'})
out=ROOT/'evidence/package-smoke.json'
out.write_text(json.dumps({'executable':str(exe),'workingDirectory':'unrelated temporary directory','results':results},indent=2))
print(f'{len(results)} packaged ISA journeys passed')
