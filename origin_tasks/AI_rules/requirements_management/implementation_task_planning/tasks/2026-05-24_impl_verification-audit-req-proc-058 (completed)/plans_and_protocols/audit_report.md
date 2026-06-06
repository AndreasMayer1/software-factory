# Audit Report: REQ-PROC-058 Implementation Verification

**Date**: 2026-05-25
**Task**: TASK-PROC-058-06
**Auditor**: Automated session (claude-sonnet-4-6 / 299e58fa)
**Scope**: AC-01–AC-13, AC-15–AC-17 (AC-14 excluded — under REQ-PROC-035)
**Method**: Read .claude/skills/task-derive-from-requ/SKILL.md, task-create/SKILL.md, task-create-code/SKILL.md; verify each AC against skill content; check referenced scripts exist.

---

## Summary

| Metric | Value |
|--------|-------|
| ACs audited | 16 (of 17 — AC-14 excluded) |
| Fully covered | 16 (100%) |
| Partial | 0 |
| Not covered | 0 |
| Expected gaps (not blocking) | 1 (detect_cross_ref_gaps.py absent — fallback active by design) |
| Blocking gaps | 0 |

**Overall verdict: PASS. All 16 audited ACs are implemented. No blocking gaps. Task complete.**

---

## Per-AC Findings

### AC-01 — Coverage matrix at decomposition time
- **Requirement**: Every requirement decomposed into tasks must have a coverage matrix. Zero-coverage AC is a blocking error.
- **Implementation**: task-derive-from-requ Phase 3 "Coverage matrix (AC-01, blocking gate)" — produces a table mapping every AC to ≥ 1 task. Phase 3 validation: "100% AC coverage (hard error if not)" blocks Phase 5.
- **Evidence**: `.claude/skills/task-derive-from-requ/SKILL.md` Phase 3, coverage matrix template and validation checks section.
- **Status**: ✓ COVERED

### AC-02 — Verification task is mandatory
- **Requirement**: Every decomposition includes ≥ 1 verification task matching the requirement type (code→test, process→audit, doc→review).
- **Implementation**: task-derive-from-requ Phase 3 "Verification task (AC-02, mandatory)" with type-matching table. Phase 3 validation: "Verification task present (hard error if not)".
- **Evidence**: `.claude/skills/task-derive-from-requ/SKILL.md` Phase 3 Verification task section.
- **Status**: ✓ COVERED

### AC-03 — Sizing signals on every planned task
- **Requirement**: Each planned task carries REQ-PROC-001 sizing metadata (S1–S4, opus_recommended reflecting S1–S4 composition).
- **Implementation**: task-derive-from-requ Phase 3 "Sizing signals (S1–S4 per REQ-PROC-001)" table with explicit computation per signal. `opus_recommended` formula: "S1>60 OR (S1>30 AND S4) OR S3 OR (S4 with >3 files) → true".
- **Evidence**: `.claude/skills/task-derive-from-requ/SKILL.md` Phase 3 sizing signals table.
- **Status**: ✓ COVERED

### AC-04 — Plan-before-create gate
- **Requirement**: Coverage matrix and task plan produced and validated before any task is created. User reviews and approves before task-create or task-create-code is called.
- **Implementation**: task-derive-from-requ Phase 4 "Interactive mode: present plan + coverage matrix. User approves, modifies, or rejects. No task created until approved." Phase 5: "For each approved task in plan order." Automated mode: auto-accept; coverage matrix is the gate; plan logged to plans_and_protocols/.
- **Evidence**: `.claude/skills/task-derive-from-requ/SKILL.md` Phase 4 and Phase 5.
- **Status**: ✓ COVERED

### AC-05 — Wraps task-create and task-create-code
- **Requirement**: Decomposition skill delegates individual task creation to task-create (non-code) or task-create-code (Dart code). Existing creation primitives preserved — decomposition skill wraps them, not replaces.
- **Implementation**: task-derive-from-requ Phase 5: "Code tasks → invoke task-create-code with plan-driven values; Non-code tasks → invoke task-create with plan-driven values." The skill passes pre-computed plan values (covers_acs, effort, layer, after, opus_recommended, target_package, implementation_notes).
- **Evidence**: `.claude/skills/task-derive-from-requ/SKILL.md` Phase 5 steps 1 and 2.
- **Status**: ✓ COVERED

### AC-06 — Enforcement-creates-violations detection
- **Requirement**: When a planned task creates enforcement mechanisms (scripts, gates, lint rules, checkers), automatically propose a companion remediation task depending on the gate-creation task, with scope: "run [gate], fix all violations, confirm zero output."
- **Implementation**: task-derive-from-requ Phase 2 step 3: "Enforcement-creates-violations detection (AC-06): if a task's scope includes creating scripts/gates/lint rules/checkers → propose a companion remediation task" with `after: [gate-creation task]`, scope text, and `covers` matching gate task.
- **Evidence**: `.claude/skills/task-derive-from-requ/SKILL.md` Phase 2 step 3.
- **Status**: ✓ COVERED

### AC-07 — Dependency graph with correct ordering
- **Requirement**: Decomposition produces dependency graph as `after:` chains. No circular dependencies. Ordering reflects logical sequence (infrastructure before consumers, enforcement before remediation).
- **Implementation**: task-derive-from-requ Phase 3 field "after: Dependency list — logical ordering (infrastructure before consumers, enforcement before remediation)." Phase 3 validation: "No circular dependencies in after: chains."
- **Evidence**: `.claude/skills/task-derive-from-requ/SKILL.md` Phase 3 table (after row) and validation checks.
- **Status**: ✓ COVERED

### AC-08 — Post-creation validation
- **Requirement**: After all tasks created, a post-creation validation step runs `scripts/requirements/coverage_report.py` and confirms 100% AC coverage. Any discrepancy is a blocking error.
- **Implementation**: task-derive-from-requ Phase 6: `python3 scripts/requirements/coverage_report.py | grep "REQ-XXX" -A 20`. "Confirm 100% coverage post-creation. Print final coverage matrix. Any discrepancy between plan and actual → blocking error." Script `scripts/requirements/coverage_report.py` verified to exist.
- **Evidence**: `.claude/skills/task-derive-from-requ/SKILL.md` Phase 6; script existence confirmed via `ls`.
- **Status**: ✓ COVERED

### AC-09 — Incremental decomposition for partially-covered requirements
- **Requirement**: Skill handles partially-covered requirements by reading existing tasks, computing current coverage, planning only for uncovered ACs. When existing tasks have empty `covers:` fields, infer coverage from goal.md body and propose `covers:` updates before planning new tasks.
- **Implementation**: Phase 1 steps 3–4: "Compute current coverage: which ACs have ≥ 1 task, which have zero." Phase 1.4 "Covers-field repair (AC-09)": reads goal.md bodies for tasks with empty covers, infers from scope description + task name, proposes updates. Interactive: presents for confirmation. Automated: auto-applies confidence ≥ high; question.md for ambiguous cases.
- **Evidence**: `.claude/skills/task-derive-from-requ/SKILL.md` Phase 1 steps 3 and 4; Phase 1 "Mode decision" logic.
- **Status**: ✓ COVERED

### AC-10 — task-create warns on uncovered ACs (redirect)
- **Requirement**: When task-create or task-create-code is invoked directly in standalone mode on a requirement with uncovered ACs, redirect to task-derive-from-requ. Exempt: bugfix, explore/define, plan-driven invocations. Automated mode: never auto-override.
- **Implementation**:
  - task-create §3c "Redirect Logic (AC-10) — Standalone Mode Only": trigger conditions (standalone + impl/verify type + requirement has ACs with zero coverage), redirect action, exemptions, automated mode rule ("never auto-override — always redirect").
  - task-create-code has identical "Redirect Logic (AC-10) — Standalone Mode Only" section with same trigger logic.
- **Evidence**: `.claude/skills/task-create/SKILL.md` §3c; `.claude/skills/task-create-code/SKILL.md` Redirect Logic section.
- **Status**: ✓ COVERED

### AC-11 — task-create and task-create-code accept plan-driven inputs
- **Requirement**: Both skills accept pre-computed values from a task creation plan. In plan-driven mode, provided values replace discovery and coverage-asking phases. For task-create-code, file-level scope analysis still runs to refine sizing.
- **Implementation**:
  - task-create-code Phase 0A: reads plan entry via `parse_task_creation_plan.py`, uses plan values as authoritative defaults (covers_acs, effort, layer, after, task_type, implementation_notes, opus_recommended). File-level Phase 2 still runs to refine (AC-15).
  - task-create "Plan-driven mode": skips coverage-asking (step 3b), package prompting (step 3.4), and user location-confirmation (step 4); uses plan values directly.
- **Evidence**: `.claude/skills/task-create-code/SKILL.md` Phase 0A; `.claude/skills/task-create/SKILL.md` "Operating Modes → Plan-driven mode."
- **Status**: ✓ COVERED

### AC-12 — Shared plan format
- **Requirement**: Plan format shared between task-derive-from-requ and release-begin-impl Phase 2c. Both produce plans consumable by task-create-code via same Phase 0A path. Plan entry fields: task_name, req_path, requirements_version, covers_acs, effort, layer, after, task_type, implementation_notes, opus_recommended, target_package.
- **Implementation**: task-derive-from-requ Phase 4 "Plan file format (SEC-04 unified format)" defines YAML structure with all required fields. Stale-plan detection via `requirements_version.commit` (Phase 0A step 3.5). Script `scripts/tasks/parse_task_creation_plan.py` verified to exist.
- **Evidence**: `.claude/skills/task-derive-from-requ/SKILL.md` Phase 4 plan format YAML; `.claude/skills/task-create-code/SKILL.md` Phase 0A step 2.
- **Status**: ✓ COVERED

### AC-13 — Code tasks describe WHAT not HOW
- **Requirement**: Code tasks (goal.md created by task-create-code) describe WHAT to implement — not HOW. Implementation plans with concrete code changes created fresh at execution time.
- **Implementation**: task-create-code "Philosophy: Tasks contain WHAT to implement, not HOW." Template includes explicit "Note: This task describes WHAT to implement, not HOW." Phase 3.3 Scope Overview field description: "Brief summary from Phase 2 scan — NOT concrete code changes."
- **Evidence**: `.claude/skills/task-create-code/SKILL.md` Philosophy section; Phase 3.3 template note.
- **Status**: ✓ COVERED

### AC-14 — release-begin-impl Phase 2c
- **Status**: EXCLUDED — under REQ-PROC-035. Verified by REQ-PROC-035's own verification task.

### AC-15 — No duplicated computation
- **Requirement**: Two patterns: "compute once, trust downstream" (coverage matrix, verification task, user review) and "estimate upstream, refine downstream" (sizing, effort, dependencies). Standalone mode is the only case where downstream computes all concerns itself.
- **Implementation**: task-derive-from-requ "No-Duplication Enforcement (AC-15)" section with explicit two-pattern table. task-create-code Phase 2.3 escalation: if file analysis reveals significantly larger task than plan estimate, escalates (interactive: ask user; automated: question.md). task-create plan-driven mode skips per-task coverage and confirmation.
- **Evidence**: `.claude/skills/task-derive-from-requ/SKILL.md` "No-Duplication Enforcement" section; `.claude/skills/task-create-code/SKILL.md` Phase 2.3 plan-driven escalation.
- **Status**: ✓ COVERED

### AC-16 — Cross-package ACs produce tasks in their own package
- **Requirement**: When ACs within a single requirement have different target_package values, task-derive-from-requ groups tasks by AC package. Coverage matrix groups by package. A single decomposition run may produce tasks in multiple packages.
- **Implementation**: task-derive-from-requ Phase 2 step 5 "Cross-package handling (AC-16): group tasks by AC target_package. A task covers ACs from one package; tasks in different packages are separate. Coverage matrix grouped by package." Coverage matrix template includes "Package" column.
- **Evidence**: `.claude/skills/task-derive-from-requ/SKILL.md` Phase 2 step 5; Phase 3 coverage matrix template.
- **Status**: ✓ COVERED

### AC-17 — Cross-reference completeness gate before task creation
- **Requirement**: Before producing the task plan, task-derive-from-requ verifies cross-reference completeness. Detects gaps via script (or fallback grep). Classifies gaps (hard/semantic/ignore). Applies via spawned requ-explore agent. Blocks until gate passes. Phase 2 must not start until all non-ignored candidates are applied.
- **Implementation**: task-derive-from-requ Phase 1.5 is a 5-subsection gate:
  - **1.5.1 Detect**: Preferred path: `detect_cross_ref_gaps.py`; fallback (script absent): inline keyword-grep pattern. **`detect_cross_ref_gaps.py` does NOT exist yet** — fallback is active. This is expected: the skill explicitly documents "Fallback — script absent (the REQ-PROC-045 impl task has not landed yet)." TASK-PROC-045-07 will deliver the script.
  - **1.5.2 Classify**: Interactive (AskUserQuestion: hard/semantic/ignore) and automated (cross_ref_gaps.md + question.md + terminate) paths.
  - **1.5.3 Apply**: Spawns general-purpose agent with requ-explore semantics; detailed prompt template; `run_in_background: true` with heartbeat.
  - **1.5.4 Resume**: Re-runs detection after agent commits; non-empty residual → hard error (interactive) or question.md (automated).
  - **1.5.5 Waiver**: If all candidates ignored, Apply is skipped; protocol records reasons.
  - **Block-and-resume contract**: "Phase 2 MUST NOT begin while any non-ignored candidate remains unapplied."
- **Evidence**: `.claude/skills/task-derive-from-requ/SKILL.md` Phase 1.5 (all 5 subsections + contract).
- **Expected placeholder**: `scripts/requirements/detect_cross_ref_gaps.py` absent — fallback grep active per design. Not a blocking gap.
- **Status**: ✓ COVERED (with expected placeholder for script)

---

## Section Coverage

| Section | AC-01 | Notes |
|---------|-------|-------|
| SEC-01 (Skill Boundary) | ✓ | Three-skill boundary defined in each SKILL.md description and behavior; orchestrate-vs-create split enforced |
| SEC-02 (Workflow Integration) | ✓ | Quick/Full/Plan-driven modes + W1–W5 paths; redirect logic in task-create and task-create-code |
| SEC-03 (Code Task Creation) | ✓ | task-create-code plan-driven (Phase 0A) and standalone (Phase 0B) modes; Phase 6 conformance check |
| SEC-04 (Unified Plan Format) | ✓ | Plan YAML format defined in task-derive-from-requ Phase 4; consumed by task-create-code via parse_task_creation_plan.py |

---

## Confirmed Gaps

**None.** All 16 audited ACs are fully implemented in the three skills.

---

## Expected Placeholders (not blocking gaps)

| Item | Status | Owning task |
|------|--------|-------------|
| `scripts/requirements/detect_cross_ref_gaps.py` | Absent; fallback grep active per skill design | TASK-PROC-045-07 |

The skill explicitly documents this fallback and its expected lifetime ("the REQ-PROC-045 impl task has not landed yet"). The fallback produces the same output — a list of candidate REQ-IDs. No behavioral difference until the script lands.

---

## Audit Reproducibility

To reproduce this audit:
1. Read the three skill files: `.claude/skills/task-derive-from-requ/SKILL.md`, `.claude/skills/task-create/SKILL.md`, `.claude/skills/task-create-code/SKILL.md`
2. For each AC, locate the implementing section by searching for the AC keyword or phase number
3. Run `ls scripts/requirements/coverage_report.py scripts/tasks/parse_task_creation_plan.py scripts/tasks/create_orchestration_task.py scripts/tasks/propose_after.py scripts/tasks/check_task_against_plan.py` to verify script existence
4. The findings table above should be reproducible from the same skill file versions
