---
task_id: TASK-PROC-045-07
type: impl
parent_requirement: REQ-PROC-045
urgency: 4
urgency_reason: U4-DEP
impact: 4
impact_reason: I4-ENAB
status: completed
started: 2026-05-25
completed: 2026-05-25
session_completed_at: 2026-05-25T20:10:33Z
effort: M
created: 2026-05-24
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-11]
  sections: [SEC-06]
scope_description: "Implement the cross-reference completeness detection mechanism (REQ-PROC-045 AC-11/SEC-06) — likely as a deterministic Python script. Invoked by requ-explore Phase 1.4 and task-derive-from-requ Phase 1.5 (REQ-PROC-058 AC-17). Derives 2-4 search terms, greps requirements_tasks/, excludes already-referenced IDs."
release_description: ""
opus_recommended: false
writes_requirements: false
requirements_version:
  commit: c829ed37
  file: ../../requirements.md
session_id: e28d42b1-0786-43d1-a4b7-d24ae879a472
session_account: gmail2

---
# Goal: Implement cross-reference completeness detection mechanism

## Objective

Implement the keyword-grep mechanism that REQ-PROC-045 AC-11 / SEC-06 define. Given a target requirement, return the set of semantically related requirements not already cross-referenced. Used by `requ-explore` Phase 1.4 (overlap detection during authoring) and by `task-derive-from-requ` Phase 1.5 (cross-reference completeness gate before task creation).

## Requirements Summary

REQ-PROC-045 AC-11 mandates the mechanism: derive 2-4 search terms from the target requirement's topic (domain nouns, action verbs, component names), grep across `requirements_tasks/functional/`, `non-functional/`, and `process/`, exclude any hit whose REQ-ID already appears in the target's `after:`, `blocks:`, or `## Related Requirements` section. The choice between script and inline skill instructions is left to this impl task.

Per REQ-PROC-058 Developer Guidelines ("Prefer scripts over skill instructions"): a deterministic script is the preferred implementation.

For complete requirements at task creation time:
```
git show c829ed37:requirements_tasks/process/AI_rules/requirements_management/requirements_structure_quality/requirements.md
```

Current requirements: ../../requirements.md

## Scope

### In Scope

1. **Decision: script vs inline** — recommended: script. Reasons:
   - Deterministic (same input → same output across operators)
   - Token-efficient (skill invocations stay slim)
   - Reusable across multiple consumers (requ-explore + task-derive-from-requ)
   - Per the "prefer scripts" principle in REQ-PROC-058

2. **Implement script** (recommended path): `scripts/requirements/check_cross_refs.py`
   - Input: path to a requirement's `requirements.md`
   - Process:
     - Parse YAML frontmatter to get current `after:`, `blocks:`
     - Parse `## Related Requirements` section to get referenced REQ-IDs
     - Derive 2-4 search terms from requirement title + first paragraph (or accept explicit `--terms` flag)
     - Grep `requirements_tasks/functional/`, `non-functional/`, `process/` for those terms
     - For each hit: extract its REQ-ID
     - Exclude hits whose REQ-ID is already in after/blocks/Related, or is the target itself
     - Output: JSON list of `{id, path, matched_terms, snippet}` for each candidate gap
   - Exit codes: 0 = ran successfully (regardless of whether gaps found); 1 = script error
   - Tests: pytest coverage in `scripts/tests/` for: zero matches, multiple matches with exclusion, malformed YAML, missing target

3. **Update requ-explore skill** (`.claude/skills/requ-explore/SKILL.md` Phase 1.4):
   - Replace inline keyword-grep prose with a call to the new script
   - Preserve the user-facing behavior (surface gaps for user to decide)
   - Use `claude-modify-skill` per CLAUDE.md

4. **Document for task-derive-from-requ consumer**: ensure the script's output format is documented so TASK-PROC-058-03 (cross-reference completeness gate) can consume it

### Out of Scope

- The classification / fix workflow downstream of detection — that's task-derive-from-requ Phase 1.5 (TASK-PROC-058-03)
- requ-explore's other phases — only Phase 1.4 changes
- Modifying any requirement's after/blocks/Related fields — that's downstream of detection
- Migrating existing requirements with cross-ref gaps — separate effort

## Acceptance Criteria

- [x] `scripts/requirements/check_cross_refs.py` exists (or inline implementation chosen with documented justification)
- [x] Script produces valid JSON output per documented schema
- [x] Script correctly excludes already-referenced IDs (after, blocks, Related)
- [x] Script handles malformed input gracefully (exit 1 with clear stderr)
- [x] Tests in `scripts/tests/` cover happy path + edge cases (zero matches, all matches excluded, missing YAML, etc.)
- [x] `requ-explore` Phase 1.4 updated to invoke the script via `claude-modify-skill`
- [x] Output format documented for downstream consumer (TASK-PROC-058-03 will call it)
- [x] Use `claude-write-script` for the Python script (mandatory per CLAUDE.md)
- [x] Python gates pass (scripts/quality/check_python_gates.sh)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | None — REQ-PROC-045 already updated (c829ed37); no upstream blockers |

## Notes

This task unblocks TASK-PROC-058-07 (the REQ-PROC-001 test case) — that task awaits this script.

If the inline-instructions path is chosen instead (less recommended), document the rationale in `plans_and_protocols/decision_inline_vs_script.md` before implementing.

Mandatory:
- `claude-write-script` for the Python script
- `claude-modify-skill` for the requ-explore update
- Python quality gates must pass
