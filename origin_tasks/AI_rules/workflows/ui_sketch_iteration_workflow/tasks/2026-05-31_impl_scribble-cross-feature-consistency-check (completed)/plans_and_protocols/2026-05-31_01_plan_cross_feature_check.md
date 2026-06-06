# Plan: Cross-Feature Consistency Check (AC-35)

Date: 2026-05-31
Task: TASK-PROC-032-17

## Goal

Add a cross-feature consistency check invoked from `ui-scribble-auto-review` that flags
divergent component choices for the same role across sibling-feature scribbles sharing a
user flow, for human resolution.

## Approach: Inline (no sub-agents needed for planning)

## Deliverables

1. **New agent**: `.claude/agents/ui-scribble-cross-feature-checker.md`
   - Cheap model (haiku); spawned by `ui-scribble-auto-review`
   - Reads current scribble's `flow_positions` + `flutter_component_mapping`
   - Finds sibling scribbles sharing the same `flow_id` under `requirements_tasks/scribbles/`
   - Compares `flutter_component_mapping` keys: same key → different widget = divergence
   - Fallback: reads HTML when mapping metadata absent
   - Outputs structured divergence table flagged "human resolution needed"

2. **Modified skill**: `.claude/skills/ui-scribble-auto-review/SKILL.md`
   - Step 1: add `ui-scribble-cross-feature-checker` as 4th parallel reviewer,
     gated on `flow_positions` present in `metadata.yaml`
   - Step 2: include cross-feature findings in merged gap list
   - No change to contract.yaml inputs (checker reads scribble tree itself)
   - contract.yaml: add checker to side_effects/quality_criteria

## Integration Points

- Per-flow walk: when `flow_positions` exists, checker naturally integrates because
  the flow IDs drive sibling discovery
- Standalone: when no `flow_positions`, checker outputs NO_FLOW_POSITIONS and is omitted
  from the merged gaps — zero overhead

## Status: IMPLEMENTING
