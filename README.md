# TraceScope

A working bilingual execution workbench: edit real programs, capture execution, inspect typed values and object identities, and replay without repeating side effects.

**Status: substantial working implementation; full requested acceptance is incomplete.** See [requirements](docs/REQUIREMENTS.md), [capability matrix](capabilities.json), [delivery report](docs/DELIVERY.md), and [original brief](docs/PRODUCT-BRIEF.md). No Linux, security or physical-device compatibility is implied by a successful build.

![TraceScope desktop](evidence/desktop.png)

## Run in this workspace

```powershell
.venv\Scripts\python.exe -m tracescope desktop --trusted-local
```

For local WASM only and locked native execution, omit `--trusted-local`. The flag grants host execution with your account permissions; it is **not a sandbox**. Browser alternative: replace `desktop` with `serve`, then open the printed URL including its session token. Use only trusted code in native mode.

## Artifacts

- `packages/TraceScope-Windows/TraceScope.exe` — portable Windows application; keep the whole folder, including its bundled `runtime`.
- `packages/TraceScope-debug.apk` — installable development APK with offline web/WASM assets.
- `packages/TraceScope-Windows.zip` and `TraceScope-source.zip` — portable and source archives; checksums in `packages/artifacts.json`.
- `dist/` — production frontend and bundled WASM.
- `evidence/` — actual traces, baseline comparisons, test reports and screenshots.
- `docs/USER-GUIDE.en.md` and `docs/USER-GUIDE.vi.md` — operating instructions and limitations.

## Build and verify

```powershell
powershell -File scripts/setup.ps1
npm.cmd run build
npm.cmd test
.venv\Scripts\python.exe -m pytest tests/test_core.py -q -p no:faulthandler
.venv\Scripts\python.exe -m tracescope doctor
.venv\Scripts\python.exe scripts/build_android.py
powershell -File scripts/build_windows.ps1
```

Windows packaging bundles CPython from the build environment and needs GCC for its small native launcher (`scripts/setup-toolchains.ps1`). It does not depend on an installed Python at runtime. Android packaging needs JDK 21, SDK platform 35 and build tools 35.0.0; override `JAVA_HOME` / `ANDROID_HOME` as needed. On Linux use `scripts/setup-linux.sh`; Linux acceptance is blocked by unavailable Fedora hardware/VM in this session.

Headless capture:

```powershell
.venv\Scripts\python.exe -m tracescope trace examples/scan.py --language python --trusted-local --out evidence/my-run.json
.venv\Scripts\python.exe -m tracescope trace examples/x86-64.s --language assembly --profile x86-64 --out evidence/my-assembly.json
.venv\Scripts\python.exe -m tracescope validate evidence/my-run.json
```

Adapters: CPython tracing + actual bytecode; JDI Java/Kotlin + javap; GCC/rustc + GDB + exact-binary objdump; actual QuickJS in WASM + TypeScript checker; HTML/CSS WASM grammars + sandboxed browser snapshots; Unicorn x86/ARM/RISC-V instruction execution. These are scoped teaching baselines, not universal language or project support.

The app currently lacks complete multi-file/build-system workflows, native isolation, full DOM bridge, comprehensive lifetimes/data-dependency graphs, live controls for every adapter, JIT/WASM instruction-state tracing, and complete asymptotic inference patterns. Those remain explicit open requirements.
