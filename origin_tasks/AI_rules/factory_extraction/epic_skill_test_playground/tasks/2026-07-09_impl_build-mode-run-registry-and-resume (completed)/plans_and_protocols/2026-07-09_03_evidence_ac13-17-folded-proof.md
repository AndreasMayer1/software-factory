# Folded AC-13..AC-17 real-artifact verification (TASK-PROC-068-22, EGP archetype F)

Real (non-mocked filesystem) run executed 2026-07-09, automated session
`7d1fa37d-f0de-4522-b79c-3611a4932f05`. Methodology = the developer-accepted AC-11 functional-proof
precedent (`../../2026-07-02_impl_playground-build-mode-harvest (completed)/plans_and_protocols/2026-07-03_02_evidence_ac11-functional-proof.md`):
exercise the REAL building blocks against REAL on-disk artifacts with a **cheap deterministic
contained child** (a `LaunchDeps` popen side-effect that authors a real net-new product-def file),
NOT a full `claude -p` derivation. Rationale: a real multi-hour nested `claude` derivation is
expensive and could itself trip the shared usage-limit and freeze the running session; the NEW
logic this task adds (registry enrichment, cold re-attach, dynamic poll, completion-gated harvest)
is filesystem/registry logic whose correctness is independent of whether the child is `claude` or a
deterministic script — exactly the AC-11 precedent's argument. OS-level containment itself is proven
separately by AC-09's real bwrap/unshare jail test.

Harnesses (ad-hoc, run from `/tmp`, removed after — as the AC-11 proof did):
`/tmp/t2_proof_partA.py` (fresh run → preserved) and `/tmp/t2_proof_partB_cold.py` (a SEPARATE cold
interpreter → re-attach → complete). Scratch target `/tmp/t2_proof/target` (never the tracked
`test_harness_app/`, so the mechanism proof pollutes no repo tree). Isolated copy created at the
REAL worktree_root `/workspaces/private_mood_tracker`.

## AC-13 — isolated copy at the configured out-of-project location, its own git repo
Part A, real `create_workspace` + `deploy_candidate` + `init_workspace_git`:
- workspace path `= /workspaces/private_mood_tracker/playground_ws_t2proofA` — under the real
  worktree_root, **not** `/tmp` → `is under worktree_root (not /tmp): True`.
- `.git present: True` — the copy is its own git repository.

## AC-14 — preserve-by-default (interrupted) vs harvest-then-discard (complete), real-artifact oracle
- **Interrupted run** (Part A, `completion_predicate → False`): `completed=False`,
  `workspace_preserved=/workspaces/private_mood_tracker/playground_ws_t2proofA`, `harvested_paths=[]`,
  registry `status=preserved`. The child-authored file exists in the copy
  (`child-authored file exists in copy: True`) yet was **not** harvested
  (`NOT harvested into target: True`) — preserve-by-default, harvest skipped entirely.
- **Completed run** (Part B resume, `completion_predicate → True` + clean exit): `completed=True`,
  `harvested_paths=['requirements_user_needs/user_flows/_t2_proof/flow.md']`, the real net-new file
  landed in the target (`child file harvested into target: True`), the isolated copy was discarded
  (`preserved copy discarded (workspace gone): True`), registry `status` flipped to `complete`. The
  real-artifact oracle: a real file authored on disk by the child, harvested into a real target,
  then the copy removed.

## AC-15 — cold session re-attaches from the registry, no re-deploy/seed/snapshot
Part B is a **fresh interpreter** (no in-memory carryover from Part A). It:
- discovered the preserved run purely from the on-disk registry
  (`build_resume.find_resumable_run` → `t2proofA-…`);
- reused the PRESERVED workspace (`reused preserved workspace (existed before resume): True`);
- **proved** deploy/seed/snapshot are never re-run by monkeypatching every `_prepare_workspace`
  building block (`create_workspace`, `deploy_candidate`, `init_workspace_git`,
  `sync_product_definition`, `snapshot_product_definition`) to RAISE — `resume_run` completed
  without raising (`resume completed WITHOUT calling any _prepare_workspace block: True`), and the
  resume manifest carried `seeded_paths=[]` (no re-seed). The persisted baseline sidecar
  (12 pre-child hashes) was reused, not recomputed.

## AC-16 — usage-limit-as-freeze (no orchestrator change) + dynamic completion poll
Two independent grounds:
1. **Shared-window freeze/resume, no orchestrator modification** — code-inspection of
   `scripts/automation/orchestrate.py::rate_limit_sleep` (line ~213): on all-accounts-limited the
   orchestrator sleeps until the ABSOLUTE reset time (`reset_dt`), recomputing remaining as
   `(reset_dt - now)` each tick (WSL2-suspend-safe), then resumes. Both the inner orchestrator
   (deployed into the isolated copy via `automation/`, G2-5) and the outer orchestrator call the
   same primitive — the shared account window freezes the whole tree together and thaws it together
   (synthesis §"Usage-limit", G2-4). No change to `orchestrate.py` was made or required (goal
   Out-of-Scope confirms). The cold-resume mechanism proven in AC-15 is the same path that re-runs
   after a limit-kill.
2. **Dynamic completion poll (not a fixed 15 min)** — `completion_poll.compute_poll_interval`
   scales with remaining ChainState units, clamped `[floor=60s, ceiling=900s]`:
   `{0→60, 1→60, 5→300, 20→900, 100→900}` — floor honoured at 0 units, scales at 5 units (300s),
   ceiling honoured at 100 units (not unbounded, not the old fixed 15-min constant).

The full **real usage-limit reset** derivation-resumability proof (REQ-PROC-071-06 AC-08) is
explicitly **T3** (`TASK-PROC-068-23` or successor), per the goal's Out-of-Scope — it requires a
real multi-hour nested derivation under a real reset, out of this task's scope.

## AC-17 — injected completion predicate over the copy path (not hard-coded to layer-derivation)
Part A: the injected predicate recorded the path it was called with;
`predicate saw copy path == workspace: True`. `build.py` imports no `ChainState`
(re-confirmed by T1's `test_completion_predicate_is_injected_and_receives_copy_path`).

## Cleanup
Isolated copy discarded by the completed resume (`shutil`-based `destroy_workspace`, prefix-guarded,
never git-reset). Post-run: no `playground_ws_*` residue under the worktree_root; `/tmp/t2_proof`
removed; no change to any tracked repo tree from the proof (only this task's source/skill/test files
remain in `git status`).

## Verdict
All of AC-13, AC-14, AC-15, AC-16 (mechanism + dynamic poll; real-limit reset deferred to T3 per
scope), and AC-17 confirmed end-to-end against real on-disk artifacts.
