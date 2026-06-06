---
task_id: TASK-PROC-058-10
type: impl
parent_requirement: REQ-PROC-058
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-ENAB
status: completed
completed: 2026-06-04
effort: XS
created: 2026-06-04
started: 2026-06-04
expected_tool_calls: 12
skill_chain_depth: 2
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Fix claude-route Mode A so type:explore tasks route by writes_requirements (true→requ-explore, else→task-resolve) instead of all going to requ-explore; align task-resolve description."
release_description: ""
opus_recommended: false
writes_requirements: false
requirements_version:
  commit: e680b5e9
  file: ../requirements.md
---

# Goal: Fix claude-route Explore Routing (route by writes_requirements, not bare type)

## Objective

`claude-route` Mode A step 4 currently routes **all** `type: explore` tasks to
`requ-explore`:

```
- `type: explore` or investigation goals → `requ-explore`
```

But `requ-explore` is "THIS SKILL MUST BE USED TO ADD OR MODIFY REQUIREMENTS" — it is
for *authoring* requirements. Many explore tasks are brainstorming / investigation /
evaluation that produce analysis or proposal documents and author no requirement
(e.g. TASK-PROC-032-28, the ralph-loop explore). Routing those to `requ-explore` is wrong.

Fix the routing to mirror the discriminator the rest of the factory already uses —
the `writes_requirements` frontmatter flag:

- `type: explore` + `writes_requirements: true`  → `requ-explore` (task authors/changes a requirement)
- `type: explore` + `writes_requirements: false`/absent → `task-resolve` (brainstorming / investigation / evaluation; deliverables are analysis/proposal docs, no requirement authored)

Also align `task-resolve`'s description, which currently reads as impl-only, so it
correctly reflects that it now also receives non-requirement explore tasks.

## Requirements Summary

REQ-PROC-058 (Implementation Task Planning Quality) documents `claude-route`'s
goal-shape detection / routing in its Workflow Integration section (the W-row table).
This task corrects one branch of that routing table; it implements no specific AC.

For complete requirements at task creation time:
```
git show e680b5e9:requirements_tasks/process/AI_rules/requirements_management/implementation_task_planning/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- `.claude/skills/claude-route/SKILL.md` — Mode A step 4 explore routing rule (split by `writes_requirements`).
- `.claude/skills/task-resolve/SKILL.md` — description (no longer impl-only).
- Both edits performed via the `claude-modify-skill` skill (mandatory), with INDEX.md sync where the description changes.

### Out of Scope
- Adding a new task `type` (e.g. `type: requ`). Considered and **rejected** — see Decision Context.
- Any change to `next_tasks.py` ordering, `release_readiness.py` staging/gating, or the
  `task_ordering_rules.yaml` `-10000` `writes_requirements` weight. Investigation (this
  session) confirmed the far-future-requirement shipping concern is already handled by
  `release_readiness.py` stage logic (authoring tasks go non-blocking once packages are
  assigned). No change needed there.
- `task-create` — its Explore Goal Template already emits `writes_requirements` (line ~561)
  and `requ-derive-from-flow` sets it `true`, so the routing signal is already reliable on
  new tasks. No edit required.

## Decision Context

A new task type (`type: requ`) was considered for disambiguating requirement-authoring
explores from brainstorming explores. It was **rejected**, for the same reason the prior
task **TASK-PROC-034-18** (`release_version_management/.../2026-04-22_explore_next-task-prioritization-fix`)
rejected it when it introduced `writes_requirements`:

> "Add a new `type: derive` (…). Rejected — more invasive (every `type`-reading script
> needs updating, CLAUDE.md task-type docs need updating, validator enum expansion) for
> no semantic advantage over a boolean."

The metadata schema (`.claude/schemas/goal_metadata.yaml`) deliberately consolidated
`define`/`review`/`analyze` into `explore` — fewer types, not more. `type == "explore"`
is overloaded across ≥5 code sites (`next_tasks.py` `--type`, the AC-coverage guard,
`_layer_intra_type_rank`, the ordering layers, `release_readiness.py` `non_impl_types`),
whereas `writes_requirements` is the clean, single-purpose signal. Routing on the boolean
keeps `claude-route` consistent with `next_tasks.py` and `release_readiness.py`, which
already key on it.

Full investigation synthesis: `plans_and_protocols/2026-06-04_01_synthesis_routing-and-ordering.md`.

## Acceptance Criteria

- [x] `claude-route` Mode A step 4 routes `explore` + `writes_requirements: true` → `requ-explore`.
- [x] `claude-route` Mode A step 4 routes `explore` + `writes_requirements: false`/absent → `task-resolve`.
- [x] `task-resolve` description no longer reads as impl-only; INDEX.md kept in sync.
- [x] No new task type introduced; no ordering/readiness scripts changed.
- [x] Edits performed through `claude-modify-skill`.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

- Standalone redirect (task-create §3c) skipped by design: REQ-PROC-058 has 1 uncovered
  AC (95% coverage), but it is unrelated to this routing correction, which implements no
  specific AC. Documented override.
- Parent placement is a best-fit: no requirement cleanly owns the `claude-route` routing
  table; REQ-PROC-058 is the closest (it documents claude-route routing in Workflow
  Integration). Trivially movable if a better home emerges.
