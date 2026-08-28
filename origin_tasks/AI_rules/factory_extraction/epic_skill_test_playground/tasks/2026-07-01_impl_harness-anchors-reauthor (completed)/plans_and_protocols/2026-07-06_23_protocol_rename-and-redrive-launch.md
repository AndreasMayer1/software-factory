# Protocol 23 — Developer answer A: rename personas, then launch the contained re-derivation

Agent: main session (automated), session ec060365-1ed5-4d49-98ce-cce64740eaf8, account web.

## Developer answer (checkpoint 22)

**A)** Run the contained re-derivation now, automated/unobserved. Plus a new standing directive:
persona folders must be named after the persona's real human name (snake_case), not the
role/archetype label — rename `personas/archivist/` → `personas/theo/` and
`personas/quick_logger/` → `personas/maya/`, updating cross-references. Applies going forward.

## Work done this session

1. **Rename** (mechanical, done directly — not delegated to the contained child):
   - `git mv personas/archivist → personas/theo`, `git mv personas/quick_logger → personas/maya`.
   - `SCENARIO_INDEX.md`: `persona_folder: archivist/quick_logger` → `theo/maya`.
   - Regenerated `test_harness_app/requirements_user_needs/_meta/id_registry.md` via
     `generate_id_registry.py --user-needs --root test_harness_app` (generated file, per CLAUDE.md
     never hand-edited).
   - Checked for other references: only historical protocol/checkpoint files under this task's own
     `plans_and_protocols/` mention the old names — left untouched (audit trail, not live content).
     `as_is_data_flow.md` uses "archivist"/"quick_logger" as common nouns describing behavior
     patterns, not path literals — no change needed there.
   - Re-validated `SCENARIO_INDEX.md` against its schema: PASS.

2. **Mechanism choice for the depth re-derivation (checkpoint-18's still-owed substance)**: composed
   the playground primitives directly via a throwaway `/tmp/harness_redrive_driver.py` (not under
   `scripts/`, `claude-write-script` N/A — same precedent as protocol 13's driver), **not**
   `scripts/playground/build.py`'s own CLI. Reason: protocol 16 already found and documented that
   `build.py`'s `main()` calls `containment.scrub_env()` for the child's env, which redirects `HOME`
   into the isolated copy and breaks the AC-12 auth binds (`~/.claude`/`~/.ccs` are bind-mounted at
   their REAL absolute paths; redirecting `HOME` makes the `claude` CLI look for config under the
   isolated dir instead, where it doesn't exist). The driver instead uses `child_env =
   dict(os.environ)` (real HOME), exactly matching `run_skeleton.py`'s own (correct) approach and
   protocols 13/16's proven working pattern. Everything else mirrors `build.py`'s `run_build_mode`:
   deploy the whole factory into a fresh `tempfile.mkdtemp()` isolated copy, seed it with
   `test_harness_app`'s current registry-classified product-definition state, run the contained
   `claude -p` child via `wrap_with_containment` + `run_with_hung_detection`, harvest the same globs
   back into `test_harness_app/` (merge, not overwrite-discard), then `shutil.rmtree` the isolated copy.

3. **Delegated-LLM-work mechanism (REQ-PROC-041-06) — considered, not used.** Read `delegation.py`,
   `pool_capacity.py`, and the implementing plan in detail. That mechanism is for a launching session
   that **registers a descriptor and then exits** while an out-of-band worker keeps running — its own
   plan/code shows the launching session's pool lease is released unconditionally by `held_slot`'s
   `finally` the moment the launching session's process exits (`_reap_and_count`/`live_count` are
   lease-file-only, with no descriptor-awareness), so reusing my already-held lease for the worker and
   then exiting would open a real (if TTL-bounded) capacity-accounting gap — not something to
   hand-roll against a tier-A pool semaphore without dedicated review. Since I can stay **attentive**
   for this run instead (background Bash + no exit, per the plain background-tool-call pattern) rather
   than detaching and exiting, the exact incident pattern 041-06 was built for (parent exits, worker
   orphaned, false-success re-run) does not apply here — I never exit while the child runs. The
   `after:` gate on `TASK-PROC-041-06-05` is satisfied regardless (harmless), but this task does not
   actually invoke that machinery.

4. **No heartbeat loop.** Per `claude-automated-mode`'s Responsibility Boundary, this session must
   never call `ScheduleWakeup` (that's the orchestrator's job, not the session's) — so the
   CLAUDE.md background-agent-cache-protection heartbeat pattern (which is built on `ScheduleWakeup`)
   is skipped here. The driver runs via a background Bash call; its completion will surface as a
   normal tool-result notification.

## Prompt given to the contained child

`/tmp/harness_redrive_prompt.txt` (not persisted in-repo — throwaway, like protocol 13's driver).
Summary: read `README_3`/`README_4` (which now carry the Driver–Context spine, TASK-PROC-010-17,
commit `5cb7e7f2`); for each of Theo/Maya + their one scenario, invoke `ux-write-persona`/
`ux-write-scenario` (real skills, not freehand) to deepen R0 (Driver & Lens + swap-test), R1
(beyond-the-moment), R2 (social field), T (trajectory), composite-archetype governor, and the
persona/scenario boundary — while preserving IDs, names, folder paths (already renamed), the
completeness-vs-speed value conflict, and `review_status: draft` (explicit instruction never to
self-assert `approved` — a prior run already did this once and had to be corrected).

## Expected artifacts (declared, for my own post-run review — not a formal delegation manifest)

- `test_harness_app/requirements_user_needs/personas/theo/persona.md`
- `test_harness_app/requirements_user_needs/personas/theo/scenarios/detailed_entry_after_movie/scenario.md`
- `test_harness_app/requirements_user_needs/personas/maya/persona.md`
- `test_harness_app/requirements_user_needs/personas/maya/scenarios/quick_rating_after_movie/scenario.md`
- `test_harness_app/requirements_user_needs/SCENARIO_INDEX.md` (notes only, folders already correct)

## Next step

Launch `/tmp/harness_redrive_driver.py` via a backgrounded Bash call. On completion: review the
harvested anchors for real Driver–Context-spine depth and `review_status: draft`, then park for the
mandatory AC-4 developer-approval gate via `automation/pending_feedback/TASK-PROC-068-11/` — do not
self-approve, do not `task-complete`. If the child hits a rate/session limit again: per
`claude-automated-mode`, do not retry-loop — leave the task `in_progress`, re-emit the limit line
verbatim, terminate (exit 3), and let the orchestrator resume it.
