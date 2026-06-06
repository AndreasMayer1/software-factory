---
task_id: TASK-OPT-20260603-80c619b9
type: impl
parent_requirement: REQ-PROC-006
status: pending
created: 2026-06-03
awaiting: ["user-unblock"]
target_path: .claude/skills/code-bugfix/SKILL.md
optimization_target: skill_body
optimization_dimension: trigger_accuracy
source_event:
  event_type: skill_changed_and_used
  fingerprint: .claude/skills/code-bugfix/SKILL.md@80c619b958772dbb91ce2ef24a0a881b8315097e
  confidence: low
optimization_approach:
  web_research_recommended: false
  reason: "default: internal change"
---
# Goal: optimize `.claude/skills/code-bugfix/SKILL.md` (trigger_accuracy)

## Objective

The code-bugfix skill was changed and used with low trigger confidence; the skill body lacks explicit TRIGGER/SKIP conditions, leaving ambiguity about when to invoke it over alternatives (e.g. task-resolve). Add explicit TRIGGER and SKIP rules.

## Source

Produced by claude-optimize (REQ-PROC-006). This task is
auto-blocked (`awaiting: ["user-unblock"]`) — the developer must
review and unblock before any executor picks it up (G-INV-1).

## Scope

Review code-bugfix SKILL.md and add explicit TRIGGER (when to use) and SKIP (when not to use) conditions in the skill description or header. Verify: structural rubric scores ≥ 4/5 — (1) TRIGGER conditions present, (2) SKIP conditions present, (3) ≥1 positive example stated, (4) ≥1 negative example stated, (5) description ≤ 20 words.
