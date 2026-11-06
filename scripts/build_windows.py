"""Bundle the current pinned CPython environment without changing OS mitigations.

Unicorn 2.1.4 cannot run in the CFG-enabled PyInstaller bootloader. Keep it in
an ordinary, bundled CPython process, identical to the tested source runtime.
"""
import json, os, shutil, subprocess, sys, sysconfig, zipfile
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root/'packages'/'TraceScope-Windows'
out.mkdir(parents=True, exist_ok=True)
runtime = out/'runtime'
runtime.mkdir(exist_ok=True)
base = Path(sys.base_prefix)
version = f'{sys.version_info.major}{sys.version_info.minor}'
for name in ('python.exe', 'pythonw.exe', f'python{version}.dll', 'python3.dll', 'vcruntime140.dll', 'vcruntime140_1.dll', 'LICENSE.txt'):
    shutil.copy2(base/name, runtime/name)
shutil.copytree(base/'DLLs', runtime/'DLLs', dirs_exist_ok=True)
with zipfile.ZipFile(runtime/f'python{version}.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
    for path in (base/'Lib').rglob('*'):
        relative = path.relative_to(base/'Lib')
        if path.is_file() and not set(relative.parts).intersection({'site-packages', '__pycache__', 'test', 'tests', 'idlelib', 'tkinter', 'ensurepip'}):
            archive.write(path, relative)
# _pth isolates imports from globally installed Python and environment paths.
(runtime/f'python{version}._pth').write_text(f'python{version}.zip\nDLLs\nsite-packages\n..\nimport site\n')
site = Path(sysconfig.get_paths()['purelib'])
excluded = {'pip', 'PyInstaller', '_pyinstaller_hooks_contrib', '_pytest', 'pytest', '__pycache__'}
for path in site.iterdir():
    if path.name in excluded or path.name.endswith('.pyc'):
        continue
    target = runtime/'site-packages'/path.name
    target.parent.mkdir(exist_ok=True)
    if path.is_dir():
        shutil.copytree(path, target, dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__'))
    else:
        shutil.copy2(path, target)
for name in ('tracescope', 'dist'):
    shutil.copytree(root/name, out/name, dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__'))
shutil.copy2(root/'capabilities.json', out/'capabilities.json')
compiler = root/'.tools/w64devkit/bin/gcc.exe'
if not compiler.exists():
    compiler = shutil.which('gcc')
if not compiler:
    raise SystemExit('Run scripts/setup-toolchains.ps1 or provide GCC on PATH.')
env = os.environ.copy()
env['PATH'] = str(Path(compiler).parent) + os.pathsep + env.get('PATH', '')
subprocess.run([str(compiler), '-municode', '-O2', '-static', str(root/'scripts/windows_launcher.c'), '-o', str(out/'TraceScope.exe')], check=True, env=env)
(out/'runtime-build.json').write_text(json.dumps({'python':sys.version, 'packaging':'bundled CPython with native launcher', 'globalSecuritySettingsChanged':False}, indent=2))
print(out/'TraceScope.exe')
