---
task_id: TASK-OPT-20260603-44eef038
type: impl
parent_requirement: REQ-PROC-006
status: pending
created: 2026-06-03
awaiting: ["user-unblock"]
target_path: .claude/skills/code-complex/SKILL.md
optimization_target: skill_body
optimization_dimension: trigger_accuracy
source_event:
  event_type: skill_changed_and_used
  fingerprint: .claude/skills/code-complex/SKILL.md@44eef03890afdaaab42a03afdb470ef61d394620
  confidence: low
optimization_approach:
  web_research_recommended: false
  reason: "default: internal change — trigger rules are project-specific"
---
# Goal: optimize `.claude/skills/code-complex/SKILL.md` (trigger_accuracy)

## Objective

The code-complex skill was modified and then used with low confidence (stage=1). Its trigger description is too broad, lacking explicit SKIP conditions, which causes uncertain invocations. Sharpen the TRIGGER section with ≥2 concrete positive-match patterns and ≥1 explicit SKIP condition.

## Source

Produced by claude-optimize (REQ-PROC-006). This task is
auto-blocked (`awaiting: ["user-unblock"]`) — the developer must
review and unblock before any executor picks it up (G-INV-1).

## Scope

Add a TRIGGER section to code-complex/SKILL.md that lists ≥2 named positive-match conditions (e.g. 'new layer introduced', 'cross-layer refactor') and ≥1 explicit SKIP/negative-match condition. Verify: structural rubric [positive_conditions≥2, skip_condition≥1, trigger_section_chars≤800] scores 3/3.
