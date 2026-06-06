---
task_id: TASK-PROC-044-09
type: impl
parent_requirement: REQ-PROC-044
urgency: 4
urgency_reason: U4-BLOCKING
impact: 4
impact_reason: I4-QUAL
status: completed
effort: M
created: 2026-05-29
started: 2026-05-30
completed: 2026-05-30
session_completed_at: 2026-05-30T01:19:09Z
after: [TASK-PROC-044-03]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-02, AC-06]
  sections: []
scope_description: "Build the factory-map render script (Cytoscape.js JSON + static HTML viewer with filters) reading contracts + schemas + factory_flows.md. Include script-call edges decorating skill nodes (inferred from may_invoke + side_effects). Author PreToolUse/PostToolUse Read-tool hooks logging file path + active task ID + bytes per session. Aggregator script computes per-file/per-skill read-frequency. Render heat overlay on factory-map nodes. Feed read-frequency events into .factory/optimize/events/ for claude-optimize consumption. Document the AC-06 interpretation (single-location read via the factory-map artifact) in this task's plans_and_protocols/."
release_description: ""
opus_recommended: false   # reason: focused infrastructure work — render script + hooks + visualization; tier-B scripts
writes_requirements: false
requirements_version:
  commit: b10665f5
  file: ../../requirements.md
source_exploration: TASK-PROC-044-02
bundle_id: FU-7
session_id: 3a916971-89e4-4210-855d-53be90f2207c
session_account: gmail

---
# Goal: Factory-Map Render + Token-Cost Measurement + AC-06 Interpretation

## Objective

Build the single-location-read artifact that satisfies REQ-PROC-044 AC-06 ("active skills + artifact dependencies + ordering rules documented in single authoritative location"). The artifact is an interactive HTML view rendered from the contract graph + schemas + factory_flows.md, with read-frequency heat overlay.

## Background

The exploration in TASK-PROC-044-02 noted (in §05_round_3_synthesis.md §D-6) that AC-06's "single authoritative location" property is satisfied per-dimension (skills in `.claude/skills/`, contracts in sidecar `.yaml`, ordering in `.claude/task_ordering_rules.yaml`, flows in `factory_flows.md`) — but not globally. The factory-map render script produces a single readable artifact aggregating all dimensions, addressing AC-06's literal interpretation.

Per `09_amendments.md` §A-4, FU-7 also absorbs token-cost measurement (hooks + aggregator + heat overlay).

## How to Approach This

1. Read `05_round_3_synthesis.md` §D-6 + `09_amendments.md` §A-4.
2. Build `scripts/factory/render_factory_map.py` (use `claude-write-script`):
   - Read all `.claude/skills/<name>/contract.yaml` (post-Wave-1 these exist for at least the 4 producer skills; the script handles partial migration gracefully)
   - Read all `.claude/schemas/*.yaml`
   - Read `factory_flows.md`
   - Output: Cytoscape.js JSON format (`{nodes:[], edges:[]}`)
     - Nodes: skills + artifacts (typed)
     - Edges: producer→artifact, artifact→consumer (with derived_from condition), skill→skill via may_invoke, skill→script (decoration)
   - Wrap the JSON in a static HTML viewer using Cytoscape.js (~150KB CDN load is fine; or vendor the library)
3. Implement filters in the HTML viewer:
   - By family (code-*, ui-*, requ-*, task-*, etc.)
   - By artifact type (.yaml schema, .md skill, .py script, generated file)
   - By may_invoke graph distance from a chosen node
4. Author the Claude Code hooks:
   - PreToolUse on `Read` — logs `{tool: "Read", file_path, session_id, task_id, timestamp}` to a session-scoped log file
   - PostToolUse on `Read` — records bytes read (from the tool result)
   - Settings.json wiring (per CLAUDE.md update-config skill)
5. Build `scripts/factory/aggregate_read_metrics.py`:
   - Walk session log files
   - Aggregate per-file and per-skill read-frequency
   - Output JSON suitable for the factory-map heat overlay
6. Wire the aggregator to emit `.factory/optimize/events/*.json` for `claude-optimize` to consume — exposes high-read files as candidates for optimization (caching, sectioning, references-instead-of-inline)
7. Update the HTML viewer to load the heat data and color/size nodes accordingly
8. Document the AC-06 interpretation in this task's `plans_and_protocols/`: which file IS the AC-06 "single authoritative location"? Answer: the rendered HTML at a canonical path (e.g. `releases/<v>/factory_map.html` or `requirements_tasks/STATUS.factory_map.html`). The script regenerates on demand; CI can regenerate per commit.

## Acceptance Criteria

- [x] `scripts/factory/render_factory_map.py` exists, tier B, passes Python gates
- [x] Output Cytoscape.js JSON is valid (loads without errors in the HTML viewer)
- [x] HTML viewer renders the full graph with filters working (by family, artifact-type, distance)
- [x] Script-call edges present on skill nodes (where may_invoke or side_effects name a script)
- [x] PreToolUse + PostToolUse hooks present in `.claude/settings.json` (or settings.local.json); logging works
- [x] `scripts/factory/aggregate_read_metrics.py` produces aggregated heat data; tier B; passes Python gates
- [x] Heat overlay renders on factory-map nodes (color/size driven by aggregated data)
- [x] `.factory/optimize/events/*.json` emission verified (a read-heavy file produces an event)
- [x] AC-06 interpretation documented in this task's `plans_and_protocols/` with the canonical path of the rendered artifact

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-044-03 (Wave 1) | pending (soft) | The script tolerates partial contract migration but is most useful once Wave 1 lands; can develop in parallel using prototype contracts |

## Notes

This task is in `flutter_app/.claude/task_ordering_priority_override.txt`. The "should we include script calls?" question from the round-3-followup feedback was answered YES (as edge decorations on skill nodes for v1); promoting scripts to first-class nodes with their own contracts is a Wave-3+ refinement.
