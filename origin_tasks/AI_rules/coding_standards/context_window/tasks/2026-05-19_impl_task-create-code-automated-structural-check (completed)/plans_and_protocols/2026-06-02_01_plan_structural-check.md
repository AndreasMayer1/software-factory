# Plan: task-create-code automated structural check (TASK-PROC-001-07)

Agent: a63355a5-7097-47a9-badd-587fe571078c

## Context

- Predecessor TASK-PROC-001-06 already wired REQ-PROC-001 AC-01/02/03 into the **sibling**
  `task-create` skill: added `expected_tool_calls`/`skill_chain_depth`/`synthesis_*`/`discovery_command`
  to `.claude/schemas/goal_metadata.yaml` (shared schema — already present, no schema change needed),
  replaced the Opus trigger table with complexity criteria, and added a **Sizing Gate** section.
- This task (001-07) applies the same treatment to `task-create-code`, plus the code-task-specific
  change in its goal scope: replace the **LLM Quick-Explore-Agent** file-count estimate (Phase 2.2/2.3)
  with a **deterministic structural check**, and make S1 (skill-chain depth) a **co-equal** signal
  alongside the file-count tiers.

## Edits to `.claude/skills/task-create-code/SKILL.md`

1. **Phase 2.2** — replace "Spawn Quick Explore Agent" (Task tool) with "Automated Structural Check":
   deterministically count distinct files in the proposed scope via `git ls-files` over the scope's
   explicit paths + glob patterns. No agent spawn.
2. **Phase 2.3** — keep file-count tiers; add `skill_chain_depth` as a **co-equal** signal. Either
   signal crossing its threshold triggers the higher tier (Small ≤3 files & depth ≤2; Medium 4-8
   files or depth 3; Large 8+ files or depth ≥4 → Split NOW). Preserve tier → opus_recommended mapping.
3. **Phase 3.3 frontmatter template** — add `expected_tool_calls` + `skill_chain_depth` (AC-01),
   mirroring task-create's wording. Add a "declare the sizing signals" gather step.
4. **Phase 3.3g opus_recommended** — note the tier now derives from the structural check + skill-chain
   depth (signal source change only; mapping preserved).
5. **New "Sizing Gate (REQ-PROC-001 AC-03)" subsection** — trigger `expected_tool_calls > 60` OR
   `skill_chain_depth >= 4`; require one of {opus_recommended, child-split, named fan-out plan};
   interactive warn / automated block. Mirror task-create.
6. **Automated Mode table** — drop the now-removed agent row, retitle Phase 2.3 row, add Sizing Gate row.

## Edits to `.claude/skills/task-create-code/contract.yaml`

- Register the Sizing Gate as a `user_input_gate` (selection, conditional).

## Execution

Route all skill edits through `claude-modify-skill` (mandatory). Schema unchanged.
