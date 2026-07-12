[CmdletBinding()]
param(
    [string]$Destination,
    [switch]$InstallToKrita
)

$repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$source = Join-Path $repo 'krita-plugin'
if (-not (Test-Path -LiteralPath $source)) {
    throw "Krita plugin source was not found at $source"
}

if ($InstallToKrita) {
    if ($Destination) {
        throw 'Use either -Destination or -InstallToKrita, not both.'
    }
    $Destination = Join-Path $env:APPDATA 'krita\pykrita'
}
if (-not $Destination) {
    $Destination = Join-Path $repo 'staging\krita-pykrita'
}

$resolvedRepo = [System.IO.Path]::GetFullPath($repo)
$resolvedDestination = [System.IO.Path]::GetFullPath($Destination)
if (-not $InstallToKrita -and -not $resolvedDestination.StartsWith($resolvedRepo, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'A non-Krita staging destination must remain inside the workspace.'
}

New-Item -ItemType Directory -Force -Path $resolvedDestination | Out-Null
Copy-Item -LiteralPath (Join-Path $source 'kritamcp.desktop') -Destination $resolvedDestination -Force
Copy-Item -LiteralPath (Join-Path $source 'kritamcp') -Destination $resolvedDestination -Recurse -Force
Write-Output "Krita plugin copied to $resolvedDestination"
if (-not $InstallToKrita) {
    Write-Output 'This is a non-system-drive staging copy. Use -InstallToKrita only when ready to enable it in Krita.'
}
