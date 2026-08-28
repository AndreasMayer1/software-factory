# Protocol 02 — Real-child build-mode proof (AC-4) + residual harvest-leak finding

Task: TASK-PROC-068-19 · Date: 2026-07-08 · Mode: code-bugfix (slim/scripts)
Session: ed35d6af-be83-477a-a5d1-1339cef455f0 (gmail2)

## What this session did

Ran the **real authenticating `claude -p` child through `run_build_mode()`** —
the combined AC-11 ∧ AC-12 proof the original AC-11 verification substituted
away (Protocol 01 left AC-3 and AC-4 open). Result: AC-1 and AC-2 are proven
empirically; **AC-4 is NOT met** because excluding `process/` alone is
necessary-but-not-sufficient — a residual host-factory leak remains. This is a
genuine scope/AC-10 decision → escalated to the developer (pending_feedback).

## AC-1 (build-mode auth) — PROVEN ✓

- First attempt failed rc=1 for an unrelated reason: the invocation passed a
  non-UUID `--session-uuid` (`ac4-buildproof-<epoch>`); `claude` rejects it with
  `Error: Invalid session ID. Must be a valid UUID.` NOT an auth failure. Fixed
  by letting `build.py` generate `uuid4()` (its default).
- Manual contained-command repro with a valid UUID authenticated cleanly:
  `{"type":"result","subtype":"success","is_error":false,"result":"OK",
  "total_cost_usd":0.0996,...}` — the real-path `~/.claude` bind (Defect-1 fix:
  `child_env = dict(os.environ)`, real HOME) resolves. `claude` binary is
  reachable in the jail (nvm bin under `/usr`, ro-bound).
- Full `run_build_mode()` run: child session `1a23bed8-…`, **rc=0**, cost
  **$0.2008**, wrote the artifact, JSONL shows `File created. Stopping.`
  → Defect 1 fixed and AC-12 real-path auth bind verified end-to-end.

## AC-2 (process/ excluded from deploy & harvest) — PROVEN ✓

- `deploy_candidate` deployed the whole factory into the isolated copy; the
  harvest manifest (`harvested_paths`) contains **zero**
  `requirements_tasks/process/**/requirements.md`.
- Post-run `find test_harness_app -path '*requirements_tasks/process*'` = **0**.
  The ~130-file process over-inclusion is gone at the root. Defect 2 fixed for
  the process corpus.

## AC-4 (test_harness_app gained ONLY that artifact) — FAILED ✗ (residual leak)

Baseline `test_harness_app/`: 8889 files, clean git, personas {maya, theo}, 0
process files. After the real run, `git status --porcelain test_harness_app/`
showed **13 net-new files**, not 1:

- `requirements_user_needs/personas/persona-buildproof/persona.md` ← the intended
  proof artifact (correct).
- **12 unintended host-factory files** (byte-identical to host; `diff -q` empty →
  deploy-brought, NOT seeded — absent from `seeded_paths`, present in
  `harvested_paths`):
  - `requirements_tasks/STATUS.md`, `RELEASE_BACKLOG.md`, `RELEASES.md`,
    `package_assignment_rules.md`, `_meta/id_registry.md`
  - `requirements_tasks/_scribble_components/{c_app_bar,c_filled_button,
    c_mood_entry_card,c_navigation_bar,c_plan_list_item,c_review_guide}/metadata.yaml`
  - `requirements_user_needs/_meta/value_tradeoff_summary.md`

Root cause: `deploy.py` excludes `requirements_tasks/{functional,non-functional,
process}` but NOT the top-level `requirements_tasks/` aggregate/generated files,
`_scribble_components/`, `_meta/id_registry.md`, or
`requirements_user_needs/_meta/value_tradeoff_summary.md`. Those host files
survive deploy, match the full-registry harvest globs
(`requirements_tasks/STATUS.md`, `requirements_tasks/_scribble_components/*/metadata.yaml`,
`requirements_tasks/_meta/id_registry.md`, `requirements_user_needs/_meta/value_tradeoff_summary.md`,
…), and — because they are net-new host content (not round-tripped from the
seed) — land in `test_harness_app/`. This violates AC-4's "only that artifact"
and AC-11's "transient deployed factory machinery is absent."

Cleanup: the 12 leaked files + the proof persona were all untracked; removed to
restore `test_harness_app/` to its 8889-file baseline. Temp isolated dirs and
child JSONL removed.

## Why the fix is NOT simply "exclude these too" — AC-10 tension

Unlike `process/` (an authoring-time-only input, safe to drop), several residual
files are **harness-runtime inputs** read by skills that run in the harness:

- `requirements_tasks/_scribble_components/*/metadata.yaml` ← read by the
  `ui-scribble-*` skills (ui-scribble-iterate/auto-review/feedback-classify, …).
- `requirements_tasks/_meta/id_registry.md` ← read by `task-create`,
  `ux-flow-draft`, `task-repair-meta`, … (ID allocation).

So dropping them from deploy would risk **AC-10** (a deployed skill failing for
lack of a file it reads). The two candidate fixes therefore diverge:

- **Option A — widen deploy excludes.** Simple, mirrors the process/ fix, but
  UNSAFE for the runtime-input subset above (AC-10 regression risk); would need a
  per-file audit of which residuals are authoring-time-only.
- **Option B — scope the HARVEST to net-new files** (diff the post-run isolated
  copy against its pre-seed/pre-deploy state; harvest only what the child newly
  authored). Keeps deploy whole (AC-10 safe) and generalizes to ALL residual
  leakage, not just this fileset. This is the approach the original AC-11 proof
  suggested ("harvest only what the derivation itself newly wrote"). It is a
  design change to `build.py`'s harvest step — beyond this task's declared
  Defect-1/Defect-2 charter, and its Out-of-Scope note ("Changing what deploy.py
  copies beyond excluding requirements_tasks/process").

## Status of the six ACs

- AC-1 (auth) ✓ proven · AC-2 (process/ excluded) ✓ proven · AC-5 (tests) ✓
  (Protocol 01, 38/38) · AC-6 (bugfix conventions) — no debug artifacts left.
- AC-3 (AC-10 guard: real skill end-to-end with process/ excluded) — NOT run.
  Deliberately deferred: the residual-leak decision may change deploy/harvest
  behavior, which would invalidate an AC-3 run done now. Run it after the
  decision.
- AC-4 (only that artifact) ✗ — blocked on the Option-A-vs-B decision above.

## Escalation

Written to `automation/pending_feedback/TASK-PROC-068-19/question.md`. The scoped
fix (exclude process/) is landed and proven for AC-1/AC-2, but AC-4 cannot be met
within the declared scope; the sufficient fix is a design choice with AC-10
implications. Not self-authorized — this is a requirements/architecture decision.
