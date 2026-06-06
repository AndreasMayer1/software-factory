# Synthesis: Requirement-to-Task Decomposition Quality

Date: 2026-05-23
Session: TASK-PROC-058-01 (Opus)

## 1. The Problem — Stated from Evidence

Two independent incidents demonstrate the same failure pattern:

**REQ-PROC-046** (Code Quality Gates): 13 ACs, 14+ tasks created. AC-03 and AC-06
had zero task coverage. ~160 pre-existing violations from new gate scripts were
never addressed. No verification task existed. The requirement was treated as
"mostly done" while structural gaps remained invisible. Full incident report:
`plans_and_protocols/2026-05-23_01_incident_req-proc-046-coverage-gap.md`.

**REQ-PROC-001** (Context Window): 8 ACs, 7 pending tasks. AC-04 (open-scope
fan-out plan) and AC-07 (iterative-fix Opus default) have zero task coverage.
No verification task exists. Discovered during this session's sanity check.

Both share the same root cause: tasks were created one at a time, ad hoc, with
no holistic view of the requirement's AC set. Coverage was never validated
at decomposition time — only discoverable after the fact via `coverage_report.py`,
which nobody ran.

## 2. Current Landscape

### Skill inventory (task creation paths)

| Skill | What it does | Coverage check? | Sizing check? |
|---|---|---|---|
| `task-create` | Generic task workspace. Classification, ID, metadata. | Case B: reads requirement to check "task fits" — single-task view. No AC coverage matrix. | Opus recommendation heuristics only. |
| `task-create-code` | Dart code tasks (lib/test/integration_test). | Same as task-create. No multi-task coverage view. | Quick-Explore-Agent file estimate + Small/Medium/Large tiers. |
| `requ-explore` | Writes requirements. Does NOT create tasks. | N/A — output is requirements, not tasks. | N/A |
| `requ-derive-from-flow` | Flow → requirement gaps → goal.md files. | Coverage at flow level, not at AC level. | N/A |
| `release-begin-impl` Phase 2c | Release-scope task plan. Creates `task_creation_plan.md`. | Checks requirement completeness and scope. Does NOT produce per-requirement AC coverage matrix. | Creates orchestration tasks; sizing implicit in plan structure. |
| `product-intake` | Routes changes through persona → scenario → flow → requirement. | Upstream of task creation entirely. | N/A |

### Existing coverage tooling

| Script | What it does | When it runs |
|---|---|---|
| `scripts/requirements/coverage_report.py` | Post-hoc AC → task coverage report. | On demand. Never mandatory. |
| `scripts/requirements/check_ac_coverage.py` | Per-package AC coverage check. | During release workflows. |
| `scripts/requirements/validate_meta.py` | Validates YAML frontmatter. | On demand. |

### The gap

Between "requirement exists" and "tasks exist" there is no mandatory, holistic
quality gate. Individual tasks are created with a single-task view (does this task
map to some ACs?), but the question "do ALL ACs have at least one task?" is never
asked during creation. It is only answerable after the fact, and nobody asks it.

## 3. Workflow Inventory

Five distinct paths lead to "I need tasks for this requirement":

| # | Path | Frequency | Error-prone? | Why |
|---|---|---|---|---|
| W1 | requ-explore finishes → user wants tasks in same session | High | Medium | Context is rich but AC coverage is not checked. User typically creates tasks one by one. |
| W2 | Existing requirement → gap discovered → ad-hoc task creation | High | High | Most error-prone. No holistic view. Developer creates 1-2 tasks for the immediate gap, missing others. |
| W3 | Dedicated explore task to decompose a requirement into tasks | Medium | Medium | Purpose-built for this, but no structured quality gate on the output. |
| W4 | release-begin-impl Phase 2c → task_creation_plan.md | Low (per-release) | Low | Most structured path. Plan agent sees all requirements at once. But no per-requirement AC coverage matrix. |
| W5 | product-intake → requirement that needs decomposition | Low | High | Indirect. product-intake creates/updates the requirement but doesn't create tasks. |

## 4. Design Decision: `task-derive-from-requ` Skill

**User decision**: The decomposition quality skill wraps `task-create` (confirmed
2026-05-23). This means a new skill — not an extension of task-create.

**Skill name**: `task-derive-from-requ`

**Why a new skill**:
- task-create handles single-task creation — it's a primitive. Adding multi-task
  decomposition planning to it would conflate two concerns.
- task-create-code split off for Dart-specific concerns — same pattern applies here.
- The new skill needs to see ALL ACs at once, produce a coverage matrix, and then
  call task-create/task-create-code for each task. This is orchestration, not creation.

**What it wraps**:
- `task-create` for non-code tasks (process, doc, skill, script, explore, define)
- `task-create-code` for Dart code tasks (lib/, test/, integration_test/)
- The choice is automatic based on task scope analysis.

## 5. Skill Design

### Phases

**Phase 1 — Gather**
- Read the requirement's requirements.md (all ACs, sections, behavior)
- Read existing tasks (if any) — compute current coverage
- Read related/blocking requirements (after: / blocks: chains)
- Identify: which ACs need tasks? What exists already?

**Phase 2 — Analyze**
- Group ACs by logical implementation unit (which ACs belong together?)
- Identify cross-cutting concerns (ACs that touch multiple areas)
- Determine task types per group:
  - Code tasks (lib/test/integration_test) → will use task-create-code
  - Process/doc/skill tasks → will use task-create
  - Explore tasks → for ACs with high uncertainty
  - Verification task → mandatory
- Identify enforcement-creates-violations pattern:
  - If a task creates new scripts/gates/rules that will find violations
    → propose a companion remediation task

**Phase 3 — Plan**
- For each task in the plan:
  - Name, type, ACs covered, scope description
  - Sizing signals (from REQ-PROC-001):
    - S1: expected_tool_calls estimate
    - S2: scope openness (closed/open)
    - S3: synthesis_dependent (true/false)
    - S4: iterative-fix loop (true/false — does it touch lib/ with verify-quality?)
  - opus_recommended: derived from S1-S4 composition
  - Dependencies (after: chains between tasks)
- Produce coverage matrix: AC → task(s) mapping
- Verify: 100% AC coverage (hard gate), verification task present

**Phase 4 — Review**
- Present the plan + coverage matrix to user
- User can: approve, modify tasks, split/merge, reject
- No task is created until user approves

**Phase 5 — Create**
- For each approved task:
  - If code task → invoke task-create-code
  - If non-code task → invoke task-create
- Pass sizing metadata, coverage info, dependencies

**Phase 6 — Validate**
- Run coverage_report.py on the requirement
- Confirm 100% AC coverage post-creation
- Print final coverage matrix

### Mandatory outputs

1. **Coverage matrix** — every AC mapped to at least one task. Zero-coverage ACs
   are a hard error that blocks Phase 5.
2. **Verification task** — at least one task that verifies the requirement is met
   end-to-end after all impl tasks complete. Type depends on requirement type:
   - Code requirements: test task (integration or widget tests)
   - Process requirements: audit task (run scripts, check outcomes)
   - Documentation requirements: review task
3. **Dependency graph** — tasks ordered by after: chains. No circular dependencies.

### Enforcement-creates-violations detection

When a task's scope includes "create script", "add gate", "implement checker",
"new lint rule", or similar → the skill automatically proposes a companion task:
"Fix pre-existing violations detected by [new gate]". This prevents the REQ-PROC-046
pattern where gate scripts were created without baseline cleanup.

The companion task has:
- `after: [the gate-creation task]` (can't fix violations before the gate exists)
- Same ACs as the gate-creation task (both serve the same requirement)
- Explicit scope: "run [gate script], fix all violations, confirm zero output"

## 6. Integration with Existing Workflows

### W1 (requ-explore → tasks): Recommended path

After requ-explore completes, the user (or automation) invokes task-derive-from-requ on the
newly written requirement. task-derive-from-requ reads the fresh requirements.md and produces
a holistic decomposition.

**Not mandatory in requ-explore itself**: requ-explore's job is to write the
requirement. Forcing decomposition in the same session risks context blowup
(REQ-PROC-001 concern). The decomposition happens in a separate invocation.

### W2 (existing requirement → ad-hoc task): Guard

When a user invokes task-create directly for a requirement that has uncovered ACs,
task-create should warn: "This requirement has N uncovered ACs. Consider running
task-derive-from-requ for a holistic decomposition before creating individual tasks."

This is a warning, not a block. Individual task creation remains valid for targeted
gap-filling.

### W3 (dedicated explore task): Natural fit

An explore task whose goal is to decompose a requirement into tasks is exactly
what task-derive-from-requ does. claude-route should detect this goal shape and invoke task-derive-from-requ.

### W4 (release-begin-impl): Future integration

release-begin-impl Phase 2c currently creates a monolithic task_creation_plan.md.
A future evolution could have Phase 2c call task-derive-from-requ per requirement. This is an
integration point, not a blocker for the initial implementation.

### W5 (product-intake): Downstream

product-intake creates/updates requirements. After it completes, the user invokes
task-derive-from-requ on the affected requirements. No integration change needed.

## 7. REQ-PROC-001 Sizing Integration

Each task in the plan carries sizing signals per the four-signal framework:

| Signal | How task-derive-from-requ computes it |
|---|---|
| S1 (expected_tool_calls) | Estimate from scope: count of files + skill invocations × per-skill cost (requ-explore ≈ 20, task-resolve ≈ 15, verify-quality cycle ≈ 10) |
| S2 (scope openness) | Closed if task scope names specific files/ACs. Open if scope uses patterns ("all types matching...", "every feature under...") |
| S3 (synthesis_dependent) | True if task deliverable requires holding multiple input domains simultaneously. Flagged by task-derive-from-requ based on AC grouping. |
| S4 (iterative-fix loop) | True if task touches lib/ and drives verify-quality. Automatic for impl tasks targeting lib/. |

Composition → opus_recommended:
- S1 > 60 OR (S1 > 30 AND S4 true) → opus or split
- S2 open without fan-out plan → require fan-out plan
- S3 true → opus, monolithic
- S4 true with > 3 files → opus

## 8. Test Cases: Validation Against Incidents

### REQ-PROC-046 (would task-derive-from-requ have caught the gaps?)

| Gap | Would task-derive-from-requ catch it? | How? |
|---|---|---|
| AC-03 zero coverage | YES | Coverage matrix would flag AC-03 as uncovered. Hard error. |
| AC-06 zero coverage | YES | Same — coverage matrix. |
| ~160 violations from new gates | YES | Enforcement-creates-violations detection would propose remediation task. |
| No verification task | YES | Mandatory verification task in every decomposition. |
| Gate scripts without tests | PARTIAL | Verification task would test the gates, but may not specifically test the scripts themselves. A more specific detection ("task creates scripts → propose test task") could catch this. |

### REQ-PROC-001 (would task-derive-from-requ have caught the gaps?)

| Gap | Would task-derive-from-requ catch it? | How? |
|---|---|---|
| AC-04 zero coverage | YES | Coverage matrix. |
| AC-07 zero coverage | YES | Coverage matrix. |
| No verification task | YES | Mandatory verification task. |
| Sizing signals not applied to tasks | YES | Each task would get S1-S4 computed during Phase 3. |

Score: both incidents fully caught except one partial (gate script testing).

## 9. Design Decisions Made During Review (2026-05-23)

1. **task-derive-from-requ is mandatory** when requirement has `trackable_items.acceptance_criteria`.
   Two modes prevent friction: quick mode (1-2 tasks, coverage check only) and
   full mode (complete decomposition). Mode selection is automatic.

2. **task-create-code is brought under REQ-PROC-058.** It previously had no
   dedicated requirement. Its behavior (scope analysis, plan-driven mode, plan
   conformance) is now governed by this requirement alongside task-derive-from-requ.

3. **Unified plan format.** task-derive-from-requ and release-begin-impl Phase 2c produce
   plans in the same format. task-create-code consumes them through the same
   Phase 0A path. This means release-begin-impl's existing plan infrastructure
   is reusable.

4. **release-begin-impl Phase 2c** gains per-requirement coverage matrices
   (AC-14). This is a new quality gate on the release flow — the plan must show
   100% AC coverage per requirement before the user gate.

5. **task-create redirects** to task-derive-from-requ when invoked on a requirement with
   uncovered ACs. Not a warning — a redirect. task-create remains independent
   only for tasks without a parent requirement or requirements without ACs.

6. **No duplicated computation (AC-15).** Each quality concern (coverage, sizing,
   dependencies, user review) is computed once, at the level with the right
   information. Downstream skills trust upstream results. Concretely: when
   task-derive-from-requ has computed coverage + sizing + dependencies, task-create-code
   accepts those values and does not recompute. When task-create-code runs
   standalone, it does its own analysis. The duplication rule only applies
   when an upstream skill has already done the work.

## 10. What Remains Uncertain

1. **How deep should the analysis go?** Phase 2 (Analyze) could be shallow
   ("group ACs, assign task types") or deep ("read related requirements, analyze
   code impact, estimate effort"). Deeper analysis produces better plans but
   consumes more context. The REQ-PROC-001 S3 signal applies to task-derive-from-requ itself.

2. **Interaction with release-begin-impl Phase 2c**: Phase 2c currently creates
   a monolithic plan. Future evolution: Phase 2c calls task-derive-from-requ per requirement.
   The unified plan format (SEC-04) makes this mechanically possible. The question
   is whether it's worth the refactoring effort now or later.

3. **task-create-code standalone mode**: When task-create-code is invoked directly
   (not via task-derive-from-requ), it runs its own scope analysis. Should this mode warn
   about coverage gaps the way task-create does? Probably yes — same AC-10 logic.

4. **REQ-PROC-001 test case**: REQ-PROC-001 has AC-04 and AC-07 with zero task
   coverage and no verification task. Re-planning it through task-derive-from-requ is a
   confirmed test case for the initial implementation.

5. **REQ-PROC-035 impact**: REQ-PROC-035 SEC-05 (Task Creation Process) and
   SEC-06 (release-begin-impl Integration) describe Phase 2c as a monolithic
   planner that does its own per-requirement analysis. AC-14 of REQ-PROC-058
   changes this: Phase 2c delegates per-requirement decomposition to task-derive-from-requ.
   REQ-PROC-035 needs a corresponding update to SEC-05/SEC-06 to reflect this
   delegation. This is a separate requ-explore invocation, not part of this
   explore task. REQ-PROC-058 `blocks: [REQ-PROC-035]` to track this dependency.

6. **REQ-PROC-045 impact**: REQ-PROC-058 AC-17 references REQ-PROC-045 as the
   owner of the keyword-grep detection mechanism for cross-reference completeness.
   REQ-PROC-045 today does not own this mechanism — it covers structural
   conformance (folders, IDs). REQ-PROC-045 needs a new AC for the keyword-grep
   detection mechanism that AC-17 invokes. REQ-PROC-058 `blocks: [REQ-PROC-045]`
   to track this dependency.

4. **Task-create-code integration depth**: task-create-code has its own sizing
   logic (Quick-Explore-Agent, Small/Medium/Large). Should task-derive-from-requ's sizing
   override or complement? Currently: complement (task-derive-from-requ sets S1-S4, task-create-code
   adds file-level analysis).

5. **The "mostly done" problem**: When a requirement is partially decomposed
   (some tasks exist, some ACs uncovered), should task-derive-from-requ handle incremental
   decomposition? Yes — Phase 1 reads existing tasks and Phase 3 only plans
   tasks for uncovered ACs. But the coverage matrix still shows the full picture.
