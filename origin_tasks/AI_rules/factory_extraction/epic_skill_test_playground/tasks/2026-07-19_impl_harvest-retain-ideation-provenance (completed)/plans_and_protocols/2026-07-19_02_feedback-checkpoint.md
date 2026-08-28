---
skill: task-create
mode: interactive
decision: "revised"
task_id: TASK-PROC-068-35
captured_at: 2026-07-19
---

# Question

Registry task-workspace one-liner framed tasks as 'drive and log work' (process/work-log only)

# Developer Answer

"Files inside requirements_tasks/**/tasks/<task>/ that drive and log work" => that is not entirely correct. Tasks do not only define the process how to build something, but they also contain technology specific implementation details. The requirmenets only capture the what, the tasks capture the how. That means that tasks are the real specification of the product, the requirmenets are just the abstraction. We have a good definition somewhere, I think in the requ explore and/or task create skills.

# Rationale Captured

Developer corrected the framing: tasks capture the technology-specific HOW (the product's concrete implementation specification), the counterpart to a requirement's abstract WHAT — not mere work-log. This reshaped the task-workspace registry definition AND justified scoping the AC-11 retention to the referenced ideation index+ledger rather than wholesale factory-runtime/task-workspace category inclusion (kept test_harness_app clean per AC-21).
