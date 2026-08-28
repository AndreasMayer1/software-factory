---
task_id: TASK-PROC-068-04
type: impl
parent_requirement: REQ-PROC-068
urgency: 3
urgency_reason: U3-QUALITY
impact: 4
impact_reason: I4-QUAL
status: completed
effort: L
created: 2026-06-27
started: 2026-06-27
completed: 2026-06-27
session_completed_at: 2026-06-27T13:10:06Z
expected_tool_calls: 45
skill_chain_depth: 3
synthesis_dependent: true
synthesis_justification: "SG-01 launch adapter + SG-04 OS-containment + cost capture must be held together across the Python substrate layer — all three interact at the child-session boundary."
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-07, AC-08, AC-09]
  sections: []
egp:
  - { ac: AC-07, archetype: F, referent: "the observed behaviour of a real deploy-run-reset cycle returning the harness to a clean state" }
  - { ac: AC-08, archetype: C, referent: "the real token consumption + wall-clock duration of the child sessions a test run launches" }
  - { ac: AC-09, archetype: S, referent: "a real untrusted candidate factory launched as a child session attempting to reach the host factory tree via absolute paths or working-directory escape" }
consequence: HIGH
scope_description: "Walking skeleton: deploy candidate factory into test_harness_app/, run skill as cwd, git-reset between runs, capture token+wall-clock cost. SG-01 real launch adapter + SG-04 OS-containment required."
release_description: ""
opus_recommended: true   # reason: cross-cutting invariant — SG-01 adapter + SG-04 OS-containment + cost wiring span the child-session boundary and must be reasoned about simultaneously; archetype-S/HIGH consequence (AC-09)
writes_requirements: false
requirements_version:
  commit: 9b25bde0
  file: ../requirements.md
session_id: cd26108b-11c1-450b-81df-17e28036268d
session_account: gmail
---
# Goal: Walking Skeleton — Deploy → Run → Git-Reset → Cost

## Objective

Build the walking skeleton of the Skill-Test Playground substrate. The skeleton performs the
minimum viable loop on a single fixture:

1. **Deploy** a candidate factory (a snapshot of `.claude/skills/`) into `test_harness_app/`
2. **Run** a skill with `test_harness_app/` as the working directory (child session)
3. **Git-reset** the harness between runs (clean state per run)
4. **Capture** real token + wall-clock cost from the child session

Single fixture, single-cell loop. No multi-pair corpus yet; no discriminating-maturity walk yet.

### Mandatory first-build gates (from SG red-team — accepted corrections, not open debate)

**SG-01 — Real launch adapter (feasibility floor risk):**
`orchestrate.py:_launch_claude_session` is NOT a reusable API — it requires `OrchestratorDeps`,
`state.json`, `inbox.md`, `stop_flag`; its hung-detection hardcodes the *current* project's JSONL
path, not the child's cwd. "Thin facade" is wishful. This task MUST build a real `orchestrate.py`
launch adapter: extract the launch core from its orchestrator-global deps and parameterize the JSONL
hung-detection path on the CHILD's cwd.

**SG-04 — OS-level containment (child_session_safety floor risk, AC-09, archetype-S/HIGH):**
Worktree alone does NOT close CON-04's absolute-path cwd-escape. This task MUST re-instate ONE
OS-level containment layer (separate OS user OR namespace-unshare) to close the absolute-path
cwd-escape vector. The divergence-phase ideation generated these options; synthesis NUF-dropped them
for cost — that NUF was the red-team finding. Reinstate one.

**SG-02 note (already PASS — reuse, do not re-litigate):**
Cost capture via `claude -p --output-format json` (`.total_cost_usd`) was verified PASS in
TASK-PROC-073-01-01 (spike, run1 $0.2706 + run2 $0.2784 via JSON envelope). Reuse this exact path;
do not attempt `--bare` or re-verify from scratch.

**SG-03 note (advisory scope — bake into output):**
The ~100 paired-fixture validity floor (paired win-rate + variance bands) is unreachable at skeleton
stage. Skeleton-stage regression verdicts are ADVISORY. The skeleton MUST record this advisory scope
explicitly in its output artifacts so consumers are not misled.

### Script work mandate

This task touches `scripts/` (Python substrate for deploy/run/reset/cost). Use the
`claude-write-script` skill for every script created or modified under `scripts/`. Python quality
gates apply (REQ-PROC-051: G1 lint, G2 type, G3 tests, G4 no hand-rolled YAML, G5 print discipline).

## Requirements Summary

REQ-PROC-068 defines the Skill-Test Playground substrate. The ACs this task covers:

- **AC-07** (EGP: F / MEDIUM): A real deploy-run-reset cycle returns the harness to a clean state
  after each run — the harness is verifiably unmodified after reset.
- **AC-08** (EGP: C / MEDIUM): Real token consumption + wall-clock duration of child sessions are
  captured per run and emitted into the cost ledger (hard `max_budget_usd` cap).
- **AC-09** (EGP: S / HIGH): An untrusted candidate factory launched as a child session cannot reach
  the host factory tree via absolute paths or working-directory escape — OS-level containment enforced.

For complete requirements at task creation time:
```
git show 9b25bde0:requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- `test_harness_app/` deploy mechanism (snapshot a candidate skill set into the harness)
- Child-session launch adapter (SG-01): extracted from `orchestrate.py`, parameterized on child cwd
- OS-level containment layer (SG-04): one of {separate OS user, namespace-unshare}
- Git-reset between runs: harness returns to clean state after each child session
- Cost capture: `claude -p --output-format json` → `.total_cost_usd` + `.duration_ms` → cost ledger
- Single fixture, single-cell loop (no multi-pair corpus in this task)
- Advisory scope annotation in output artifacts (SG-03)
- Python scripts via `claude-write-script`; all five Python quality gates must pass

### Out of Scope
- Multi-pair corpus (T-corpus / TASK-PROC-073-01-02)
- Discriminating-maturity walk (T-maturity)
- Multi-cell loop / full oracle integration
- Behavioural oracle (execute-both-versions variant)

## Acceptance Criteria

- [x] AC-07 — EGP: F (the observed behaviour of a real deploy-run-reset cycle returning the harness to a clean state); consequence: MEDIUM — evidenced by scripts/tests/test_playground_run_skeleton.py::test_run_single_fixture_resets_harness_after_run
- [x] AC-08 — EGP: C (the real token consumption + wall-clock duration of the child sessions a test run launches); consequence: MEDIUM — evidenced by scripts/tests/test_playground_run_skeleton.py::test_run_single_fixture_returns_ledger_with_advisory (total_cost_usd + duration_ms ledger, hard max_budget_usd cap, SG-03 advisory annotation)
- [x] AC-09 — EGP: S (a real untrusted candidate factory launched as a child session attempting to reach the host factory tree via absolute paths or working-directory escape); consequence: HIGH — evidenced by scripts/tests/test_playground_containment.py::test_real_jail_blocks_host_tree_access (real bwrap/unshare mount-namespace jail; host sentinel unreachable from inside)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-073-01-01 (disproof spike) | completed | GREEN verdict — SG-02 cost path verified; reuse `--output-format json` |

## Notes

- **SG-01 is the hardest engineering item**: `_launch_claude_session` has deep orchestrator deps.
  Read `scripts/orchestrate.py` carefully before designing the adapter. The adapter must be a clean,
  independently-testable module — not a hack around the existing function.
- **SG-04 choice**: pick the containment layer that is cheapest to add and easiest to verify.
  Namespace-unshare (Linux `unshare --user --map-root-user`) is likely cheaper than a full OS-user
  setup; either is acceptable as long as CON-04 is closed and the closure is tested.
- **Cost ledger**: carry a hard `max_budget_usd` cap; emit a warning (do not silently run over).
- **Advisory annotation**: every result artifact must include a visible note that skeleton-stage
  verdicts are ADVISORY pending the ~100 paired-fixture floor (T-corpus + T-maturity will address).
