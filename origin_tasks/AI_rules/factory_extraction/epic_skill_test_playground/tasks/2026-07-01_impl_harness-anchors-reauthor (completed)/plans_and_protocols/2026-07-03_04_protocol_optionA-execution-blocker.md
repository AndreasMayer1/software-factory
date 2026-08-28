# Protocol 04 — Option A resume: execution blocked by an unfixed repo-destroying hazard

Task: TASK-PROC-068-11 · resumed 2026-07-03 after developer chose **Option A** (cwd/deploy redirect)
in feedback checkpoints 02/03 (identical resolutions, authored by TASK-PROC-068-17).

## What the resolution told me to do

1. Clean-slate the non-conformant anchors.
2. Complete the harness structural mirror (goal step 4 / AC-01).
3. Run `scripts/playground/deploy.py` to deploy the whole factory into `test_harness_app/`.
4. Invoke `ux-write-persona` / `ux-write-scenario` with the deployed harness as cwd, via a contained
   child session (`scripts/playground/containment.py`).
5. Park again for the developer approval gate (AC-4).

Grounds given: TASK-PROC-068-16 "extended deploy to the whole factory" and its AC-10 evidence proved
the mechanism working.

## What I verified before touching the tree (all read-only)

**Finding 1 — the git-reset topology hazard is real, unfixed, and repo-destroying.**
- `git -C test_harness_app rev-parse --show-toplevel` → `/workspaces/private_mood_tracker/flutter_app`.
  `test_harness_app/` is **not its own git repo**; it is tracked by the outer repo (31 files) and is
  **not** gitignored (only `node_modules/`, `dist/` are).
- `scripts/playground/reset.py::reset_harness` runs `git reset --hard HEAD` + `git clean -fdx` with
  `cwd=<harness>`. On the real `test_harness_app/`, `git reset --hard HEAD` resolves to the **outer**
  repo and would **discard all uncommitted work across the entire `flutter_app` tree**.
- This is not my inference alone — the 068-16 plan states it verbatim ("Discovered risk … not fixed —
  out of this task's scope"): making `test_harness_app/` its own repo (`git rm --cached -r` + gitignore
  + nested `git init`) is "a topology change touching AC-01/AC-06/AC-11 assumptions … well beyond
  'extend deploy'." It was flagged as a candidate follow-up and **never created as a task**.

**Finding 2 — the AC-10 proof did NOT prove what Option A needs.**
- The AC-10 functional proof (`…2026-07-02_impl_extend-harness-deploy-full-factory/…/2026-07-03_02_evidence_ac10-functional-proof.md`)
  ran inside a **disposable scratch repo** (`mktemp -d` + its own `.git`), explicitly "never the real
  `test_harness_app/`, per the discovered hazard."
- It executed a **stdlib-only Python script** (`doc_governance.py --list-violations`) inside the bwrap
  jail — **not a `claude` child session**. The one script it *tried* that needed a user-site dependency
  (`generate_id_registry.py` → `ruamel.yaml`) **failed** in the jail because bwrap binds only `/usr`,
  `/etc` (+ harness), not `/home/vscode/.local/...`.
- The only code path that launches a real `claude` child session, `run_skeleton.py`, wraps it in the
  same `--unshare-all` bwrap jail (**no network** → the Anthropic API is unreachable) **and ends with
  `reset_harness()`** (Finding 1's repo-destroying reset, and it would erase the just-authored anchors
  anyway). No evidence exists that a `claude` session has ever run against the real harness.

**Finding 3 — the authoring skills' guidelines are not present in the deployed harness.**
- `deploy.py` **excludes `requirements_user_needs/`** at the top level. `ux-write-persona` /
  `ux-write-scenario` read `requirements_user_needs/README_3…/README_4…` etc.; with cwd=harness those
  resolve under `test_harness_app/requirements_user_needs/`, which has no README type-defs. The mirror
  step (goal step 4) must seed them, but that is a separate design point (are the type-defs harness
  content, or factory content that deploy should stop excluding?).

## Why I am not proceeding

Executing Option A as written means (a) flooding the outer-repo-tracked `test_harness_app/` with a
whole-factory copy, then (b) running an unproven, almost-certainly-non-functional `claude`-in-bwrap
authoring session (no network / binary / creds / READMEs), in a mechanism whose only persistence-capable
orchestrator (`run_skeleton`) carries a `git reset --hard` that resolves to the **entire repo**. The
downside is catastrophic and hard to reverse (whole-tree work loss), the upside path is unproven. Per
the confirm-before-hard-to-reverse rule I will not run it. The machine resolution (068-17) relied on the
AC-10 proof without accounting for the fact that the proof was scratch-only *specifically to dodge this
hazard*, and proved script-exec, not claude-session authoring.

## Recommended safe paths (for the developer to choose)

- **A1 — fix the harness git topology first (prerequisite task).** Create/authorize the flagged
  follow-up: make `test_harness_app/` its own git repo (`git rm --cached -r test_harness_app` + add to
  root `.gitignore` + nested `git init` + seed commit). Then the deploy/isolate/reset model is safe and
  Option A can run. This is the clean, if larger, path — and it is the prerequisite 068-16 already
  identified.
- **A2 — minimal trusted authoring (no containment, no reset).** This is the *host* factory authoring
  the harness's *own* anchors — a trusted one-time seed, not an untrusted-candidate regression run
  (AC-09's threat model is untrusted candidates). Seed the harness mirror (`CLAUDE.md`, `doc/`,
  `requirements_user_needs/README_*`, `.claude/skills/`), then run a `cd test_harness_app && claude -p`
  child session (NO bwrap, NO reset) that invokes the two authoring skills so they write into
  `test_harness_app/requirements_user_needs/`. Requires developer sign-off because it (i) shells a
  nested `claude` session (CLAUDE.md §Agent Spawn Topology normally forbids this outside the sanctioned
  playground path) and (ii) intentionally skips containment for a trusted run.
- **A3 — parametrize the skills (former Option B).** Add a target-root arg to the two skills via
  `claude-modify-skill` so they author into `test_harness_app/…` from this session directly (harness-
  local ID space / SCENARIO_INDEX / cascade scope). No nested session, no deploy, no reset hazard.

I have made **no tree mutations** (clean-slate not yet run) so a clean re-park strands nothing.
