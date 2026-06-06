---
id: REQ-PROC-058
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-ENAB
status: active
effort: L
stakeholder: developer
created: 2026-05-23
updated: 2026-06-05
after: [REQ-PROC-009]
blocks: [REQ-PROC-035, REQ-PROC-045]
market_research_refs: []
target_package: ""
trackable_items:
  acceptance_criteria:
    - id: AC-01
      name: "Coverage matrix at decomposition time"
    - id: AC-02
      name: "Verification task is mandatory"
    - id: AC-03
      name: "Sizing signals on every planned task"
    - id: AC-04
      name: "Plan-before-create gate"
    - id: AC-05
      name: "Wraps task-create and task-create-code"
    - id: AC-06
      name: "Enforcement-creates-violations detection"
    - id: AC-07
      name: "Dependency graph with correct ordering"
    - id: AC-08
      name: "Post-creation validation"
    - id: AC-09
      name: "Incremental decomposition for partially-covered requirements"
    - id: AC-10
      name: "task-create warns on uncovered ACs"
    - id: AC-11
      name: "task-create-code accepts plan-driven inputs"
    - id: AC-12
      name: "Shared plan format across task-derive-from-requ and release-begin-impl"
    - id: AC-13
      name: "Code tasks describe WHAT, not HOW"
    - id: AC-14
      name: "release-begin-impl Phase 2c produces per-requirement coverage matrices"
    - id: AC-15
      name: "No duplicated computation across skill levels"
    - id: AC-16
      name: "Cross-package ACs produce tasks in their own package"
    - id: AC-17
      name: "Cross-reference completeness gate before task creation"
    - id: AC-18
      name: "Wave-scoped decomposition mode with wave-tagged plan entries"
    - id: AC-19
      name: "Fused-responsibility skills carry a trade-off record"
    - id: AC-20
      name: "Every plan-entry task_type resolves to a registered skill"
  sections:
    - id: SEC-01
      name: "Skill Boundary"
      heading: "## Skill Boundary"
    - id: SEC-02
      name: "Workflow Integration"
      heading: "## Workflow Integration"
    - id: SEC-03
      name: "Code Task Creation (task-create-code)"
      heading: "## Code Task Creation (task-create-code)"
    - id: SEC-04
      name: "Unified Plan Format"
      heading: "## Unified Plan Format"
    - id: SEC-05
      name: "Skill-Design Trade-off Record"
      heading: "## Skill-Design Trade-off Record"
    - id: SEC-06
      name: "Registry Routing Contract"
      heading: "## Registry Routing Contract"
---

# Implementation Task Planning Quality

## Overview

When implementation tasks are created from a requirement, the task set as a whole satisfies quality properties that no individual task can guarantee: every acceptance criterion has at least one covering task, a verification task confirms the requirement is met end-to-end, tasks are sized to fit the executing agent's context budget, and the dependency ordering is sound.

## Purpose

Task decomposition today happens ad-hoc: tasks are created one at a time via `task-create` or `task-create-code`, each with a single-task view of the requirement. No holistic quality gate exists at decomposition time. The consequence is predictable — ACs fall through the cracks, verification is forgotten, and the requirement is treated as "done" when structural gaps remain invisible.

Two independent incidents demonstrated this failure pattern:
- **REQ-PROC-046**: 13 ACs, 14+ tasks. AC-03 and AC-06 had zero coverage. ~160 pre-existing violations from new gate scripts were never addressed. No verification task.
- **REQ-PROC-001**: 8 ACs, 7 tasks. AC-04 and AC-07 had zero coverage. No verification task.

The root cause is identical: task creation lacks a mandatory step that views the full AC set, ensures complete coverage, and includes verification.

## Acceptance Criteria

- **AC-01** — Every requirement decomposed into tasks has a coverage matrix that maps each AC to at least one task. An AC with zero task coverage is a blocking error that prevents task creation from proceeding.

- **AC-02** — Every requirement decomposition includes at least one verification task that confirms the requirement is met end-to-end. The verification task type matches the requirement type: test task for code requirements, audit task for process requirements, review task for documentation requirements.

- **AC-03** — Each task produced by decomposition carries REQ-PROC-001 sizing metadata: `expected_tool_calls` or `skill_chain_depth`, and `synthesis_dependent: true` with justification when applicable. The `opus_recommended` field reflects the S1-S4 composition from REQ-PROC-001.

- **AC-04** — The coverage matrix and task plan are produced and validated before any task is created. The user reviews and approves the plan before task-create or task-create-code is called.

- **AC-05** — The decomposition skill delegates individual task creation to `task-create` (non-code tasks) or `task-create-code` (Dart code tasks touching `lib/`, `test/`, `integration_test/`). The choice is automatic based on task scope. The existing creation primitives are preserved — the decomposition skill wraps them, not replaces them.

- **AC-06** — When a planned task's scope includes creating enforcement mechanisms (scripts, gates, lint rules, checkers), the decomposition automatically proposes a companion remediation task to address pre-existing violations. The companion task depends on the enforcement-creation task and has explicit scope: run the new gate, fix all violations, confirm zero output.

- **AC-07** — The decomposition produces a dependency graph expressed as `after:` chains between tasks. No circular dependencies exist. The ordering reflects logical implementation sequence (infrastructure before consumers, enforcement before remediation).

- **AC-08** — After all tasks are created, a post-creation validation step runs `scripts/requirements/coverage_report.py` on the requirement and confirms 100% AC coverage. Any discrepancy between the planned coverage matrix and the actual post-creation coverage is a blocking error.

- **AC-09** — The skill handles partially-covered requirements: it reads existing tasks, computes current coverage, and plans tasks only for uncovered ACs. The coverage matrix shows the full picture (existing + planned tasks) so the user sees the complete state. When existing tasks have empty `covers:` fields, the skill reads their goal.md bodies, infers coverage from scope description and task name, and proposes `covers:` updates for user confirmation before planning new tasks. This metadata repair runs in Phase 1, before any new task is planned.

- **AC-10** — When `task-create` or `task-create-code` is invoked directly in standalone mode (not through task-derive-from-requ or a plan-driven path) on a requirement that has uncovered ACs, it redirects to task-derive-from-requ. Exempt from redirect: bugfix tasks (repairs, not decompositions), explore/define tasks (upstream of implementation), and plan-driven invocations (coverage already ensured by the plan).

- **AC-11** — Both `task-create-code` and `task-create` accept pre-computed values from a task creation plan (produced by task-derive-from-requ or release-begin-impl Phase 2c). In plan-driven mode, the provided values (ACs, effort, layer, dependencies, opus_recommended) replace the skill's own discovery and coverage-asking phases. For task-create-code, file-level scope analysis still runs to refine sizing (estimate-and-refine per AC-15). For task-create, no refinement is needed — plan values are used directly.

- **AC-12** — The task creation plan format is shared between task-derive-from-requ and release-begin-impl Phase 2c. Both produce plans consumable by task-create-code through the same Phase 0A path. A plan entry contains: task name, covered ACs, effort, layer, after-chains, task type, implementation notes, and opus_recommended.

- **AC-13** — Code tasks (goal.md files created by task-create-code) describe WHAT to implement and the requirement context for sizing — not HOW. Implementation plans with concrete code changes are created fresh at execution time by the implementing skill (code-simple, code-complex, code-test) against the current codebase.

- **AC-14** — release-begin-impl Phase 2c delegates per-requirement decomposition to task-derive-from-requ. The release plan contains per-requirement coverage matrices produced by task-derive-from-requ, not by Phase 2c's own independent analysis. Phase 2c adds release-level concerns (package ordering, cross-requirement dependencies, scope completeness) on top. Every requirement in the release has 100% AC coverage in the plan before the user gate (Phase 5) is presented.

- **AC-15** — No quality concern is redundantly recomputed across skill levels. Two patterns govern the flow of authority:
  - **Compute once, trust downstream**: Coverage matrix, verification task presence, and user review are computed by the upstream skill (task-derive-from-requ or release-begin-impl) and accepted without recomputation by downstream skills. These concerns require the holistic view that only the upstream level has.
  - **Estimate upstream, refine downstream**: Sizing, effort, and dependencies are estimated by the upstream skill based on AC-level analysis, then refined by the downstream skill (task-create-code) with domain-specific detail — file-level scope analysis, layer detection, codebase-level dependency scanning. Refinement may escalate: if task-create-code's file analysis reveals a task is significantly larger than the plan estimated (e.g., Large → Split NOW), it reports back rather than silently proceeding with a mismatched plan.
  
  Standalone mode (no upstream plan) is the only case where a downstream skill computes all concerns itself.

- **AC-16** — When ACs within a single requirement have different `target_package` values (cross-package ACs), task-derive-from-requ groups tasks by AC package and assigns each task the package of the ACs it covers. The coverage matrix groups by package and shows which package each task belongs to. A single decomposition run may produce tasks in multiple packages.

- **AC-17** — Before producing the task plan, task-derive-from-requ verifies cross-reference completeness of the target requirement. It checks the `after:` chain, `blocks:` chain, and `## Related Requirements` body section against a keyword-grep across `requirements_tasks/` (detection mechanism defined by REQ-PROC-045). Detected gaps are classified by the user (or by the developer via answer.md in automated mode) into: hard dependency (add to `after:`), semantic relationship (add to Related Requirements), or not related (ignore with reason). Classified fixes are applied by spawning an agent that invokes `requ-explore` against the target requirement; the agent commits the cross-reference updates. task-derive-from-requ blocks until the agent completes, then re-runs Phase 1 to verify gaps are resolved. The write-requirement step is part of the task-derive-from-requ workflow, executed via a delegated requ-explore agent in both interactive and automated modes.

- **AC-18** — `task-derive-from-requ` exposes a `--scope {presentation,code}` mode that bisects a requirement's decomposition along the wave boundary. In `--scope presentation`, the plan it produces for a Presentation requirement contains only scribble entries (plus basis/coverage/foundation entries); in `--scope code`, the plan contains the Presentation coding entries derived from the approved scribble and its `flutter_handoff.yaml`. Every plan entry carries a `wave:` tag (`presentation` or `code`) and a `scope:` tag identifying the design-unit, so a plan distinguishes which entries belong to which wave and design-unit. A pure-domain requirement is decomposed in full in a single `presentation`-scope run with all entries tagged `wave: code` (no scribble entry), because it has no Presentation-layer artifact to gate on.

- **AC-19** — A skill whose specification documents more than one artifact-in→artifact-out pair, or that carries a mode flag (such as `--scope`), carries a documented **trade-off record**: the chosen fusion of responsibilities and what the alternative (separate single-responsibility skills) would have offered. A single-responsibility skill (exactly one artifact-in→artifact-out pair and no mode flag) carries only its one-sentence responsibility statement and no trade-off record.

- **AC-20** — Every value that a plan entry's `task_type` field may take resolves to a skill registered as its routing consumer in `.factory/registry/artifacts.yaml`. A `task_type` that names no registered consumer skill is detectable and rejected by the registry routing-contract check. No plan entry can route to a skill string that does not name an existing skill.

## Skill Boundary

Three skills form the implementation task planning system. Each has a distinct responsibility:

| Skill | Responsibility | Scope |
|---|---|---|
| `task-derive-from-requ` (new) | Multi-task decomposition with quality gates | One requirement → N tasks with coverage matrix |
| `task-create-code` (existing) | Single Dart code task creation with scope analysis | One task → goal.md for lib/test/integration_test changes |
| `task-create` (existing) | Single non-code task workspace creation | One task → goal.md for process/doc/skill/explore tasks |

**`task-derive-from-requ` orchestrates; `task-create` / `task-create-code` create.** task-derive-from-requ analyzes the requirement, produces a plan with coverage matrix, gets user approval, then calls the creation primitives for each task.

**`task-derive-from-requ` is mandatory when a requirement has `trackable_items.acceptance_criteria` and the task type is impl or verify.** When `task-create` or `task-create-code` is invoked directly in standalone mode on such a requirement, it redirects to task-derive-from-requ (AC-10). Exempt: bugfix tasks (repairs), explore/define tasks (upstream of decomposition), and plan-driven invocations (coverage already ensured). Two modes prevent this from being heavy-handed:
- **Quick mode** (1-2 tasks, user names ACs explicitly, at most 1 code task): coverage check before and after, creates tasks immediately. Overhead vs bare task-create: ~1 read + 1 coverage check.
- **Full mode** (new requirement with zero tasks, ≥ 3 uncovered ACs, or > 1 code task in quick mode): complete 6-phase decomposition process.

Mode selection is automatic based on current coverage state, not user choice.

**`task-create` remains independent** for tasks without a parent requirement (standalone explore tasks that will create a requirement) or requirements without acceptance criteria.

**release-begin-impl Phase 2c** currently performs per-requirement decomposition as part of its release-level planning — a monolithic agent reads all requirements and produces one plan. This duplicates task-derive-from-requ's per-requirement analysis (AC grouping, sizing, ordering) at a lower quality level (no coverage matrix, no verification tasks, no enforcement detection). The target state separates concerns:
- **Phase 2c owns release-level concerns**: which packages, what execution order, cross-requirement dependencies, release scope completeness.
- **task-derive-from-requ owns per-requirement concerns**: AC coverage, verification, sizing, enforcement detection.
- **Phase 2c calls task-derive-from-requ per requirement**, then assembles the per-requirement plans into a release plan in the unified format (SEC-04).

## Workflow Integration

Five paths lead to "I need implementation tasks for this requirement." task-derive-from-requ integrates differently with each:

| Path | Integration | Mode |
|---|---|---|
| **W1**: requ-explore finishes, user wants tasks | User invokes task-derive-from-requ on the freshly written requirement. Separate invocation from requ-explore to avoid context blowup. | Full |
| **W2**: Existing requirement, gap discovered | task-create redirects to task-derive-from-requ (AC-10). Quick mode for 1-2 targeted tasks; full mode if ≥ 3 ACs uncovered. | Quick or Full |
| **W3**: Dedicated explore task to decompose a requirement | Natural fit. claude-route detects goal shape and invokes task-derive-from-requ. | Full |
| **W4**: release-begin-impl Phase 2c | Phase 2c handles release-level concerns (package ordering, scope completeness), delegates per-requirement decomposition to task-derive-from-requ (AC-14). Combined output is consumed by task-create-code via Phase 0A. | Plan-driven |
| **W5**: product-intake landing on a requirement | Downstream. product-intake creates/updates requirements. User invokes task-derive-from-requ afterward. | Full |

**Mandatory with escape hatch.** task-derive-from-requ is mandatory when the requirement has acceptance criteria (see SEC-01). Quick mode keeps the overhead minimal for simple cases. For requirements without acceptance criteria, or for tasks without a parent requirement, task-create operates independently.

## Behavior

### Decomposition phases

The skill operates in six phases. The first four produce the plan; the last two execute it.

**Phase 1 (Gather)**: Read the requirement, all ACs, existing tasks and their coverage, related/blocking requirements. Compute current coverage state. For existing tasks, read goal.md frontmatter only (covers: field) — not full bodies. For code requirements (functional features), optionally run `check_requirement_implementation.py` to detect already-implemented ACs without covering tasks (orphaned implementation). If > 3 related requirements need reading, spawn a gather agent to read and distill rather than reading all inline.

**Phase 2 (Analyze)**: Group ACs by logical implementation unit. Determine task types (code, process, doc, explore, verification). Detect enforcement-creates-violations pattern. Identify cross-cutting concerns.

**Phase 3 (Plan)**: For each planned task: name, type, ACs covered, scope, sizing signals (S1-S4 from REQ-PROC-001), opus_recommended, dependencies. Produce coverage matrix. Verify: 100% AC coverage, verification task present, no circular dependencies.

**Phase 4 (Review)**: Present plan + coverage matrix to user. User approves, modifies, or rejects. No task is created until user approves.

**Phase 5 (Create)**: For each approved task, call task-create (non-code) or task-create-code (Dart code). Pass pre-computed values from the plan (plan-driven mode per AC-11).
- **≤ 6 tasks**: create inline in the current session.
- **> 6 tasks**: persist the plan as a file artifact. Create an orchestration task (same pattern as release-begin-impl Phase 6) that materializes ≤ 6 tasks per session via plan-driven mode.

**Phase 6 (Validate)**: Run coverage_report.py. Confirm 100% coverage post-creation. Print final coverage matrix.

### Cross-reference completeness gate (Phase 1.5)

Between Phase 1 (Gather) and Phase 2 (Analyze), a cross-reference completeness gate runs:

1. **Detect**: keyword-grep across `requirements_tasks/` for terms derived from the target requirement (mechanism per REQ-PROC-045). Compare hits against `after:`, `blocks:`, and `## Related Requirements`. Surface candidates not already cross-referenced.

2. **Classify** (user decision):
   - **Interactive mode**: present each gap to the user. User picks: hard dependency (after:), semantic relationship (Related Requirements), or ignore with reason.
   - **Automated mode**: write `cross_ref_gaps.md` to `plans_and_protocols/` listing detected gaps. Write `question.md` to `automation/pending_feedback/<TASK_ID>/`. Terminate session. Developer fills `answer.md` with classifications. Orchestrator resumes the session.

3. **Apply (always via spawned agent)**: task-derive-from-requ spawns a single agent that invokes `requ-explore` against the target requirement with the classified fixes as input. The agent reads the classifications, updates the requirement's `after:` / `blocks:` / Related Requirements section, and commits. This applies to both interactive and automated modes — the write happens in a delegated agent, not in the main session.

4. **Resume**: after the agent commits, task-derive-from-requ re-runs Phase 1 to verify gaps are resolved, then proceeds to Phase 2.

This makes the write-requirement step part of the task-derive-from-requ workflow, not a separate user action. The user (or developer in automated mode) makes the classification call; the skill performs the write via a delegated agent.

### Automated mode

When `CLAUDE_AUTOMATED_MODE=1`, task-derive-from-requ adjusts its interactive checkpoints:
- **Phase 4 (Review)**: auto-accept — plan quality is enforced by the coverage matrix gate, not user review. The plan is logged to plans_and_protocols/ for post-hoc audit.
- **Phase 5 (Create)**: always use orchestration task pattern — predictable context budget, no inline risk.
- **Escalation**: any blocking error (zero-coverage AC, missing verification task, script failure) writes `question.md` and stops.

### Orchestration task reuse

When Phase 5 persists a plan (> 6 tasks or automated mode), it creates an orchestration task using `create_orchestration_task.py` with a `--plan` flag pointing to the persisted plan file. The plan file follows the unified format (SEC-04). The orchestration infrastructure from release-begin-impl (self-perpetuating chain, ≤ 6 tasks per session, validation at chain end) is reused without modification.

### Escalation path (bottom-up)

When task-create-code's file-level analysis in Phase 5 contradicts the plan estimate:
- **Interactive mode**: ask user — "Plan estimated effort S but file analysis shows Large (8+ files). Split this task? Promote to Opus? Override?"
- **Automated mode**: write `question.md` in the task's `plans_and_protocols/` and stop (same pattern as verify-quality cycle 5 escalation).

### Verification task types

| Requirement type | Verification task |
|---|---|
| Code (lib/, test/) | Integration or widget tests confirming ACs are met; or audit task running quality gates |
| Process (AI rules, workflows) | Audit task: run relevant scripts/tools, verify outputs match AC descriptions |
| Documentation (doc/, requirements) | Review task: checklist against ACs |

### Sizing signal computation

| Signal | How computed |
|---|---|
| S1 (expected_tool_calls) | Scope file count + skill invocations x per-skill cost estimate |
| S2 (scope openness) | Closed if files/ACs named; open if scope uses patterns |
| S3 (synthesis_dependent) | True if deliverable requires holding multiple input domains |
| S4 (iterative-fix loop) | True if task touches lib/ and drives verify-quality |

## Code Task Creation (task-create-code)

`task-create-code` is the sole mechanism for creating tasks that change files in `lib/`, `test/`, or `integration_test/`. It bridges functional requirements to implementation tasks with scope analysis, sizing, and proper metadata.

**Two operating modes**:

| Mode | Trigger | Discovery | Sizing |
|---|---|---|---|
| **Plan-driven** (Phase 0A) | Pre-computed values from task-derive-from-requ or release-begin-impl plan | Skipped — plan provides ACs, package | Upstream estimates accepted as baseline; file-level analysis refines effort, layer, opus_recommended |
| **Standalone** (Phase 0B + Phase 2) | Direct invocation or zero-parameter mode | RELEASE_BACKLOG scanning, requirement resolution | Full analysis: Quick-Explore-Agent → Small/Medium/Large tiers |

In plan-driven mode, task-create-code trusts coverage and holistic concerns from the plan, but still performs file-level scope analysis to refine sizing and detect splits. If file analysis reveals a significant mismatch (plan says Small but files say Large → Split NOW), task-create-code escalates rather than silently creating a mismatched task. In standalone mode, it performs all analysis itself. Both modes produce the same goal.md format.

**Plan conformance check**: When a plan exists, task-create-code validates the created task against the plan entry (Phase 6). Mismatches in target_package, covered ACs, or layer are flagged.

**Sizing relationship with REQ-PROC-001**: task-create-code's Small/Medium/Large tiers (file count, layer count) are complementary to the S1-S4 context-budget signals. S1-S4 predict whether the executing session will overflow; Small/Medium/Large predict implementation complexity. task-derive-from-requ computes S1-S4; task-create-code computes Small/Medium/Large. Both are written to goal.md.

## Unified Plan Format

Task creation plans are the shared artifact between task-derive-from-requ and release-begin-impl Phase 2c. task-create-code consumes plans from either source through the same path (Phase 0A).

**A plan entry contains**:
- `task_name`: descriptive name for the task
- `req_path`: path to the parent requirement
- `requirements_version`: commit hash of requirements.md at plan creation time (enables stale-plan detection by task-create-code)
- `covers_acs`: list of ACs this task covers
- `effort`: T-shirt size (XS–XL)
- `layer`: affected architectural layer(s)
- `after`: dependency list (task IDs)
- `task_type`: impl, explore, verify, etc.
- `implementation_notes`: context for the implementer
- `opus_recommended`: boolean with reason
- `target_package`: release package assignment
- `wave`: `presentation` or `code` — the wave this entry belongs to (AC-18)
- `scope`: the design-unit identifier this entry belongs to (AC-18)

**Wave-tagged entries**: A plan distinguishes Presentation design-units from pure-domain design-units through the `wave`/`scope` tags. A `wave: presentation` entry is a scribble (or basis/coverage/foundation) entry; a `wave: code` entry is a coding entry. A pure-domain design-unit's entries are all `wave: code` and carry no scribble entry. A Presentation coding entry (`wave: code`, `scope` of a Presentation unit) traces to an approved scribble of its design-unit.

**Coverage matrix in the plan**: Every plan includes a coverage matrix section mapping each AC of each in-scope requirement to at least one plan entry. An AC with zero entries is a blocking error (AC-01).

**The plan is an intermediate artifact, not a permanent one.** After all tasks are created and validated (Phase 6), the plan has served its purpose. The goal.md files are the permanent record; the plan is the planning-time quality gate.

## Skill-Design Trade-off Record

A **fused-responsibility skill** is a skill that carries more than one artifact-in→artifact-out pair, or a mode flag (such as `--scope`). The artifact-in→artifact-out pairs of a skill are expressible against `.factory/registry/artifacts.yaml`, which makes the fused-vs-single distinction objectively checkable (AC-19).

Every fused-responsibility skill carries a trade-off record documenting the chosen fusion and what separating it into single-responsibility skills would have traded away. A single-responsibility skill carries only its one-sentence responsibility statement.

The `task-derive-from-requ --scope {presentation,code}` mode is a fused-responsibility skill by this rule (it carries a mode flag): it carries a trade-off record noting that the two-wave decomposition is fused into one moded skill rather than split into separate presentation-decomposer and code-decomposer skills — chosen for shared decomposition machinery and a single coverage-matrix authority, trading away the simpler single-responsibility boundary.

## Registry Routing Contract

`.factory/registry/artifacts.yaml` registers, for every plan-entry `task_type` value, the skill that consumes it (its routing contract). The set of valid `task_type` values is exactly the set registered there.

A plan-entry `task_type` that names no registered consumer skill is an unresolvable routing target: the registry routing-contract check detects and rejects it (AC-20). This closes the class of defect where a plan entry routes to a skill string that does not name an existing skill. The fused-vs-single trade-off-record trigger (the artifact-in→artifact-out pairs of AC-19) is evaluated against the same registry, so one contract governs both the routing resolution and the trade-off-record obligation.

## Developer Guidelines

### Key Decisions

- **Prefer scripts over skill instructions.** Where a step in the skill workflow can be expressed as a deterministic script invocation, it should be. Scripts produce reproducible output, consume fewer LLM tokens, and reduce the risk of an LLM applying a check inconsistently. The implementation tasks for this requirement decide per-step whether a script is feasible; the skill instructions invoke scripts where they exist and fall back to LLM reasoning only where genuinely necessary (semantic understanding, naming, scope description, classification judgment).

- **No redundant recomputation (AC-15).** Two authority patterns:

  **Compute once, trust downstream** (upstream has the best information):

  | Concern | Computed by | Downstream behavior |
  |---|---|---|
  | Coverage matrix | task-derive-from-requ / release-begin-impl Phase 2c | Trusted — not recomputed |
  | Verification task | task-derive-from-requ | Trusted — not recomputed |
  | User review | task-derive-from-requ Phase 4 / release-begin-impl Phase 5 | Plan-driven mode skips per-task confirmation |
  | Requirement reading | task-derive-from-requ Phase 1 | Plan's AC list and scope trusted |

  **Estimate upstream, refine downstream** (downstream has domain-specific detail):

  | Concern | Upstream estimate | Downstream refinement |
  |---|---|---|
  | Sizing (S1-S4) | task-derive-from-requ: from AC count, skill chain estimate | task-create-code: accepts as baseline, file analysis may reveal need to split or promote to Opus |
  | Sizing (S/M/L) | Not computed upstream | task-create-code: file count, layer detection |
  | Effort | task-derive-from-requ: rough from AC complexity | task-create-code: precise from file/layer analysis; may escalate if significantly different |
  | Dependencies | task-derive-from-requ: logical AC-level ordering | task-create-code: supplements with `requirement_then_implementation` heuristic from propose_after.py |

  When a skill runs standalone (no upstream plan), it computes everything itself.

- **Coverage matrix is blocking.** An AC with zero task coverage prevents Phase 5 from proceeding. This is deliberate — the REQ-PROC-046 and REQ-PROC-001 incidents both resulted from non-blocking coverage checks.
- **Verification is not optional.** Every decomposition includes a verification task. Omitting it requires explicit user override with documented justification.
- **Sizing is integral, not bolted on.** S1-S4 signals are computed during Phase 3, not after task creation. This means oversized tasks are split in the plan before any workspace is created.
- **Plan granularity tension.** The plan must be detailed enough to ensure coverage but not so detailed that it duplicates the work the tasks will do. Task-plan decides *what* to build and *in what order*; each task's own plan decides *how*.

### Common Pitfalls

- Creating tasks one at a time without checking overall AC coverage — this is exactly the failure mode task-derive-from-requ prevents.
- Making the plan too detailed — the plan is a task list with coverage matrix, not an implementation design. Implementation details belong in each task's plans_and_protocols/.
- Forgetting the verification task — the most common gap across both incidents.
- Creating enforcement scripts without a companion remediation task — the REQ-PROC-046 gate-without-baseline pattern.

## Related Requirements

- [REQ-PROC-009](../requirements_and_tasks/requirements.md) — Defines task structure, metadata, and coverage tracking. task-derive-from-requ builds on the coverage tracking system (trackable_items, covers field) defined there.
- [REQ-PROC-001](../../coding_standards/context_window/requirements.md) — Defines the four-signal sizing framework (S1-S4). task-derive-from-requ computes these signals for each planned task per AC-03.
- [REQ-PROC-035](../release_preparation/requirements.md) — Defines release-begin-impl including Phase 2c (task creation planning). Phase 2c owns release-level concerns; per-requirement decomposition is delegated to task-derive-from-requ (AC-14). Both produce plans in the unified format (SEC-04).
- [REQ-PROC-045](../requirements_structure_quality/requirements.md) — Structural quality of requirements. task-derive-from-requ operates on requirements that satisfy these structural rules.

## References

- `scripts/requirements/coverage_report.py` — Post-creation coverage validation (Phase 6)
- `scripts/requirements/check_ac_coverage.py` — Per-package AC coverage check
- `.claude/skills/task-create/SKILL.md` — Single-task creation primitive (wrapped by task-derive-from-requ)
- `.claude/skills/task-create-code/SKILL.md` — Dart code task creation primitive (wrapped by task-derive-from-requ)
- Incident report: `requirements_tasks/process/AI_rules/requirements_management/implementation_task_planning/tasks/2026-05-23_explore_requirement-to-task-decomposition-quality/plans_and_protocols/2026-05-23_01_incident_req-proc-046-coverage-gap.md`
- Synthesis: `requirements_tasks/process/AI_rules/requirements_management/implementation_task_planning/tasks/2026-05-23_explore_requirement-to-task-decomposition-quality/plans_and_protocols/2026-05-23_02_synthesis_decomposition_quality.md`
