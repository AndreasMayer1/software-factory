# Protocol: Coverage Check, release_description Warning, and Smoke Test Gate

_Task: TASK-PROC-036-10_

---

## 2026-04-19T19:16
**Agent**: Context & Planning Agent
**Agent ID**: ae1035f97d969174a
**Action**: Phase 1 — Context gathering and implementation plan creation
**Outcome**: Pass
- Read all referenced files: `check_release_preconditions.py` (157 lines), `release/skill.md` (6 steps), `CLAUDE.md` scripts table, `run_individual_integration_tests.ps1`, both research files from TASK-PROC-036-09
- Confirmed: `smoke_test_windows.ps1` and `smoke_test_llm.py` do not yet exist
- Confirmed: task folder and `plans_and_protocols/` directory already exist (created at task setup)
- Created plan file: `plans_and_protocols/2026-04-19_01_plan_coverage-smoke-gate.md`
- Plan covers all 5 files with exact code, insertion points, and renumbering table

**Plan summary**:
- `check_release_preconditions.py`: Add `parse_frontmatter()` + `find_goal_files()` helpers; insert Check 2b (release_description warning, non-blocking) after Check 2; replace Check 4 with `--coverage` + `check_line_coverage()` helper (parses lcov.info directly, accounts for untested files by scanning lib/*.dart)
- `release/skill.md`: Insert new Step 2 (smoke gate with "proceed" confirmation), renumber old Steps 2–6 → 3–7, update all `4.x` sub-step refs to `5.x`, update Step 6 cross-reference from `Step 4.1` → `Step 5.1`
- `smoke_test_windows.ps1`: PowerShell script; builds with `flutter build windows --release`, runs 6 smoke-critical integration tests using `--plain-name` pattern; exits 0 on all pass
- `smoke_test_llm.py`: Python script; launches release .exe, waits 6s, captures full-screen screenshot via PIL, sends to `claude-haiku-4-5-20251001` with structured pass/fail prompt; exits 0 on PASS
- `CLAUDE.md`: Add "Windows release scripts" subsection with two entries after the existing "Scripts that modify" list

**Next Step**: Implement all changes in the order listed in the plan (check_release_preconditions.py → skill.md → smoke_test_windows.ps1 → smoke_test_llm.py → CLAUDE.md). Run `python3 -m py_compile scripts/smoke_test_llm.py` and `flutter test` as verification steps.

## 2026-04-19T20:02
**Agent**: Implementation Agent
**Agent ID**: unknown (main conversation agent)
**Action**: Phase 2 — Full implementation of all 5 files per plan
**Outcome**: Pass — all verification checks passed
- `scripts/check_release_preconditions.py`: Added `find_goal_files()`, `parse_frontmatter()`, `check_line_coverage()` helpers and `COVERAGE_THRESHOLD = 75.0` constant before `main()`. Inserted Check 2b (release_description warning, non-blocking) after Check 2. Replaced Check 4 with `flutter test --coverage` + `check_line_coverage()` call. Renamed old `# Check 4b` comment to `# Check 4c` for clarity. Used module-level `re` (no duplicate import).
- `.claude/skills/release/skill.md`: Inserted new Step 2 (smoke gate with "proceed" confirmation flow). Renumbered old Steps 2–6 → 3–7. Updated all sub-step headers `4.x` → `5.x`. Updated body cross-reference "Step 4.1" in Step 6 → "Step 5.1". Updated "Do not proceed to Step 5" → "Step 6" in section 5.5.
- `scripts/smoke_test_windows.ps1`: Created — builds with `flutter build windows --release`, runs 6 smoke-critical integration tests via `--plain-name`; exits 0 on all pass, 1 on any failure.
- `scripts/smoke_test_llm.py`: Created — launches release .exe, waits 6s, captures screenshot via PIL.ImageGrab, calls `claude-haiku-4-5-20251001` with structured PASS/FAIL prompt; exits 0 on PASS.
- `CLAUDE.md`: Added "Windows release scripts (run on Windows host, not in WSL2):" subsection with both script entries at end of section 10.

**Verification**:
- `python3 -m py_compile scripts/check_release_preconditions.py` → exit 0
- `python3 -m py_compile scripts/smoke_test_llm.py` → exit 0
- skill.md step headers: Step 1–7 sequential, no gaps, no duplicates
- CLAUDE.md Windows release scripts subsection present (single occurrence)
- `flutter test` → exit 0, no FAILED lines

**Next Step**: Run `task-complete` to mark TASK-PROC-036-10 as completed and commit.

## 2026-04-19T17:33:32Z
**Agent**: Orchestrator (task-complete inline)
**Agent ID**: (main conversation agent — automated mode)
**Action**: Task close-out — TASK-PROC-036-10
**Outcome**: Pass
- goal.md frontmatter updated: `status: completed`, `completed: 2026-04-19`, `session_completed_at: 2026-04-19T17:27:43Z`
- REQ-PROC-036 requirements.md: All sections SEC-01–SEC-07, SEC-09, SEC-10 confirmed covered by completed tasks (SEC-08 is explicitly out-of-scope for 0.0.1); `status` updated from `active` → `implemented`
- target_package "Transfer Data Model" has `assigned_release: "0.0.1"` (not null); description freshness question skipped (automated mode)
- `validate_meta.py`: 100 pre-existing errors, 230 warnings — none introduced by this task
- `generate_status_overview.py --full`: STATUS.md regenerated (134 requirements, 300 tasks, 11 releases)
- `complete_task.py`: Folder renamed to `2026-03-29_impl_release-skill-coverage-and-smoke-gate (completed)`

**Next Step**: Task fully closed — no further action required.
