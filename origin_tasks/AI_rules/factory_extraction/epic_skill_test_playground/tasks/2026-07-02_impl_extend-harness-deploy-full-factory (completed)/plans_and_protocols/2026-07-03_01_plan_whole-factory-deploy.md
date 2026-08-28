# Plan — Extend harness deploy to whole factory (TASK-PROC-068-16)

Agent: main session (automated), session_id 49f95366-4629-4938-81b9-2b2675477080

## Approach: inline (single script + its test file; no agent delegation — read/act loop is small)

## Exclude sets (from goal.md's developer-approved list + entangled-tree risks)

Resolved against the real top-level tree (`LC_ALL=C ls -1`):

- Top-level excludes (exact name match at repo root):
  `.codegraph .dart_tool .idea .roo_archive .vscode .VSCodeCounter .git .github .githooks
  .mypy_cache .pytest_cache .ruff_cache .venv android assets build coverage doc-temp web
  windows Temp figma ios linux macos packages lib integration_test test test_driver
  test_hive dev-analytics releases requirements_market_research requirements_general_overview
  requirements_user_needs test_harness_app`
  (`test_harness_app` excluded per risk 1 — it is the deploy target, not factory content.
  `requirements_user_needs` excluded wholesale — risk-note classifies it as pure app content,
  not mixed.)
- Sub-folder excludes (path relative to repo root, only meaningful inside otherwise-copied trees):
  `requirements_tasks/functional`, `requirements_tasks/non-functional`
  (`requirements_tasks/process/**` and other non-app subfolders of `requirements_tasks/` are
  copied — this is the factory's own requirement corpus.)
- `scripts/` and `doc/` are mixed (factory+app) per the seed plan, but over-inclusion is safe
  (harness is isolated + git-reset; can't breach AC-09). No sub-folder split attempted for them —
  copied wholesale. extraction-synthesis §1a/§1b is a non-authoritative reference only.

## Implementation

`scripts/playground/deploy.py::deploy_candidate` extended (via `claude-write-script` skill,
mandatory for scripts/ edits):
- Copies `host_project_dir` → `harness_dir` wholesale using `shutil.copytree(..., ignore=...,
  dirs_exist_ok=True)`.
- `dirs_exist_ok=True` (no upfront `rmtree`) — preserves the harness's own `.git` across repeat
  deploys; the pipeline's existing `reset_harness()` step (runs *after* each fixture, so *before*
  the next deploy) is what brings the harness back to a clean baseline, not the deploy step.
- Ignore-callback computes each entry's path relative to the copy root so it can apply both the
  top-level-only excludes and the `requirements_tasks/{functional,non-functional}` sub-folder
  excludes. Marked `# TEMPORARY:` per goal.md's requirement (coarse rule, replaced post-extraction
  per REQ-PROC-066 scope — noted, not created).
- `list_deployed_skills` unaffected (still reads `.claude/skills/` inside the now-larger deployed
  tree).

`reset.py` / `run_skeleton.py`: **not modified**. See "Discovered risk" below for why touching
reset's git semantics is deliberately left alone.

## Discovered risk (documented, not fixed — out of this task's scope)

`test_harness_app/` (the real, persistent harness dir used by the orchestrator) is **not its own
git repository** — `git -C test_harness_app rev-parse --show-toplevel` resolves to the outer
`flutter_app` repo root. Empirically verified in a throwaway scratch repo:
- `git clean -fdx` run with `cwd=<subdir>` **is** scoped to that subdir (safe).
- `git reset --hard HEAD` run with `cwd=<subdir>` (no nested `.git`) resets/reverts the **entire
  outer repository**, not just the subdir (confirmed by reproduction: a modified file at the outer
  repo root was silently reverted by a `reset --hard` invoked from a plain subdirectory).

`reset.py::reset_harness()` runs both commands with `cwd=harness_dir` and no pathspec. Today this
is (accidentally) inert only because `test_harness_app/` has near-zero real usage history. Once
whole-factory deploy is live and the orchestrator actually drives `run_skeleton.py` against the
real `test_harness_app/`, the `reset_harness()` step in that pipeline would hard-reset the *entire*
host repo — a repo-wide destructive operation, not scoped containment.

**Decision for this task**: do not restructure `test_harness_app/`'s git topology (would mean
`git rm --cached -r test_harness_app`, adding it to root `.gitignore`, and `git init`-ing a nested
repo — a topology change touching AC-01/AC-06/AC-11 assumptions elsewhere; well beyond "extend
deploy (and reset/launch as needed)"). Instead:
- The AC-10 functional proof (below) uses a **disposable scratch directory outside the repo**,
  initialized as its own throwaway git repo, as `harness_dir` — never the real `test_harness_app/`.
  This proves deploy + containment + script-calling-skill execution for real, without going near
  the hazard.
- This finding is recorded here for the developer; flagging as a candidate follow-up (not created
  as a task — no new work is being spawned by this task).

## AC-10 functional proof design

1. Scratch dir `mktemp -d` (e.g. `/tmp/playground-proof-XXXX`), `git init` + one commit so
   `git -C scratch rev-parse --show-toplevel` resolves to itself (matches reset.py's assumption).
2. Real (non-mocked) `deploy_candidate(host_project_dir=<repo root>, harness_dir=scratch)`.
3. Assert exclusions took effect (`lib/`, `test/`, `requirements_user_needs/`,
   `requirements_tasks/functional/` absent; `scripts/`, `.claude/skills/`,
   `requirements_tasks/process/` present).
4. Real containment: `wrap_with_containment(cmd, scratch)` wrapping a script-calling skill's
   underlying script (e.g. `generate_id_registry.py`, which anchors on
   `script_dir.parent.parent` — exactly the failure mode AC-10 exists to close), run with
   `cwd=scratch`, asserting successful completion using only deployed contents.
5. Negative control: attempt to read a host-tree sentinel file by absolute path from inside the
   jail — must fail (reuses the pattern from
   `test_real_jail_blocks_host_tree_access`), evidencing "no reach-back."
6. Optionally exercise `reset_harness(scratch)` too (safe here — scratch has its own `.git`) as a
   bonus demonstration of the full deploy→run→reset cycle working end-to-end.
7. Capture transcript into this task's `plans_and_protocols/` as the EGP-F evidence artifact; clean
   up the scratch dir.

## Steps

1. [x] Read goal.md + seed plan + real top-level tree + entangled risk notes.
2. [x] Empirically verify the git-reset scoping hazard in a throwaway repo (no host risk taken).
3. [x] `claude-write-script` → extend `deploy.py`.
4. [x] `claude-write-script` → extend `scripts/tests/test_playground_deploy.py`.
5. [x] Run Python quality gates — G1/G2/G4/G5/G6/G7 PASS; G3 fails only on 2
   pre-existing baseline failures in `test_aggregate_read_metrics.py`
   (confirmed via `git stash` + re-run against the unmodified baseline —
   unrelated to this task's files). `test_playground_deploy.py` +
   `test_playground_run_skeleton.py`: 28/28 passed.
6. [x] Execute the real AC-10 functional proof (scratch dir), capture evidence
   → `2026-07-03_02_evidence_ac10-functional-proof.md`.
7. [x] `doc-update-guidelines` — not warranted (no non-obvious gate workaround;
   the git-topology finding is a design/process risk, not a doc/ gap; already
   documented in this plan for the developer).
8. [ ] `claude-log`.
9. [ ] `task-complete`.
