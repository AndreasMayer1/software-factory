---
task: TASK-PROC-068-07 (T-harness-middle, terminal batch 1/3)
session: d792b971-10d2-48d2-8a00-fa27eb6cc8c7
date: 2026-06-30
model: Opus 4.8
mechanism: layer-derivation (REQ-PROC-071) — fixpoint_loop + coverage_delta + backfill_orchestration CLI
authority: ADVISORY (carried below — see §Caveats)
---

# Plan — 071-driven harness-middle generation

## Objective (from goal.md)
Apply the verified layer-derivation mechanism to **generate ≥1 middle artifact layer of the
Skill-Test Playground harness's product-definition stack** (`test_harness_app/` tree) from its
anchored endpoints — mechanically derived, not hand-authored — closing coverage against the
neighbour anchors and terminating in `COVERAGE_FIXPOINT`, minimal (no invented artifacts).

## Starting state (verified)
- `test_harness_app/` exists but holds **only the bottom endpoint**: the React/Vite app (`src/`).
- No `requirements_user_needs/` or `requirements_tasks/` in the harness tree — the product-definition
  stack `personas → scenarios → flows → requirements → tasks → code` is empty above `code`.
- Factory-tree feature specs (`feat_*/requirements.md`, REQ-PROC-068-01..05) are *instrument-feature
  specs* (coupling intent only); product detail must be authored in the harness tree (AC-06).

## Mechanism contract (read from source)
- `coverage_delta.py`: per-boundary delta = `required − satisfied` (set-difference on IDs). Anchor
  supplies required structural elements; draft supplies satisfied IDs. `is_closed` ⇔ no unsatisfied.
- `fixpoint_loop.py`: composes the loop; terminal `RunOutcome.COVERAGE_FIXPOINT` ⇔ zero open gaps.
  Default hinge seam = scenario↔flow (most disagreement-tolerant; flow is AC-06's default hinge).
  **Production driver is SESSION-DRIVEN** (dev decision #6a): the session authors the real artifacts
  to satisfy anchor demand and writes a coverage report; Python reads the open-gap set from it.
  `run_loop`/`apply_additive_repairs` are diagnostic/test-only and are used here only to emit the
  terminal-outcome verdict over the real authored ID set (exactly as the re-capstone driver did).
- Proven case (re-capstone TASK-PROC-071-07, PASS ADVISORY): **flow ← scenario + requirement**,
  draft started empty, reconstructed to the exact neighbour-demanded set, diff missing=∅ invented=∅,
  COVERAGE_FIXPOINT.

## Derivation chosen — the FLOW middle layer
Anchored endpoints (authored as the fixed neighbours of the derived layer, in `test_harness_app/`):
- **Top anchor — scenario layer** (grounded on minimal personas Archivist / Quick-Logger from the
  epic spec). Each scenario references the flow(s) it needs → this is the upper flow-demand.
- **Bottom anchor — requirement layer** (the harness product requirements for the now-slice
  features). Each requirement's `flow_coverage` references the flow(s) it implements → lower demand.
- **Derived middle — flow layer**: generated to satisfy the union of upper+lower flow demand,
  minimal (authored ⊆ demanded), terminating COVERAGE_FIXPOINT.

Flow demand (must match on both sides — the epic's three flows, all through the dashboard):
- FLOW-HARNESS-01 Add a rating · FLOW-HARNESS-02 Browse the library · FLOW-HARNESS-03 Review insights

## Execution steps
1. Author the harness product-definition anchors (minimal — "enough to fire the test case", not a
   believable product's worth, per epic Build/Derivation order):
   - `test_harness_app/requirements_user_needs/personas/` — 2 personas.
   - `test_harness_app/requirements_user_needs/personas/<p>/scenarios/` — scenarios referencing flows.
   - `test_harness_app/requirements_tasks/.../requirements.md` — 4 feature requirements w/ flow_coverage.
2. Mechanically derive the flow layer: author `test_harness_app/requirements_user_needs/user_flows/`
   flows satisfying the neighbour demand; write a coverage report `{covered_ids: [authored flow IDs]}`.
3. Run the real mechanism over the boundary (anchor = neighbour-demanded flow IDs, draft = coverage
   report) via `coverage_delta.py` (is_closed) + `fixpoint_loop.py` (COVERAGE_FIXPOINT), and the
   minimality check (authored ⊆ demanded → invented=∅). Capture the verdict in the protocol.
4. Write the results protocol carrying the FIVE mandatory advisory caveats.
5. `claude-log` → `doc-update-guidelines` → `task-complete` (commits).

## Scope guards
- All product content stays in `test_harness_app/` (two-tree split; AC-06). No harness product
  content authored in the factory tree.
- The mechanism itself is NOT modified or re-verified (REQ-PROC-071 done, ADVISORY).
- No Dart `lib/`/`test/` touched → `verify-quality` Dart gates not triggered; harness artifacts are
  process/product docs. Any Python *driver* run is throwaway (not committed under `scripts/`).

## Caveats (ADVISORY — carried verbatim into the results protocol; this task consumes oracle verdicts)
1. Corpus N=3 ≪ floor_n=100 — qualitative, not statistical.
2. Pairs above the termination point are not authoritative.
3. Demonstrated scope is the demonstrated set, not a generalized capability claim.
4. Calibration (REQ-PROC-044-05) not established — cannot displace human judgment.
5. Artifact-level oracle, not behavioural.
