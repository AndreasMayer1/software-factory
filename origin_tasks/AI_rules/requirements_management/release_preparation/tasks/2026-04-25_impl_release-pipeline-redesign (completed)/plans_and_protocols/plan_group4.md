# Plan: Group 4 — release-begin-impl-finalize + claude-automated-mode simplification

Date: 2026-04-25
Task: TASK-PROC-035-08 (Distributed Release Pipeline Redesign)
Group: 4 (depends on Groups 1–3)

This plan is **self-contained**. Implementation agent does NOT need to read the protocol.

---

## Objective

Two skill changes that close the post-creation review loop of the distributed release pipeline:

1. **CREATE** `.claude/skills/release-begin-impl-finalize/skill.md` (new skill, 5 phases)
2. **MODIFY** `.claude/skills/claude-automated-mode/skill.md` (remove Cases A/B, retain C/D, with transition guard)

Then update `.claude/skills/INDEX.md` and `.claude/factory_flows.md` via the `claude-modify-skill` skill.

---

## Dependencies (already satisfied by Groups 1–3)

- Group 1 scripts exist: `scripts/check_task_against_plan.py`, `scripts/reconcile_after_chains.py`, `scripts/find_orchestration_tasks.py`, `scripts/generate_status_overview.py` (already exists)
- Group 2: `release-begin-impl` rewritten; `create_orchestration_task.py` updated with --plan-path / Exit-3 replacement
- Group 3: orchestration task goal.md template self-perpetuates (Cases A/B redundancy is real)

---

## Execution Plan

### Agent 1 (single agent — implementation-engineer): Write both skill files + update index/flows

Order of operations:

1. Create folder `.claude/skills/release-begin-impl-finalize/`
2. Write `.claude/skills/release-begin-impl-finalize/skill.md` with the exact content in **Section A** below
3. Edit `.claude/skills/claude-automated-mode/skill.md` — replace lines 24–79 (the Bootstrap section, from `## Bootstrap` heading through the Case D line, before `## The One Rule`) with the exact content in **Section B** below. Leave all other sections untouched.
4. Invoke `claude-modify-skill` skill twice (or once with both targets) to:
   - Add `release-begin-impl-finalize` entry to `.claude/skills/INDEX.md` (release category, after `release-begin-impl`)
   - Add `release-begin-impl-finalize` entry to `.claude/factory_flows.md` (Release Workflow table, between autorun step 6 and release step 7)
5. Run `dart fix --apply` is NOT applicable (no Dart files).
6. Use `claude-log` skill before exiting.

---

## Section A — Complete content of `.claude/skills/release-begin-impl-finalize/skill.md`

Copy verbatim into the new file:

````markdown
---
name: release-begin-impl-finalize
description: Post-creation review: coverage audit, after-chain reconciliation, semantic validation, user gate, finalize
tools: "*"
model: inherit
---

You run the post-creation review pipeline for an active release. Triggered after autorun reports all packages covered, or when the chain-end validation orchestration task instructs the user to run it.

## Inputs

- `release_version` — auto-detected from `requirements_tasks/RELEASES.md` active entry (the release with `status: active`).

## Scope Note

This skill never reads a feature's `requirements.md` in the orchestrator context. Only Phase 3 semantic agents read requirement files. Phases 1 and 2 are script-driven only.

## Detection vs. Fixing (handoff from validation orchestration task)

Two concerns, one pipeline:

- **Detection** (automated, runs at chain end): the validation orchestration task calls `python3 scripts/reconcile_after_chains.py` WITHOUT `--apply` and writes `validation_report.md`.
- **Fixing** (user-supervised, this skill Phase 2): reads `validation_report.md`, calls `python3 scripts/reconcile_after_chains.py --apply` to fix detected issues. User reviews the applied fixes.

The `validation_report.md` is the handoff document. Semantic correctness is NOT in that report — it belongs to Phase 3 of this skill.

---

## Phase 0 — Bootstrap

1. Read `requirements_tasks/RELEASES.md`; find the entry with `status: active`. Capture `release_version`.
2. Locate `task_creation_plan.md` (the approved plan):
   - Search `requirements_tasks/process/AI_rules/requirements_management/release_preparation/tasks/` for an explore task folder whose `goal.md` has `target_release: <release_version>` AND `status: completed`.
   - The plan lives at `[that_folder]/task_creation_plan.md`. Capture as `plan_path`.
   - If no such plan is found: print a clear error and stop. The skill requires an approved plan.

## Phase 1 — Coverage Audit (script-driven only)

1. Run `python3 scripts/generate_status_overview.py --release <release_version>` and read the output.
2. For every package in the release's `packages:` array, verify ≥1 non-terminal impl task exists. If any package has zero non-terminal impl tasks: list the gaps and STOP. The user must address gaps before re-running the skill.
3. Plan-conformance audit (non-blocking): for each impl task assigned to this release, run:
   ```bash
   python3 scripts/check_task_against_plan.py --task <task_id> --plan <plan_path>
   ```
   Collect results into a single audit report (in-memory or written to a temp file). Surface mismatches to the user as a report. Do NOT block — this is an audit, not a gate (per protocol §2b, Round 3 §3).
4. Do NOT read any feature `requirements.md` in this phase (script-driven only — see protocol §6).

## Phase 2 — After-Chain Reconciliation (script-driven only)

1. If `validation_report.md` exists from the chain-end validation orchestration task, read it (it lists the detected missing/incorrect after-chain entries with the exact remediation command).
2. Run detection mode:
   ```bash
   python3 scripts/reconcile_after_chains.py --release <release_version> --plan <plan_path>
   ```
3. If missing entries are reported:
   - Show the report to the user.
   - Run with `--apply`:
     ```bash
     python3 scripts/reconcile_after_chains.py --release <release_version> --plan <plan_path> --apply
     ```
   - Confirm fixes to the user before proceeding to Phase 3.
4. If no missing entries: print "after-chains clean" and proceed.

## Phase 3 — Semantic Validation (agents only)

1. From `RELEASES.md` active entry, derive the in-scope feature list (each feature has a `requirements.md`).
2. For each feature, gather the impl-task `goal.md` paths (any task with `target_package` matching one of the feature's packages, or `parent_requirement` matching the feature's REQ-ID).
3. Spawn one agent per feature in parallel (N agents). Use this exact prompt template:

   ```
   You are a semantic validator for release <release_version>.

   Read the following files:
   1. <feature_requirements_path> — the feature requirements (ACs)
   2. <list of impl task goal.md paths for this feature>

   For each AC in the requirements:
   - Find the impl task goal.md that covers it (by Objective + Scope text)
   - Check: does the goal.md's Objective + Scope address the AC's intent?
   - Flag ONLY high-confidence semantic mismatches (where the goal.md clearly
     does not address what the AC requires)
   - Do NOT flag stylistic differences, minor wording variations, or cases
     where the goal.md seems to cover it implicitly

   Output: write to release_finalize_semantic/feat_<REQ-ID>.md

   Structure:
   ## Summary
   [1-2 sentence overall verdict: pass / issues found]

   ## AC Coverage
   | AC | Covering Task | Status | Notes |
   |----|---------------|--------|-------|
   | AC-01 | TASK-xxx | OK | |
   | AC-02 | TASK-xxx | MISMATCH | [specific issue] |

   ## High-Confidence Mismatches
   [List only items flagged MISMATCH above, with explanation]
   ```

4. Wait for all N agents to finish. Each agent writes one file under `release_finalize_semantic/feat_<REQ-ID>.md` (relative to the active release's working folder, e.g. the explore task folder or a `releases/<version>/` subfolder — pick the explore task folder for co-location with the plan).
5. Note: orchestrator never reads feature `requirements.md` directly; only the agents do.

## Phase 4 — User Review Gate

1. Read every file under `release_finalize_semantic/`.
2. Build a consolidated summary:
   - Total features reviewed
   - Number of features with issues
   - List of high-confidence mismatches (AC + task + one-line explanation)
   - Path to each per-feature report for deeper review
3. Present to the user. The user must explicitly approve, or request fixes.
4. If fixes are requested: user addresses them (edit goal.md files, add tasks, etc.) and re-runs `/release-begin-impl-finalize`. Skill exits.

## Phase 5 — Finalize

On explicit user approval:

1. Optionally update `requirements_tasks/RELEASES.md`: add `tasks_complete_date: <today>` to the active release entry (ask user; default yes).
2. Run `python3 scripts/generate_status_overview.py` (regenerate `requirements_tasks/STATUS.md`).
3. Invoke `claude-commit` skill to commit the changes.
4. Print exactly:
   ```
   Implementation tasks complete. Run /release to cut the release.
   ```

---

## Key Constraints

- Phase 1 + Phase 2: script-driven only (no inline requirement file reads).
- Phase 3: always agents, one per feature (fan-out + parallelism).
- Orchestrator never reads feature `requirements.md` directly.
- Two user gates exist in the full pipeline: scope+plan approval (in `release-begin-impl` Phase 5) and final review (this skill, Phase 4).
````

Notes for the implementer:
- The frontmatter uses `tools: "*"` (string with asterisk) — match exactly.
- The fenced code block at the very top is opened with four backticks in this plan only because the skill content itself contains triple-backtick code blocks. When writing the actual skill file, use the inner content (start the file with `---` frontmatter line; the outer four-backtick fence is just to display the content here).
- Forbidden sections (do NOT add): `## Testing`, `## Open Questions`, `## Version History`, `## Implementation Roadmap`.
- Inline `(reason)` parentheticals are used where helpful (e.g. "(per protocol §6)"). No Dart-style `///` comments anywhere.

---

## Section B — Replacement Bootstrap section for `.claude/skills/claude-automated-mode/skill.md`

### Surgical edit instructions

The current file is 149 lines. Modify ONLY the Bootstrap section.

**Delete**: lines 24 through 79 inclusive — i.e. from the line `## Bootstrap: Release Build-Out Check` (line 24) through the Case D line (line 79: `**Case D — runnable tasks exist**: Skip bootstrap entirely. Proceed to "Do next task".`).

**Insert** (in place of deleted lines): the exact block below.

**Do NOT touch**:
- Lines 1–23 (frontmatter, intro, `## Detection` section)
- Lines 80+ (`## The One Rule`, `## When Human Input Is Genuinely Needed`, `## When NOT to Use pending_feedback`)

### Replacement block (paste verbatim)

````markdown
## Bootstrap: Release Build-Out Check

Run at session start, before "Do next task":

```bash
python3 scripts/next_tasks.py 2>&1
```

<!-- TRANSITION BLOCK — Cases A and B removed (TASK-PROC-035-08, Group 4)

Removal condition: Cases A and B were removed because the new self-perpetuating
orchestration task template (Group 3) makes them redundant:

- Case A (uncovered ACs → create orchestration task): the chain self-perpetuates
  via create_orchestration_task.py invoked inside each orch task's own ACs. No
  bootstrap trigger is needed to create the next orchestration task.

- Case B (all packages covered → create validation task): when all packages are
  covered, create_orchestration_task.py creates a validation orchestration task
  instead of returning Exit 3. The chain handles it.

GUARD: Do NOT delete this transition block (or re-introduce Cases A/B logic in
any reduced form) until ALL of the following are true:
  1. The new self-perpetuating orchestration task template (Group 3) is deployed.
  2. All in-flight old-template orchestration tasks have reached terminal status.

To verify (2), run:
  python3 scripts/find_orchestration_tasks.py --status pending,in_progress

If that command returns any old-template orch tasks, keep this transition block
in place; the bootstrap is intentionally minimal during the transition cycle.
-->

**Case C — all packages covered, all completed, no open questions**: Check:
   ```bash
   # Any pending impl tasks for active release?
   python3 scripts/next_tasks.py --type impl 2>&1 | head -5
   # Any unanswered questions?
   ls automation/pending_feedback/*/question.md 2>/dev/null
   # Validation report exists?
   find requirements_tasks/ -name "validation_report.md" 2>/dev/null | head -1
   ```
   If no runnable impl tasks AND no unanswered questions AND a validation report exists AND all 0.0.1 packages have non-terminal impl tasks → write release-complete summary to `automation/release_status/<version>_complete.md`:
   ```markdown
   # Release <version> Complete
   Date: <today>
   All packages covered. Impl tasks created and completed. Validation passed. No open questions.
   Next step: Run /release-begin-impl-finalize for final review, then /release to cut the release.
   ```
   Then proceed normally (orchestrator will stop with queue_empty on its own).

**Case D — runnable tasks exist**: Skip bootstrap entirely. Proceed to "Do next task".
````

Critical points the implementer must verify after the edit:
- The "Next step" line in the Case C summary template explicitly mentions `/release-begin-impl-finalize` BEFORE `/release` (this is the behavior change — the old text said only "run `release` skill").
- The HTML comment `<!-- TRANSITION BLOCK ... -->` is preserved verbatim. Its removal-condition wording is load-bearing — future maintainers must see exactly when it is safe to delete.
- Cases A and B are entirely absent from the file.
- The `## Detection`, `## The One Rule`, `## When Human Input Is Genuinely Needed`, `## When NOT to Use pending_feedback` sections are byte-identical to before.

---

## Section C — INDEX.md and factory_flows.md updates (via `claude-modify-skill`)

After both skill files are written, invoke `claude-modify-skill` skill. It owns the INDEX.md / factory_flows.md sync. Pass it:

- Skill name: `release-begin-impl-finalize`
- Action: "register new skill"
- INDEX.md insertion target: "release" category table, immediately after the row for `release-begin-impl`. Suggested row:
  ```markdown
  | **release-begin-impl-finalize** | Post-creation review of an active release: coverage audit, after-chain reconciliation, semantic validation, user gate, finalize |
  ```
  Also add to the Quick Reference table near the top:
  ```markdown
  | Finalize implementation phase of a release | `release-begin-impl-finalize` | `/release-begin-impl-finalize` |
  ```
  And update the "Release Workflow" phase table to insert a new row between Phase C (Autorun) and Phase D (Release):
  ```markdown
  | C2 — Finalize Impl | 6.5 | `release-begin-impl-finalize` | After autorun reports all packages covered; semantic review + user gate before /release |
  ```

- factory_flows.md insertion target: in the Release Workflow section, between the autorun step and the `/release` step. Add a node/row that reflects: "after autorun completes → user runs `/release-begin-impl-finalize` → semantic validation gate → /release".

If `claude-modify-skill` cannot perform both inserts atomically, run it twice (once per target file). Each run should commit independently.

---

## Quality Criteria

- [ ] `.claude/skills/release-begin-impl-finalize/skill.md` exists with the exact content from Section A
- [ ] Frontmatter has `name`, `description`, `tools: "*"`, `model: inherit` — and nothing else
- [ ] All 5 phases present and in order; Phase 0 (bootstrap that locates plan_path) present
- [ ] No forbidden sections (`## Testing`, `## Open Questions`, `## Version History`, `## Implementation Roadmap`)
- [ ] Phase 3 agent prompt template included verbatim
- [ ] `claude-automated-mode/skill.md` no longer contains "Case A" or "Case B" instruction blocks
- [ ] Transition HTML comment with removal-condition guard is present in `claude-automated-mode/skill.md`
- [ ] Case C "Next step" line references `/release-begin-impl-finalize` before `/release`
- [ ] `## Detection`, `## The One Rule`, `## When Human Input Is Genuinely Needed`, `## When NOT to Use pending_feedback` sections in `claude-automated-mode/skill.md` are byte-identical to the pre-edit version
- [ ] `INDEX.md` lists `release-begin-impl-finalize` (Quick Reference + release category + Release Workflow table)
- [ ] `factory_flows.md` references `release-begin-impl-finalize` between autorun and `/release`
- [ ] `claude-log` invoked before exit

---

## Risks

- **Risk 1**: Implementer accidentally removes the transition HTML comment, leading future maintainers to delete Case-A handling prematurely while old-template orchestration tasks still exist.
  - Mitigation: Section B explicitly calls out the comment as load-bearing. Quality criteria check verifies its presence.

- **Risk 2**: `claude-modify-skill` may not yet know about the new "C2 — Finalize Impl" row format in INDEX.md's Release Workflow table.
  - Mitigation: Provide the exact row text in Section C. If `claude-modify-skill` adds only the category-table entry, the implementer adds the Quick Reference row and Release Workflow row by direct edit, then re-runs `claude-modify-skill --validate` if available.

- **Risk 3**: Phase 3 agents need a deterministic mapping from feature → impl task goal.md paths. The skill currently relies on `target_package` / `parent_requirement` matching, which assumes tasks set those fields correctly.
  - Mitigation: Phase 1 already runs `check_task_against_plan.py` for every impl task; that script's audit will surface any task with mismatched `target_package`. If Phase 1 audit shows widespread mismatches, the user is expected to fix them before Phase 3 has reliable input. Phase 3 itself does not need a new mechanism.

- **Risk 4**: The validation orchestration task may not yet have run when the user invokes `/release-begin-impl-finalize` (e.g. user runs it manually before the chain finishes), so `validation_report.md` may be absent.
  - Mitigation: Phase 2 step 1 says "if `validation_report.md` exists" — its absence is non-fatal; the skill still runs detection mode itself. The handoff is an optimization, not a requirement.

---

## Execution Summary

- **Number of agents needed**: 1 (single implementation-engineer agent).
- **Order**: write new skill file → edit claude-automated-mode → run `claude-modify-skill` → log → exit.
- **Estimated effort**: S (small — three file edits, one skill invocation).
- **Sequential dependency on prior groups**: Group 1 (scripts must exist), Group 2 (release-begin-impl rewritten), Group 3 (orchestration template self-perpetuates) — all assumed complete before Group 4 starts.
