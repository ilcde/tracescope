# Baselines, established before implementation

TraceScope is not complete against the full product brief until the requirements ledger and acceptance evidence say so. A working subset does not establish platform-wide support.

| Input | Baseline | Projects and library boundary | Observation |
|---|---|---|---|
| Python | CPython 3.11; verified tracing fallback | .py, workspace imports; standard library; native calls opaque | before-line, calls, returns, exceptions, safe locals; real `dis` bytecode |
| Java | Java/JDK 21 | .java, javac debug metadata, standard library | JDI line steps, frames, locals and object fields; javap bytecode |
| Kotlin | Kotlin/JVM compiler discovered locally, JDK 21 | .kt, stdlib; generated coroutine frames are JVM frames | JDI lines/locals; Kotlin source filename, no claim of reconstructed coroutine state |
| C / C++ | C17 / C++17 GCC or Clang + GDB | single file and explicitly supplied companion sources; CMake integration pending | GDB MI source steps, locals, addresses, binary disassembly |
| Rust | stable rustc + GDB | .rs; Cargo integration pending | DWARF steps, locals; ownership explanations are static, not observed moves |
| JavaScript | QuickJS 0.32.0 package WASM engine, ES2020 teaching subset | one script, functions, loops, closures, promises; no Node APIs | AST-inserted before-statement snapshots; bounded descriptor inspection |
| TypeScript | TypeScript 5.9.2, target ES2020 | same runtime boundary, real type checking | original source coordinates preserved by transformer; runtime types distinct |
| HTML | browser HTML parser + tree-sitter HTML WASM grammar | one HTML document, network blocked | static WASM syntax + real DOM/computed-style snapshot; no invented per-line execution |
| CSS | browser CSS engine + tree-sitter CSS WASM grammar | stylesheet applied to a controlled HTML document | static WASM syntax + real computed styles and boxes; no browser-internal timing |
| Assembly | Unicorn 2.1.4, Capstone 5.0.6, Keystone 0.9.2 / external assembler | freestanding bounded code, no OS/syscalls | actual instruction stepping, register and memory writes |

All versions will be recorded in run provenance. Compile/trace and benchmark are separate executions. No native JIT code is claimed. Android uses bundled web/WASM logic locally; heavyweight backends require an authenticated HTTPS runner. APK build and physical-device acceptance are separate states.

Host-native execution is disabled by default until an isolation boundary is available, or the operator explicitly starts a trusted-development runner. This opt-in is not a sandbox. Process quotas alone do not meet isolation acceptance.
