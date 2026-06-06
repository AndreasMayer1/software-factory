---
requirement: REQ-PROC-061
requirements_version: bbc9d0a5
created: 2026-06-03
mode: full
note: "Granularity per developer: merge classifier+registry (1+2) and doc+verification (4+5); trial-removal standalone with opus."
---

# Task Creation Plan for REQ-PROC-061 (new ACs AC-13/14/15)

## Tasks

- task_name: "harden usage-check classifier and add retention registry"
  req_path: "requirements_tasks/process/AI_rules/ai_tool_management/dependency_lifecycle/requirements.md"
  requirements_version: "bbc9d0a5"
  covers_acs: [AC-13, AC-14]
  effort: M
  layer: scripts
  after: []
  task_type: impl
  opus_recommended: false
  implementation_notes: >
    Edit scripts/release/check_dependency_usage.py via claude-write-script.
    AC-13: add config-referenced class (scan analysis_options.yaml include/plugins/custom_lint
    for package refs) and native-declared class (cross-ref .flutter-plugins-dependencies);
    tier output likely-dead vs needs-manual-review vs retained. Harden the import matcher to
    also catch `export 'package:'` and conditional/deferred imports (#4); add hygiene checks —
    runtime dep imported only from test/, stale INDIRECT_REQUIREMENTS entries, surface
    dependency_overrides (#5). AC-14: introduce a data-owned retention registry
    (proposed automation/dependency_reviews/kept.yaml: package, class, reason, acknowledged date);
    script reads it into an acknowledged-kept classification; report stale entries (package gone);
    wire the decision task to append on a keep. Externalize INDIRECT_REQUIREMENTS to YAML and add
    --fail-on-candidates exit code (#6). Native declaration is needs-manual-review, never auto-retain.

- task_name: "implement empirical trial-removal recovery model"
  req_path: "requirements_tasks/process/AI_rules/ai_tool_management/dependency_lifecycle/requirements.md"
  requirements_version: "bbc9d0a5"
  covers_acs: [AC-15]
  effort: M
  layer: scripts+process
  after: [PLAN-TASK-1]
  task_type: impl
  opus_recommended: true   # reason: developer-directed; cross-cutting synthesis across script, CI coverage, decision-task workflow, and residual-risk policy
  implementation_notes: >
    Implement the trial-removal recovery procedure per AC-15 and the ADR
    (decisions/2026-06-03_trial-removal-recovery-model.md): isolated branch/worktree, run
    analyzer + tests + every CI-covered platform's build-plus-smoke lane, revert on red and
    write the failing signal into the AC-14 retention registry as keep-justification. Gate on
    per-target-platform CI coverage derived from .flutter-plugins-dependencies; allow-with-residual-risk
    for uncovered platforms (record acceptance in proposal + decision task). Exempt config-referenced
    and code-generation packages. Demonstrate the model end-to-end on the concrete local_notifier
    removal candidate (#9). Depends on the registry from task 1.

- task_name: "document AC-13/14/15 and verify usage-check end-to-end"
  req_path: "requirements_tasks/process/AI_rules/ai_tool_management/dependency_lifecycle/requirements.md"
  requirements_version: "bbc9d0a5"
  covers_acs: [AC-10, AC-13, AC-14, AC-15]
  effort: M
  layer: docs
  after: [PLAN-TASK-1, PLAN-TASK-2]
  task_type: impl
  opus_recommended: false
  implementation_notes: >
    AC-10 (single authoritative location): update doc/process/dependency_lifecycle.md to document
    the new evidence classes, the tiered output, the retention registry, and the trial-removal
    recovery model — consistent with REQ-PROC-061. VERIFICATION (merged from the separate verify
    task per developer): run check_dependency_usage.py and confirm (a) very_good_analysis/custom_lint/
    clean_architecture_kit are no longer plain removal candidates (config-referenced), (b) native-declared
    packages appear in needs-manual-review, (c) a keep written to kept.yaml suppresses that package next
    run and a stale entry is reported, (d) the trial-removal procedure + CI-coverage gating is documented
    and exercised. Any AC not demonstrably met is a blocking error.

## Coverage Matrix

| AC | Task(s) |
|----|---------|
| AC-10 | task-3 (re-touch; also covered by completed lifecycle-authoritative-documentation) |
| AC-13 | task-1, task-3 |
| AC-14 | task-1, task-3 |
| AC-15 | task-2, task-3 |

Verification: folded into task-3 (developer merged 4+5); satisfies AC-02 verification-coverage
via the Verification section in the last task.
