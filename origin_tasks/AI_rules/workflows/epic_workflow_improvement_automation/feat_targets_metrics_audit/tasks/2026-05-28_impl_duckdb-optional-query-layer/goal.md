---
task_id: TASK-PROC-006-16
type: impl
parent_requirement: REQ-PROC-006-02
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-ENAB
status: pending
effort: M
created: 2026-05-28
after: [TASK-PROC-006-12]
awaiting: ["v1.5-prioritization"]
awaiting_note: "Optional v1.5 enhancement per round-4 §6 IMPL-M and decision N-D-7. Hold until claude-optimize-audit (IMPL-G) has accumulated runs.tsv data that warrants joins; not required for v1."
covers:
  # Re-mapped during the 2026-06-01 epic restructure: this task moved from the old
  # single REQ-PROC-006 (where it covered AC-11/AC-12) to feat_targets_metrics_audit
  # (REQ-PROC-006-02), which is still a placeholder with no ACs yet. Coverage will be
  # re-assigned when REQ-PROC-006-02's exploration task (TASK-PROC-006-02-01) writes
  # the feature's acceptance criteria.
  acceptance_criteria: []
  sections: []
scope_description: "Add a DuckDB-based optional query layer to claude-optimize-audit for cross-session analytics over JSONL inputs. No ETL, no schema migration, no daemon — DuckDB reads raw JSONL. runs.tsv remains canonical."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
target_package: "claude-optimize"
backlog_id: IMPL-M
requirements_version:
  commit: eabdeaf0
  file: ../requirements.md
---

# Goal: DuckDB Optional Query Layer for Audit Skill (IMPL-M, v1.5 optional)

## Objective

Once the audit skill (IMPL-G) has accumulated enough runs.tsv data that
cross-session joins become useful, add a DuckDB-based query layer to the audit
skill. DuckDB reads JSONL directly — no ETL, no schema migration, no daemon.
This task is `awaiting:` v1.5 prioritization and is explicitly optional for v1.

## Requirements Summary

Reference: REQ-PROC-006 §"Effectiveness Metrics and Audit" — "Database
deferral (v1.5): Cross-session analytics that require joins over session JSONL
may optionally use DuckDB as a query-time dependency in a future version"
(commit eabdeaf0). Round-4 Part 1 (full design discussion) and Part 1.4 (the
account-local caveat).

For complete requirements at task creation time:
```
git show eabdeaf0:requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope

- Add DuckDB as a query-time dependency to claude-optimize-audit only (not to claude-optimize, not to monitors).
- Provide a small wrapper around DuckDB that queries raw JSONL files directly (no ETL, no schema migration, no daemon).
- runs.tsv remains the canonical record — DuckDB is for ad-hoc cross-session joins only.
- Document the account-local caveat (round-4 Part 1.4) in the audit skill body so no caller treats DuckDB query results as canonical history.
- Follow REQ-PROC-060 (Dependency Admission Gate) for the DuckDB introduction — escalate before adding the dependency.

### Out of Scope

- Migrating any existing analytics to DuckDB (the v1 metrics from IMPL-G continue to use runs.tsv + git history).
- Cross-account synchronisation of JSONL (account-local is the documented limitation).

## Acceptance Criteria

- [ ] DuckDB introduced via REQ-PROC-060 escalation; no self-authorization.
- [ ] Audit skill gains a documented sub-command (or flag) that performs at least one cross-session join example from runs.tsv + JSONL.
- [ ] runs.tsv is still the canonical record (no DuckDB-only data path replaces or augments it as a source of truth).
- [ ] Account-local caveat is documented in the audit skill body, with a sentence naming round-4 Part 1.4 as the source.

## Dependencies

| Dependency | Status | Notes |
|---|---|---|
| TASK-PROC-006-12 (IMPL-G) | pending | Needs the audit skill to extend |
| v1.5 prioritization | external | Optional; hold until audit data warrants joins |

## Notes

Concept docs: round-4 Part 1 (full DB-or-not analysis), Part 1.3 (DuckDB chosen
as embedded query-time layer; never as canonical store), Part 1.4 (three-account
caveat), decision N-D-7 (defer to v1.5).

Per REQ-PROC-060: never self-authorize a new top-level dependency. The
implementer must invoke the back-pressure protocol before adding DuckDB to
pubspec / Python manifest / package manifest.
