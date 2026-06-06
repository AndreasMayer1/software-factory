# Plan: Contributing-Requirements and Participating-Flows Discovery (TASK-PROC-032-26)

Date: 2026-06-01
Session: 948c1786-a147-4abd-a873-2bea7709a8b9

## Context

AC-41 requires a discovery script that auto-populates `contributing_requirements` (primary +
cross-cutting) and `participating_flows` into `scribble_metadata.yaml` from `feature_path`,
the requirements matrix, and a UI-scope heuristic. A consistency lint checks that the primary
contributing requirement's `feature_path` matches the scribble's `feature_path`.

## Key Findings

### Schema state
- `contributing_requirements`: already in schema (required, array). Legacy `requirement: REQ-...`
  scalar also accepted as one-entry equivalent.
- `participating_flows`: NOT in schema yet. D30 was "Recovered" (not dropped). D41/D42 are dropped.
  We add `participating_flows` as an optional field (implementing D30).

### Existing scribbles
- Both v1+v2 of `therapist/data_transfer` use legacy `requirement: REQ-FUNC-007-01` scalar.
- Neither has `contributing_requirements:` array or `participating_flows:`.
- REQ-FUNC-007-01 has `feature_path: therapist/data_transfer` and `user_needs.implements_flows:
  [{id: FLOW-002}, {id: FLOW-003}]`.
- Consistency: primary requirement's feature_path == scribble's feature_path → CONSISTENT.

### Requirements structure
- Requirements at `requirements_tasks/functional/**/**/requirements.md`
- YAML frontmatter has `id`, `feature_path`, `user_needs.implements_flows[].id`
- Primary requirement discovery: grep for `feature_path: <value>` in all requirements YAML
- Cross-cutting heuristic: requirements sharing ≥1 flow ID with the primary AND having UI scope
  (UI scope = has `feature_path` field set, not a pure data/security requirement)

## Implementation Phases

### Phase 1: Schema — add `participating_flows`
File: `.claude/schemas/scribble_metadata.yaml`
Add under `optional:`:
```yaml
  participating_flows:
    type: array
    items: { type: string }
    description: >
      Flow IDs (e.g. [FLOW-002, FLOW-003]) that this scribble's screens participate in.
      Derived automatically from the primary contributing requirement's implements_flows list.
      Written by scripts/scribbles/discover_scribble_requirements.py.
```

### Phase 2: Discovery script
File: `scripts/scribbles/discover_scribble_requirements.py`
- Input: path to scribble metadata.yaml (or scribble directory)
- Algorithm:
  1. Read `feature_path` from metadata.yaml
  2. Search all `requirements_tasks/functional/` for req with matching `feature_path` frontmatter
  3. Primary = exact match (ambiguous if 0 or 2+)
  4. Parse primary req's `user_needs.implements_flows[].id` → participating_flows list
  5. Cross-cutting: requirements that (a) share ≥1 flow_id from participating_flows AND (b)
     have `feature_path` field set (UI scope heuristic) AND (c) are not the primary
  6. Write `contributing_requirements: [primary, ...cross_cutting]` to metadata.yaml
     (normalize legacy `requirement:` scalar to array form)
  7. Write `participating_flows: [FLOW-xxx, ...]` to metadata.yaml
  8. Run consistency lint: primary req's `feature_path` must match scribble's `feature_path`
  9. Flag ambiguities with YAML comment if any
- Exit codes: 0=ok, 1=error, 2=ambiguous (partial write, needs human review)
- Tier: B (infrastructure script, called by generator agent)

### Phase 3: Run on existing scribbles
- Run on v1 and v2 of `requirements_tasks/scribbles/therapist/data_transfer/`
- Verify consistency lint passes

### Phase 4: Wire into ui-scribble-generator
- After writing `metadata.yaml` (step in MUST-DO list), add:
  "Run `python3 scripts/scribbles/discover_scribble_requirements.py <metadata_path>` and
   incorporate the updated `contributing_requirements` and `participating_flows` into the
   written metadata.yaml."

## Out of Scope
- D41 (presentation_layer field) — stays dropped
- D42 (serves_requirements field) — stays dropped
- Any changes to scribble HTML files
