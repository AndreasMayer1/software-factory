---
task_id: TASK-PROC-036-10
type: impl
parent_requirement: REQ-PROC-036
urgency: 3
urgency_reason: U3-PROC
impact: 4
impact_reason: I4-ENAB
status: completed
started: 2026-04-19
completed: 2026-04-19
session_completed_at: 2026-04-19T17:27:43Z
session_id: 4a8c86fb-e5a2-4dd4-b32f-de01be1de98b
session_account: web
effort: M
created: 2026-03-29
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: [SEC-01, SEC-02, SEC-10]
target_package: "Transfer Data Model"
scope_description: "Add coverage threshold check and release_description warning to check_release_preconditions.py; add smoke test gate step to /release skill; create smoke_test_windows.ps1 and smoke_test_llm.py scripts"
release_description: "Release process validates test coverage and confirms smoke test before publishing."
requirements_version:
  commit: bbe691f2
  file: ../requirements.md
---

# Goal: Release Skill — Coverage Check, release_description Warning, and Smoke Test Gate

## Objective

Extend the release workflow with three improvements identified in TASK-PROC-036-09:

1. **Coverage threshold check** (`check_release_preconditions.py`): After `flutter test`, verify that line coverage meets the project minimum (75%). The check must account for all tracked source files, not only those imported by tests. Fails hard if below threshold.

2. **`release_description` warning** (`check_release_preconditions.py`): After the task completion check, list any `impl`-type tasks assigned to the active release that have no `release_description` field set. Non-blocking — displayed as a warning so the developer can confirm omissions are intentional.

3. **Smoke test gate** (`/release` skill + two new scripts):
   - New step 2 in the `/release` skill: instruct the developer to run the provided scripts on Windows, then wait for explicit "proceed" confirmation before continuing to delivery.
   - `scripts/smoke_test_windows.ps1`: builds the Windows release candidate and runs integration tests covering critical end-to-end flows via the existing individual test runner pattern.
   - `scripts/smoke_test_llm.py`: launches the Windows release binary, captures a screenshot, and sends it to the Claude API (image input) for a visual pass/fail verdict. Advisory only.

## Requirements Summary

SEC-01 (Release Skill): skill step order updated — smoke gate is step 2, delivery is step 3.
SEC-02 (Automation Scripts): `check_release_preconditions.py` gains coverage check (Check 4b) and release_description warning (Check 2b, non-blocking).
SEC-10 (Smoke Test Gate): two new scripts implementing the two-layer gate; skill waits for "proceed" before delivery.

For complete requirements at task creation time:
```
git show bbe691f2:requirements_tasks/process/AI_rules/workflows/release_workflow/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- `scripts/check_release_preconditions.py`: add Check 4b (coverage) and Check 2b (release_description warning)
- `.claude/skills/release/skill.md`: insert new Step 2 (smoke gate), renumber Steps 2–6 → 3–7
- `scripts/smoke_test_windows.ps1`: new script (build + run integration tests via individual runner)
- `scripts/smoke_test_llm.py`: new script (launch app + screenshot + Claude API verdict)
- `CLAUDE.md` scripts table: add the two new scripts

### Out of Scope
- Writing the Dart integration test file itself (`integration_test/smoke_test.dart`) — that is a separate task under the functional test requirement
- Changes to `execute_release.py`
- Changes to `generate_technical_release_notes.py`

## Acceptance Criteria

- [ ] `check_release_preconditions.py` runs `flutter test --coverage` and fails if line coverage < 75%; measurement covers all tracked source files
- [ ] `check_release_preconditions.py` prints a warning (non-blocking) listing impl tasks without `release_description`, or confirms all are set
- [ ] `/release` skill Step 2 instructs developer to run `smoke_test_windows.ps1` and `smoke_test_llm.py`, then waits for "proceed" before running `execute_release.py`
- [ ] `smoke_test_windows.ps1` builds the Windows release and runs integration tests using the existing individual runner pattern; exits 0 on pass
- [ ] `smoke_test_llm.py` launches the release binary, captures a screenshot, calls the Claude API with image input, and prints PASS or FAIL with reason; exits 0 on PASS
- [ ] Both scripts are listed in CLAUDE.md scripts table
- [ ] All existing tests pass

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-036-09 | completed | Research; findings in plans_and_protocols/ |

## Notes

- Coverage tool choice (dlcov vs lcov) is an implementation decision — see research in `tasks/2026-03-28_explore_release-skill-improvements (completed)/plans_and_protocols/2026-03-28_01_research_release-patterns.md`
- `smoke_test_llm.py` requires an Anthropic API key on the Windows machine (`ANTHROPIC_API_KEY` env var)
- The skill cannot launch the Windows app directly (WSL2/Windows boundary) — the scripts are run by the developer on Windows
- Integration test runner pattern: `scripts/integration_test_runner/run_individual_integration_tests.ps1` — `smoke_test_windows.ps1` follows the same pattern but scoped to smoke-relevant tests only
