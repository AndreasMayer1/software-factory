---
task_id: TASK-PROC-045-08
type: explore
parent_requirement: REQ-PROC-045
urgency: 3
urgency_reason: U3-FIX
impact: 4
impact_reason: I4-ENAB
status: completed
effort: L
created: 2026-05-28
started: 2026-05-28
completed: 2026-05-28
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: [SEC-03]
scope_description: "Extend REQ-PROC-045 to define a sanctioned-taxonomy mechanism (single-axis-per-level, anchor files, placement algorithm, governance gate) across process/, non-functional/, and functional/; remove §3 carve-out for process/ and non-functional/; differentiate epic boundary tests per category. Migration policy and enforcement extension are split out into follow-up tasks."
release_description: ""
opus_recommended: true   # reason: cross-cutting structural-quality decision touching three top-level folders, multiple existing skills, and the LLM-judgment side of placement
writes_requirements: true
requirements_version:
  commit: c829ed37
  file: ../requirements.md
---

# Goal: Extend Epic Enforcement to process/ (and evaluate non-functional/) — modify REQ-PROC-045

## Objective

REQ-PROC-045 §3 ("Organizational Folder Semantics", around line 136) explicitly exempts `process/` and `non-functional/` from the `epic_*/feat_*` enforcement rule that governs `functional/`. That carve-out is load-bearing: it legitimises the loose, deep, unsignposted folder shape `process/AI_rules/` has drifted into, where overlapping clusters (`requirements_management/` ↔ `workflows/`, `factory_quality/` ↔ everything) make it hard for both humans and LLM sessions to find the right place to add a new requirement.

This exploration should discover **whether and how** to remove that carve-out for `process/`, what stricter epic-content rules would replace the gap left behind, and whether the same rule should extend to `non-functional/`. The output is a modification of REQ-PROC-045's text and ACs — not a new requirement, and not the actual restructuring of any existing folder (that is downstream impl work under the updated REQ-PROC-045).

## Background

TASK-PROC-063-01 (`epic_factory_skill_chain`) attempted to write a new epic-level requirement (REQ-PROC-063) for end-to-end factory skill chain integrity and discovered that REQ-PROC-063 could not be placed cleanly into `process/AI_rules/` because the existing taxonomy is unprincipled — and the unprincipled state is *permitted* by REQ-PROC-045's carve-out. That synthesis is at:

```
requirements_tasks/process/AI_rules/workflows/epic_factory_skill_chain/tasks/2026-05-27_explore_factory-skill-chain-epic (completed)/plans_and_protocols/2026-05-28_01_synthesis.md
```

Read it as context, not as a plan.

REQ-PROC-045 today defines (and these stay correct as-is):
- WHO–WHAT naming pattern (DDD ubiquitous language + semantic cohesion)
- Three epic boundary tests (independent value, domain entity, parallel development)
- "Depth via grouping, not nested epics" rule
- LLM judgment checklist (10 questions)
- Cross-reference completeness detection (AC-11)
- Validation enforcement at `requ-explore` Phase 1 + `release-begin-impl` Phase 0

The boundary tests were authored for `functional/` and may not translate cleanly to `process/` epics, which often govern continuous quality rather than discrete user-visible value. The "Independent value" test, in particular, is suspect — process epics deliver value to the development workflow, not to end users.

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-05-28_00_user_initial_input.md`

Read it as a seed bed, not a spec.

For complete requirements at task creation time:
```
git show c829ed37:requirements_tasks/process/AI_rules/requirements_management/requirements_structure_quality/requirements.md
```

Current requirements: ../requirements.md

## How to Approach This

Use design thinking as the guiding process — empathize before defining, diverge before converging, let questions lead, iterate. A single pass through the material will not be enough. Surface surprises — the most valuable discoveries are the ones that were not anticipated.

The modification of REQ-PROC-045 should be **targeted** (Scenario E of requ-explore): remove the carve-out, add the new content, do not rewrite existing sections beyond what the change requires. Show any contradiction or content-loss to the user before applying.

## Seeds

1. **Do the three epic boundary tests survive translation to process/ epics?** The "Independent value" test was framed for user-visible features — process epics deliver value to the development workflow, not to end users. The "Domain entity" test assumes a clear primary entity — process epics often span multiple artifact types (skills, scripts, requirements, tasks). The "Parallel development" test may or may not apply when the "developers" are mostly LLM sessions doing one-shot edits. Either reformulate the tests for process/ or accept a different boundary heuristic.

2. **What is the right shape for non-functional/?** It currently has bare topic folders (`architecture/data_versioning/`, `architecture/logging/`, `ui_ux_design_system/accessibility/`). Some of these are one-shot — a single requirement that completes and stays implemented. Others (the design system) genuinely have many sub-rules. Is the right rule "epic_-required like functional/", "epic_-required only when there's already a second sibling", or "exempt — keep flat"? The answer probably differs across non-functional/ sub-areas.

3. **Stricter epic-content rules.** Today's Epic Size Gate enforces a 90-line body and a fixed section list. The user's framing — "epics are kind of what you already have suggested with the readme files, but with more strict rules what they must contain" — suggests epics need an *inclusion-criteria* section that names what kinds of requirements/features the epic accepts, and an *anti-scope* section that names what the epic explicitly excludes. These would be the things the LLM consults when deciding where to place a new requirement. Define these new mandatory sections, including how they avoid duplicating SEC-03 / §Scope content already in epic requirements.md files.

4. **Migration policy for existing violations.** `process/AI_rules/` has dozens of bare topic folders today. Options: (a) Strangler Fig — gradually convert clusters of related bare folders into `epic_*/feat_*` shape over multiple tasks; (b) grandfathering — only require the new shape for new requirements; (c) forced refactor — one big restructure. Each has different cost, risk, and chain-of-custody implications. Decide which becomes the default rule in REQ-PROC-045 and which becomes the recommended path for the actual restructuring impl tasks.

5. **Overlap with REQ-PROC-049 (Language Coherence).** REQ-PROC-049 governs the *language* layer above the structural layer — names, states, operations. If folder names start carrying inclusion-criteria semantics (seed 3), does that increase or decrease the language-coherence burden? Are there new failure modes (e.g., an epic's inclusion criteria contradicting its name)?

6. **Interaction with REQ-PROC-058 AC-17 (cross-reference completeness gate).** REQ-PROC-045 AC-11 defines the detection mechanism; REQ-PROC-058 AC-17 defines the gate that invokes it during `task-derive-from-requ`. If epics gain explicit inclusion criteria + anti-scope, the cross-reference detection could become *targeted* — instead of grepping the whole corpus, the detector could first match the new requirement against epic inclusion criteria. Worth considering, but may be premature.

7. **Top-level grouping folders inside categories** — `client/`, `therapist/`, `shared/` under `functional/`; `architecture/`, `requirements_management/`, `workflows/` under `process/AI_rules/`. These are organizational folders, not epics. The new rules must keep them legitimate. Codify the distinction crisply enough that LLM placement decisions don't get confused.

8. **The `feat_*` standalone case under groupings** — `functional/shared/feat_donations/`, `feat_education/`, etc. exist directly under a grouping with no enclosing epic. Today's REQ-PROC-045 §3 explicitly allows this. Does the same allowance carry over to `process/`? Or should process/ require everything to belong to some epic, even at the cost of premature epic creation?

## Execution Model

Gather raw material — read artifacts, follow threads, surface facts and anomalies. Synthesize iteratively; multiple gathering rounds may be needed before the problem space is well understood.

The session's model is fixed at launch (Opus when `opus_recommended: true`, Sonnet otherwise). No mid-session model switching.

**Web research**: For seeds requiring external knowledge — best practices, prior art, tool capabilities, what others have tried — use web search. Always delegate web research to a spawned `general-purpose` agent with a focused question; never run WebSearch inline. Raw web content inflates the gathering agent's context window fast with irrelevant results; the subagent returns only a distilled summary while the raw content stays in its own context.

Frame search queries as questions rather than keyword bags — this produces more useful results (e.g. *"how do large knowledge-base projects partition rules-as-code across categories without per-folder size limits?"* rather than *"knowledge base folder structure"*). When a snippet is insufficient, instruct the subagent to use WebFetch to read the full page before summarising.

## Output

The modified `requirements.md` of REQ-PROC-045, plus the synthesis trail in `plans_and_protocols/`. Specifically:

- The §3 carve-out for `process/` is removed (or explicitly replaced with a narrower carve-out, justified in the synthesis).
- New mandatory sections / ACs codify the stricter epic-content rules (inclusion criteria + anti-scope) — or a documented decision to NOT codify them, with rationale.
- A documented decision on non-functional/'s policy (extend, partially extend, exempt) with the reasoning visible in the requirements text.
- A documented migration policy for existing violations.
- The validation script's responsibilities (if changed) are listed as work to extend in follow-up impl tasks — this task does NOT touch `scripts/quality/` or `scripts/validate_epic_requirements.py`.
- The actual restructuring of `process/AI_rules/` folders is NOT done here.
- REQ-PROC-063 placement remains deferred until after this modification lands (TASK-PROC-063-02 is parked with `awaiting:` pointing at this task).

## Acceptance Criteria

- [x] Exploration produced at least one synthesis round
- [x] The synthesis defines the problem space in terms that were not fully known at task creation
- [x] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [x] The output is honest about what remains uncertain

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-063-01 | completed | Discovery task that surfaced this work (deferred REQ-PROC-063) |
| TASK-PROC-063-02 | parked | Will resume only after this modification lands and `process/` has been restructured |
