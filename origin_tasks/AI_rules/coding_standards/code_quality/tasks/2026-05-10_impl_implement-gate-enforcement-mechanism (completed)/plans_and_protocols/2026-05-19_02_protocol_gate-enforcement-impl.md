# Protocol: Implement gate enforcement mechanism

Date: 2026-05-19
Session: f3baf030-84f3-4593-9241-cee2bf64864a (gmail, automated mode)

## Actions taken

1. **Plan written** to
   `plans_and_protocols/2026-05-19_01_plan_gate-enforcement-mechanism.md`.

2. **Created `verify-quality` skill** at
   `.claude/skills/verify-quality/skill.md`. The skill:
   - Detects the active task via `status: in_progress` grep.
   - Reads/initializes a five-cycle counter at
     `<task-folder>/plans_and_protocols/cycle_state.json`.
   - Pre-flight: refuses to run on a dirty tree without `--allow-dirty`.
   - Decides which gate set applies (Dart-only, Python-only, or both) based
     on the `git diff --name-only HEAD` output.
   - Per-change gates: `flutter analyze` (via win bridge),
     `scripts/quality/check_quality_gates.sh` (aggregate runner that
     bundles SP1–SP4, AC11, AC12, complexity, type-naming, arch-imports,
     no-direct-styling, test-smells, folder-taxonomy),
     `check_critical_path_coverage.py`, and `check_python_gates.sh` for
     scripts/ changes.
   - Release-cadence gates: `check_bundle_size.py`,
     `check_test_determinism.sh`.
   - Spawns the `quality-checker` agent for structural review.
   - On RED at cycles 1–4: increments the counter, writes a structured
     failure summary, exits non-zero.
   - On RED at cycle 5: uses the project's existing pending_feedback
     escalation (`automation/pending_feedback/<TASK_ID>/question.md` +
     copy of `TEMPLATE_answer.md`), then terminates via
     `scripts/automation/terminate_session.sh`.
   - On GREEN: deletes `cycle_state.json` and exits 0.
   - Bypass: `SKIP_QUALITY_GATES=1` short-circuits with a stderr warning.
   - Contains a self-test stanza (smoke test) covering the full chain.

3. **Extended `.claude/agents/quality-checker.md`**:
   - Added cadence flag (`--per-change` default, `--release` for the heavy set).
   - Added Phase 1.5 (gate execution) — the agent now invokes the same
     scripted gates as the skill, on top of its existing structural review.
   - Defined an explicit blocking output contract: the final line must be
     one of `STATUS: GREEN`, `STATUS: YELLOW`, `STATUS: RED — <reason>`.
   - Updated Phase 3 Output to match the new contract.

4. **Extended `.claude/settings.json`**:
   - New `Stop` hook: runs `scripts/quality/check_quality_gates.sh` when
     any `lib/`, `test/`, or `integration_test/` file was modified; on
     non-zero, emits `hookSpecificOutput.additionalContext` telling the
     LLM to enter the back-pressure protocol via `verify-quality`. Skipped
     when `SKIP_QUALITY_GATES=1`.
   - New `PreToolUse(Bash:"git commit*")` hook: runs the same aggregate
     gate runner; on non-zero, denies the Bash invocation with
     `permissionDecision: "deny"` and a clear bypass-with-authorization
     message. Skipped when `SKIP_QUALITY_GATES=1`.
   - Both hook scripts validated with `bash -n`.

5. **Extended `.claude/skills/task-complete/skill.md`**:
   - Added Step 2a: in code-change mode, invoke `verify-quality` before
     marking the task complete; refuse completion on RED. References
     REQ-PROC-046 AC-10.

6. **Updated `.claude/skills/INDEX.md`**:
   - Added `verify-quality` to the Quick Reference table.
   - Added `verify-quality` row to the task-* category table.

7. **Updated `.claude/factory_flows.md`**:
   - Replaced the `quality-checker validates against doc/` arrow label with
     `verify-quality (blocking) → quality-checker against doc/` so the
     diagram reflects the new chain.

## Acceptance criteria check (mechanism-level)

| AC | Status | Evidence |
|----|--------|----------|
| Agent invokes every per-change gate; release behind a flag | DONE | quality-checker.md Phase 1.5 + cadence flag |
| Agent exits non-zero on RED via STATUS line | DONE | quality-checker.md output contract |
| verify-quality skill exists with five-cycle counter | DONE | .claude/skills/verify-quality/skill.md Steps 2,5,6 |
| CLAUDE.md and INDEX.md references resolve | DONE | INDEX.md table edits; CLAUDE.md unchanged (skill file now exists at the referenced path) |
| Stop hook runs verify-quality when lib/test changed | DONE | settings.json Stop hook |
| PreToolUse(Bash:"git commit*") halts on RED | DONE | settings.json PreToolUse Bash matcher |
| task-complete refuses on RED | DONE | task-complete/skill.md Step 2a |
| Bypass mechanism documented | DONE | verify-quality skill.md "Bypass" section + hook code respects `SKIP_QUALITY_GATES=1` |
| Smoke-test stanza demonstrates the full chain | DONE | verify-quality skill.md Step 7 |
| Counter resets on task transition | DONE BY DESIGN | counter file lives inside the active task's plans_and_protocols/; new task ⇒ new folder ⇒ fresh counter |

## Out-of-scope items (per goal.md)

- Implementations of individual gate scripts — owned by sibling tasks
  (TASK-PROC-046-03 through -05, TASK-PROC-052-01, TASK-PROC-002-02,
  TASK-PROC-002-03), all already completed.
- Caching of unchanged inputs for hook performance — follow-up.
- CI / GitHub Actions integration — separate concern; settings.json hooks
  suffice for solo-dev use.
- The CLAUDE.md prose update (back-pressure protocol description) is the
  deliverable of TASK-PROC-046-06; this task only had to make the
  references resolve.

## Related tasks

- TASK-PROC-046-06 (CLAUDE.md back-pressure prose): superseded note added
  to its scope; should add this task to its `after:` list during its
  pickup.
