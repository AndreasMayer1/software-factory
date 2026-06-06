---
skill: requ-explore
mode: automated
decision: ""
task_id: TASK-PROC-032-30
captured_at: 2026-06-05
---

# Question

---
task_id: TASK-PROC-032-30
session_id: dc27d645-874a-4cd6-b6ac-8852c1dabf72
account: gmail
status: awaiting_answer
asked_at: 2026-06-05T16:42:48Z
skill: requ-explore
---

# Pending Question

## What was done

I authored the **consistency & scribble-layer model** (redesign manifest task **T-A2**) into
REQ-PROC-032 (`requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md`).

- **14 new ACs (AC-42 … AC-55)** appended to the existing `trackable_items.acceptance_criteria` block.
- One new body section **SEC-18 "Consistency and Scribble-Layer Model"** (added to `sections` + body, line 803).
- Existing AC-01…AC-41 / SEC-01…SEC-17 untouched. `status` left `active`. No `target_package` on the new ACs
  (matches every existing AC in this internal-tooling requirement).
- Protocol: `…/tasks/2026-06-05_explore_author-scribble-consistency-model/plans_and_protocols/2026-06-05_01_protocol_author-consistency-spine.md`

### New ACs (one line each)
- **AC-42** — Scribble-Currency Invariant (SCI) holds continuously (one rule covers t=start gate and t=mid-release governance).
- **AC-43** — Standing script-driven SCI audit; blocking at finalization; additive to the parity check.
- **AC-44** — Five-edge staleness rot-graph, each edge with its named detector.
- **AC-45** — Loopback-as-task L1–L6 (normative-upstream edit ⇒ new task; un-approved scribble ⇒ same task, new version).
- **AC-46** — Lazy-wavefront depth-1 cross-requirement cascade; live `flow_positions`; visited-set termination.
- **AC-47** — Two-stage width breaker, configurable, soft=3 / hard=7 measured-on-fixture defaults.
- **AC-48** — L3 coverage assertion + source-gap chain-length alert.
- **AC-49** — Entry-context spine (PROP-8): emit + reviewer check + bounded reconciliation + container dimension.
- **AC-50** — Coverage/ordering (PROP-9/11): coverage report, auto scribble task, primary-path depth-1 ordering, basis resolution.
- **AC-51** — App-shell/launch-map requirement + two-tier seam detection (authored as constraint; skill change lands in T-C17).
- **AC-52** — Domain→design conditional edge + data-bound detector.
- **AC-53** — AC facet-tagging {presentation|behaviour|both}: auto + human-confirm, fail-safe to presentation.
- **AC-54** — Generative readers block / referential readers flag; verify hard-block + advisory override.
- **AC-55** — Soft-SCI as configurable, sign-off-gated mode, default OFF.

### The consistency model (synthesis)
The scribble is the locked-in design contract a coding task consumes. One invariant — **SCI** — keeps it
trustworthy: no coding task is runnable while a covered scribble is missing / unapproved / stale, and that
*same* rule is the hard gate at release start and the discrepancy-window governance mid-release. Staleness
propagates along exactly **five edges**, each with a detector; stale-scribble readers that *generate*
downstream artifacts **block**, while *referential* readers merely **flag**. Loopbacks resolve mechanically
(upstream edit ⇒ new task; un-approved scribble ⇒ same task, new version). Cross-feature cascade is resolved
**lazily**, one depth-1 hop at a time (no rotting global graph), bounded by a **two-stage width breaker**.
**Facet tags** split each AC into presentation / behaviour waves, failing safe to `presentation` on ambiguity.

## Decisions needing your sign-off

**Decision 1 — Soft-SCI mode.**
Authored with the recommended default: soft-SCI is an explicit **configurable, sign-off-gated mode, default OFF**
(AC-55). SCI stays a hard invariant; the relaxation merely *exists* but is gated behind explicit sign-off.
- **Confirm** → keep AC-55 as authored.
- **Override** → "documented pivot only" (no configurable mode). This removes the liveness escape hatch the
  contingency plan keeps for densely-coupled releases.

**Decision 2 — Width-breaker thresholds.**
Authored with the recommended default: the breaker is **configurable with measured-on-fixture defaults**
(soft=3 / hard=7), to be **accepted/tuned in the validation task T-CV's acceptance** (AC-47).
- **Confirm** → keep AC-47 as authored.
- **Override** → hard-code the numbers now, freezing 3/7 before any fixture measurement (contradicts the
  pre-registration discipline).

## What remains genuinely uncertain
Facet-tag mis-tag rate (empirical, fixture-measured); cascade width / breaker N (3/7 are guesses — the
dashboard hub is the likely red zone); liveness under hard SCI (correctness guaranteed, throughput not
modeled); `both`-facet frequency; how often the code-first exception (rot-graph edge 3) is actually invoked.

## What I need from you (to close this task — goal ACs 5 & 6)

1. **Approve the final synthesis** (or request changes), and
2. **Confirm or override each of the two decisions** above, and
3. **State the next step.** My proposed next step:
   > Run **`task-derive-from-requ`** on REQ-PROC-032 to generate the consistency-layer impl tasks
   > (manifest **T-C8…C14, C17**) from AC-42…AC-55, and **append every derived task to
   > `.claude/task_ordering_priority_override.txt`** (per your 2026-06-05 directive in goal.md — these tasks
   > carry no `target_package` and would not otherwise surface in `next_tasks.py`).

   Confirm this next step, or specify a different one.

# Developer Answer

Approved

# Rationale Captured

(Automated archival — no rationale extracted.)
