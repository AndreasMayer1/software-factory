---
task_id: TASK-PROC-049-03
type: analyze
parent_requirement: REQ-PROC-049
urgency: 3
urgency_reason: U3-TECH-DEBT
impact: 4
impact_reason: I4-ENAB
status: completed
started: 2026-05-16
completed: 2026-05-16
session_completed_at: 2026-05-16T13:05:19Z
effort: S
created: 2026-05-15
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-05]
  sections: []
target_package: ""
scope_description: "Coordinate with REQ-PROC-046 back-pressure work on the shared scripts/quality/_arb_parser.py interface"
release_description: ""
opus_recommended: false
requirements_version:
  commit: 5747c0c2
  file: ../../requirements.md
session_id: 960ff671-f6cd-4a9b-8d66-79e8eba22ed5
session_account: gmail2
---

# Goal: Coordination read + shared ARB parser

## Objective

Determine the ownership and shape of the shared ARB parser that REQ-PROC-049's `check_canon.py` (T5) and REQ-PROC-046's G6 linguistic-complexity sub-check will both consume. Output a decision document that either:

(a) commits to consume an ARB-parser module already designed by the REQ-PROC-046 back-pressure work, OR

(b) creates `scripts/quality/_arb_parser.py` with the minimal interface specified in design synthesis v3 §5.2:
```python
def iter_arb_entries(path) -> Iterable[ArbEntry]: ...
```

This is the only canon-bootstrap task that can run in parallel to T1 (TASK-PROC-049-02). It exists because two requirement streams need the same parsing infrastructure, and uncoordinated work would duplicate code.

## Background

The full canon-coherence design (v3 §5.2) calls for ARB parsing in `check_canon.py`. The back-pressure work in REQ-PROC-046 has its own ARB-consuming sub-check (G6 linguistic complexity). Both should share one parser module.

Relevant prior-work tasks (look up by `task_id:` in their `goal.md` frontmatter under `requirements_tasks/process/AI_rules/coding_standards/code_quality/tasks/2026-05-10_*`):

- TASK-PROC-046-01
- TASK-PROC-046-02
- TASK-PROC-046-08
- TASK-PROC-046-14

Read each folder's `goal.md` and any files under `plans_and_protocols/`. The questions to answer:

1. Has the back-pressure work already defined an ARB-parser module shape?
2. Is the G6 linguistic-complexity sub-check implementation already specified (which would dictate the parser interface)?

For complete requirements at task creation time:
```
git show 5747c0c2:requirements_tasks/process/AI_rules/requirements_management/language_coherence/requirements.md
```

Current requirements: ../../requirements.md

Design references:
- `2026-05-15_10_final_decisions.md` §2 row T2 (this task)
- `2026-05-15_08_opus_synthesis_v3.md` §5.2 (parser interface) and §13 (open coordination question)

## Requirements Summary

Indirectly supports AC-05 (drift-detection check). The parser is a dependency of `check_canon.py` which delivers AC-05.

## Scope

### In Scope

- Read TASK-PROC-046-01, -02, -08, -14 goal.md and plans_and_protocols/.
- Write a decision document at `plans_and_protocols/2026-05-15_01_arb_parser_decision.md` covering:
  - Findings from the read (what's defined, what isn't).
  - Decision: consume an existing parser OR create `scripts/quality/_arb_parser.py` here.
  - If "create": the minimal interface from v3 §5.2 (`iter_arb_entries(path) -> Iterable[ArbEntry]`), plus the `ArbEntry` dataclass shape needed by both consumers.
  - Coordination follow-up: who owns the parser file longer-term and which task touches it next.
- If decision is "create": implement `scripts/quality/_arb_parser.py` with that minimal interface and a small inline unit test or doctest.
- Update REQ-PROC-046 cross-reference is owned by T7 (TASK-PROC-049-08) — only flag any required cross-ref here.

### Out of Scope

- Modifying any TASK-PROC-046-* goal.md or plans_and_protocols/ files (read-only).
- Implementing the G6 sub-check.
- Implementing `check_canon.py` (T5 / TASK-PROC-049-06 consumes the parser).

## Acceptance Criteria

- [x] All four TASK-PROC-046 tasks have been read.
- [x] `plans_and_protocols/2026-05-15_01_arb_parser_decision.md` exists and answers the two coordination questions.
- [x] Decision is recorded (consume vs. create) with a one-paragraph rationale.
- [x] If "create": `scripts/quality/_arb_parser.py` exists with the v3 §5.2 minimal interface.
- [x] If "consume": the decision doc names the file path and module the parser will live at, plus the task that creates it. (N/A — decision was "create")
- [x] Cross-ref note: if REQ-PROC-046's requirements.md needs a Related-Requirements entry pointing at REQ-PROC-049, flag it in the decision doc (T7 applies it).

## Implementing Skill

`task-resolve` — small, deterministic process work.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | Runs in parallel with T1. |

## Notes

- This task is intentionally read-heavy and write-light. The whole point is to avoid duplicate parser work across two requirement streams.
- v3 §13 explicitly lists `_arb_parser.py` ownership as an open question — this task resolves it.
