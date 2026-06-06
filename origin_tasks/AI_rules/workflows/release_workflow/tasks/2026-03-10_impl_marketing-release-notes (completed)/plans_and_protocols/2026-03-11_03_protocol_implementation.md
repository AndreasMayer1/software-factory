# Protocol: TASK-PROC-036-04 Implementation

**Date**: 2026-03-11
**Status**: Complete

## What was done

TASK-PROC-036-04 delivers the marketing release notes generation logic as a verbatim spec
document, rather than editing the release skill directly. TASK-PROC-036-01 owns the skill file
and will embed this spec as Step 4.

## Deliverables

1. `plans_and_protocols/2026-03-11_01_plan_marketing-release-notes.md` — plan document
2. `plans_and_protocols/2026-03-11_02_spec_marketing-notes-section.md` — **primary deliverable**:
   the verbatim Step 4 section for the release skill

## Key decisions

**Spec document approach** (not direct skill edit): The release skill doesn't exist yet;
TASK-PROC-036-01 owns it. Writing a spec document avoids file coordination problems between tasks.
TASK-PROC-036-01 must read this spec and copy everything from `## Step 4` onward into the skill.

**Generation algorithm via mapping table**: The original draft told Claude what fields to extract
but not how to use them. The improved spec adds a `description/goals/includes` → prose mapping
table so Claude knows which field drives which part of the output.

**Stability framing as mental model**: Rather than a comparison list, the spec frames it as a
question Claude asks before writing: "What does the app do now that it didn't before?" This is
more actionable during generation.

**Donation prompt guidance added**: SEC-05 specifies that a donation prompt is optional and
only for significant new features. This was missing from the original draft. Alpha/PoC releases
are explicitly excluded.

**Bug-fix-only release example added**: The original only showed a feature release example.
Adding a bug-fix example gives Claude a second reference point for the most common release type.

**Nested code fence problem fixed**: The original used triple backticks to wrap the verbatim
section, then used triple backticks again inside for examples — this breaks markdown rendering.
The improved version uses 4-space indented code blocks for examples and no outer wrapper.

## TASK-PROC-036-01 integration note

When creating `.claude/skills/release/skill.md`, the agent must:
1. Read this spec file
2. Copy everything from `## Step 4 — Marketing release notes` through `### 4.7 Write approved files` verbatim
3. The path to this spec: `requirements_tasks/process/AI_rules/workflows/release_workflow/tasks/2026-03-10_impl_marketing-release-notes/plans_and_protocols/2026-03-11_02_spec_marketing-notes-section.md`
