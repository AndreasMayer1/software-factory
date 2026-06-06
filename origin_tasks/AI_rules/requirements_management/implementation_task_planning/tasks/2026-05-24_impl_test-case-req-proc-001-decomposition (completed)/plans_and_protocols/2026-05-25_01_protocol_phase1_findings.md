# TASK-PROC-058-07 — Protocol: Phase 1 + Phase 1.5 findings

Date: 2026-05-25
Session: 60d42e81-7a35-434b-87dd-1e6f3f73bec8 (gmail2, automated)
Skill under test: `task-derive-from-requ` run against REQ-PROC-001 (Context Window).

This task is BOTH a real-world validation of the skill AND a fix for the
REQ-PROC-001 coverage gaps. Findings (positive and negative) are the deliverable.

## Phase 1 — Gather

### Coverage of REQ-PROC-001 (authoritative, from coverage_report.py)

| AC | Covered by | Status |
|----|-----------|--------|
| AC-01 | TASK-PROC-001-06, -07 | covered |
| AC-02 | TASK-PROC-001-06 | covered |
| AC-03 | TASK-PROC-001-06, -07 | covered |
| AC-04 | TASK-PROC-001-10 | covered (closed AFTER this test task was authored) |
| AC-05 | TASK-PROC-001-04, -08, -09 | covered |
| AC-06 | TASK-PROC-001-05 | covered |
| AC-07 | — | **ZERO COVERAGE** |
| AC-08 | TASK-PROC-001-03 | covered |

10 existing tasks (TASK-PROC-001-01 … -10).

### FINDING A — test premise partially stale (positive signal)
The goal.md states AC-04 and AC-07 both have zero coverage. As of today AC-04 is
covered by TASK-PROC-001-10 ("open-scope-discovery-gate", created 2026-05-25).
Only AC-07 remains uncovered. The skill correctly surfaces the *current* gap,
not the snapshot from task-authoring time. This validates that the coverage
matrix is computed live, not cached.

### FINDING B — no verification task exists (confirmed gap)
No task under REQ-PROC-001 has `type: verify`, `verification_task: true`, or a
`verification_bundle:`. The skill's mandatory verification-task gate (AC-02 of
the skill) correctly flags this. A verification task must be created.

### FINDING C — legacy empty `covers:` fields (covers-repair, AC-09)
- TASK-PROC-001-01 (completed, 2025-08-31 "update clinerules context window"):
  empty covers. Predates the AC structure (ACs added in 2026-01-04 consolidation).
  Low inference confidence → left as-is, documented (not auto-repaired).
- TASK-PROC-001-02 (completed, explore "task-sizing-to-fit-context-budget"):
  `covers.acceptance_criteria: []`. Explore task that produced the S1–S4 design;
  explore tasks legitimately do not "cover" ACs. Left as-is, documented.
Neither qualifies for high-confidence auto-repair (task name does not directly
match an AC name), so per the skill's automated-mode rule they are documented
rather than force-assigned.

## Phase 1.5 — Cross-Reference Completeness Gate (REQ-PROC-058 AC-17)

REQ-PROC-001 currently has NO cross-references: `after: []`, `blocks: []`, and
no `## Related Requirements` section.

### FINDING D — script name mismatch (integration bug)
The skill's Phase 1.5.1 looks for `scripts/requirements/detect_cross_ref_gaps.py`
(per REQ-PROC-045 AC-11). TASK-PROC-045-07 actually implemented the detector as
`scripts/requirements/check_cross_refs.py`. The skill's "preferred script present"
check therefore fails and would fall back to inline grep. The script DOES exist
under the other name and works. **Fix needed**: align the skill's documented path
(and invocation) with the implemented script, OR rename the script. Reported as a
follow-up bugfix (see test_case_findings, to be completed on resume).

### FINDING E — script interface mismatch (integration bug)
The skill documents the invocation as:
  `detect_cross_ref_gaps.py --target <path> --json`
The implemented `check_cross_refs.py` uses a positional `requirement` argument,
an optional `--terms`, and emits JSON to stdout by default (no `--json` flag,
no `--target` flag). Same root cause as Finding D — the skill was written against
a planned interface that the implementation diverged from.

### FINDING F — auto-derived search terms too generic (quality issue)
Run with auto-derived terms, `check_cross_refs.py` produced **128 candidates**
because the derived terms were generic words from the User Story
("User", "want", "Story", "developer"). With explicit domain terms
(`"context window" "fan-out" "tool-call" "escalation"`) it produced **9**
candidates. The auto-term derivation needs domain-noun extraction, not raw
high-frequency words. Recommend the skill always pass explicit terms (or the
script's term derivation be improved). Reported as a follow-up.

### Candidate classification (9 explicit-term candidates)

| REQ-ID | Matched | Recommendation | Rationale |
|--------|---------|----------------|-----------|
| REQ-PROC-008 | context window | **semantic** | Orchestrator manages context via subtasks; REQ-PROC-001 Design Decision references orchestrator mode. Genuine relation, no reciprocal ref today. |
| REQ-PROC-058 | escalation | **semantic** | task-derive-from-requ consumes REQ-PROC-001's S1–S4 sizing signals. REQ-PROC-058 already references REQ-PROC-001 one-way; the back-reference is missing. |
| REQ-PROC-046 | escalation | **ignore** | REQ-PROC-046 already documents REQ-PROC-001 as "unrelated; concerns conversational context, not code quality." Honour that assessment. |
| REQ-PROC-005 | context window | **ignore** | Incidental mention in testing-workflow prose. |
| REQ-PROC-026 | escalation | **ignore** | "escalation" used re visual hierarchy emphasis. Unrelated. |
| REQ-PROC-032 | context window | **ignore** | Incidental mention in metadata.yaml description. |
| REQ-PROC-051 | escalation | **ignore** | Gate boilerplate ("never declared complete"); different sense. |
| REQ-PROC-052 | escalation | **ignore** | Same gate boilerplate. |
| REQ-PROC-056 | escalation | **ignore** | Same gate boilerplate. |

No `hard` dependencies identified — REQ-PROC-001 does not depend on any of these
being implemented first.

### Why the session pauses here
Per `task-derive-from-requ` Phase 1.5.2, in automated mode the cross-reference
**classification** is a human-in-the-loop checkpoint: write the gaps file +
`question.md`, copy `answer.md`, commit, terminate. The recommendations above are
provided to the developer, who confirms/edits them in `answer.md`. On resume
(Phase 1.5.3) a spawned agent applies the confirmed classifications, then the
decomposition proceeds (Phase 2+): create a task for AC-07 and a verification task.

## Remaining work after resume
1. Apply confirmed cross-ref classifications (spawn agent — Phase 1.5.3).
2. Phase 2–4: plan a task for AC-07 + a verification task for REQ-PROC-001.
3. Phase 5: create via orchestration task (automated mode).
4. Phase 6: validate 100% coverage.
5. File follow-up bugfix(es) for Findings D/E/F.
6. Complete `test_case_findings.md`.
