---
id: REQ-PROC-055
status: active
urgency: 2
urgency_reason: "U2-OPP: An attractive external plugin (han) prompted the need, but no governed method exists to evaluate or adopt external Claude Code tooling — the opportunity is real but not time-critical"
impact: 4
impact_reason: "I4-ENAB: A reusable evaluation-and-adoption method lets the factory absorb good ideas from any external plugin without risking its established workflows; absence means every evaluation is ad-hoc and re-derives methodology"
effort: ongoing
stakeholder: app_provider
created: 2026-05-26
updated: 2026-05-26
personas_served: [PERSONA-015]
after: []
blocks: []
market_research_refs: [] # No relevant findings identified — pure internal process requirement
trackable_items:
  sections:
    - id: SEC-01
      name: "User Story"
      heading: "## User Story"
    - id: SEC-02
      name: "Purpose"
      heading: "## Purpose"
    - id: SEC-03
      name: "Evaluation Framework"
      heading: "## Evaluation Framework"
    - id: SEC-04
      name: "Outcome Requirements"
      heading: "## Outcome Requirements"
    - id: SEC-05
      name: "Scope Boundaries"
      heading: "## Scope Boundaries"
    - id: SEC-06
      name: "References"
      heading: "## References"
---

# External Tooling & Plugin Adoption

## User Story

As the App Provider (PERSONA-015) — a solo creator who must ship a high-quality app and keep maintaining it sustainably for years — I want a safe, low-effort way to fold *proven* external ideas into the factory, so that the factory keeps improving its outcomes (dev & app security, code quality, maintainability, performance, UX, testing) without coupling to unproven upstreams or forcing costly re-testing of established workflows.

## Purpose

This requirement is a **means, not an end**. The end is the factory's purpose — maximising app-outcome quality per unit of sustainable solo effort and risk, grounded in PERSONA-015's "minimum effective dose" and "longevity over velocity" values. The *outcome dimensions themselves* are owned by other requirements (see Where "Good Outcomes" Live below); this requirement does not redefine them. It governs only **one input channel** into the factory's continuous improvement: external Claude Code tooling (plugins, skills, agents, patterns).

The factory is a self-modifying system, and the wider Claude Code ecosystem now produces plugins that may encode ideas worth absorbing. Without a governed on-ramp, every evaluation re-derives its own comparison approach, overlap is missed, and adoption decisions are made without weighing maintenance cost, upstream churn, licensing, or the risk of re-testing established workflows — directly threatening the solo-maintainer sustainability constraint.

This requirement was triggered by the evaluation of the **han** plugin (github.com/testdouble/han, MIT, Test Double) in TASK-PROC-055-01. That evaluation surfaced the deeper need: a *reusable* framework plus a *standing policy*, so the han decision and all future plugin evaluations rest on the same foundation. This requirement governs the **method and policy**, not any one plugin's verdict (the han verdict lives in that task's synthesis report).

## Evaluation Framework

Any external-tooling evaluation follows this method. It is the reusable asset; a verdict produced without it is incomplete.

**Method (in order):** (1) inventory both sides; (2) normalize both into the shared capability taxonomy so missing whole categories are detectable; (3) map each external component to its nearest internal equivalent and classify overlap (none / partial / full); (4) score each component on the axes below; (5) flag external gaps we feel and philosophy conflicts; (6) roll up to an adoption-level recommendation per component. Gathering of external material is delegated to subagents that return distilled summaries, to protect the synthesiser's context.

**Capability taxonomy** (compare like-with-like): A Planning · B Review & critique · C Investigation & research · D Implementation · E Documentation & comms · F Specialist analysis lenses · G Governance / quality gates · H Process orchestration · I Product / user-needs modeling.

**Scoring axes** (per external component): Overlap (none/partial/full) · Gap-fill value (none/low/med/high) · Philosophy fit (conflict/neutral/aligned with our stateful, gate-enforced, pipeline-first model) · Self-containment (does it drag dependencies — other agents, external CLIs, file layouts) · Adaptation cost (S/M/L) · Re-test risk (none/low/med/high) · Attribution burden (none/notice/per-file).

**Adoption levels:** *Full* (replace ours) · *Selective* (copy + adapt + freeze) · *Inspirational* (port the idea into our own component) · *None*.

**Decision heuristics:** default to *Inspirational* when in doubt (lowest blast radius, zero attribution burden); never *Full*-adopt anything on the governance / orchestration / product-modeling spine (bands G/H/I — the factory's moat); *Selective* is most defensible for self-contained, project-agnostic specialist lenses (band F); treat any external skill that spawns named external agents as a bundle, not a single unit.

## Outcome Requirements

The following properties must hold at all times, independent of how they are achieved.

### OR-1: A Reusable Evaluation Framework Exists

The method, capability taxonomy, scoring axes, adoption levels, and decision heuristics in **Evaluation Framework** above are available and are the basis of every external-tooling evaluation. A new evaluation reuses this framework rather than inventing its own.

### OR-2: Inspirational-First, Spine Protected

The standing default is *inspirational* adoption — porting an external idea into our own stable component. No external component ever *fully replaces* a factory component on the governance, process-orchestration, or product/user-needs-modeling spine. Higher-coupling levels (*selective copy*, *full*) are chosen only with an explicit, recorded justification that the value outweighs the maintenance and re-test cost.

### OR-3: Attribution & Provenance Are Recorded

Every file copied or adapted from an external source into this repository is recorded in a root-level `THIRD_PARTY_NOTICES.md` carrying the source name, its license, the upstream copyright line, the source commit SHA copied from, and the list of adapted files. Inspirational ports (idea reused, no text copied) carry no attribution obligation and are not required to appear there.

### OR-4: Copies Are Frozen and Collision-Free

An externally-sourced skill or agent brought into the repo is a point-in-time snapshot: it is not wired to track upstream, and the factory owns it thereafter. Its name does not collide with any built-in Claude Code skill/agent or any existing factory component; where the source name would collide, the copy is renamed.

### OR-5: Dispatch-Changing Adoptions Are Re-Validated

Any adoption that changes how `code-*` or `task-*` skills dispatch agents, or that alters a quality gate, is re-validated against representative implementation and bugfix tasks before it is relied upon in automated mode.

### OR-6: Every Evaluation Produces a Recorded Decision

Each external-tooling evaluation ends with a recorded adopt / adapt / skip decision per relevant component, honest about residual uncertainty, and traceable from the evaluation task.

## Scope Boundaries

This requirement governs the **evaluation method and adoption policy** for external Claude Code tooling. It does **not** govern:

- The verdict on any specific plugin → that lives in the evaluating task's synthesis report (han: TASK-PROC-055-01).
- General third-party software-dependency supply-chain safety (packages, libraries) → see REQ-PROC-056.
- How new first-party skills are created or modified → see the `claude-create-skill` / `claude-modify-skill` skills and their governing requirements.

## References

**Grounding & parent**
- PERSONA-015 (App Provider / The Creator): the sustainability + minimum-effective-dose values this requirement serves.
- Apex parent **pending**: a "Factory Purpose & Continuous Improvement" requirement is being defined (TASK-PROC-055-01 follow-up). Once it exists, this requirement is adopted as a child input channel, alongside REQ-PROC-006 and the quality standards.

**Where "good outcomes" live** (this requirement does not redefine them — it provides a safe on-ramp for external ideas that improve them):
- Dev & app security, supply chain → REQ-PROC-052 (Privacy & Security gates), REQ-PROC-056 (Dependency Supply-Chain Safety)
- Code quality / maintainability → REQ-PROC-046 (Code Quality), REQ-PROC-051 (Python Code Quality)
- Testing → REQ-PROC-002 (Test Quality), REQ-PROC-005 (Testing Workflow)
- UX & performance → `non-functional/ui_ux_design_system/*`, `non-functional/` performance requirements
- Factory-machine integrity → REQ-PROC-044 (Software Factory Quality Properties)
- Continuous improvement loop → REQ-PROC-006 (Workflow Improvement Automation)

**Prior art & source**
- REQ-PROC-038: CodeGraph integration (prior external-tool integration)
- han plugin: github.com/testdouble/han (MIT, Test Double)

**This requirement's evaluation evidence**
- TASK-PROC-055-01 synthesis report: `tasks/2026-05-26_explore_han-plugin-evaluation (completed)/plans_and_protocols/2026-05-26_05_synthesis_decision_report.md`
- Reusable framework + our-factory inventory: same task, `..._04_framework_and_our_inventory.md`
