---
task_id: TASK-PROC-061-18
type: explore
parent_requirement: REQ-PROC-061
urgency: 2
urgency_reason: U2-MAINT
impact: 3
impact_reason: I3-PROCESS
status: completed
effort: M
created: 2026-06-03
started: 2026-06-03
completed: 2026-06-03
expected_tool_calls: 25
skill_chain_depth: 2
synthesis_dependent: true
synthesis_justification: "Must hold the script's classifier logic, the monthly-review process, CI platform coverage, and the requirement's ACs simultaneously to design a coherent recovery model."
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-11, AC-12]
  sections: []
scope_description: "Harden the dependency-retirement / usage-check (check_dependency_usage.py) — reduce false positives, add a durable false-positive recovery path, and design a test-driven trial-removal model with per-platform CI gating."
release_description: ""
opus_recommended: true  # reason: cross-cutting design + explicit trade-off/decision task (trial-removal model, new recovery ACs spanning script + process + CI)
writes_requirements: true
requirements_version:
  commit: 804bcfc0
  file: ../requirements.md
---

# Goal: Harden the dependency-retirement usage-check (false-positive reduction + recovery model)

## Objective

The monthly usage-check (`scripts/release/check_dependency_usage.py`, REQ-PROC-061
AC-11) decides which `pubspec.yaml` dependencies are *removal candidates*. Today it
produces a mix of genuine dead weight and structural false positives, and offers no
durable way to recover from a false positive — a "keep" decision is not persisted, so
the same noise resurfaces every month.

This exploration must converge on a coherent design for:
1. **Reducing false positives** at classification time (config-referenced tooling,
   native plugins, matcher gaps).
2. **A durable false-positive recovery path** — so a "keep" decision is made once, with
   recorded justification, not re-litigated monthly.
3. **A test-driven trial-removal model** — remove on a branch, let the test/build/CI
   oracle decide, revert if red — together with an honest account of where that oracle
   is blind (the no-import population it targets, and native deps on platforms with no
   CI lane).

What is NOT yet settled: which of these become new ACs on REQ-PROC-061 vs. pure tooling
changes; the exact shape of the recovery registry; whether trial-removal is gated
strictly on per-target-platform CI coverage or allowed with documented residual risk;
and how the work decomposes into impl tasks.

## Background

`check_dependency_usage.py` was created by the completed task
`2026-06-02_impl_monthly-review-usage-check`. It scans `lib/ test/ integration_test/`
for `import 'package:<name>/'` and buckets each dependency as `directly_imported` /
`indirectly_required` (a hardcoded `INDIRECT_REQUIREMENTS` allowlist) /
`no_evidence_of_use` (= removal candidate). The monthly review writes a proposal under
`automation/dependency_reviews/YYYY-MM/`; the reusable decision task gates actual removal
(developer chooses "approve removal or keep").

A design conversation on 2026-06-03 surfaced concrete false positives and a structural
gap in the recovery path. The full synthesis (with the supporting data) is captured in:
`plans_and_protocols/2026-06-03_01_design.md`.

The user's own framing — especially the trial-removal idea and the native/C++ testing
gap — is preserved verbatim in:
`plans_and_protocols/2026-06-03_00_user_initial_input.md`

Read it as a seed bed, not a spec.

For complete requirements at task creation time:
```
git show 804bcfc0:requirements_tasks/process/AI_rules/ai_tool_management/dependency_lifecycle/requirements.md
```

Current requirements: ../requirements.md

## How to Approach This

Use design thinking — the problem space is already partly mapped in the design doc, but
the trade-offs (esp. trial-removal gating and which items become ACs) are open. Start
from the captured synthesis, validate the findings still hold, then converge on
decisions and a decomposition. Re-run the probe commands in the design doc to confirm the
data has not drifted before proposing changes.

## Seeds

- The removal-candidate list today mixes true positives (`mockito`, `rxdart`,
  `bloc_concurrency`, `google_fonts`, `mutation_test`, `glados`) with structural false
  positives (`very_good_analysis`, `custom_lint`, `clean_architecture_kit` — referenced
  in `analysis_options.yaml`, never imported). How should the classifier tell them apart?
- A "keep" decision evaporates each cycle — there is no ledger the script reads. What is
  the lightest durable recovery path that covers *all* false-positive classes (indirect,
  native, config), not just the one `INDIRECT_REQUIREMENTS` was built for?
- For the no-import population (which is the entire candidate set), removal breaks
  nothing observable — so a green test run is necessary-not-sufficient. When is
  trial-removal trustworthy, and when does it give false confidence?
- Native/C++ deps are only validated by per-platform CI. Today only Windows is fully
  covered (Linux-desktop/macOS/iOS/Android-device are not). Should trial-removal be
  gated on per-target-platform CI coverage (from `.flutter-plugins-dependencies`), and
  what happens to deps targeting uncovered platforms?
- A failed trial-removal *names its own consumer* (the build/link error). Can that
  auto-populate the recovery ledger with the evidence `INDIRECT_REQUIREMENTS` demands?
- Which of the ten captured items are requirement-level (new ACs on REQ-PROC-061) vs.
  pure script changes? How does the rest decompose into impl tasks?

## Execution Model

Gather raw material — re-read the script, the requirement, the process doc
(`doc/process/dependency_lifecycle.md`), and the CI workflows under `.github/workflows/`.
Validate the design doc's findings against current state. Then converge: frame the open
decisions for the user, propose AC changes if needed (this task may write/propose
requirements), and produce an impl decomposition.

The session's model is fixed at launch (Opus, per `opus_recommended: true`).

**Web research**: if needed (e.g. prior art on empirical dependency-elimination or
plugin-usage detection), delegate to a spawned `general-purpose` agent with a focused
question; never run WebSearch inline.

## Output

A decision-ready design: each of the ten items resolved to either a proposed REQ-PROC-061
AC change or a scoped script/tooling change; the recovery model (registry shape) and the
trial-removal model (gating rule + residual-risk stance) settled or framed clearly enough
for the user to decide; and a decomposition into impl tasks. An ADR draft for the
trial-removal recovery model should exist under a `decisions/` folder for the requirement.

## Acceptance Criteria

- [x] Exploration produced at least one synthesis round (validates/updates the captured design) — findings re-validated against current repo state; design doc 01 is the synthesis
- [x] The synthesis resolves each of the ten items to AC-change vs. tooling-change, in terms not fully known at task creation — 3 new ACs (AC-13/14/15); items #2/#4/#5/#6 ruled tooling; #9 review task; #10 doc update
- [x] Decisions requiring user input (trial-removal gating, residual-risk acceptance, which items become ACs) are framed clearly enough to decide — asked via AskUserQuestion; resolved to allow-with-residual-risk + all three ACs
- [x] The output is honest about what remains uncertain (oracle blind spots, uncovered CI platforms) — residual-risk acceptance and native-declaration circular-evidence caveat are recorded in the requirement and ADR

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies (predecessor already completed) |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK (impl_monthly-review-usage-check)](../2026-06-02_impl_monthly-review-usage-check%20(completed)/goal.md) | Predecessor — created `check_dependency_usage.py`; this task hardens it |
| [TASK (explore_reevaluate-analyzer-ceiling)](../2026-06-03_explore_reevaluate-analyzer-ceiling/goal.md) | Adjacent — touches the same packages (clean_architecture_kit/bloc_lint) but for version ceilings, not usage classification |

## Notes

Task type is `explore` (design-capture); implementation will be decomposed into impl
tasks. Items #7 (recovery registry) and #8 (trial-removal model) likely require new
REQ-PROC-061 ACs — route through `requ-explore` before the corresponding impl work.
Any edit to `scripts/release/check_dependency_usage.py` at implementation time must go
through the `claude-write-script` skill (Python gates).
