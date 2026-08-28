---
skills_used:
  - claude-automated-mode
  - task-start
  - claude-route
  - task-resolve
  - claude-write-script
  - claude-commit
  - verify-quality
  - doc-update-guidelines
  - task-complete
---

# Protocol: Verification complete — all three ACs proven against real behaviour

**Session**: 69804c91-9f5e-4c63-af04-e7983ca11aeb (automated, gmail2)
**Date**: 2026-07-18

## Developer decision applied

`automation/pending_feedback/TASK-PROC-068-34/answer.md` → **Option B**: `deploy.py` excludes all of
`automation/`. Implemented in `scripts/playground/deploy.py` (`_TOP_LEVEL_EXCLUDES`) via
`claude-write-script`, with a regression test
(`scripts/tests/test_playground_deploy.py::test_deploy_excludes_automation_dir`) and a documented
residual AC-10-class risk (the `claude-automated-mode` skill's own escalation procedure `cp`s
`automation/pending_feedback/TEMPLATE_answer.md`, which is now absent from the deployed copy too —
not pre-emptively worked around, flagged for the next run that actually needs it). Full Python gate
suite (G1–G7): **all PASS**.

## Re-verification after the fix

Removed the stale `automation/` leak from the still-preserved `playground_ws_8303399e` workspace to
mirror what the fixed `deploy.py` would have produced, but `build_resume` refused it (`blocked` is
not in the resumable status set — by design, AC-18: a blocked run must not be auto-relaunched). Ran
a **fresh** `run_build_mode` instead (fresh deploy, so the fix applies from the start). The first
attempt was killed by my own Bash foreground timeout at 9 min (real ideation-start runs vary
6–10+ min) — `build_resume resume` picked it up and finished cleanly on the second attempt.

## AC-20 — PROVEN (2 real runs, restore + compaction + cross-run stability)

**Run 1** (fresh maintenance run, no bundle existed yet): real child session drove a degenerate
chain-state certification, one real standalone `ideation-start` (Quick, embedded) for a genuinely
trivial decision, then authored a persona referencing that ideation commit's real sha plus two noise
commits. `total_cost_usd=1.9704804`, `duration_ms=298877` (~5 min), outcome `complete`.

Verified directly against the persisted bundle (`git clone` + `git log --graph`):
```
* bcd6ae4 playground compaction: squash of 3 unreferenced commits
* cc6c86c ideation: decide proof-persona phrasing (Quick, embedded)
* 8de21ae certify degenerate persona_scenario boundary (already-approved anchors)
* d738eb7 certify degenerate persona_scenario boundary (already-approved anchors)
* a5bd1bc playground baseline
```
The harvested persona literally carries `<!-- decided_by: IDEATION-001 @ cc6c86c14a9353a84beb370be5761c3571b9293f -->`
— the exact `git rev-parse HEAD` output the child captured — and `cc6c86c14a9353a84beb370be5761c3571b9293f`
resolves to a real commit in the bundle whose diff shows a genuine
`.../plans_and_protocols/2026-07-18_004_ideation_ledger.yaml` (147 lines, real ideas/criteria/
rationale, not fabricated). Compaction squashed exactly the 3 commits above it (persona-author +
noise1 + noise2) into `bcd6ae4`, leaving `cc6c86c` and its ancestors untouched — matches the
preserve-referenced/squash-unreferenced design exactly.

**Run 2** (restore-on-deploy from the persisted bundle): log confirms `Step 3: restoring workspace
git from persisted bundle: .../harness.bundle`. Child did a fresh cheap degenerate certification
(different unit_id, no new reference) plus two noise commits touching only the seeded persona file.
`total_cost_usd=0.6758868`, `duration_ms=147966` (~2.5 min), outcome `complete`.

Verified directly against the re-persisted bundle:
```
* e121149 playground compaction: squash of 4 unreferenced commits
* bcd6ae4 playground compaction: squash of 3 unreferenced commits   <- run 1's persisted tip
* cc6c86c ideation: decide proof-persona phrasing (Quick, embedded)  <- run 1's REFERENCED commit
* 8de21ae certify degenerate persona_scenario boundary (already-approved anchors)
* d738eb7 certify degenerate persona_scenario boundary (already-approved anchors)
* a5bd1bc playground baseline
```
`bcd6ae4` (run 1's own persisted tip) present **unchanged** as a direct ancestor — prior-run
immutability holds. `cc6c86c` present with the **exact same 40-hex hash** as run 1 — the headline
AC-20 claim ("a commit reference a run records... stays reachable in every later run") verified
across 2 real runs, not asserted from the code's own output. Run 2's own 4 new commits (restore
baseline + certify + 2 noise) squashed into `e121149`, sitting directly on `bcd6ae4` — compaction
correctly re-fired on the second run too, using the (correctly recovered) prior persisted tip as its
new immutability boundary.

## AC-11 — PROVEN (real build/maintain run, harvest scope, provenance retention)

After both runs, `test_harness_app/`:
- Gained **only** the intended artifacts: `requirements_user_needs/personas/persona-gitproof/`
  (harvested, `harvested_paths` confirms) and `.playground_harness_git/harness.bundle` (persisted).
  `git status --porcelain test_harness_app/` shows exactly these two untracked entries; file count
  8889 → 8891 (exactly +2), matching `harvested_paths`/registry exactly.
- Zero transient deployed factory machinery: `.claude/`, `scripts/`, `.factory/`, `doc/`,
  `automation/` all confirmed absent from `test_harness_app/`.
- The harness's own factory-runtime provenance (the real ideation index/ledger backing the
  `decided_by`-referenced decision) is retained as project data — not as a plain checked-out file
  (ideation content isn't in `_PRODUCT_DEFINITION_CATEGORIES`'s harvest allowlist), but as committed
  history inside the harness's own persisted git bundle, recoverable via `git show <sha>:<path>`
  against `test_harness_app/.playground_harness_git/harness.bundle` — a real, inspectable, retained
  form of "project data of the standalone harness," and it survived run 2 untouched (see AC-20).
- `requirements_user_needs/product_materialization/` — absent before, absent after; not clobbered
  (nothing to clobber yet; TASK-PROC-068-33's exclude is confirmed in place and doesn't interfere
  with these two runs, which never touched materialization).

### Ancillary finding (not blocking, noted for awareness)

The harvested persona's `decided_by: IDEATION-001 @ <sha>` reused an id already taken in the host's
own (deployed, unmodified — confirmed via `git diff` showing zero change to
`.factory/ideation/index.yaml` across both runs) ideation index by an unrelated 2026-06-09 decision
("name the extracted software factory standalone repo"). The child's embedded `ideation-start`
invocation evidently allocated the per-ledger-file `NNN` counter correctly (its own run folder was
empty) but did not register/increment the **global** `IDEATION-NNN` id against the real deployed
index (`index.yaml` diff is empty both runs) — a potential `ideation-start` embedded-mode gap
distinct from the git-persistence mechanism under test here. Does not affect AC-20/AC-11/AC-21 (the
`_PROVENANCE_REF_PATTERNS` regex matches the sha, not the id's semantic correctness) — noted, not
escalated, out of this task's scope.

## AC-21 — PROVEN (static, both before and unaffected by the above)

See `2026-07-18_02_protocol_run1-and-finding.md` — grep of all non-`scripts/playground/` factory
code found zero harness-specific special-casing; all `test_harness_app` mentions outside playground
are ordinary project-type guidelines/gates or generic mechanisms. Unaffected by the deploy.py fix
(which lives inside `scripts/playground/`, the encapsulation boundary itself).

## Cost / cleanup

Total real spend this task: run1-blocked attempt $2.0629 (wasted, pre-fix) + run1 fresh-complete
$1.9704804 + run2 $0.6758868 ≈ **$4.71** (plus untracked partial spend from two session-teardown-
killed attempts, likely small — no cost was ever recorded for those in the run registry). Preserved
dead workspace `playground_ws_8303399e` (BLOCKED, pre-fix, superseded) left in place as an audit
trail alongside its run-registry record — not deleted, matches how the earlier ABANDONED run
(TASK-PROC-068-14) was also left in place.

## Outcome

**All three ACs (AC-20, AC-21, AC-11) verified PASS against real, observed build/maintain
behaviour** — no stubs, no `f(x)==x` self-derivation. One real defect found, escalated, developer-
authorized, fixed, and gate-verified along the way (has_recorded_blocker false-positive on
pre-existing host `pending_feedback` state).
