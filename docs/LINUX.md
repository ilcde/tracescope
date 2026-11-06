# Linux delivery status

Fedora is still the required primary acceptance platform. **Blocked:** this session runs on Windows, and the user confirmed there is no Fedora host or VM available. Fedora/SELinux/Wayland/X11, Ubuntu/Debian, Arch and glibc compatibility have not been runtime verified. No RPM or Linux binary is claimed to be tested.

`scripts/setup-linux.sh` is a reproducible source setup entry point, not evidence of execution. It installs project dependencies into `.venv`, restores the npm lockfile and builds the frontend. The browser UI can be served without a desktop WebView. GTK desktop operation requires PyGObject/WebKitGTK and compatible native dependencies.

Package names consulted in official repositories:

- Fedora WebKitGTK: https://packages.fedoraproject.org/pkgs/webkitgtk/webkit2gtk4.1/index.html
- Fedora OpenJDK 21 development: https://packages.fedoraproject.org/pkgs/java-21-openjdk/
- PyGObject build dependencies for Fedora/Debian/Arch: https://gnome.pages.gitlab.gnome.org/pygobject/getting_started.html
- Arch WebKitGTK 4.1: https://archlinux.org/packages/extra/webkit2gtk-4.1/
- Fedora bubblewrap: https://packages.fedoraproject.org/pkgs/bubblewrap/bubblewrap/index.html

Do not substitute Ubuntu package commands for Fedora. Use the distribution package manager to discover exact package availability for the selected release. Required tool roles: Python 3.11+, Node compatible with Vite 6, JDK 21, Kotlin/JVM 2.3.10, GCC/G++, GDB, binutils, rustc 1.90+, and desktop WebKitGTK/PyGObject when using the native shell.

Acceptance on a future Fedora host must run the language/ISA suites, native window tests, compile-failure/cancellation tests, and SELinux-enforcing Wayland plus X11 sessions. Keep SELinux enabled. A container-only test cannot prove desktop/Wayland behavior.

Native isolation is not yet implemented as a verified Linux boundary. Merely installing bubblewrap or setting process limits is insufficient. Default native execution stays locked. The current `--trusted-local` mode is an explicit development exception with normal host access and must not be used for untrusted imported code/build scripts.
