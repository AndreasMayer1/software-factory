# sync_windows_scripts.ps1
# Install tool for Windows scripts — copies scripts from the repo to an
# out-of-repo location with a review gate (SHA-256 diff + confirmation).
#
# Verb prefix: sync_ (state-modifying, in the known verb list).
#
# Usage:
#   .\sync_windows_scripts.ps1 [-TargetDir <path>] [-MirrorPath <path>]

[CmdletBinding()]
param(
    [string] $TargetDir  = (Join-Path $HOME "projects\private_mood_tracker\windows-scripts"),
    [string] $MirrorPath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# -- Resolve MirrorPath (project root) ----------------------------------------

. "$PSScriptRoot\find_project_root.ps1"
if (-not $MirrorPath) {
    $MirrorPath = Find-ProjectRoot
}

# -- Source directory ----------------------------------------------------------

$sourceDir = Join-Path $MirrorPath "scripts\windows"
if (-not (Test-Path -LiteralPath $sourceDir)) {
    throw "Source directory not found: $sourceDir"
}

# -- Compute SHA-256 manifest of source files ----------------------------------

function Get-FileManifest {
    param([string]$Dir, [string[]]$ExcludeFolders = @())
    $manifest = @{}
    $items = Get-ChildItem -LiteralPath $Dir -File -Recurse -ErrorAction Stop
    foreach ($item in $items) {
        # Skip files in excluded subfolders
        $relativePath = $item.FullName.Substring($Dir.Length).TrimStart('\', '/')
        $skip = $false
        foreach ($excl in $ExcludeFolders) {
            if ($relativePath -like "$excl\*" -or $relativePath -like "$excl/*") {
                $skip = $true
                break
            }
        }
        if ($skip) { continue }
        # Skip manifest and config files (install artifacts, not source)
        if ($relativePath -eq '_manifest.json' -or $relativePath -eq 'windows_scripts.config.json') {
            continue
        }
        $hash = (Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash
        $manifest[$relativePath] = $hash
    }
    return $manifest
}

Write-Host "=== sync_windows_scripts ===" -ForegroundColor Cyan
Write-Host "Source   : $sourceDir"
Write-Host "Target   : $TargetDir"
Write-Host "Mirror   : $MirrorPath"
Write-Host ""

$sourceManifest = Get-FileManifest -Dir $sourceDir -ExcludeFolders @("tests")

# -- Diff against existing install ---------------------------------------------

$manifestPath = Join-Path $TargetDir "_manifest.json"
$added   = @()
$removed = @()
$changed = @()

if (Test-Path -LiteralPath $manifestPath) {
    $oldManifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    $oldFiles = @{}
    foreach ($prop in $oldManifest.PSObject.Properties) {
        $oldFiles[$prop.Name] = $prop.Value
    }

    # Find added and changed files
    foreach ($file in $sourceManifest.Keys) {
        if (-not $oldFiles.ContainsKey($file)) {
            $added += $file
        } elseif ($oldFiles[$file] -ne $sourceManifest[$file]) {
            $changed += $file
        }
    }
    # Find removed files
    foreach ($file in $oldFiles.Keys) {
        if (-not $sourceManifest.ContainsKey($file)) {
            $removed += $file
        }
    }

    if ($added.Count -eq 0 -and $removed.Count -eq 0 -and $changed.Count -eq 0) {
        Write-Host "No changes detected. Install is up to date." -ForegroundColor Green
        return
    }

    Write-Host "Changes detected:" -ForegroundColor Yellow
    foreach ($f in $added)   { Write-Host "  + $f (new)" -ForegroundColor Green }
    foreach ($f in $removed) { Write-Host "  - $f (removed)" -ForegroundColor Red }
    foreach ($f in $changed) {
        Write-Host "  ~ $f" -ForegroundColor Yellow
        $installedFile = Join-Path $TargetDir $f
        $sourceFile    = Join-Path $sourceDir $f
        $gitAvailable  = $null -ne (Get-Command git -ErrorAction SilentlyContinue)
        if ($gitAvailable -and (Test-Path -LiteralPath $installedFile)) {
            Write-Host ""
            $savedEAP = $ErrorActionPreference
            $ErrorActionPreference = "Continue"
            git diff --no-index -- $installedFile $sourceFile 2>$null
            $ErrorActionPreference = $savedEAP
            Write-Host ""
        } else {
            Write-Host "    old hash: $($oldFiles[$f])"
            Write-Host "    new hash: $($sourceManifest[$f])"
        }
    }
} else {
    Write-Host "No previous install found. Fresh install." -ForegroundColor Yellow
    foreach ($f in ($sourceManifest.Keys | Sort-Object)) {
        Write-Host "  + $f" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Full manifest ($($sourceManifest.Count) files):"
foreach ($f in ($sourceManifest.Keys | Sort-Object)) {
    Write-Host "  $f  $($sourceManifest[$f])"
}

# -- Confirmation prompt -------------------------------------------------------

Write-Host ""
$response = Read-Host "Confirm install? [y/N]"
if ($response -notin @('y', 'Y', 'yes', 'Yes')) {
    Write-Host "Aborted." -ForegroundColor Red
    return
}

# -- Copy files ----------------------------------------------------------------

if (-not (Test-Path -LiteralPath $TargetDir)) {
    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
}

foreach ($relativePath in ($sourceManifest.Keys | Sort-Object)) {
    $srcFile = Join-Path $sourceDir $relativePath
    $dstFile = Join-Path $TargetDir $relativePath
    $dstDir  = Split-Path $dstFile -Parent
    if (-not (Test-Path -LiteralPath $dstDir)) {
        New-Item -ItemType Directory -Path $dstDir -Force | Out-Null
    }
    Copy-Item -LiteralPath $srcFile -Destination $dstFile -Force
}

# Remove files that no longer exist in source
foreach ($f in $removed) {
    $dstFile = Join-Path $TargetDir $f
    if (Test-Path -LiteralPath $dstFile) {
        Remove-Item -LiteralPath $dstFile -Force
    }
}

# -- Write config --------------------------------------------------------------

$configPath = Join-Path $TargetDir "windows_scripts.config.json"
$configObj  = @{ project_root = $MirrorPath }
$configObj | ConvertTo-Json | Set-Content -LiteralPath $configPath -Encoding UTF8

# -- Write manifest ------------------------------------------------------------

$sourceManifest | ConvertTo-Json | Set-Content -LiteralPath $manifestPath -Encoding UTF8

# -- Summary -------------------------------------------------------------------

Write-Host ""
Write-Host "Install complete." -ForegroundColor Green
Write-Host "  Files copied : $($sourceManifest.Count)"
if ($removed.Count -gt 0) {
    Write-Host "  Files removed: $($removed.Count)"
}
Write-Host "  Config       : $configPath"
Write-Host "  Manifest     : $manifestPath"
