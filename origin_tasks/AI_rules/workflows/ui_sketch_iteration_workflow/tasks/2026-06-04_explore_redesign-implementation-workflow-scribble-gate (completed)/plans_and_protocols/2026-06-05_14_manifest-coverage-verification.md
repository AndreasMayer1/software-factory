# Manifest coverage verification — does `13` capture everything?

Task: TASK-PROC-032-29. Date: 2026-06-05.
Answers the developer ask: *verify that that plan captures everything — compare it to all decisions and all
documents we have.* Method: enumerate every decision, every Round-1 §8 change-list row, every eval-substrate
proposal (PROP-1…14, PROP-R1/R2), the P-A…P-F problem set, the `11` resolutions, and the `12` contingency
hooks; map each to a manifest handle in `13`; mark **✅ covered / 🟡 partial / ❌ GAP**. Gaps found are then
**remediated** (patched into `13`) and re-marked.

**Verdict up front:** the manifest covered the structural spine completely, but the first pass **missed four
readability/UX proposals and two cross-cutting encodings**. All six are now remediated in `13` (see §6).
After remediation: **complete**, with two items correctly **excluded** (tracked elsewhere) and two left as
**explicit authoring decisions** (not gaps — choices for STEP A).

---

## 1. Confirmed decisions (Q1/Q2, D-0…D-6)

| Decision | Manifest coverage | Status |
|----------|-------------------|--------|
| Q1 fixture-first | Phase B before Phase D; T-CV gate before T-D1 | ✅ |
| Q2 web fixture | T-B1 (web toolchain), tech-agnostic handoff in T-A1/C3 | ✅ |
| D-0 routing bug | T-C0 (first) + T-C6 (registry contract, prevents recurrence) | ✅ |
| D-1 bisection hard | T-A1 (hard requirement) | ✅ |
| D-2 per-design-unit | T-A1 (gate scope) | ✅ |
| D-3 names | T-A1 (begin/derive-code/finalize rename) | ✅ |
| D-3 task-start wrapper | **Excluded — tracked as TASK-PROC-069-01** (see §5) | ✅ (intentional) |
| D-4 SCI reader table | T-A2 (readers) + T-C9 (verify hard-block) | ✅ |
| D-5 PROP-14 dependency | T-A5 (REQ-PROC-060 entry) + T-C18 | ✅ |
| D-6 S1→S4 staging | Phase A = A1(S1)/A2(S2)/A3(S3)/A5(S4) | ✅ |

## 2. `11` recommendations (B1–B8, C1–C6)

| Item | Handle | Status |
|------|--------|--------|
| B1 D-0 first | T-C0 | ✅ |
| B2 bisection hard | T-A1 | ✅ |
| B3 data-point home + code-first exception | T-A2 + T-C14 | ✅ |
| B4 trade-off record (fused-only) | T-A1 + T-C7 | ✅ |
| B5 verify hard-block + override | T-A2 + T-C9 | ✅ |
| B6 2-stage width breaker | T-A2 + T-C11 | ✅ |
| B7 vendored MD renderer | T-A5 + T-C18 | ✅ |
| B8 S1→S4 staging | Phase A | ✅ |
| C1 5-edge rot-graph | T-A2 | ✅ |
| C2 AC facet-tagging | T-A2 + T-C14 | ✅ |
| C3 handoff design-intent/target-binding split | T-A1 + T-C3 | ✅ |
| C4 data-bound detector | T-C14 | ✅ |
| C5 registry routing-contract | T-A1 + T-C6 | ✅ |
| C6 L3 chain-length alert | T-C13 (within coverage assertion) | ✅ |

## 3. Round-1 §8 change-list (the canonical 15) + P-A…P-F

| Change-list row | Handle | Status |
|-----------------|--------|--------|
| 1 bisect waves (`--scope`) | T-C1, T-C2 | ✅ |
| 2 `release-derive-code` | T-C3 | ✅ |
| 3 rename finalize | T-C4 | ✅ |
| 4 scribble-gate terminal | T-C5 | ✅ |
| 5 fix `ui-create-scribble` bug | T-C0 | ✅ |
| 6 SCI + audit | T-C8 + T-C4 | ✅ |
| 7 `stale_since` set + refresh task | T-C8 | ✅ |
| 8 loopback-as-task (L2) | T-C10 | ✅ |
| 9 lazy-wavefront cascade | T-C11 | ✅ |
| 10 entry-context spine (PROP-8) | T-C12 | ✅ |
| 11 coverage/ordering (PROP-9/11) | T-C13 | ✅ |
| 12 comment-leak + PROP-1 + overlay | T-A3 + T-C15 | ✅ |
| 13 design-unit map by-product | T-C17 | ✅ |
| 14 PROP-14 flow viewer | T-A5 + T-C18 | ✅ |
| 15 Round-2 §2 inputs (sequential reviewers, gate-on-convergence, container dim) | T-A4/T-C16 (reviewers, cadence); container dim in T-C12 | ✅ |
| **P-A** scribble layer before code | T-A1/T-C1-3 | ✅ |
| **P-B** split Begin-Impl | T-C2/3/4 | ✅ |
| **P-C** loopback | T-C10 | ✅ |
| **P-D** token/session cut map | **see GAP-5** | 🟡→✅ |
| **P-E** discrepancy window | T-C8 | ✅ |
| **P-F** cross-req cascade | T-C11 | ✅ |

## 4. Eval-substrate proposals PROP-1…14 / PROP-R1-R2 (the completeness stress-test)

| PROP | What | Handle | Status |
|------|------|--------|--------|
| PROP-1 | audience-separated review layer | T-A3/T-C15 | ✅ |
| PROP-2 | orientation-first + entry-context reviewable | T-C12 | ✅ |
| **PROP-3** | reviewer-guide reusable component | **first pass: none** | ❌→✅ **GAP-1** |
| PROP-4 | persist per-reviewer findings | T-C15 | ✅ |
| **PROP-5** | script-generated state variants (small-multiples) | **first pass: none** | ❌→✅ **GAP-2** |
| **PROP-6** | trim `question.md`, route by audience | **first pass: none** | ❌→✅ **GAP-3** |
| PROP-7 | selective reviewers | T-C16 | ✅ |
| PROP-8 | entry/exit info-model completeness | T-C12 | ✅ |
| PROP-9 | scribble coverage first-class | T-C13 | ✅ |
| PROP-10 | entry-reference integrity check + bounded recovery | T-C11/C12 (partial — integrity check not named) | 🟡→✅ **GAP-4** |
| PROP-11 | coverage & ordering mechanism (R1–R4/G1–G4) | T-C13 | ✅ |
| PROP-12 | staleness & regen trigger | T-C8 | ✅ |
| PROP-13 | decoupled iteration + overlay | T-A4/T-C15/T-C16 | ✅ |
| PROP-14 | flow viewer | T-A5/T-C18 | ✅ |
| PROP-R1 | `claude-route` unconditional bookkeeping | **excluded → TASK-PROC-069-01** | ✅ (intentional, §5) |
| PROP-R2 | `task-start` wrapper | **excluded → TASK-PROC-069-01** | ✅ (intentional, §5) |

## 5. Correctly-excluded items (verify the exclusion is deliberate, not an omission)

- **PROP-R1/R2 + D-3 task-start wrapper** → the developer said (feedback `03`) "task-start wrapper over
  claude-route: i already created a separate task — consider it done." Confirmed: the git log shows
  **`TASK-PROC-069-01` — create explore task for task-start wrapper over claude-route** (commit 6d9b26c8). So
  these are **out of this redesign's scope by decision**, tracked elsewhere. Correct exclusion. ✅
- **Factory extraction (T-E1 / TASK-PROC-066-01)** — deferred by Q1; exists as its own task. Correct. ✅

## 6. GAPS FOUND → remediated in `13`

The first manifest pass over-indexed on the structural spine and dropped four readability/UX proposals and two
cross-cutting encodings. Remediation (now applied to `13`):

- **GAP-1 — PROP-3 reviewer-guide reusable component.** Added to **T-A3** (requirement) and **T-C15**
  (generator consumes the `_scribble_components/` review-guide component).
- **GAP-2 — PROP-5 script-generated state variants.** Added to **T-C15** (generator small-multiples helper).
- **GAP-3 — PROP-6 trim `question.md` by audience.** Added to **T-A4** (gate-content requirement) and
  **T-C16** (Phase-3 gate emitter).
- **GAP-4 — PROP-10 integrity check made explicit.** **T-C11** now names the *mode-independent
  entry-reference integrity check + bounded recovery* (not only the cascade), so the standing validate+recover
  isn't folded invisibly into the cascade detector.
- **GAP-5 — P-D session/token cut map as explicit ACs.** **T-A1** now must encode the session/token cut map
  (`10`§6: orchestrator-vs-agent-vs-new-task boundaries; handoff distillation) as requirement ACs, not leave
  it implicit in skill behaviour.
- **GAP-6 — fixture instrumentation probes** (the `12` six probes) were in T-B0 prose but not as emit-points
  in the skills that produce them. Added explicit emit ACs to **T-C8** (stall report), **T-C11** (cascade
  log), **T-C13/C14** (facet-tag audit, graph-stats), **T-C3** (salvage diff).

## 7. Two NON-gaps left as explicit STEP-A authoring decisions (choices, not omissions)

These are genuine open choices the requirements author must make — flagged so they aren't mistaken for gaps:

1. **Soft-SCI as a configurable mode?** `12` E1-B2 (the one near-one-way-door contingency) implies the
   *requirement* may want to permit a gated soft-SCI mode. Decision for **T-A2**: encode soft-SCI as an
   explicit configurable-but-sign-off-gated mode, or leave it as a documented pivot only. (Recommendation:
   encode it as a mode that defaults OFF — cheaper than retrofitting under pressure.)
2. **Contingency thresholds (`12`§0.6) — requirement or planning-only?** Decision for **T-A2/T-B0**: bake the
   pre-registered green/amber/red bands into the fixture's validation ACs, or keep them as a planning artifact
   the T-CV review consults. (Recommendation: bake into T-CV's acceptance so the gate is deterministic.)

## 8. Final verdict

After the GAP-1…6 remediations to `13`:
- **All 4 confirmed decisions, all 10 D-items, all 8 B-recommendations, all 6 C-resolutions, all 15
  change-list rows, all P-A…P-F, and all 14 PROPs + PROP-R1/R2 are accounted for** — either covered by a
  manifest handle or deliberately excluded with a named owner.
- **Coverage is complete.** The only remaining open items are the **two STEP-A authoring choices** (§7), which
  are decisions to make while authoring T-A2, not missing work.
- **Honest residual:** this verification checks *coverage* (every source item maps to a task), not
  *sufficiency* (whether each task, once executed, fully satisfies its source). Sufficiency is verified later
  by `task-derive-from-requ`'s coverage matrix + the per-requirement verification tasks — out of scope here.
