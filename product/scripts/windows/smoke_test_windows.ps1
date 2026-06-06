# smoke_test_windows.ps1
# Builds the Windows release candidate and runs smoke integration tests.
# Run this script from the project root on the Windows host (not inside WSL2).
# Exit code 0 = all tests passed. Exit code 1 = build or test failure.

param(
    [string]$ProjectRoot = ""
)

$ErrorActionPreference = "Stop"

. "$PSScriptRoot\find_project_root.ps1"
if (-not $ProjectRoot) {
    $ProjectRoot = Find-ProjectRoot
}

Write-Host "=== Smoke Test: Windows Release Candidate ==="
Write-Host ""

# Step 1: Build Windows release
Write-Host "Step 1: Building Windows release..."
Push-Location $ProjectRoot
try {
    flutter build windows --release
    if ($LASTEXITCODE -ne 0) {
        Write-Host -ForegroundColor Red "ERROR: flutter build windows --release failed (exit code: $LASTEXITCODE)."
        exit 1
    }
    Write-Host -ForegroundColor Green "Build succeeded."
} finally {
    Pop-Location
}

Write-Host ""

# Step 2: Run smoke integration tests
# Uses the individual test runner pattern from scripts/integration_test_runner/
# Only runs tests covering critical end-to-end flows for smoke validation.
Write-Host "Step 2: Running smoke integration tests..."

$testSuiteFile = "integration_test\integration_suite_test.dart"

# Smoke-relevant test names — critical end-to-end flows only.
# These cover: app launch, role selection, navigation to main screens.
# Update this list when new smoke-critical tests are added.
$smokeTests = @(
    "Role Selection Flow Role Selection Flow Tests Onboarding Flow First Launch - Shows Onboarding Screen and Dialog",
    "Role Selection Flow Role Selection Flow Tests Onboarding Flow Select Therapist Role - Navigates to PlansScreen",
    "Role Selection Flow Role Selection Flow Tests Onboarding Flow Select Client Role - Navigates to DataInputScreen",
    "Role Selection Flow Role Selection Flow Tests Post-Onboarding Flow (Client) App Launch - Client Role Already Selected - Navigates to DataInputScreen",
    "Role Selection Flow Role Selection Flow Tests Post-Onboarding Flow (Therapist) App Launch - Therapist Role Already Selected - Navigates to PlansScreen",
    "Simple Launch Simple App Launch Test with Mock Bloc (pumpWidget, Set Size) App pumps MyApp and finds DataInputScreen after pumps"
)

$allPassed = $true
$failedTests = @()

Push-Location $ProjectRoot
try {
    foreach ($testName in $smokeTests) {
        Write-Host "  Running: $testName"
        $output = flutter test $testSuiteFile --plain-name "$testName" -d windows *>&1
        $exitCode = $LASTEXITCODE
        if ($exitCode -ne 0) {
            Write-Host -ForegroundColor Red "  FAILED: $testName"
            $allPassed = $false
            $failedTests += $testName
        } else {
            Write-Host -ForegroundColor Green "  PASSED: $testName"
        }
    }
} finally {
    Pop-Location
}

Write-Host ""
if ($allPassed) {
    Write-Host -ForegroundColor Green "=== SMOKE TEST RESULT: PASS ==="
    Write-Host "All $($smokeTests.Count) smoke tests passed."
    exit 0
} else {
    Write-Host -ForegroundColor Red "=== SMOKE TEST RESULT: FAIL ==="
    Write-Host "$($failedTests.Count) of $($smokeTests.Count) smoke tests failed:"
    foreach ($t in $failedTests) {
        Write-Host "  - $t"
    }
    exit 1
}
