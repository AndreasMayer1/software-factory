---
task_id: TASK-PROC-009-15
type: impl
parent_requirement: REQ-PROC-009
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: completed
effort: S
created: 2026-06-06
completed: 2026-06-06
expected_tool_calls: 20
skill_chain_depth: 2
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-02, AC-03]
  sections: [SEC-08]
scope_description: "Conform generate_id_registry.py output to the SEC-08 ID Registry Content Contract (enumerate hierarchical IDs, count them, keep next-available top-level-only)."
release_description: ""
opus_recommended: false
requirements_version:
  commit: a9eb6506
  file: ../requirements.md
---

# Goal: Conform the ID registry generator to the SEC-08 content contract

## Objective

Make `scripts/artifacts/generate_id_registry.py` produce output that satisfies the
ID Registry Content Contract added to REQ-PROC-009 SEC-08 (AC-01, AC-02, AC-03).

This task bundles two deliverables (per developer decision — single impl task instead
of a separate requ-explore task plus a code task):

1. **Requirement clarification (already authored this session)** — REQ-PROC-009 SEC-08
   gained an "ID Registry Content Contract" subsection and its first three acceptance
   criteria (AC-01, AC-02, AC-03). This task owns the commit of that requirement edit.
2. **Code fix** — bring the generator's output into conformance with those ACs.

## Requirements Summary

REQ-PROC-009 SEC-08 ("ID Generation Rules") now states the content contract of the
auto-generated ID registry (`requirements_tasks/_meta/id_registry.md`):

- **AC-01** — The registry catalog lists every valid requirement ID, including
  hierarchical sub-requirement IDs (`REQ-CAT-NNN-NN`), each nested under its parent
  epic's top-level ID.
- **AC-02** — Every per-category count and the registry total include hierarchical
  sub-requirement IDs.
- **AC-03** — Each category's "Next Available ID" is derived from top-level IDs only;
  a hierarchical ID shares its parent epic's top-level number and does not advance the
  next-available number.

For complete requirements at task creation time:
```
git show a9eb6506:requirements_tasks/process/AI_rules/requirements_management/requirements_and_tasks/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- The catalog-listing scan in `generate_id_registry.py` (the regex
  `^REQ-(FUNC|NFUNC|PROC)-\d{3}$` at lines ~205 and ~445) so hierarchical
  sub-requirement IDs (`REQ-CAT-NNN-NN`) are included in the catalog and grouped under
  their parent epic's top-level ID.
- Per-category counts and the Overview total so they reflect hierarchical IDs.
- Regenerating `requirements_tasks/_meta/id_registry.md` from the corrected generator.
- Python quality gates (via `claude-write-script`) for the script change.

### Out of Scope
- `compute_next_ids` (top-level-only) — correct as-is per AC-03; MUST NOT change.
- Any change to ID formats, the user-needs registry path, or VTR handling beyond what
  the contract requires.
- Cleaning "malformed" IDs — investigation confirmed every real `requirements.md`
  frontmatter ID is well-formed; the earlier apparent hits were in `goal.md`/findings
  files the generator does not ingest.

## Acceptance Criteria

- [x] AC-01: Regenerated `id_registry.md` lists every hierarchical sub-requirement ID
      (`REQ-CAT-NNN-NN`) as its own entry grouped under its parent epic's top-level ID.
      (82 nested `└─` entries.)
- [x] AC-02: Per-category counts and the Overview total in the regenerated registry
      include hierarchical sub-requirement IDs. (Total 108 → 190.)
- [x] AC-03: Each category's "Next Available ID" is unchanged and derived from
      top-level IDs only. (PROC-070 / NFUNC-024 / FUNC-024 / VTR-008 unchanged.)
- [x] `compute_next_ids` is untouched.
- [x] Python quality gates pass for the changed files (10/10 tests; G1/G2/G4/G5 green via claude-write-script).

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-009-?](../2026-02-07_impl_auto_id_registry%20%28completed%29/goal.md) | Predecessor — built the ID registry generator this task conforms to the new SEC-08 contract |

## Notes

- **§3c redirect override**: type is `impl` and REQ-PROC-009's ACs (AC-01..AC-03) had
  zero coverage at creation, which normally redirects to `task-derive-from-requ`. The
  developer explicitly chose a single bundled impl task, so the redirect is overridden
  (`--standalone-override` equivalent).
- The script change MUST go through the `claude-write-script` skill (mandatory for any
  edit under `scripts/`), which runs the Python gates.
- `requirements_version.commit` (a9eb6506) is the last committed baseline; the SEC-08
  edit authored this session is uncommitted and is committed as part of this task.
