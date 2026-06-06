---
task_id: TASK-PROC-051-01
type: explore
parent_requirement: REQ-PROC-051
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
effort: M
created: 2026-05-17
started: 2026-05-17
completed: 2026-05-17
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Explore and define Python code quality rules + decide whether/how to update existing Dart-scoped code_quality requirements"
release_description: ""
opus_recommended: true   # reason: explore task with cross-cutting scope (doc/, scripts/, requirements organization) + explicit trade-off decisions (rename existing requirement vs. add sibling vs. parent-shared)
writes_requirements: true
requirements_version:
  commit:
  file:
---

# Goal: Define Python Code Quality Rules + Restructure Code-Quality Requirements

## Objective

What does "good Python code quality" mean for this repo, and how should it be structured as governance? The orchestrator and its supporting scripts have grown into ~8 000 lines of Python with zero `doc/` coverage — the same kind of governance the Dart side gets from `doc/architecture/`, `doc/testing/`, `doc/linter/`, etc. We do not yet know what the right set of rules is, how heavyweight the governance should be, or how the existing Dart-scoped REQ-PROC-046 should be reconciled with a Python sibling.

What is not yet known:
- Which rules are worth codifying versus left as implicit conventions
- Whether `doc/python/` should mirror `doc/<dart-equivalent>/` shape or take a different shape
- How `REQ-PROC-046` (Dart code quality, currently implicit-by-paths) should be repositioned — clarified, renamed, restructured as a shared parent, or left alone
- Whether the same back-pressure protocol that governs Dart quality applies to Python
- Whether tooling config (`pyproject.toml`, `ruff`, `mypy`) lives inside this requirement's scope or a sibling

## Background

The orchestrator was built incrementally as a tool to drive unattended LLM sessions. It was originally "a script." It is now 3328 lines in `scripts/automation/orchestrate.py` plus 5031 lines of tests, with substantial patterns of its own (dependency injection via `OrchestratorDeps`, frozen-clock testing, context managers for cleanup invariants, dual-tracker consolidation, enums over bool returns). Most of those patterns emerged from real bugs that taught us why they matter — but none of that learning is captured outside the code itself.

`doc/` today is entirely Dart-scoped — every file in `doc/architecture/`, `doc/testing/`, `doc/linter/`, etc. assumes the audience is writing Dart for `lib/`, `test/`, or `integration_test/`. `REQ-PROC-046` (the back-pressure code-quality gate) is the same: its acceptance criteria cite Dart-only paths and tools. The implicit "Dart-only" scope was fine when there was little Python in the repo. With 8 000+ lines now under no governance, the implicit scoping is starting to mislead.

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-05-17_00_user_initial_input.md`

Concrete suggestions made during the originating conversation — including the proposed `doc/python/` file list, patterns to codify, anti-patterns observed, and open meta-questions — are preserved in:
`plans_and_protocols/2026-05-17_01_prior_findings_for_exploration.md`

Read both as a seed bed, not a spec. The exploration is free to discard, reorder, or invert any of those starting points.

For complete requirements at task creation time: no `requirements.md` exists at this path yet — this exploration produces it.

Current requirements (after exploration completes): ../requirements.md

## How to Approach This

Use design thinking as the guiding process — empathize before defining, diverge before converging, let questions lead, iterate. A single pass through the material will not be enough. Surface surprises — the most valuable discoveries are the ones that were not anticipated.

Read the existing Dart code-quality requirement (`REQ-PROC-046`) closely before drafting anything Python-side. The implicit-Dart scoping there is the elephant in the room and any decision about Python rules has to take a position on it (clarify, restructure, leave alone).

Read the orchestrator (`scripts/automation/orchestrate.py`) and its tests (`scripts/automation/tests/test_orchestrate.py`) to see which patterns deserve to be elevated — not just from `01_prior_findings_for_exploration.md` but from a fresh read. The patterns there are the most concrete evidence of what works for this repo specifically. Generic Python style guides (PEP 8, etc.) are easy to copy; what's missing is the project-specific lessons.

## Seeds

These are NOT a checklist — they are lenses to look through. Expect some to lead nowhere and others to open new threads.

- **Why does the orchestrator's `OrchestratorDeps` pattern feel different from typical Python testing?** What does writing it that way prevent that `mock.patch` doesn't? Is the rule "always use Deps" too strong, or is it the right strong opinion?

- **The `print()` question.** The orchestrator's `print(f"[orchestrator {_ts()}] ...")` statements are simultaneously its public protocol (consumed by `sleep_when_autorun_done.ps1` and the monitoring cron) AND its internal debug log. Is that conflation a problem to fix, a feature to preserve, or both?

- **Three hand-rolled YAML parsers in `orchestrate.py`** (`update_goal_session_fields`, `_promote_task_to_opus_for_context_limit`, `_rewrite_question_session_id`) all do similar work line-by-line. Is "use PyYAML" the right rule, or do the implementation-specific concerns (preserving comments, atomic writes) justify the duplication?

- **What does `coding_standards/` mean as a folder, today?** It has four buckets (`code_quality`, `context_window`, `privacy_and_security`, `testing`). All implicitly assume Dart. If Python becomes a peer, does the folder need a parent `requirements.md` that says how language-scoping works, or is that bureaucratic? What would happen if a third language appeared?

- **The `--max-tasks` accounting policy change** during this conversation (errors no longer count) was a policy decision, not a style decision. Should code-quality requirements be allowed to encode policy ("only successes consume a slot"), or should policy live elsewhere? Where does the boundary go?

- **Back-pressure for Python?** REQ-PROC-046's central mechanism is "LLM cannot declare done while a gate fails, 5-cycle bound." Does that apply to Python work in this repo, or is the Python surface too small / too internal for a formal gate protocol?

- **What's NOT in `scripts/automation/orchestrate.py` that should be?** Reading the code, what felt like "I wish there were a rule about this"? Where did the patterns we just refactored come from — were they observed once and codified, or did they emerge from repeated pain? The patterns that emerged from pain are the most valuable to preserve.

## Execution Model

Gather raw material — read `scripts/automation/orchestrate.py`, its tests, REQ-PROC-046, REQ-PROC-043, REQ-PROC-048, and at least one or two of the `doc/` files on the Dart side to understand the existing pattern. Surface facts and anomalies. Synthesize iteratively; multiple gathering rounds may be needed before the problem space is well understood.

The session's model is fixed at launch (Opus when `opus_recommended: true`, Sonnet otherwise). No mid-session model switching.

**Web research**: For seeds requiring external knowledge — best practices, prior art, tool capabilities, what others have tried — use web search. Always delegate web research to a spawned `general-purpose` agent with a focused question; never run WebSearch inline. Raw web content inflates the gathering agent's context window fast with irrelevant results; the subagent returns only a distilled summary while the raw content stays in its own context.

Frame search queries as questions rather than keyword bags — this produces more useful results (e.g. *"how do solo maintainers structure Python code-quality rules when AI agents write most of the code?"* rather than *"python code quality LLM"*). When a snippet is insufficient, instruct the subagent to use WebFetch to read the full page before summarising.

## Output

When this exploration is done, a future implementer reading the synthesis output should understand:

- What the recommended structure is for `doc/python/` — which files, what each contains, what the writing style should be
- What the recommended structure is for `requirements_tasks/process/AI_rules/coding_standards/` post-exploration — does REQ-PROC-046 stay Dart-only with explicit scoping, does it become a shared parent, does the `python_code_quality/` folder live where it is or move
- Which patterns from the orchestrator have been elevated to documented rules (with their "why")
- Which anti-patterns have been called out (with their "why")
- Whether tooling config (`pyproject.toml`, `ruff`, `mypy`) is in scope for this requirement or deferred to a sibling
- Whether the Dart back-pressure protocol applies to Python or a different model fits
- A concrete list of next-stage tasks: at minimum an `impl` task to author the chosen `doc/python/` files and an `impl` task (if needed) to restructure REQ-PROC-046 and related requirements

The output is honest about what remains uncertain — for example, if the choice between "shared parent requirement" and "parallel siblings" comes down to taste and you want the user to decide, say so explicitly rather than pre-deciding silently.

## Acceptance Criteria

- [x] Exploration produced at least one synthesis round
- [x] The synthesis defines the problem space in terms that were not fully known at task creation
- [x] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [x] The output is honest about what remains uncertain
- [x] A `requirements.md` is drafted at `requirements_tasks/process/AI_rules/coding_standards/python_code_quality/requirements.md` with REQ-PROC-051 as its ID
- [x] A position is taken (with rationale) on whether REQ-PROC-046 should be clarified, restructured, or left alone; if change is proposed, the migration path is sketched — Position: sibling without rename; REQ-PROC-046 left alone (its ACs are already explicit-Dart in body text). See `plans_and_protocols/2026-05-17_04_protocol_synthesis.md`.
- [x] Next-stage `impl` task seeds (one for `doc/python/` authoring, one for any requirement restructure) are drafted as goal.md files in this task's `plans_and_protocols/` for `requ-derive-from-flow` or manual task-create to pick up — Promoted to full tasks: TASK-PROC-051-02 (mechanism), TASK-PROC-051-03 (doc/python/ authoring), TASK-PROC-051-04 (cleanup). No requirement restructure needed (sibling decision).

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |
