# Linux packaging and acceptance

Fedora 43 and 44 are explicit CI targets, alongside Ubuntu 24.04. Each job runs actual Python, JVM, C/C++/Rust and all eight ISA tests. Fedora packages use RPM; Ubuntu uses DEB. The same job installs its package, runs RISC-V code through the installed launcher from `/tmp`, and exercises a real GTK/WebKit window on Xvfb. Refer to the [exact workflow result](https://github.com/ilcde/tracescope/actions/workflows/verify.yml) for pass/fail evidence.

## Build and install

After `npm ci && npm run build` and installing Python dependencies:

```bash
# Fedora; also needs rpm-build
python scripts/build_linux.py --rpm
sudo dnf install ./packages/tracescope-*.rpm

# Ubuntu; also needs dpkg-deb
python scripts/build_linux.py --deb
sudo apt install ./packages/tracescope_*.deb

tracescope doctor
tracescope desktop --trusted-local
```

The application installs under `/usr/share/tracescope`, with a `/usr/bin/tracescope` launcher and desktop entry. It ships pinned dependency wheels. First launch creates a user-owned virtual environment using those wheels, with no Python package downloads. Distribution GTK/PyGObject/WebKit libraries remain system dependencies. Compilers/JDK/Kotlin are separate prerequisites.

The `.tar.gz` bundle uses the same runtime: extract it and run `TraceScope/launch.sh`. It is distribution- and Python-ABI-specific, not a universal Linux executable. Do not copy a Fedora package to Ubuntu or change its Python version file to bypass the check.

## User data and removal

Run records and caches live under `$XDG_STATE_HOME/tracescope` (normally `~/.local/state/tracescope`). Override with `TRACESCOPE_DATA_DIR`. Application resources stay separate from mutable state. Package removal with `dnf remove tracescope` or `apt remove tracescope` preserves this user directory; delete it manually only if you want to discard saved execution records and the local runtime.

## What the CI environment establishes

The container jobs validate the named distributions' toolchains, libraries, packages and an X11 virtual display. CI allows ptrace for debugger tests. Its WebKit test process has a container-only sandbox override because nested user namespaces are unavailable there; the shipped launcher never sets that override. These are functional tests, **not native isolation or SELinux acceptance**.

No physical Fedora host or VM is available in this session. SELinux-enforcing Wayland and physical X11 acceptance remain unverified. Keep SELinux and normal host protections enabled. Other Debian releases, Arch, ARM Linux and musl need independent runs.

## Official prerequisites

- [pywebview Linux installation](https://pywebview.flowrl.com/guide/installation)
- [Fedora WebKitGTK 4.1 package](https://packages.fedoraproject.org/pkgs/webkitgtk/webkit2gtk4.1/)
- [PyGObject installation by distribution](https://gnome.pages.gitlab.gnome.org/pygobject/getting_started.html)

Native code execution is locked by default. `--trusted-local` opts into normal host access and is not suitable for untrusted imported code. See [security](SECURITY.md).
