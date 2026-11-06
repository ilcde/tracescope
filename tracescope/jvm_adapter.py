import json, os, subprocess, time
from pathlib import Path
from .discovery import find, ROOT
from .protocol import Recorder, digest

def run(config,emit):
    directory=Path(config['workdir']);project=Path(config.get('projectDir',directory));source=project/config['filename'];source.write_text(config['source'],encoding='utf-8')
    java=find('java');javac=find('javac');kotlin=find('kotlinc')
    if not java or not javac: raise RuntimeError('JDK 21 required')
    helper=ROOT/'tracescope/jvm/TraceAgent.java'
    start=time.perf_counter_ns()
    p=subprocess.run([javac,'--add-modules','jdk.jdi','-d',str(directory),str(helper)],capture_output=True,text=True,timeout=30)
    if p.returncode: raise RuntimeError(p.stderr)
    classpath=str(directory); main='Main'
    if config['language']=='java': command=[javac,'-g','-d',str(directory),*[str(project/name) for name in config.get('files',{config['filename']:''}) if name.endswith('.java')]]
    else:
        if not kotlin: raise RuntimeError('Kotlin/JVM compiler required')
        command=[kotlin,*[str(project/name) for name in config.get('files',{config['filename']:''}) if name.endswith('.kt')],'-java-parameters','-jvm-target','17','-d',str(directory)]
        classpath+=os.pathsep+str(Path(kotlin).parent.parent/'lib/kotlin-stdlib.jar');main='MainKt'
    main=config.get('mainClass',main)
    p=subprocess.run(command,capture_output=True,text=True,timeout=50)
    emit({'metrics':{'compileMs':(time.perf_counter_ns()-start)/1e6},'command':command})
    if p.returncode:raise RuntimeError(p.stderr)
    classfiles=list(directory.rglob('*.class'));build=digest(b''.join(p.read_bytes() for p in sorted(classfiles) if not p.stem.startswith('TraceAgent')))
    javap=str(Path(java).parent/'javap.exe') if os.name=='nt' else 'javap'
    # Oracle javapath only exposes selected launchers; use javac's real JDK when necessary.
    if os.name=='nt' and not Path(javap).exists():
        candidates=list(Path('C:/Program Files/Java').glob('jdk-21/bin/javap.exe'));javap=str(candidates[0]) if candidates else 'javap'
    bytecode=subprocess.run([javap,'-c','-l','-p','-classpath',classpath,main],capture_output=True,text=True,timeout=15).stdout
    emit({'buildHash':build,'artifacts':[dict(kind='bytecode',label='JVM bytecode / '+main,text=bytecode,buildHash=build,instructions=[])],
          'limitations':['JDI before-line snapshots. Native JIT assembly, GC allocations and logical Kotlin coroutine reconstruction are unavailable. Compilation includes debugger-helper compilation.']})
    recorder=Recorder(emit,config.get('maxEvents',2000));start=time.perf_counter_ns()
    stdin=directory/'stdin.txt';stdin.write_text(config.get('stdin',''),encoding='utf-8')
    if config.get('mode')=='benchmark':
        p=subprocess.run([java,'-Xmx128m','-cp',classpath,main]+config.get('args',[]),input=config.get('stdin','').encode('utf-8'),capture_output=True,timeout=15)
        recorder.event('io',output=(p.stdout+p.stderr).decode('utf-8',errors='replace'))
        emit({'metrics':{'executionMs':(time.perf_counter_ns()-start)/1e6,'measurement':'cold JVM process including startup; no JMH/warmup claim'}})
        if p.returncode:raise RuntimeError('JVM exit '+str(p.returncode))
        return
    process=subprocess.Popen([java,'--add-modules','jdk.jdi','-cp',str(directory),'TraceAgent',classpath,main+' '+ ' '.join('"'+s.replace('"','')+'"' for s in config.get('args',[])),str(stdin)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8')
    try:
        for row in process.stdout:
            event=json.loads(row);kind=event.pop('kind');line=event.pop('line',0);values=event.pop('values',{})
            # Recorder owns sequence/time; preserve observed JVM thread.
            thread=event.pop('thread','main')
            rec=recorder.event(kind,line,values=values,jvmThread=thread,**event)
        process.wait(timeout=20)
        if process.returncode:raise RuntimeError(process.stderr.read()[:8000])
    finally:
        if process.poll() is None:process.kill()
    emit({'metrics':{'executionMs':(time.perf_counter_ns()-start)/1e6,'measurement':'JDI debugger wall time including inspection'}})
