$ErrorActionPreference = 'Stop'
Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    if (Test-Path -LiteralPath 'graphify-out') {
        graphify update .
        if ($LASTEXITCODE -ne 0) { throw 'Graphify update failed.' }
    } else { Write-Output 'Graphify is not configured in this repository.' }
    if (-not (Get-Command sentrux -ErrorAction SilentlyContinue)) { throw 'Sentrux is required for architecture validation.' }
    if (Test-Path -LiteralPath '.sentrux/rules.toml') {
        sentrux check .
        if ($LASTEXITCODE -ne 0) { throw 'Sentrux rules failed.' }
    } else { Write-Output 'No Sentrux rules configured; rule check not applicable.' }
    sentrux gate .
    if ($LASTEXITCODE -ne 0) { throw 'Sentrux architecture regression.' }
} finally { Pop-Location }
