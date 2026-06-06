---
id: REQ-PROC-062
urgency: 3
urgency_reason: U3-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: active
effort: M
stakeholder: developer
created: 2026-05-28
updated: 2026-06-02
after: [REQ-PROC-009, REQ-PROC-045]
blocks: []
market_research_refs: [] # No relevant findings identified
target_package: ""  # internal process tooling — unassigned
personas_served: [PERSONA-015]
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "Each AC in a requirement is verifiable: a reader with access to the artifact can evaluate it as pass or fail without subjective judgment. Words such as 'appropriate', 'reasonable', 'efficient', 'good', 'sufficient', or 'performant' do not appear in ACs unless the criterion defines its own threshold (e.g. 'loads in < 2 s on a mid-range 2019 Android device')."
    - id: AC-02
      text: "No AC uses transition verbs (replace, update, migrate, add to, convert, remove from, change, refactor). Every AC describes the state of the system when the requirement is fully met, verifiable by inspecting the final artifact alone."
    - id: AC-03
      text: "Each AC is atomic: it tests exactly one verifiable property. ACs that combine multiple distinct properties with 'and' are split into separate ACs. Exception: both parts are conditions of a single indivisible response (e.g. 'when X, the system does Y and emits Z' where Y and Z are parts of one atomic event)."
    - id: AC-04
      text: "Each AC is evidence-grounded: it is justified by at least one piece of real evidence — a user-described need, a named direct dependency, an existing code path that breaks without it, a regulation in effect today, or a documented incident. ACs failing this gate are placed in a '## Deferred (YAGNI)' section with a reopen condition, not removed silently."
    - id: AC-05
      text: "The ## Purpose section answers three questions: (a) what user problem or need this requirement addresses, (b) what triggered this requirement (research insight, user feedback, technical constraint, documented incident), (c) why it matters now. A Purpose section that only restates the requirement title does not meet this criterion."
    - id: AC-06
      text: "Every sentence in the ## Developer Guidelines section describes a constraint or invariant of the finished system. No sentence in Developer Guidelines describes a step to take during implementation, a migration action, or a to-do. Violation examples: 'Add validation to all form fields', 'Replace X with Y', 'Ensure the following are migrated'."
    - id: AC-07
      text: "No requirement file contains the sections ## Testing Requirements, ## Open Questions, ## Version History, or ## Implementation Roadmap. Testing specifics belong in task plans; open questions are converted to exploration tasks; version history is tracked by git; roadmaps belong in task plans."
    - id: AC-08
      text: "Each AC in an epic-level requirement describes a capability or outcome — what the product, system, or factory achieves — without naming any screen, field, YAML key, class, method, artifact section, or skill phase. An epic AC is verifiable by a domain-knowledgeable reader observing the system at the capability level, without inspecting any artifact, source file, or internal component."
    - id: AC-09
      text: "Each AC in a feature-level requirement for the app codebase (`lib/`, `test/`, `integration_test/`) is verifiable by running the app or using a development tool (static analyzer, linter, test runner, network inspector) — without reading source code. Permitted vocabulary: screen names, route names, field labels, domain entity names, visible UI states. Prohibited vocabulary: class names, method names, widget names, BLoC state class names."
    - id: AC-10
      text: "Each AC in a feature-level requirement for the software factory (skills, agents, scripts, workflow rules) is verifiable by inspecting a produced artifact (`requirements.md`, `goal.md`, script output) or by invoking a skill or script and observing its output — without reading skill internals or agent step logic. Permitted vocabulary: artifact field names, YAML frontmatter keys, document section headings, folder naming patterns, script exit codes and output content, skill phase names. Prohibited vocabulary: internal skill step logic, agent reasoning steps, implementation details of how a skill or script produces its output."
---

# Requirement Content Quality

## Overview

Requirements are blueprints for implementation. Their quality determines whether derived tasks are well-scoped and whether the factory can verify completion. This requirement defines the content properties that every requirement in the factory must satisfy — independent of how it was created or when.

## Purpose

The factory's structure quality (REQ-PROC-045) and language coherence (REQ-PROC-049) are formally specified and mechanically checked. Content quality is not: it exists only as a skill-internal checklist in `requ-explore` Phase 2.5, which applies prospectively to requirements written through that skill. No contract covers existing requirements, no other pathway enforces these properties, and no single source of truth defines what "good content" means.

The gap matters because requirements drive tasks, tasks drive code, and code drives user experience. A requirement with non-verifiable ACs produces tasks with ambiguous acceptance criteria. A requirement with transition-language ACs cannot be verified after completion. A Purpose section that restates the title provides no justification for the work it triggers. Each of these failures propagates silently downstream until a task is completed, a test passes, and the wrong thing is built.

REQ-PROC-045 explicitly scopes out content quality in its anti-scope section. This requirement fills that gap, turning the requ-explore Phase 2.5 checklist into a formal contract with enforceable properties.

## Behavior

A requirement meets content quality when all of its ACs satisfy AC-01 through AC-04 (verifiable, end-state, atomic, evidence-grounded), its Purpose satisfies AC-05, its Developer Guidelines section satisfies AC-06, no forbidden sections (AC-07) are present, and every AC is written at the correct abstraction level for its hierarchy tier: AC-08 for epic-level requirements; AC-09 for feature-level requirements covering the app codebase; AC-10 for feature-level requirements covering the software factory.

Existing requirements that pre-date this requirement are not immediately invalid — they become subject to this contract when they are next opened for update via `requ-explore`.

## Developer Guidelines

### Key Decisions

- **Prospective enforcement via requ-explore, retrospective via exploration task**: The requ-explore Phase 2.5 checklist is the primary enforcement point for new requirements. Retrofitting existing requirements is a separate effort, scoped in the enforcement exploration task (TASK-PROC-062-01).
- **AC-01 threshold rule**: A threshold that appears "obvious in context" is not sufficient — the threshold must be written in the AC itself. Reviewers and LLM agents months later will not have the original context.
- **AC-03 atomicity exception is narrow**: "And" is only permitted when both parts are conditions of a single indivisible event. When in doubt, split.
- **AC-04 deferred ACs are preserved, not deleted**: Deleting speculative ACs loses the reasoning for why they were considered. The ## Deferred (YAGNI) section with a reopen condition is the only valid disposition for an AC that fails the evidence gate.
- **AC-07 is unconditional**: These sections are never acceptable in a requirements file regardless of how useful they seem in the moment. Version history belongs to git. Open questions belong in exploration tasks.
- **AC-08 capability-level rule**: If an epic AC names a specific screen, artifact field, class, or skill phase, it belongs in a feature — not the epic. "The system allows users to transfer data between devices" passes; "The QR transfer screen is accessible from the home screen" fails.
- **AC-09/AC-10 share the same boundary principle**: permitted vocabulary is the *interface* (screens and fields for app; artifacts and outputs for factory); prohibited vocabulary is the *internals* (classes and methods for app; skill step logic and agent reasoning for factory). The factory analogy makes this concrete: skills and agents are the source code of the factory; artifacts are its domain model. An AC referencing an artifact field name (e.g. `acceptance_criteria` YAML key) is at the same abstraction level as an AC referencing a screen field name — both are domain model vocabulary, not implementation detail.

### Common Pitfalls

- **Threshold-free quality adjectives**: "The app responds quickly", "The UI is clean", "The export is reliable" — none of these is verifiable. Each needs a threshold or measurable condition.
- **Purpose as title paraphrase**: "This requirement defines the data export feature" says nothing a reader couldn't infer from the title. Purpose must answer WHY.
- **Mixed AC atomicity**: "The user can create, edit, and delete entries" — three verifiable properties collapsed into one AC. Split.
- **Implicit evidence**: "This AC exists because it's best practice" — not evidence. Name the practice, the source, and why it applies here.
- **Epic ACs at feature abstraction**: "The mood entry form validates input before saving" on an epic — names a screen, belongs in a feature AC. Epic ACs name capabilities: "Users can record mood entries."
- **Implementation vocabulary in app feature ACs**: "The `MoodBloc` emits `MoodSavedState` after persisting the entry" — names a class. Rewrite as observable behavior: "After saving a mood entry, the entry appears in the mood history list."
- **Skill internals in factory feature ACs**: "The `requ-explore` skill iterates over each AC and calls the verifiability checker" — describes internal logic. Rewrite as observable output: "Running `requ-explore` on a requirement containing a transition-language AC produces an error identifying the offending AC."

## Related Requirements

- [REQ-PROC-009](../requirements_and_tasks/requirements.md) — defines the overall requirement format and structure; content quality builds on top of structural compliance
- [REQ-PROC-045](../requirements_structure_quality/requirements.md) — structural quality of the requirements folder; explicitly scopes out content quality in its anti-scope, delegating it here
- [REQ-PROC-049](../language_coherence/requirements.md) — language coherence across artifacts; orthogonal dimension (consistent naming vs. content quality)
- [REQ-PROC-064](../requirement_currency/requirements.md) — requirement currency; a requirement that meets content quality is also easier to assess for currency (verifiable ACs have a clear pass/fail boundary that makes staleness detectable)
- [REQ-PROC-003](../requirements_writer_mode_flexibility/requirements.md) — governs how requirements are authored; content quality constrains what requ-explore must produce

## References

- `.claude/skills/requ-explore/SKILL.md` Phase 2.5 — the existing quality checklist this requirement formalizes
- `.claude/skills/requ-explore/SKILL.md` Phase 2.2 — YAGNI evidence gate (operationalization of AC-04)
- `requirements_tasks/process/AI_rules/requirements_management/requirements_structure_quality/requirements.md` §Anti-Scope — "per-requirement content quality (covered by requ-explore Phase 2.5)" — explicit delegation to this requirement
