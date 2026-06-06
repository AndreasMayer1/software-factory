# Synthesis — claude-route explore routing + the requ-vs-release ordering question

Date: 2026-06-04 · Session investigation (interactive). This doc is self-contained so a
future agent need not re-derive it.

## 1. The trigger

`claude-route` Mode A step 4 routes **all** `type: explore` tasks to `requ-explore`:

```
- `type: explore` or investigation goals → `requ-explore`
```

`requ-explore` is for *authoring/modifying requirements*. But explore tasks come in two
flavours:
- **requirement-authoring** explores (write/extend a requirement) — e.g. ralph-loop
  (`writes_requirements: true`).
- **brainstorming/investigation/evaluation** explores — produce analysis/proposal docs,
  author no requirement — e.g. TASK-PROC-032-28 (`writes_requirements: false`).

Routing the second kind to `requ-explore` is wrong.

## 2. Options considered for the discriminator

| Option | Verdict |
|---|---|
| New task type `type: requ` (or `define`) for requirement-authoring | **Rejected** |
| Boolean `writes_requirements` as the routing discriminator | **Chosen** |

### Why not a new type
- Prior art: **TASK-PROC-034-18** (the task that *introduced* `writes_requirements`,
  2026-04-22, `release_version_management/.../2026-04-22_explore_next-task-prioritization-fix`)
  explicitly rejected a new type in its Opus plan, "Options Reconsidered → Option 3":
  > "Add a new `type: derive`… Rejected — more invasive (every `type`-reading script needs
  > updating, CLAUDE.md task-type docs need updating, validator enum expansion) for no
  > semantic advantage over a boolean."
- The schema (`.claude/schemas/goal_metadata.yaml`) deliberately **consolidated**
  `define`/`review`/`analyze` into `explore` (enum = `[explore, impl, verify, bugfix,
  optimize]`). Adding `requ` reverses that direction.
- `type == "explore"` is **overloaded** across ≥5 code sites: `next_tasks.py` `--type`
  choices, the AC-coverage suppression guard, `ranker._layer_intra_type_rank`, the
  ordering layers (`requirement_derivation`/`requirement_exploration`), and
  `release_readiness.py` `non_impl_types = {"explore"}`. A new type must be taught to all
  of them or it silently misbehaves.
- `writes_requirements` is already first-class and consumed by `next_tasks.py`,
  `release_readiness.py`, `check_requirements_ready.py`, `validate_meta.py`, the ordering
  rules, and the schema. Routing on it keeps the router consistent with the rest.

### Data at investigation time
- `type:` distribution: impl 389, explore 205, analyze 12, verify 9, optimize 6, bugfix 5,
  review 3, define 2 (+ 1 `functional`, 1 `explore+impl`).
- Among 205 explore tasks: `writes_requirements:true` 48, `false` 30, **absent 123**.
  (Absent default → `task-resolve`, the safe open-ended fallback. New tasks already get
  the field from task-create's template + requ-derive-from-flow, so absence is a legacy
  artifact only.)

## 3. The ordering/gating concern (raised mid-investigation)

**Concern:** does treating requirement-authoring tasks as high-priority force *all* such
tasks (including ones for a release 6 months out) to complete before begin-impl can start
coding the current release?

### How requirement-authoring tasks are scoped
`requ-derive-from-flow` **cannot** set `target_release`/`target_package` — the requirement
doesn't exist yet, so it hasn't been triaged into a package (assignment needs the full
cross-flow picture; that's `release-plan`'s job). The tasks it emits carry only
`suggested_release_chunk` (from the flow's `release_scope`) + `urgency`/`impact`.

### Ordering (next_tasks.py)
- `.claude/task_ordering_rules.yaml`: `writes_requirements: true` → `weight: -10000`.
- Sort key (`task_ordering/defaults.py make_sort_key`):
  `(special_flags_weight, is_next, layer_order, layer_intra_type_rank, req_not_active, -priority_score)`.
- `special_flags_weight` is **position 1**, *ahead of* `is_next` (release/package scope).
  So a `writes_requirements:true` task outranks in-scope impl tasks **globally** —
  including far-future ones. This is **deliberate**: TASK-PROC-034-18 put it there *because*
  these tasks have no package to scope by, and the "requirement before its impl" safety
  guarantee was judged more important. The front-loading is an accepted, low-frequency
  tradeoff (requirement-writing tasks are rare; usually tied to the active derivation push).
  Manual escape hatch: `priority_override` (load_priority_override) pins a chosen task.

### Gating (release_readiness.py) — the decisive finding
`detect_stage()` has explicit staging logic:
> "Stage 1 (requirements authoring) only blocks if Stage 2 (package assignments) is not
> yet satisfied. Once packages are assigned, any remaining authoring tasks are
> non-blocking process tasks unrelated to this release."

- The global, unscoped authoring check (`check_requirements_ready()` — lists *all*
  `writes_requirements:true` pending tasks, no release filter) gates **only at Stage 1**,
  and only `if not all_assigned`.
- Once packages are assigned (Stage 2 passed), `requ_blocking` is never re-checked.
  **Begin-impl (Stage 3), active (Stage 4), cut-release (Stage 5) do not wait on any
  authoring task.**

**Conclusion: a far-future requirement-authoring task does NOT block shipping.** The
architecture already protects the shipping concern.

### Residual friction (advisory only, neither blocks shipping)
1. Stage-1 muddiness: before package assignment, the global list shows every pending
   authoring task (incl. future-release ones) as "complete before assigning packages".
2. `next_tasks.py` front-loads far-future authoring tasks via the `-10000` global boost.

Latent lever if it ever hurts: `suggested_release_chunk` (present on the task, ignored by
ordering/readiness). Would need a chunk-label → release mapping confirmed before wiring.
**Not pursued** — out of scope; the shipping concern is already handled.

## 4. Decision

1. **Routing fix (this task, TASK-PROC-058-10):** boolean-only. `claude-route` routes
   `explore` by `writes_requirements`; `task-resolve` description updated. No new type, no
   schema/script/test churn, no ordering/readiness change.
2. **Ordering/gating:** no change needed. Shipping is not blocked (staging logic). The
   `-10000` global boost is a deliberate, documented tradeoff from TASK-PROC-034-18.

## 5. Key references
- `.claude/skills/claude-route/SKILL.md` (Mode A step 4) — the bug.
- `.claude/skills/requ-explore/SKILL.md` / `task-resolve/SKILL.md` — the two route targets.
- `.claude/schemas/goal_metadata.yaml` — type enum + consolidation note.
- `.claude/task_ordering_rules.yaml` — `writes_requirements` special_flag (`-10000`), layers.
- `scripts/task_ordering/{ranker.py,defaults.py}` — enrichment + `make_sort_key`.
- `scripts/tasks/next_tasks.py` — `--type` filter, AC-coverage guard.
- `scripts/release/release_readiness.py` — `detect_stage` (staging), `check_requirements_ready`.
- Prior task: `…/release_version_management/tasks/2026-04-22_explore_next-task-prioritization-fix (completed)/plans_and_protocols/2026-04-22_02_opus_plan.md`.
