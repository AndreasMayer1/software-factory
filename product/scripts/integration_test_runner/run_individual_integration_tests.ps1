# PowerShell Script to Run Integration Tests Individually

# Get the directory where the script is located
$scriptDir = $PSScriptRoot

# Define the output directory relative to the script location
$outputDir = Join-Path $scriptDir "test_outputs"

# Define the path to the main integration test suite file (relative to project root)
# IMPORTANT: This script MUST be run from the project root directory.
# Assuming the script will be run from the project root directory
$testSuiteFile = "integration_test/integration_suite_test.dart"
# If running the script from its own directory, adjust the path:
# $projectRoot = Resolve-Path (Join-Path $scriptDir "..") # Go up one level
# $testSuiteFile = Join-Path $projectRoot "integration_test/integration_suite_test.dart"

Write-Host "Creating output directory: $outputDir"
# Create the output directory, overwriting if it exists is handled by Set-Content later
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

# -----------------------------------------------------------------------------
# MANUAL TEST LIST (Temporary Workaround)
# -----------------------------------------------------------------------------
# Automatic test discovery ('flutter test --machine') is currently failing
# due to issues within the test suite itself (exiting with code 1).
# As a workaround, manually list the full test names below.
# Ensure these names match exactly what 'flutter test --plain-name' expects,
# including all parent group names.
# Example:
# $testNames = @(
#    "Group A Test 1",
#    "Group A Group B Test 2",
#    "Group C Test 3"
# )

$testNames = @(
    # --- PASTE FULL TEST NAMES HERE ---
    "Role Selection Flow Role Selection Flow Tests Onboarding Flow First Launch - Shows Onboarding Screen and Dialog",
    "Role Selection Flow Role Selection Flow Tests Onboarding Flow Select Therapist Role - Navigates to PlansScreen",
    "Role Selection Flow Role Selection Flow Tests Onboarding Flow Select Client Role - Navigates to DataInputScreen",
    "Role Selection Flow Role Selection Flow Tests Post-Onboarding Flow (Client) App Launch - Client Role Already Selected - Navigates to DataInputScreen",
    "Role Selection Flow Role Selection Flow Tests Post-Onboarding Flow (Therapist) App Launch - Therapist Role Already Selected - Navigates to PlansScreen",
    "Dependency Injection Therapist Plans Dependency Injection PlanTemplatesBloc is properly registered",
    "Dependency Injection Therapist Plans Dependency Injection PlanTemplatesBloc is registered as singleton",
    "Dependency Injection Therapist Plans Dependency Injection PlanTemplatesBloc can be created without errors",
    "Plan Templates TherapistPlanTemplatesFeatureRootScreen end-to-end flow across screen sizes",
    "Simple Launch Simple App Launch Test with Mock Bloc (pumpWidget, Set Size) App pumps MyApp and finds DataInputScreen after pumps",
    "Therapist Navigation Therapist Navigation navigates correctly between sections on large/medium screens (NavigationRail)",
    "Therapist Navigation Therapist Navigation navigates correctly between sections on small screens (BottomNavigationBar)"
    # --- END OF TEST NAMES ---
)

# Basic check if the manual list is empty
if ($null -eq $testNames -or $testNames.Count -eq 0) {
    Write-Error "The manual test list in the script is empty. Please add test names."
    exit 1
}
# -----------------------------------------------------------------------------

Write-Host "Found $($testNames.Count) tests to run."

# Loop through each test name
foreach ($testName in $testNames) {
    Write-Host "--------------------------------------------------"
    Write-Host "Running test: $testName"

    # Sanitize the test name to create valid directory/file names
    # Replace common invalid characters with underscores
    $sanitizedFullName = $testName -replace '[^a-zA-Z0-9_]+', '_' -replace '__+', '_'
    
    # Define lengths for splitting the name (adjust as needed)
    $maxDirNameLength = 20  # Shorter directory name
    $maxFileNameLength = 80 # Shorter filename part
    
    # Split the sanitized name into directory and file parts
    $subDirName = $sanitizedFullName
    if ($subDirName.Length -gt $maxDirNameLength) {
        $subDirName = $subDirName.Substring(0, $maxDirNameLength)
    }
    
    $logFileName = $sanitizedFullName
    if ($logFileName.Length -gt $maxFileNameLength) {
        # Take the end part for the filename if the full name is too long
        $startIndex = $sanitizedFullName.Length - $maxFileNameLength
        $logFileName = $sanitizedFullName.Substring($startIndex)
    }
    $logFileName += ".log" # Add extension

    # Define and create the subdirectory path
    $subDirPath = Join-Path $outputDir $subDirName
    if (-not (Test-Path $subDirPath)) {
        New-Item -ItemType Directory -Force -Path $subDirPath | Out-Null
        Write-Host "Created subdirectory: $subDirPath"
    }

    # Define the final output file path
    $outputFile = Join-Path $subDirPath $logFileName
    Write-Host "Saving output to: $outputFile"

    # Construct the command
    $command = "flutter test $testSuiteFile --plain-name ""$testName"" -d windows"
    Write-Host "Executing: $command"

    # Execute the command, capturing all output streams (*>&1) into a variable
    # Use Invoke-Expression to handle potential quoting issues in the command string
    $output = Invoke-Expression "$command *>&1"
    
    # IMPORTANT: Check $LASTEXITCODE *immediately* after the command finishes
    $exitCode = $LASTEXITCODE

    # Write the captured output to the log file, overwriting it (-Force)
    try {
        Set-Content -Path $outputFile -Value $output -Force -ErrorAction Stop
    } catch {
        Write-Error "Failed to write log file '$outputFile'. Error: $($_.Exception.Message)"
        # Keep the script running to report the test status, but log writing failed.
    }

    # Check the captured exit code and report status
    if ($exitCode -ne 0) {
        Write-Host -ForegroundColor Red "Test '$testName' FAILED (Exit Code: $exitCode). Check log file: $outputFile"
    } else {
        Write-Host -ForegroundColor Green "Test '$testName' PASSED."
    }
}

Write-Host "--------------------------------------------------"
Write-Host "Finished running all individual tests."
Write-Host "Outputs saved in: $outputDir"