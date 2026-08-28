---
task_id: TASK-PROC-068-19
type: bugfix
parent_requirement: REQ-PROC-068
urgency: 4
urgency_reason: U3-QUALITY
impact: 4
impact_reason: I4-QUAL
status: completed
started: 2026-07-07
completed: 2026-07-08
session_completed_at: 2026-07-08T06:58:28Z
effort: M
created: 2026-07-07
expected_tool_calls: 45
skill_chain_depth: 2
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-11]
  sections: []
egp:
  - { ac: AC-11, archetype: F, referent: "a real build/maintain run observed to derive the harness layers in an isolated deployed copy and deposit the registry-classified product-definition artifacts into test_harness_app/, retaining them" }
consequence: MEDIUM
scope_description: "Fix (1) scripts/playground/build.py's build-mode so a REAL contained `claude` child authenticates (stop scrub_env redirecting HOME, honoring AC-12), and (2) scripts/playground/deploy.py so it stops deploying the factory's own requirements_tasks/process/** governance corpus into the harness copy (not needed at runtime — only when authoring the skills themselves, which never happens in the harness), which is the ROOT of the ~130-file harvest over-inclusion. Re-prove AC-11 with a real authenticating child — AC-11 ∧ AC-12 together — and confirm a real factory skill still runs end-to-end with process/ excluded (AC-10)."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: 524a8867
  file: ../requirements.md
session_id: ed35d6af-be83-477a-a5d1-1339cef455f0
session_account: gmail2
---
# Goal: Ensure that AC-11 (build mode) of REQ-PROC-068 works correctly with a real authenticating child (honoring AC-12) and a process-free deploy (no harvest over-inclusion)

## Objective

`scripts/playground/build.py`'s build/maintain mode (AC-11) has **never run a real `claude` child
successfully end-to-end**. Two defects make a real build-mode run fail or corrupt the harness; both were
hand-patched in TASK-PROC-068-11's throwaway driver but remain unfixed in `build.py` itself. Fix both in
`build.py`, then re-prove AC-11 with a **real authenticating child** — the combined proof (AC-11 ∧ AC-12)
that the original AC-11 verification never ran.

## Bug Report

**Steps to reproduce:**
1. Invoke `run_build_mode()` (or `build.py`'s CLI) so it deploys the whole factory into an isolated
   copy, seeds from `test_harness_app/`, and launches a **real `claude -p` child** to derive the harness
   product-definition layers.
2. Observe the child's authentication, and observe what lands in `test_harness_app/` after the harvest.

**Expected behavior:**
- The contained `claude` child **authenticates** and runs the derivation (AC-12: `~/.claude` bound at its
  real path, child's real HOME preserved).
- The harvest deposits into `test_harness_app/` **only the product-definition artifacts the derivation
  actually authored** — nothing else is retained.

**Actual behavior:**
- **Defect 1 — auth broken (build-mode path only).** `build.py:277` sets
  `child_env = scrub_env(dict(os.environ), cfg.isolated_dir)`. `scrub_env` (`containment.py`) redirects
  `HOME` into the isolated copy, so the `claude` CLI expands `~/.claude` to `<isolated_dir>/.claude` —
  which is not bound — and **cannot authenticate**, defeating AC-12's real-path bind. The sibling
  `run_skeleton.py:238` does the opposite on purpose (`child_env = dict(os.environ)`, real HOME,
  explicitly citing AC-12); `build.py` was never brought into line.
- **Defect 2 — harvest over-inclusion (root cause: deploy keeps process/ needlessly).** `deploy.py`
  keeps `requirements_tasks/process/**` in the deployed copy — but **by omission, not by a demonstrated
  runtime need**: its exclude-set comment justifies keeping `requirements_user_needs/` machinery (the
  README type-defs the authoring skills read) but gives **no** runtime justification for the process
  corpus. Those ~130 `requirements_tasks/process/AI_rules/**/requirements.md` files are the **specs that
  define the factory's own skills/scripts** — read only when *authoring* those skills, which never
  happens inside the harness (the harness runs candidate skills against a product; it does not develop
  the factory). Because they are deployed, the full-registry harvest's `requirements` glob
  (`requirements_tasks/**/requirements.md`) matches them and sweeps them into `test_harness_app/`.
  `deploy.py` calls the over-inclusion "safe *because git-reset between runs*", which holds for test mode
  (`run_skeleton.py` resets) but **not** for build mode, which harvests before discarding and never
  resets. (Observed live in TASK-PROC-068-11 protocol 25: "swept ~130 unrelated files".) **Fix at the
  root: stop deploying process/ at all** — nothing that runs in the harness needs it, so it cannot be
  harvested.

**Environment:** devcontainer (Linux), bwrap available; host `~/.claude` present.

**Logs:** see `../2026-07-02_impl_playground-build-mode-harvest (completed)/plans_and_protocols/2026-07-03_02_evidence_ac11-functional-proof.md` (documents the over-inclusion risk it deferred) and `../2026-07-01_impl_harness-anchors-reauthor/plans_and_protocols/2026-07-06_23_protocol_rename-and-redrive-launch.md` (protocol 23 — why the throwaway driver dropped `scrub_env`) and `…/2026-07-06_25_protocol_redrive-succeeded-park-for-ac4.md` (protocol 25 — the harvest-scope cleanup).

## Why the original AC-11 verification missed both

The AC-11 EGP-F "functional proof" (TASK-PROC-068-18) substituted a **deterministic bash action**
(`mkdir`/`printf`) for the real `claude` child — "a real but cheap deterministic contained action" — so
(a) a bash write needs no `~/.claude`, hiding the `scrub_env` auth break, and (b) the proof narrowed its
own real harvest to a single glob to sidestep the over-inclusion it had just documented. AC-11 and AC-12
were each "verified" separately; **no proof ever ran a real authenticating child through
`run_build_mode()`** — the exact intersection where both defects live. This bugfix closes that gap.

## Scope

### In Scope
- **Fix Defect 1** in `build.py`: stop redirecting HOME for the child env — mirror `run_skeleton.py`'s
  real-HOME approach so the AC-12 auth binds resolve. (Prefer aligning `build.py` with `run_skeleton.py`;
  if `scrub_env` is genuinely needed for a bwrap-unavailable fallback, make its use conditional on that
  fallback rather than unconditional.)
- **Fix Defect 2** in `deploy.py`: add `requirements_tasks/process` to `_SUBFOLDER_EXCLUDES` so the
  factory's own governance corpus is **never deployed** into the harness copy — removing the harvest
  over-inclusion at its root (nothing to sweep in). Update the exclude-set comment to record *why*
  (process specs are authoring-time inputs, not harness-runtime inputs).
- **Validate the "not needed at runtime" claim (AC-10 guard):** confirm a real factory skill that runs
  in the harness (e.g. `layer-derivation-start` / `requ-explore` / `ux-write-persona`) still completes
  **end-to-end** with process/ excluded. If any skill is found to actually *read* a
  `requirements_tasks/process/**/requirements.md` at runtime, STOP and escalate (that is an AC-10
  tension — a requirements decision, not a silent workaround).
- **Re-prove AC-11 with a real authenticating child** (AC-11 ∧ AC-12): a minimal, cheap-but-real
  `claude -p` child that authenticates and writes one product-def artifact; assert the child authenticated
  AND that `test_harness_app/` gained **only** that artifact (no factory-governance files).
- Python quality gates green (`scripts/quality/check_python_gates.sh`).
- All `scripts/` edits go through the `claude-write-script` skill.

### Out of Scope
- Changing what `deploy.py` copies **beyond** excluding `requirements_tasks/process` (the AC-10
  whole-factory contract otherwise stands; AC-10 delegates the enumeration to the factory and requires
  only that skills run end-to-end, which the validation above confirms).
- Editing REQ-PROC-068 AC-10 text — not needed unless the validation surfaces a real runtime dependency
  on process specs (then escalate).
- `run_skeleton.py` (test-and-reset mode) — already correct; do not regress it.
- Re-authoring any harness persona/scenario/flow content (that is TASK-PROC-068-11 / -12).
- The `ux-write-persona/scenario` targeting story and the persona-brevity rework (TASK-PROC-010-18).

## Acceptance Criteria

- [x] AC-1: `build.py` build-mode launches a **real `claude` child that authenticates** — the child's env
      preserves real HOME (or `scrub_env` is applied only on the bwrap-unavailable fallback), so AC-12's
      `~/.claude` bind resolves. Regression-checked against `run_skeleton.py`'s working pattern.
- [x] AC-2: `deploy.py` no longer deploys `requirements_tasks/process/**` into the harness copy
      (`_SUBFOLDER_EXCLUDES` extended; comment updated with the rationale). Consequently a build-mode run
      leaves **zero** deploy-brought `requirements_tasks/process/**/requirements.md` files in
      `test_harness_app/`.
- [x] AC-3: **AC-10 guard — skills still run with process/ excluded.** A real factory skill that runs in
      the harness completes end-to-end against the process-free deployed copy. Any discovered runtime read
      of a `requirements_tasks/process/**/requirements.md` is escalated (AC-10 tension), not worked around.
- [x] AC-4: **Combined real-child proof (AC-11 ∧ AC-12).** A real authenticating `claude -p` child is run
      through `run_build_mode()` (minimal/cheap), and the evidence records: the child authenticated, it
      wrote a registry-classified product-def artifact in the isolated copy, and `test_harness_app/`
      gained **only** that artifact. Written to `plans_and_protocols/`. This is the proof the original
      AC-11 verification substituted away.
- [x] AC-5: Unit tests updated so build-mode's env is asserted (preserves real HOME) and `deploy.py`'s
      new exclude is asserted (process/ absent from a deployed copy) — not silently faked past. Python
      gates green.
- [x] AC-6: `[DIAG-*]` prefix on any diagnostic `debugPrint`/print; `// TEMPORARY:` on any temporary probe
      (per CLAUDE.md bugfix conventions); all such artifacts removed at close (`task-complete-bugfix`).

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking predecessors; the working pattern (real HOME + auth binds) already exists in `run_skeleton.py` / `containment.py` |

## Related Tasks

| Task | Reason |
|------|--------|
| [../2026-07-02_impl_playground-build-mode-harvest (completed)/goal.md](../2026-07-02_impl_playground-build-mode-harvest%20%28completed%29/goal.md) | Implemented build.py (AC-11) with the scrub_env auth bug + full-registry harvest; its AC-11 proof substituted an auth-free bash action and deferred the over-inclusion |
| [../2026-07-01_impl_harness-anchors-reauthor/goal.md](../2026-07-01_impl_harness-anchors-reauthor/goal.md) | TASK-PROC-068-11 — hit both defects live (protocols 23–25) and hand-patched them in a throwaway driver; the real consumer that needs build-mode to actually work |
| [../2026-07-01_impl_harness-middle-rederive/goal.md](../2026-07-01_impl_harness-middle-rederive/goal.md) | TASK-PROC-068-12 (pending) — the task the over-inclusion was deferred to; will run a real full build-mode harvest and needs this fix first |

## Notes

- The working reference already in-repo: `run_skeleton.py:227-238` (real HOME + inherited
  `CLAUDE_CONFIG_DIR`, AC-12) and `containment.py::_auth_config_binds` (real-path `~/.claude` bind). This
  bugfix brings `build.py` into line with them.
- Execution: `code-bugfix` (slim/scripts mode); all `scripts/` edits via `claude-write-script` (runs
  Python gates); close via `task-complete-bugfix`.
- Root process lesson (for the protocol): AC-11 and AC-12 were verified separately, each against a
  workload chosen for cheapness; nothing tested their intersection. AC-3 here is deliberately the
  combined proof.
