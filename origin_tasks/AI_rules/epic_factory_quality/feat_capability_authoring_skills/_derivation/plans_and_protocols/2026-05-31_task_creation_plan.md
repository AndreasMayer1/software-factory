---
requirement: REQ-PROC-044-01
requirements_version: 6ece1dc7
created: 2026-05-31
mode: full
---

# Task Creation Plan for REQ-PROC-044-01 (Capability-Authoring Skills)

Process requirement — NO target_package (all ACs `unassigned`; process scope).

## Tasks

- task_name: "create-claude-agent-authoring-skills"
  ref: N1
  req_path: "requirements_tasks/process/AI_rules/epic_factory_quality/feat_capability_authoring_skills/requirements.md"
  requirements_version: "6ece1dc7"
  covers_acs: [AC-01, AC-02, AC-03, AC-04, AC-05]
  effort: L
  layer: process
  after: []
  task_type: impl
  opus_recommended: true
  target_package: none
  sizing: { S1: ">60 (2 SKILL.md + 2 contract.yaml + INDEX.md + factory_flows.md, claude-create-skill x2)", S2: "closed (skills/files named)", S3: "true (skill design + agent-authoring judgment + domain-vocab pedagogy synthesis)", S4: "false (no lib/)" }
  implementation_notes: >
    Create the `claude-create-agent` AND `claude-modify-agent` skills USING the
    `claude-create-skill` skill (mandated for skill creation). Both must bake in,
    as enforced/observable end-state guarantees on the resulting `.claude/agents/*.md`:
    (AC-01) collision-checked naming scheme (vs Claude built-in agents, Han imports
    e.g. han-adversarial-validator, and existing project agents); allowed_tools
    heuristic by intent class (narrowest set; no bare `*` without recorded
    justification — mirror the `tools: "*"` rule in claude-create-skill); a
    when-to-create-an-agent gate (disqualifying questions: extend existing
    skill/agent instead?); the agent-vs-session suitability check per
    TASK-PROC-032-10 file 13 §5.
    (AC-02) required structural sections — role identity ≤50 tokens + `## Domain
    Vocabulary`, `## Anti-Patterns`, `## Protocols`, `## Output`, `## Rules`.
    (AC-03) the Domain-Vocabulary authoring aid — produces 10–25 expert-tier terms
    each passing the "15-year-practitioner test"; instruction-driven with strong
    language to push the LLM past shallow/common-web vocabulary; MAY delegate
    web/research lookup; shallow vocabulary REJECTED not padded. This is the home
    of recovered capability D9.
    (AC-04) contract-mechanism integration — emit/maintain `contract.yaml` per the
    REQ-PROC-044 mechanism and REFERENCE the sub-skill-vs-agent split rubric
    (REQ-PROC-044 AC-03) rather than re-deriving it.
    (AC-05) record single ownership: add both new skills to `.claude/skills/INDEX.md`
    as part of the governed meta-skill set, with the existing four
    (claude-create-skill, claude-modify-skill, claude-write-script,
    claude-modify-ordering-rules); each ownership entry cross-links the existing
    governing AC (e.g. REQ-PROC-044 AC-03 split rubric; REQ-PROC-042 for ordering;
    REQ-PROC-043 for write-script) rather than duplicating it.
    claude-create-skill handles INDEX.md + factory_flows.md updates.
    Deferred (YAGNI): retro-justifying the ui-scribble-* agents under the rubric —
    reopen when: a REQ-PROC-032 scribble task edits those agents through the new
    pair (tracked there, not here).

- task_name: "port-domain-vocabulary-to-existing-agents"
  ref: N2
  req_path: "requirements_tasks/process/AI_rules/epic_factory_quality/feat_capability_authoring_skills/requirements.md"
  requirements_version: "6ece1dc7"
  covers_acs: [AC-03]
  effort: M
  layer: process
  after: [N1]
  task_type: impl
  opus_recommended: true
  target_package: none
  sizing: { S1: "~moderate (6 agent files edited via claude-modify-agent)", S2: "closed (6 agents named)", S3: "true (expert-tier vocabulary per distinct agent domain)", S4: "false" }
  implementation_notes: >
    USING the new `claude-modify-agent` skill, add `## Domain Vocabulary` (10–25
    expert-tier terms passing the 15-year-practitioner test) and `## Anti-Patterns`
    to the six existing agents: architecture-advisor, implementation-engineer,
    opus-advisor, quality-checker, setup-optimizer, test-engineer. This is
    capability D9 executed THROUGH the new skill — it is the real-world exercise of
    AC-03's authoring aid. Each agent keeps its contract.yaml in sync (AC-04
    mechanism). Vocabulary must be domain-distinct per agent (architecture vs
    testing vs implementation vs review vs setup vs Opus-routing); shallow/generic
    terms rejected.

- task_name: "verify-capability-authoring-skills"
  ref: V
  req_path: "requirements_tasks/process/AI_rules/epic_factory_quality/feat_capability_authoring_skills/requirements.md"
  requirements_version: "6ece1dc7"
  covers_acs: [AC-01, AC-02, AC-03, AC-04, AC-05]
  effort: M
  layer: process
  after: [N1, N2]
  task_type: verify
  opus_recommended: true
  target_package: none
  sizing: { S1: "moderate (audit reads many artifacts)", S2: "closed", S3: "true (judges shipped artifacts against ACs)", S4: "false" }
  implementation_notes: >
    Audit the SHIPPED artifacts (not the impl tasks' claims) against AC-01..AC-05:
    (AC-01) author a throwaway test agent through claude-create-agent and confirm a
    colliding name is rejected, allowed_tools matches intent class, the
    when-to-create gate fires, and the agent-vs-session check runs; (AC-02) confirm
    every agent authored/modified through the pair carries role identity ≤50 tokens
    + the five required sections; (AC-03) confirm the Domain-Vocabulary aid produces
    10–25 terms and that the six existing agents (post-N2) carry expert-tier
    vocabulary passing the practitioner test — reject if generic/padded; (AC-04)
    confirm contract.yaml is emitted/maintained for the new skills and the rubric is
    referenced not re-derived; (AC-05) confirm INDEX.md lists the six meta-skills as
    the governed set with cross-links (no duplicated/stale ownership). File a
    fix-task for any gap rather than ticking optimistically.

## Coverage Matrix

| AC | Task(s) | Package |
|----|---------|---------|
| AC-01 | N1, V | none (process) |
| AC-02 | N1, V | none (process) |
| AC-03 | N1, N2, V | none (process) |
| AC-04 | N1, V | none (process) |
| AC-05 | N1, V | none (process) |

100% coverage. 2 impl tasks (N1, N2) + 1 verify task. Separate verification task
created (instruction-mandated; justified by cross-AC end-state assertions even
though impl-task count is 2). No circular dependencies: N1 → N2 → V.

## Cross-reference gate (Phase 1.5)

Passed. One semantic cross-ref added (REQ-PROC-043). See
`2026-05-31_cross_ref_classifications.md`.
