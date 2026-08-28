---
skill: task-resolve
mode: automated
decision: ""
task_id: TASK-PROC-068-26
captured_at: 2026-07-19
---

# Question

---
task_id: TASK-PROC-068-26
session_id: 45b4b247-f46f-4843-a9c4-128a9db225a4
account: web
status: awaiting_answer
asked_at: 2026-07-15T07:40:40Z
skill: task-resolve
---

# Pending Question (follow-up — Option A run attempted, two new blockers found)

Full investigation: `plans_and_protocols/2026-07-15_05_blocker_provenance-harvest-gap.md`
(negligible budget spent — first run torn down at span-0 enrich; contaminated copy destroyed).

Option A (drive span-0 DONE) was launched. Inspecting the copy surfaced **two** build-mode gaps the
task plan didn't anticipate:

1. **Deploy leak (workaroundable):** `deploy.py` doesn't exclude
   `requirements_user_needs/product_materialization/`, so the **flutter app's own** materialization
   (MAT-002) leaks into the harness copy → `ux-write-materialization` would run UPDATE/supersession
   against a foreign MAT id. Fixable in-driver (delete the leaked file before authoring).

2. **Provenance non-harvest (fundamental):** AC-1 requires `check_materialization_provenance.py` = OK,
   but that check is hardwired to the **flutter_app** repo (resolves `IDEATION-NNN @ <sha>` against
   flutter's ideation index + git). The child authors provenance **inside the ephemeral copy** (its own
   `.factory/ideation` + its own fresh git repo), and `.factory/ideation` is **not** a harvest category
   (only user-needs/requirements/scribble/source-code), and `test_harness_app` has no `.factory`. So the
   harvested artifact's `decided_by` dangles → host check returns MISSING. **AC-1 is unsatisfiable by
   pure build-mode harvest.**

**Which way?**
- **A (recommended):** run the medium-selection **ideation in the host session** (flutter_app),
  committing the ledger + index entry (referencing harness scenarios) → `IDEATION-NNN @ <sha>`
  resolvable in flutter_app; feed it to the child, which authors materialization with that `decided_by`
  and deletes the leaked flutter file. No mechanism change; more elaborate driver.
- **B:** open a separate mechanism task (REQ-PROC-068/074) to make build-mode carry the ideation
  provenance across harvest AND fix the `deploy.py` exclude. Leaves 068-26 (and dependent 068-12)
  blocked meanwhile.
- **C:** relax AC-1 for the harness fixture (drop the `provenance OK` gate) — a requirement edit routed
  through the proper flow.

# Developer Answer

# Answer (developer decision, relayed via manual orchestrator session 2026-07-19)

**Decision: Option B — build the mechanism.** Investigation of the last commits showed Option B was
almost entirely already built, and the question's framing overstated it. Resolution below.

## What was already true (both original blockers effectively resolved before this)
- **Blocker 1 (deploy leak):** already fixed — TASK-PROC-068-33 added
  `requirements_user_needs/product_materialization/` to `deploy.py::_SUBFOLDER_EXCLUDES`.
- **Blocker 2 (commit reachability), the hard half:** already built — TASK-PROC-068-32/34: harvest
  compaction preserves the referenced `decided_by @ <sha>` commit and persists it to
  `test_harness_app/.playground_harness_git/harness.bundle`, restored on the next deploy.
- **Host-side git access (the elaborate part of the original Option A/B framing): NOT needed and NOT
  built.** `check_materialization_provenance.py` is only ever invoked inside a deployed copy
  (`layer-derivation-start`/`-resume`, `ux-flow-draft`), where the bundle is restored → commit reachable.

## What was actually missing, and what was built
The provenance check ALSO reads the ideation **index entry** and **ledger** as files on disk (steps 2–3),
and neither harvest (wrong categories) nor bundle-restore (reachability, not checkout) put them there.

**TASK-PROC-068-35** now conforms the harvest to **REQ-PROC-068 AC-11's retention clause**: at harvest,
`retain_ideation_provenance()` scalpel-retains exactly the referenced `IDEATION-NNN`'s index entry +
ledger + task folder into `test_harness_app/` as its own project data (no wholesale category inclusion —
AC-21 intact; no leak of other ideation entries). Verified with a **real deterministic end-to-end test**
(harvest → retain → persist bundle → real redeploy via `create_workspace`+`restore_workspace_git` →
`check_materialization_provenance.check()` returns `OK`) and all 7 Python quality gates green.

## Resolution for TASK-PROC-068-26 — UNBLOCKED
068-26's **AC-1** (materialization authored via `ux-write-materialization`; provenance resolves `OK`) is
now achievable by pure build-mode harvest. **Resume 068-26**: re-run the build-mode materialization
derivation. On completion the harvest retains the provenance and `check_materialization_provenance.py`
resolves `OK` after redeploy — no outer-session ideation (old Option A) required.

Depends-on now satisfied: TASK-PROC-068-35 (completed).

# Rationale Captured

(Automated archival — no rationale extracted.)
