import json, os, re, subprocess, time
from pathlib import Path
from pygdbmi.gdbcontroller import GdbController
from .discovery import find
from .protocol import Recorder, digest

def run(config,emit):
    language=config['language']; directory=Path(config['workdir']); filename=config['filename'];project=Path(config.get('projectDir',directory));src=project/filename
    src.write_text(config['source'],encoding='utf-8')
    exe=directory/('program.exe' if os.name=='nt' else 'program')
    compiler=find({'c':'gcc','cpp':'g++','rust':'rustc'}[language]); debugger=find('gdb')
    if not compiler or not debugger: raise RuntimeError('Compiler and GDB required; run doctor')
    env=os.environ.copy();env['PATH']=str(Path(find('gcc') or compiler).parent)+os.pathsep+env.get('PATH','')
    optimize=config.get('buildProfile')=='optimized'
    if language=='rust': command=[compiler,str(src),'--crate-name','tracescope_user','-g',*(['-C','link-self-contained=yes'] if os.name=='nt' else []),'-C','opt-level='+('2' if optimize else '0'),'-C','linker='+str(find('gcc')),'-o',str(exe)]
    else:
        sources=[str(project/name) for name in config.get('files',{filename:config['source']}) if Path(name).suffix in (('.c',) if language=='c' else ('.cpp','.cc','.cxx','.c'))]
        command=[compiler,*sources,'-I',str(project),'-g','-O2' if optimize else '-O0','-fno-omit-frame-pointer','-std=c17' if language=='c' else '-std=c++17','-o',str(exe)]
    start=time.perf_counter_ns(); result=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',errors='replace',env=env,cwd=directory,timeout=45)
    emit({'metrics':{'compileMs':(time.perf_counter_ns()-start)/1e6},'command':command})
    if result.returncode: raise RuntimeError((result.stderr or result.stdout or f'Compiler exited {result.returncode}')[:12000])
    build=digest(exe.read_bytes());objdump=find('objdump')
    assembly=subprocess.run([objdump,'-d','-l','-C',str(exe)],capture_output=True,text=True,timeout=15).stdout if objdump else ''
    instructions=[];line=0
    for row in assembly.splitlines():
        match=re.search(re.escape(filename)+r':(\d+)',row)
        if match:line=int(match[1])
        match=re.match(r'\s*([\da-f]+):\s+((?:[\da-f]{2} )+)\s*(\S+)\s*(.*)',row)
        if match: instructions.append(dict(address='0x'+match[1],bytes=match[2].strip(),mnemonic=match[3],operands=match[4],line=line,layer='machine code'))
    emit({'buildHash':build,'artifacts':[dict(kind='assembly',label='Exact binary / '+Path(compiler).name,buildHash=build,instructions=instructions[:15000])],
          'limitations':['GDB source snapshots with bounded aggregate fields. Raw C++/Rust representation is shown without executing pretty-printers. Ownership, allocation lifetimes and complete heap tracking are not reconstructed. Values may be optimized out.']})
    recorder=Recorder(emit,config.get('maxEvents',2000))
    if config.get('mode')=='benchmark':
        start=time.perf_counter_ns();p=subprocess.run([str(exe)]+config.get('args',[]),input=config.get('stdin',''),capture_output=True,text=True,env=env,cwd=directory,timeout=10)
        recorder.event('io',output=p.stdout+p.stderr);emit({'metrics':{'executionMs':(time.perf_counter_ns()-start)/1e6,'measurement':'uninstrumented process wall time including startup'}})
        return p.returncode
    stdin=directory/'stdin.txt';stdin.write_text(config.get('stdin',''),encoding='utf-8')
    stdout=directory/'stdout.txt'
    gdb=GdbController(command=[debugger,'--interpreter=mi3','--quiet','--nx'],time_to_check_for_additional_output_sec=.02)
    def cmd(s):
        return gdb.write(s,timeout_sec=15,raise_error_on_timeout=False)
    def result_payload(rows):
        return next((r.get('payload',{}) for r in rows if r.get('type')=='result' and r.get('message')=='done'),{})
    def typed(raw):
        value=raw.get('value','<uncaptured>')
        state='optimized-out' if 'optimized out' in value else 'unavailable' if '<error' in value or '<unavailable>' in value else 'available' if 'value' in raw else 'uncaptured'
        return dict(type=raw.get('type','unknown'),value=value,state=state,address=None,size=None)
    def aggregate(name,fallback):
        if not re.fullmatch(r'[A-Za-z_$][\w$]*',name):return fallback
        root=result_payload(cmd('-var-create - * '+json.dumps(name)))
        if not root.get('name'):return fallback
        budget=[64]
        def capture(node,depth=0):
            value=typed(node);count=int(node.get('numchild','0'))
            if not count:return value
            if depth>=3 or budget[0]<=0:return dict(value,state='truncated')
            rows=result_payload(cmd('-var-list-children --all-values '+node['name']+' 0 '+str(min(32,budget[0]))))
            children={}
            for child in rows.get('children',[]):
                # pygdbmi versions normalize the MI child wrapper differently.
                child=child.get('child',child);budget[0]-=1
                if 'type' not in child and child.get('exp') in ('public','private','protected'):child['type']='C++ access group'
                children[child.get('exp',child.get('name','?'))]=capture(child,depth+1)
                if budget[0]<=0:break
            if children:value.update(children=children,length=count,value=value['value'] if 'value' in node else '{'+str(count)+' fields}',state='truncated' if len(children)<count else 'available')
            return value
        try:return capture(root)
        finally:cmd('-var-delete '+root['name'])
    start=time.perf_counter_ns();exitcode=0;seen_user=False
    def user_file(frame):
        try:
            name=Path(frame.get('fullname','')).resolve().relative_to(project.resolve()).as_posix()
            return name if name in config.get('files',{filename:''}) else None
        except ValueError:return None
    try:
        cmd('-gdb-set auto-load off');cmd('-gdb-set may-call-functions off');cmd('-gdb-set debuginfod enabled off');cmd('-gdb-set pagination off');cmd('-gdb-set confirm off');cmd('-gdb-set print elements 32');cmd('-gdb-set print pretty off')
        cmd('-file-exec-and-symbols '+json.dumps(str(exe).replace('\\','/')))
        rows=cmd('-break-insert '+('tracescope_user::main' if language=='rust' else 'main'))
        if any(r.get('type')=='result' and r.get('message')=='error' for r in rows):raise RuntimeError('GDB could not locate the user entry point: '+str(rows))
        args=' '.join(json.dumps(v) for v in config.get('args',[]))
        # CLI run redirection is controlled by generated absolute paths, never source text.
        rows=cmd('-interpreter-exec console '+json.dumps('run '+args+' < "'+str(stdin).replace('\\','/')+'" > "'+str(stdout).replace('\\','/')+'"'))
        while True:
            stops=[r for r in rows if r.get('type')=='notify' and r.get('message')=='stopped']
            if not stops:
                rows=gdb.get_gdb_response(timeout_sec=10,raise_error_on_timeout=False)
                if not rows: break
                continue
            stop=stops[-1]['payload']
            if stop.get('reason','').startswith('exited'):
                raw=stop.get('exit-code','0')
                exitcode=int(raw,8) if raw.startswith('0') else int(raw)
                break
            if stop.get('reason')=='signal-received': raise RuntimeError('Debugger signal: '+stop.get('signal-name','unknown'))
            frame=stop.get('frame',{});values={}
            variables=result_payload(cmd('-stack-list-variables --simple-values')).get('variables',[])
            for v in variables[:64]:
                value=typed(v)
                if 'value' not in v:value=aggregate(v['name'],value)
                values[v['name']]=value
            stack=result_payload(cmd('-stack-list-frames 0 20')).get('stack',[])
            current_file=user_file(frame)
            if current_file:
                if language=='rust' and not seen_user:
                    cmd('-interpreter-exec console '+json.dumps('skip -rfu ^(core|std|alloc)::'))
                seen_user=True
                recorder.event('line',int(frame.get('line',0)),function=frame.get('func','main'),values=values,instruction=frame.get('addr'),file=current_file,depth=len(stack),stack=[dict(id=str(s.get('level',i)),name=s.get('func','?'),line=int(s.get('line',0))) for i,s in enumerate(stack)])
            rows=cmd('-exec-step' if language=='rust' or not seen_user or current_file else '-exec-finish')
    finally:
        gdb.exit()
    if stdout.exists():recorder.event('io',output=stdout.read_text(encoding='utf-8',errors='replace')[:65536])
    emit({'metrics':{'executionMs':(time.perf_counter_ns()-start)/1e6,'measurement':'debugger wall time including inspection; not benchmark'}})
    return exitcode
