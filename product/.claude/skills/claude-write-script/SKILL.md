---
name: claude-write-script
description: Create or modify a script in /scripts AND run Python quality gates. MANDATORY for EVERY edit to scripts/**/*.py or scripts/**/*.ps1 — no exceptions for one-line fixes, "trivial" edits, code-bugfix slim mode, or task-resolve. If you are about to Edit/Write a file under scripts/, invoke this skill first.
tools: [Read, Write, Edit, Grep, Glob, Bash]
model: inherit
---

You create or modify scripts in `scripts/`, run the Python quality gates on `.py` changes (REQ-PROC-051), and keep CLAUDE.md Section 11 accurate.

## Scope (read this before anything else)

This skill is the **only** sanctioned entry point for modifying files under `scripts/`. It applies to:

- New script creation
- Any modification to an existing script — including renames, one-line fixes, typo corrections, import reordering, comment-only edits
- Bugfix-driven script edits (regardless of what other skill / workflow triggered them)

If you find yourself about to call `Edit` or `Write` on a path matching `scripts/**/*.py` or `scripts/**/*.ps1` without having invoked this skill, stop and invoke it. There is no "small edit" exception.

## Timezone rule (mandatory for all scripts)

All timestamps written to files or stdout MUST use the OS local timezone — never bare UTC unless the value is explicitly stored for machine-to-machine exchange (e.g. state.json).

- **Python**: use `datetime.now().astimezone()` (not `datetime.now()` or `datetime.utcnow()`); format with `.strftime(...)` after
- **PowerShell**: use `Get-Date` (already local); never `[datetime]::UtcNow` for display
- **Displaying a UTC-stored value**: call `.astimezone()` / `.ToLocalTime()` before formatting

Mixing naive-local and UTC datetimes across scripts causes incorrect comparisons. Apply this rule even when modifying an existing script that already uses UTC for display.

## Steps

0. **New scripts only — determine domain subfolder** (skip for modifications to existing scripts):

   Scripts live in `scripts/<domain>/`, never flat at `scripts/` top level.
   Sole top-level exception: `scripts/validate_scripts_org.py`.

   Choose domain by answering in order:
   1. Windows-host-only? (`.ps1`, or Python requiring Windows builds/screen-capture/`pwsh`) → `windows/`
   2. Belongs to a preserved subsystem? (automation, task_ordering, integration_test_runner, tests) → that subsystem folder
   3. Otherwise assign by domain:
      - Works on tasks (create/query/complete/order tasks) → `tasks/`
      - Works on requirements (IDs, coverage, validation, package sync) → `requirements/`
      - Generates a derived file with a fixed canonical output path → `artifacts/`
      - Works on user flows, personas, or scribbles → `user_needs/`
      - Works on the release pipeline → `release/`
      - Shared infrastructure utility with no domain home (≤5 scripts total in util/) → `util/`

   **Naming**: `verb_noun[_qualifier].ext`, lowercase snake_case.
   Verb prefix must match lifecycle:
   - Read-only: `check_`, `find_`, `is_`, `next_`, `top_`, `propose_`, `validate_`, `should_`, `summarize_`, `parse_`, `goal_preview`
   - File-generating: `generate_`, `aggregate_`, `merge_`, `process_`
   - State-modifying: `allocate_`, `sync_`, `complete_`, `execute_`, `reconcile_`, `create_`, `migrate_`, `update_`

   Place the script at `scripts/<domain>/verb_noun.ext`.

0b. **Windows-host script rules** (apply when domain is `windows/`):

   - **Path resolution (REQ-PROC-054 AC-16)**: the script MUST use the shared helper (`find_project_root.ps1` dot-sourced for PS; `find_project_root.py` imported for Python) to obtain the project root — NOT hardcode a path or derive it solely from `$PSScriptRoot` / `Path(__file__).parents[N]`. The helper provides 3-level precedence: explicit param → co-located config → in-repo auto-derivation. A script that skips the config lookup is non-conforming.
   - **Test placement (REQ-PROC-043 AC-08 / REQ-PROC-054 AC-18)**: tests for windows scripts go in `scripts/windows/tests/` (Pester `*.Tests.ps1`, Python helper tests), NOT beside the script. Step 2 "Python only" does not govern windows test placement — this rule does.

0c. **Read `doc/python/` guidelines** (Python only — skip for `.ps1`):

   Before writing or modifying any Python under `scripts/`, read:
   - `doc/python/README.md` — entry point, tier overview, gate summary
   - `doc/python/anti_patterns.md` — named failure modes (god functions, magic values, hand-rolled YAML, clock bypass, broad except, etc.)
   - `doc/python/architecture.md` — structural rules incl. function-size/complexity limits and decomposition strategies
   - For TIER A modules: also `doc/python/dependency_injection.md`

   These files are short (~150 lines each). Reading them costs less than producing code that violates their judgment-level rules.

1. **Do the script work** — create the new script or apply the requested modification to the existing one

2. **Write or update tests for any behavioral change** (Python only):

   A behavioral change is anything that alters what the code does for some input: new/changed branch, new pattern match, changed return value, new guard, bugfix. Pure formatting, import reordering, comment-only edits, and rename-only changes are exempt.

   - If the script already has a test file (e.g. `scripts/automation/tests/test_orchestrate.py`, `scripts/tests/test_*.py`), add or update a test that exercises the changed behavior — and that would FAIL against the pre-change code. This is mandatory; a bugfix without a regression test is incomplete.
   - If a new script has non-trivial logic and no test file exists, create one next to the existing test suite for its domain.
   - Prefer testing pure functions directly (the cheapest, most durable coverage); the existing suites inject fakes via `OrchestratorDeps`-style boundaries for I/O.

   Skip only when the change is genuinely non-behavioral (see exemptions above) — state which exemption applies when you skip.

3. **Run Python quality gates** (skip for non-`.py` changes):

   If any changed file matches `scripts/**/*.py`, run:
   ```bash
   scripts/quality/check_python_gates.sh
   ```
   This is the G1–G5 gate runner from REQ-PROC-051 (AC-11). Five gates: G1 lint (ruff), G2 type (mypy), G3 tests (pytest), G4 no hand-rolled YAML, G5 print() discipline.

   **Interpreting the result** (per CLAUDE.md Python gates section):
   - Compare failures against develop's baseline — `develop` itself currently fails G4 and may fail others until TASK-PROC-051-04 lands.
   - Block only on findings YOUR change introduced. If a gate that already failed on develop still fails the same way, that is not a regression for this change.
   - If your change touched a file that previously had no findings and now has findings, that IS a new finding — block on it.

   **On new findings — back-pressure protocol** (REQ-PROC-046 §Back-Pressure Protocol, inherited by REQ-PROC-051):
   - 5-cycle bound: fix the new finding, re-run the full gate set (not just the failing gate), repeat
   - After 5 failed cycles, escalate via `automation/pending_feedback/<TASK-ID>/` (do not silently relax the gate or the rule)
   - Never weaken `pyproject.toml`, ruff/mypy config, or REQ-PROC-051 ACs during the same task to make a failure go away — that is the silent-acceptance prohibition

   PowerShell changes (`scripts/**/*.ps1`) skip this step — REQ-PROC-051 governs Python only.

4. **Decide whether CLAUDE.md Section 11 needs an update** — apply these rules in order:

   **Rule 1 — Generated files** (mandatory): If the script produces a file that must not be manually edited, add one row to the "Generated Files" table: `| output_path | script_path |`.

   **Rule 2 — Problem→script lookup** (mandatory): If the script provides general-purpose analytical capability that replaces `grep`/`find`/manual file reading for a recurring question (e.g. "what tasks run before X?", "what's blocked?", "what's the coverage?"), add one row to the "Use Scripts, Not Grep" table. Phrase the entry as a need/problem, not a script description.

   **Rule 3 — Skills-only exclusion**: If the script is only ever invoked within a specific skill and has no ad-hoc use outside that skill, do NOT add it to CLAUDE.md. The skill owns the knowledge.

   **Rule 4 — No flags or usage details**: Never document flags, arguments, or detailed usage in CLAUDE.md. The LLM calls `<script> --help` when it needs to know how to use a script.

   **Rule 5 — Litmus test**: Ask "Would the LLM reach for `grep`/`find` instead of this script?" If yes → Rule 2 applies. If no → skip.

5. **Update CLAUDE.md Section 11** only if Rule 1 or Rule 2 applies. One line per entry, no more.
6. **Tell the user** what was done, the gate-run result (if Python), and whether CLAUDE.md was updated or not (and why)
