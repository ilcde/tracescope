import ast, dis, io, os, sys, threading, time, types
from pathlib import Path
from .inspect_values import Inspector
from .protocol import Recorder, TraceLimit, digest

def run(config, emit):
    source, filename = config['source'], config.get('filename','main.py')
    project=Path(config.get('projectDir','.')).resolve()
    project_files={str((project/name).resolve()):name for name in config.get('files',{filename:source})}
    filename=str(project/filename)
    start = time.perf_counter_ns()
    code = compile(source, filename, 'exec')
    compile_ms = (time.perf_counter_ns()-start)/1e6
    instructions=[]
    def walk(c):
        for ins in dis.get_instructions(c):
            instructions.append(dict(address=str(ins.offset), mnemonic=ins.opname, operands=ins.argrepr,
                                     line=ins.positions.lineno or 0, function=c.co_name, bytes='', layer='CPython bytecode'))
        for item in c.co_consts:
            if isinstance(item,types.CodeType): walk(item)
    walk(code)
    emit({'artifacts':[dict(kind='bytecode',label='CPython '+sys.version.split()[0], instructions=instructions, buildHash=digest(source))],
          'buildHash':digest(source), 'metrics':{'compileMs':compile_ms},
          'limitations':['CPython line events are before-line, not after-statement. Native extensions are opaque. Objects retained for stable identities affect memory.']})
    recorder = Recorder(emit,config.get('maxEvents',5000)); inspector = Inspector()
    control = {'mode':'continue', 'depth':0, 'paused':False, 'stop':False, 'target':None}
    condition = threading.Condition(); original_stdin = sys.stdin
    def commands():
        import json
        for line in original_stdin:
            try: cmd = json.loads(line)
            except Exception: continue
            with condition:
                action=cmd.get('action')
                if action=='stop': control['stop']=True
                elif action=='pause': control['mode']='pause'
                else:
                    control.update(mode=action, paused=False, target=cmd.get('line'))
                condition.notify_all()
    threading.Thread(target=commands,daemon=True).start()
    frames={}; nextframe=0; lastframe=None; maxdepth=0
    breakpoints=set(config.get('breakpoints',[]))
    def trace(frame,event,arg):
        nonlocal nextframe,lastframe,maxdepth
        current_file=project_files.get(str(Path(frame.f_code.co_filename).resolve()))
        if current_file is None:return trace
        if event not in ('line','call','return','exception','opcode'): return trace
        if control['stop']: raise TraceLimit('cancelled')
        if id(frame) not in frames:
            nextframe+=1; frames[id(frame)]=str(nextframe)
        stack=[]; f=frame
        while f:
            if str(Path(f.f_code.co_filename).resolve()) in project_files:
                stack.append(dict(id=frames.get(id(f),'?'),name=f.f_code.co_name,line=f.f_lineno))
            f=f.f_back
        depth=len(stack)
        maxdepth=max(maxdepth,depth)
        if config.get('instruction'): frame.f_trace_opcodes=True
        extra={'stack':stack, 'depth':depth, 'instruction':str(frame.f_lasti),'file':current_file}
        if event=='return': extra['result']=inspector.value(arg)
        if event=='exception': extra['exception']=type.__getattribute__(arg[0],'__name__')
        recorder.event('instruction' if event=='opcode' else event,frame.f_lineno,frames[id(frame)],frame.f_code.co_name,inspector.locals(frame.f_locals),**extra)
        if event in ('line','opcode'):
            pause = control['mode']=='pause' or frame.f_lineno in breakpoints
            pause |= control['mode']=='stepInto'
            pause |= control['mode']=='stepOver' and depth<=control['depth']
            pause |= control['mode']=='stepOut' and depth<control['depth']
            pause |= control['mode']=='runTo' and frame.f_lineno==control['target']
            if pause:
                with condition:
                    control.update(paused=True,depth=depth)
                    emit({'status':'paused'})
                    while control['paused'] and not control['stop']: condition.wait(.1)
                    emit({'status':'running'})
        if event=='return': frames.pop(id(frame),None)
        return trace
    class Output(io.TextIOBase):
        count=0
        def write(self,text):
            self.count+=len(text)
            if self.count>65536: raise TraceLimit('output quota reached')
            if text: recorder.event('io',output=text)
            return len(text)
        def flush(self): pass
    original=(sys.stdin,sys.stdout,sys.stderr,sys.argv)
    sys.stdin=io.StringIO(config.get('stdin','')); sys.stdout=sys.stderr=Output()
    sys.argv=[filename]+config.get('args',[])
    env={'__name__':'__main__','__file__':filename}
    original_path=list(sys.path);original_cwd=os.getcwd();sys.path.insert(0,str(project));os.chdir(project)
    start=time.perf_counter_ns(); cpu=time.process_time_ns()
    try:
        if config.get('mode')!='benchmark': sys.settrace(trace)
        exec(code,env,env)
    finally:
        sys.settrace(None)
        sys.stdin,sys.stdout,sys.stderr,sys.argv=original
        sys.path[:]=original_path;os.chdir(original_cwd)
        emit({'metrics':{'executionMs':(time.perf_counter_ns()-start)/1e6,'cpuMs':(time.process_time_ns()-cpu)/1e6,
                         'measurement':'uninstrumented execution' if config.get('mode')=='benchmark' else 'instrumented execution including debugger waits',
                         'maxStackDepth':maxdepth}})
