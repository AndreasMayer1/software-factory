---
task_id: TASK-OPT-20260603-b86670ca
type: impl
parent_requirement: REQ-PROC-006
status: pending
created: 2026-06-03
awaiting: ["user-unblock"]
target_path: .claude/skills/claude-write-script/SKILL.md
optimization_target: skill_body
optimization_dimension: trigger_accuracy
source_event:
  event_type: skill_changed_and_used
  fingerprint: .claude/skills/claude-write-script/SKILL.md@b86670ca0cd038fa144509c303ae713c8444d9c5
  confidence: low
optimization_approach:
  web_research_recommended: false
  reason: "default: internal change"
---
# Goal: optimize `.claude/skills/claude-write-script/SKILL.md` (trigger_accuracy)

## Objective

The claude-write-script skill was changed and used with low-confidence trigger accuracy (stage 1), indicating the SKILL.md trigger description may be ambiguous or under-specified for some invocation contexts (e.g. code-bugfix slim mode, task-resolve). Review and tighten the trigger wording to eliminate ambiguous cases and ensure consistent invocation across all skill entry points.

## Source

Produced by claude-optimize (REQ-PROC-006). This task is
auto-blocked (`awaiting: ["user-unblock"]`) — the developer must
review and unblock before any executor picks it up (G-INV-1).

## Scope

Sharpen the description field and any TRIGGER section in .claude/skills/claude-write-script/SKILL.md so invocation rules are unambiguous. Verify: structural rubric in .claude/skills/claude-write-script/SKILL.md scores >= 3/4 — (1) names specific file paths or extensions covered, (2) names at least one scenario or mode that must still invoke this skill despite seeming minor, (3) has no wording overlap with adjacent skills that could cause mis-routing, (4) all mandatory-invocation carve-outs listed in CLAUDE.md Section 7 are mirrored in the description.
