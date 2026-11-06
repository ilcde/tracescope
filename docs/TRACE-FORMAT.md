# TraceScope portable trace v1

`schema: "tracescope/1"`. A run has UUID runId, SHA-256 sourceHash, immutable source snapshot and filename, content buildHash, adapter version, host and target metadata, createdAt, events, artifacts, diagnostics, metrics, status and limitations. No trace data is executable. Import validates source hash, sequence order, quotas and value structure.

Events have zero-based `seq`, decimal-string monotonic `timeNs`, kind, source line (one-based or 0 unavailable), column, thread/task/frame and function, phase, typed values, delta set/remove, and a checkpoint flag every 100 events. All events currently include complete bounded snapshots as well as deltas; checkpoint seeking therefore never needs to re-execute code. Event kinds are backend observations, not a promise that every backend emits all possible kinds.

Every value has `type`, string `value`, explicit `state`, optional identity, bounded children, size and address. Integers and addresses never pass through a JavaScript Number. null/undefined/uninitialized/uncaptured remain different. Object IDs refer to logical identity, not fabricated physical addresses. Source type vs runtime type is not universally available.

Python uses actual frame IDs scoped to the run; JDI supplies JVM frame depth/thread identifiers; GDB frames are inspected per stop. Async causal edges and stable native frame identities are not fully captured. One schedule is one observation.

Machine artifacts have exact buildHash, address, bytes, mnemonic, operands, source line when available. Python bytecode is labelled bytecode. JVM bytecode is javap text. Generated JavaScript is labelled generated source. WASM VM instruction state is not captured.

Replay is reading an immutable log. It never repeats console writes, file writes, network requests, stdin or user code. It is not reverse execution. Source edits invalidate active-source highlighting until rerun; the original snapshot remains exportable.
