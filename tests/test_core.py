import json,sys,time,subprocess
from pathlib import Path
import pytest
from tracescope.inspect_values import Inspector
from tracescope.protocol import manifest,validate_trace,digest
from tracescope.complexity import analyze
from tracescope.service import Runner
from tracescope.assembly_adapter import run as emulate

ROOT=Path(__file__).resolve().parent.parent

def test_exact_values_cycles_and_no_user_code():
    inspector=Inspector();a=[];a.append(a)
    value=inspector.value(a)
    assert value['children']['0']['identity']==value['identity']
    assert value['children']['0']['relation']=='aliases'
    assert inspector.value(9007199254740993)['value']=='9007199254740993'
    assert inspector.value(float('inf'))['value']=='inf'
    class Trap:
        def __getattribute__(self,name):raise AssertionError('inspection executed code')
        def __repr__(self):raise AssertionError('repr executed')
    assert inspector.value(Trap())['state']=='uncaptured'
    class Meta(type):
        @property
        def __name__(cls):raise AssertionError('metaclass getter executed')
    class MetaTrap(metaclass=Meta):pass
    assert inspector.value(MetaTrap())['type']=='object (custom metaclass)'

def test_python_object_storage_without_getters():
    class Node:
        __slots__=('value','next','__dict__')
        @property
        def dangerous(self):raise AssertionError('property executed')
    node=Node();node.value=21;node.next=node;node.label='node'
    captured=Inspector().value(node)
    assert captured['children']['value']['value']=='21'
    assert captured['children']['label']['value']=='node'
    assert captured['children']['next']['relation']=='aliases'
    assert 'dangerous' not in captured['children']

def test_trace_validation_rejects_corruption():
    trace=manifest('python','x=1','main.py','test');validate_trace(trace)
    trace['source']='x=2'
    with pytest.raises(ValueError,match='hash'):validate_trace(trace)
    trace['source']='x=1';trace['events']=[{'seq':9}]
    with pytest.raises(ValueError):validate_trace(trace)

def test_complexity_justifies_bounds_not_nested_loop_count():
    a=analyze('def scan(n):\n    total=0\n    for i in range(n):\n        total+=i\n    return total\n')
    assert a['bound']=='O(n)' and a['classification']=='justified bound'
    triangular=analyze('def f(n):\n    total=0\n    for i in range(n):\n        for j in range(i):\n            total+=j\n    return total\n')
    assert triangular['bound']=='O(n^2)'
    independent=analyze('def f(n):\n    x=0\n    for i in range(n):\n        x+=1\n    for j in range(n):\n        x+=2\n    return x\n')
    assert independent['bound']=='O(n)'
    assert analyze('def f(n):\n    return f(n-1)\n')['classification']=='unknown'
    assert analyze('for i in range(n):\n    n+=1\n')['classification']=='unknown'

CASES={
 'x86-16':('mov ax, 4\nmov bx, 8\nadd ax, bx\nmov word ptr [0x8000], ax\nmov cx, word ptr [0x8000]\ncmp cx, 12\njne end\ncall incval\njmp end\nincval:\ninc cx\nret\nend:\nnop','cx'),
 'x86-32':('mov eax, 4\nmov ebx, 8\nadd eax, ebx\nmov dword ptr [0x8000], eax\nmov ecx, dword ptr [0x8000]\ncmp ecx, 12\njne end\ncall incval\njmp end\nincval:\ninc ecx\nret\nend:\nnop','ecx'),
 'x86-64':('mov rax, 4\nmov rbx, 8\nadd rax, rbx\nmov rdx, 0x8000\nmov qword ptr [rdx], rax\nmov rcx, qword ptr [rdx]\ncmp rcx, 12\njne end\ncall incval\njmp end\nincval:\ninc rcx\nret\nend:\nnop','rcx'),
 'arm32':('mov r0, #4\nmov r1, #8\nadd r0, r0, r1\nmov r2, #0x8000\nstr r0, [r2]\nldr r3, [r2]\ncmp r3, #12\nbne end\nbl incval\nb end\nincval:\nadd r3, r3, #1\nbx lr\nend:\nnop','r3'),
 'thumb':('movs r0, #4\nmovs r1, #8\nadds r0, r0, r1\nmovw r2, #0x8000\nstr r0, [r2]\nldr r3, [r2]\ncmp r3, #12\nbne end\nbl incval\nb end\nincval:\nadds r3, #1\nbx lr\nend:\nnop','r3'),
 'arm64':('mov x0, #4\nmov x1, #8\nadd x0, x0, x1\nmov x2, #0x8000\nstr x0, [x2]\nldr x3, [x2]\ncmp x3, #12\nb.ne end\nbl incval\nb end\nincval:\nadd x3, x3, #1\nret\nend:\nnop','x3'),
 'rv32':('addi x5, x0, 4\naddi x6, x0, 8\nadd x7, x5, x6\nlui x8, 8\nsw x7, 0(x8)\nlw x9, 0(x8)\naddi x10, x0, 12\nbne x9, x10, end\njal x1, incval\njal x0, end\nincval:\naddi x9, x9, 1\njalr x0, 0(x1)\nend:\nnop','x9'),
 'rv64':('addi x5, x0, 4\naddi x6, x0, 8\nadd x7, x5, x6\nlui x8, 8\nsd x7, 0(x8)\nld x9, 0(x8)\naddi x10, x0, 12\nbne x9, x10, end\njal x1, incval\njal x0, end\nincval:\naddi x9, x9, 1\njalr x0, 0(x1)\nend:\nnop','x9')}

@pytest.mark.parametrize('profile',CASES)
def test_actual_isa_register_memory_call_branch(profile):
    source,register=CASES[profile];packets=[];emulate({'source':source,'profile':profile,'maxEvents':100},packets.append)
    events=[p['event'] for p in packets if 'event'in p]
    assert events[-1]['values'][register]['value']=='13'
    assert any(m['address']=='0x8000' and m['after'].startswith('0c') for e in events for m in e.get('memory',[]))
    assert any(e.get('reads') for e in events)
    assert all(e['instruction'] and e['before'] for e in events)
    assert events[-1]['timeNs'].isdigit()
    (ROOT/'evidence'/('isa-'+profile+'.json')).write_text(json.dumps(packets,indent=2),encoding='utf-8')

def collect(config):
    runner=Runner(True);rid=runner.start(config);run=runner.runs[rid]
    deadline=time.monotonic()+110
    while run['process'].poll() is None and time.monotonic()<deadline:time.sleep(.02)
    time.sleep(.1)
    return run['data']

def test_python_changed_input_recursion_alias_exception_baseline():
    source='n=int(input())\ndef f(x):\n    if x<=1: return 1\n    return x*f(x-1)\na=[]\na.append(a)\nb=a\nlarge=9007199254740993\ntry:\n    1/0\nexcept ZeroDivisionError:\n    result=f(n)\nprint(result,large)\n'
    results=[]
    for n in ('4','5'):
        trace=collect({'language':'python','source':source,'stdin':n})
        assert trace['status']=='completed';out=''.join(e.get('output','') for e in trace['events'])
        baseline=subprocess.run([sys.executable,'-c',source],input=n,text=True,capture_output=True)
        assert out==baseline.stdout;results.append(out)
        assert any(e['kind']=='exception' for e in trace['events'])
        assert any(e.get('depth',0)>3 for e in trace['events'])
        assert any(e['values'].get('large',{}).get('value')=='9007199254740993' for e in trace['events'])
        validate_trace(trace)
        (ROOT/'evidence'/('python-input-'+n+'.json')).write_text(json.dumps(trace),encoding='utf-8')
    assert results[0]!=results[1]

def test_live_pause_step_and_cancellation():
    runner=Runner(True);rid=runner.start({'language':'python','source':'x=1\nx+=1\nprint(x)\n','breakpoints':[2]});run=runner.runs[rid]
    deadline=time.monotonic()+10
    while run['data']['status']!='paused' and time.monotonic()<deadline:time.sleep(.02)
    assert run['data']['status']=='paused'
    assert run['data']['events'][-1]['values']['x']['value']=='1'
    runner.control(rid,{'action':'stepInto'})
    time.sleep(.3);assert run['data']['status']=='paused'
    assert run['data']['events'][-1]['values']['x']['value']=='2'
    runner.control(rid,{'action':'stop'});assert run['process'].poll() is not None

def test_quota_partial_trace_and_native_lock():
    trace=collect({'language':'python','source':'i=0\nwhile True:\n    i+=1\n','maxEvents':30})
    assert trace['status']=='truncated' and len(trace['events'])==30
    validate_trace(trace)
    with pytest.raises(PermissionError):Runner().start({'language':'python','source':'print(1)'})

@pytest.mark.parametrize('language,filename',[('java','Main.java'),('kotlin','Main.kt'),('c','main.c'),('cpp','main.cpp'),('rust','main.rs')])
def test_compiled_changed_source_matches_separate_baseline(language,filename):
    source=(ROOT/'examples'/filename).read_text().replace('4, 8, 2, 6, 1','7, 8, 2, 6, 1')
    traced=collect({'language':language,'source':source});baseline=collect({'language':language,'source':source,'mode':'benchmark'})
    assert traced['status']=='completed',traced['diagnostics']
    assert baseline['status']=='completed',baseline['diagnostics']
    output=lambda t:''.join(e.get('output','') for e in t['events'])
    assert output(traced)==output(baseline) and '24' in output(traced)
    assert any(e['values'] for e in traced['events'])
    assert traced['buildHash'] and traced['artifacts'][0]['buildHash']==traced['buildHash']
    (ROOT/'evidence'/(language+'-modified.json')).write_text(json.dumps(traced),encoding='utf-8')
    (ROOT/'evidence'/(language+'-benchmark.json')).write_text(json.dumps(baseline),encoding='utf-8')
