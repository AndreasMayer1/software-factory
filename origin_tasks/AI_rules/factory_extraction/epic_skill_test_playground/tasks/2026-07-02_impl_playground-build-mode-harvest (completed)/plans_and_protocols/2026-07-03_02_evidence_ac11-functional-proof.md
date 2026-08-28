# AC-11 Functional Proof Evidence (EGP archetype F)

Real (non-mocked) run executed 2026-07-03. Scratch isolated copy at
`/tmp/playground-build-proof-whdtd1y5` (deleted after the run via
`shutil.rmtree`, never git-reset). Real interaction with the REAL
`test_harness_app/` for exactly the two operations the task scope allows:
(a) reading its current `requirements_user_needs/` for the seed step, (b)
the harvest step depositing the proof artifact.

Methodology mirrors T-B's AC-10 proof: exercises the real building blocks
(`deploy_candidate`, `sync_product_definition`, `wrap_with_containment`,
real `subprocess.run`) directly rather than the full `run_build_mode()` /
`run_with_hung_detection()` polling loop — that loop is designed around a
real `claude -p` child session (expensive); the proof needs a real but cheap
deterministic contained action, same principle as T-B's AC-10 proof running
a deterministic script instead of a real skill invocation.

## Setup

1. `HOST` = this repo root (`/workspaces/private_mood_tracker/flutter_app`).
2. `TARGET` = the REAL `test_harness_app/` (never a scratch stand-in for
   this proof — the task explicitly requires real interaction with it).
3. `REGISTRY` = `HOST/.factory/registry/artifacts.yaml`.
4. Baseline snapshot: 8909 files under the real `test_harness_app/` before
   the run (used at the end to prove exactly one new file landed).

## Step 1 — real `deploy_candidate`

```
deploy_candidate(HOST, isolated_dir) → isolated_dir now has 37 top-level
  entries: factory content (scripts/, .claude/, doc/, …) present;
  test_harness_app/ and requirements_user_needs/ absent (deploy_candidate's
  own exclude set — confirmed by assertion).
```

## Step 2 — real `load_product_definition_globs`

32 globs loaded from the real registry. Asserted: none of the 32 globs
start with a factory-machinery category prefix (`scripts/`, `.claude/skills/`,
`doc/`, `automation/`, `.factory/`) — the registry-driven classification
structurally cannot leak factory machinery into the harvest set.

## Step 3 — real seed: `sync_product_definition(TARGET, isolated_dir, globs)`

7 paths seeded from the REAL `test_harness_app/requirements_user_needs/`
into the isolated copy, including the harness's real current flows:
`FLOW-HARNESS-01_add_rating/flow.md`, `FLOW-HARNESS-02_browse_library/flow.md`,
`FLOW-HARNESS-03_review_insights/flow.md`, `FLOW_INDEX.md`. Confirms
`deploy_candidate`'s exclude of `requirements_user_needs/` is exactly what
build mode's seed step exists to backfill (module docstring's "why seed"
rationale, verified for real here).

## Step 2 — real contained (bwrap) child session writes the proof artifact

```
wrap_with_containment(['bash', '-c', "mkdir -p ... && printf ... > ..."], isolated_dir)
→ ['bwrap', '--unshare-all', '--die-with-parent', ...]   (real bwrap, not the
   PLAYGROUND_ALLOW_UNCONTAINED bypass — bwrap is available on this host)
subprocess.run(contained_cmd, env=scrub_env(...), cwd implied by --chdir isolated_dir)
→ returncode 0
```

Deterministically wrote:
`<isolated_dir>/requirements_user_needs/user_flows/_build_mode_proof/flow.md`
— a registry-classified path (matches the `flow` token's
`requirements_user_needs/user_flows/*/flow.md` glob, with `_build_mode_proof`
as the wildcard segment) inside the isolated copy's own product tree,
self-scoped, written by a real jailed child process.

## Step 4b — negative control

A host-tree sentinel file (`/tmp/host-sentinel-.../sentinel.txt`) was
created outside the isolated copy. `cat` of its absolute path inside the
same jail used for the proof-writing command returned exit code 1 (file
not found — absent from the child's mount namespace), confirming the
proof-writing action ran fully contained with no host reach-back.

## Step 5 — dry-run FULL-registry harvest (mechanism proof, scratch target only)

`sync_product_definition(isolated_dir, dry_harvest_scratch_dir, globs)` (all
32 globs) copied 138 paths, including the proof artifact, into a disposable
scratch directory (never the real `test_harness_app/`). Confirms the
registry-driven harvest mechanism is real and correctly classifies
categories end-to-end.

**Discovered risk (documented for TASK-PROC-068-12's awareness, not fixed
here — out of this task's mechanism-only scope):** of the 138 paths the
FULL-registry harvest would copy, 130 are pre-existing factory-governance
`requirements.md` files under `requirements_tasks/process/AI_rules/**` (and
potentially `requirements_tasks/scribbles/**/v*/` sets) that originate from
`deploy_candidate`'s whole-factory copy — NOT from anything a real
derivation authored. `deploy.py`'s exclude set only removes
`requirements_tasks/{functional,non-functional}` (app-owned content); it
deliberately keeps `requirements_tasks/process/**` because script-calling
skills need it present (AC-10, T-B). `deploy.py`'s own docstring calls the
resulting over-inclusion "safe" specifically *because* the harness is
"git-reset between runs" — that safety argument holds for test-mode
(`run_skeleton.py` resets after every run) but does **not** hold for build
mode, which harvests before discarding and never resets. A real,
unscoped, full-registry harvest run (e.g. by TASK-PROC-068-12, once it
actually invokes `run_build_mode()`) will therefore also copy this ~130-file
factory-governance corpus into the real `test_harness_app/` as a side
effect of the mechanism alone, independent of what the actual derivation
authors. Recommend TASK-PROC-068-12 (or a preparatory follow-up) address
this before running a real, full, unscoped build-mode harvest — e.g. by
diffing against the pre-seed isolated-copy state to harvest only what the
derivation itself newly wrote, or by giving build-mode's deploy step its own
tighter exclude set for `requirements_tasks/process/**`. Neither is
implemented in this task: `build.py` implements exactly what AC-11 and the
plan specify (full registry-category harvest); this is a downstream
interaction with `deploy.py`'s already-documented TEMPORARY over-inclusion,
not a defect in this task's own scope.

Because of this discovered risk, **the actual write into the real
`test_harness_app/` in step 6 below is deliberately scoped** to only the
glob relevant to the proof artifact, per this task's explicit boundary
("the harvest step depositing the proof artifact" — singular). The full
mechanism is still proven real (step 5, scratch target); only the narrower,
safe slice of it is applied to the real, tracked project tree.

## Step 6 — real SCOPED harvest into the REAL `test_harness_app/`

```
sync_product_definition(isolated_dir, TARGET, ["requirements_user_needs/user_flows/*/flow.md"])
→ ['requirements_user_needs/user_flows/FLOW-HARNESS-01_add_rating/flow.md',
   'requirements_user_needs/user_flows/FLOW-HARNESS-02_browse_library/flow.md',
   'requirements_user_needs/user_flows/FLOW-HARNESS-03_review_insights/flow.md',
   'requirements_user_needs/user_flows/_build_mode_proof/flow.md']
```

The three `FLOW-HARNESS-*` files were already present in the real
`test_harness_app/` (they were the seed source in step 3) — re-copying them
back is a no-op merge, not new content. The proof artifact is new.

## Step 7 — discard the isolated copy

`shutil.rmtree(isolated_dir, ignore_errors=True)` — confirmed
`Path(isolated_dir).exists() is False` afterward. Never git-reset (the
isolated copy is not reliably its own git repo — same topology hazard T-B
documented for `test_harness_app/` itself).

## Step 8 — real `test_harness_app/` gained exactly the proof artifact

Post-run file listing diffed against the step-0 baseline (8909 files):
exactly one new file —

```
requirements_user_needs/user_flows/_build_mode_proof/flow.md
```

`git status --porcelain -- test_harness_app` after the run shows only this
new untracked path (plus a pre-existing, unrelated untracked
`test_harness_app/.factory/` left over from an earlier session, not touched
by this proof).

## Conclusion

AC-11 referent satisfied: a real build/maintain run — real
`deploy_candidate` into a real isolated scratch copy, real seed from the
REAL `test_harness_app/`'s current `requirements_user_needs/`, a real
bwrap-contained child session that deterministically derived (wrote) a
registry-classified artifact inside the isolated copy's own product tree,
a real registry-driven harvest depositing that artifact back into the REAL
`test_harness_app/`, retained (not reset) — while the isolated copy itself
was discarded via `shutil.rmtree`.

**Retained proof artifact (for TASK-PROC-068-12's awareness — ignore it as
a synthetic marker, not real derived content, when authoring the real
harness middle layers):**

```
test_harness_app/requirements_user_needs/user_flows/_build_mode_proof/flow.md
```

**Discovered risk for TASK-PROC-068-12 (documented above, not fixed here):**
an unscoped full-registry harvest run will also sweep in ~130 pre-existing
`requirements_tasks/process/AI_rules/**/requirements.md` files that
`deploy_candidate`'s whole-factory copy brings into the isolated copy
regardless of what the derivation authors — a consequence of `deploy.py`'s
already-documented TEMPORARY over-inclusion combined with build mode's
"harvest before discard, no reset" model.

Cleanup: isolated copy, dry-harvest scratch target, and host sentinel all
removed after the run; no residue in `/tmp`. Only the one intended proof
artifact remains in the repository, and only in `test_harness_app/`.
