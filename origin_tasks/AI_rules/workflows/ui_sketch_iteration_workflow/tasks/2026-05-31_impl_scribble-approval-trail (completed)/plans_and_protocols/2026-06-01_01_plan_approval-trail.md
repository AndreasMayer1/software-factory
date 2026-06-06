# Plan: TASK-PROC-032-25 — APPROVAL_TRAIL.md

## Deliverable
Add a new step to `ui-scribble-approve-handoff` that emits `APPROVAL_TRAIL.md` on approval.

## Data Sources (from existing scribble structure)
- `scribbles/v{n}/metadata.yaml` — `design_decisions` + `gaps_fixed` fields per version
- `scribbles/v{n}/feedback.md` — auto-review brief + developer feedback
- Inter-version diffs: derived by reading v{n} and comparing to v{n-1} metadata/feedback

## Output Location
`scribbles/APPROVAL_TRAIL.md` (sibling of all version folders, at feature level)

## APPROVAL_TRAIL.md Structure
```markdown
# Approval Trail — <feature_path>
Requirement: <req_id>
Approved Version: v{n}
Approved: <date>

## Version History
### v1 — <date> — <status>
#### Design Decisions
- <decision> (<reason>)
#### Developer Feedback
<content of feedback.md Feedback section>

### v2 — <date> — approved
#### What Changed
<content of feedback.md What Changed section>
#### Design Decisions
- <decision> (<reason>)
#### Developer Feedback
<content>

## Locked Decisions (Final Version)
<design_decisions from approved version>
```

## Skill Changes
1. `SKILL.md`: Add Step 5 after handoff emission, before flow composite index
2. `contract.yaml`: Add APPROVAL_TRAIL.md to `produces`

## Execution
Inline — 2 files to modify.
