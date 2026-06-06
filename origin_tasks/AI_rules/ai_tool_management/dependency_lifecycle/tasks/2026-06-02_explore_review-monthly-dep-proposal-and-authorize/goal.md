---
task_id: TASK-PROC-061-08
type: explore
parent_requirement: REQ-PROC-061
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: pending
effort: M
created: 2026-06-02
expected_tool_calls: 45
writes_requirements: false
recurring: true
covers:
  acceptance_criteria: [AC-12]
  sections: []
scope_description: "Recurring decision task: review the latest monthly dependency proposal and authorize downstream actions. Executes autonomous bumps/removals in-session; creates scoped impl tasks for major-version bumps."
release_description: ""
opus_recommended: false
after: []
requirements_version:
  commit: 676c488f
  file: ../requirements.md
---

# Goal: Review Monthly Dependency Proposal and Authorize Actions

## Objective

This is a **standing recurring task**. It is NOT a one-off exploration — it is the developer's
action-authorization entry point for each monthly dependency review cycle. It is reset to
`status: pending` by the agent that completes the monthly review (REQ-PROC-061 AC-12).

Each cycle: read the current proposal, walk the developer through each class of finding, execute
authorized autonomous actions in-session, and create scoped impl tasks for any authorized
major-version bumps.

## Background

The monthly dependency review cron writes its proposal to
`automation/dependency_reviews/YYYY-MM/proposal.md`. Three finding classes are possible:

| Class | Description | Action |
|---|---|---|
| Autonomous bumps | Patch/minor bumps that passed DG1–DG4 (REQ-PROC-056) | Execute in-session after developer authorization |
| Removal candidates | Packages with no evidence of use (AC-11) | Remove from pubspec.yaml in-session after developer authorization |
| Major-version bumps | Semver-major upgrades requiring human pre-authorization (AC-07) | Create one scoped impl task per authorized bump |

The protocol file for each cycle records the developer's decisions and outcomes so future
sessions see the documented reasoning, not a silent gap.

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-06-02_00_user_initial_input.md`

Read it as a seed bed, not a spec.

For complete requirements at task creation time:
```
git show 676c488f:requirements_tasks/process/AI_rules/ai_tool_management/dependency_lifecycle/requirements.md
```

Current requirements: ../requirements.md

## How to Approach This

1. **Find the current proposal**: `ls automation/dependency_reviews/` — take the latest YYYY-MM folder.
2. **Read `proposal.md`**: identify all findings by class.
3. **Present by class** to the developer: start with removals (lowest risk), then autonomous bumps, then major bumps.
4. **Execute authorized actions** (removals + autonomous bumps): apply, run `flutter pub get`, `dart fix --apply`, full quality gates (REQ-PROC-046 + REQ-PROC-002 + REQ-PROC-052). Record evidence.
5. **Create impl tasks** for each authorized major bump (one task per package): reference the proposal and the developer's authorization in the task goal.
6. **Write the cycle protocol** to `plans_and_protocols/YYYY-MM-DD_01_protocol_YYYY-MM-cycle.md`.

## Seeds

1. Does the proposal have any deferred findings from a previous cycle that should be re-evaluated now?
2. Are any removal candidates actually indirectly required (platform binaries, code-generation support) — can the indirect dependency chain be named?
3. For authorized major bumps: what is the right scope for each impl task? Migration complexity varies by package — the task description should reflect what is actually known from the proposal.
4. Did any quality gate fail after applying an autonomous bump? If so, escalate that bump to manual review rather than force-passing.

## Execution Model

Read the proposal; present findings; act. The developer is present for this task — decisions are made interactively, not inferred.

**No web research expected** for routine cycles. If a major bump requires CHANGELOG investigation to scope an impl task, delegate to a general-purpose agent with a focused question.

## Output

A future session reading the protocol file should be able to answer without re-investigating:
- Which autonomous bumps were applied, and which were deferred and why
- Which removal candidates were removed, kept (with reason), or deferred
- Which major bumps were authorized and which impl tasks were created for them

## Acceptance Criteria

- [ ] All findings from the current proposal have been presented to the developer and a decision recorded for each
- [ ] All authorized autonomous bumps applied; quality gates pass; evidence recorded in protocol
- [ ] All authorized removal candidates removed from pubspec.yaml; quality gates pass; evidence recorded
- [ ] One scoped impl task created per authorized major-version bump
- [ ] Protocol file written to plans_and_protocols/ for this cycle

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| monthly-dep-review cron | recurring | This task is reset to pending by the review agent after proposal is written |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-061-07](../2026-06-02_explore_decide-2026-06-major-bumps/goal.md) | Scope boundary — covers June 2026 major-bump decisions; this task covers all future cycles |
| [TASK-PROC-061-05](../2026-06-02_impl_apply-2026-06-autonomous-bumps/goal.md) | Scope boundary — covers June 2026 autonomous bump execution; this task covers all future cycles |
