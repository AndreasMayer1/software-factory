# run_all_windows_tests.ps1
# Test runner for Windows scripts — discovers and runs all *.Tests.ps1
# Pester test files in this folder.
#
# Located in scripts/windows/tests/ (not scanned by validate_scripts_org.py).
#
# Usage:
#   .\scripts\windows\tests\run_all_windows_tests.ps1

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# -- Ensure Pester is available ------------------------------------------------

$pester = Get-Module -ListAvailable -Name Pester | Sort-Object Version -Descending | Select-Object -First 1
if (-not $pester -or $pester.Version -lt [version]"5.0.0") {
    Write-Host "Pester v5+ not found. Installing..." -ForegroundColor Yellow
    Install-Module Pester -Force -Scope CurrentUser -SkipPublisherCheck
}

Import-Module Pester -MinimumVersion 5.0.0 -Force

# -- Discover test files -------------------------------------------------------

$testDir   = $PSScriptRoot
$testFiles = @(Get-ChildItem -LiteralPath $testDir -Filter "*.Tests.ps1" -File)
$testCount = ($testFiles | Measure-Object).Count

if ($testCount -eq 0) {
    Write-Host "No *.Tests.ps1 files found in $testDir" -ForegroundColor Yellow
    exit 0
}

Write-Host "=== run_all_windows_tests ===" -ForegroundColor Cyan
Write-Host "Test directory : $testDir"
Write-Host "Test files     : $testCount"
Write-Host ""

# -- Run tests -----------------------------------------------------------------

$config = New-PesterConfiguration
$config.Run.Path = $testDir
$config.Run.Exit = $true
$config.Output.Verbosity = "Detailed"

Invoke-Pester -Configuration $config
