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

- **Detection** (automated, runs at chain end): the validation orchestration task calls `python3 scripts/tasks/reconcile_after_chains.py` WITHOUT `--apply` and writes `validation_report.md`.
- **Fixing** (user-supervised, this skill Phase 2): reads `validation_report.md`, calls `python3 scripts/tasks/reconcile_after_chains.py --apply` to fix detected issues. User reviews the applied fixes.

The `validation_report.md` is the handoff document. Semantic correctness is NOT in that report — it belongs to Phase 3 of this skill.

---

## Phase 0 — Bootstrap

1. Read `requirements_tasks/RELEASES.md`; find the entry with `status: active`. Capture `release_version`.
2. Locate `task_creation_plan.md` (the approved plan):
   - Search `requirements_tasks/process/AI_rules/requirements_management/release_preparation/tasks/` for an explore task folder whose `goal.md` has `target_release: <release_version>` AND `status: completed`.
   - The plan lives at `[that_folder]/task_creation_plan.md`. Capture as `plan_path`.
   - If no such plan is found: print a clear error and stop. The skill requires an approved plan.

## Phase 1 — Coverage Audit (script-driven only)

1. Run `python3 scripts/artifacts/generate_status_overview.py --release <release_version>` and read the output.
2. For every package in the release's `packages:` array, verify ≥1 non-terminal impl task exists. If any package has zero non-terminal impl tasks: list the gaps and STOP. The user must address gaps before re-running the skill.
3. Plan-conformance audit (non-blocking): for each impl task assigned to this release, run:
   ```bash
   python3 scripts/tasks/check_task_against_plan.py --task <task_id> --plan <plan_path>
   ```
   Collect results into a single audit report (in-memory or written to a temp file). Surface mismatches to the user as a report. Do NOT block — this is an audit, not a gate (per protocol §2b, Round 3 §3).
4. Do NOT read any feature `requirements.md` in this phase (script-driven only — see protocol §6).

## Phase 2 — After-Chain Reconciliation (script-driven only)

1. If `validation_report.md` exists from the chain-end validation orchestration task, read it (it lists the detected missing/incorrect after-chain entries with the exact remediation command).
2. Run detection mode:
   ```bash
   python3 scripts/tasks/reconcile_after_chains.py --release <release_version> --plan <plan_path>
   ```
3. If missing entries are reported:
   - Show the report to the user.
   - Run with `--apply`:
     ```bash
     python3 scripts/tasks/reconcile_after_chains.py --release <release_version> --plan <plan_path> --apply
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
2. Run `python3 scripts/artifacts/generate_status_overview.py` (regenerate `requirements_tasks/STATUS.md`).
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
