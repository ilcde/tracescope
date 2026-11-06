"""Build distribution-specific offline Linux bundles and Fedora RPMs.

Build on the target distribution: wheels are pinned to its Python ABI.
The package never executes pip as root or changes security configuration.
"""
import argparse, hashlib, os, platform, shutil, subprocess, sys, tarfile, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--rpm',action='store_true');parser.add_argument('--deb',action='store_true');args=parser.parse_args()
    if sys.platform!='linux':raise SystemExit('Build Linux packages on the target Linux distribution.')
    release=platform.freedesktop_os_release();distro=release['ID']+release['VERSION_ID']
    arch=platform.machine();version='0.2.0';pyver=f'{sys.version_info.major}.{sys.version_info.minor}'
    output=ROOT/'packages';output.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='tracescope-package-') as work:
        work=Path(work);stage=work/'TraceScope';stage.mkdir()
        for name in ('tracescope','dist','docs','examples'):
            shutil.copytree(ROOT/name,stage/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        for name in ('requirements.txt','capabilities.json','README.md'):
            shutil.copy2(ROOT/name,stage/name)
        shutil.copy2(ROOT/'scripts/linux-launcher.sh',stage/'launch.sh');(stage/'launch.sh').chmod(0o755)
        (stage/'python-version').write_text(pyver)
        wheels=stage/'wheels';wheels.mkdir()
        subprocess.run([sys.executable,'-m','pip','wheel','-r',str(ROOT/'requirements.txt'),'--wheel-dir',str(wheels)],check=True)
        digest=hashlib.sha256()
        for wheel in sorted(wheels.iterdir()):
            with wheel.open('rb') as stream:
                for chunk in iter(lambda:stream.read(1024*1024),b''):digest.update(chunk)
        (stage/'wheels.sha256').write_text(digest.hexdigest())
        with tarfile.open(output/f'TraceScope-{distro}-{arch}.tar.gz','w:gz') as archive:archive.add(stage,arcname='TraceScope')
        if args.rpm:
            top=work/'rpmbuild';(top/'SPECS').mkdir(parents=True)
            spec=top/'SPECS/tracescope.spec'
            spec.write_text(f'''Name: tracescope
Version: {version}
Release: 1%{{?dist}}
Summary: Source execution and typed state visualizer
License: LicenseRef-Proprietary
URL: https://github.com/ilcde/tracescope
BuildArch: {arch}
Requires: python3 = {platform.python_version().split('.')[0]}.{platform.python_version().split('.')[1]}.*
Requires: python3-pip, python3-gobject, gtk3, webkit2gtk4.1
AutoReqProv: no
%global debug_package %{{nil}}
%global __os_install_post %{{nil}}
%description
TraceScope desktop and command line, with offline Python dependency wheels.
Native language compilers and debuggers are installed separately.
%install
mkdir -p %{{buildroot}}/usr/share/tracescope %{{buildroot}}/usr/bin %{{buildroot}}/usr/share/applications %{{buildroot}}/usr/share/icons/hicolor/scalable/apps
cp -a {stage}/. %{{buildroot}}/usr/share/tracescope/
ln -s /usr/share/tracescope/launch.sh %{{buildroot}}/usr/bin/tracescope
cp {ROOT}/scripts/tracescope.desktop %{{buildroot}}/usr/share/applications/
cp {ROOT}/scripts/tracescope.svg %{{buildroot}}/usr/share/icons/hicolor/scalable/apps/
%files
/usr/share/tracescope
/usr/bin/tracescope
/usr/share/applications/tracescope.desktop
/usr/share/icons/hicolor/scalable/apps/tracescope.svg
''')
            # RPM dependencies use the standard interpreter ABI capability.
            spec.write_text(spec.read_text().replace(f'Requires: python3 = {pyver}.*',f'Requires: python(abi) = {pyver}'))
            subprocess.run(['rpmbuild','-bb','--define',f'_topdir {top}',str(spec)],check=True)
            for rpm in (top/'RPMS').rglob('*.rpm'):shutil.copy2(rpm,output/rpm.name)
        if args.deb:
            debroot=work/'deb';control=debroot/'DEBIAN';control.mkdir(parents=True)
            target=debroot/'usr/share/tracescope';shutil.copytree(stage,target)
            (debroot/'usr/bin').mkdir(parents=True);(debroot/'usr/bin/tracescope').symlink_to('/usr/share/tracescope/launch.sh')
            for source,dest in [('scripts/tracescope.desktop','usr/share/applications/tracescope.desktop'),('scripts/tracescope.svg','usr/share/icons/hicolor/scalable/apps/tracescope.svg')]:
                path=debroot/dest;path.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/source,path)
            debarch={'x86_64':'amd64','aarch64':'arm64'}.get(arch,arch)
            upper=f'{sys.version_info.major}.{sys.version_info.minor+1}'
            size=sum(p.stat().st_size for p in target.rglob('*') if p.is_file())//1024
            (control/'control').write_text(f'''Package: tracescope
Version: {version}-1
Architecture: {debarch}
Maintainer: TraceScope project <noreply@github.com>
Depends: python3 (>= {pyver}), python3 (<< {upper}), python3-venv, python3-pip, python3-gi, gir1.2-gtk-3.0, gir1.2-webkit2-4.1
Installed-Size: {size}
Homepage: https://github.com/ilcde/tracescope
Description: Source execution and typed state visualizer
 Desktop and command line with offline Python dependency wheels.
 Native language compilers and debuggers are installed separately.
''')
            subprocess.run(['dpkg-deb','--root-owner-group','--build',str(debroot),str(output/f'tracescope_{version}_{distro}_{debarch}.deb')],check=True)
    print('Linux packages:',output)

if __name__=='__main__':main()
