param(
    [ValidateSet("codex", "opencode", "claude", "workbuddy", "all")]
    [string]$Agent = "codex",
    [ValidateSet("project", "user")]
    [string]$Scope = "user",
    [string]$ProjectRoot = (Get-Location).Path,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    $python = "python"
}

$arguments = @(
    (Join-Path $PSScriptRoot "install_agent_skill.py"),
    "--agent", $Agent,
    "--scope", $Scope,
    "--project-root", $ProjectRoot
)
if ($Force) {
    $arguments += "--force"
}

& $python @arguments
exit $LASTEXITCODE
