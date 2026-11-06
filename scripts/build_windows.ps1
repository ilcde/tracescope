$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
npm.cmd run build
if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed' }
& .venv\Scripts\python.exe scripts/build_windows.py
if ($LASTEXITCODE -ne 0) { throw 'Windows package build failed' }
