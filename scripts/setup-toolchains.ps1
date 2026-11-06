$ErrorActionPreference = 'Stop'
$traceRoot = (Resolve-Path -LiteralPath (Split-Path $PSScriptRoot -Parent)).Path
Set-Location -LiteralPath $traceRoot
$traceTools = Join-Path $traceRoot '.tools'
New-Item -ItemType Directory -Force -Path $traceTools | Out-Null
$traceLock = Get-Content -LiteralPath 'toolchains.lock.json' -Raw | ConvertFrom-Json
foreach ($item in $traceLock) {
    $destination = Join-Path $traceTools $item.file
    if (-not (Test-Path -LiteralPath $destination)) { Invoke-WebRequest $item.url -OutFile $destination }
    if ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant() -ne $item.sha256) { throw "Checksum mismatch for $($item.file)" }
}
$archiveTool = Get-Command 7z.exe -ErrorAction SilentlyContinue
if ($archiveTool) { $sevenZip = $archiveTool.Source } else { $sevenZip = 'C:\Program Files\7-Zip\7z.exe' }
if (-not (Test-Path -LiteralPath $sevenZip)) { throw '7-Zip is required to unpack w64devkit without executing the archive.' }
& $sevenZip x (Join-Path $traceTools 'w64devkit.7z.exe') "-o$traceTools" -y
if ($LASTEXITCODE -ne 0) { throw 'Toolchain extraction failed' }
tar -xf (Join-Path $traceTools 'rust.tar.xz') -C $traceTools
if ($LASTEXITCODE -ne 0) { throw 'Rust extraction failed' }
$rustDestination = Join-Path $traceTools 'rust'
New-Item -ItemType Directory -Force -Path $rustDestination | Out-Null
foreach ($component in @('rustc','rust-std-x86_64-pc-windows-gnu','rust-mingw')) {
    Copy-Item -Path (Join-Path $traceTools "rust-1.90.0-x86_64-pc-windows-gnu\$component\*") -Destination $rustDestination -Recurse -Force
}
Write-Output 'Workspace GCC/GDB and Rust installed. JDK 21 and Kotlin/JVM 2.3.10 remain separate prerequisites.'
