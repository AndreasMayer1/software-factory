# find_project_root.ps1
# Resolution helper for Windows scripts — dot-sourced by other scripts.
# Exports Find-ProjectRoot with 3-level precedence for locating the project root.
#
# Precedence:
#   1. Explicit -ProjectPath parameter
#   2. windows_scripts.config.json in the script's directory (out-of-repo install)
#   3. Auto-derive from script location (in-repo: scripts/windows -> scripts -> project)

function Find-ProjectRoot {
    [CmdletBinding()]
    param(
        [string] $ProjectPath = ""
    )

    # Precedence 1: explicit parameter
    if ($ProjectPath) {
        if (-not (Test-Path -LiteralPath $ProjectPath)) {
            throw "Find-ProjectRoot: explicit ProjectPath does not exist: $ProjectPath"
        }
        return $ProjectPath
    }

    # Precedence 2: windows_scripts.config.json next to the calling script
    $configPath = Join-Path $PSScriptRoot "windows_scripts.config.json"
    if (Test-Path -LiteralPath $configPath) {
        $config = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
        if ($config.project_root) {
            $resolved = $config.project_root
            if (-not (Test-Path -LiteralPath $resolved)) {
                throw "Find-ProjectRoot: config project_root does not exist: $resolved"
            }
            return $resolved
        }
    }

    # Precedence 3: auto-derive from script location (in-repo layout)
    # scripts/windows/ -> scripts/ -> <project root>
    $scriptDir = if ($PSScriptRoot) { $PSScriptRoot }
                 elseif ($MyInvocation.MyCommand.Path) { Split-Path $MyInvocation.MyCommand.Path -Parent }
                 else { $null }
    if ($scriptDir) {
        $derived = Split-Path (Split-Path $scriptDir -Parent) -Parent
        if (Test-Path -LiteralPath $derived) {
            return $derived
        }
    }

    throw "Find-ProjectRoot: cannot determine project root. Pass -ProjectPath explicitly."
}
