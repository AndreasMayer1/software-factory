# Wave-2/3 Rubric Refinement Tracking

**Task:** TASK-PROC-044-08 · **Date:** 2026-05-30

## Purpose

This file collects rubric refinement proposals from Wave-2 (FU-2, TASK-PROC-044-06-equivalent)
and Wave-3 (FU-3) rollouts. Per Round 3 §7 bullet 11: the rubric was validated on one pipeline
(SCRIBBLE-SPLIT); expect refinements when applied to code-*, doc-*, claude-*, release-* families.

## Synthesis Gate

After Wave 3 completes, review all proposals below and either:
- **Confirm v1 holds** — add a "v1 confirmed" note here (no follow-up task needed)
- **Propose v2** — if ≥ 1 unresolved edge case changes signal definitions or the ≥2 threshold,
  create a follow-up task to update `claude-create-skill` §"Phase Split Decision"

## Pending Proposals

*(none yet — Wave 2 and Wave 3 not yet started)*

## How to File a Proposal

When FU-2 or FU-3 discovers a rubric edge case, add a `## Proposal N` section:

```markdown
## Proposal N

**Discovered by:** <task-id>
**Skill family:** <e.g. code-*, claude-*, release-*>
**Phase in question:** <description>
**Signal scores:** S1=? S2=? S3=? S4=? → Score=?/4
**Edge case:** <what the rubric got wrong or was ambiguous about>
**Proposed adjustment:** <new signal definition, weight, or threshold change>
**Status:** open | resolved | deferred
```
