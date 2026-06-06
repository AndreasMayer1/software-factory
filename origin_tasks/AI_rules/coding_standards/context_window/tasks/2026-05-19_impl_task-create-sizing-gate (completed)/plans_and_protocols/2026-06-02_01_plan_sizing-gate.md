# Plan: task-create sizing gate (TASK-PROC-001-06)

## Deliverable
Edit `.claude/skills/task-create/SKILL.md` (via `claude-modify-skill`) to wire
REQ-PROC-001 AC-01/02/03 into task creation.

## Changes

1. **Standard Goal Template frontmatter** (currently lines ~518-543):
   - Add `expected_tool_calls` and `skill_chain_depth` (declare at least one) — AC-01.
   - Add `synthesis_dependent: true  # justification` (omit when false) — AC-02.
   - Add optional `discovery_command` field for open-scope (S2) tasks.

2. **Replace "Opus Recommendation Check" trigger table** (lines ~337-355) with
   refined complexity-based criteria from goal.md. Remove vague
   `urgency ≥ 4 AND impact ≥ 4` rule. Splitting preferred over escalation.

3. **New "### Sizing Gate (REQ-PROC-001)" section**: creation-time check —
   if `expected_tool_calls > 60` OR `skill_chain_depth >= 4`, require at least
   one of: `opus_recommended: true`, child tasks declared, or named fan-out
   plan in goal.md body — else block/warn (AC-03).

4. Reference REQ-PROC-001 §"Signals recap" (verified to exist at
   requirements.md:92) rather than restating the S1–S4 definitions.
   Keep within token budget.

## Approach
Inline (single artifact, clear shape). No agents. Route edits via
`claude-modify-skill` per CLAUDE.md.
