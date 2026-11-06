# Adapter SDK v1

An adapter exposes `run(config, emit)` in an isolated worker. It must discover its actual toolchain, build the supplied source, emit build identity/artifacts, then emit observed events and terminal status. Capabilities are advertised separately in `capabilities.json`; add no language without a real source/input modification test.

Configuration: `language`, `source`, generated `filename`, generated `workdir`, `stdin`, `args`, `buildProfile` (`learn`/`optimized`), `mode` (`trace`/`benchmark`), `maxEvents`, and optional architecture `profile`. Never accept shell command strings from a client. Compilers/build systems are untrusted workloads and need the same isolation as execution.

Transport is UTF-8 JSON Lines on the worker stdout. `{"event": ...}` adds an immutable observation. `{"artifacts": [...]}` attaches exact build products. `{"metrics": {...}}` merges actually measured phases. Final packets use `status` = completed, failed, truncated or cancelled, and a termination/diagnostic if applicable. Python accepts JSON control commands on the original stdin: pause, continue, stepInto, stepOver, stepOut, runTo with line, stop. Other adapters must reject live control; historical navigation is separate.

Inspection must not invoke user code. Declare accessor/proxy/native boundaries. Use strings for exact integers, addresses and monotonic nanoseconds. Limit event bytes, traversal depth and children. Cleanup must terminate the entire process tree. Build output, source and disassembly must share a content hash.

## Adding an adapter

1. Define and document a stable runtime, project and library baseline.
2. Implement discovery/build/launch/inspection in a separate worker module.
3. Add a capability entry with implementation and verification independently recorded.
4. Register the module in worker/service and the frontend language registry.
5. Add headless and UI integration tests with changed source and changed input, plus an uninstrumented comparison.
6. Declare unsupported controls; never silently translate instruction-step into source-step.

The current SDK is synchronous worker streaming, not a full DAP implementation. Arbitrary third-party adapters, dynamic discovery, separate pause/inspect interfaces and multi-file project adapters remain gaps.
