# Comparison Framework + Our-Factory Inventory

Status: drafted during Phase 1 (gathering). The framework is the data-independent
first deliverable the goal mandates ("define the comparison framework before doing
the comparison"). The synthesis report (file 05) applies it.

Agent IDs for this exploration (for resume):
- Orchestrator: this session
- Gather han skills: a10296335ac405c4c
- Gather han agents: a6eb3e144968a9ee6
- Web research: aa23483171b6b067d

---

## Part A — Our Factory Inventory (the "ours" side of the map)

### Skills (57 total)
Organized by lifecycle stage, NOT by generic capability. Highly project-specific.

| Cluster | Skills | Character |
|---|---|---|
| requ-* | requ-explore, requ-derive-from-flow, requ-assign-packages, requ-apply-market, requ-merge, requ-verify-flow-coverage | Requirements lifecycle; tied to our REQ-ID registry + flow coverage |
| task-* | task-create, task-create-code, task-derive-from-requ, task-complete, task-complete-bugfix, task-repair-meta, task-unblock-check, task-resolve, verify-quality | Stateful task lifecycle; goal.md/protocol.md, dependency graph |
| code-* | code-simple, code-complex, code-bugfix, code-test, code-run-integration | Flutter/Dart impl workflows; read doc/ guidelines first |
| release-* | release, release-plan, release-status, release-begin-impl, release-begin-impl-finalize | Package→version release orchestration |
| ux-* | ux-write-persona, ux-write-scenario, ux-write-canon-concept, ux-create-flow (+3 internal), ux-validate-rule, vcd-log-tradeoff | Product/user-needs pipeline — has NO han equivalent |
| ui-* | ui-create-scribble, ui-create-scribble-improve, ui-verify-flutter, ui-improve-flutter | Wireframe→Flutter visual pipeline — NO han equivalent |
| doc-* | doc-update-guidelines, doc-split, doc-update-tokens | Maintains doc/ guidelines (our "LAW") |
| claude-* | claude-route, claude-optimize, claude-create-skill, claude-write-script, claude-modify-skill, claude-modify-ordering-rules, claude-ask, claude-log, claude-save-checkpoint, claude-install-os-tool, claude-commit, claude-resume-agent, claude-autorun, claude-automated-mode | Factory infrastructure / self-modification / automation |

### Agents (6, broad roles)
| Agent | Model | Role |
|---|---|---|
| architecture-advisor | opus | Plan multi-file/architectural changes |
| implementation-engineer | sonnet | Implement planned features |
| test-engineer | sonnet | Full TDD workflow (plan+write+fix) |
| quality-checker | sonnet | Check code vs doc/ guidelines |
| opus-advisor | opus | Deep investigation, writes report |
| setup-optimizer | opus | Analyze usage, suggest factory improvements |
(+ harness built-ins: general-purpose, Explore, Plan, claude.)

### Hooks
- SessionStart: blocked-task warning (top_blocked_task.py)
- PostToolUse: `dart fix --apply` + `dart analyze` on edited .dart; inbox processing
- PreToolUse: script-quality-gate enforcement on scripts/**/*.{py,ps1}; git-commit gate

### Quality gates (~20 scripts in scripts/quality/)
G1–G8, TQ1–TQ4, SP1–SP6, Python G1–G5. Enforced via verify-quality skill +
pre-commit hook. Five-cycle back-pressure protocol with developer escalation.

### Defining characteristics of OUR factory
1. **Stateful** — protocol.md long-term memory, task lifecycle, dependency graph.
2. **Gate-enforced** — 18+ blocking quality gates, refuses completion on RED.
3. **Product-pipeline-first** — Persona→Scenario→Flow→Requirement→Task→Code is the
   spine; "never change app behavior except top-down" is constitutional.
4. **Self-modifying** — skills create/modify skills; claude-optimize loop.
5. **Single-stack** — Flutter/Dart, Clean Architecture, BLoC. doc/ is LAW.
6. **Orchestrator model** — main session delegates to a small set of broad agents.

---

## Part B — Reusable Plugin-Evaluation Framework

> Designed to be reused for ANY future external plugin/marketplace evaluation,
> not just han. Lives here so the methodology survives as an asset.

### B.1 Method (the process, in order)
1. **Inventory both sides** — catalog every component (skill/agent/hook/doc) with a
   one-line purpose. (Delegate gathering to subagents to protect context.)
2. **Normalize into a shared capability taxonomy** (B.2) so we compare like-with-like
   and can detect whole *missing categories* (the highest-value discovery type).
3. **Map each external component → nearest internal equivalent** → classify overlap
   (none / partial / full).
4. **Score each component on the axes** (B.3).
5. **Flag the two special cases**: (a) external GAPS we feel = candidate wins;
   (b) PHILOSOPHY CONFLICTS = adopt only by adaptation or not at all.
6. **Roll up to adoption-level recommendations** (B.4) per component and overall.

### B.2 Capability taxonomy (compare like-with-like)
- **A. Planning** — feature/phased/implementation/work-item decomposition
- **B. Review & critique** — code review, plan review, adversarial challenge, gap analysis
- **C. Investigation & research** — codebase exploration, evidence-gathering, external research
- **D. Implementation** — writing code, TDD execution
- **E. Documentation & comms** — ADRs, project docs, stakeholder summaries, PR descriptions
- **F. Specialist analysis lenses** — concurrency, edge cases, risk, security, data, devops, UX
- **G. Governance / quality** — coding standards, quality gates, test quality
- **H. Process orchestration** — requirements pipeline, task lifecycle, release management
- **I. Product / user-needs modeling** — personas, scenarios, flows, value trade-offs

### B.3 Scoring axes (per external component)
| Axis | Scale | Question |
|---|---|---|
| Overlap | none / partial / full | Do we already have an equivalent? |
| Gap-fill value | none / low / med / high | Does it fix a gap we actually feel? |
| Philosophy fit | conflict / neutral / aligned | Compatible with stateful + gate-enforced + pipeline-first? |
| Self-containment | low / med / high | Adoptable alone, or drags deps (other agents, gh CLI, file layout)? |
| Adaptation cost | S / M / L | Effort to make it work in our project |
| Re-test risk | none / low / med / high | Does adopting force re-testing existing workflows? |
| Attribution burden | none / note / per-file | MIT obligation if copied/adapted |

### B.4 Adoption levels (decision output)
- **Full** — replace our component with han's. Justified only when overlap=none or
  han is strictly better AND philosophy fit=aligned AND re-test risk≤low.
- **Selective** — cherry-pick the component (copy + adapt) into our `.claude/`.
  Best when gap-fill value≥med, self-containment≥med, philosophy fit≠conflict.
- **Inspirational** — do not copy; let han's idea inform a rewrite of OUR own
  component. Best when philosophy fit=conflict or adaptation cost=L but the *idea*
  is valuable. Lowest re-test risk, zero attribution burden.
- **None** — skip. Overlap=full with no quality delta, or gap-fill value=none.

### B.5 Decision heuristics
- Default to **Inspirational** when in doubt — it has the lowest blast radius on a
  stateful, gate-enforced factory and avoids re-testing established workflows.
- **Never Full-adopt** anything on the orchestration/governance/pipeline spine
  (categories G/H/I): those are where our factory's value lives and where han is
  weakest (han is stateless and project-agnostic by design).
- **Selective is most attractive for category F** (specialist analysis lenses):
  han's agents there are self-contained, project-agnostic, and fill a real gap
  (our 6 broad agents have no adversarial/concurrency/edge-case/security lens).
- Treat any han skill that **spawns named han agents** as a *bundle*, not a
  single unit — adopting the skill drags its agent roster.

---

## Part C — Hypotheses to test against gathered data (resolve in file 05)
- H1: Han's strength is categories A/B/C/F; our strength is G/H/I. (expect complementary)
- H2: Han's specialist agents (F) are the most selectively-adoptable items.
- H3: Han's philosophy (YAGNI, evidence-first, adversarial) is *compatible* with us
      at the principle level but its *stateless* execution model conflicts with our
      protocol.md/task-lifecycle statefulness.
- H4: Lowest-risk wins = "inspirational" adoption of review/planning rigor into our
      existing code-complex / architecture-advisor, not wholesale skill imports.
- H5: MIT cost is low (retain notice in a THIRD_PARTY/NOTICE file + per-file header
      on adapted files); no blocker for internal non-distributed use. (confirm via research)
