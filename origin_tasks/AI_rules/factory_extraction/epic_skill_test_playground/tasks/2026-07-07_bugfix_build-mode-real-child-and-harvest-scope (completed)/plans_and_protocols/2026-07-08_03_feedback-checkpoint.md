---
skill: code-bugfix
mode: automated
decision: ""
task_id: TASK-PROC-068-19
captured_at: 2026-07-08
---

# Question

---
task_id: TASK-PROC-068-19
session_id: ed35d6af-be83-477a-a5d1-1339cef455f0
account: gmail2
status: awaiting_answer
asked_at: 2026-07-08T00:20:00Z
skill: code-bugfix
---

# Pending Question

Full details in: `requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/tasks/2026-07-07_bugfix_build-mode-real-child-and-harvest-scope/plans_and_protocols/2026-07-08_02_protocol_real-child-proof-and-residual-leak.md`

## What's proven, and the blocker

The real authenticating `claude -p` child ran through `run_build_mode()`
end-to-end (rc=0, cost $0.20). **AC-1 (auth via real-HOME bind) and AC-2
(`process/` excluded → 0 process files harvested) are proven.** But **AC-4
("test_harness_app/ gained ONLY that artifact") FAILS**: the run left **13**
net-new files, not 1 — the proof persona **plus 12 host-factory files** that
`deploy.py` still copies and the full-registry harvest sweeps in:

- `requirements_tasks/{STATUS.md, RELEASE_BACKLOG.md, RELEASES.md,
  package_assignment_rules.md, _meta/id_registry.md}`
- `requirements_tasks/_scribble_components/*/metadata.yaml` (6 files)
- `requirements_user_needs/_meta/value_tradeoff_summary.md`

So excluding `process/` is **necessary but not sufficient** for AC-4 / AC-11
("transient deployed factory machinery is absent"). This is beyond the task's
declared Defect-1/Defect-2 charter (Out-of-Scope: "changing what deploy.py
copies beyond excluding requirements_tasks/process").

## The decision (why it's not a silent fix)

Two candidate fixes, with an **AC-10 tension** that makes the choice non-obvious:

- **Option A — widen deploy excludes** (drop these files too). Simple, mirrors
  the process/ fix, BUT unsafe for the runtime-input subset: `_scribble_components/*`
  is read by the `ui-scribble-*` skills and `_meta/id_registry.md` by
  `task-create`/`ux-flow-draft` — all skills that run *in the harness*. Dropping
  them risks AC-10 (deployed skill fails for a missing file it reads).
- **Option B — scope the HARVEST to net-new files** (diff post-run isolated copy
  vs. its pre-seed state; harvest only what the child authored). Keeps deploy
  whole (AC-10-safe), generalizes to all residual leakage. This is the approach
  the original AC-11 proof recommended. It is a design change to `build.py`'s
  harvest step — larger, and beyond this task's stated scope.

## Please choose

1. **Option B in this task** — expand scope: implement net-new-only harvest in
   `build.py`, then re-prove AC-4 + run AC-3. (Recommended — robust, AC-10-safe.)
2. **Option A in this task** — expand scope: audit each residual file, exclude
   only the authoring-time-only ones from deploy; accept that any runtime-input
   residuals need a different remedy. (Partial; may not fully satisfy AC-4.)
3. **Split** — land the proven process/ fix here (AC-1/AC-2/AC-5), reword/close
   AC-4 to the process-only claim, and file a follow-up task for the residual
   over-inclusion (Option B).
4. Something else / different AC-4 interpretation.

Current landed state: Defect-1 (build.py auth) and Defect-2 (deploy excludes
process/) fixes + unit tests are committed-in-tree and green (38/38). No residue
left in `test_harness_app/` (restored to baseline). AC-3 not yet run (deferred —
the decision may change deploy/harvest).

# Developer Answer

option b.

but additionally we can exclude all files that are creatred by a script. also we can exclude the _scribble_components folder, because it contains flutter app specific scribble components. I could go on, but it's a waste of time do define all folders+files that can be excluded now before the Lineome extraction.

# Rationale Captured

(Automated archival — no rationale extracted.)
