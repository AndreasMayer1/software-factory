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

# Protocol: task-create sizing gate (TASK-PROC-001-06)

Session: e1394763 (automated, web account)

## Done

Edited `.claude/skills/task-create/SKILL.md` (via claude-modify-skill route):

1. **Standard goal.md frontmatter template** — added `expected_tool_calls` /
   `skill_chain_depth` (≥1 required, AC-01), plus commented optional
   `synthesis_dependent` / `synthesis_justification` (AC-02) and
   `discovery_command` (open-scope S2 tasks).
2. **Opus Recommendation Check** — replaced the old trigger table (which had the
   vague `urgency ≥ 4 AND impact ≥ 4` rule) with six complexity-based criteria
   from goal.md. Splitting is now the stated default response to volume;
   escalation reserved for irreducible reasoning complexity.
3. **New "Sizing Gate (REQ-PROC-001 AC-03)" section** — creation-time check:
   trigger `expected_tool_calls > 60` OR `skill_chain_depth >= 4`; requires one
   of {opus_recommended, child-task split, named fan-out plan}; block in
   automated mode, warn+ask in interactive.
4. **Step 5c (Create goal.md)** — wired in "Declare the sizing signals",
   "Set opus_recommended", and "Apply the Sizing Gate" so the gate runs.
5. Referenced REQ-PROC-001 §"Signals recap" (verified at requirements.md:92)
   instead of restating S1–S4 — keeps token budget.

Supporting edits:
- `.claude/schemas/goal_metadata.yaml` — added `discovery_command` field
  (the other three fields were already declared).
- `.claude/skills/task-create/contract.yaml` — registered the Sizing Gate
  interactive checkpoint as a `user_input_gates` entry (decision_kind: selection,
  conditional).

## Verification

- `check_skill_contracts.py`: task-create contract passes. The 3 reported
  violations (claude-watch-tool-reliability, claude-write-hook, ui-verify-flutter)
  are pre-existing baseline failures in files this session did not touch.
- No INDEX.md / factory_flows.md change needed (description unchanged; internal
  logic refinement only). No new contract tokens. No CodeGraph (no code reading).
