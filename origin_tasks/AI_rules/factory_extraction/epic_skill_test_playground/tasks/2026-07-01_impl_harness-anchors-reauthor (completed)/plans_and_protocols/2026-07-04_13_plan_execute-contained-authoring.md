# Plan 13 — Execute the contained-authoring run (developer unblocked, 2026-07-04)

Developer answer (checkpoint 12) fixed the infrastructure my protocol-06 finding identified and
authorized proceeding with the **contained** path. Loop broken (e6584a6f). Verified this session:
`containment.py` `--share-net` (network in jail — `claude --version` runs contained, rc 0), AC-12 auth
binds (`~/.claude` present, bound at real path), `claude` binary resolves in-jail (symlink target under
`/usr/local`, bound via `--ro-bind /usr`), `deploy.py` now keeps `requirements_user_needs/` READMEs while
excluding main `personas/`+`user_flows/`.

## Driver choice: compose primitives, NOT `build.py`

`build.py` is unsuitable as-is for two proven reasons:
1. It uses `scrub_env` (HOME→isolated) — the AC-12 protocol (11) states this **defeats the auth binds**;
   only `run_skeleton` was migrated to real-HOME. → I set `child_env = dict(os.environ)` (real HOME).
2. Its harvest is **full-registry** → the AC-11 proof flagged it would sweep ~130 factory
   `requirements_tasks/process/AI_rules/**/requirements.md` into `test_harness_app/`. → I **scope** the
   harvest to persona + scenario globs only.

So I compose `deploy_candidate` + `sync_product_definition` (seed) + `wrap_with_containment` +
`run_with_hung_detection` + **scoped** `sync_product_definition` (harvest) + `shutil.rmtree`, via a
throwaway `/tmp` driver (not under `scripts/`, so `claude-write-script` N/A).

## Steps

1. **Clean-slate** (AC-1): `git rm` the non-conformant harness product-def artifacts —
   `test_harness_app/requirements_user_needs/personas/**`, `.../user_flows/**` (incl. `_build_mode_proof`
   residue + `FLOW_INDEX.md`), `test_harness_app/requirements_tasks/functional/rating_app/requirements.md`.
   (Flows+requirements are re-derived downstream by 068-12.)
2. **Isolated copy**: `/workspaces/private_mood_tracker/playground-authoring-<uuid>` (sibling of
   `flutter_app`, OUTSIDE the repo). `deploy_candidate(HOST, isolated)` → factory machinery + READMEs,
   no main personas. `sync_product_definition(TARGET, isolated, product_globs)` seed (harness is now
   clean-slated → near-empty). Overwrite `isolated/requirements_user_needs/SCENARIO_INDEX.md` with a
   minimal **harness** stub so the child's index edits are harness-scoped, not main's.
3. **Contained child** (`claude -p`, cwd=isolated, real HOME, `CLAUDE_AUTOMATED_MODE` stripped so it does
   NOT enter orchestrator/automated mode): prompt instructs authoring the anchors via `ux-write-persona`
   /`ux-write-scenario`, README_3/README_4-conformant, **status-quo** scenarios, folder-per-scenario,
   update SCENARIO_INDEX. Background + 4:30 heartbeat (run >5 min).
4. **Scoped harvest** into `test_harness_app/`: only
   `requirements_user_needs/personas/*/persona.md`,
   `requirements_user_needs/personas/*/scenarios/*/scenario.md`,
   `requirements_user_needs/SCENARIO_INDEX.md`. Discard isolated (`shutil.rmtree`).
5. **Verify** main tree untouched (`git status requirements_user_needs/` clean — containment makes this
   structurally guaranteed, but assert anyway); review harvested anchors for README_3/4 conformance.
6. **Park at AC-4** (mandatory developer approval) — present the authored personas+scenarios; flag it must
   be a genuine human review.

## Personas / scenarios to author (from goal + REQ-PROC-068 value-conflict)

- **Archivist** (values completeness) vs **Quick-Logger** (values speed); they meet on the single
  rating-entry form (the P-E/P-F/T4 coupling surface).
- Scenarios are **status-quo / pre-app**: how these users rate & journal movies/books *today, without the
  app* (README_4 CRITICAL RULE). Minimal set that anchors the downstream flow/requirement derivation.

## Safety

- Containment binds only `isolated` + `~/.claude`/`~/.ccs` RW → child **cannot** write the main
  `flutter_app` tree (AC-09). Harvest is scoped + one-directional (isolated→test_harness_app). Main
  `requirements_user_needs/` is never a write target. No `git reset` anywhere near `test_harness_app`.
