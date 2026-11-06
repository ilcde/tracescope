import glob, os, platform, shutil, subprocess, sys
from pathlib import Path
ROOT=Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent.parent))

def find(name):
    env=os.environ.get('TRACESCOPE_'+name.upper().replace('+','P'))
    if env and Path(env).exists(): return env
    for base in (ROOT,Path.cwd(),Path(sys.executable).parent):
        local=base/'.tools'/'w64devkit'/'bin'/(name+'.exe')
        if local.exists(): return str(local)
        if name=='rustc':
            local=base/'.tools/rust/bin/rustc.exe'
            if local.exists():return str(local)
    candidates={
      'kotlinc':glob.glob('C:/Program Files/JetBrains/*/plugins/Kotlin/kotlinc/bin/kotlinc.bat'),
      'rustc':glob.glob(str(ROOT/'.tools/rust/*/bin/rustc.exe'))+glob.glob(str(ROOT/'.tools/rust/bin/rustc.exe')),
      'clang':glob.glob(os.path.expandvars('%LOCALAPPDATA%/Android/Sdk/ndk/*/toolchains/llvm/prebuilt/windows-x86_64/bin/clang.exe')),
    }
    return shutil.which(name) or next(iter(candidates.get(name,[])),None)

def version(name):
    path=find(name)
    if not path: return {'status':'unavailable','path':None}
    flag='-version' if name in ('java','javac','kotlinc') else '--version'
    try:
        p=subprocess.run([path,flag],capture_output=True,text=True,timeout=15)
        return {'status':'available','path':path,'version':(p.stdout+p.stderr).strip().split('\n')[0]}
    except Exception as e: return {'status':'blocked','path':path,'reason':str(e)}

def doctor():
    return {'host':platform.platform(),'python':sys.version,'tools':{n:version(n) for n in ('node','java','javac','kotlinc','gcc','g++','gdb','objdump','rustc','clang','bwrap','docker','adb')},
            'isolation':'Native execution disabled by default. Trusted mode is not a sandbox.',
            'androidSdk':os.environ.get('ANDROID_HOME',os.path.expandvars('%LOCALAPPDATA%/Android/Sdk'))}
