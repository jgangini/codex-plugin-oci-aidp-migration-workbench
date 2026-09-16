$ErrorActionPreference = 'Stop'
Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    if (Test-Path -LiteralPath 'graphify-out/GRAPH_REPORT.md') { Get-Content -LiteralPath 'graphify-out/GRAPH_REPORT.md' }
    if (-not (Get-Command sentrux -ErrorAction SilentlyContinue)) { throw 'Sentrux is required for architecture validation.' }
    sentrux gate --save .
    if ($LASTEXITCODE -ne 0) { throw 'Sentrux baseline failed.' }
    if (Test-Path -LiteralPath '.sentrux/rules.toml') {
        sentrux check .
        if ($LASTEXITCODE -ne 0) { throw 'Sentrux rules failed.' }
    } else { Write-Output 'No Sentrux rules configured; rule check not applicable.' }
} finally { Pop-Location }
