---
task_id: TASK-PROC-053-03
type: impl
parent_requirement: REQ-PROC-053
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
started: 2026-05-26
completed: 2026-05-26
session_completed_at: 2026-05-26T19:13:47Z
effort: M
created: 2026-05-26
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-02, AC-03, AC-04, AC-07]
  sections: []
scope_description: "Create doc-lookup-dependencies skill, wire ctx7 CLI, privacy validation script, and cross-cutting doc"
release_description: ""
opus_recommended: false
writes_requirements: false
requirements_version:
  commit: db92ca63
  file: ../requirements.md
session_id: 3514c866-5cb7-4562-80f9-a0228cbb1c8f
session_account: gmail2
---
# Goal — Foundation: doc-lookup-dependencies skill + context7 CLI + privacy script

## Objective

Implement the foundational infrastructure that all code-producing chains
will use to comply with REQ-PROC-053.

## Scope

### In Scope

1. **`doc-lookup-dependencies` skill** — single lookup checkpoint for all
   code-producing chains. See synthesis §4.6 for API sketch and §4.1–4.5
   for internals (lookup_log.jsonl, dedup key, toolchain-clean probe,
   channel chain, budget cap sentinel).
2. **context7 integration via `ctx7` CLI** — no MCP (security decision);
   skill dispatches via Bash. ctx7 is already installed.
3. **Privacy validation script** (`scripts/util/validate_doc_lookup_query.py`) —
   sanitizes queries before forwarding to context7; strips paths and
   project-specific identifiers.
4. **`doc/cross_cutting_standards/documentation_lookup.md`** — operational
   policy doc (log schema, channel chain, per-tech table pointers).
5. Wire lookup-log count summary into commit messages (D7) — amend
   `task-complete` or `claude-commit` skill.

### Out of Scope

- Per-skill checkpoint wire-in (Tier 2 task).
- Per-technology threshold tables (Tier 3 task).

## Design Reference

Synthesis document:
`requirements_tasks/process/AI_rules/coding_standards/external_documentation_lookup/tasks/2026-05-21_explore_operationalize-doc-lookup-policy (completed)/plans_and_protocols/2026-05-26_03_synthesis_design.md`

Key decisions from user feedback (2026-05-26_04_feedback.md):
- Skill name: `doc-lookup-dependencies` (not `doc-lookup`)
- No MCP — use ctx7 CLI (MCP has security issues)
- D7 accepted: lookup-log count in commit messages
- D8: Option A — context7 with query sanitization script
- D9: 2 calls when slug must be resolved, 1 when cached; budget bands unchanged

## Acceptance Criteria

- [x] `doc-lookup-dependencies` skill created and self-consistent
- [x] ctx7 CLI integration works (test with a real lookup)
- [x] Privacy script validates/sanitizes queries (paths stripped)
- [x] `doc/cross_cutting_standards/documentation_lookup.md` created
- [x] Lookup-log count wired into commit messages

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-053-02 | completed | Synthesis design (see plans_and_protocols/) |
