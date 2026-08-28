# Protocol 20 — Reset to pending, gated on the delegated-LLM-work fix (REQ-PROC-041-06)

Author: interactive session (developer-directed), 2026-07-06.

## Why this reset

This task's remaining work (the AC-4 depth re-derivation owed per checkpoint-18) can only be authored
into the harness via the **contained `bwrap` nested-`claude` playground child** (protocols 13–19). That
mechanism is exactly what repeatedly failed: it is expensive (~$1.7 / ~40 turns), **rate-limit-prone**
(429 mid-run, twice), self-approving, and — run out-of-band while the launching session exits — it is
the root of the TASK-PROC-068-11 incident (parent exits 0 → orchestrator mis-reads as done → deletes
`pending_feedback/` → child dies at 0 output → destructive clean-slate re-runs every resume).

A new requirement now addresses precisely this class of failure: **REQ-PROC-041-06
(`feat_delegated_llm_work`)** — a first-class delegated-LLM-work task state, a host-level
user-configurable **pool-capacity semaphore** (default 1) so the nested child cannot race the shared
account pool, a **verified-artifact completion verdict** (no false `EXIT=0` success), and an
**idempotent no-destroy-without-replace re-entry** invariant. Its impl+verify tasks are
TASK-PROC-041-06-02..05.

**Decision (developer-directed):** rather than answer the protocol-19 A/B/C venue question now against
the *unfixed* orchestrator, gate this task on the fix and give it a clean run afterward.

## Actions taken

1. **Gated on the fix.** `after:` now includes `TASK-PROC-041-06-05` (the delegated-work **verify**
   task) in addition to the already-complete `068-16` + `066-13`. This task stays blocked until the
   delegated-work mechanism is implemented AND verified.
2. **Reset to `pending`.** `status: in_progress → pending`; removed the stale `session_id`
   (`13c0851e…`), `session_account`, and `started` — so the orchestrator does not resume the old
   (rate-limited) session and instead starts a clean run once unblocked.
3. **Working tree restored.** The 5 stray-deleted harness anchor files
   (`test_harness_app/requirements_user_needs/…` — 2 personas, 2 scenarios, SCENARIO_INDEX) were
   restored from HEAD (`git checkout`). They were an uncommitted deletion from the original
   `91be1f5b` session; the 066-13-corrected baseline is intact at HEAD. Nothing lost.
4. **Stray `/tmp` marker cleaned** (`/tmp/harness_authoring.log` from the original run).
5. **Protocol-19 A/B/C venue question retired.** `automation/pending_feedback/TASK-PROC-068-11/` is
   removed from the active inbox; the full decision context is preserved in **protocol 19** (and here).
   The venue choice (automated contained run vs. interactive "live test") is **deferred to when this
   task actually runs** — and is *safer either way* once 041-06 is in place. The re-derivation
   substance (checkpoint-18: deepen both personas + both scenarios against the TASK-PROC-010-17
   Driver–Context spine, `5cb7e7f2`, via the real `ux-*` skills) is unchanged and still owed.

## Net state

`pending`, no session, blocked on `TASK-PROC-041-06-05`. Working tree clean of this task's residue.
On the next orchestrator run it will NOT be selected until the delegated-work fix is verified; then it
gets a first clean, fix-protected run.
