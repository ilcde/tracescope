$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path '.venv\Scripts\python.exe')) { python -m venv .venv }
& .venv\Scripts\python.exe -m pip install -r requirements.lock.txt
npm.cmd ci
npm.cmd run build
& .venv\Scripts\python.exe -m tracescope doctor
