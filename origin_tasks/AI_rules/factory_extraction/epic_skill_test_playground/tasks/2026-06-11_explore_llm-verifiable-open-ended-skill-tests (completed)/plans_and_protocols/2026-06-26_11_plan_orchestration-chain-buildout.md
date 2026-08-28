# Plan — Build-out as a self-propagating orchestration-task chain

**Date:** 2026-06-26 · **Task:** TASK-PROC-068-01 · Developer directive this session.

## Principle (developer directive)

The build order lives **entirely in the task graph** — encoded as `after:` edges between real
tasks. No side files (`task_ordering_priority_override.txt`, analysis docs) carry ordering; those
hold rationale only. Where a downstream task cannot yet be wired because it does not exist
(its shape depends on a predecessor's outcome), an **orchestration task creates it** at the right
moment — and **creates the next orchestration task for the following gap**, so the pattern
self-propagates and never leaves a dangling edge to a non-existent task.

## The gap-filler (orchestration-task) pattern

Each "gap" in the build-out gets one orchestration task:
- `orchestration_task: true` (schema-supported: "coordinates or delegates to sub-tasks rather than
  producing direct deliverables").
- `after: [<the gate task(s) for this gap>]` — so it only runs once the predecessor outcome is known.
- Its `goal.md` instructs the executing session to:
  1. read the predecessor outcome (e.g. the spike's go/no-go, or the maturity verdict),
  2. **create the next batch of work tasks** via `task-derive-from-requ` (AC-backed) / `task-create`,
     wiring their `after:` edges to the now-completed predecessors and to each other,
  3. **create the next orchestration task** gated `after:` this batch's gate,
  4. embody any **conditional / stop-loss branch** (green → build; red → stop + fallback task).

**Why this beats pre-wiring:** edge creation is deferred to the instant the predecessor outcome is
known; stop-loss branching is expressed naturally (a non-existent downstream task is implicitly
cancelled); there is never an edge to a task that does not exist.

**Reuse note:** the schema fields (`orchestration_task`, `discovery_command`) exist. The existing
`scripts/tasks/create_orchestration_task.py` is **release-bound** (REQ-PROC-035) — it is the *model*,
not a reusable tool. The *general* automated version is the ralph loop (REQ-PROC-065-06), not yet
built. So for this chain we **hand-instantiate** the pattern via `task-create` + the goal.md recipe
above. (Pleasing side effect: this chain is itself a real exercise of the perpetuating pattern 065-06
will generalise, and a future capability-test subject for it.)

**Termination:** the gaps are finite and known (spike → tester-maturity → layer-deriv/ralph →
full playground). The final orchestration task creates the last batch and **no** successor
orchestration task; the chain ends.

## Concrete chain

```
Stage 0 (THIS task, 068-01, now)
  ├─ author spike-scoped requirements:
  │     REQ-PROC-073: AC disproof-spike · AC git-history regression-corpus · AC discriminating-maturity gate
  │     REQ-PROC-068: minimal substrate ACs (deploy→run-as-cwd→git-reset on 1 fixture, mirror, cost) + 1 child-session-safety AC (developer sign-off)
  ├─ T-spike            (impl, AC-backed, after: [])            run disproof spike on a KNOWN ideation defect-pair; emit go/no-go + cost/detection
  └─ T-orch1            (orchestration_task, after: [T-spike])  first gap-filler

Stage 1  T-orch1 runs (reads spike outcome)
  GREEN → author the deferred full oracle/substrate requirement slice, then create:
     ├─ T-skeleton      (impl)   walking skeleton: deploy→run→reset→cost
     ├─ T-corpus        (impl)   seed fixtures from ideation git history (~45 labeled pre/post pairs)
     ├─ T-maturity      (verify, after: [T-skeleton, T-corpus])  PASS = catches ≥N labeled ideation defects (measurable gate)
     └─ T-orch2         (orchestration_task, after: [T-maturity])   ← unblocks the PARKED layer-deriv & ralph design tasks
  RED  → document stop-loss; create T-fallback (build layer-deriv/ralph with manual testing); chain ends toward playground

Stage 2  T-orch2 runs (after: T-maturity) — layer-deriv (071-02) & ralph (065-06-08) DESIGN tasks are PARKED in pending_feedback
  ├─ create T-unblock-071-02 (developer-gate task): surface 071-02's parked 10-decision gate + the captured pre-answers
  │     (epic_layer_derivation/.../2026-06-26_02_developer_pre-answers-parked.md) as the draft; developer fills answer.md
  │     → 071-02 resumes & emits its OWN layer-derivation impl/verify/re-capstone chain
  ├─ create T-unblock-065-06-08 (developer-gate task): same for ralph's parked design task
  └─ T-orch3            (orchestration_task, after: [<layer-deriv re-capstone verify>, <ralph verify>])
  Held by creation-time: 071-02/065-06-08 emit their chains only HERE (post-maturity), so the impl/fix tail runs
  against the mature tester WITHOUT injecting after-edges into their emitted chains.

Stage 3  T-orch3 runs
  └─ derive full playground enhancements (071-driven harness-middle generation; ralph-driven autonomous test runs); NO successor orch task → END
```

**Parked-task resumption is itself a task (developer correction, 2026-06-26).** Layer-deriv design
(**071-02**) and ralph design (**065-06-08**) are *already done designing* but **parked in
`pending_feedback`** awaiting the developer's go/no-go. A blocked task resumes **only** when its
`answer.md` is written — a note in `plans_and_protocols/` preserves content but does NOT resume it. So
resumption must be an explicit **task**: T-orch2 creates `T-unblock-*` tasks that surface each parked
gate (with the captured pre-answers as the draft) so the **developer fills `answer.md`** — per the
human-only-writes-answer.md safety rule a session must not fabricate it. Because those unblock tasks are
created only *after* tester-maturity, the layer-deriv/ralph **impl + fix tail is held behind the mature
tester by when they are unblocked** — no after-edge injection needed.

## Cross-cutting principle (from 071-02 pre-answers): resumable, task-based control — not script-steering

The developer's 071-02 answers raise a danger that applies to this whole build-out: a long-running
**script** holding steering control is unsafe under usage limits — a session can be killed mid-run,
unable to stop the script or write a status report, and must resume from where it left off. The
mitigation is the same architecture this plan already uses: put control in **resumable tasks/sessions**
(recoverable via the task lifecycle), not in a Python driver that steers sessions. Both the layer-deriv
backfill keep-alive and this orchestration chain should lean on the existing perpetuating substrate
(**TASK-PROC-065-06-01**) rather than reinvent steering — the developer named it explicitly for
layer-derivation's keep-alive, and it is the same `orchestration_task`/after-self-chain substrate this
plan rides.

## This session's scope (Stage 0 only)

1. Author the spike-scoped REQ-PROC-073 + REQ-PROC-068 ACs (archetype-S sign-off with developer).
2. Derive **T-spike** (from the disproof-spike AC) and **T-orch1** (orchestration task).
3. Everything past Stage 0 is created by the orchestration chain at runtime — nothing else is
   pre-derived.

## Decisions (2026-06-26, developer) — refine the spike + maturity gate

- **Spike seed defect = `fix(TASK-PROC-004-04-08): make serve mode non-blocking at the gate (AC-07)`.**
  Chosen as the easiest, clearest quality flaw — a blocking-at-the-gate behavioural bug, obvious to
  identify. Right choice for a disproof spike: if the tester can't catch the *clearest* flaw cheaper
  than the manual review that originally found it, the premise is dead and we learned it for almost nothing.

- **Maturity gate is NOT a fixed N.** Replace "catches ≥N" with a **difficulty-ordered, developer-gated
  batch walk**:
  1. Rank the git-history defect corpus by *expected-LLM-detection difficulty* (easy → hard).
  2. Present defects to the developer in **batches of 3, easiest-first**; show the batch content.
  3. Developer **approves** each batch the tester must catch.
  4. Developer **terminates** the walk when the next batch is too hard to fairly expect an LLM judge to
     detect. The set caught up to that stop point = the tester's **demonstrated discriminating scope**;
     verdicts beyond it stay `advisory`.
  Rationale: some defects are genuinely beyond LLM-judge detection, so an arbitrary N would over- or
  under-claim. The developer walking up the difficulty curve and calling the ceiling is the honest
  calibration, and it matches the human_time_saved lens (stop as soon as marginal defects stop being
  worth catching). Consequence: **T-maturity is an interactive task** (developer present), itself a
  batch-gated loop — the same batch-and-gate shape as the orchestration chain and ideation's gates.

---

## Continuation (2026-07-01) — Anchor-conformance remediation, full-factory deploy, and a machine-resolution channel

**Trigger:** TASK-PROC-068-11 (`harness-anchors-reauthor`) parked in `pending_feedback` on a blocker: the
anchor authoring skills (`ux-write-persona` / `ux-write-scenario`) are hardwired to the **main**
`requirements_user_needs/` tree and cannot target `test_harness_app/`. Investigating the blocker (with the
developer, this session) surfaced a deeper, file-verified picture than the blocker itself stated. This
section records it and the resulting task sequence. **No tasks have been created yet** — see the open
decision D1 at the end; creation is blocked on it.

### Verified findings (read from files — not assumed)

1. **A deploy + cwd-redirect mechanism already exists** (`scripts/playground/`): `deploy.py`,
   `launch_adapter.py` (child session with `cwd=harness`), `containment.py` (bwrap/unshare jail),
   `run_skeleton.py` (deploy → run → **git-reset**). Built by TASK-PROC-068-04, used by run-captest /
   ralph. The blocker's claim that this is "only TASK-PROC-071-05-05 / out of scope" was **wrong** —
   071-05-05 is the layer-derivation *content-gate fix*, unrelated to deploy.

2. **But `deploy.py` copies ONLY `.claude/skills/`** — not `scripts/`, `doc/`, `CLAUDE.md`, or the
   README type-defs. The harness has none of those (verified: `CLAUDE.md`, `doc/`, `.claude/` all absent).

3. **Root cause the skills-only deploy cannot host authoring skills:** the skills shell out to
   `scripts/…` helpers that anchor on their own file location, not cwd and not a parameter. Concretely
   `generate_id_registry.py` computes `project_root = script_dir.parent.parent` (line 853). So:
   - **cwd=harness does not redirect it** (path derives from where the script *lives*), and
   - **a skill-level target-root param cannot redirect it** either (the side effect is inside the
     transitively-called script).
   Combined with `containment.py` (AC-09) this is a hard contradiction: a *contained* child is correctly
   blocked from reaching the host `scripts/`, and doesn't have them locally → **any script-calling skill
   breaks inside the harness.** This is exactly why the anchor authoring cannot run today.

4. **AC-07 / AC-09 of REQ-PROC-068 are NOT false passes** (corrected mid-analysis):
   - AC-09 (EGP **S / HIGH**, containment) is genuinely met — evidenced by
     `scripts/tests/test_playground_containment.py::test_real_jail_blocks_host_tree_access`. It asserts
     *security* (child cannot escape), which holds.
   - AC-07 (EGP **F / MEDIUM**) asserts the deploy→run→**reset cycle** returns the harness to a clean
     state — its EGP referent is the clean-state cycle, which works.
   - **Neither AC mandates copying the *full* factory.** 068-04 legitimately deployed a skills-only
     snapshot. So the full-factory copy is **new scope, not unchecked coverage of AC-07/AC-09.**

5. **The full-factory copy IS grounded — in REQ-PROC-066 (factory extraction), not REQ-PROC-068:**
   - **AC-04** — "every factory runtime artifact carries a factory / project / entangled classification"
     → this *is* the per-file copy manifest (Track A / T-A).
   - **AC-02** — "obtain the factory and its updates … requiring no manual file-by-file copying" → this
     *is* the full-factory deploy mechanism (T-B). The extraction synthesis
     (`…/tasks/2026-05-28_explore_software-factory-extraction (completed)/…/2026-06-28_05_synthesis_extraction-plan.md`)
     §1c already scopes the `scripts/` per-file classification as "~1 task," and §2 states the playground
     deploy *is* the consumer install mechanism dogfooded. REQ-PROC-066 is `status: defined`, **0/6 ACs
     covered, only explorations done** (no impl decomposition yet).

6. **The machine-resolution channel is new scope in REQ-PROC-041-04.** Its AC-01–AC-09 all describe the
   **human** `answer.md` flow (AC-03 developer creates `answer.md`; AC-05 resume with answer content;
   AC-06 merge to `feedback-checkpoint`). `answer.md` itself carries a hard human-only guard
   ("AUTOMATED SESSIONS: Do NOT write to this file"). So a task cannot write `answer.md`. This *extends*
   the pattern already documented above (lines 73–81: "parked-task resumption is itself a task" that
   surfaces the gate for the **developer**). The developer's decision this session:

   > **`resolution.md` (a machine channel, separate from human `answer.md`) is legitimate ONLY when a
   > task is blocked needing a mechanism that does not yet exist and another task implements it.** Not for
   > human-judgment questions; not for premise changes generally. `answer.md` stays human-only.

   TASK-PROC-068-11 fits exactly: it needs the harness-targeting deploy → T-B builds it → the resolution
   says "the mechanism you were blocked on now exists," never "the human picked an option."

### Proposed task sequence (two independent tracks joining at the bridge)

Following this plan's principle: **order lives in the `after:` graph.** The
`task_ordering_priority_override.txt` entries the developer asked for are **visibility/priority only** —
its own header states it "DOES NOT ENFORCE AN EXECUTION ORDER"; it just surfaces these unpackaged process
tasks in `next_tasks.py`. No contradiction with the graph-owns-order rule.

**Track A — full-factory deploy (grounds in REQ-PROC-066; home pending D1):**
- **T-A `author-factory-copy-manifest`** — `.factory/registry/factory_copy_manifest.yaml` from the
  extraction boundary map §1a/1b/1c: factory scaffolding to copy (`.claude/`, `scripts/` **transitive
  closure**, general `doc/`, CLAUDE.md constitution-half, `.factory/`) vs project-only excludes; `scripts/`
  classified per-file. → REQ-PROC-066 **AC-04**. `after: []`.
- **T-B `extend-harness-deploy-full-factory`** — `deploy.py` (+ reset/launch) copies the manifest's
  closure, not just `.claude/skills/`; proves a *contained* child runs a script-calling skill
  (`generate_id_registry.py`) end-to-end. → REQ-PROC-066 **AC-02**. **Safety-relevant** (pairs with
  `containment.py`). `after: [T-A]`.

**Track R — machine-resolution channel (grounds in REQ-PROC-041-04):**
- **T-R1 `requ-machine-resolution-channel`** (`requ-explore`) — add ACs to REQ-PROC-041-04 for the
  `resolution.md` channel + the safety discriminator above; `answer.md` stays human-only. `after: []`.
- **T-R2 `impl-machine-resolution-channel`** — orchestrator detects `resolution.md` → resumes with it as
  prompt → archives; guard blocks any task from writing `answer.md`; tests. → REQ-PROC-041-04 new ACs.
  `after: [T-R1]`.

**Track C — reuse for the middle layer:**
- **T-C `layer-derivation-reuse-of-deploy`** (`claude-modify-skill`) — `layer-derivation-start` runs its
  unit skills under the deployed harness so 068-12 consumes the same mechanism. `after: [T-B]`.
  (Grounding requirement TBD — D3.)

**Bridge — unpark 068-11:**
- **T-D `resolve-068-11-targeting`** — writes `resolution.md` for 068-11 ("mechanism now exists at
  `scripts/playground/…`; author anchors via the deployed harness"), with provenance (T-B done). →
  068-11 resumes. `after: [T-B, T-R2]`.

**Rewire of existing tasks:**
- **TASK-PROC-068-11**: `after: [] → [T-B]` (its real prerequisite; T-D unparks it via the new channel).
- **TASK-PROC-068-12**: `after: [071-05-05, 068-11] → [071-05-05, 068-11, T-C]`.
- **TASK-PROC-068-13**, **TASK-PROC-068-03**: unchanged (already re-point to the frontier).

**Graph:**
```
T-A → T-B → T-C ┐
                ├→ 068-12 (also after 071-05-05, 068-11) → 068-13 → 068-03
T-R1 → T-R2 ────┤
T-B, T-R2 → T-D → [068-11 resumes] → feeds 068-12
```

### Open decisions (do NOT assume — developer input required)

- **D1 (blocks creation): requirement home for T-A / T-B.** The honest grounding is REQ-PROC-066
  AC-04 / AC-02, but REQ-PROC-066 is undecomposed (0/6, explorations only), so a standalone impl task
  there trips `task-create`'s redirect to `task-derive-from-requ` (holistic decomposition of the *entire*
  extraction — far larger than this gap). Options: **(a)** narrow standalone tasks on REQ-PROC-066 with
  `--standalone-override`; **(b)** add a playground-scoped "deploy-completeness" AC to REQ-PROC-068 and
  ground there, treating it as a precursor realization of 066 AC-02/AC-04; **(c)** run
  `task-derive-from-requ` on REQ-PROC-066 (heavy, but the "proper" decomposition). Recommendation: **(b)**
  keeps the work playground-scoped and unblocked while honestly cross-referencing 066; but this is the
  developer's call.
- **D2:** whether T-B is full or partial coverage of AC-02 / AC-04 (extraction-time standalone repo is
  the full realization; the harness deploy is the dogfooded subset).
- **D3:** grounding requirement for T-C (REQ-PROC-068 vs REQ-PROC-071).
- **D4 (flag only):** TASK-PROC-071-05-05 is itself `in_progress` and parked in `pending_feedback` on its
  own question — it independently gates 068-12. Out of scope for this sequence; noted so the chain isn't
  assumed clear.

**State:** plan persisted; task creation paused pending D1.

### Revision (2026-07-01, developer) — decouple from REQ-PROC-066; NO external factory manifest

Developer direction refines Track A and **resolves D1**:

- **Scope the full-factory-deploy entirely under REQ-PROC-068 (playground), independent of REQ-PROC-066.**
  REQ-PROC-066 is far larger than extraction — it *builds* the standalone factory project (separate repo,
  distribution, self-hosting the loops); extraction is the easy part. The deploy mechanism is a small
  precursor. REQ-PROC-066 can **consume** this implementation later as a realization of its AC-02, but must
  not gate it. My earlier "ground T-A/T-B in REQ-PROC-066 AC-04/AC-02" is withdrawn.

- **T-A (governed copy manifest) is DROPPED.** Enumerating "what is the factory" in an artifact *outside*
  the factory creates an authoritative definition in the wrong place — guaranteed to drift once the factory
  becomes its own project. **What the factory is must be defined only by the factory project itself**
  ("everything it provides"), once that project exists. No governed manifest.

- **Requirement = one intent-level AC on REQ-PROC-068**, no file/artifact enumeration:
  > *A deploy places the **whole** factory into the harness such that a **contained** child session can
  > invoke any factory skill end-to-end (no reach-back to the host tree).*
  Says "the whole factory," never "these files" — defers *what* "whole" means to the factory itself.
  Add as a new AC via a minimal `requ-explore`, **or** frame T-B as a remediation of AC-07 read as
  whole-factory (bugfix type → redirect-exempt).

- **Implementation (T-B), pre-extraction:** factory + app still share one repo, so the deploy needs a
  boundary **at code level only** — a coarse **exclude-based** rule: copy everything EXCEPT the app
  (`lib/`, `test/`, `integration_test/`, functional/non-functional requirements, `requirements_user_needs/`,
  the app `scripts/`/`doc/` subset — extraction-synthesis §1b as a **non-authoritative** reference, not a
  spec). Exclude-based so factory growth is copied by default; over-inclusion is safe (harness is isolated +
  git-reset; can't breach AC-09, which is about reaching *out*). Mark `// TEMPORARY:`.

- **Future post-extraction switchover task** (REQ-PROC-066 scope, created later): replace the temp
  exclude-rule with "copy whatever the extracted factory project provides." Noted, not created now.

- **D1 RESOLVED:** home = REQ-PROC-068; no REQ-PROC-066 entanglement; no holistic-decomposition redirect
  (new AC + `--standalone-override`, or bugfix-on-AC-07). **T-A removed; T-B `after: []`.**

**Updated Track A:**
- ~~T-A author-factory-copy-manifest~~ — **dropped** (no external factory manifest).
- **T-B `extend-harness-deploy-full-factory`** → REQ-PROC-068 (new intent-level whole-factory-deploy AC).
  `after: []`. Coarse TEMPORARY exclude-rule + a contained-child end-to-end functional proof
  (script-calling skill runs inside the jail). Tracks R/C and the bridge T-D are unchanged.

#### Pre-extraction exclude set — T-B impl guidance (developer-approved 2026-07-01; **NON-exhaustive**)

Developer supplied non-factory top-level entries; explicitly "not a complete list." T-B finalizes the
rule in code as `// TEMPORARY:`; over-inclusion is safe (harness isolated + git-reset). Resolved against
the actual top-level tree (`LC_ALL=C` sort):

- **Tooling/dotdirs:** `.codegraph`, `.dart_tool`, `.idea`, `.roo_archive`, `.vscode`, `.VSCodeCounter`
- **Platform/build/app assets:** `android`, `assets`, `build`, `coverage`, `doc-temp`, `web`, `windows`,
  `Temp` (the "temp folder")
- **Alphabetical range `doc-temp`→`packages` (in-between):** `figma`, `integration_test`, `ios`, `lib`,
  `linux`, `macos`. (Endpoint `packages` inclusivity: developer to confirm — treated as excluded pending.)
- **"test folders":** `test/`, `test_driver/`, `test_hive/`
- **Implicitly non-factory (dev: "not a complete list") for T-B to also exclude:** `.git`, `.github`,
  `.githooks`, `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `.venv`, `dev-analytics`, `releases`,
  `requirements_market_research`, `requirements_general_overview`.

⚠ **Two risks T-B must handle:**
1. **`test_harness_app/` must NOT be treated as factory content** — it is the deploy *target*, not a thing
   to copy. A naive `test*` glob would sweep it in with the "test folders"; exclude it explicitly.
2. **Top-level exclusion is insufficient for the entangled trees.** `requirements_tasks/` (factory
   `process/AI_rules/**` vs app `functional/`+`non-functional/`), `requirements_user_needs/` (app), and
   `scripts/`/`doc/` (mixed factory+app) need **sub-folder** boundaries. Deferred to T-B impl;
   extraction-synthesis §1a/§1b is the non-authoritative reference. Err toward copying (over-inclusion safe).

The requirement AC stays intent-level ("the **whole** factory"); this list lives only in T-B's temp code,
to be replaced post-extraction by "copy whatever the extracted factory project provides."

### Standing rule (developer, 2026-07-01) — recursive override registration

**Every task that creates other tasks MUST add the tasks it creates to
`.claude/task_ordering_priority_override.txt`, and must carry this same instruction into each created
task's `goal.md` — so the rule propagates recursively down the chain.** Rationale: the override is the
active queue while this remediation runs; a created-but-unregistered task would be invisible to
`next_tasks.py` and silently stall the chain. Applied to the tasks created this session (068-14,
041-04-05, 068-15 — all registered) and baked into 068-15's step 7 for the impl tasks it will create.

### Tasks created this session (2026-07-01)

- **TASK-PROC-068-14** `explore_whole-factory-deploy-ac` (REQ-PROC-068, `after: []`) — Track A root.
- **TASK-PROC-041-04-05** `explore_machine-resolution-channel` (REQ-PROC-041-04, `after: []`) — Track R root.
- **TASK-PROC-068-15** `impl_orchestrate-deploy-and-resolution-chain` (orchestration_task,
  `after: [041-04-05, 068-14]`) — fans out T-B/T-R2/T-C/T-D, rewires 068-11/068-12, registers them.

All three registered in the override. `next_tasks.py` now leads with the two unblocked roots (068-14,
041-04-05). The impl tasks (T-B/T-R2/T-C/T-D) and the 068-11/068-12 rewiring are created by 068-15 once the
two ACs exist (grounding rule: no ungrounded impl tasks).
