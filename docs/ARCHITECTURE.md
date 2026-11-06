# Architecture decisions

1. Python service, TypeScript/React client, pywebview desktop shell. The inspected host has CPython 3.11, Node 24, JDK 21, Android SDK, but no Rust toolchain on PATH. A Python service makes the debugger and CPU emulator integrations directly testable. Tauri is not assumed viable without its native prerequisites.
2. One portable schema separates static artifacts, observed events and low-level artifacts. Immutable snapshots plus deltas/checkpoints support side-effect-free replay; the live run and historical cursor are independent.
3. QuickJS is an actual WASM-hosted VM. Instrumentation observes source statements, not WASM instructions. HTML and CSS use WASM grammars for analysis and a sandboxed browser frame for actual rendering.
4. Native execution is a separate trust boundary. Local trusted development is explicit. The service binds loopback by default and requires a per-process bearer token for execution. Remote listening requires TLS and explicit configuration. No compiler plugins or project scripts are run implicitly.
5. Assembly examples are freestanding emulator programs. They are not operating-system executables or physical-cycle simulations. Each architecture has its own actual assembled bytes and emulator state.
6. Windows portable delivery uses a small native launcher and a bundled ordinary CPython runtime, isolated from global Python imports with `python311._pth`. An attempted PyInstaller build crashed Unicorn with exit `0xC0000409`, matching its documented CFG incompatibility. The replacement passed packaged Python and RISC-V runs. System mitigation settings are unchanged. WebView2 must run on the normal interactive desktop.

## Consulted official references

- https://docs.python.org/3.11/library/sys.html#sys.settrace — line hook semantics and audit-hook limitations
- https://docs.oracle.com/en/java/javase/21/docs/api/jdk.jdi/module-summary.html — JDI inspection
- https://github.com/justjake/quickjs-emscripten — WASM lifecycle, limits, pending jobs
- https://www.typescriptlang.org/docs/handbook/2/basic-types.html — erasure and type checking
- https://clang.llvm.org/docs/CrossCompilation.html — target sysroot requirements
- https://doc.rust-lang.org/rustc/codegen-options/index.html — debug/codegen options
- https://www.unicorn-engine.org/docs/ — real CPU emulation
- https://v2.tauri.app/start/prerequisites/ — desktop/mobile prerequisites
- https://source.android.com/docs/core/runtime/art-ti — Android runtime restrictions
- https://github.com/unicorn-engine/unicorn/issues/2281 — Windows Unicorn/CFG incompatibility
- https://pyinstaller.org/en/stable/common-issues-and-pitfalls.html — frozen-runtime compatibility and process environment considerations
