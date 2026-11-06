# Current trust boundary and unfinished isolation

Do not describe this release as a secure native-code sandbox. This is an open mandatory requirement.

- Local JavaScript/TypeScript execute inside a bounded QuickJS WebAssembly VM with no filesystem, network, process or native bridge. VM memory, stack, event, output and wall limits are set. The engine is still a dependency that needs normal security maintenance.
- HTML/CSS render in an opaque sandboxed iframe. CSP disallows network, external resources, forms and user scripts. Only the nonce-bearing snapshot observer runs. Preview messages are accepted only from the specific iframe with a session nonce. Parser and rendering snapshots are separate observations.
- The local runner binds loopback and requires a random per-process bearer token for execution and inspection. Native execution is locked by default. Tokens are not embedded in shipped bundles. The frontend sends the token via Authorization, not query strings.
- Remote listening requires an explicit token and TLS certificate/key. Android origin CORS is explicit. Tokens are scoped to the runner session, not per-project permissions; restarting/replacing the token revokes access. Pairing UX, per-workspace grants and remote device acceptance are incomplete.
- `--trusted-local` gives user programs the runner account's filesystem/network rights. Imported programs, compilers and build scripts are not isolated. Windows Job controls are resource limits, not a security boundary. Linux namespaces/seccomp and a native Windows isolated worker remain unimplemented.
- Windows workers are assigned to a Job with kill-on-close, process-count, committed-memory and CPU limits. Wall time and trace-size quotas are enforced by the parent. Assignment status is recorded. Cancellation terminates the Job/process tree and preserves partial evidence. This is robustness, not protection from hostile code.
- Assembly is freestanding CPU emulation. External-file assembler directives are rejected, but assembler/emulator implementation vulnerabilities are not ruled out. RISC-V compilation runs a real LLVM-derived assembler.
- Debug Android builds deliberately expose WebView debugging for acceptance tests and use a development signing key. Release signing, disabling debug access and distribution hardening remain open. No JavaScript/native interface is exposed to child frames. Android document import/export uses user-mediated document intents.

Never disable SELinux, Windows security features, TLS validation or browser origin protections to make this app run. No source is uploaded to third-party services by default.
