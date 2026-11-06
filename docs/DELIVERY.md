# TraceScope 0.2 delivery record

## Published project

- Source: [ilcde/tracescope](https://github.com/ilcde/tracescope)
- WebUI: [GitHub Pages](https://ilcde.github.io/tracescope/)
- Packages: [Releases](https://github.com/ilcde/tracescope/releases)
- Verification: [platform workflow](https://github.com/ilcde/tracescope/actions/workflows/verify.yml)
- Deployment: [Pages workflow](https://github.com/ilcde/tracescope/actions/workflows/pages.yml)

The repository and WebUI were published with the user's explicit approval. Local logs, credentials, execution records and caches are excluded. CI publishes deterministic test evidence separately. Releases are development previews, not a claim of full product acceptance.

## Changes delivered in 0.2

**Visuals:** a typed neuron graph built from actual captured values, references and containment, with alias/cycle deduplication; larger labels and controls; resizable panels; a fullscreen diagram retaining replay controls; zoom/fit and real SVG export; vertical phone layout; refined workbench/settings styling. Network-style presentation does not imply unobserved data dependencies or neural execution.

**Languages/projects:** editor modes for every named language; actual TypeScript standard declarations; relative JS/TS ES modules; unbraced loop hooks; Python imports; C/C++ source sets and headers; Java/Kotlin multi-file compilation; Rust modules; HTML with local CSS files. Projects have entry-file selection, arguments, stdin, environment and JVM main-class configuration. Import/export, local persistence and source-file snapshots are implemented. Helper-file edits invalidate old trace associations.

**Inspection/control:** safe Python instance dictionaries/slots without properties; actual bounded C/C++/Rust aggregate fields through GDB, with program function calls disabled during inspection; Python conditional breakpoints and observed-value watches; correct Rust user entry-point stepping and disabled GDB debuginfod downloads.

**Platforms:** public static WebUI with HTTPS runner configuration; Windows portable CPython package; Fedora 43/44 RPM and offline bundles; Ubuntu 24.04 DEB and offline bundle; Android debug APK with system multi-file picker. Installed resources and mutable run data are separate. Desktop WebView storage uses an application profile and a reusable local origin. Browsers with disabled storage keep an in-memory draft and can export it.

**Distribution:** lockfiles, setup/build scripts, CI for Windows/Fedora/Ubuntu/browser/Android, Pages deployment, installation/update/removal guidance, English/Vietnamese guides and the complete original requirement ledger.

## Verification evidence

The local backend release suite has **35 passing tests**, including all eight ISA profiles, changed inputs, compile failures, exact values, cycles/getter traps, six native multi-file language paths, native aggregate fields, HTTPS-origin/auth checks and Python live conditions/watches. Eight Node test groups cover real QuickJS execution, TypeScript diagnostics, modules, replay, graph invariants, project validation, locale keys and empirical-fit behavior.

Browser interaction tests exercise the Pages subdirectory layout, actual neuron edges, fullscreen/fit, TypeScript library types, multi-file trace export and helper-file replay, project persistence, stale-helper detection, HTML/CSS rendering, Vietnamese phone layout and disabled browser storage. They capture actual screenshots, not mockups.

CI runs the same backend suite on Windows, Fedora 43/44 and Ubuntu 24.04. Linux jobs additionally build and install the actual package, execute RISC-V through its launcher from an unrelated directory and test a GTK/WebKit window on Xvfb. Android CI builds and verifies the APK signature. Check the exact run result before attributing success to a commit; job configuration alone is not evidence.

Windows portable ISA checks and Android emulator UI checks are separate from source/backend tests. Package checksums accompany releases. Exact versions discovered in CI appear in its environment artifacts; the direct dependency baseline is `requirements.txt` and `package-lock.json`.

## Remaining acceptance gaps

The original brief is still **incomplete**. All ten named languages have real tested execution/observation paths within documented baselines; arbitrary versions, libraries and projects are not universally supported. Open requirements include:

- Cargo/CMake/Maven/Gradle build-system orchestration beyond source-file projects.
- Verified isolation for compilation and native execution. Trusted mode has normal account access.
- Complete DOM/event bridge and browser-native JS adapter, CSS cascade origin reconstruction.
- Comprehensive heap lifetimes, Rust ownership, variable dependencies and concurrent causal reconstruction.
- Live controls across every adapter, hardware watchpoints, JIT-native and WASM instruction-state stepping.
- All requested static complexity patterns and memory-cost models.
- Physical Fedora SELinux/Wayland and physical Android/Poco acceptance, complete accessibility budgets and release-signing hardening.

No Fedora physical host/VM was available. Container X11 checks are useful but do not remove that limitation. CI's ptrace and WebKit container settings apply only to tests and are not shipped security configuration. No zero-error guarantee is made.

The 100 original paragraph requirements remain intact in [REQUIREMENTS.md](REQUIREMENTS.md) and `requirements.json`; documented gaps remain work to finish rather than accepted substitutions.
