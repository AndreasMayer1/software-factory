---
skills_used:
  - claude-automated-mode
  - claude-route
  - task-resolve
  - claude-modify-skill
  - claude-log
  - task-complete
  - claude-commit
---

# Protocol: task-create-code automated structural check (TASK-PROC-001-07)

Date: 2026-06-02
Agent: a63355a5-7097-47a9-badd-587fe571078c
Automated: yes

## What changed

All edits routed through `claude-modify-skill`.

### `.claude/skills/task-create-code/SKILL.md`
- **Phase 2.2** — replaced "Spawn Quick Explore Agent" (Task tool) with **Automated Structural
  Check**: deterministically count distinct files from the proposed scope's explicit paths + globs
  via `git ls-files -- $SCOPE_GLOBS $SCOPE_PATHS | sort -u | wc -l`, plus untracked new-file paths.
  Result `file_count` is recorded in the protocol as the reproducible tier basis (removes run-to-run
  LLM variance).
- **Phase 2.3** — retitled "Estimate Size (two co-equal signals)". File-count tiers preserved; added
  `skill_chain_depth` as a **co-equal** signal. Either signal crossing its threshold triggers the
  higher tier (take the max): Small ≤3 files & depth ≤2; Medium 4-8 files or depth 3; Large 8+ files
  or depth ≥4 → Split NOW. `file_count` → `expected_tool_calls`; depth → `skill_chain_depth`.
- **Phase 3.3g** — noted the tier now derives from the structural check + skill-chain depth; the
  existing tier → `opus_recommended` mapping table is preserved (signal source change only).
- **Phase 3.3h (new)** — declare ≥1 of `expected_tool_calls` / `skill_chain_depth` (AC-01), then
  apply the **Sizing Gate (AC-03)**: trigger `expected_tool_calls > 60` OR `skill_chain_depth >= 4`;
  require one of {opus_recommended, child-split, named fan-out plan}; interactive warn / automated block.
- **Frontmatter template** — added `expected_tool_calls` + `skill_chain_depth` lines (AC-01),
  matching the wording 001-06 used in `task-create`.
- **Automated Mode table** — added a Sizing Gate row (block: split or fan-out plan).
- **Frontmatter `tools:`** — dropped `Task` (its only consumer, the Quick Explore Agent, was removed).

### `.claude/skills/task-create-code/contract.yaml`
- Registered the **Sizing Gate** `user_input_gate` (decision_kind: selection, required: conditional).

## Not changed
- `.claude/schemas/goal_metadata.yaml` — fields `expected_tool_calls`, `skill_chain_depth`,
  `synthesis_*`, `discovery_command` already added by TASK-PROC-001-06. No schema change needed.
- `INDEX.md` — description unchanged.
- `factory_flows.md` — edge label "scope estimation" still accurate (internal mechanism change only).

## Verification
- `python3 scripts/quality/check_skill_contracts.py` — `task-create-code` passes (clean). The 3
  reported violations are pre-existing and unrelated (`claude-write-hook` has no contract.yaml).

## AC mapping
- **AC-01** — goal.md template + Phase 3.3h require ≥1 of `expected_tool_calls` / `skill_chain_depth`;
  values are deterministic and visible to creation-time tooling.
- **AC-03** — Sizing Gate (Phase 3.3h + Automated Mode row + contract gate) enforces one of the three
  end states for high-volume tasks.
