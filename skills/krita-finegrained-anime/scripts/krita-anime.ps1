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
    $repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
}
$python = Join-Path $repo '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    throw "krita-anime is not installed and no workspace venv exists. Set KRITA_FINEGRAINED_HOME."
}
$env:PYTHONPATH = Join-Path $repo 'src'
& $python -m krita_anime.cli @CommandArgs
exit $LASTEXITCODE
