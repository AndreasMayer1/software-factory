# Manifest coverage verification — round 2 (deeper pass)

Task: TASK-PROC-032-29. Date: 2026-06-05.
Developer ask: *run another verification round once that one is done.* Round 1 (`14`) checked the manifest
against decisions, the §8 change-list, and PROP-1…14. Round 2 deliberately uses **different lenses** that
round 1 could not see through:
1. raw eval **F-findings F1–F16** (round 1 only checked the PROPs they fed);
2. **existence checks** — do the referenced requirements actually exist?;
3. **manifest-internal integrity** — is the dependency graph valid, are derived/source edges coherent?;
4. **assumed-but-unlisted prerequisites** — things the manifest relies on but never names as work.

**Verdict:** round 2 confirmed round 1's remediations all landed, and found **3 new gaps** (one actionable on
an already-created task) + **2 minor notes**. All 3 gaps are now **remediated**. After round 2 the plan is
coverage-complete with the two STEP-A authoring choices (`14`§7) still the only open decisions.

---

## 1. Confirmations (round-1 remediations actually landed)

Grep-verified in `13`: GAP-1 (PROP-3, T-A3/C15), GAP-2 (PROP-5, T-C15), GAP-3 (PROP-6, T-A4/C16), GAP-4
(PROP-10 integrity check, T-C11), GAP-5 (session/token cut map, T-A1), GAP-6 (six emit-probes across
T-C3/C8/C11/C13/C14). ✅ all present.

Existence-verified: **REQ-PROC-032** (`ui_sketch_iteration_workflow/requirements.md`), **REQ-PROC-035**
(`release_preparation/requirements.md`), **REQ-PROC-058** (`implementation_task_planning/requirements.md`) all
exist — the Phase-A requ-explore targets are real, not phantom. ✅

## 2. F-findings F1–F16 cross-check (round 1 didn't check these directly)

| Finding | Covered by | Status |
|---------|-----------|--------|
| F1 reviewer detail in comments → (R2§1) nesting leak | T-A3/T-C15 | ✅ |
| F2 per-reviewer findings not persisted | T-C15 (PROP-4) | ✅ |
| F3 entry context absent (+ dimension) | T-C12 | ✅ |
| F4 state variants detached | T-C15 (PROP-5, GAP-2) | ✅ |
| F5 question.md duplicates | T-C16 (PROP-6, GAP-3) | ✅ |
| F6 flow-step mapping exists (substrate) | T-A3/T-C18 | ✅ |
| F7 claude-route skipped | TASK-PROC-069-01 (excluded) | ✅ |
| F8 entry context known, dropped, unreviewed | T-C12 | ✅ |
| F9 reads no router/app-shell | T-C12 (bounded reconciliation) | ✅ |
| F10 brownfield + no coverage model | T-C13/T-C11 | ✅ |
| F11 basics not covered | T-C13 | ✅ |
| **F12 launch seam unowned** | **was thin** | ❌→✅ **R2-GAP-1** |
| **F13 requ-derive-from-flow is the early detection point** | **was thin** | ❌→✅ **R2-GAP-1** |
| **F14 two-tier (Tier A/B) seam detection** | **was thin** | ❌→✅ **R2-GAP-1** |
| F15 requirement edit → stale scribble | T-C8 (PROP-12) | ✅ |
| F16 rigid gate cadence | T-C16 (PROP-13) | ✅ |

## 3. New gaps found in round 2 → remediated

- **R2-GAP-1 — PROP-11 R4 / F12–F14 two-tier entry-seam detection + the app-shell/launch-map requirement.**
  Round 1 mapped PROP-11 to T-C13 but T-C13 only carried R1–R3 (coverage/ordering); **R4** (detect the
  unowned outer launch seam early, two-tier — Tier A in `requ-derive-from-flow`, Tier B in
  `requ-verify-flow-coverage --all` — and *create* the app-shell/feature-launch-map requirement) had no task.
  T-C17 carried only the design-unit map. → **Remediated:** T-C17 now also owns the two-tier `foundation_gap`
  entry-seam detection and the app-shell/launch-map requirement creation. This is load-bearing — it is the
  canonical PROP-8 Tier-1 target every feature scribble resolves entry context against; without it the
  entry-context spine has nothing to point at.
- **R2-GAP-2 — TASK-PROC-066-03 goal.md lacked the instrumentation ACs.** The fixture task was created
  *before* `12` existed, so the six measurement probes the manifest (T-B0) assumes were not in the actual
  task's `goal.md`. → **Remediated:** added an Output bullet to TASK-PROC-066-03 requiring the now-slice
  requirements to specify the six probes ("the fixture is an *instrumented* app"), with a pointer to `12`§0.6.
  Without this fix, the empirical-validation plan (`12`) would have had no data source.
- **R2-GAP-3 — T-B1 web toolchain didn't note dependency-admission.** Standing up React/Angular is a large
  dependency addition; REQ-PROC-060 requires developer authorization. → **Remediated:** T-B1 now states it
  routes through REQ-PROC-060 dependency-admission.

## 4. Manifest-internal integrity (round 2 only)

- **DAG validity:** no cycles. Seeds with no predecessor: T-C0, T-A1, T-B0(done). Every other task's `after`
  resolves to an earlier handle. ✅
- **Derived/source coherence:** every `[DERIVED]` C-task lists its **source A-task** (the requirement it is
  derived from) in the "Source AC" column AND an execution `after`. Reading rule confirmed: a derived task
  cannot exist before its source A-task lands (that is what makes it *derived*), so the source A-task is an
  implicit hard predecessor on top of the explicit `after`. The critical-path diagram honours this
  (T-A1→T-C1, T-A2→T-C8…). ✅ (Minor: the table could state "after = source A-task + listed exec dep" to make
  the implicit edge explicit — noted, not blocking.)
- **No orphan handles:** every handle referenced in the critical-path diagram and the counts exists as a row. ✅

## 5. Two minor notes (not gaps — already covered, flagged for clarity)

- **Playground user-needs (personas/scenarios/flows).** T-B2 (build now-slice features) is `[DERIVED]` from
  approved flows, which implies the playground needs a minimal persona/scenario/flow set first. This **is**
  covered — TASK-PROC-066-03's goal.md Execution Model already says "expect to define a small set of
  personas/scenarios/flows for the playground product" (via the `ux-*` chain). Covered by T-B0; the manifest
  row just doesn't restate it. No action.
- **Cross-file rename blast radius (T-C4).** Renaming `release-begin-impl-finalize`→`release-finalize-impl`
  touches CLAUDE.md, `factory_flows.md`, INDEX.md, sibling skills, hooks (per R1§8). `claude-modify-skill`
  owns that sweep; flagged so the executor scopes it as a multi-file rename, not a one-file edit.

## 6. Final round-2 verdict

- Round-1 remediations: **all present.**
- New deeper findings: **3 gaps, all remediated** (R2-GAP-1 in `13` T-C17; R2-GAP-2 in the fixture task's
  `goal.md`; R2-GAP-3 in `13` T-B1).
- F1–F16: **fully accounted for.** Referenced requirements: **all exist.** Manifest DAG: **valid.**
- **Coverage is complete across two independent verification lenses.** Remaining open items are unchanged:
  the two STEP-A authoring *choices* (`14`§7 — soft-SCI mode; thresholds-as-ACs), which are decisions, not
  missing work.
- **Honest residual (unchanged):** this is *coverage* verification (every source item → a task), not
  *sufficiency* (does each task, executed, fully satisfy its source). Sufficiency is established downstream by
  `task-derive-from-requ`'s coverage matrix and the per-requirement verification tasks. Two verification
  rounds cannot substitute for that — they ensure nothing is *missing*, not that everything listed is
  *enough*.

## 7. Diminishing returns note
Round 1 found 6 gaps; round 2 found 3 (all from lenses round 1 lacked) + 2 non-gaps. A round 3 along the same
lenses would likely find ≤1 and of decreasing materiality — the high-value lenses (decisions, change-list,
PROPs, F-findings, existence, DAG) are now exhausted. The next *material* verification is no longer
documentary: it is **executing T-A1/T-A2 and letting `task-derive-from-requ`'s own coverage matrix check
sufficiency** — a different kind of check than re-reading the manifest.
