"""SDK-only debug APK build; no Gradle network resolution or toolchain mutation."""
import os,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sdk=Path(os.environ.get('ANDROID_HOME',os.path.expandvars('%LOCALAPPDATA%/Android/Sdk')))
tools=sdk/'build-tools/35.0.0';platform=sdk/'platforms/android-35/android.jar'
jdk=Path(os.environ.get('JAVA_HOME','C:/Program Files/Java/jdk-21'))
suffix='.exe' if os.name=='nt' else ''
build=ROOT/'build/android';build.mkdir(parents=True,exist_ok=True);(build/'classes').mkdir(exist_ok=True);(build/'dex').mkdir(exist_ok=True)
def run(args):
    p=subprocess.run([str(a) for a in args],capture_output=True,text=True,encoding='utf-8',errors='replace')
    if p.returncode:print(p.stdout+p.stderr);sys.exit(p.returncode)
    if p.stderr:print(p.stderr)
run([jdk/('bin/javac'+suffix),'-source','8','-target','8','-bootclasspath',platform,'-d',build/'classes',ROOT/'android/src/app/tracescope/MainActivity.java'])
with zipfile.ZipFile(build/'classes.jar','w') as z:
    for path in (build/'classes').rglob('*.class'):z.write(path,path.relative_to(build/'classes'))
run([jdk/('bin/java'+suffix),'-cp',tools/'lib/d8.jar','com.android.tools.r8.D8','--min-api','26','--lib',platform,'--output',build/'dex',build/'classes.jar'])
run([tools/('aapt2'+suffix),'link','--manifest',ROOT/'android/AndroidManifest.xml','-I',platform,'-A',ROOT/'dist','-o',build/'unsigned.apk'])
# Rebuild the ZIP directory consistently before alignment. Appending with
# Python to AAPT2's existing archive can leave header flags inconsistent.
with zipfile.ZipFile(build/'unsigned.apk') as source,zipfile.ZipFile(build/'with-dex.apk','w',zipfile.ZIP_DEFLATED) as z:
    for item in source.infolist():z.writestr(item.filename,source.read(item),compress_type=item.compress_type)
    z.write(build/'dex/classes.dex','classes.dex')
run([tools/('zipalign'+suffix),'-f','4',build/'with-dex.apk',build/'aligned.apk'])
keystore=build/'debug.keystore'
if not keystore.exists():run([jdk/('bin/keytool'+suffix),'-genkeypair','-keystore',keystore,'-storepass','android','-alias','androiddebugkey','-keypass','android','-keyalg','RSA','-keysize','2048','-validity','3650','-dname','CN=TraceScope Development'])
out=ROOT/'packages';out.mkdir(exist_ok=True)
run([jdk/('bin/java'+suffix),'-jar',tools/'lib/apksigner.jar','sign','--ks',keystore,'--ks-pass','pass:android','--key-pass','pass:android','--out',out/'TraceScope-debug.apk',build/'aligned.apk'])
run([jdk/('bin/java'+suffix),'-jar',tools/'lib/apksigner.jar','verify','--verbose',out/'TraceScope-debug.apk'])
print(out/'TraceScope-debug.apk')
