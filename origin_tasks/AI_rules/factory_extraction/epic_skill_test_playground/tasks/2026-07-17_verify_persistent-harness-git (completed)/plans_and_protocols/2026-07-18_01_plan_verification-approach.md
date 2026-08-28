# Plan: End-to-end verification of persistent harness git (TASK-PROC-068-34)

**Session**: 69804c91-9f5e-4c63-af04-e7983ca11aeb (automated, gmail2)
**Mode**: inline (main session Bash — no subagents; real `claude -p` child runs are the
work item itself, nothing to delegate)

## What is being verified

AC-20 (persistent git: restore/persist/compaction), AC-21 (encapsulation), AC-11
(harness retains its own factory-runtime provenance) — all against REAL
`run_build_mode()` behaviour, per the Oracle-Independence Declaration in goal.md.
Baseline confirmed: `test_harness_app/` currently has NO `.playground_harness_git/`
bundle yet (mechanism never exercised against the real harness since TASK-PROC-068-31/32/33
landed) and NO `.factory/ideation/` content — this is genuinely the first real proof run.

## Key mechanics established by reading the implementation (workspace.py / build.py)

- `run_build_mode` only harvests+persists on the **COMPLETE** outcome, which requires
  `--acceptance-oracle chainstate` + a `.layerderiv/chain_state.json` that reaches
  `complete: true`. There is no way to reach harvest without this apparatus.
- Cheapest legitimate way to reach `complete: true`: a **single degenerate span unit**
  whose anchors are ALREADY-approved persona+scenario (no real authoring — just
  `enrich` -> naturalness report -> commit -> `complete ... done`). This is the exact
  pattern TASK-PROC-068-14's run used for its first unit ("persona-scenario-fixed").
  Existing approved anchors in `test_harness_app`: PERSONA-001 (Theo), PERSONA-002
  (Maya), scenario SCEN-002-01 (Maya/quick_rating_after_movie).
- `_collect_referenced_commits` scans harvested files + every `requirements_tasks/**/goal.md`
  in the copy for `@ <hex4-40>` or `commit: <hex4-40>` (resolved against the WORKSPACE's
  own git — foreign/host hashes are dropped, this is the harness-vs-factory filter).
  Whatever commit those patterns name, IF it resolves in the workspace repo, is
  preserved; everything else above the newest preserved point is squashed
  (`_MIN_SQUASHABLE_TAIL = 2`, so need >=2 commits in the squashable tail to prove
  compaction actually fires, not just no-ops).
- AC-11's "ideation index and ledger backing a derived decision, retained as project
  data" is satisfied through the SAME git-persistence mechanism (AC-20), not through
  the harvest file-copy allowlist (`_PRODUCT_DEFINITION_CATEGORIES` does NOT include
  an ideation category — ideation content is "transient machinery" from harvest's POV,
  but it survives because it's *committed history* inside the bundle). So: run a real,
  minimal `ideation-start` (embedded, Quick effort) for a genuinely trivial open
  micro-decision inside the child session, commit its output, and reference that
  commit's sha from a harvested artifact — this single action produces material for
  BOTH AC-20 (a referenced, preserved commit) and AC-11 (real ideation index+ledger
  retained via the persisted bundle) at once, without touching the
  materialization/layer-derivation apparatus that TASK-PROC-068-14 already found
  contamination-prone (068-26) — that full chain is out of this task's scope; a
  degenerate certification + a standalone ideation-start call is the minimal real
  substitute that stays inside scope while still being genuine (not fabricated)
  behaviour.

## Run design

**Run 1** (first-ever maintenance run against the real harness — no bundle exists,
`_prepare_workspace` will `init_workspace_git`):
1. Plan+run the single-unit degenerate chain (fixed_layers=[persona, scenario],
   anchor on PERSONA-001/PERSONA-002 + SCEN-002-01) to `complete: true`. ~1 commit.
2. Invoke `ideation-start` (Skill, embedded mode, Quick effort) inside the copy for a
   genuinely trivial decision ("pick a one-line primary-frustration phrasing for a new
   tiny proof persona between two options"), using a throwaway task folder under
   `requirements_tasks/functional/_playground_proof/tasks/...` (that subtree is
   excluded from deploy, so it's guaranteed empty in the copy — no collision). Commit
   its output (index.yaml + ledger). Capture the commit sha (`git rev-parse HEAD`).
3. Author ONE new tiny real persona file (`requirements_user_needs/personas/persona-gitproof/persona.md`,
   real "user-needs" harvest category) whose body includes a line
   `<!-- decided_by: IDEATION-001 @ <sha-from-step-2> -->`. Commit it (commit "R").
4. Two more trivial commits after R (touch/edit the same file) — pure noise, meant to
   be squashed.
5. Exit. Gate: chainstate oracle sees complete:true -> COMPLETE -> harvest (net-new:
   the proof persona) -> `_collect_referenced_commits` finds the step-2 sha in the
   harvested persona body -> `compact_workspace_git` preserves it, squashes the R+2
   noise tail (tail_len=3 >= 2) -> `export_workspace_git_bundle` persists to
   `test_harness_app/.playground_harness_git/harness.bundle`.
6. Orchestrator (me) independently verifies via raw `git` against a temp clone of the
   exported bundle: the step-2 ideation commit is present with the SAME sha I captured
   in step 2; `git show <sha>:...` recovers the real ideation index/ledger content;
   history above it collapsed to one squash commit (proves compaction fired for real,
   not a no-op).

**Run 2** (`_prepare_workspace` now restores-on-deploy from the persisted bundle):
1. New degenerate-or-trivial chain to reach complete:true again (cheap, no new
   reference needed).
2. A couple more noise commits.
3. Harvest/compact/export again.
4. Orchestrator verifies: run 1's ideation commit sha is STILL present, UNCHANGED,
   reachable from the new tip (stability across >=2 runs — the actual AC-20 claim,
   not just "restore worked once"); run 1's own persisted tip (the run-1 squash
   commit) is present unchanged as an ancestor (prior-run immutability); run 2's own
   junk got squashed too.

**AC-11 check** (after both runs): `test_harness_app/` file tree carries zero
transient factory machinery (no `.claude/`, `scripts/`, `.factory/registry/` —
these were never harvest-eligible categories to begin with) while
`test_harness_app/.playground_harness_git/harness.bundle` — inspected via
`git show <bundle-ref>:.factory/ideation/index.yaml` — carries the real ideation
index+ledger as committed project data; `requirements_user_needs/product_materialization/`
(if untouched by these runs) is confirmed NOT clobbered (still absent/unchanged,
since this task doesn't touch it — a `git status`/absence check before and after
suffices, given deploy.py's exclude for that path was TASK-PROC-068-33's whole job).

**AC-21 check** (static, no run needed): grep all non-`scripts/playground/` factory
code (skills, other scripts, quality gates, orchestration configs) for
`test_harness_app`-specific special-casing beyond ordinary path mentions (docs,
examples). Confirm none.

## Cost/risk controls

- `--max-budget-usd 2.0` per run (script default) — hard cap, not a target; precedent
  real runs in this exact epic cost $0.10-$0.63 for comparable-sized work.
- Both runs target the REAL `test_harness_app/` (required — the bundle's storage
  convention is inside the harness itself, `workspace.py:harness_git_bundle_path`,
  "with the harness in the container project, never an OS temp dir" — there is no
  throwaway-target option for this specific mechanism, unlike the AC-4 precedent
  which could use /tmp). This is an intentional, durable, in-scope side effect of the
  feature under test (AC-11 explicitly wants the harness to retain this permanently).
  If anything goes wrong (contamination, escalation-worthy blocker), stop and write
  pending_feedback rather than attempting cleanup/rollback of a durable git-history
  mechanism by hand.
- Not attempting the full materialization/layer-derivation multi-unit chain
  (TASK-PROC-068-14's territory, already flagged contamination-prone at 068-26) —
  out of this task's scope; the degenerate-cert + standalone-ideation substitute
  above is judged sufficient to exercise the real mechanism faithfully.

## Verification (not double-work — this file IS the plan; results logged in the
02_protocol file as runs execute)
