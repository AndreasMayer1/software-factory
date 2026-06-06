---
id: REQ-PROC-006
status: active
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-ENAB
effort: L
stakeholder: developer
created: 2025-10-04
updated: 2026-06-01
after: []
blocks: []
market_research_refs: [] # No relevant findings identified — internal process tool
trackable_items:
  # NOTE: This epic was elevated from a single feature requirement on 2026-06-01.
  # The acceptance criteria below are retained for reference-stability (existing
  # cross-refs and tasks point at REQ-PROC-006 AC-NN). Going forward, the seven
  # feature requirements (REQ-PROC-006-01 … -07) own the detailed, testable ACs;
  # each feature's exploration task fills its requirement. The sections that held
  # feature-level detail (Monitor Taxonomy, Two-Field Taxonomy, Web Research
  # Heuristics, Write-Surface Deny-List) moved into their owning features.
  acceptance_criteria:
    - id: AC-01
      text: "claude-optimize produces at most one improvement task per invocation; if no viable candidate exists, the run ends as a documented no-op"
    - id: AC-02
      text: "Candidate events are produced by two classes of producer: (1) monitor scripts that execute after every task-complete invocation and read only committed, project-local sources — no monitor reads session JSONL; (2) aggregator scripts invoked on demand that may read project-local session logs under .factory/session_logs/ to derive cross-session signals. Aggregators are not invoked in the post-task-complete critical path."
    - id: AC-03
      text: "All optimizer state resides under `.factory/optimize/` (committed to git); no optimizer state exists in per-account OS memory"
    - id: AC-04
      text: "Every task produced by claude-optimize has `awaiting: [\"user-unblock\"]` in its YAML frontmatter; no code path exists that produces an unblocked task (G-INV-1)"
    - id: AC-05
      text: "Monitor scripts execute as standalone Python processes invoked by a post-task-complete hook; they are not callable as tools by any agent during a session (G-INV-2)"
    - id: AC-06
      text: "The scoring and audit capability is implemented as a separate skill (claude-optimize-audit) from the task-producing skill (claude-optimize); the producer is never scored within its own run (G-INV-3)"
    - id: AC-07
      text: "When both bugfix and optimization candidates exist, the bugfix candidate is always selected; no fairness or rotation rule applies"
    - id: AC-08
      text: "Every produced task carries a verifiable acceptance criterion using ground-truth signals or a structural scoring rubric; single-LLM judgment is never the sole verification method"
    - id: AC-09
      text: "Every claude-optimize run (including no-ops) results in a git commit containing the updated runs.tsv and state.json"
    - id: AC-10
      text: "A write-surface deny-list prevents claude-optimize from producing tasks that target files on the evaluation surface; the deny-list is enforced programmatically at task-creation time"
    - id: AC-11
      text: "The claude-optimize-audit skill tracks two effectiveness metrics: user-unblock-rate (primary, fast-cadence) and revert-rate (secondary, slow-cadence)"
    - id: AC-12
      text: "The claude-optimize-audit skill computes a deterministic N-point health score per audit run, recorded with a trend delta in audit_history.tsv"
  sections:
    - id: SEC-01
      name: "Overview"
      heading: "## Overview"
    - id: SEC-02
      name: "Purpose"
      heading: "## Purpose"
    - id: SEC-03
      name: "Scope"
      heading: "## Scope"
    - id: SEC-04
      name: "Features"
      heading: "## Features"
    - id: SEC-05
      name: "Cross-Feature Invariants"
      heading: "## Cross-Feature Invariants"
    - id: SEC-06
      name: "Dependencies"
      heading: "## Dependencies"
---

# Epic: Workflow Improvement Automation

## Overview

claude-optimize is a self-improvement loop for the Software Factory: cheap structural monitors detect improvement opportunities, the loop emits at most one auto-blocked improvement task (or a documented no-op) per run, and a separate audit skill scores the loop's effectiveness against explicit targets. This epic spans detection, a target/metrics model, two evaluation modalities (statistical and simulation), the standing guardrails and budgets, orchestration/cadence, and a bounded self-optimization experiment.

## Purpose

The factory evolves continuously — skills are added and modified, ordering rules change, guidelines grow. Without systematic detection of regressions and improvement opportunities, quality degrades silently: the same question gets asked repeatedly, a skill edit introduces a subtle bug, or a guideline drifts from practice. The north-star is **app quality**; because that is too distal to measure directly, the loop ladders scope-local leading indicators up to it, under hard guardrails that prevent reward-hacking and protect product delivery. Originated as a 2025-10-04 user story; redesigned through a four-round exploration (TASK-PROC-006-02) and a holistic re-alignment (TASK-PROC-006-20, May–June 2026) that elevated it to this epic.

## Scope

**Included:** structural detection + event pipeline; the three-layer target model and the effectiveness audit; a slow real-signal statistical evaluation contract; a fast offline simulation harness; the standing guardrails and token/meta-work budgets; the subordinate autonomous trigger, weekly cadence, and ranked-batch consumption; and a staged, developer-witnessed self-optimization experiment.

**Excluded:** the optimizer never executes improvements itself (downstream executor skills do); it never modifies its own ruler (the audit rubric, quality gates, or the evaluation surface — see the deny-list in feat_guardrails_and_budgets); single-LLM "is this better?" judgment is never the sole verification.

## Features

- [`feat_detection_event_pipeline`](feat_detection_event_pipeline/requirements.md) — Monitors + aggregator, event schema/idempotency, consolidation combiner, queue ceiling, trajectory logging.
- [`feat_targets_metrics_audit`](feat_targets_metrics_audit/requirements.md) — Three-layer target model + the audit skill, effectiveness metrics, and deterministic rubric (absorbs TASK-PROC-006-16 DuckDB layer).
- [`feat_evaluation_statistical_contract`](feat_evaluation_statistical_contract/requirements.md) — Slow real-signal evaluation: events-not-tasks, anytime-valid stopping, drift detection, pending→verdict lifecycle, attribution + holdback.
- [`feat_evaluation_simulation_harness`](feat_evaluation_simulation_harness/requirements.md) — Fast offline verdict: paired old-vs-new, scenario sets, Git-branch test-data management, held-out split, synthetic-from-real, per-skill simulation budget.
- [`feat_guardrails_and_budgets`](feat_guardrails_and_budgets/requirements.md) — Session-byte budget start-gate (G-INV-4), meta-work subordination (G-INV-5), the deny-list, and the meta-recursion boundary; enforcement detail for G-INV-1/2/3.
- [`feat_orchestration_cadence_production`](feat_orchestration_cadence_production/requirements.md) — Subordinate autonomous trigger, activity-gated weekly cadence, the producer skill, ranked-batch consumption + proposal cap/digest.
- [`feat_self_optimization_experiment`](feat_self_optimization_experiment/requirements.md) — Two staged developer-witnessed runs, OEC + auto-abort guardrails, and the experiment kill-switch.

## Cross-Feature Invariants

These bind *all* features and may not be removed or weakened by any future evolution of the loop. They are hard constraints, not goals.

**G-INV-1 — Produced tasks are auto-blocked.** Every task claude-optimize creates has `awaiting: ["user-unblock"]`. The developer is always the gate between proposal and execution; the autorun orchestrator never picks up an optimize-produced task until consciously unblocked.

**G-INV-2 — Detection runs outside any agent's tool surface.** Monitor scripts are plain Python invoked by `task-complete`. They are not tools the optimizing agent can call, shape, or suppress; an agent cannot make a monitor fire (or not fire) to influence its own perceived productivity.

**G-INV-3 — Scoring is separated from production.** The `claude-optimize-audit` skill that computes the health score is a different skill from `claude-optimize` that produces tasks; the producing agent is never scored against a metric it can manipulate within the same run.

**G-INV-4 — Session-byte weekly budget, soft start-gate.** *(proposed — see feat_guardrails_and_budgets)* Meta-work draws on a weekly byte budget (shared-CCS-authoritative); when exhausted the optimizer's start is soft-gated so it cannot consume the calendar weeks of delivery the plan reserves for product work.

**G-INV-5 — Meta-work subordination.** *(proposed — see feat_guardrails_and_budgets)* The optimizer must never starve product delivery: bugfix and product tasks always precede optimization work, and optimizer-produced tasks enter the normal queue subordinate to product delivery.

## Dependencies

- **REQ-PROC-044** (Software Factory Quality Properties) — claude-optimize contributes to functional reliability through metrics-based improvement.
- **REQ-PROC-008** (Orchestrator Workflow) — the orchestrator invokes task-complete, which triggers monitors.
- **REQ-PROC-046** (Code Quality) — verify-quality is on the deny-list; claude-optimize must not target it.
- **REQ-PROC-059** (Cross-Factory LLM Work Principles) — principles (a)–(h) provide a detection lens for claude-optimize.

## References

- Holistic re-alignment + epic restructure: `tasks/2026-05-30_explore_holistic-optimizer-analysis-and-target-realignment/plans_and_protocols/` (syntheses `_02`/`_04`/`_06`, feedback `_03`/`_05`/`_06-01`, restructure plan `_07`).
- Original design exploration: `tasks/2026-05-01_explore_redesign-claude-optimize-skill (completed)/plans_and_protocols/` (rounds 1–4 + decisions log).
</content>
