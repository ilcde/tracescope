# TraceScope user guide

TraceScope 0.1 is a working execution workbench, **not a completed implementation of the full product brief**. Read `capabilities.json` and `REQUIREMENTS.md` for exact boundaries.

## Start on this Windows workspace

```powershell
.venv\Scripts\python.exe -m tracescope desktop --trusted-local
```

This opens a native WebView2 application. `--trusted-local` enables Python/JVM/native code with your account's filesystem and network access. It is **not a sandbox**. Omit the flag to keep native execution locked; local browser/WASM mode still works. Do not run untrusted imported projects in trusted mode.

Browser alternative:

```powershell
.venv\Scripts\python.exe -m tracescope serve --trusted-local
```

Open the exact URL printed by the runner; its fragment contains the session token. The token stays in session storage and is sent in an Authorization header. The service binds loopback by default. Stop the runner to revoke its generated token.

Portable Windows build: `packages\TraceScope-Windows\TraceScope.exe desktop --trusted-local`. Keep the entire `TraceScope-Windows` folder together, including `runtime`, `tracescope` and `dist`. Python and emulator libraries are bundled. Java/Kotlin/C/C++/Rust toolchains remain separate prerequisites discoverable on PATH or via `TRACESCOPE_JAVA`, `TRACESCOPE_JAVAC`, `TRACESCOPE_KOTLINC`, `TRACESCOPE_GCC`, `TRACESCOPE_GPP`, `TRACESCOPE_GDB`, `TRACESCOPE_RUSTC`, and `TRACESCOPE_OBJDUMP`.

## Explore a program

1. Choose a language or open a source file. Every example is editable. Java uses `Main.java` / class `Main`; Kotlin uses `Main.kt`.
2. Read the observation boundary above the editor. Set stdin, JSON-array arguments, CPU profile and build mode in Run settings.
3. Run & trace (F5). Real capture happens independently of playback speed. Live Python breakpoints pause before their source line. Other adapters collect bounded logs and then replay.
4. Scrub the timeline or use previous / into / over / out. Step-over/out use captured frame depth where present. During a paused live Python session these buttons issue debugger commands. Missing frame information cannot support real step-over/out semantics.
5. Select a typed value. The inspector displays actual state, previous snapshot, identity and sizes/addresses only where known. Object IDs denote logical identity, not fabricated addresses. Aliases point to the same object ID.
6. Switch diagrams between logical values/objects, the observed source path, and captured call stack. SVG export produces a typed-value snapshot. CodeMirror supports Ctrl+F search and gutter breakpoints.
7. Open Instructions & VM. Python/JVM bytecode, generated JavaScript and native machine code are labelled separately. They are not interchangeable. Source mappings may be missing, especially in optimized code.
8. Export/import a portable JSON trace. Historical navigation never executes code or repeats I/O. Edits do not change the captured source; use the source snapshot button to inspect the old build. Last completed session is persisted in IndexedDB.

## Benchmarks and complexity

Benchmark launches a separate execution. Python statement hooks and native/JVM debuggers are absent in this mode; output capture still has overhead. JVM numbers include cold process startup and are not JMH-quality steady-state benchmarks. Trace timings include inspection and debugger waiting.

The Python static analyzer accepts a restricted side-effect-free scalar/range subset. It can justify constant, linear, independent and triangular loop upper bounds under a unit-cost integer model. Calls, dynamic dispatch, unsupported recursion and changing loop bounds produce **unknown**. It does not infer arbitrary Big O. Memory claims concern scalar slots, not process RSS or integer bit growth.

JavaScript/TypeScript size sweeps feed 16, 64, 256 and 1024 to `input()`, run three separate uninstrumented executions per size, and show median/range and candidate fit errors. Your program must actually use that input as its size. A fit is not proof or a worst-case guarantee.

## Assembly

Profiles: x86-16 real mode (386+ instruction set; no BIOS/DOS), x86-32, x86-64, ARM32 ARM and Thumb, AArch64, RV32I and RV64I teaching baselines. Unicorn executes assembled bytes. Capstone disassembles the same bytes. RISC-V uses the Zig/LLVM integrated assembler and a fixed linker script.

The emulator maps 128 KiB, starts at 0x1000 and initializes the stack at 0xf000. No OS or syscall services exist. Use base registers for x86-64 memory addressing; Keystone's `[absolute]` syntax may assemble RIP-relative operands for some forms. Always inspect the decoded operands. The diagram reports actual register before/after states and memory reads/writes. It is an ISA model, not measured hardware pipelines or CPU cycles. General ELF/PE program loading is not implemented.

## Android

Install `packages/TraceScope-debug.apk`. This is a development-signed, debuggable APK, not a store release. It bundles the frontend and WASM assets. JavaScript, TypeScript, HTML, CSS, editing and replay work locally without a server. Source/trace import uses Android's document picker. Export asks Android to create a document. The last completed trace persists locally; there is no service that keeps a live remote run alive after Android kills the activity.

Run settings accept an HTTPS runner URL and token. The runner must use a certificate trusted by Android and explicit remote bind options:

```powershell
.venv\Scripts\python.exe -m tracescope serve --host 0.0.0.0 --cert runner.pem --key runner-key.pem --token YOUR_RANDOM_SESSION_TOKEN --trusted-local
```

Pairing is manual bearer-token configuration. Native compilation occurs on that runner, never on Android. There is no certificate bypass, automatic device discovery or per-project access-grant UI. Paired TLS/device execution has not yet passed end-to-end acceptance. A desktop browser is not a substitute for this missing verification.

## Troubleshooting

Run `.venv\Scripts\python.exe -m tracescope doctor`. Missing tools are reported explicitly. Native execution stays locked without the trusted flag. A failing compile retains timing and diagnostics. A stopped/quota-limited execution retains its valid partial trace. User code may legitimately raise exceptions or exit nonzero; do not assume every failed status is an adapter failure.

Live capture is bounded to 5,000 events and 24 MB per run, 64 KiB output in instrumented adapters, 120 s runner wall time, and two concurrent sessions. Windows Job objects add a 1 GiB committed-memory limit, 24-process limit and 60 s job CPU limit when assignment succeeds. These controls do not establish isolation. Output quotas on all compiler/benchmark subprocesses are not complete. Only trusted code should use native mode.
