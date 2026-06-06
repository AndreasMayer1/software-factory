---
task_id: TASK-PROC-044-02
type: explore
parent_requirement: REQ-PROC-044
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: completed
effort: L
created: 2026-05-29
started: 2026-05-29
completed: 2026-05-29
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-02, AC-03, AC-04, AC-06]
  sections: []
scope_description: "Design and prototype the mechanism (sidecar contract.yaml + schemas + lint + handoff blocks + split rubric + bidirectional-feedback channel) that operationalizes REQ-PROC-044 ACs 01/02/03/04/06 across the factory; ratify the proposed scribble-pipeline sub-skill split before SCRIBBLE-SPLIT executes"
release_description: ""
opus_recommended: true   # reason: cross-cutting design + multi-skill prototype + bidirectional-feedback formalization
writes_requirements: false
requirements_version:
  commit: b10665f5
  file: ../../requirements.md
---

# Goal: Explore the Skill Interface Contracts Mechanism

## Objective

REQ-PROC-044 (Software Factory Quality Properties, `status: active`) declares 6 ACs covering reachable outputs (AC-01), traceability (AC-02), extensibility (AC-03), graceful degradation (AC-04), determinism (AC-05), and authoritative documentation (AC-06). The factory satisfies these only partially today — many skill-to-skill interactions are implicit conventions that work but produce a transparency, modifiability, and debuggability tax. This exploration designs and prototypes the **mechanism** that operationalizes these ACs.

Concretely unresolved at this task's creation: *what* form the declared contract takes (sidecar `contract.yaml` vs frontmatter schema vs registry vs hybrid), *where* schemas for shared artifacts live, *how* violations are detected (lint vs runtime guard), *which* skills get split into sub-skills versus stay bundled, and *what pattern* handles bidirectional feedback (coder→scribble, reviewer→flow, validator→scribble, and the broader review-channel question).

The exploration must end with **prototypes on real skills**, not paper designs. A future implementer reads the synthesis and the prototypes to author the rollout — they should not need to re-derive the mechanism.

## Background

This task is spun out of **TASK-PROC-032-10** (exploring the scribble–coder contract). That task surfaced the implicit-interface problem as systemic, not scribble-specific. Five iteration documents in TASK-PROC-032-10's `plans_and_protocols/` capture the analysis to date — read them in order before starting:

1. **File 08** — `2026-05-28_08_skill_interface_exploration.md` (the agent-produced inventory + initial mechanism proposals; INCOMPLETE per developer note — treat as starting position, not conclusion)
2. **File 09** — `2026-05-29_09_design_thinking_iteration_4.md` (integration with the scribble-contract work; introduces bundles, dependency graph)
3. **File 10** — `2026-05-29_10_redundancy_check.md` (post-iteration audit; R3 collapse + R9 gap-fill; sharp scope boundaries)
4. **File 12** — `2026-05-29_12_design_thinking_iteration_5.md` (strategic narrowing; REQ-PROC-044 alignment; frontmatter audit dropping D41/D42; PRINCE2 evaluation; total-cost decision)
5. **File 13** — `2026-05-29_13_session_token_efficiency_analysis.md` (session-vs-agent decision tree; recommended cuts for the scribble pipeline)

Full paths:
```
requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/tasks/2026-05-27_explore_scribble-contract-and-ux-review/plans_and_protocols/{08,09,10,12,13}_*.md
```

REQ-PROC-044 (the parent) is at: `../../requirements.md` (current); for the version at this task's creation: `git show b10665f5:requirements_tasks/process/AI_rules/factory_quality/requirements.md`.

**Related parallel work** (read at task start, integrate constraints if it completes during execution):
- **TASK-PROC-057-01** — apex factory-purpose exploration. Defines the north star + continuous-improvement loop. Likely to land "minimum effective dose" framing that constrains contract complexity. Path: `requirements_tasks/process/AI_rules/factory_purpose/tasks/2026-05-26_explore_factory-purpose-and-improvement-loop/goal.md`.

**Total-cost framing**: this task is the *prerequisite* for the 10 deferred bundles in TASK-PROC-032-10 (Q2-CONTRACT, Q1-AGENTS, NEW-SKILL, VISUAL-VALIDATE, BREAKPOINTS, INSPIRATION, PREBRIEF, CROSS-FEATURE, DOMAIN-VOCAB, SCRIBBLE-SPLIT). It also blocks resumption of release 0.0.1 implementation. Execute efficiently — the goal is *enough* mechanism to move, not *perfect* mechanism.

## How to Approach This

Design thinking. Empathize first — walk through three concrete real-world scenarios (one from each pain category in file 08) where the implicit contract caused or would cause silent failure. Diverge before converging — re-evaluate the agent's recommendations in file 08 against the developer's round-6 feedback (especially the sub-skill-vs-agent question). Resist the temptation to import the heaviest mechanism (full JSON Schema everywhere); the project's token budget and developer-velocity constraints differ from a production SDK.

Multiple rounds are expected. The first round inventories what's actually broken (the agent's inventory was sampled, not exhaustive). The second round prototypes the candidate mechanisms on 2–3 representative skills. The third round synthesizes the recommendation, including a migration sequence.

## Seeds

(Lenses, not a checklist. Frame as questions. Expect some to lead nowhere, others to open new threads.)

1. **What's the smallest declared contract that catches the most failures?** If skills declared only `(input_files_expected, output_files_produced, invokes_skills)`, would a static lint catch most of today's implicit-interface bugs? Or does data-shape (frontmatter keys, YAML schemas) declaration carry its weight?

2. **Where does the contract live?** Inline frontmatter in `SKILL.md` vs sidecar `contract.yaml` vs registry file in `.claude/contracts/`. Trade-offs: token cost at skill load, ease of update via `claude-modify-skill`, lint affordance. **File-12 §3.1 audit note**: most artifacts ALREADY have definitions in their root folders (README files describing how the artifact looks). Migration must remove stale duplicates — never let the new mechanism coexist with old prose specs.

3. **Bidirectional feedback as one channel or many?** The developer's round-6 reframing: a `revision_requests/` folder for skill→skill reviews, separate from `pending_feedback/` for developer questions, risks orchestrator-interference (current orchestrator scans only `pending_feedback/`; new channel would be missed). **Should the channels unify?** Consider: pending_feedback today already carries iterative review proposals (skills asking "is this good?"). A nested structure (revision_requests as a subfolder under pending_feedback, all scanned by the orchestrator) may be the right answer. Also: improvement suggestions live in `factory/` folder today — does that channel merge too, or stay separate?

4. **`revision_request` file vs creating a task** — when does each apply? File-12 §4.5 proposes: standalone work → task; decision/review → revision_request file; developer question → pending_feedback. Validate this taxonomy on real examples (coder→scribble, validator→scribble, reviewer→flow) and refine.

5. **Sub-skill vs agent — the sharp question** (developer round-6 §7): *"If a sub-skill only spawns an agent, maybe it's better to write a description of what the sub-skill does in the agent and replace the sub-skill by this agent."* Apply to the proposed SCRIBBLE-SPLIT (file 09 §7.1):
   - `ui-scribble-generate` — spawns ONE agent. Does it have orchestration value, or replace with `scribble-generator` agent invoked directly by the orchestrator?
   - `ui-scribble-auto-review` — spawns MULTIPLE agents (auto-reviewer + ux-protocol + persona-embodiment). Real orchestration value.
   - `ui-scribble-feedback-classify` — spawns agents that classify + invoke other skills. Real orchestration value.
   - `ui-scribble-approve-handoff` — spawns ONE agent. Sub-skill or just the agent?
   Codify the rubric.

6. **Skill granularity — when does "split into sub-skills" beat "add a phase inside one skill"?** File 08 §3.5 proposed adding the rubric to `claude-create-skill`. Concrete criteria: phases share intermediate state that escapes context if split → bundle; phases plausibly invoked independently → split; phase boundary is a natural human review point → split; phase outputs are file-based → split is cheap. Validate.

7. **Lint vs runtime check.** Pre-commit lint (`scripts/quality/check_skill_contracts.py`) catches drift cheaply. Runtime guard (skill refuses to start if precondition unmet) is stronger but costs an extra Bash call per skill. Given automation-mode reliability concerns, which buys us more?

8. **Migration story.** Even a clean schema is worthless if it can't be incrementally adopted. Can we adopt skill-by-skill, with `contract_version: 0` meaning "unmanaged"? File-12 §3 dropped `presentation_layer:` and `serves_requirements:` because existing artifacts (heuristic / `requirements_matrix.md`) suffice. **Look first; add only what's missing.** Where `requirements_matrix.md` may not exist for a flow: see `requ-derive-from-flow` skill for the existing handling.

9. **Bundled skills that should stay bundled.** Some skills are coherent units precisely because their phases share intermediate state (`requ-explore`, `ux-create-flow`, the proposed `ui-scribble-iterate` orchestrator). The contract effort should not fragment these. List exceptions explicitly.

10. **Agent-vs-session evaluation in `claude-create-agent`.** File-13 §5 distinguishes session split (cold restart) from agent invocation (sub-context inside warm session) — different cost trade-offs. The forthcoming `claude-create-agent` skill (D22, NEW-SKILL bundle) should bake this evaluation into its when-to-create-an-agent decision. Treat file-13 §5–§6 as input for that skill's rubric.

## Decisions to Resolve (must be settled before completion)

1. **Sub-skill split for the scribble pipeline** — confirm or revise file 09 §7.1's 4-sub-skill cut, applying seed 5's question. Decision feeds the SCRIBBLE-SPLIT impl task.
2. **Contract mechanism** — pick one of: sidecar `contract.yaml` (file 08 §3.1 recommendation) / inline frontmatter / registry / hybrid. Justify against the project's token budget and the developer's "transparency" goal.
3. **Bidirectional feedback channel structure** — unified-channel (revision_requests as subfolder of pending_feedback) or separate channels with orchestrator update. Decide and prescribe orchestrator-side changes.
4. **revision_request vs task taxonomy** — final rule for when each applies.
5. **Migration sequence** — which skill family adopts first; what `contract_version: 0` opt-out looks like; how stale duplicates are removed without losing information.
6. **Whether REQ-PROC-044 needs new ACs** — if the mechanism discovers gaps in the existing 6 ACs, propose additions via `requ-explore` (a separate follow-up); do NOT modify REQ-PROC-044 from this task.

## Execution Model

Gather raw material — read the 5 iteration documents listed in Background, REQ-PROC-044, CLAUDE.md, `.claude/factory_flows.md`, `.claude/skills/INDEX.md`, sample 8–12 skill SKILL.md files across families (code-*, ui-*, ux-*, requ-*, task-*, doc-*). Synthesize iteratively — multiple gathering rounds may be needed.

**Inventory pass at start** (per file-12 §2.3): read `requirements_tasks/STATUS.md` and grep `requirements_tasks/process/AI_rules/factory_*` for `type: explore` tasks. Identify related-but-separately-pursued work. Avoid duplicating their efforts.

**TASK-PROC-057-01 awareness** (per file-12 §2.2): read that task's current state at start. If it completes during this exploration, integrate its constraints (especially "minimum effective dose" framing) into the mechanism choice.

The session's model is fixed at launch (Opus per `opus_recommended: true`).

**Agent delegation principle** (per file-13 §6 — the developer's real-time emphasis): delegate to a fresh agent when work needs heavy unrelated context, is self-contained (clear inputs/outputs, no user-interaction mid-work), produces large output the main session only needs summarized, or is parallel-able. Stay in the main session when work uses already-loaded context, needs iterative user interaction, or is a single quick read/edit. Concretely:
- **Web research** — always delegate to a `general-purpose` agent with a focused question; never run WebSearch inline. Frame queries as questions (e.g., *"how do mature multi-agent systems declare skill interface contracts?"* not keyword bags). Per round-6: prior agent's web research was acknowledged as incomplete — do a deeper round.
- **Cross-skill inventory fan-out** (reading >10 SKILL.md files for the inventory) — delegate per family to a sub-agent.
- **Prototyping** — each candidate-mechanism prototype on a real skill is its own bounded unit; delegate via spawned implementation-flavored agent or write directly if the prototype is small.

**Prototype phase is mandatory.** §3.1 of file 08 is paper design. Validate by prototyping on 2-3 representative skills (e.g., `ui-create-scribble`, `code-simple`, `task-create`) showing the proposed contract in concrete YAML + a ≤80-line lint script that catches one real violation. Without prototypes, the recommendation is unsubstantiated.

## Output

A future implementer reading the synthesis + prototypes can answer:
- Which contract mechanism we adopt and why (one of: sidecar / frontmatter / registry / hybrid)
- The minimal required contract fields every skill MUST declare
- How violations are detected (lint, CI, runtime guard) and where they're reported
- Which skills are split into sub-skills, which stay bundled, and the rubric
- The bidirectional-feedback pattern (channel structure, escalation, orchestrator changes)
- The revision_request-vs-task taxonomy with worked examples
- The migration sequence — which skill family adopts first, what the rollout looks like, how stale duplicates are removed
- Whether REQ-PROC-044 needs new ACs (yes/no + which)

**Per developer round-5 S2**: handoff files alone are dead ends. The synthesis MUST end by either creating concrete follow-up tasks via `task-create` (the rollout work the recommendation implies) OR documenting why no immediate follow-up is needed. Tasks are the only real integration mechanism.

## Acceptance Criteria

- [x] Exploration produced at least one synthesis round (Round 1, Round 2 via agent, Round 3 — plus Round 4 covering external interfaces; documented in `plans_and_protocols/03_round_1_synthesis.md`, `04_round_2_prototype_summary.md`, `05_round_3_synthesis.md`, `07_external_interfaces.md`, `09_amendments.md`)
- [x] The synthesis defines the problem space in terms that were not fully known at task creation (e.g. the source: annotation requirement surfaced only in Round 2 prototyping; the session-mechanics clarification for revision_target.yaml surfaced only in user feedback; cleanup discipline requirements emerged in dialogue)
- [x] Decisions requiring user input are identified and framed clearly enough for the user to decide (6 OPEN decisions framed in 05_round_3_synthesis.md; user confirmed via AskUserQuestion and provided feedback in files 06 and 08; amendments in 09)
- [x] The output is honest about what remains uncertain (Round 3 §7 lists 11 numbered uncertainties; Round 4 §6 + Round 2 summary §"Honest list of what the prototype could NOT validate")
- [x] Prototype: candidate contract mechanism applied to ≥2 representative skills with concrete YAML (3 skills prototyped: `prototypes/contract_ui-create-scribble.yaml`, `prototypes/contract_code-simple.yaml`, `prototypes/contract_task-create.yaml`; plus 2 schemas)
- [x] Prototype: ≤80-line lint script that catches ≥1 real interface violation (`prototypes/check_skill_contracts.py` — 76 lines of code, tier B; `prototypes/lint_demo_run.md` shows the demo catching a path-rename violation with the specific actionable error format from web research §Q5)
- [x] Follow-up tasks created via `task-create` for the rollout work (per S2 — handoff files alone are dead ends) — 8 tasks created: TASK-PROC-044-03 (Wave 1 producers), -04 (Wave 2 consumers), -05 (Wave 3 + sunset), -06 (revision channel + cleanup), -07 (SCRIBBLE-SPLIT), -08 (rubric codification), -09 (factory-map + token measurement), -10 (external interfaces explore). All seeded in `task_ordering_priority_override.txt`. Parent TASK-PROC-032-10 marked `awaiting:` the 8 new tasks.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-032-10 | in_progress | Parent exploration; this task is its spin-off. TASK-PROC-032-10 resumes (iteration 6) AFTER this task completes |
| TASK-PROC-057-01 | pending | Parallel apex exploration; integrate its constraints if it completes during this work |

## Notes

This exploration is paused work in TASK-PROC-032-10 (the scribble–coder-contract exploration). The 5 iteration documents in TASK-PROC-032-10's `plans_and_protocols/` are required reading; they capture the analysis that led to spinning this task out. The 10 downstream bundles in that exploration's iteration-4 §9 are explicitly deferred until this task returns.

Added to `task_ordering_priority_override.txt` to ensure execution priority over the paused release-0.0.1 implementation chain (per file-12 §7 total-cost recommendation).
