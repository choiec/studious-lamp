$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path -LiteralPath (Join-Path -Path $PSScriptRoot -ChildPath '..\..') -ErrorAction Stop).Path
Set-Location -LiteralPath $repoRoot
& uv sync --locked --offline
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
