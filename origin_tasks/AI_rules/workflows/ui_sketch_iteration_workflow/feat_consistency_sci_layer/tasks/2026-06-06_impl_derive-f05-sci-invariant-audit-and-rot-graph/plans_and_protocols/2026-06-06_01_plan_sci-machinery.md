# Plan: SCI Invariant Machinery, Rot-Graph Detectors, Standing Audit (T-C8)

Task: TASK-PROC-032-05-01 · Requirement: REQ-PROC-032-05 (AC-01, AC-02, AC-03, AC-14)
Session: 36c6db87 · Date: 2026-06-06

## Synthesis — the model held in one place

The **Scribble-Currency Invariant (SCI)**: no coding task is runnable while the scribble of
any requirement it covers is missing, unapproved, or stale relative to that requirement's
current committed version. One invariant, observed at t=start (hard scribble gate) and
t=mid-release (discrepancy-window governance) by the same mechanism.

**Resolution chain** (coding task → scribble):
`coding task goal.md` → `parent_requirement` → that requirement's `feature_path`
→ `requirements_tasks/scribbles/<feature_path>/` → highest `v{N}` with `status: approved`
→ its `metadata.yaml`.

A "coding task" for SCI purposes = a task with `type: impl` whose `parent_requirement`
resolves to a requirement that carries a non-empty `feature_path` (i.e. a Presentation
requirement that owns renderable screens and therefore a scribble). Tasks whose requirement
has no `feature_path` (pure rule/token/process) are out of SCI scope.

## Deliverables

### D1 — New script `scripts/quality/check_scribble_currency.py` (+ tests) [AC-01, AC-02, AC-03, E1]
Standing, script-driven SCI audit. For every coding task, resolve the covered scribble and
assert it is approved and current. Reports SCI violations; exits non-zero on hard violation.

**Resolution & violation rules** (edge 2 — the audit core):
- no scribble dir for the feature_path → VIOLATION (missing)
- no version with `status: approved` → VIOLATION (unapproved)
- approved version has `stale_since` set → VIOLATION (stale; this is how edge 1 surfaces)
- approved version metadata carries optional `requirements_commit`, AND the requirement's
  `requirements.md` has a newer committed version (git) than that commit → VIOLATION (behind).
  If `requirements_commit` absent → emit an advisory note (cannot verify commit currency),
  NOT a hard violation (graceful degradation).

**Five named detectors** (AC-03 — each edge has a named detector function):
1. `detect_requirement_to_scribble_staleness(scribble_meta)` — edge 1; triggered by a
   LOCKED-IN requirement edit; detected by the `stale_since` marker on the scribble.
2. `detect_scribble_to_coding_task_staleness(task, scribble_meta, root)` — edge 2; the audit
   core above (missing / unapproved / stale / behind).
3. `detect_domain_to_databound_scribble_staleness(scribble_meta, root)` — edge 3; active only
   for code-first data-bound scribbles (`data_bound: true` + `domain_commit` on metadata);
   compares the domain value-object's commit. Absent metadata → no-op (documented hook; full
   facet/design-unit wiring is AC-11/AC-12 territory, not this task).
4. `detect_scribble_to_dependent_scribble_staleness(scribble_meta)` — edge 4; lazy-wavefront
   cascade. Named detector present and callable; surfaces `stale_since` on a dependent. Full
   cascade engine is T-C11 (out of scope) — this is the documented edge-4 hook.
5. `detect_scribble_to_verification_staleness(scribble_meta)` — edge 5; verification reader's
   currency check (stale-at-verification). Named detector present; full verify-flutter
   block/override is T-C9 (out of scope) — documented edge-5 hook.

**E1 stall report**: `--stall-report` prints the list of coding tasks blocked by a stale
scribble, each with task_id, requirement, feature_path, and reason.

**Soft-SCI** (AC-14): read `.factory/config/sci.yaml`:
```yaml
soft_sci:
  enabled: false      # default OFF → hard blocking invariant
  signoff: ""         # developer sign-off text; REQUIRED non-empty when enabled
  signed_off_at: ""
```
- default / file absent → enabled=false → violations are HARD (exit 1).
- enabled=true AND signoff non-empty → violations downgraded to warnings, output labeled
  `PROVISIONAL`, exit 0.
- enabled=true AND signoff empty → ERROR "soft-SCI requires recorded sign-off" (exit 1):
  the mode cannot silently relax the guarantee.

**CLI**: `--root`, `--stall-report`, `--release` (label: blocking gate context), `--json`
(optional). Exit 0 = OK / provisional; exit 1 = hard SCI violation(s).
Tier header `# tier: B`. Must pass Python gates G1–G5. Reuses `util.yaml_frontmatter`
and the ruamel/plain-yaml read pattern from `update_scribble_requirements.py`.

### D2 — Release-finalization gate wiring [AC-02]
Add a new check to `scripts/release/check_release_preconditions.py` that invokes
`check_scribble_currency.py` and blocks the release on hard SCI violations (additive to the
existing storage-mirror parity check; they are distinct — parity = orphaned paths, currency =
staleness). Non-breaking: must not crash; must surface the script output verbatim on failure.
Verify no existing test of check_release_preconditions.py breaks.

### D3 — requ-explore skill edit (via claude-modify-skill) [AC-03 edge 1, refresh task]
Add an "SCI: stale-on-edit protocol" step: when a LOCKED-IN requirement edit lands (an edit
to a presentation- or both-facet AC that an approved scribble locked), the skill MUST:
1. Set `stale_since: <today>` on every approved scribble whose `contributing_requirements`
   includes the edited requirement (edge 1 marker).
2. Auto-create a **blocking scribble-refresh task** (via `task-create`) that blocks dependent
   coding tasks until a refreshed approved scribble exists.
Also document soft-SCI: while OFF (default) SCI is a hard block; the refresh task is mandatory.

### D4 — task-derive-from-requ skill edit (via claude-modify-skill) [AC-01, AC-14]
Document that derived coding tasks are governed by SCI: a coding task is non-runnable while its
covered scribble is missing/unapproved/stale; the standing audit
(`scripts/quality/check_scribble_currency.py`) enforces this. Document soft-SCI as the only
sign-off-gated escape hatch (default OFF) under which a coding task may proceed against a stale
scribble with `provisional` output and mandatory re-verification on refresh.

### D5 — Schema + docs (small, direct edits)
- `.claude/schemas/scribble_metadata.yaml`: add optional `requirements_commit` (string; the
  requirement `requirements.md` commit this scribble was generated against — enables the
  AC-02 commit-currency comparison) and optional `data_bound` (bool) + `domain_commit` (string)
  for edge 3; broaden `stale_since` description to include LOCKED-IN requirement edits (edge 1),
  not only T1/T2 rule changes.
- `requirements_tasks/SKETCHES_README.md`: extend "Stale Scribble Lifecycle" prose to note the
  requirement-edit trigger and the SCI audit / refresh-task mechanism (pointer only; schema is
  canonical for field shape).

## Execution (delegation)
- **Agent A (background)**: D1 + D2 — script + tests + release wiring, all via claude-write-script;
  runs Python gates; returns summary. Write-set: `scripts/`.
- **Agent B (background, parallel)**: D3 + D4 — both skill edits via claude-modify-skill,
  SEQUENTIAL within the agent (shared INDEX.md/factory_flows.md write target). Write-set:
  `.claude/skills/`, `.claude/skills/INDEX.md`, `.claude/factory_flows.md`.
- **Main session (inline, before spawning)**: D5 schema + README (informs both agents).
A and B have disjoint write-sets → run in parallel. Heartbeat while they run.

## Acceptance check (maps to goal.md checklist)
- stale_since on requirement edit → D3
- blocking refresh task auto-created → D3
- five named detectors → D1
- check_scribble_currency.py resolves task→scribble→currency, reports violations → D1
- standalone + release gate → D1 + D2
- soft-SCI default OFF, sign-off-gated → D1 (enforcement) + D3/D4 (protocol)
- E1 stall report → D1
- skill edits reflect machinery → D3, D4
- no tests broken; Python gates G1–G5 pass → Agent A
