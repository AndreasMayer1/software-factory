---
task_id: TASK-OPT-20260603-ba333ffe
type: impl
parent_requirement: REQ-PROC-006
status: pending
created: 2026-06-03
awaiting: ["user-unblock"]
target_path: .claude/skills/claude-automated-mode/SKILL.md
optimization_target: skill_body
optimization_dimension: trigger_accuracy
source_event:
  event_type: skill_changed_and_used
  fingerprint: .claude/skills/claude-automated-mode/SKILL.md@ba333ffebbc0deda4869b2c1ea7a125adee246e3
  confidence: low
optimization_approach:
  web_research_recommended: false
  reason: "default: internal change"
---
# Goal: optimize `.claude/skills/claude-automated-mode/SKILL.md` (trigger_accuracy)

## Objective

The skill body's detection block relies on the LLM recalling CLAUDE.md rather than being self-contained, causing inconsistent invocation when context is partially summarized. Rewrite the Detection section to explicitly name both trigger signals so the skill is invocable without external memory.

## Source

Produced by claude-optimize (REQ-PROC-006). This task is
auto-blocked (`awaiting: ["user-unblock"]`) — the developer must
review and unblock before any executor picks it up (G-INV-1).

## Scope

Rewrite the Detection section so it clearly names both invocation signals (CLAUDE_AUTOMATED_MODE=1 env var and automation/.automated_mode file) and the MONITORING early-exit path. Verify: structural rubric in goal.md scores ≥ 3/3 (1 = both signals explicitly named in prose, 2 = detection bash check is the first executable step, 3 = MONITORING path terminates immediately without further work).
