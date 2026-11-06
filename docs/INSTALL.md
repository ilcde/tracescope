# Install and run TraceScope

## WebUI

Open [TraceScope on GitHub Pages](https://ilcde.github.io/tracescope/). JavaScript and TypeScript execute locally in QuickJS WebAssembly. HTML and CSS use WASM analysis and the browser preview. Replay and diagram export also work in the browser. GitHub Pages serves static files: it cannot launch CPython, the JVM, GCC, Rust or Unicorn on GitHub's server for a website visitor.

For Python, Java, Kotlin, C, C++, Rust and assembly, install a runner below. Use its local WebUI or connect the published WebUI to an HTTPS runner you control. Never put a GitHub token in the runner token field.

## Windows

The portable build includes CPython and assembly runtimes; extract the entire ZIP and launch `TraceScope.exe`. For source development install Python 3.11+, Node 22+, Git and JDK 21, then:

```powershell
git clone https://github.com/ilcde/tracescope.git
cd tracescope
powershell -ExecutionPolicy Bypass -File scripts/setup.ps1
powershell -ExecutionPolicy Bypass -File scripts/setup-toolchains.ps1
.venv\Scripts\python.exe -m tracescope doctor
.venv\Scripts\python.exe -m tracescope desktop --trusted-local
```

The setup-toolchains script installs checksum-pinned workspace-local GCC, GDB and Rust. It needs 7-Zip to unpack the vendor archive. Install Kotlin/JVM 2.3.10 separately and add its `bin` directory to PATH, or set `TRACESCOPE_KOTLINC` to `kotlinc.bat`. Tool overrides are documented in the English user guide. Nothing requires WSL.

## Fedora 43 / 44

```bash
sudo dnf install git python3 python3-pip nodejs npm gcc gcc-c++ gdb binutils java-devel unzip curl
# Optional native GTK window; the browser UI does not need GTK.
sudo dnf install python3-gobject gtk3 webkit2gtk4.1
git clone https://github.com/ilcde/tracescope.git
cd tracescope
bash scripts/setup-linux.sh
```

Install Rust 1.90+ using your distribution packages or rustup and Kotlin/JVM 2.3.10 from its official release. JDK 21 is the pinned CI baseline; the `doctor` output reports the actual local toolchain. Configure PATH before starting TraceScope.

```bash
.venv/bin/python -m tracescope doctor
.venv/bin/python -m tracescope serve --trusted-local
# Or a native desktop window with the optional GTK dependencies:
.venv/bin/python -m tracescope desktop --trusted-local
```

The printed URL includes an execution token; keep it private. Keep SELinux enabled. Fedora container CI exercises compilers/debuggers and all ISA profiles but does not prove a physical Wayland/X11 session or SELinux desktop behavior. CI ptrace permissions are scoped to its test containers, not installation instructions to disable host security.

## Ubuntu / Debian

```bash
sudo apt-get update
sudo apt-get install git python3 python3-pip python3-venv nodejs npm gcc g++ gdb binutils openjdk-21-jdk unzip curl
# Optional native window:
sudo apt-get install python3-gi gir1.2-gtk-3.0 gir1.2-webkit2-4.1
git clone https://github.com/ilcde/tracescope.git
cd tracescope
bash scripts/setup-linux.sh
.venv/bin/python -m tracescope serve --trusted-local
```

Use Node 22+ if the distribution's Node is older. Install the same Rust/Kotlin toolchains described above. Ubuntu 24.04 is the automated baseline; other Debian releases need their own acceptance run.

## Android

Download the `android-debug-apk` artifact from a successful [GitHub Actions run](https://github.com/ilcde/tracescope/actions/workflows/verify.yml), or build with `python scripts/build_android.py` after installing JDK 21, SDK platform 35 and build-tools 35.0.0. Install `TraceScope-debug.apk`. It is a development build, not a signed production store release.

Local offline functionality includes JavaScript/TypeScript WASM, HTML/CSS analysis, editing and replay. Heavyweight languages use your HTTPS runner. Android uses the system document picker to open/export files. No root access is required.

## Execution trust and verification

Without `--trusted-local`, native execution is locked. That flag authorizes normal host access; quotas are not a sandbox. Do not run untrusted imported programs or build scripts in this mode.

```bash
npm test
npm run build
node tests/web-ui.mjs
.venv/bin/python -m pytest tests/test_core.py tests/test_journeys.py -q -p no:faulthandler
```

The browser test uses Playwright Chromium on Linux (`npx playwright install --with-deps chromium`). Results and actual screenshots are written under `evidence/` and uploaded by CI. Check the exact workflow commit and job result before treating a platform as verified.
