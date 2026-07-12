[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$CommandArgs
)

$command = Get-Command krita-anime -ErrorAction SilentlyContinue
if ($command) {
    & $command.Source @CommandArgs
    exit $LASTEXITCODE
}

$repo = $env:KRITA_FINEGRAINED_HOME
if (-not $repo) {
    $skillRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
    $homeMarker = Join-Path $skillRoot '.krita-finegrained-home'
    if (Test-Path -LiteralPath $homeMarker) {
        $repo = (Get-Content -LiteralPath $homeMarker -Raw).Trim()
    }
}
if (-not $repo) {
    $repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
}

$python = $null
foreach ($environment in @('.agent-runtime', '.venv')) {
    $candidate = Join-Path $repo "$environment\Scripts\python.exe"
    if (Test-Path -LiteralPath $candidate) {
        $python = $candidate
        break
    }
}
if (-not $python) {
    throw "krita-anime is not installed and no E:-hosted runtime exists. Set KRITA_FINEGRAINED_HOME or install the CLI."
}
$env:PYTHONPATH = Join-Path $repo 'src'
& $python -m krita_anime.cli @CommandArgs
exit $LASTEXITCODE
