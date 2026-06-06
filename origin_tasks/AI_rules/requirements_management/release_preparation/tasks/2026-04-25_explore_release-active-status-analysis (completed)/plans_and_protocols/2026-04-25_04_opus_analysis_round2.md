# Opus Analysis Round 2: Architecture Deep-Review

Date: 2026-04-25
Based on: Plans v1–v3 in this folder + current skill files + next_tasks.py source

---

## 1. Bootstrap-Guard Timing — Best Solution

### The Problem (restated precisely)

`release-begin-impl` creates an explore task with `writes_requirements: true`
so the bootstrap doesn't fire while scope verification is in progress. Phase 6
then calls `create_orchestration_task.py`. If the explore task is still
`in_progress` after Phase 6, two things go wrong:

1. **`next_tasks.py` ranking rule #1**: "Critical-path explores
   (writes_requirements: true) always first." An `in_progress` explore task
   is NOT excluded (only `completed`/`cancelled`/`superseded` are excluded).
   The autorun would try to execute the explore task, not the orchestration
   task.

2. **Case A bootstrap**: blocked while the explore task is pending/in_progress.
   (Minor secondary concern if the orchestration task has `target_release` and
   therefore appears in `next_tasks.py` directly — but rule #1 above is the
   real problem.)

### Option A — Mark explore task completed at end of Phase 6 (proposed earlier)

Phase 6 last step: `task-complete` on the explore task.

**Pro**: Simple, semantically correct (the session IS done after Phase 6).
**Con**: If Phase 6 partially fails (RELEASES.md updated, script crashes),
the explore task is stranded `in_progress`. Autorun is blocked.

Verdict: Viable but requires Phase 6 to be atomic or include a recovery path.

### Option B — Use `after:` chain instead of `writes_requirements:true`

`create_orchestration_task.py` accepts `--after-task TASK-ID` and writes
`after: [TASK-ID]` in the orchestration task's goal.md. The explore task
does NOT need `writes_requirements: true`.

The explore task blocks the orchestration task through the normal dependency
mechanism. When the explore task is completed (at any point), the orchestration
task becomes executable. `next_tasks.py` already enforces this via the blocked-
task filter.

**Pro**: Clean dependency semantics. No reliance on `writes_requirements` guard.
No bootstrap entanglement. Works identically in manual and automated mode.
**Con**: `create_orchestration_task.py` needs one new argument. The explore task
ID must be discoverable when the script runs (it must be passed in or found).

**How to pass the ID**: `release-begin-impl` Phase 6 knows the explore task ID
(it created it). It calls the script with `--after-task TASK-PROC-035-07`.
The script writes `after: [TASK-PROC-035-07]` to the orchestration task's
goal.md. Clean.

### Option C — Set explore task status to completed BEFORE calling the script

Phase 6 sequence:
1. Verify user has approved (Phase 5 gate passed)
2. Mark explore task `completed` (update goal.md status field inline)
3. Activate RELEASES.md
4. Call `create_orchestration_task.py`
5. Print handoff message

If step 3–4 fail, the explore task is already completed but RELEASES.md isn't
activated. User needs to activate manually. Not ideal but recoverable.

### Recommendation: Option B

**Use `after:` chain as the primary mechanism.** It is structurally correct,
has no timing risks, and expresses the actual semantic dependency ("orchestration
task can only run once scope verification is finished").

`writes_requirements: true` on the explore task is still useful for a secondary
purpose: it keeps `next_tasks.py` from surfacing unrelated impl tasks DURING
the interactive `release-begin-impl` session (before Phase 6). Keep it — but
it's no longer load-bearing for the bootstrap guard.

The explore task can be completed at any point during or after Phase 6 without
timing pressure, because the orchestration task's `after:` chain is the real
gate.

**Implementation delta**: `create_orchestration_task.py` gains one optional
argument `--after-task TASK-ID` that appends the ID to the `after:` list in
the generated goal.md. Phase 6 of `release-begin-impl` passes the explore task
ID when calling the script.

---

## 2. Skill Name: release-finalize vs. release-begin-impl-finalize

### Why `release-finalize` is poor

"Finalize" in a release context typically means "cut the release" (tag, publish).
A user seeing `/release-finalize` would reasonably expect it to publish the
release. It is ambiguous.

### Why `release-begin-impl-finalize` is better

It creates an explicit pair:

```
/release-begin-impl           → starts implementation workflow (scope, plan, activate)
/release-begin-impl-finalize  → ends implementation workflow (verify, review, approve)
/release                      → cuts the release (tag, publish)
```

The three-step lifecycle is now self-documenting from skill names alone.

### Alternative options considered

| Name | Problem |
|------|---------|
| `release-finalize` | Sounds like it cuts the release |
| `release-impl-complete` | "complete" is a verb (action) — could mean "run to complete" |
| `release-verify-impl` | Good but loses the symmetry with `release-begin-impl` |
| `release-impl-review` | Accurate but asymmetric |
| `release-begin-impl-finalize` | Verbose but unambiguous and symmetric ✓ |

**Decision: use `release-begin-impl-finalize`.**

---

## 3. What Could Still Go Wrong — Gaps and Risks

### Gap A — `task_creation_plan.md` has no defined schema

Plan v3 describes what the plan *contains* (task name, AC mapping, effort,
layer, after-chains, opus_recommended, architecture notes, test strategy)
but does not define the *format*. `task-create-code` zero-parameter mode must
read this plan — if the format is freeform prose, parsing is unreliable.

**Fix**: Define a concrete schema. Recommendation: YAML frontmatter per entry,
human-readable body for notes.

```markdown
## Planned Tasks

### PKG-0.0.1-core: Transfer Data Model

#### Task: TASK-FUNC-007-12 (planned)
```yaml
name: Implement Transfer Session entity and repository
target_package: PKG-0.0.1-core
covers_acs: [AC-01, AC-02, AC-03]
effort: M
layer: domain
after: []
opus_recommended: false
req_commit: d357041e
```
**Rationale**: AC-01–03 all describe the same entity; splitting would require
shared test fixtures with no benefit.

#### Task: TASK-FUNC-007-13 (planned)
...
```

This format is both human-readable and machine-parseable with a simple Markdown
extractor.

### Gap B — Cross-release UI screen/component dependency is not tracked

If release 0.0.2 adds a UI component to a screen created in release 0.0.1,
no current mechanism captures this dependency. `propose_after.py` only sees
tasks within the current release (and completed tasks from earlier ones). The
Task Creation Planner (Phase 2c) doesn't look at previously completed tasks'
created artifacts.

**Concrete example**: A "Send QR" button is added to the HomeScreen. The
HomeScreen was created by a task in release 0.0.0 (completed). The button task
must run AFTER the screen exists — but since the screen task is completed, the
`after:` chain is irrelevant. What actually matters is that the screen's
Dart file exists and is structured to accept the widget. This is a code
dependency, not a task dependency.

**Assessment**: This is not a scheduling problem (task ordering) but a code
design problem (screen API). The right fix is in the feature's requirements:
explicitly state "this feature adds to the existing HomeScreen — see
FLOW-002 step 4" so the implementing agent knows where to add the widget.

**Action for Planner**: The Task Creation Planner's architecture notes section
should explicitly flag "adds to existing screen" vs. "creates new screen". The
implementing agent's context window then contains that note and reads the
existing screen file directly. No new tooling needed.

### Gap C — `propose_after.py` doesn't understand UI layer semantics

`propose_after.py` is heuristic-based. It detects "same-package" with high
confidence. It does NOT reliably detect:
- Screen → Component dependencies (component needs screen to exist)
- Repository → BLoC → Screen ordering (Clean Architecture layer order)
- Test task → the impl task it tests

The Task Creation Planner partially solves this (it produces explicit `after:`
entries). But when tasks are created without a plan (ad hoc, off-cycle),
`propose_after.py` is the only guard.

**Fix**: Enhance `propose_after.py` with layer-aware rules:
- If a task's covered ACs include presentation-layer items AND another task
  in the same package covers domain-layer items → propose `after: [domain task]`
- The layer is derivable from the AC text (or from the Planner's layer field
  if available)

This is a medium-effort enhancement to `propose_after.py` that makes it
significantly more reliable for Clean Architecture projects.

### Gap D — Phase 2b agent state tracking via `_agent_state.md` is fragile

The current design tracks agent IDs in `_agent_state.md` so the orchestrator
can resume blocked agents. Problems:
1. If the orchestrator session crashes, agent IDs are lost (they're session-
   specific).
2. The grep-based blocker detection is fragile.
3. Resuming an agent by ID requires it to still be alive in the same session.

**Simplification**: Replace agent ID tracking with **output file polling**.
Each remediation agent is given a unique output path (e.g.,
`phase_2b/gap_{n}/output.md`). Instead of resuming by ID, the orchestrator:
1. Knows the expected output paths for all spawned agents.
2. After all agents complete (or session resumes), checks for `question.md`
   files in `phase_2b/` directories.
3. For each answered question file, re-spawns a FRESH agent (not resumes the
   original) with: "The user answered. Read [answered_file], continue from
   [context summary], write output to [output_path]."

This eliminates the need for `_agent_state.md` entirely. The state is the
presence/absence of output files. Robust to session crashes.

### Gap E — No rollback or recovery path if Phase 6 partially fails

If RELEASES.md is updated to `status: active` but `create_orchestration_task.py`
fails (Exit 4), the release is "activated" with no orchestration task. The
autorun will find no `target_release` tasks and the bootstrap will fire — but
the bootstrap check may fail too (depending on what broke the script).

**Fix**: Phase 6 should check BEFORE writing:
1. Run `create_orchestration_task.py --dry-run` (new flag) to verify it would
   succeed.
2. Only if dry-run exits 0: update RELEASES.md, then run without `--dry-run`.
3. If dry-run fails: report the error and stop (don't activate yet).

This makes Phase 6 atomic in practice (the slow part fails fast before any
mutation).

### Gap F — Validation task (Case B) and `release-begin-impl-finalize` overlap

Case B in `claude-automated-mode` creates a validation task that checks:
AC coverage, after-chains, target_package, opus_recommended flags.

`release-begin-impl-finalize` Phases 2–3 check: after-chain reconciliation,
semantic validation.

These partially overlap on after-chains. If the autorun's Case B validation
runs before the user invokes `release-begin-impl-finalize`, the after-chain
check happens twice. Not a correctness problem, but wasteful.

**Clarification needed in the final design**: Case B does structural validation
(automated). `release-begin-impl-finalize` does semantic validation + user
review (interactive). The after-chain check belongs in Case B only. Remove
after-chain reconciliation from `release-begin-impl-finalize` (the user review
skill should not re-run automated checks).

### Gap G — `task-create-code` zero-parameter mode selects the "next package"
but the planner's ordering may differ

`task-create-code` zero-parameter mode calls `next_tasks.py` to find the next
uncovered package. `next_tasks.py` ranks by semver. The Task Creation Planner
may specify a DIFFERENT ordering (e.g., data model before UI, regardless of
semver package order).

If `task-create-code` ignores the Planner's ordering and follows `next_tasks.py`
semver ranking, tasks are created out of the intended dependency order.

**Fix**: The Planner's `task_creation_plan.md` should include a
`## Execution Order` section listing package IDs in the intended order.
`task-create-code` zero-parameter mode, when a plan exists, uses this order
instead of `next_tasks.py` semver ranking.

---

## 4. Simplifications (Without Quality Loss)

### S1 — Remove Phase 4 (Gap Verification) from `release-begin-impl`

Phase 4 runs a verification agent that re-reads all question files and reruns
`generate_status_overview.py`. But:
- The Task Creation Planner (Phase 2c) already produces a complete coverage
  picture.
- The user reviews and approves the plan in Phase 5 (the repurposed user gate).
- A separate verification pass duplicates the planner's output.

**Remove Phase 4 entirely.** The plan IS the verification. If the plan misses
something, `release-begin-impl-finalize` will catch it.

### S2 — Phase 1 should run `generate_status_overview.py` instead of spawning an agent

Phase 1 currently spawns an agent to read 3 files and check scope coverage.
But `generate_status_overview.py --release [version]` already produces a
coverage report. Phase 1 could simply:
1. Run the script.
2. Read the output file.
3. Report to the user.

No agent spawn needed. Saves a session context budget.

**Only spawn Phase 1 agent if** the user is in package mode AND wants a
cross-package consistency check that the script doesn't produce.

### S3 — Remove `_agent_state.md` from Phase 2b (see Gap D above)

Replace with output-file polling. Eliminates a complex state-tracking artifact.

### S4 — Remove Case A from `claude-automated-mode`

Plan v3 already proposes this. Now confirmed: once orchestration tasks are
self-perpetuating (each creates the next), Case A is never needed. Remove.

**Important sequencing**: Don't remove Case A until the new orchestration task
template (3-step self-perpetuating ACs) is deployed. During transition, keep
both paths. After all in-flight tasks drain, remove Case A.

### S5 — Phase 1 package-mode: read `RELEASE_BACKLOG.md` directly, no agent

In package mode, the "scope" is the package list from `RELEASE_BACKLOG.md`.
Phase 1 can read this file in the orchestrator context (it's small) and
verify each package maps to ≥1 requirement without spawning an agent.
Agent only needed if > 5 packages (to avoid context pollution).

---

## 5. Responsibility Clarity — Is Anything Doubled?

### Dependency Definition — Three Overlapping Mechanisms

| Mechanism | When | Scope |
|-----------|------|-------|
| `propose_after.py` | At task creation | Per-task, heuristic |
| Task Creation Planner | Before any task is created | Cross-task, holistic |
| After-Chain Reconciliation (release-begin-impl-finalize Phase 2) | After all tasks created | Cross-task, post-hoc fix |

These are complementary, not duplicated:
- Planner: sets intent holistically before creation
- `propose_after.py`: enforces mechanical rules per task
- Reconciliation: safety net for post-creation gaps

**Clear separation**: Planner is authoritative. `propose_after.py` is a
mechanical cross-check. Reconciliation is a one-time repair pass. No overlap
in timing or authority.

**Enhancement needed**: `propose_after.py` should read `task_creation_plan.md`
if available and auto-accept planned `after:` entries without re-deriving them.
This eliminates false positives and makes the tool's output consistent with
the plan.

### AC Coverage — Three Overlapping Checks

| Check | When | Mechanism |
|-------|------|-----------|
| Phase 1 scope check | start of release-begin-impl | agent or script |
| Phase 2 epic agents | mid-session | agents |
| `check_ac_coverage.py` | Case B validation | automated |

These are NOT redundant:
- Phase 1: package-to-requirement mapping (are all packages addressed?)
- Phase 2: AC-to-feature mapping (are all ACs covered by feature requirements?)
- `check_ac_coverage.py`: task-to-AC mapping (are all ACs covered by impl tasks?)

Each checks a different layer of coverage. Keep all three.

### User Gates — Down to Two (Correct)

Plan v3: scope+plan approval (Phase 5 of `release-begin-impl`) and final review
(`release-begin-impl-finalize` Phase 4). This is the right number.

Old skill had 5+ implicit gates (Phase 2 approval, Phase 2b for each gap,
Phase 5 redundant approval, Phase 6 confirmation). Plan v3 is a major
improvement.

### Task Creation — Single Owner

`task-create-code` is the only skill that creates impl task `goal.md` files.
No other skill should duplicate this. `release-begin-impl` Phase 3 (old) was
the violation. Plan v3 removes it. Clear.

---

## 6. Systematic Dependency Detection

### Current State

`propose_after.py` detects:
- Same-package tasks (reliable)
- Cross-package via `target_release` (partially reliable)
- Does NOT detect: layer ordering, screen-before-component, test-after-impl

### What the Task Creation Planner must explicitly output

The Planner is the place where full cross-task dependency reasoning happens.
It must produce, per task entry:
```yaml
after: [TASK-FUNC-007-05, TASK-FUNC-007-06]
after_rationale: "data model must exist before BLoC can reference entities"
layer: domain   # data | domain | presentation | test | integration
```

The Planner should also include a `## Layer Dependency Rules` section
documenting the ordering for this release:
```
data → domain → presentation → test (unit/widget) → integration
```

And for screen-specific dependencies:
```
Screen tasks → component tasks that add to that screen
```

The Planner identifies this by checking whether a feature's ACs say "add X
to [Screen]" vs. "create [Screen]".

### What `propose_after.py` should do after the plan exists

If `task_creation_plan.md` exists for the active release:
1. Read the plan.
2. For the task being created: find its plan entry.
3. Use the plan's `after:` list directly (no re-derivation needed).
4. Fallback to heuristic only if no plan entry exists.

This makes `propose_after.py` deterministic when a plan exists.

---

## 7. Artifact Quality — What's In, What's Not, What's the Standard

### `task_creation_plan.md` (new artifact — needs schema now)

**In**: Per-task entries (name, ACs, effort, layer, after-chains, rationale),
architecture notes, test strategy, layer ordering declaration, execution order.

**Not in**: Full requirement text (referenced by `req_commit` + path), code
snippets, implementation details.

**Quality standard**:
- Every in-scope package has ≥1 task entry.
- Every task entry has explicit `covers_acs`, `layer`, `effort`.
- Every cross-layer dependency has explicit `after` + `after_rationale`.
- Architecture notes flag at minimum: shared abstractions, screen ownership
  ("creates" vs. "adds to"), and test strategy per feature.
- User-approved before activation.

**Parseable format**: The schema in Gap A above. Each task entry is a level-3
Markdown heading with a YAML block and optional prose rationale.

### Orchestration task `goal.md` (enhanced)

**In**: 3-step self-perpetuating acceptance criteria, `target_release`, `after:`
pointing to the explore task.

**Not in**: Feature-level detail (that's the impl task's responsibility).

**Quality standard**: The 3 ACs must be checkable (did task-create-code run? did
the next orchestration task or finalization task get created? was task-complete
called?).

### Phase question files (`questions/iteration_NN/phaseN/*.md`)

**In**: Concrete findings, open questions numbered, proposed remediation actions.

**Not in**: Long requirement text (reference by path only), code.

**Quality standard**: "## Summary for User" section with ≤3 bullets + numbered
open questions. User should be able to make all decisions without reading any
other file.

Currently only Phase 2 agents have this requirement enforced. **Apply the same
standard to Phase 2c (Planner output) and Phase 1 output.** The user's cognitive
load when reviewing findings must be minimized.

### `validation_report.md` (Case B output)

**In**: Structural checks (AC coverage, after-chains, target_package, opus flags).

**Not in**: Semantic correctness (that's `release-begin-impl-finalize`'s job).

**Quality standard**: Machine-generated, must be reproducible. Any failure must
include the exact failing task ID, the expected vs. actual value, and the
remediation command to run.

---

## 8. Quality Rating and Recommendation for Further Rounds

### What Plans v1–v3 Get Right

- Architecture decision (distributed over monolithic) is correct.
- Removal of redundant phases is correct.
- Task Creation Planner concept is the right solution for the holistic-
  understanding gap.
- Two user gates (vs. 5+) is the right target.
- Self-perpetuating orchestration chain is elegant.

### Remaining Open Issues Before Implementation

| Issue | Severity | Gap reference |
|-------|----------|---------------|
| `task_creation_plan.md` has no defined schema | High | Gap A |
| `propose_after.py` doesn't know about the plan | High | Gap G, section 6 |
| Phase 6 timing problem — best solution chosen (Option B) but not yet in skill spec | High | Section 1 |
| Case A removal must be sequenced carefully | Medium | S4 |
| `release-begin-impl-finalize` name confirmed but old name still in plan v2/v3 docs | Low | Section 2 |
| After-chain check belongs in Case B only, not in finalize skill | Medium | Gap F |
| Phase 4 removal from `release-begin-impl` not yet reflected in implementation plan | Low | S1 |
| `propose_after.py` layer-awareness not scoped | Medium | Gap C |
| Phase 2b `_agent_state.md` → file-polling simplification | Low | Gap D, S3 |

### Quality Rating: 7.5 / 10

Plans v1–v3 are architecturally sound. The high-severity gaps (schema, timing,
`propose_after.py` integration with plan) are design-level issues that, if left
unresolved, will surface as implementation problems during coding.

### Is Another Round Needed?

**Yes — one more targeted round.** Scope: the three high-severity gaps.

Specifically, the next Opus round should produce:
1. **The concrete schema for `task_creation_plan.md`** — enough for an engineer
   to implement both the Planner (writer) and `task-create-code` (reader)
   without ambiguity.
2. **Updated Phase 6 spec** — incorporating Option B (after-chain) timing
   solution, including the `--after-task` argument to `create_orchestration_task.py`.
3. **`propose_after.py` enhancement spec** — when a plan exists, use it;
   when it doesn't, use the enhanced layer-aware heuristic.

After that round, Plans v3 + the gap analysis here + the new round's outputs
together form a complete implementation brief. Implementation can begin.
