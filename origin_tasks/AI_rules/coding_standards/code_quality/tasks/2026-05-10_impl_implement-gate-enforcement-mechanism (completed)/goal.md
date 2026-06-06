---
task_id: TASK-PROC-046-11
type: impl
parent_requirement: REQ-PROC-046
urgency: 3
urgency_reason: U3-PROC-IMPROVEMENT
impact: 5
impact_reason: I5-ENAB
status: completed
effort: L
created: 2026-05-10
started: 2026-05-19
completed: 2026-05-19
session_completed_at: 2026-05-19T06:50:37Z
after: [TASK-PROC-046-03, TASK-PROC-046-04, TASK-PROC-046-05, TASK-PROC-052-01, TASK-PROC-002-02, TASK-PROC-002-03]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-10]
  sections: []
scope_description: "Implement automated gate enforcement: extend the quality-checker agent to invoke every gate from REQ-PROC-046, REQ-PROC-002, REQ-PROC-052; create the verify-quality skill that CLAUDE.md and INDEX.md already reference; configure .claude/settings.json hooks (Stop + commit) so gates run without LLM cooperation; implement the five-cycle back-pressure counter and escalation behavior."
release_description: ""
opus_recommended: true   # reason: substantial architectural work; designing the enforcement mechanism touches agents, skills, hooks, and task-complete; benefits from Plan phase
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ""
  file: ../../requirements.md
session_id: f3baf030-84f3-4593-9241-cee2bf64864a
session_account: gmail
---
# Goal: Implement automated gate enforcement (verify-quality skill, hooks, back-pressure protocol)

## Objective

REQ-PROC-046, REQ-PROC-002, and REQ-PROC-052 define a back-pressure protocol that should make code-quality gates *blocking* rather than advisory: an LLM cannot declare a change complete while any gate is failing; failures trigger revision; five cycles cap escalation. Today none of this is enforced. The `quality-checker` agent runs `dart analyze` and layer-boundary checks but is advisory (its RED status doesn't halt anything). The `verify-quality` skill referenced by CLAUDE.md and INDEX.md does not exist as a file. The five-cycle counter has no implementation surface.

This task makes the protocol real. Three layers of enforcement work together: an extended `quality-checker` agent that knows about every gate; a `verify-quality` skill that wraps it and is the canonical entry point CLAUDE.md and INDEX.md already reference; and `.claude/settings.json` hooks that run gates without LLM cooperation at the natural enforcement points.

## Requirements Summary

REQ-PROC-046 AC-10: code that fails any active quality gate is never declared complete; failures trigger revision; five-cycle bound; escalation on irrecoverable failure. The same protocol is inherited by REQ-PROC-002 AC-07 and REQ-PROC-052 AC-09.

This task is the only one whose deliverable is the *mechanism* that makes the protocol real. Sibling tasks deliver the *gates* (analyzer rules, scripts, mutation testing, accessibility tests, etc.). This task wires the gates into a runner that the protocol applies to.

Current requirements: ../../requirements.md

## Scope

### In Scope

**Layer 1 — Extend the `quality-checker` agent** (`.claude/agents/quality-checker.md`):
- Add invocations for every gate that has a script:
  - G1: `flutter analyze` (already runs) + `dart fix --apply` idempotence check + `dart pub get --enforce-lockfile`
  - G2 complexity bounds: parsed from `flutter analyze` output (DCM rules report violations there)
  - G3 test correctness: run `flutter test` (currently absent — add it)
  - G3 critical-path coverage: invoke `scripts/quality/check_critical_path_coverage.*` (from TASK-PROC-046-04)
  - G4 architectural purity: already covered by analyzer + agent's existing layer-boundary check
  - G5 suppression discipline: invoke `scripts/quality/check_suppression_justification.*` (from TASK-PROC-052-01)
  - G6 accessibility: covered by widget tests in G3 once the backfill lands
  - G8 bundle size: invoke `scripts/quality/check_bundle_size.*` (from TASK-PROC-046-05) — release-cadence only
  - TQ1 assertion-strength: covered by G1 once analyzer rules land (TASK-PROC-046-03)
  - TQ4 determinism: invoke `scripts/quality/check_test_determinism.*` (from TASK-PROC-002-03) — release-cadence only
  - SP1–SP4, SP6: invoke the grep gate scripts (from TASK-PROC-052-01)
- Add a "release-cadence vs per-change" mode flag so the agent only runs heavy gates (G7 dynamic, G8, TQ4, mutation testing) when explicitly requested.
- Make the agent's output **blocking** rather than advisory: RED status produces an exit code that downstream consumers (verify-quality skill, task-complete, hooks) can act on.

**Layer 2 — Create the `verify-quality` skill** (`.claude/skills/verify-quality/skill.md`):
- The canonical entry point. CLAUDE.md and INDEX.md already reference it.
- **Verifies the working tree is in a clean state before running gates** (`git status --porcelain` empty, or only the changes from the current task — implementer decides the policy). Refuses to run on a dirty tree without an explicit override flag (`--allow-dirty`). This closes the "gates passing locally because of stale build artifacts or uncommitted local fixes" pitfall named in REQ-PROC-046 §Common Pitfalls.
- Spawns `quality-checker` agent with the appropriate cadence flag.
- Reads the agent's output; if RED, halts and presents the failures to the LLM caller in a structured form.
- Implements the five-cycle counter: maintains a `cycle_count` field in the active task's `plans_and_protocols/cycle_state.json` (or similar). Each invocation increments. On RED at cycle 5, the skill **uses the project's existing automation Q&A mechanism** per `.claude/skills/claude-automated-mode/skill.md` lines 76–139:
  - Writes `automation/pending_feedback/<TASK_ID>/question.md` using `automation/pending_feedback/TEMPLATE_question.md` as the frontmatter source of truth (fields: `task_id`, `session_id`, `account`, `status: awaiting_answer`, `asked_at`, `skill: verify-quality`).
  - Copies `automation/pending_feedback/TEMPLATE_answer.md` to `<TASK_ID>/answer.md` (the AI does NOT write to answer.md — it must keep the `<!-- AWAITING_HUMAN_ANSWER -->` sentinel until the developer answers).
  - Runs `bash scripts/automation/terminate_session.sh` to exit cleanly.
  - The session's `goal.md` keeps `status: in_progress` and its `session_id`; the orchestrator's `scripts/automation/orchestrate.py:find_answered_feedback` (lines 1362–1419) detects the pending question and `scripts/tasks/next_tasks.py:load_pending_feedback_ids` (lines 74–122) keeps the task off the queue.
  - On resume (when developer fills `answer.md`), the orchestrator runs `claude --resume <session_id> -p <answer-content>` and the cycle counter resets in the resumed session's first verify-quality invocation.
  - There is no separate `cycle_state.json` discoverability concern — the cycle counter file lives in `plans_and_protocols/` and is read by the resumed session naturally.
- Updates INDEX.md to remove any references to the skill being a future stub.

**Layer 3 — Configure hooks** (`.claude/settings.json`):
- `Stop` hook: at the end of every Claude Code response, invoke `verify-quality` if any file in `lib/`, `test/`, or `integration_test/` was modified during the response. This guarantees gates run even if the LLM forgets to invoke them.
- `PreToolUse(Bash:"git commit*")` hook: invoke `verify-quality`; halt commit if RED. This is the absolute backstop.
- The hooks must respect the per-change vs. release-cadence distinction — `Stop` runs per-change gates only; release gates remain manually triggered or scheduled.
- Document hook behaviour and how to bypass in emergencies (`SKIP_QUALITY_GATES=1` environment variable, used only with explicit user authorization).

**Layer 4 — Integrate with `task-complete` skill** (`.claude/skills/task-complete/skill.md`):
- Before marking a task as completed, invoke `verify-quality`.
- If RED, refuse completion and report the failures.
- This is the final backstop: even if the `Stop` hook misfires, task-complete blocks any task from being marked done while gates fail.

### Out of Scope

- Implementing the gate scripts themselves. Each is owned by a sibling task. This task only *wires* them.
- Adding new gates beyond those in the three requirements. The gate set is closed (per REQ-PROC-046 §Behavior).
- Changing the protocol's substance. The five-cycle bound and escalation behavior are specified by REQ-PROC-046 AC-10; this task implements them.
- CI / GitHub Actions integration. `.claude/settings.json` hooks suffice for solo-dev use; CI is a separate concern.

## Acceptance Criteria

- [x] `.claude/agents/quality-checker.md` invokes every per-change gate from the three requirements via the appropriate script or analyzer; release-cadence gates are gated behind a mode flag.
- [x] `quality-checker` exits non-zero on RED and emits a structured failure summary; downstream consumers can rely on the exit code.
- [x] `.claude/skills/verify-quality/skill.md` exists, spawns `quality-checker`, implements the five-cycle counter, writes escalation notes, and refuses further invocation past cycle 5.
- [x] CLAUDE.md and INDEX.md references to `verify-quality` resolve to the new skill.
- [x] `.claude/settings.json` includes a `Stop` hook that runs `verify-quality` when `lib/`, `test/`, or `integration_test/` was modified, and a `PreToolUse(Bash:"git commit*")` hook that halts on RED.
- [x] `task-complete` skill invokes `verify-quality` before marking completion; refuses completion on RED.
- [x] Bypass mechanism (`SKIP_QUALITY_GATES=1`) is documented with explicit warning that it should be used only with user authorization.
- [x] An integration smoke test demonstrates the full chain: introduce a deliberate violation in `lib/`, observe that `verify-quality` returns RED, confirm `task-complete` refuses, confirm the `git commit` hook halts.
- [x] The five-cycle counter resets when the task transitions to a new task or when explicitly cleared by the user.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-046-03 | pending | Analyzer rules must land — they are gates G1, G2, partially G6 |
| TASK-PROC-046-04 | pending | Critical-path coverage script must exist for the agent to invoke it |
| TASK-PROC-046-05 | pending | Bundle-size script must exist for release-cadence invocation |
| TASK-PROC-052-01 | pending | Grep gates (suppression, debug, secrets, network, telemetry, weak crypto) must exist |
| TASK-PROC-002-02 | pending | Mutation tooling must exist for the AC-02 gate to run |
| TASK-PROC-002-03 | pending | Determinism script must exist for release-cadence invocation |

## Notes

This task supersedes the part of TASK-PROC-046-06 (CLAUDE.md update) that says *"update the verify-quality skill (or equivalent) to enforce the gates if it does not already; align its checklist with the gate set"* — that line was written assuming the skill existed; it doesn't. TASK-PROC-046-06 should now focus on documentation only (describe the gates and the protocol in CLAUDE.md), and rely on this task to deliver the implementation. Update TASK-PROC-046-06's `after:` to include this task once it's queued.

**Why hooks matter even with a skill**: a skill the LLM forgets to invoke might as well not exist. A hook fires on harness events the LLM cannot suppress. The two layers (skill + hook) defend against different failure modes — skill against direct invocation paths; hook against forgotten invocation.

**Five-cycle counter location**: writing to the active task's `plans_and_protocols/cycle_state.json` keeps the counter task-scoped (different tasks don't share a cycle budget) and survives session boundaries (the file is on disk). On task transition the counter resets because the new task has its own `plans_and_protocols/`.

**Performance concern**: the `Stop` hook runs after every response that touched `lib/`. The full per-change gate set (analyzer + tests + grep gates) takes time. Cache strategies — only re-run gates whose inputs changed since the last green — are valuable but out of scope here; this task delivers correctness first, optimization can be a follow-up.
