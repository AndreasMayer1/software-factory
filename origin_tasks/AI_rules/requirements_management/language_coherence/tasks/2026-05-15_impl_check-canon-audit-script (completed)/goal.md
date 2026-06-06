---
task_id: TASK-PROC-049-06
type: impl
parent_requirement: REQ-PROC-049
urgency: 3
urgency_reason: U3-TECH-DEBT
impact: 4
impact_reason: I4-ENAB
status: completed
completed: 2026-05-16
session_completed_at: 2026-05-16T13:45:25Z
effort: M
created: 2026-05-15
started: 2026-05-16
after: [TASK-PROC-049-02, TASK-PROC-049-03, TASK-PROC-049-04]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-03, AC-05]
  sections: []
target_package: ""
scope_description: "Implement scripts/user_needs/check_canon.py — pass/fail drift detector covering requirements, ARB, translation_context placeholder, Dart user-facing strings, plus AC-03 verb-precision and reference-validation modes"
release_description: ""
opus_recommended: false
requirements_version:
  commit: 5747c0c2
  file: ../../requirements.md
session_id: a7b6338e-9151-4875-af68-6b964db4c674
session_account: gmail2

---

# Goal: Implement check_canon.py audit script

## Objective

Implement the canon-coherence audit script at `scripts/user_needs/check_canon.py`. The script delivers AC-05 (repeatable pass/fail drift detection) and AC-03 (generic-verb precision check). It is wired into release pre-flight by T8 (TASK-PROC-049-09).

## Background

Full specification lives in design synthesis v3 §3 (architecture), §5 (interface), and §8 (modes):

- §3 — four artefact walkers and their responsibilities.
- §5.1 — CLI shape and exit codes.
- §8.2 — DDD-light naming enforcement.
- §8.4 — `--code-coverage` mode reporting.

Additional final-decisions context:

- `2026-05-15_10_final_decisions.md` §1.2 — confirms scope excludes `lib/core/` (v1 §10.3).
- `2026-05-15_10_final_decisions.md` §1.3 — audience-aware lookup mechanics.

The ARB parser comes from T2 (TASK-PROC-049-03), either consumed from REQ-PROC-046 or freshly created at `scripts/quality/_arb_parser.py`.

For complete requirements at task creation time:
```
git show 5747c0c2:requirements_tasks/process/AI_rules/requirements_management/language_coherence/requirements.md
```

Current requirements: ../../requirements.md

## Requirements Summary

- AC-03 — generic-verb precision check.
- AC-05 — repeatable pass/fail drift detector across all in-scope artefact types.

## Scope

### In Scope

Use the `claude-write-script` skill. Implement `scripts/user_needs/check_canon.py` with:

**Four artefact walkers** (v3 §3):

1. Requirements markdown — walks `requirements_tasks/**/requirements.md` and matches body terms against canon.
2. ARB string values — uses the parser from T2 (`scripts/quality/_arb_parser.py` or whichever module T2 designated).
3. `translation_context` placeholder walker — no-op placeholder until REQ-NFUNC-013 AC-08 lands; the walker must exist (even as a stub) and print a one-line "deferred" message in `--code-coverage` mode.
4. Dart user-facing strings — walks `lib/features/**/presentation/*.dart`. **Excludes `lib/core/`** per final_decisions §1.2 confirming v1 §10.3.

**AC-03 verb-precision check** (v3 §3 / §8):

- Detects generic verbs (Edit, Delete, Update, Add, Create, Remove, Save, Submit) in user-facing text.
- Flags occurrences where the verb has divergent downstream consequences across the objects it applies to (per AC-03 condition (b)).
- Empirical tuning is expected — false positives are acceptable in v1; the check exits 1 on real divergences.

**Modes / flags**:

- Default: exit 0 on pass, 1 on fail; human-readable summary to stdout.
- `--json` — machine-readable output for CI.
- `--validate-references` — resolves CONCEPT-* / PERSONA-* / SCEN-* / FLOW-* / REQ-* IDs against their respective registries.
- `--code-coverage` — reports per v3 §8.4 (which canon concepts have at least one code-level alias, which don't, coverage percent).
- Audience-aware lookups: when checking artefacts, the script consults the canonical name plus `audience_variants.<audience>` overrides where applicable.

**General**:

- Exit codes: 0 pass, 1 fail. Other non-zero codes only for unexpected errors.
- No `///` WHY comments unless the code is genuinely non-obvious (then mandatory per CLAUDE.md §5).

### Out of Scope

- Wiring into release pre-flight (T8 / TASK-PROC-049-09).
- The translation_context walker's real implementation — stub-only for now.
- Auto-fixing — script is read-only.
- Performance optimization — correctness first; v1 can be slow.

## Acceptance Criteria

- [x] `scripts/user_needs/check_canon.py` exists, created via `claude-write-script`.
- [x] All four walkers implemented (translation_context as documented stub).
- [x] `lib/core/` is explicitly excluded from the Dart walker.
- [x] AC-03 verb-precision check covers all eight listed generic verbs.
- [x] `--json` flag emits valid JSON.
- [x] `--validate-references` resolves CONCEPT-*, PERSONA-*, SCEN-*, FLOW-*, REQ-* IDs.
- [x] `--code-coverage` mode reports per v3 §8.4.
- [x] Audience-aware lookup uses canonical name + `audience_variants.<audience>` overrides.
- [x] Exit codes: 0 on pass, 1 on fail.
- [x] Script runs cleanly against the empty canon (after T1) and against the bootstrap canon (after T3) — empty case must not crash.

## Implementing Skill

`claude-write-script` (MANDATORY for script creation per CLAUDE.md).

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-049-02 | pending | Folder + generator must exist. |
| TASK-PROC-049-03 | pending | ARB parser interface decision required. |
| TASK-PROC-049-04 | pending | Bootstrap canon needed to exercise the checks meaningfully. |

## Notes

- Script lives at `scripts/user_needs/check_canon.py` per the script-organization rules (CLAUDE.md §11).
- Do NOT re-design the audit logic — v3 §3 is the source of truth.
- The script must run in <60s on the current repo for release pre-flight to be acceptable (no hard SLA, but be reasonable).
