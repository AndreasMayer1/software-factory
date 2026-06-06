---
id: REQ-PROC-035
urgency: 4
urgency_reason: U4-PLAN
impact: 4
impact_reason: I4-QUAL
status: active
effort: M
stakeholder: developer
created: 2026-03-06
updated: 2026-06-05
after: [REQ-PROC-034, REQ-PROC-009, REQ-PROC-058]
blocks:
  - REQ-PROC-036
market_research_refs: [] # No relevant findings identified
trackable_items:
  sections:
    - id: SEC-01
      name: "Requirement Completeness"
      heading: "## Requirement Completeness"
      target_package: "Transfer Data Model"
    - id: SEC-02
      name: "Task Coverage"
      heading: "## Task Coverage"
      target_package: "Transfer Data Model"
    - id: SEC-03
      name: "Scope Completeness"
      heading: "## Scope Completeness"
      target_package: "Transfer Data Model"
    - id: SEC-04
      name: "User Approval Gate"
      heading: "## User Approval Gate"
      target_package: "Transfer Data Model"
    - id: SEC-05
      name: "Task Creation Process"
      heading: "## Task Creation Process"
      target_package: "Transfer Data Model"
    - id: SEC-06
      name: "release-begin-impl Integration"
      heading: "## release-begin-impl Integration"
      target_package: "Transfer Data Model"
    - id: SEC-07
      name: "Release Status Overview"
      heading: "## Release Status Overview"
      target_package: "Transfer Data Model"
    - id: SEC-08
      name: "Two-Wave Decomposition"
      heading: "## Two-Wave Decomposition"
      target_package: "Transfer Data Model"
    - id: SEC-09
      name: "Scribble-Gate Terminal"
      heading: "## Scribble-Gate Terminal"
      target_package: "Transfer Data Model"
    - id: SEC-10
      name: "release-derive-code Skill"
      heading: "## release-derive-code Skill"
      target_package: "Transfer Data Model"
    - id: SEC-11
      name: "release-finalize-impl Skill"
      heading: "## release-finalize-impl Skill"
      target_package: "Transfer Data Model"
    - id: SEC-12
      name: "Session and Token Allocation"
      heading: "## Session and Token Allocation"
      target_package: "Transfer Data Model"
target_package: "Transfer Data Model"

---

# REQ-PROC-035: Release Preparation

## User Story

As a developer I want to ensure that before implementation begins on a release, all requirements are complete and sufficiently detailed, all necessary task files exist, and no required features have been overlooked — so that coding can start with confidence and nothing is discovered mid-sprint that forces scope changes.

## Overview

A release version is only implementation-ready when three conditions are simultaneously true:

1. Every requirement assigned to the release is complete enough to be implemented
2. Every such requirement has at least one task file (goal.md) describing the implementation work
3. The requirement set fully covers the release scope as defined in RELEASES.md

This requirement defines what "preparation complete" means for a release, what quality gates must be passed, and what artifacts must exist before the developer declares a release ready to implement.

---

## Requirement Completeness

A requirement assigned to a release is **implementation-ready** when it is at a granularity level where tasks can be directly derived from it (per REQ-PROC-009 epic vs. feature rules), and its acceptance criteria or sections are specific enough that an engineer can act on them without ambiguity.

Requirements that are too coarse, too vague, or missing feature-level breakdowns are not ready. Any gaps discovered during preparation must be resolved — by creating or refining requirements — and reviewed by the developer before tasks are created for them.

---

## Task Coverage

A release is task-covered when every implementation-ready requirement assigned to the release has at least one task file created for it, following the conventions in REQ-PROC-009.

**Epic requirements are exempt** from implementation task coverage (per REQ-PROC-009). Task coverage applies to feature-level requirements only.

---

## Scope Completeness

The requirement set for a release is **scope-complete** when every item listed under `scope_boundaries.includes` in RELEASES.md maps to at least one assigned requirement.

Items that are frequently overlooked and must be explicitly verified:

- **Navigation and routing**: Is the basic navigation shell (role routing, tab structure, initial route) covered by an assigned requirement?
- **Role selection and onboarding**: If the release includes a first-launch or role selection flow, is it covered?
- **Data model and persistence**: Is the underlying data layer (serialization, local storage, model versioning) covered?
- **UI theme and design system**: Are any design system requirements (theme, navigation patterns) that the release features depend on assigned to this release or an earlier one?

A scope gap is a `scope_boundaries.includes` item for which no assigned requirement provides coverage. Scope gaps must be resolved — either by assigning an existing requirement to the release or by creating a new requirement — before preparation is complete.

---

## User Approval Gate

Preparation is complete only after the developer has reviewed and approved:

1. **All requirements** in the release scope — including any newly created ones
2. **All task files** created for the release

New requirements are not finalized, and tasks are not created for them, until the developer approves the requirement. Multiple feedback iterations are expected and allowed. A partial approval (approve some, revise others) is valid — approved items may proceed while others are still being iterated.

The developer's approval is the single quality gate. No task enters implementation status for a release that has not passed this gate.

---

## Task Creation Process

Implementation tasks for a release are created package-by-package using `task-create-code`. A package is covered once every plan entry belonging to that package has a corresponding non-terminal impl task.

**Manual path**: The developer invokes `task-create-code` in zero-parameter mode. The skill selects the highest-priority uncovered package from `RELEASE_BACKLOG.md` and creates the task.

**Self-perpetuating chain (automated path)**: `release-begin-impl` Phase 6 creates the first orchestration task via `scripts/create_orchestration_task.py`. Each orchestration task targets exactly one package and materializes every plan entry belonging to that package, capped at six entries per session. The same-package constraint keeps session context focused; the six-entry ceiling guards against context blowup on large packages. If a package contains more than six uncreated entries, the next orchestration task continues with the same package until all its entries are materialized before advancing to the next package in the plan's execution order.

An orchestration task's acceptance criteria are a dynamic list of N+2 entries, where N is the number of plan entries to be materialized in this session (1 ≤ N ≤ 6):
- One entry per plan entry: "Run `task-create-code` in zero-parameter mode for `[task_name]` (covers ACs: [ac-list])" — or `ui-create-scribble` for scribble-type entries as specified in `task_creation_plan.md`
- One entry: "Run `python3 scripts/create_orchestration_task.py --after-task <this_task_id> --plan-path <plan_path>` — creates the next orchestration task (advancing to the next uncreated package, or a validation orchestration task when all packages are covered)"
- One entry: "Run `task-complete` on this orchestration task"

The autorun executes each orchestration task in sequence, materializing one full package's tasks (up to six) per session. No external bootstrap triggers are needed; the chain is self-sustaining.

**Two-slot alternation guard**: The create step (AC N+1) runs *while the orchestration task that issues it is still `in_progress`* — it must, because AC ordering requires creating the next link before `task-complete` closes the current one. A naive "an orchestration task already exists, refuse" guard would therefore deadlock the chain: the issuing task would match its own guard. To prevent this, `create_orchestration_task.py` excludes the issuing caller (passed as `--after-task <this_task_id>`) from its duplicate check. The guard still refuses (exit 2) if a *different* non-terminal orchestration task exists for the active release, so two live orchestration tasks never coexist. To avoid accumulating one folder per link, the chain alternates between at most **two** orchestration-task folders per active release: when creating the next link, the script overwrites the folder of the caller's own immediate predecessor (the now-terminal orchestration task named in the caller's `after:` list) rather than creating a third folder. If no terminal predecessor folder exists (the first link in a chain, or a clean state), a fresh folder is created instead. The validation orchestration task (created when all packages are covered) obeys the same two-slot rule. The at-most-two-folders invariant holds for both the impl and validation branches.

**Orchestration-first ordering**: While any non-terminal orchestration task exists for the active release, it ranks above any implementation task in the next-task ordering output. As a consequence, the entire orchestration chain for a release runs to completion — making every implementation task visible — before any implementation task is surfaced for execution. This ordering eliminates false-positive coverage warnings during the materialization phase and gives the developer a complete release picture before implementation begins.

**Task Creation Plan**: `release-begin-impl` Phase 2c (Task Creation Planner) produces a `task_creation_plan.md` artifact as a sibling to the explore task's `goal.md`. Phase 2c does NOT perform per-requirement decomposition itself; it spawns one `task-derive-from-requ` agent per in-scope requirement and assembles their outputs. Each `task-derive-from-requ` agent produces a per-requirement plan with a coverage matrix mapping every AC to at least one task (per REQ-PROC-058 AC-01), a mandatory verification task, sizing signals, and dependency ordering. Phase 2c then composes these per-requirement plans into the release plan and adds release-level concerns on top: ordered package execution list, cross-requirement dependencies, and release scope completeness checks. The release plan and the per-requirement plans share the unified format defined in REQ-PROC-058 SEC-04. `task-create-code` in zero-parameter mode reads this plan for authoritative task configuration, skipping user confirmation (the developer approved the plan at Phase 5). Each orchestration task carries a `plan_path:` frontmatter field pointing to the plan.

**Completeness signal**: When all packages are covered, `create_orchestration_task.py` creates a validation orchestration task instead of an impl task. The validation task runs structural checks: AC coverage completeness, after-chain integrity, `target_package` consistency, and `opus_recommended` flag sanity. The chain ends when the validation task completes successfully.

**Guard**: The first orchestration task carries `after: [<explore_task_id>]`. The explore task is auto-closed at Phase 6 end by `task-complete`. The orchestration task cannot execute until the explore task reaches terminal status, preventing premature execution while `release-begin-impl` is still running.

---

## release-begin-impl Integration

The `/release-begin-impl` skill is the single entry point for "I have verified requirements, now start implementation." It runs the following phases:

- **Phase 0**: Detect mode (package vs. release), identify the target release, and check for any in-progress prior `release-begin-impl` session for the same release (offering resume or abandon).
- **Phase 1**: Scope coverage check — verifies every package in the release has ≥1 assigned requirement, every `scope_boundaries.includes` item maps to ≥1 requirement, and no package appears in both scope and exclusions.
- **Phase 2**: Epic agents run in parallel — each reads an epic's requirements.md and child feature files to verify feature coverage and completeness.
- **Phase 2b**: Remediation — gap fixes are applied via output-file polling. Each remediation agent writes to a pre-assigned path; the orchestrator scans for output files rather than tracking agent IDs.
- **Phase 2c — Task Creation Planner**: Phase 2c delegates per-requirement decomposition to `task-derive-from-requ` (per REQ-PROC-058 AC-14). For each in-scope feature requirement, Phase 2c spawns a `task-derive-from-requ` agent that produces a per-requirement plan with coverage matrix, verification task, sizing signals (S1–S4 per REQ-PROC-001), and dependency ordering. Phase 2c then assembles the per-requirement plans into `task_creation_plan.md`, adding release-level concerns: ordered package execution list, cross-requirement dependencies, and release scope completeness. The release plan and the per-requirement plans share the unified format defined in REQ-PROC-058 SEC-04. Already-implemented ACs (detected by `scripts/check_requirement_implementation.py`) are marked `task_type: verify`. Every in-scope requirement has 100% AC coverage in the assembled plan before Phase 5 is reached.
- **Phase 5 — User Gate**: The orchestrator runs `scripts/summarize_plan.py` and presents a 1-page summary alongside the full plan path, the per-requirement coverage matrices produced in Phase 2c, and all Phase 1–2 findings. The developer reads and either approves or requests revisions. Only when the developer says "approved" does Phase 6 proceed.
- **Phase 6 — Activate and hand off**:
  1. Pre-checks (no mutations): verify Phase 5 gate passed; verify `task_creation_plan.md` exists; run `create_orchestration_task.py --dry-run --after-task <explore_id>` — must exit 0.
  2. Mutations (committed atomically by `task-complete` in the final step): set RELEASES.md `status: planned → active`; run `create_orchestration_task.py --after-task <explore_id> --plan-path <plan_path>` (creates first orchestration task with `after: [<explore_id>]` and `plan_path`); mark all explore task acceptance criteria as completed; call `task-complete` on the explore task — this produces one atomic commit covering RELEASES.md, the new orchestration task, and the closed explore task.
  3. Print handoff message with the new orchestration task ID and recommended next step.

**Explore task lifecycle**: The explore task that runs `release-begin-impl` is auto-closed at Phase 6 end. `task-complete` is called on it as the final step of Phase 6. The first orchestration task's `after: [<explore_id>]` ensures it cannot execute while the explore task is still open.

**After Phase 6 completes**: The developer starts `/autorun`. The orchestration task is immediately runnable (after-chain is satisfied because the explore task was just completed). The autorun runs each orchestration task in sequence, materializing one full package's impl tasks (up to six) per session, until the validation orchestration task completes. Orchestration tasks always rank above implementation tasks (see SEC-05 "Orchestration-first ordering"), so every impl task for the release exists in the task list before any impl task starts executing.

**After autorun completes**: Once the validation orchestration task reports success (all packages covered, structural checks passed), the developer runs `/release-begin-impl-finalize`. This interactive skill runs:
- Phase 1: Coverage re-verification (`generate_status_overview.py`) plus plan conformance audit (`check_task_against_plan.py` per impl task).
- Phase 2: After-chain reconciliation (`reconcile_after_chains.py --release [v] --plan [plan_path]`; applies fixes with `--apply` if gaps found).
- Phase 3: Semantic validation — N agents, one per feature, each verifying that impl task goal.md files address the AC intent.
- Phase 4: User review gate — consolidated findings presented for developer approval.
- Phase 5: On approval, finalizes RELEASES.md metadata, regenerates STATUS.md, commits.

`/release` may only be invoked after `/release-begin-impl-finalize` completes successfully.

**The developer must NOT set `status: active` manually in RELEASES.md.** The skill enforces the one-active-at-a-time constraint. Manual edits bypass this guard.

**Lifecycle**:
- `planned` → set to `active` by `release-begin-impl` Phase 6 when preparation is approved
- `active` → set to `released` by the `/release` skill after successful release
- Only one release may have `status: active` at a time; `release-begin-impl` must enforce this

---

## Release Status Overview

The `scripts/release_readiness.py` script and `/release-status` skill give the developer a quick picture of where the project stands in the release workflow — without reading any other documentation.

**How to use**: Run `/release-status` at any time. The script detects the current stage (0–5) and prints a recommended next step.

**Stages detected**:

| Stage | Condition | Recommended action |
|-------|-----------|-------------------|
| 0 | No requirements-authoring tasks exist for the next release | Run `/requ-derive-from-flow` or `/requ-explore` |
| 1 | Requirements-authoring tasks exist but not all completed | Complete or unblock the listed tasks |
| 2 | Requirements complete, but packages not all assigned | Run `/requ-assign-packages` |
| 3 | Packages assigned, release not yet active | Run `/release-begin-impl` |
| 4 | Release active, impl tasks being created/executed | Note progress; check if autorun is running. When `task_creation_plan.md` is present, Stage 4 may show a per-package status table (orchestration task pending / running / completed per package). |
| 5 | All impl tasks done | Run `/release` to cut the release |

**Implementation**: The script reads RELEASES.md, RELEASE_BACKLOG.md, task goal.md files, and `automation/.automated_mode`. It imports or subprocesses `check_requirements_ready.py` for stage 1–2 detection.

---

## Two-Wave Decomposition

Implementation of a release proceeds in two decomposition waves separated by the scribble gate. The boundary between the waves is determined per design-unit, not per release.

A **design-unit** is a set of requirements coupled by a shared flow or shared entry surface. A **pure-domain unit** is a design-unit whose output set contains no Presentation-layer artifact: it touches only the domain and data layers and produces no widget, screen, or scribble. Any design-unit that produces at least one scribble or Presentation-layer artifact is a **Presentation unit**.

The decomposition of a release satisfies the following invariant:

- **Wave 1 (`release-begin-impl`)**: For every Presentation unit, Wave 1 holds only its scribble plan entries together with PROP-11 basis, coverage, and foundation plan entries. For every pure-domain unit, Wave 1 holds the unit's full coding plan entries. No Presentation coding plan entry exists for any Presentation unit at the end of Wave 1.
- **Wave 2 (`release-derive-code`)**: The Presentation coding plan entries for a Presentation unit exist only after that unit's scribbles are approved. A Presentation coding plan entry traces to an approved scribble and its `flutter_handoff.yaml` as its decomposition input.

This bisection is a **hard requirement**: the existence of a Presentation coding task for a requirement whose covering scribble is missing or unapproved is a release-preparation violation. The per-design-unit boundary is the liveness knob — coding decomposition for a unit proceeds as soon as that unit's scribbles approve, independently of the scribble state of other units.

*Trade-off record (per-design-unit boundary):* The boundary is **per-design-unit** rather than release-global. Chosen because it preserves cross-unit parallelism — backend work for a pure-domain unit and coding for an already-approved unit proceed while other units' scribbles are still in review. Traded away: the simplicity of a single release-global gate, at the cost of requiring the design-unit map (a cheap by-product of the upstream cluster analysis) to define the boundary.

---

## Scribble-Gate Terminal

The orchestration chain carries two terminal orchestration-task states. They compose as a sequence rather than as alternatives.

- The **scribble-gate terminal** is reached when the scribble orchestration chain has run every scribble task of a design-unit to a completed-and-approved state. Its terminal orchestration task instructs the chain to run `release-derive-code` for that unit's Presentation coding decomposition. The scribble-gate terminal precedes and gates Wave-2 code derivation: no Presentation coding task is materialized before the scribble-gate terminal for its unit is reached.
- The **`_VALIDATION` terminal** remains the release-readiness terminal. It is reached when all packages are covered and runs the structural checks (AC coverage completeness, after-chain integrity, `target_package` consistency, `opus_recommended` sanity). The release-readiness `_VALIDATION` terminal is reached only after the coding chain materialized in Wave 2 is complete.

Both terminals obey the existing self-perpetuating-chain rules (one-active-orchestration-task constraint, two-slot folder alternation, orchestration-first ordering). A plan entry of `task_type: scribble` resolves to `ui-scribble-iterate`.

---

## release-derive-code Skill

`release-derive-code` is the Wave-2 orchestrator skill. It runs during an already-begun implementation, after the scribble gate for a design-unit is reached.

Its end-state responsibility: for each Presentation requirement of a design-unit whose scribbles are approved, `release-derive-code` produces that requirement's Presentation coding plan entries by running per-requirement decomposition in `--scope code` mode (REQ-PROC-058), reading the approved scribble and its `flutter_handoff.yaml` as the decomposition input rather than the raw Presentation requirement text. It injects the SCI coding edge (each coding task `after` the scribble task of every requirement it covers) and spawns the coding orchestration chain for the unit.

---

## release-finalize-impl Skill

The Wave-2 finalize skill is named `release-finalize-impl`. It is the release-readiness skill invoked after the coding orchestration chain reaches the `_VALIDATION` terminal, and `/release` may only be invoked after it completes successfully.

`release-finalize-impl` runs the coverage re-verification, after-chain reconciliation, semantic validation, and user-review gate that finalize the release. Its Phase-1 coverage audit additionally performs an **SCI audit**: for every coding task, it resolves the scribble of each covered requirement and asserts that the scribble is `approved` and its contributing-requirements commit is at or beyond the requirement's current committed version. A coding task whose covered scribble is missing, unapproved, or stale is an SCI violation that blocks finalization. The SCI audit extends, and does not replace, the orphaned-path parity check.

---

## Session and Token Allocation

The chain's work is allocated across three execution contexts so that each session holds only what it needs and persistent artifacts are the hand-off medium:

- **Orchestrator (main session)** owns release-level coordination and never reads `requirements.md` wholesale. Per-requirement decomposition in both waves is performed by **spawned background agents**, one `task-derive-from-requ` invocation per requirement.
- **Spawned agent** context: each Wave-1 `task-derive-from-requ --scope presentation` agent and each Wave-2 `task-derive-from-requ --scope code` agent runs in its own context. The Wave-2 agent reads the small `flutter_handoff.yaml` plus the bounded set of non-Presentation ACs of its requirement, not the raw Presentation requirement again.
- **New task** context: each scribble task and each coding task runs in a fresh session. The scribble session reads its requirement, flow, and personas once and distills the requirement's Presentation content into `flutter_handoff.yaml`; the coding session reads that distilled `flutter_handoff.yaml` plus its covered ACs. The scribble→code hand-off through `flutter_handoff.yaml` is the point at which a Presentation requirement's locked-in content is read once and reused, rather than re-read by the Wave-2 decomposition and the coding session.

---

## Related Requirements

- **REQ-PROC-034** (Release Version Management): Defines how releases are versioned and how requirements are assigned to them. Release preparation acts on the output of that process.
- **REQ-PROC-009** (Requirements and Tasks): Defines task file structure and conventions. All task files created during preparation must follow those conventions.
- **REQ-PROC-058** (Implementation Task Planning Quality): Defines `task-derive-from-requ`, the per-requirement decomposition skill that Phase 2c delegates to (AC-14), and the unified plan format (SEC-04) that the release plan and per-requirement plans share.
