# AI Software Factory — Information Flows

This document shows what types of information can be fed into the system, where each type enters the pipeline, and what path it takes through the project artifacts until it lands in the app.
Note: This document might not be 100% accurate, the skills are single point of truth. 

---

## How the User Feeds Information into the System

The user always talks to Claude Code — that is the system. Claude decides which skill to invoke.

```
Natural language:   "I found out that Persona X..."
                    "Create a new task to achieve goal Y"
                    "We are removing feature Z"

Invoke skill:       "Use product-intake skill"
                    "Use ux-write-persona skill for PERSONA-001"

Execute goal.md:    "Do requirements_tasks/.../goal.md"
                    → task-start validates + gates + marks in_progress → claude-route detects type and invokes the right skill
```

---

## Information Flow Diagram

```mermaid
flowchart TD
    %% ── INPUT TYPES ──────────────────────────────────────────────────
    subgraph INPUT["Types of Information (User Input)"]
        I_PER["👤 Persona Insight<br/>New discovery about a user:<br/>Pain Point · Mental Model · Behavior<br/>Context · Constraint"]
        I_SCN["📖 Scenario Discovery<br/>New situation or occasion<br/>when a user uses the app"]
        I_FLW["🗺️ User Flow Decision<br/>How a user navigates,<br/>what steps they take"]
        I_MKT["📊 Market Research<br/>Competitive analysis, market trends,<br/>external user feedback"]
        I_DSN["🎨 Design Decision<br/>T1/T2 design rule, sketch feedback<br/>(e.g. spacing, colors, interactions)"]
        I_TOK["🪙 Token Decision (standalone)<br/>Technical design value with no<br/>persona driver: Spacing · Color<br/>Animation · Radius"]
        I_FTR["✨ Feature Request<br/>New or changed functionality<br/>(always enters at the top)"]
        I_BUG["🐛 Bug Fix / Technical Change<br/>Something is broken, or a technical<br/>improvement with no UX cascade"]
        I_SCP["✂️ Scope Change<br/>Remove or deprioritize<br/>feature / persona / scenario"]
        I_SKL["🔧 New Skill / Workflow<br/>Extend the factory with<br/>a new automation"]
        I_VTR["⚖️ Value Trade-off Decision<br/>Conflict between persona values<br/>during design or implementation"]
    end

    %% ── ARTIFACTS (where information is stored) ──────────────────────
    P[("📋 persona.md<br/>PERSONA-xxx<br/><br/>Who are the users?<br/>Mental Models · JTBD<br/>Constraints · Anti-Traits")]
    S[("📖 scenario.md<br/>SCEN-xxx-xx<br/><br/>When & why?<br/>3-Act Structure<br/>Success Criteria")]
    FL[("🗺️ flow.md<br/>FLOW-xxx<br/><br/>How do they navigate?<br/>Happy Path + Exceptions<br/>Step by step")]
    REQ[("📐 requirements.md<br/>REQ-FUNC/NFR/PROC-xxx<br/><br/>What must the app do?<br/>Acceptance Criteria")]
    DS[("🎨 Design Rules<br/>doc/presentation/design/<br/>  t1_*.md  t2_*.md<br/>  persona_design_bridge.md")]
    SCR[("✏️ UI Scribbles<br/>[requirement-path]/scribbles/<br/><br/>Structural wireframes<br/>v1 → v2 → approved<br/>+ flutter_review/comparison.md<br/>+ APPROVAL_TRAIL.md")]
    TOK[("🪙 Token System<br/>tokens.json<br/>→ process_design_tokens.dart<br/>→ tokens.g.dart")]
    DOC[("📖 Coding Guidelines<br/>doc/architecture/<br/>doc/testing/<br/>doc/domain/<br/>doc/linter/")]
    TASK[("⚙️ Task<br/>goal.md<br/>plan.md · protocol.md")]
    VRFY[("✅ Verification Task<br/>goal.md (verification_task: true)<br/><br/>One per bundle<br/>blocked via after<br/>until bundle tasks complete")]
    CODE[("💻 Code<br/>lib/**/*.dart<br/>test/**/*.dart")]
    SELF[("🔄 Self-Improvement<br/>CLAUDE.md · Skills<br/>(affects all future flows)")]
    VTR[("⚖️ Value Trade-off Records<br/>VTR-NNN inline in:<br/>flows · requirements · design rules<br/>Aggregated: value_tradeoff_summary.md")]
    NOTES[("📝 Developer Notes<br/>notes.md (alongside flow.md)<br/><br/>Implementation intent from flow review:<br/>component prefs · arch choices · lib constraints<br/>Feeds developer intent → requirements")]

    %% ── ENTRY POINTS: Input → Artifact ───────────────────────────────

    I_PER -->|"ux-write-persona"| P

    I_SCN -->|"ux-write-scenario"| S

    I_FLW -->|"ux-create-flow"| FL

    I_MKT -->|"requ-apply-market<br/>requ-explore"| REQ
    I_MKT -. "can also add scope exclusions<br/>to Persona<br/>(requ-apply-market + ux-write-persona)" .-> P

    I_DSN -->|"ux-validate-rule:<br/>validates against personas,<br/>writes to doc/design/ if approved"| DS

    I_TOK -->|"doc-update-tokens:<br/>adds token, triggers build"| TOK

    I_FTR -->|"product-intake:<br/>Persona Gate → Scenario Gate<br/>→ Flow Gate → Requirement Gate"| P

    I_BUG -->|"task-create → code-bugfix<br/>(slim or worktree mode, no UX cascade)"| TASK

    I_SCP -->|"product-intake:<br/>Deprecation Cascade<br/>(Persona → Scenario → Flow → REQ)"| P

    I_SKL -->|"claude-create-skill / claude-modify-skill (skills)<br/>claude-create-agent / claude-modify-agent (agents)<br/>writes/edits skill.md or agents/*.md,<br/>syncs INDEX.md + factory_flows.md"| SELF

    I_VTR -->|"vcd-log-tradeoff:<br/>reads persona vcd: blocks,<br/>user decides, inserts VTR inline"| VTR

    %% VCD: record is embedded inside an existing artifact, which continues to code
    VTR -->|"decision constrains design rule<br/>→ DS continues to TOK → CODE"| DS
    VTR -->|"decision constrains requirement<br/>→ REQ continues to TASK → CODE"| REQ
    VTR -->|"decision constrains user flow<br/>→ FL continues to REQ → TASK → CODE"| FL

    %% Detection during implementation: conflict found mid-task → record before proceeding
    TASK -. "code-complex / code-simple detects<br/>value conflict mid-task<br/>→ triggers vcd-log-tradeoff" .-> VTR

    %% ── PIPELINE: Artifact → Artifact ────────────────────────────────

    P -->|"ux-write-persona cascade scan:<br/>ux-write-scenario"| S
    S -->|"ux-write-scenario cascade scan:<br/>ux-create-flow"| FL
    FL -. "ux-flow-draft Step 2b:<br/>feedback classified →<br/>impl. intent written to notes.md<br/>(alongside flow.md)" .-> NOTES
    NOTES -. "requ-derive-from-flow Phase 1.1b:<br/>matched per step ref →<br/>## Developer Intent in goal.md" .-> REQ
    FL -->|"requ-derive-from-flow<br/>(gap analysis + Opus)<br/>creates explore goal.md tasks →<br/>requ-explore writes requirements.md<br/>+ Developer Guidelines from intent"| REQ
    FL -. "requ-derive-from-flow Phase 4.5:<br/>one verification task per bundle<br/>(after all bundle explore tasks)" .-> VRFY
    VRFY -->|"requ-verify-flow-coverage<br/>(per-gap agents + Opus synthesis)<br/>quality gate: does REQ cover FL?"| REQ
    REQ -->|"task-create-code<br/>(scope estimation)"| TASK

    %% ── DESIGN SYSTEM: influences on implementation ──────────────────

    P -. "persona traits inform<br/>design decisions<br/>(persona_design_bridge.md)" .-> DS
    REQ -->|"ui-scribble-iterate<br/>(v1 → v2 → approved)"| SCR
    SCR -->|"scribble feedback classifies<br/>new T1/T2/T3 rules"| DS
    DS -->|"doc-update-tokens:<br/>design rule implies token value<br/>(e.g. min touch target → buttonMinHeight)"| TOK
    SCR -. "Scribble Gate:<br/>approved scribble read<br/>before implementation" .-> TASK
    CODE -. "ui-verify-flutter:<br/>structural check vs. scribble<br/>→ ui-improve-flutter:<br/>visual polish on real code" .-> SCR
    TOK -. "tokens.g.dart<br/>used directly in code" .-> CODE

    %% ── GUIDELINES → CODE ────────────────────────────────────────────

    DOC -. "coding agents read before<br/>every implementation<br/>(Architecture · Tests · Domain)" .-> CODE

    %% ── TASK → CODE ─────────────────────────────────────────────────

    TASK -->|"code-simple / code-complex / code-bugfix / code-test<br/>+ verify-quality (blocking) → quality-checker against doc/"| CODE

    %% ── FEEDBACK LOOPS ───────────────────────────────────────────────

    CODE -. "task-complete:<br/>status: implemented<br/>(when all tasks done)" .-> REQ

    CODE -. "doc-update-tokens:<br/>missing token discovered<br/>during implementation" .-> TOK

    TASK -. "doc-update-guidelines:<br/>learnings from protocol.md<br/>improve Coding Guidelines" .-> DOC

    TASK -. "claude-optimize<br/>(event-driven, one task per run):<br/>consumes events from .factory/optimize/<br/>→ auto-blocked improvement task" .-> SELF
```

---

## Which Information Takes Which Path

| Input | Entry point | Required path to app |
|-------|-------------|----------------------|
| Persona Insight | persona.md (via ux-write-persona) | → cascade scan (scenarios + flows) → Requirements → Task → Code |
| Scenario Discovery | scenario.md (via ux-write-scenario) | → cascade scan (flows) → Requirements → Task → Code |
| User Flow Decision | flow.md (via ux-create-flow) | → Requirements (gap analysis) → Verification Gate (requ-verify-flow-coverage) → Task → Code |
| Market Research | requirements.md | → Task → Code *(can also add persona scope exclusions)* |
| Design Decision (rule) | doc/design/*.md (via ux-validate-rule) | → Task → Code |
| UI Scribble | [requirement-path]/scribbles/ (via ui-scribble-iterate) | → Design Rules (T1/T2/T3) → (Scribble Gate) → Task → Code |
| Token Decision (standalone) | tokens.json → tokens.g.dart | → used directly in code |
| Token Decision (persona-driven) | Design Rules → tokens.json → tokens.g.dart | → used directly in code |
| Feature Request | persona.md | → Persona Gate → Scenario → Flow → Requirements → Task → Code |
| Bug Fix / Technical Change | Task (goal.md) | → code-bugfix (slim or worktree mode) → task-complete-bugfix → Code |
| Scope Change | persona.md | → Deprecation Cascade (Scenario → Flow → Requirements) |
| New Skill / Workflow | .claude/skills/ (via claude-create-skill) · .claude/agents/ (via claude-create-agent) | — extends the factory itself |
| Task Ordering Rule Change | `.claude/task_ordering_rules.yaml` (via claude-modify-ordering-rules) | — governs how `next_tasks.py` ranks open tasks; changes take effect immediately on next run |
| Value Trade-off Decision | VTR record inline in Design Rule / Requirement / Flow (via vcd-log-tradeoff) | → artifact continues its normal path: Design Rule → Token → Code; Requirement → Task → Code; Flow → Requirement → Task → Code |

---

## Release Workflow Sequence

The release workflow follows four sequential phases. Run `/release-status` at any time to see which phase you are in and the recommended next step.

| Phase | Skill | What it does |
|-------|-------|-------------|
| A — Requirements | `requ-explore` | Document requirements for the release |
| A — Requirements | `release-plan` | Assign ACs/sections to packages in RELEASE_BACKLOG.md |
| A — Requirements | `requ-derive-from-flow` | *(if needed)* Derive requirements from user flows |
| A — Requirements | `requ-assign-packages` | Bulk-assign `target_package` to unassigned ACs |
| B — Begin Implementation | `release-begin-impl` | Verify requirements ready, set release `active`, create orchestration task |
| C — Autorun | `/autorun` | Iteratively creates impl tasks per package, then executes them |
| D — Release Execution | `release` | Pre-flight → smoke test → merge/tag/push → release notes |

---

## Why This Path?

The pipeline is top-down because each layer justifies the one below it:

- **Personas** justify why scenarios exist
- **Scenarios** justify why user flows are designed the way they are
- **User Flows** reveal which features the app needs → Requirements
- **Requirements** define what must be implemented → Task
- **UI Scribbles** are the structural wireframes that bridge requirements and design rules — approved scribbles gate implementation and can trigger new T1/T2/T3 rules
- **Design Rules** ensure all UI changes are persona-aligned and consistent — and can prescribe concrete values that become tokens (e.g. a motor constraint → minimum touch target → `buttonMinHeight` token)
- **Code** is the end product of all decisions above

Feedback loops keep the system current:
- **Implementation → Guidelines**: Learnings from tasks improve `doc/` for future implementations
- **Sketch Feedback → Design Rules**: New visual decisions are anchored as T1/T2 rules in DS
- **Task-Complete → Requirements**: Status propagation keeps the overview accurate
- **Code → Tokens**: Missing tokens discovered during implementation are added immediately
- **claude-optimize → System**: Event-driven producer — at most one auto-blocked improvement task per run (or a documented no-op). The developer must unblock before any executor picks it up (G-INV-1).
- **claude-create-skill → System**: The user can extend the factory with new automations at any time
- **Verification Gate → Requirements**: After each bundle of exploration tasks completes, the verification task unblocks automatically. `requ-verify-flow-coverage` checks whether the written requirements actually cover the flow gaps — confirmed gaps are remediated, intentional deviations are documented, unresolved conflicts are parked as decisions. This closes the loop between flows and requirements before implementation begins.
- **Task Ordering Rules → Task Queue**: `.claude/task_ordering_rules.yaml` defines how `next_tasks.py` ranks open tasks — layer order, priority boosts, and explicit overrides. Edit via `claude-modify-ordering-rules`; validate with `scripts/task_ordering/validate_rules.py`. `scripts/propose_after.py` suggests `after:` dependencies for new tasks.
- **vcd-log-tradeoff → VTR Records**: When persona values conflict, the decision is documented inline in the artifact where the conflict arose. That artifact then continues its normal path to code — so the decision always reaches the app. The VTR-NNN ID makes it traceable (WHY comments in code can reference it).
