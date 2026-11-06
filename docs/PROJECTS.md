# Multi-file projects

Use **Open source** to select multiple files, or open a portable `tracescope-project/1` JSON file. The file tabs edit each source. **Run settings → Project entry file** chooses the entry point independently of the file being edited. Project export preserves files, stdin, arguments, environment settings and JVM main class. The historical source viewer follows captured file names without rewriting your edits.

Implemented paths:

| Language | Multi-file path |
|---|---|
| Python | Actual imports from the staged project; trace events identify imported user files |
| C / C++ | Compile all translation units with the project include directory; GDB captures helper-file events |
| Rust | `mod` files resolved by rustc; break at the actual Rust user entry point |
| Java / Kotlin | Compile project source files together; configurable JVM main class and JDI source paths |
| JavaScript / TypeScript | Actual project-relative ES modules loaded by QuickJS; TypeScript checks against its bundled standard declarations |
| HTML / CSS | Local linked stylesheet files are inlined into the isolated preview and independently parsed in WASM |

Example:

```json
{
  "schema": "tracescope-project/1",
  "language": "python",
  "entry": "main.py",
  "files": {
    "main.py": "from helper import triple\nresult=triple(7)\nprint(result)\n",
    "helper.py": "def triple(n):\n    value=n*3\n    return value\n"
  },
  "config": {"stdin": "", "args": [], "env": {}}
}
```

Headless capture:

```bash
python -m tracescope project my-project.json --trusted-local --out trace.json
```

Projects contain at most 64 text files / 1 MB. Absolute paths and parent traversal are rejected. Source staging and generated build output are separate directories. Native code retains ordinary host access in trusted mode; path validation is not a sandbox.

Package registries, Node APIs, CMake/Cargo/Gradle/Maven build orchestration, external JVM dependencies, generated-source projects and arbitrary npm packages remain outside this project format. HTML user scripts remain blocked by the preview CSP. The implementation does not claim those capabilities from merely accepting multiple files.
