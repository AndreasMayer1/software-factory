---
task_id: TASK-PROC-045-05
type: impl
parent_requirement: REQ-PROC-045
urgency: 3
urgency_reason: U3-TECH-DEBT
impact: 4
impact_reason: I4-ENAB
status: pending
effort: XS
created: 2026-04-26
after: [TASK-PROC-045-02]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-07]
  sections: []
scope_description: "Add whole-corpus structure validation call to release-begin-impl Phase 0 pre-flight as a blocking check"
release_description: ""
requirements_version:
  commit: ""
  file: ../../requirements.md
---

# Goal: Integrate Whole-Corpus Structure Validation into release-begin-impl Phase 0

## Objective

Add a single blocking step to `release-begin-impl` Phase 0 (Bootstrap) that runs `scripts/validate_epic_requirements.py` (or its renamed successor) against the entire `requirements_tasks/` corpus. If violations are reported, the release-begin-impl flow aborts with a clear message listing the violations and instructing the user to fix them before proceeding.

## Scope

### In Scope
- `.claude/skills/release-begin-impl/skill.md`: Phase 0 addition only — one new step, minimal change
- The check is whole-corpus (all of `requirements_tasks/`), not scoped — release start demands a clean structure project-wide
- The step must be **blocking**: violations cause an abort, not a warning

### Out of Scope
- Changes to any other phase of release-begin-impl
- Fixing pre-existing violations (those must be resolved by the user separately before release can proceed)
- Changes to the validation script itself (TASK-PROC-045-02)

## Exact Change Required

In `.claude/skills/release-begin-impl/skill.md`, find Phase 0 (Bootstrap) and add the following step **before** the existing completeness / coverage checks:

---
**Step: Requirements Structure Validation**

Run:
```bash
python3 scripts/validate_epic_requirements.py
```

If the script exits non-zero:
- Display the full violation list to the user
- Output: "Release cannot proceed: requirements structure violations found. Fix the violations listed above, then re-run release-begin-impl."
- **Abort** — do not continue to Phase 1.

If the script exits 0: continue normally.
---

## Acceptance Criteria

- [ ] AC-07: `release-begin-impl` Phase 0 invokes the structural validation script and aborts the flow when violations are reported
- [ ] Violations are displayed clearly with folder path and rule ID before aborting
- [ ] A clean run (exit 0) produces no change in existing Phase 0 behaviour

## Notes

- Depends on TASK-PROC-045-02 (script extension) being done.
- This is deliberately a minimal change — one step, one script call, one abort condition.
- The script path may change if TASK-PROC-045-02 renames it; update accordingly.
- Pre-existing violations known from the smoke run in TASK-PROC-045-02 must be resolved (or the affected epics set to `status: draft`) before this step can pass.
