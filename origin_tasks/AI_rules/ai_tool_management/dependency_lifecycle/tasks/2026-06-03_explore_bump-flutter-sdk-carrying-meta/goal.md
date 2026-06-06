---
task_id: TASK-PROC-061-12
type: explore
parent_requirement: REQ-PROC-061
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: pending
after: []
covers:
  acceptance_criteria: []
  sections: []
effort: M
created: 2026-06-03
expected_tool_calls: 20
skill_chain_depth: 2
scope_description: "Evaluate a Flutter SDK bump that would carry meta 1.17.0 → 1.18.2 (pinned by the bundled SDK)"
release_description: ""
opus_recommended: false
requirements_version:
  commit: 804bcfc0
  file: ../requirements.md
---

# Goal: Evaluate a Flutter SDK bump (carries meta 1.18.2)

## Objective

`meta` is pinned at 1.17.0 by the bundled Flutter SDK (currently 3.41.4) via
`flutter` / `flutter_test`. The 2026-06 review proposed `meta 1.18.2`, but it is
**not reachable** without upgrading the Flutter SDK itself. This task evaluates
whether/when to bump the Flutter SDK — which would carry `meta` to 1.18.2 as a
side effect — weighing the SDK upgrade's own risk and value against the small
gain from `meta` alone.

What is not yet known: which Flutter SDK version pins `meta >=1.18.2`, what else
that SDK changes (Dart version, framework breaking changes, plugin
compatibility), and whether an SDK bump is justified now or should wait for an
independent driver.

## Background

Deferred from **TASK-PROC-061-05** (apply 2026-06 autonomous bumps). A real
`pub solve` in the devcontainer showed `meta 1.18.2` is gated by the SDK pin,
not by any direct constraint we control. `meta` on its own does not justify an
SDK upgrade; this task exists so the deferral is tracked and folded into the
next Flutter-SDK-bump decision rather than lost.

Evidence: `automation/dependency_reviews/2026-06/proposal.md` (Deferred targets)
and `../2026-06-02_impl_apply-2026-06-autonomous-bumps/plans_and_protocols/2026-06-02_01_protocol_apply-bumps.md`.

For complete requirements at task creation time:
```
git show 804bcfc0:requirements_tasks/process/AI_rules/ai_tool_management/dependency_lifecycle/requirements.md
```

Current requirements: ../requirements.md

## How to Approach This

Treat `meta` as a passenger, not the driver. The real question is the Flutter
SDK upgrade's risk/value. Identify the lowest SDK version that satisfies
`meta >=1.18.2`, then assess that SDK's full change surface against the project.

## Seeds

- Which Flutter/Dart SDK version first pins `meta >=1.18.2`?
- What breaking changes / plugin-compatibility shifts come with that SDK jump?
- Is there an independent reason to bump the SDK soon (security, a needed
  framework fix, a plugin that requires it)? If not, is deferring correct?
- Does the devcontainer toolchain need updating in lockstep, and what is the
  cost of that?

## Execution Model

Gather from `pubspec.yaml` (`environment.sdk`), the installed Flutter version,
and pub.dev `meta` SDK constraints. Delegate web research (Flutter release notes
for the target version) to a spawned `general-purpose` agent. The session model
is fixed at launch (Sonnet).

## Output

A clear recommendation: bump the SDK now (with the target version and a
migration risk summary) or defer (with the condition that should trigger a
re-check). `meta 1.18.2` lands automatically whenever the SDK bump happens.

## Acceptance Criteria

- [ ] Exploration produced at least one synthesis round
- [ ] The synthesis defines the problem space in terms that were not fully known at task creation
- [ ] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [ ] The output is honest about what remains uncertain

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No hard blockers |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-061-05](../2026-06-02_impl_apply-2026-06-autonomous-bumps/goal.md) | Predecessor — deferred meta 1.18.2 here after the real solve showed the SDK pin |

## Notes

Deferred from TASK-PROC-061-05 per the developer's Option-A decision (2026-06-03).
