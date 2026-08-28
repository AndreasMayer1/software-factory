# Protocol 01 — Anchor re-authoring: investigation + blocking mechanism question

Task: TASK-PROC-068-11 · session 91be1f5b-25be-4577-a8f4-ae4dfa718184 · account gmail2 · 2026-07-01

## What the task asks

Clean-slate the non-conformant harness product-definition artifacts and **re-author the anchor
layers (personas + scenarios) via the real factory authoring skills** (`ux-write-persona`,
`ux-write-scenario`), README_3/README_4-conformant, targeting the harness tree
(`test_harness_app/requirements_user_needs/`). Hard developer-approval gate before completion.
This is binding under REQ-PROC-068 AC-06 ("product definition authored via the factory skill chain").

## What I found

1. **The two anchor authoring skills are hardwired to the MAIN project tree, not the harness.**
   - `ux-write-persona` CREATE mode: `mkdir -p "requirements_user_needs/personas/[name]/scenarios"`
     (root-relative → resolves to the main mood-tracker tree, not `test_harness_app/`).
   - Both skills read type-def READMEs from the main `requirements_user_needs/` (harmless), but their
     **side effects target the main project**: `generate_id_registry.py --user-needs` (allocates a
     MAIN-project PERSONA-/SCENARIO-ID — the harness should own its own ID space), the SCENARIO_INDEX
     update, and the cascade scans (run against MAIN-project flows/scenarios).
   - Neither skill accepts a target-root / project-root / harness parameter (grep for
     `target.?root|base.?path|harness|cwd|--root|repo.?root|project.?root` → none).

2. **The sanctioned way to run factory skills against the harness is the "Deploy & isolate" invariant**
   (epic requirements §Real-Project Mirror + AC-07/AC-09): the candidate factory is *deployed into the
   harness and run with the harness as cwd*, so root-relative paths resolve under `test_harness_app/`.
   That mechanism is **explicitly out of scope here** — it is TASK-PROC-071-05-05 / the deploy machinery.
   The harness mirror is also currently **incomplete**: no `test_harness_app/CLAUDE.md`, no `doc/`, no
   `.claude/` (so it cannot yet host a cwd-redirected skill run either).

3. **No precedent exists.** The only commit that ever wrote harness product-definition content is the
   non-conformant hand-rolled one (849a39a5, TASK-PROC-068-07). No `ux-*` skill has ever authored into
   `test_harness_app/`. This task is the first attempt, and the skill set does not support it as-is.

4. **The downstream sibling (TASK-PROC-068-12) targets the harness via `layer-derivation-start`**, which
   dispatches middle/lower-layer authoring skills with `target_artifact_paths` from
   `backfill_orchestration.py`. But that path covers scenario→flow→requirement only; the **anchor
   layers (persona, scenario) are FIXED inputs** to that chain, authored *directly* — precisely the step
   with no targeting affordance.

## The blocker

Running `ux-write-persona` / `ux-write-scenario` in this session (cwd = main `flutter_app`) would
write rating-app personas/scenarios into the **real mood-tracker** product definition and mutate its
ID registry, SCENARIO_INDEX, and cascade links — a hard-to-reverse, high-consequence corruption of the
live product the whole factory serves. I will not guess a targeting mechanism that risks that.

The three candidate resolutions each need a developer decision (they differ in cost, scope, and which
"binding" rule they bend):

- **Option A — cwd/deploy redirect (mirror-first).** First complete the harness structural mirror
  (add `test_harness_app/CLAUDE.md`, `doc/`, the README type-defs, `.claude/` as needed — goal step 4 /
  AC-01), then run the two anchor skills against the harness as cwd via an isolated child session so
  their root-relative paths + registry/index resolve under `test_harness_app/`. Cleanest conformance
  with AC-06, but leans on deploy/isolate machinery that this task lists as out of scope (overlaps
  TASK-PROC-071-05-05) — confirm whether standing up the *minimal* cwd-redirect here is acceptable or
  must wait for that task.
- **Option B — parametrize the skills.** Add an explicit target-root argument to `ux-write-persona` /
  `ux-write-scenario` (via `claude-modify-skill`) so they can author into `test_harness_app/…` and use a
  harness-local ID space / SCENARIO_INDEX / cascade scope. A skill change — arguably scope creep for a
  product-definition authoring task; confirm before I modify governed skills.
- **Option C — author to harness paths by hand following README_3/README_4.** Fastest, but **violates
  AC-06** ("via the factory skill chain") — the exact failure mode this remediation chain exists to
  correct. Not recommended; listed only for completeness.

Clean-slate (AC-1, goal step 1) is safe and unconditional but I have **not** executed it yet — I am
parking *before* mutating the tree so a deleted-but-not-reauthored state is not left half-done across
the wait. On resume with a chosen option I will: clean-slate → author → park again for the mandatory
developer approval gate (AC-4).

## Decision needed from developer

Pick A, B, or C (or specify another sanctioned mechanism) for pointing the anchor authoring skills at
`test_harness_app/`. That unblocks authoring; the hard approval gate (AC-4) is a separate, later park.
