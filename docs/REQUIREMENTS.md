# Requirements ledger

100 stable paragraph-level requirements retained from the complete brief. **Product acceptance: incomplete.**

Implementation and verification are separate. `limited` means a useful subset exists, not that the paragraph is accepted. `untested` here means the complete paragraph has not passed acceptance; individual working baselines have actual evidence in `capabilities.json` and `evidence/`. Fedora 43/44 and Ubuntu 24.04 now have GitHub Actions backend and packaging jobs. Physical Fedora SELinux/Wayland acceptance still needs a host/VM.

## Delivered, individually verified slices

- All ten named language baselines have real execution/observation paths. Python, Java, Kotlin, C, C++, Rust, JavaScript and TypeScript have modified-source/input evidence. HTML/CSS use actual WASM syntax and browser rendering.
- Eight ISA/mode profiles pass register, memory, branch and call tests. x86-16 is real mode on a 386+ instruction set, not a claim of a cycle-accurate 8086 machine.
- Immutable replay, exact large integers, safe bounded object inspection, Python live pause/step, per-build native disassembly, optimized-out native values, measured phases, a conservative complexity subset, bilingual UI, Windows native window and Android emulator local WASM.

## Open completion gate

Build-system orchestration beyond the implemented multi-file source projects; true isolation of compilation and native execution; authenticated paired-device TLS acceptance; full DOM/event bridge; browser-native JS adapter; WASM/JIT instruction state; complete heap lifetimes, ownership and dependency graphs; conditional controls beyond Python and hardware watchpoints; multi-thread causal reconstruction; all requested static complexity patterns; physical Linux desktop/security acceptance; physical Android/Poco testing and comprehensive accessibility/rendering budgets remain open.

## Updates in 0.2

- TS-04: multi-file projects across the named execution adapters, project persistence, source-file replay, environment/entry configuration and all-language editor modes are implemented; build-system orchestration remains open.
- TS-06: Python conditional breakpoints and observed-value watches now accompany live stepping; other backends still use captured replay.
- TS-07: fullscreen typed neuron diagrams, identity-aware references, readable phone layout and real SVG export are implemented. Python instance storage/slots and native aggregate fields feed the graph. Ownership and complete data-dependency reconstruction remain open.
- Distribution: public repository and WebUI deployment, CI Windows/Fedora/Ubuntu/Android jobs, Windows ZIP, Fedora RPM, Ubuntu DEB and Android APK build paths now exist. Exact pass/fail evidence is in [Actions](https://github.com/ilcde/tracescope/actions/workflows/verify.yml).

## Product goal and complete scope

- [ ] **TS-01.01** — limited / untested: The user must be able to write or import code, compile or launch it, step through actual execution, and simultaneously understand:

- [ ] **TS-01.02** — limited / untested: - The current source statement and its control-flow path. - Variable types, values, references, lifetimes, and changes. - Function calls, stack frames, heap objects, and data structures. - The corresponding bytecode, intermediate representation, or machine instructions, clearly distinguished. - Assembly instruction effects on registers, memory, branches, and the stack. - Compilation time, execution time, memory use, and justified time/space complexity analysis.

- [ ] **TS-01.03** — limited / untested: Mandatory named languages: Python, Java, C, C++, Rust, Kotlin, JavaScript, TypeScript, HTML, and CSS. JavaScript and CSS are explicit requirements even when used alongside HTML. Implement an adapter SDK for additional languages; do not claim universal language support merely because an SDK exists.

- [ ] **TS-01.04** — limited / untested: Mandatory operating systems: Fedora Linux first, other major Linux distributions, Windows, and Android. Mandatory assembly families: x86, ARM, and RISC-V, with usable 32-bit and 64-bit profiles. Investigate and implement a genuine x86 16-bit teaching mode where feasible. Design extensibly for wider registers, data representations, and future architecture profiles without inventing unsupported CPUs.

- [ ] **TS-01.05** — limited / untested: English and Vietnamese must cover the whole learning experience. Every data-bearing diagram node must visibly identify its data type. All these requirements belong to the product scope; do not silently remove difficult requirements or call an incomplete MVP finished.

## Establish an honest capability contract

- [ ] **TS-02.01** — limited / untested: Create a requirements checklist with stable IDs and a machine-readable capability matrix. Track language, runtime/version, host platform, target ISA, ABI, execution mode, tracing granularity, type inspection, memory inspection, assembly visibility, and test evidence.

- [ ] **TS-02.02** — limited / untested: Distinguish implementation status from verification status. States must include implemented, limited, unavailable, blocked, tested, and untested where appropriate. Explain limitations in the UI before the user starts a run. A disabled selector, syntax highlighting, successful cross-compilation, or a prerecorded example does not constitute execution support.

- [ ] **TS-02.03** — limited / untested: Support every named language through a real end-to-end path. Describe which combinations use local execution, emulation, or a paired runner. Do not imply that every language can be compiled directly into every ISA or that every desktop backend runs locally on Android. A documented gap remains a gap; the matrix must not become an excuse to abandon requested features.

- [ ] **TS-02.04** — limited / untested: Before implementation, define a concrete baseline for every named language: supported stable language/runtime versions, core features, standard-library boundaries, project/build formats, and observable event granularity. Each baseline must accept user-written programs and changed inputs with genuine source-to-trace synchronization. Bundled examples alone are insufficient. Retain every named language without promising support for every existing version, library, and application.

- [ ] **TS-02.05** — limited / untested: Use current official documentation and verify dependencies against the actual environment. Pin compatible versions and record meaningful architecture decisions. Prefer mature compilers, runtimes, debuggers, and emulators over reimplementing entire ecosystems.

## Architecture and integration

- [ ] **TS-03.01** — limited / untested: Use a modular architecture separating editor/UI, static analysis, execution adapters, trace transport/storage, replay, diagram rendering, benchmarking, and complexity analysis.

- [ ] **TS-03.02** — limited / untested: A strong default is a Rust execution/service core, a TypeScript frontend, and Tauri 2 for desktop/mobile packaging, provided practical compatibility tests validate the choice. React and a suitable graph renderer/layout engine are reasonable. Select another stack if necessary to satisfy actual platform requirements, documenting the decision. Do not assume desktop sidecars work unchanged on mobile.

- [ ] **TS-03.03** — limited / untested: Implement three distinct observation layers:

- [ ] **TS-03.04** — limited / untested: 1. Static structure from parsers, type checkers, compiler metadata, and control-flow analysis. 2. Real execution observations from debuggers, runtime hooks, agents, or instrumentation. 3. Actual low-level artifacts and execution from compiler output, VM tooling, native debugging, or emulation.

- [ ] **TS-03.05** — limited / untested: Interpret “injection into compilers, interpreters, and VMs” as documented compiler passes, build wrappers, debugger interfaces, interpreter monitoring, and runtime agents used within user-launched or explicitly selected sessions. Do not globally patch toolchains or attach to unrelated processes.

- [ ] **TS-03.06** — limited / untested: Provide clean adapter interfaces for capabilities, toolchain discovery, build, launch, pause, continue, step, inspection, trace streaming, cancellation, and cleanup. DAP may standardize appropriate debugger operations, but add explicit extensions where its standard requests cannot express the required data.

## Editor and project workflow

- [ ] **TS-04.01** — limited / untested: Provide a real editor with syntax highlighting, diagnostics, search, configurable fonts, line numbers, breakpoints, stdin, arguments, environment settings, and run configurations. Support single files and multi-file projects, imports/modules, and representative CMake, Cargo, Python, JVM, and web build workflows.

- [ ] **TS-04.02** — limited / untested: Show compiler errors with source locations. Keep generated files separate from source. Store project settings and session state. Support opening/saving files on desktop and Android through the platform's supported file access APIs.

- [ ] **TS-04.03** — limited / untested: Offer learning/debug and optimized build profiles. Source, binary, debug information, disassembly, and runtime trace must reference the same identified build. Editing source invalidates its association with old traces; retain old traces with their original source snapshots.

## Trace semantics and reliable state

- [ ] **TS-05.01** — limited / untested: Define a versioned, portable trace schema containing run ID, source/build hashes, adapter/toolchain versions, host and target information, sequence IDs, monotonic timestamps, source spans, thread/task/frame IDs, event kind, and state deltas.

- [ ] **TS-05.02** — limited / untested: Represent before-statement, after-statement, call, return, branch, exception, allocation, deallocation, mutation, I/O, and scheduling events when the backend can observe them. State clearly whether the highlighted line is about to execute or has completed. Account for multiple statements per line, multiline statements, short-circuit evaluation, loops, recursion, and exceptional exits.

- [ ] **TS-05.03** — limited / untested: Every runtime value, executed edge, and instruction highlight must come from execution evidence. Static possibilities and observed execution paths must look different. Do not derive runtime values from an LLM or invent missing transitions between snapshots.

- [ ] **TS-05.04** — limited / untested: Preserve exact 64-bit addresses and integers, larger integers, and special floating-point values in transport and storage. Avoid lossy conversion through JavaScript Number. Record unavailable, optimized-out, uninitialized, freed, stale, truncated, and uncaptured data as explicit states.

- [ ] **TS-05.05** — limited / untested: Use bounded object traversal and stable identities for aliases and cycles. Inspection must not silently execute getters, repr, toString, or expressions that mutate the program.

## Execution controls and replay

- [ ] **TS-06.01** — limited / untested: Implement run, pause, stop, restart, step into/over/out, source-step, instruction-step, run to cursor, and supported conditional breakpoints/watchpoints. Explain backend restrictions instead of silently ignoring a request.

- [ ] **TS-06.02** — limited / untested: Support live tracing and post-run playback. Provide speed controls, timeline scrubbing, bookmarks, event search, loop-iteration grouping, and filters for threads/tasks/functions. Keep live execution position separate from the historical position being viewed.

- [ ] **TS-06.03** — limited / untested: Implement backward navigation using an immutable event log, deltas, and periodic checkpoints. Replaying historical state must not repeat file writes, network requests, console emissions, or input prompts. True reverse execution is a separate capability-dependent feature; do not imply that visual replay rewinds the external world.

- [ ] **TS-06.04** — limited / untested: Preserve the observed order of asynchronous and concurrent events and any known causal relationships. Explain that a captured schedule is one execution. Do not claim deterministic re-execution without recording the required inputs and scheduling information.

- [ ] **TS-06.05** — limited / untested: Stream in batches, apply backpressure, and bound trace size. If sampling or event loss occurs, visibly mark it. Animation speed must not control the program's measured execution time.

## Diagrams and type-rich nodes

- [ ] **TS-07.01** — limited / untested: Implement synchronized views for control flow, executed paths, call stacks, call graphs, stack/heap memory, variable dependencies, and common data structures. Arrays, strings, matrices, linked lists, trees, maps, sets, and graphs should have useful views when their structure is known; show raw object structure otherwise.

- [ ] **TS-07.02** — limited / untested: Each data node should show name, value, and type without requiring a tooltip. Its expandable details should include declared/inferred source type, runtime type, previous value, scope, frame, identity, size, address/offset, signedness, encoding, alignment, and lifetime where applicable and observable.

- [ ] **TS-07.03** — limited / untested: Use typed relationships for contains, references, points-to, aliases, owns, and borrows. Never duplicate an aliased object as if it were independent. Separate null, undefined, uninitialized, out-of-scope, freed, and unavailable.

- [ ] **TS-07.04** — limited / untested: Do not pretend every node is a programming variable: control-flow nodes need statement/category labels; DOM nodes need element/node types; CSS nodes need property/value categories and units. Registers contain raw bits with an explicitly selected interpretation, not an inherently known source-language type.

- [ ] **TS-07.05** — limited / untested: Show decimal, hexadecimal, binary, and suitable floating-point/character views. Make actual target width and byte order visible. Unknown sizes or addresses must remain unknown. Clearly identify logical object graphs versus observed memory layouts.

## Native languages: C, C++, and Rust

- [ ] **TS-08.01** — limited / untested: Integrate actual Clang/GCC and rustc/Cargo toolchains with debug information and LLDB/GDB or equally capable backends. Use compiler instrumentation when it supplies data unavailable through normal debugging. Integrate Rust-aware inspection and C++ object/container inspection.

- [ ] **TS-08.02** — limited / untested: Support stack/heap allocations, pointers and pointer arithmetic, arrays, structs, classes, enums, function calls, references, recursion, and meaningful lifetime transitions. Represent Rust moves/borrows/drops from justified compiler/runtime information; distinguish static ownership explanations from runtime observations.

- [ ] **TS-08.03** — limited / untested: Show assembly from the exact generated binary, with symbols and source mappings. Include compiler IR where genuinely available. Support debug-friendly and optimized builds, explaining inlining, reordering, elided statements, and optimized-out values. Never animate one build using another build's disassembly.

- [ ] **TS-08.04** — limited / untested: Use sanitizer-assisted runs where supported to explain relevant memory/undefined-behavior failures. Do not claim that all undefined behavior is detectable or assign invented deterministic semantics after an invalid operation.

## Python, Java, and Kotlin

- [ ] **TS-09.01** — limited / untested: Python: use actual CPython monitoring/debugging facilities, such as sys.monitoring on compatible versions and a verified tracing fallback. Capture frames, locals, objects, calls, exceptions, generators, and coroutines at the supported granularity. Show real Python bytecode in a separate VM view. Clearly mark native-extension observation boundaries.

- [ ] **TS-09.02** — limited / untested: Java: compile with useful debug metadata and use JDI/JVMTI or suitable agents to observe actual JVM execution. Show locals, object identity, fields, calls, exceptions, threads, allocation/GC events where observable, and real JVM bytecode.

- [ ] **TS-09.03** — limited / untested: Kotlin: provide a complete Kotlin/JVM path with source mappings for generated code, lambdas, nullability, and coroutine state machines. Treat Kotlin/Native, Kotlin/JS, and Kotlin/Wasm as separately verified backends, not interchangeable labels. Add them where feasible without substituting them for Kotlin/JVM support.

- [ ] **TS-09.04** — unavailable / untested: For interpreted and VM languages, keep source, bytecode, interpreter-native execution, and JIT-native code distinct. Capture actual native JIT code only through supported runtime tooling, with method identity, compilation generation, target, inlining, and deoptimization information. Native JIT instruction stepping must have its own verified capability.

- [ ] **TS-09.05** — limited / untested: If native assembly is unavailable, explain why and show the actual available layer. Never rename bytecode as x86/ARM/RISC-V assembly, or present the interpreter's machine code as a direct compilation of the user's function.

## HTML, CSS, JavaScript, TypeScript, and mandatory WebAssembly integration

- [ ] **TS-10.01** — limited / untested: Make WebAssembly a meaningful part of this pipeline, not a decorative demo. Implement a real WASM-backed execution/analysis mode and document exactly what runs inside WASM versus the host browser.

- [ ] **TS-10.02** — limited / untested: For JavaScript, a suitable approach is an instrumented embeddable JavaScript engine compiled to WASM. Validate tracing hooks and language compatibility before committing to an engine. This is JavaScript running through a VM hosted in WASM; do not claim arbitrary JavaScript automatically becomes equivalent native WASM instructions.

- [ ] **TS-10.03** — limited / untested: For TypeScript, use a real compiler/type checker, preserve source maps, and execute the resulting JavaScript through the chosen runtime. Keep static TypeScript types distinct from observed runtime types. Test errors, closures, async functions, promises, and event-loop behavior.

- [ ] **TS-10.04** — limited / untested: For HTML/CSS, use WASM-backed parsing/analysis or another substantial stage implemented in WASM for both HTML and CSS, alongside an isolated real browser rendering surface and a controlled host bridge. Visualize DOM construction, CSS rules, cascade/specificity, inheritance, computed styles, box model, layout, and observable rendering changes with source mappings.

- [ ] **TS-10.05** — limited / untested: HTML and CSS are declarative inputs; do not fake ordinary statement execution for each source line. Let users step through observed parsing/mutation/style/layout events, with honest granularity and missing-event labels. Do not invent browser-internal paint/layout timings when the platform does not expose them.

- [ ] **TS-10.06** — limited / untested: For embedded WASM JavaScript, implement and test a documented DOM/event bridge; identify unsupported APIs. Also provide a browser-native execution adapter for full browser behavior where feasible, keeping its execution path visibly distinct. A partial DOM bridge must not be marketed as complete browser compatibility.

- [ ] **TS-10.07** — limited / untested: Show actual WASM disassembly/WAT, VM state, operand-stack/linear-memory changes where the selected backend exposes them. Obtaining instruction-level WASM state may require an instrumented interpreter; a normal browser cannot be assumed to expose it. Machine code produced by a WASM runtime is a separate, provenance-tagged view when truly accessible.

## Assembly architectures and instruction visualization

- [ ] **TS-11.01** — limited / untested: Deliver real profiles for x86-32, x86-64, ARM AArch32 including relevant ARM/Thumb modes, ARM AArch64, RISC-V RV32, and RISC-V RV64. Record CPU model, extensions, endianness, ABI, and calling convention. Use cross-toolchains plus matching hardware or a mature emulator such as QEMU or another validated engine.

- [ ] **TS-11.02** — limited / untested: Support both loading generated executables and editing/running small assembly examples. A disassembler only decodes instructions; it is not an execution engine. Cross-compilation requires valid target libraries/sysroots where applicable and is not proof of successful execution.

- [ ] **TS-11.03** — limited / untested: For each observed instruction, display its address, bytes, mnemonic, operands, source relationship, and before/after effects on registers and memory. Visualize reads, writes, loads/stores, address calculation, arithmetic, comparisons, branches, calls, returns, stack frames, and relevant flags/status. Respect architectures that do not use x86-style condition flags.

- [ ] **TS-11.04** — limited / untested: Provide Intel and AT&T syntax for x86, with correct source/destination explanation. Distinguish assembler directives, pseudo-instructions, debug/unwind metadata, and executed machine instructions.

- [ ] **TS-11.05** — limited / untested: Provide a conceptual register/ALU/memory diagram that explains data movement. Loads and stores copy values; they do not generally swap a register with RAM or erase the source. Label this as an ISA-level educational model, not measured physical pipeline/cache/micro-operation behavior.

- [ ] **TS-11.06** — limited / untested: Source-to-instruction mappings are many-to-many and may be missing or discontinuous. Navigation must preserve that fact. Comparing two architectures means two separately compiled/executed artifacts, not replacing register names in the same trace.

- [ ] **TS-11.07** — limited / untested: Investigate a genuine x86 16-bit real-mode emulator profile and implement it where feasible, clearly specifying its environment and limitations. ARM Thumb and RISC-V compressed 16-bit instruction encodings must not be mislabeled as 16-bit CPU architectures. Do not confuse SIMD/vector widths or 128-bit data types with general-purpose CPU bitness. Wider architecture profiles require actual backend support and tests.

## Compilation and runtime performance

- [ ] **TS-12.01** — limited / untested: Provide separate Trace/Learn and Benchmark modes. Benchmark runs must be genuinely separate executions without visualization instrumentation where feasible. Never report animation duration or debugger waiting as ordinary program performance, and never subtract a guessed overhead constant to fabricate native speed.

- [ ] **TS-12.02** — limited / untested: Measure compiler/transpiler elapsed time, linking where separately observable, startup, VM initialization/JIT warmup where observable, execution wall time, and process CPU time using appropriate monotonic clocks. Show compile errors and time spent before failure.

- [ ] **TS-12.03** — limited / untested: Display live elapsed counters and a final phase timeline. Only subdivide phases for which instrumentation exists; report an aggregate otherwise. Keep compilation, trace collection, transport, and UI playback separate. Measure remote execution on the runner and show network latency separately.

- [ ] **TS-12.04** — limited / untested: Record input, compiler/runtime versions, flags, optimization profile, host hardware, target architecture, cold/warm state, repetitions, and build identity. Show median and spread for repeated measurements. Use an appropriate JVM benchmarking approach with warmup; explain benchmark harness overhead for short programs.

- [ ] **TS-12.05** — limited / untested: Show per-function/line hotspots only at the granularity actually measured. Distinguish sampling from exact tracing and self time from inclusive time. Avoid double-counting nested calls or parallel compile stages.

- [ ] **TS-12.06** — limited / untested: Report memory metrics with precise meanings: tracked allocations, peak live tracked bytes, stack depth, process RSS, and runtime-managed heap are different quantities. Emulator elapsed time is host emulation cost, not target CPU latency; instruction counts are not physical CPU cycles.

## Big O time and space complexity

- [ ] **TS-13.01** — limited / untested: Implement a substantive analysis feature, not a hardcoded badge. Separate asymptotic reasoning, observed operation counts, and measured performance.

- [ ] **TS-13.02** — limited / untested: Every result must be labeled as a justified bound under stated assumptions, a static estimate, an empirical fit, or unknown. Automatic exact complexity inference for arbitrary programs is not a universal capability. Unknown is the correct answer when the analyzer cannot justify a conclusion.

- [ ] **TS-13.03** — limited / untested: Identify input-size variables such as n, m, vertices, edges, or recursion depth. Show the cost model and relevant assumptions, source ranges, loop bounds, library-operation costs, or recurrences. Distinguish worst, best, average, and amortized cases only when justified. Do not classify complexity by counting nested loops alone.

- [ ] **TS-13.04** — limited / untested: Support useful analyzable patterns: constant work, scans, independent loops, halving loops, triangular loops, two-pointer traversal, divide-and-conquer recursion, memoization, and documented amortized container operations. Make limitations explicit for input-dependent recursion, dynamic dispatch, external calls, and unknown library costs.

- [ ] **TS-13.05** — limited / untested: Provide controlled experiments over multiple input sizes, recording operation counts, elapsed time, and memory. Plot samples and candidate growth curves with sample counts, fit error, and uncertainty. An empirical fit must not be called a proof of Big O or a universal worst-case bound.

- [ ] **TS-13.06** — limited / untested: For space complexity, distinguish auxiliary live space from input/output storage, recursion-stack use, total bytes allocated, retained objects, and VM/process overhead. State whether output storage is counted. Explain variable-width integer costs where relevant to the chosen model.

- [ ] **TS-13.07** — limited / untested: For HTML/CSS, do not assign a universal algorithmic Big O to a document. Analyze a specifically defined operation and input measure, show empirical scaling, or report not applicable/unknown with a helpful explanation. Provide bilingual reasoning for every analysis state.

## Visual design and interaction quality

- [ ] **TS-14.01** — limited / untested: Create a polished learning tool with a coherent design system, clear typography, restrained colors, consistent spacing, well-designed icons, light/dark themes, and strong contrast. Avoid decorative clutter and generic dashboard panels that compete with the code.

- [ ] **TS-14.02** — limited / untested: Desktop layout: source editor on the left, primary diagram centrally, inspector on the right, and synchronized assembly/VM visualization underneath. Panels must be resizable, collapsible, dockable where practical, and usable at small desktop sizes. Include focused beginner and advanced modes.

- [ ] **TS-14.03** — limited / untested: Use stable node placement, sensible edge routing, selection pinning, zoom/pan, fit-to-selection, search, and grouping. Animations must explain actual changes: highlight the executed edge, show value updates, and animate relevant data movement. Do not rearrange the entire graph on every step.

- [ ] **TS-14.04** — limited / untested: Make graph detail progressive. Compact nodes retain type and value; expanded inspectors expose the deeper information. Avoid tiny unreadable text and overlapping labels. Support reduced motion, keyboard navigation, screen-reader descriptions, and color-independent meaning.

- [ ] **TS-14.05** — limited / untested: Android needs a touch-first arrangement with tabs/bottom sheets, comfortable controls, pinch zoom, portrait/landscape layouts, keyboard-safe editing, and lifecycle recovery. Verify tall phone layouts, including a Poco X6 Pro-sized viewport when available. Do not squeeze the desktop four-pane layout into an unreadable phone screen.

- [ ] **TS-14.06** — limited / untested: Set and measure rendering/trace budgets on named hardware. Use incremental layout, background workers, virtualization, and bounded visible graphs. Aim for smooth interaction; report actual measurements rather than claiming universal 60 FPS.

## English and Vietnamese

- [ ] **TS-15.01** — limited / untested: Localize menus, dialogs, onboarding, tooltips, graph explanations, type-state descriptions, diagnostics guidance, assembly instruction explanations, complexity reasoning, accessibility labels, and bundled lessons.

- [ ] **TS-15.02** — limited / untested: Allow language switching without restarting or losing execution state. Use natural Vietnamese with correct diacritics and fonts. Maintain a consistent technical glossary. Preserve identifiers, syntax, register names, and original compiler messages, adding localized explanations beside them where possible.

- [ ] **TS-15.03** — limited / untested: Generate core explanations from trace-backed rules/templates. Core operation must work without an LLM, API key, paid service, or internet translation. Optional AI assistance must never fabricate execution evidence or be required for promised functionality.

## Fedora, Linux, Windows, and Android delivery

- [ ] **TS-16.01** — blocked / untested: Fedora is the primary development and acceptance environment. Provide a reliable setup/doctor command checking actual packages, toolchains, debuggers, emulators, graphics dependencies, permissions, and versions. Verify current Fedora package names rather than assuming Ubuntu commands apply.

- [ ] **TS-16.02** — blocked / untested: Test normal Fedora operation with SELinux enabled, Wayland where available, and an X11 fallback. Use narrowly scoped permissions. Never instruct the user to disable SELinux or global security protections as the normal solution. Provide an RPM and a practical portable distribution when build tooling allows.

- [ ] **TS-16.03** — blocked / untested: Support representative Ubuntu/Debian and another major Linux distribution with documented prerequisites and reproducible builds. Avoid glibc compatibility claims without testing the intended baseline.

- [ ] **TS-16.04** — limited / untested: Windows must have a native application, functioning native execution paths, and an installer or portable package. WSL may be an additional backend; it must not silently replace the Windows requirement.

- [ ] **TS-16.05** — limited / untested: Android must have an installable APK and usable local functionality: bundled supported WASM/embedded execution, assembly learning modes where feasible, editing, and offline replay. Use supported Android/NDK APIs and file access. Do not require root or assume unrestricted desktop process launching/ART instrumentation.

- [ ] **TS-16.06** — limited / untested: Implement authenticated pairing with the user's Fedora/Windows runner for heavyweight or unavailable local backends. Android must be able to operate all named language workflows through the supported local or paired route. Clearly show where compilation/execution happens, connection state, and offline limits. A remote route must not be labeled local support, and a remote-only shell does not fulfill the required local functionality.

## Execution isolation and robustness

- [ ] **TS-17.01** — limited / untested: Treat imported programs, projects, build scripts, compiler plugins, annotation processors, package scripts, and trace files as untrusted inputs. Isolate compilation as well as execution.

- [ ] **TS-17.02** — limited / untested: On Linux, implement a verified unprivileged isolation design using appropriate namespaces/containers, filesystem restrictions, resource controls, and filtering. On Windows, provide a real isolation boundary or an explicitly identified isolated worker; process limits alone are not a sandbox. Document and test each platform's boundary.

- [ ] **TS-17.03** — limited / untested: Disable network and broad filesystem access by default; grant scoped capabilities when a project needs them. Set CPU, wall-time, memory, process-count, output, and trace quotas. Cancellation must terminate the whole execution process tree and clean temporary resources.

- [ ] **TS-17.04** — limited / untested: Keep user web previews separate from the privileged application origin and native IPC. Restrict bridge APIs and escape untrusted labels/output. Remote pairing must use authenticated encrypted transport, scoped workspace access, and revocable sessions. Do not upload source to third parties by default.

- [ ] **TS-17.05** — limited / untested: Recover cleanly from compilation errors, runtime exceptions, debugger crashes, corrupt traces, disconnections, infinite loops, and resource exhaustion. Preserve a valid partial trace with a clear termination reason when possible.

## Verification that proves the product works

- [ ] **TS-18.01** — limited / untested: Build meaningful unit, integration, end-to-end, and visual checks around the actual risks. Include a real execution suite for every named language and every claimed assembly profile. Test modified inputs/source, not only bundled demos.

- [ ] **TS-18.02** — limited / untested: Required acceptance journeys:

- [ ] **TS-18.03** — limited / untested: - Edit and run an ordinary program in each language; confirm changed input changes real trace state and final output. - Compare deterministic traced runs against uninstrumented baselines for output, exit status, and relevant results. - Verify recursion, aliasing/cycles, short-circuit evaluation, exceptions, async ordering, and values beyond 2^53 where applicable. - Demonstrate native source-to-instruction mapping and at least one optimized-out/unavailable case. - Execute meaningful examples on x86-32/64, ARM32/64, and RISC-V32/64; verify registers, loads/stores, calls, and branches against a trusted backend. - Demonstrate that the web mode genuinely uses WASM and that DOM/CSS results agree with the chosen supported browser behavior. - Scrub backward across I/O without repeating external side effects. - Show successful compile/run timings, a compilation failure, and an appropriately separated benchmark. - Show justified complexity examples, empirical results, and an example whose correct result is unknown. - Test cancellation, excessive output, runaway allocation, process cleanup, and malformed trace input. - Switch English/Vietnamese during a session and inspect layouts for overflow and missing translations. - Install and exercise Fedora with SELinux enabled, native Windows, and Android local/paired modes.

- [ ] **TS-18.04** — limited / untested: Capture actual logs, screenshots, or short recordings for key journeys. State hardware, OS, runtime versions, commands, and outcomes. Build success is not runtime verification; cross-compilation is not device testing. Never fabricate screenshots, test results, compatibility, or security assurances.

## Workflow, artifacts, and completion gate

- [ ] **TS-19.01** — limited / untested: Begin with repository/environment inspection and short feasibility spikes for the riskiest adapters, especially Android, WASM tracing, JVM/JIT visibility, and cross-ISA execution. Establish one genuine vertical slice early, then continue through all mandatory language/platform work rather than stopping at that slice.

- [ ] **TS-19.02** — limited / untested: Work in reviewable milestones: execution protocol and native slice; language adapters; architecture/assembly views; web/WASM pipeline; performance/complexity; mobile and packaging; visual refinement and full acceptance. Adapt ordering to discovered dependencies without dropping requirements.

- [ ] **TS-19.03** — limited / untested: Maintain the checklist, capability matrix, architecture notes, reproducible setup/build scripts, and test evidence as you implement. Make routine decisions autonomously. Ask only when credentials, inaccessible hardware, permissions, or a genuinely consequential unresolved choice prevents progress. Continue independent work while a specific capability is blocked.

- [ ] **TS-19.04** — limited / untested: Deliver complete source, dependency lockfiles, setup/doctor scripts, runnable builds/packages where possible, adapter documentation, trace format documentation, example projects, and English/Vietnamese user guides. Include a headless CLI for repeatable tracing/verification and portable trace export/import. Provide useful diagram image/vector export where feasible.

- [ ] **TS-19.05** — limited / untested: The final report must give exact launch/build commands, artifact paths, verified platforms, implemented features, evidence, and remaining limitations. Do not claim completion while a mandatory requirement is merely planned, mocked, or untested. If an environment prevents a required verification, identify the exact missing prerequisite and status truthfully rather than inventing success.

- [ ] **TS-19.06** — limited / untested: Start implementing now. The requested result is a working, visually excellent educational execution tool whose diagrams explain real program behavior.
