---
task_id: TASK-OPT-20260603-abf7812f
type: impl
parent_requirement: REQ-PROC-006
status: pending
created: 2026-06-03
awaiting: ["user-unblock"]
target_path: .claude/skills/claude-commit/SKILL.md
optimization_target: skill_body
optimization_dimension: trigger_accuracy
source_event:
  event_type: skill_changed_and_used
  fingerprint: .claude/skills/claude-commit/SKILL.md@abf7812f14f1bdc6742a86216fd01c04cfdb26e2
  confidence: low
optimization_approach:
  web_research_recommended: false
  reason: "default: internal change — skill_body + trigger_accuracy does not match any external-reference rule"
---
# Goal: optimize `.claude/skills/claude-commit/SKILL.md` (trigger_accuracy)

## Objective

The claude-commit skill body lacks explicit TRIGGER/SKIP guidance, causing low-confidence invocations; adding a TRIGGER-when / SKIP section (matching the pattern used by claude-api) will make the invocation boundary unambiguous.

## Source

Produced by claude-optimize (REQ-PROC-006). This task is
auto-blocked (`awaiting: ["user-unblock"]`) — the developer must
review and unblock before any executor picks it up (G-INV-1).

## Scope

Add TRIGGER when: / SKIP: preamble to the skill body that lists the three invocation scenarios (task-complete, automated run, manual git commit request) and the one skip scenario (pre-commit hooks, git commands that are not commits). Verify: grep -qE 'TRIGGER when:|SKIP:' .claude/skills/claude-commit/SKILL.md exits 0.
