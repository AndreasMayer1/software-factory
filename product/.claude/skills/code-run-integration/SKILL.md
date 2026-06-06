---
name: code-run-integration
description: Run integration tests individually using the test runner script
tools: ["Bash", "Read"]
model: haiku
---

You run integration tests using the dedicated test runner script.

**User invokes**: "Use run-integration-tests skill"

**Background**:
- Running the full integration test suite is unstable and may hang
- A PowerShell script exists that runs each test individually
- The script maintains a manual list of test names that must be updated when adding new tests

**You execute**:

1. **Run Tests**:
   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts/integration_test_runner/run_individual_integration_tests.ps1
   ```

2. **Review Results**:
   - Check console output for PASS/FAIL status of each test
   - Log files are saved to `scripts/integration_test_runner/test_outputs/`

3. **Report**: Summarize which tests passed and which failed

**Important Notes**:
- Tests must be run from the project root directory
- When adding new integration tests, you MUST update the `$testNames` array in the script
- Always specify `-d windows` for test commands
- See `doc/testing/integration_testing.md` for full guidelines

**Output**: "Integration tests completed. [X] passed, [Y] failed. See test_outputs/ for details."
