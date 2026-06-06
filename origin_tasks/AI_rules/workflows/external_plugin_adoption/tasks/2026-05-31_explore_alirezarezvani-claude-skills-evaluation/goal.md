---
task_id: TASK-PROC-055-05
type: explore
parent_requirement: REQ-PROC-055
urgency: 2
urgency_reason: U2-OPP
impact: 3
impact_reason: I3-EFF
status: pending
effort: M
created: 2026-05-31
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: [SEC-03, SEC-04]
scope_description: "Evaluate https://github.com/alirezarezvani/claude-skills for factory-adoptable patterns, skills, and techniques using the REQ-PROC-055 evaluation framework"
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: 2c6d1a90
  file: ../requirements.md
---

# Goal: Evaluate alirezarezvani/claude-skills for Factory Adoption

## Objective

We do not yet know whether the skills in https://github.com/alirezarezvani/claude-skills contain patterns, techniques, or implementations worth absorbing into our factory. This exploration should produce a decision-ready assessment: what the repository offers, where it overlaps with or complements our existing skill set, and which items (if any) are worth adopting, adapting, or monitoring.

The output should be actionable — a prioritized list with rationale, not just a catalog.

## Background

Our factory has ~60 skills organized around orchestrated workflows, quality gates, and task lifecycle management. We have an established evaluation framework (REQ-PROC-055) for assessing external Claude Code tooling, previously applied to the `han` plugin (TASK-PROC-055-01). That framework defines a reusable capability taxonomy and scoring axes — this task applies it to a different repository.

The repository in question (`alirezarezvani/claude-skills`) is not yet assessed. We do not know its scope, philosophy, quality, or license.

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-05-31_00_user_initial_input.md`

Read it as a seed bed, not a spec.

For complete requirements at task creation time:
```
git show 2c6d1a90:requirements_tasks/process/AI_rules/workflows/external_plugin_adoption/requirements.md
```

Current requirements: ../requirements.md

## How to Approach This

Use the REQ-PROC-055 evaluation framework as the guiding process:
1. **Inventory** — catalog what the repository contains (skills, agents, workflows, patterns)
2. **Normalize** — map each item to the REQ-PROC-055 capability taxonomy (A–I)
3. **Overlap analysis** — find the nearest internal equivalent and classify (none / partial / full)
4. **Score** — apply the scoring axes per item
5. **Synthesize** — roll up to an adoption-level recommendation per item, then a prioritized list

Gather raw material using a spawned general-purpose agent that fetches the GitHub repo content and returns a distilled summary. Do not read raw web content inline — delegate to a subagent to protect context.

## Seeds

1. **What does the repository actually contain?** Are there skills, agents, hooks, or other structures? What is the apparent philosophy (evidence-first? YAGNI? review-focused? something else)?
2. **License and upstream risk** — what license does it use, and does it impose per-file attribution or coupling to a specific CLI version?
3. **Capability gaps** — are there capability taxonomy categories (A–I) that our factory currently covers weakly, and does this repo fill them?
4. **Philosophy alignment** — does the repository's approach conflict with our stateful, gate-enforced, pipeline-first model, or does it complement it?
5. **Adaptation cost** — for the highest-value items, what would it actually take to adopt them? Are they self-contained, or do they drag dependencies?

## Execution Model

Gather raw material — clone the full repository locally, read its structure, follow threads, surface facts and anomalies. Synthesize iteratively.

**Repository acquisition (mandatory)**: Clone the entire repository to a local temp directory before starting analysis. Do not fetch individual files via WebFetch — the full clone ensures no files are missed and avoids rate-limiting on partial fetches.

```bash
git clone https://github.com/alirezarezvani/claude-skills /tmp/alirezarezvani-claude-skills
```

Once cloned, read files directly from disk using standard file tools. Delegate analysis to a spawned `general-purpose` agent that works from the local clone and returns a distilled summary — do not flood the main context with raw file dumps.

## Output

A synthesis document in `plans_and_protocols/` that a future implementer can act on without re-reading this task. It should contain:
- A structured inventory of the repository's contents, mapped to the REQ-PROC-055 capability taxonomy
- Per-item scoring on the REQ-PROC-055 axes (overlap, gap-fill value, philosophy fit, self-containment, adaptation cost, re-test risk, attribution burden)
- A prioritized adoption candidate list with rationale and recommended action (adopt / adapt / monitor / skip)
- Honest identification of what remains uncertain after the exploration

## Acceptance Criteria

- [ ] Exploration produced at least one synthesis round
- [ ] The synthesis defines the problem space in terms that were not fully known at task creation (repository contents, license, philosophy)
- [ ] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [ ] The output is honest about what remains uncertain

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-055-01 | completed | han evaluation established the framework this task applies |
