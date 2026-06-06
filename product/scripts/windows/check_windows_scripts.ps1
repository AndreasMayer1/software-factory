# check_windows_scripts.ps1
# Deterministic denylist checker for Windows scripts.
# Scans all .ps1 and .py under scripts/windows/ (excluding tests/) for
# dangerous patterns. Exit 0 = clean. Exit 1 = match found.
#
# Verb prefix: check_ (read-only, in the known verb list).
#
# Allow-list: patterns annotated with "# safety: known-safe <reason>" on the
# same line are skipped.

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# -- Resolve source directory --------------------------------------------------

. "$PSScriptRoot\find_project_root.ps1"
$projectRoot = Find-ProjectRoot
$sourceDir   = Join-Path $projectRoot "scripts\windows"

if (-not (Test-Path -LiteralPath $sourceDir)) {
    throw "Source directory not found: $sourceDir"
}

# -- Denylist patterns ---------------------------------------------------------
# Each entry: regex pattern, description, severity (error|warning),
# optional allow-file (basename where the pattern is expected).

$denylist = @(
    @{
        Pattern     = '\bInvoke-Expression\b|\bIEX\b'
        Description = "Invoke-Expression / IEX (PowerShell code injection)"
        Severity    = "error"
        AllowFile   = $null
    },
    @{
        Pattern     = '\bDownloadString\b|\bDownloadFile\b|\bInvoke-WebRequest\b|\bInvoke-RestMethod\b'
        Description = "Network download (DownloadString/DownloadFile/Invoke-WebRequest/Invoke-RestMethod)"
        Severity    = "error"
        AllowFile   = $null
    },
    @{
        Pattern     = '-EncodedCommand|\bFromBase64String\b'
        Description = "Encoded command / Base64 decode (obfuscated payloads)"
        Severity    = "error"
        AllowFile   = $null
    },
    @{
        Pattern     = '\bRegister-ScheduledTask\b'
        Description = "Register-ScheduledTask (unexpected task registration)"
        Severity    = "error"
        AllowFile   = "sleep_when_autorun_done.ps1"
    },
    @{
        Pattern     = 'Set-ItemProperty.*HK(LM|CU)'
        Description = "Registry write (Set-ItemProperty HKLM/HKCU)"
        Severity    = "error"
        AllowFile   = $null
    },
    @{
        Pattern     = '\bnet\s+user\b|\bAdd-LocalGroupMember\b'
        Description = "User account manipulation (net user / Add-LocalGroupMember)"
        Severity    = "error"
        AllowFile   = $null
    },
    @{
        Pattern     = '\bRemove-Item\b.*-Recurse'
        Description = "Recursive deletion (Remove-Item -Recurse)"
        Severity    = "warning"
        AllowFile   = $null
    },
    @{
        Pattern     = '\bStart-Process\b.*(https?://|ftp://)'
        Description = "Start-Process with URL (external content execution)"
        Severity    = "error"
        AllowFile   = $null
    }
)

# -- Scan files ----------------------------------------------------------------

$files = Get-ChildItem -LiteralPath $sourceDir -Recurse -File `
    -Include @("*.ps1", "*.py") |
    Where-Object {
        $relativePath = $_.FullName.Substring($sourceDir.Length).TrimStart('\', '/')
        -not ($relativePath -like "tests\*" -or $relativePath -like "tests/*")
    }

$findings    = @()
$errorCount  = 0

foreach ($file in $files) {
    $lines    = Get-Content -LiteralPath $file.FullName -ErrorAction Stop
    $fileName = $file.Name

    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line    = $lines[$i]
        $lineNum = $i + 1

        # Skip lines with inline allow-list annotation
        if ($line -match '#\s*safety:\s*known-safe\b') {
            continue
        }

        foreach ($rule in $denylist) {
            if ($line -match $rule.Pattern) {
                # Check file-level allow-list
                if ($rule.AllowFile -and $fileName -eq $rule.AllowFile) {
                    continue
                }

                $sev = $rule.Severity.ToUpper()
                $findings += "[{0}] {1}:{2}  {3}" -f $sev, $file.Name, $lineNum, $rule.Description
                if ($rule.Severity -eq "error") {
                    $errorCount++
                }
            }
        }
    }
}

# -- Report --------------------------------------------------------------------

Write-Host "=== check_windows_scripts ===" -ForegroundColor Cyan
Write-Host "Scanned  : $($files.Count) files"
Write-Host ""

if ($findings.Count -eq 0) {
    Write-Host "No dangerous patterns found." -ForegroundColor Green
    exit 0
} else {
    foreach ($f in $findings) {
        if ($f -match '^\[ERROR\]') {
            Write-Host $f -ForegroundColor Red
        } else {
            Write-Host $f -ForegroundColor Yellow
        }
    }
    Write-Host ""
    Write-Host "$($findings.Count) finding(s), $errorCount error(s)." -ForegroundColor Red
    if ($errorCount -gt 0) {
        exit 1
    }
    exit 0
}
