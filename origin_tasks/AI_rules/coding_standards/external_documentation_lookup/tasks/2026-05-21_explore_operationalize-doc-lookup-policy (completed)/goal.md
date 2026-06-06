---
task_id: TASK-PROC-053-02
type: explore
parent_requirement: REQ-PROC-053
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
effort: L
created: 2026-05-21
started: 2026-05-26
completed: 2026-05-26
session_completed_at: 2026-05-25T23:52:48Z
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Synthesize operational design for REQ-PROC-053 — agent-scope decisions, context7 integration mechanism, task-scope lookup log, per-technology trigger thresholds. Output is a design document; skill amendments and context7 wiring are follow-up impl tasks."
release_description: ""
opus_recommended: true   # reason: cross-cutting architectural exploration spanning every code-producing skill, web research, explicit coverage-vs-cost trade-off analysis
writes_requirements: false
requirements_version:
  commit: db92ca63
  file: ../../requirements.md
session_id: ef9d1f24-6928-43e5-b204-65354f415cc6
session_account: web
---
# Goal — Operationalize REQ-PROC-053 Documentation-Lookup Policy

## Objective

REQ-PROC-053 (committed `db92ca63`) fixes the policy:
technology-agnostic, `context7`-preferred, default-consult unless
external-evidence skips, exactly-one-checkpoint-per-authoring-chain,
tests in scope, pinned-version anchored. What it deliberately does
*not* fix is the **operational machinery** that turns each AC into
agent-executed behavior. That machinery is this task's problem space.

Open at task creation — frame each as a question the exploration must
answer well enough that a follow-up impl task can act on the answer:

- Which skills and spawned agents carry the AC-07 checkpoint, and at
  *exactly which step* in their workflow does it fire?
- What per-technology trigger calibration makes sense — Flutter widgets
  vs. `dart:core` vs. Python `pathlib` vs. native build files vs.
  GitHub Actions vs. configuration schemas?
- How is `context7` integrated mechanically (MCP server? CLI proxy?
  embedded HTTP? prompt convention?) given the devcontainer + Windows
  command bridge environment?
- What is the *task-scope lookup log* — file location, format, fields,
  dedup semantics across the skill / spawned-agent boundary, cache
  invalidation within a task?
- How does the gate-failure → lookup edge (Developer Guidelines
  paragraph) actually plug into `verify-quality` / `quality-checker`,
  and how does it shorten the cycle-count toward REQ-PROC-046's
  five-cycle bound's *floor*?
- What lookup budget is reasonable under REQ-PROC-001's per-task
  context-window framework, and what happens when the budget caps?
- How do existing LLM coding tools (Aider, Cursor, Cline, Continue,
  Copilot Workspace, …) handle the same trigger problem — and what
  should we steal or avoid?

## Background

REQ-PROC-053 was authored in TASK-PROC-053-01 (2026-05-21, commit
`db92ca63`) as the preventive counterpart to REQ-PROC-046 §6. The user
explicitly named several pieces of this task during the requirement
authoring session:

- *"Which agents/skills must comply"* is exploration / brainstorming
  territory, not a thing to pre-decide.
- *"LLMs hallucinate and are usually quite confident and do not know
  what they don't know"* — the AC-02 framing already pivots to
  external evidence, but the **evidence-checking machinery** (in
  particular AC-02 (a)'s toolchain-clean verification) is not designed.
- *"We need to make sure that the lookup is not done twice, for
  example once in the skill, then again in the agent"* — AC-07 fixed
  the property (exactly one checkpoint per chain) and named a
  *task-scope lookup log* (AC-02 (b)) as the mechanism, but the log
  itself is undesigned.
- *"Maybe we can do a web search in an agent. it's possible that
  other people already have a solution"* — prior-art research is part
  of this exploration, not optional.
- The user is creating a *separate* task in a *separate* session for
  the dependency-update mechanism (interaction point: AC-05). This
  exploration must **not** design it; it MAY identify the seam.

The user's unedited initial thinking that prompted this task is
preserved in:
`plans_and_protocols/2026-05-21_00_user_initial_input.md`

Read it as a seed bed, not a spec.

For complete requirements at task creation time:
```
git show db92ca63:requirements_tasks/process/AI_rules/coding_standards/external_documentation_lookup/requirements.md
```

Current requirements: `../../requirements.md`.

## Developer Intent

- **[PREFERENCE]** Start the exploration with **prior-art research
  delegated to a `general-purpose` agent** — never run `WebSearch` /
  `WebFetch` inline. The user explicitly named this as the first move.
  *Source: user message 2026-05-21 ("maybe we can do a web search in an
  agent. it's possible that other people already have a solution").*
- **[CONSTRAINT]** Must NOT change REQ-PROC-053's acceptance criteria.
  If a finding suggests a *policy* change rather than an operational
  refinement, surface it to the user as a separate question. Do not
  silently edit the requirement. *Source: REQ-PROC-053 stability —
  the requirement is `status: active` and is the contract.*
- **[CONSTRAINT]** Must NOT design the **dependency-update mechanism**.
  The user has flagged that as a separate task in a separate session.
  This exploration MAY identify the **interaction seam** (what
  REQ-PROC-053 operationalization needs to assume about the upgrade
  flow so the two designs compose cleanly) but no more. *Source: user
  message 2026-05-21.*
- **[PREFERENCE]** Synthesis-as-output: the deliverable is a **design
  document**, not skill edits, not a context7 integration. Follow-up
  impl tasks are derived from the synthesis. *Source: sibling
  REQ-PROC-046 exploration model (TASK-PROC-046-01, -02); explore-task
  pattern.*

## How to Approach This

Use design thinking as the guiding process — empathize before
defining, diverge before converging, let questions lead, iterate. A
single pass through the material will not be enough. Surface
surprises; the most valuable findings here are the trade-offs the
user did not anticipate (lookup cost during long iterative cycles,
freshness mismatch between `context7` and the version pinned in
`pubspec.lock`, what happens for technologies `context7` does NOT
index, how the per-skill checkpoint composes with the spawned-agent
boundary, etc.).

Order suggestion (not prescription):

1. **Prior art first** (seed 1). Spawn a `general-purpose` agent
   focused on how Aider / Cursor / Cline / Continue / Copilot
   Workspace / Claude Dev handle the documentation-lookup-trigger
   problem. Then a second `general-purpose` agent on `context7`
   internals (seed 3). Let the findings shape the design space before
   committing to a structure.
2. **Codebase reconnaissance**. Read the existing code-producing
   skills (`code-simple`, `code-complex`, `code-test`, `code-bugfix`)
   and the spawned-agent definitions (`implementation-engineer`,
   `test-engineer`, `architecture-advisor`, `quality-checker`). Map
   each authoring chain so the checkpoint placement decisions are
   grounded in actual workflow shapes.
3. **Synthesize iteratively**. Each round MAY surface decisions
   requiring user input — collect them in a `Decisions` section in
   the design doc rather than asking ad-hoc.
4. **Stop before implementation**. The deliverable is design; the
   skill amendments and the `context7` wiring land in follow-up impl
   tasks the design names.

## Seeds

1. **Prior art via web search.** How do Aider, Cursor, GitHub Copilot
   Workspace, Cline, Continue.dev, Claude Dev/Cline, and other LLM
   coding tools handle upstream-documentation lookup? Specifically:
   trigger heuristics (when do they fire?), channel preference (do any
   use `context7` or analogues?), cost-control mechanisms ("not too
   often"), cache / dedup strategies, integration with deprecation
   warnings. Findings inform — but do not constrain — the design.

2. **Agent scope.** Make the list of code-producing skills /
   agents **exhaustive** (not just the AC-07 enumeration). Identify
   spawned-vs-direct authoring chains. For each chain, propose where
   the *single* checkpoint lives (the skill, the spawned agent, or
   the skill records-only / the agent fires) with explicit reasoning.
   This is the brainstorm the user named at task creation.

3. **`context7` integration mechanism.** Read the `context7` overview
   (https://context7.com/docs/overview) and follow links. What
   integration paths exist (MCP server? CLI proxy? embedded HTTP
   client? prompt convention?). What does our environment support
   natively (devcontainer + Windows command bridge)? What's the
   lowest-friction integration that respects AC-03's channel
   preference and survives offline / degraded states?

4. **Per-technology trigger thresholds.** Concretely: when does the
   default lookup fire for a Flutter widget call vs. a `dart:core`
   call vs. a Python `pathlib` call vs. a GitHub Actions step vs. a
   shell script call? Each has a different rate of churn; what
   calibration is reasonable? Don't over-tune — propose ranges.
   Output: a per-technology table.

5. **Task-scope lookup log format.** AC-07 + AC-02 (b) rely on a
   shared log so skill-level lookups dedupe with agent-level
   checkpoints. Where does it live (`plans_and_protocols/lookup_log.md`?
   a JSON file? frontmatter-tagged?), what fields does it carry
   (technology, API surface, pinned version, source URL, timestamp,
   `context7` query ID, …), how is cache invalidation handled within
   a task, how do parallel agents in the same task avoid races?

6. **AC-02 (a) toolchain-clean verification.** When the checkpoint
   sees an existing in-repo call site, how does it verify the
   "toolchain currently passes clean at the pinned version" claim?
   Fresh `flutter analyze` on the file each time (expensive)? Trust
   the most-recent CI signal (stale)? Cache analyzer output per
   file-mtime? What's the implementation cost vs. the false-skip
   risk?

7. **Interaction with REQ-PROC-046 five-cycle bound.** When a gate
   failure surfaces an API-contract mismatch (deprecation, unknown
   symbol, signature change), REQ-PROC-053 Developer Guidelines says
   the next revision cycle's first move is a documentation lookup.
   How does this concretely change `verify-quality` /
   `quality-checker`? How does it shorten the typical cycle count
   toward the bound's floor rather than its ceiling?

8. **Interaction with REQ-PROC-001 context-window budget.** Lookups
   consume context. AC-04's anti-reflex bounds frequency, but each
   individual lookup still costs tokens. What's the per-task lookup
   budget under REQ-PROC-001's framework? When does the budget cap
   force escalation (e.g. via `pending_feedback`) rather than another
   lookup?

9. **Test-framework calibration (AC-06).** Enumerate the
   test-framework API surfaces in this project — `package:flutter_test`,
   `package:test`, `package:integration_test`, `package:glados`,
   `package:mutation_test`, `pytest` — and classify which specific
   call patterns within each are *high-risk* (`pumpAndSettle` timing,
   `Generator.combine` shrinking, parametrize-fixture composition) vs.
   *low-risk* (vanilla `expect`, simple finders). Output: a small
   classification table.

10. **Dependency-upgrade seam (interface required; design out of
    scope).** The user is creating a separate task in a separate
    session for the dependency-update mechanism. Identify the
    interface — what does REQ-PROC-053's operationalization need to
    *assume* about dependency-upgrade behavior so the two designs
    compose cleanly without one of them being rewritten when the
    other lands? E.g. when AC-05 directs a direct switch to a
    replacement at the pinned version vs. a TODO for a future
    version, what hook does the upgrade mechanism need at that point?

## Execution Model

Gather raw material — read sibling skills, the existing `doc/`
guidelines, the requirement itself at `db92ca63` — then synthesize
iteratively. Multiple gathering rounds may be needed before the
problem space is well understood.

The session's model is fixed at launch (`opus_recommended: true` —
Opus, for the cross-cutting trade-off analysis between coverage and
context cost spanning every code-producing skill). No mid-session
model switching.

**Web research**: For seeds 1 and 3 (and any other seed where external
knowledge is needed), spawn a `general-purpose` agent. Frame queries
as questions, not keyword bags: *"how does Aider decide when to look
up upstream documentation?"*, *"what integration paths does context7
expose for a devcontainer-hosted CLI agent?"*. Never run `WebSearch`
or `WebFetch` inline — raw web content inflates context fast.
Instruct the subagent to use `WebFetch` to read full pages when a
snippet is insufficient; the subagent returns a distilled summary.

**Cache rule for THIS task itself**: when this task reads upstream
documentation in the course of its own design work (e.g. reading
`context7` docs to design the integration), record the read in
`plans_and_protocols/lookup_notes.md` so the same source is not
re-fetched mid-task. This is the task's own dogfooding of the
mechanism it's designing.

## Output

A synthesis document at
`plans_and_protocols/[YYYY-MM-DD]_NN_synthesis_design.md` that:

- **Names which skills / agents carry the checkpoint** and at exactly
  which step in each (one row per authoring chain).
- **Specifies the task-scope lookup-log format** — file path, fields,
  schema, dedup mechanism, cache invalidation rule.
- **Proposes the `context7` integration mechanism** with rationale
  vs. each rejected alternative (MCP / CLI proxy / HTTP / prompt
  convention).
- **Tables per-technology trigger thresholds** — Flutter, Dart core,
  third-party Dart packages, Python stdlib, Python third-party, native
  build files, shell, configuration files. Ranges, not exact
  numbers — with the rationale behind each range.
- **Tables per-test-framework call-pattern risk classification**
  (AC-06 operationalization).
- **Enumerates decisions deferred to the user** — open questions the
  exploration could not resolve, framed so the user can decide.
- **Identifies the dependency-upgrade interface seam** — what
  REQ-PROC-053 operationalization needs from the future
  dependency-update mechanism, and vice versa.
- **Lists the follow-up impl tasks the design implies** with proposed
  task IDs (e.g. *"TASK-PROC-053-03: amend code-simple with lookup
  checkpoint"*, *"TASK-PROC-053-04: integrate context7"*). Do NOT
  pre-create those task folders — the user will decide whether to
  spawn them after reviewing the synthesis.

The output is **design, not implementation**. No skill files are
edited in this task; no `context7` integration code is written.

## Acceptance Criteria

- [x] Exploration produced at least one synthesis round before any
      output is presented to the user.
- [x] The synthesis defines the operational problem space in terms
      that were not fully spelled out at task creation — especially
      the per-skill checkpoint placement, the task-scope lookup-log
      schema, and the per-technology trigger calibration.
- [x] Decisions requiring user input are identified and framed
      clearly enough for the user to decide (collected in a
      `Decisions` section, not asked ad-hoc).
- [x] The output is honest about what remains uncertain — explicitly
      including `context7` coverage gaps, environment-integration
      friction, AC-02 (a) toolchain-clean verification cost, and the
      dependency-upgrade-mechanism seam (acknowledged but not
      designed).

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-053-01 | completed | Authored REQ-PROC-053 (commit `db92ca63`). |
| —          | —      | No other blocking dependencies. The user's separate dependency-update task is *not* a blocker — this exploration acknowledges the seam without designing the upgrade flow. |

## Notes

- Sibling exploration model: REQ-PROC-046's exploration tasks
  (TASK-PROC-046-01, -02) are the structural precedent for this kind
  of design synthesis.
- Process category: `target_package` is intentionally absent.
- After this task lands, the user expects a small fan-out of follow-up
  impl tasks — one per amended skill, plus one for `context7`
  integration. **Do NOT pre-create those.** The exploration's
  synthesis names them; the user decides which to spawn and when.
- The session that runs this task SHOULD be a fresh session — the
  authoring session for REQ-PROC-053 already covered substantial
  ground (parallel-session staging, quality-gate bypass) and clean
  context is the right starting point.
