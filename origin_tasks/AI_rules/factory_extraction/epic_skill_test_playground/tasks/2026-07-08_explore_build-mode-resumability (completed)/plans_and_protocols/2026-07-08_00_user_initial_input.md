# User Initial Input (verbatim)

Preserved raw, as a seed bed — not a spec.

---

> we need to create a task to explore how to make that resumable. I think one session should start the work in the pther project and then terminate. another session must resume it later. But how?
> the task shall find a solution and it's goal shall include to update the requirments and create impl tasks for it. It shall build a mechanism that unblocks 068-12

> Let it use the ideation skill

---

## Immediate context that prompted this (session investigation, 2026-07-08)

"That" = the DEPLOYED build-mode layer-derivation run. `scripts/playground/build.py::run_build_mode`
launches ONE contained `claude -p` child session, then **unconditionally** does
`record cost → harvest_authored → shutil.rmtree(copy)` with **no** check on
`result.returncode` / `result.succeeded` / `result.reason`.

Consequence when a usage-limit hit, a hung/session_timeout, or any non-clean exit interrupts the
derivation mid-run (the whole session tree shares one account/auth window via the `~/.claude` bind,
AC-12):
- a **partial, possibly incoherent** harvest lands in the real `test_harness_app/`, and
- the copy is **rmtree'd**, destroying the ChainState + commit-per-unit file-memory that would
  otherwise allow resume.

The LOCAL derivation is already resumable (feat_fixpoint_loop AC-02 loop-state in file-memory;
feat_backfill_orchestration AC-01 commit-per-unit; `layer-derivation-resume`). The DEPLOYED wrapper
throws that resumability away because the isolated copy is single-shot.
