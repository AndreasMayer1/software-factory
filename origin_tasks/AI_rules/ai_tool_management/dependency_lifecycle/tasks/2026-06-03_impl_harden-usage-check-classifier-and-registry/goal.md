---
task_id: TASK-PROC-061-19
type: impl
parent_requirement: REQ-PROC-061
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: pending
effort: M
created: 2026-06-03
expected_tool_calls: 35
skill_chain_depth: 2
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-13, AC-14]
  sections: []
scope_description: "Harden check_dependency_usage.py with config-referenced + native-declared evidence classes and tiered output, and add a durable retention registry the script reads."
release_description: ""
opus_recommended: false
requirements_version:
  commit: bbc9d0a5
  file: ../requirements.md
---

# Goal: Harden usage-check classifier and add retention registry

## Objective

Implement REQ-PROC-061 **AC-13** (evidence-class broadening + tiered output) and **AC-14**
(durable retention registry) in `scripts/release/check_dependency_usage.py`. Together these
turn the noisy removal-candidate list into a tiered, actionable one and give a "keep" decision
a durable home so structural false positives stop resurfacing every monthly cycle.

All edits to `scripts/release/check_dependency_usage.py` (and any new Python) **must** go
through the `claude-write-script` skill (Python quality gates).

## Requirements Summary

REQ-PROC-061 AC-13: the usage-check recognizes structural evidence beyond Dart imports —
config-referenced (analyzer/lint/ruleset entries in `analysis_options.yaml`) and
native-declared (plugin declared for ≥1 target platform in `.flutter-plugins-dependencies`,
surfaced for manual call-site verification, never auto-retained). Output is tiered: likely-dead
vs needs-manual-review vs retained.

REQ-PROC-061 AC-14: a developer "keep" is persisted in a data-owned registry (package,
retention class, reason, acknowledgement date) that the script reads into an *acknowledged-kept*
classification; stale entries (package no longer in manifests) are reported.

For complete requirements at task creation time:
```
git show bbc9d0a5:requirements_tasks/process/AI_rules/ai_tool_management/dependency_lifecycle/requirements.md
```

Current requirements: ../requirements.md

Design detail: `../2026-06-03_explore_harden-dependency-usage-check (completed)/plans_and_protocols/2026-06-03_01_design.md` (§3 items #1–#7, §4).

## Scope

### In Scope
- **AC-13** — config-referenced class (scan `analysis_options.yaml`: `include`, `plugins`, `custom_lint` rules); native-declared class (cross-ref `.flutter-plugins-dependencies`); tiered output: likely-dead / needs-manual-review / retained.
- **Matcher hardening (#4)** — also match `export 'package:…'` and conditional/deferred imports (`… if (…) 'package:…'`).
- **Hygiene checks (#5)** — runtime `dependencies:` package imported only from `test/` (misplaced → should be dev_dependency); stale `INDIRECT_REQUIREMENTS` entries; surface `dependency_overrides`.
- **AC-14** — retention registry (proposed `automation/dependency_reviews/kept.yaml`: `package`, `class` ∈ {indirect,config,native,other}, `reason`, `acknowledged` date); script reads it → acknowledged-kept tier; report stale entries; decision-task appends on a keep.
- **Ergonomics (#6)** — externalize `INDIRECT_REQUIREMENTS` to YAML; add `--fail-on-candidates` non-zero exit.

### Out of Scope
- The empirical trial-removal recovery model (AC-15 → TASK-PROC-061-20).
- Updating `doc/process/dependency_lifecycle.md` (AC-10 → TASK-PROC-061-21).

## Acceptance Criteria

- [ ] `analysis_options.yaml`-referenced packages (e.g. very_good_analysis, custom_lint, clean_architecture_kit) are classified config-referenced, not removal candidates
- [ ] Native-declared packages (per `.flutter-plugins-dependencies`) appear in a needs-manual-review tier, never auto-retained
- [ ] Output is tiered: likely-dead vs needs-manual-review vs retained
- [ ] Matcher also catches `export 'package:'` and conditional/deferred imports
- [ ] Hygiene checks report: runtime dep imported only from test/, stale allowlist entries, dependency_overrides
- [ ] A keep persisted to the retention registry suppresses that package from the active removal-candidate list on the next run; a stale entry is reported
- [ ] `INDIRECT_REQUIREMENTS` is externalized to YAML; `--fail-on-candidates` returns non-zero when candidates exist
- [ ] Python quality gates pass (via claude-write-script)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

Process category — no `target_package`. Created via task-derive-from-requ (plan-driven) from
the REQ-PROC-061 decomposition. Native-declaration is circular evidence (Flutter generates the
registrant from every declared plugin) — it downgrades to needs-manual-review, never auto-keep.
