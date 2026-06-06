---
requirement: REQ-PROC-006
requirements_version: eabdeaf0
created: 2026-05-28
mode: full
session_id: 0cdeaf76-f2e7-4a65-b0e6-98a692968152
account: web
verification_task_present: TASK-PROC-006-06
---

# Task Creation Plan — REQ-PROC-006 (claude-optimize)

Derived from REQ-PROC-006 ACs/sections (commit eabdeaf0) and the round-4 §6 impl
backlog. IMPL-A is already done (TASK-PROC-006-03 wrote the requirement). IMPL-K
(cross-factory principles) and IMPL-L (factory-only file move) are out of scope
for this requirement — IMPL-K is being derived under TASK-PROC-006-05 via the
parallel REQ-PROC-059 path; IMPL-L is "independent — can run anytime" and is not
needed to satisfy REQ-PROC-006 ACs.

The reviewer task TASK-PROC-006-06 (`type: review`) is the verification task per
task-derive-from-requ §3 (≥3 impl tasks → separate verification task). Its
`after:` list will be extended in the post-creation step.

## Tasks

- task_name: "factory-optimize-scaffolding"
  backlog_id: IMPL-B
  req_path: "requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/requirements.md"
  requirements_version: "eabdeaf0"
  covers_acs: [AC-03]
  covers_sections: []
  effort: S
  layer: process
  after: []
  task_type: impl
  opus_recommended: false
  target_package: "claude-optimize"
  scope_description: "Create .factory/optimize/ scaffolding: state.json (schema + initial values), events/ directory, history/runs.tsv header, history/audit_history.tsv header, history/web_searches.tsv header, reports/ directory, README.md describing the layout and lifecycle rules."
  release_description: ""
  implementation_notes: |
    Read the requirement §"Project-Local State" table for the canonical file
    list and the lifecycle rules ("overwritten each run" / "append-only" /
    "consume-then-delete"). State.json schema must cover counters, last-run
    timestamp, no-op streak, periodic counter (default N=10). All files must be
    git-committable (no per-account state). The README documents the
    consume-then-delete rule for events/ and the 30-day pruning rule for stale
    events.

- task_name: "monitor-scripts-and-runner"
  backlog_id: IMPL-C
  req_path: "requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/requirements.md"
  requirements_version: "eabdeaf0"
  covers_acs: [AC-02, AC-05]
  covers_sections: [SEC-01]
  effort: M
  layer: process
  after: ["IMPL-B"]
  task_type: impl
  opus_recommended: true   # reason: multi-script standalone-exec contract + G-INV-2 invariant
  target_package: "claude-optimize"
  scope_description: "Implement scripts/optimize/monitor_repeated_question.py, monitor_skill_change_reverted.py, monitor_skill_change_first_use.py (Stage 1 only initially), monitor_periodic_counter.py, and scripts/optimize/run_monitors.py. All monitors are pure-Python standalone processes, idempotent per cooldown window, emit JSON event files to .factory/optimize/events/. Total runtime target <2s."
  release_description: ""
  implementation_notes: |
    Read SEC-01 "Monitor Taxonomy" for trigger conditions, confidence levels,
    event types, and cooldown windows (14 days for repeated-question). Each
    monitor must consume committed project-local sources only (runs.tsv, git
    history, protocol files, question fingerprints) — never session JSONL in
    routine operation. Monitors are NOT exposed as tools to any agent (G-INV-2).
    Stage 2 of monitor_skill_change_first_use depends on IMPL-H (protocol
    skills_used: field); ship Stage 1 here, Stage 2 enabled after IMPL-H lands.

- task_name: "create-optimize-task-script"
  backlog_id: IMPL-D
  req_path: "requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/requirements.md"
  requirements_version: "eabdeaf0"
  covers_acs: [AC-04, AC-10]
  covers_sections: [SEC-04]
  effort: M
  layer: process
  after: ["IMPL-B"]
  task_type: impl
  opus_recommended: true   # reason: programmatic safety invariants (G-INV-1, deny-list)
  target_package: "claude-optimize"
  scope_description: "Implement scripts/optimize/create_optimize_task.py that emits the produced improvement task with awaiting:[\"user-unblock\"] (G-INV-1, non-configurable default; no code path may produce an unblocked task) and enforces the write-surface deny-list at task-creation time. Reject any produced task whose target path matches the deny-list entries listed in SEC-04."
  release_description: ""
  implementation_notes: |
    The auto-block default is a hard constraint (G-INV-1). There must be no
    flag, env var, or branch that produces a task without awaiting:["user-unblock"].
    Add a unit test asserting this invariant. Deny-list lives in the script as
    a constant initialised from SEC-04's minimum list; the script rejects
    matches by glob (so scripts/quality/** entries work). Consider a pre-commit
    hook variant only if cheap; otherwise the script-level reject is enough
    given G-INV-1 is the primary control (per requirement §"Write-Surface
    Deny-List").

- task_name: "claude-optimize-skill-rewrite"
  backlog_id: IMPL-E
  req_path: "requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/requirements.md"
  requirements_version: "eabdeaf0"
  covers_acs: [AC-01, AC-07, AC-08, AC-09]
  covers_sections: [SEC-02, SEC-03]
  effort: M
  layer: process
  after: ["IMPL-C", "IMPL-D"]
  task_type: impl
  opus_recommended: true   # reason: cross-cutting skill body redesign spanning 4 ACs + 2 sections
  target_package: "claude-optimize"
  scope_description: "Rewrite .claude/skills/claude-optimize/SKILL.md as a thin event-consumer: read .factory/optimize/events/, pick highest-priority candidate (bugfix > optimization), emit one improvement task (via IMPL-D's create_optimize_task.py) with the two-field taxonomy (optimization_target/optimization_dimension) and the optimization_approach web-research block per SEC-03 heuristics, OR exit as documented no-op. Every run commits runs.tsv and state.json (no-ops included)."
  release_description: ""
  implementation_notes: |
    Body must be token-efficient (LLM step deliberately minimal per requirement
    §"Developer Guidelines"). Verification of produced tasks MUST prefer
    ground-truth signals (test pass/fail, static analysis clean, script exit
    codes); single-LLM "is this better?" judgment as the sole verification
    method is disallowed (AC-08). Bugfix priority is strict — no fairness rule
    (AC-07). One produced task per invocation, never more (AC-01). Commit
    message format: chore(optimize): run <id> [created|no-op] [<dimension>].
    Web-research heuristics table (SEC-03) lives in the skill body — one place
    to change, no config drift.

- task_name: "wire-monitors-into-task-complete"
  backlog_id: IMPL-F
  req_path: "requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/requirements.md"
  requirements_version: "eabdeaf0"
  covers_acs: [AC-02]
  covers_sections: []
  effort: S
  layer: process
  after: ["IMPL-C"]
  task_type: impl
  opus_recommended: false
  target_package: "claude-optimize"
  scope_description: "Append run_monitors.py invocation to the tail of the task-complete skill / completion path so monitors execute after every successful task completion. Must not block task-complete on monitor failure (log + continue). Must not run during dry-runs or back-out paths."
  release_description: ""
  implementation_notes: |
    The wiring is the trigger for AC-02 (monitors execute after every
    task-complete). Make it best-effort (capture exit code, log, do not abort
    task-complete on monitor crash) since a monitor bug must not break the
    primary close-out workflow. Monitors are idempotent within their cooldown
    windows so re-runs are safe.

- task_name: "claude-optimize-audit-skill"
  backlog_id: IMPL-G
  req_path: "requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/requirements.md"
  requirements_version: "eabdeaf0"
  covers_acs: [AC-06, AC-11, AC-12]
  covers_sections: []
  effort: L
  layer: process
  after: ["IMPL-E"]
  task_type: impl
  opus_recommended: true   # reason: new skill design with deterministic rubric + two metrics + sub-audits
  target_package: "claude-optimize"
  scope_description: "Build .claude/skills/claude-optimize-audit/ as a separate skill from claude-optimize (G-INV-3). Computes user-unblock-rate (primary, fast-cadence) and revert-rate (secondary, slow-cadence) from runs.tsv + goal.md awaiting: history + git log. Computes a deterministic N-point health score with trend delta, written to audit_history.tsv. Supports --monitor=<name> sub-audits."
  release_description: ""
  implementation_notes: |
    Read the requirement §"Effectiveness Metrics and Audit" for metric
    definitions and target bands (user-unblock-rate 50–80%). The N-point score
    is computed from runs.tsv and git history ONLY — never from LLM judgment
    (AC-12). Starting rubric: 10 criteria, refinable from real data per round-4
    §9 (the rubric criteria are a guess; mechanism is sound; refine after
    real-data). audit_history.tsv format: append-only, one row per audit run,
    including the score and delta-vs-previous. Audit skill is invoked on user
    demand (not on a trigger).

- task_name: "skills-used-protocol-instrumentation"
  backlog_id: IMPL-H
  req_path: "requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/requirements.md"
  requirements_version: "eabdeaf0"
  covers_acs: [AC-02]
  covers_sections: []
  effort: S
  layer: process
  after: ["IMPL-C"]
  task_type: impl
  opus_recommended: false
  target_package: "claude-optimize"
  scope_description: "Instrument protocol.md logging (via claude-log or task-complete) to record a skills_used: list per session. This enables Stage 2 of monitor_skill_change_first_use (fires only after evidence that an edited skill was actually exercised)."
  release_description: ""
  implementation_notes: |
    The list goes into the protocol frontmatter or a dedicated field — pick the
    location consistent with existing claude-log emission. Once landed, the
    IMPL-C monitor's Stage 2 logic can be enabled (the monitor file may need a
    follow-up edit to consume the new field; treat that as part of the IMPL-C
    task's verification step or open a small follow-up).

- task_name: "consume-task-proc-044-observability"
  backlog_id: IMPL-I
  req_path: "requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/requirements.md"
  requirements_version: "eabdeaf0"
  covers_acs: [AC-02]
  covers_sections: []
  effort: M
  layer: process
  after: []
  awaiting: ["TASK-PROC-044-observability-landing"]
  awaiting_note: "Blocked until REQ-PROC-044 ships an observability data source the monitors can consume; see round-4 §6 IMPL-I."
  task_type: impl
  opus_recommended: false
  target_package: "claude-optimize"
  scope_description: "Extend the monitor set (or add a tier-0 source) to consume TASK-PROC-044 observability data once it lands. Specific monitor(s) and signals are TBD pending the observability schema produced by REQ-PROC-044."
  release_description: ""
  implementation_notes: |
    Hard-blocked on external work. Keep the goal.md alive in the backlog so the
    dependency surfaces in next_tasks.py; it remains awaiting:[external] until
    the source is available. Re-scope once REQ-PROC-044's observability AC
    completes.

- task_name: "web-searches-tsv-instrumentation"
  backlog_id: IMPL-J
  req_path: "requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/requirements.md"
  requirements_version: "eabdeaf0"
  covers_acs: [AC-03, AC-11]
  covers_sections: [SEC-03]
  effort: S
  layer: process
  after: ["IMPL-B"]
  task_type: impl
  opus_recommended: false
  target_package: "claude-optimize"
  scope_description: "Instrument the downstream executor surface (claude-log or the executor skills themselves) to append one row per performed web search to .factory/optimize/history/web_searches.tsv. Format: timestamp, task_id, query, recommended_by_optimization_approach (bool)."
  release_description: ""
  implementation_notes: |
    SEC-03 names this file as the canonical search log; the audit skill (IMPL-G)
    uses it to evaluate the web-research heuristics table empirically over time.
    Append-only file, never pruned. The recommended_by flag lets the audit
    compare actual searches against the optimization_approach recommendation
    distribution.

- task_name: "duckdb-optional-query-layer"
  backlog_id: IMPL-M
  req_path: "requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/requirements.md"
  requirements_version: "eabdeaf0"
  covers_acs: [AC-11, AC-12]
  covers_sections: []
  effort: M
  layer: process
  after: ["IMPL-G"]
  awaiting: ["v1.5-prioritization"]
  awaiting_note: "Optional v1.5 enhancement (round-4 §6 IMPL-M, decision N-D-7). Hold until claude-optimize-audit (IMPL-G) has accumulated runs.tsv data that warrants joins; not required for v1."
  task_type: impl
  opus_recommended: false
  target_package: "claude-optimize"
  scope_description: "Add a DuckDB-based optional query layer to claude-optimize-audit for cross-session analytics over JSONL inputs. No ETL, no schema migration, no daemon — DuckDB reads raw JSONL. runs.tsv remains canonical."
  release_description: ""
  implementation_notes: |
    See round-4 Part 1.3 for the rationale (DuckDB chosen as embedded
    query-time layer; never as canonical store). v1.5 implementer must
    document that DuckDB-over-JSONL is account-local (per round-4 Part 1.4) so
    no caller treats those queries as canonical history.

## Coverage Matrix

| AC / SEC | Task(s) (backlog ID) | Target Package |
|---|---|---|
| AC-01 (one task per invocation or no-op) | IMPL-E | claude-optimize |
| AC-02 (monitors post-task-complete; no session JSONL routine) | IMPL-C, IMPL-F, IMPL-H, IMPL-I | claude-optimize |
| AC-03 (state under .factory/optimize/) | IMPL-B, IMPL-J | claude-optimize |
| AC-04 (G-INV-1 produced tasks auto-blocked) | IMPL-D | claude-optimize |
| AC-05 (G-INV-2 monitors as standalone Python, not tools) | IMPL-C | claude-optimize |
| AC-06 (G-INV-3 separate audit skill) | IMPL-G | claude-optimize |
| AC-07 (bugfix candidate strictly first) | IMPL-E | claude-optimize |
| AC-08 (verifiable AC via ground-truth signals) | IMPL-E | claude-optimize |
| AC-09 (every run commits runs.tsv + state.json) | IMPL-E | claude-optimize |
| AC-10 (write-surface deny-list programmatic enforcement) | IMPL-D | claude-optimize |
| AC-11 (two metrics: user-unblock-rate + revert-rate) | IMPL-G, IMPL-J, IMPL-M | claude-optimize |
| AC-12 (deterministic N-point health score) | IMPL-G, IMPL-M | claude-optimize |
| SEC-01 Monitor Taxonomy | IMPL-C | claude-optimize |
| SEC-02 Two-Field Taxonomy | IMPL-E | claude-optimize |
| SEC-03 Web Research Heuristics | IMPL-E, IMPL-J | claude-optimize |
| SEC-04 Write-Surface Deny-List | IMPL-D | claude-optimize |

100% AC/section coverage. Verification: TASK-PROC-006-06 (review type) is the
mandatory separate verification task; its `after:` list will receive every
backlog ID created here in the post-creation step.

## Dependency Graph

```
IMPL-B ─┬─ IMPL-C ─┬─ IMPL-E ── IMPL-G ── IMPL-M (optional)
        │          └─ IMPL-F
        ├─ IMPL-D ──┘
        ├─ IMPL-H
        └─ IMPL-J

IMPL-I (external, awaiting TASK-PROC-044)
```

No cycles. Every task has sizing signals (effort + opus_recommended). Bugfix
priority and G-INV invariants flow through IMPL-D, IMPL-E, IMPL-G as named
ACs / hard constraints.

## Notes on YAGNI gate

Each task scope is the minimum needed to satisfy its named ACs/sections. The
"Deferred (YAGNI)" pattern is invoked by IMPL-M (optional v1.5 — explicit
reopen trigger: claude-optimize-audit data warrants joins) and IMPL-I (deferred
until TASK-PROC-044 observability schema lands). No other deferrals.
