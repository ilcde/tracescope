#ifndef UNICODE
#define UNICODE
#endif
#define _UNICODE
#include <windows.h>
#include <stdio.h>
#include <wchar.h>

int wmain(void) {
    wchar_t root[32768], python[32768], command[32768];
    if (!GetModuleFileNameW(NULL, root, 32768)) return 1;
    wchar_t *slash = wcsrchr(root, L'\\');
    if (!slash) return 1;
    *slash = 0;
    if (swprintf(python, 32768, L"%ls\\runtime\\python.exe", root) < 0) return 1;
    const wchar_t *args = GetCommandLineW();
    if (*args == L'"') { args++; while (*args && *args != L'"') args++; if (*args) args++; }
    else { while (*args && *args != L' ' && *args != L'\t') args++; }
    while (*args == L' ' || *args == L'\t') args++;
    if (swprintf(command, 32768, L"\"%ls\" -m tracescope %ls", python, *args ? args : L"desktop") < 0) return 1;
    STARTUPINFOW startup = {0}; startup.cb = sizeof(startup);
    PROCESS_INFORMATION child = {0};
    if (!CreateProcessW(python, command, NULL, NULL, TRUE, 0, NULL, NULL, &startup, &child)) {
        fwprintf(stderr, L"TraceScope runtime could not start (Windows error %lu). Keep the runtime folder beside TraceScope.exe.\n", GetLastError());
        return 1;
    }
    WaitForSingleObject(child.hProcess, INFINITE);
    DWORD code = 1; GetExitCodeProcess(child.hProcess, &code);
    CloseHandle(child.hProcess); CloseHandle(child.hThread);
    return (int)code;
}
