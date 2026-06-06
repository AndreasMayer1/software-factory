# Plan: Data-Entry Frame-Budget Integration Test (TASK-PROC-046-10)

**Author**: architecture-advisor
**Date**: 2026-05-18
**Skill**: code-complex
**Status**: awaiting user approval

---

## 1. Summary

This task sets up the G7-dynamic frame-budget gate for the primary data-entry
surface (`ClientDataInputRootScreen`, route `/client/data-input`). It introduces
a new `integration_test/perf/` folder containing a `flutter drive`-only
integration test that wraps a representative interaction sequence in
`IntegrationTestWidgetsFlutterBinding.traceAction()` and asserts
`average_frame_build_time_millis ≤ 16` and `missed_frame_build_budget_count == 0`.

Because this session is in automated mode (`CLAUDE_AUTOMATED_MODE=1`) and has no
physical Galaxy A40 attached, the work is split into two phases. Phase 1 (this
session) produces the test source, the documentation, and a run-runbook —
everything that is offline-authorable. Phase 2 (deferred, requires the developer
on the Windows host with the A40 connected) is the baseline run, archive of
timeline JSONs, and any remediation if the baseline fails.

Phase 2 is surfaced via a dedicated follow-up impl task (Option b below) rather
than via `automation/pending_feedback/`, because the work is itself a physical
device run that may need its own iterations (baseline → archive → optional
remediation task) and is naturally a separate unit of work.

---

## 2. Phase 1 vs Phase 2 ACs

The task's `goal.md` lists 6 acceptance criteria. Their phase assignment:

| AC | Description | Phase | Justification |
|----|-------------|-------|---------------|
| AC-G1 | Integration test file exists under `integration_test/perf/` and is runnable via `flutter drive` | **Phase 1** | Code authorship; verifiable by `dart analyze` |
| AC-G2 | Test wraps a representative data-entry interaction in `traceAction()` | **Phase 1** | Source-level property |
| AC-G3 | Test asserts ≤ 16 ms average and 0 missed budget events | **Phase 1** | Source-level property (the JSON-parse + assert block) |
| AC-G4 | Baseline run on the physical A40 is recorded; raw timeline JSONs archived in `plans_and_protocols/` | **Phase 2** | Requires A40 hardware |
| AC-G5 | `doc/testing/` documents the run command, expected outputs, failure interpretation | **Phase 1** | Documentation |
| AC-G6 | If baseline fails, remediation task is created | **Phase 2** | Conditional on Phase-2 outcome |

**Phase-1 close condition** (this task closes): AC-G1, AC-G2, AC-G3, AC-G5
satisfied; the follow-up Phase-2 task created and linked.

**Phase-2 close condition** (the follow-up task closes): AC-G4 done; AC-G6
handled (either no remediation needed, or remediation task created).

This is consistent with the project pattern where physical-device measurement is
its own task (cf. the completed `analyze_calibrate-cold-start-galaxy-a40` sibling
under the same parent requirement).

---

## 3. File-by-File Plan

Total files affected: **5**. Within `code-complex`'s 4-file soft cap +1 for the
documentation that is mandatory and unavoidable. See §9 for the gate
justification.

### 3.1 `integration_test/perf/data_entry_frame_budget_test.dart` (new)

The integration test itself. Structure:

- `main()` calls `IntegrationTestWidgetsFlutterBinding.ensureInitialized()` and
  casts the binding to `IntegrationTestWidgetsFlutterBinding` so
  `traceAction()` is callable.
- A single `testWidgets('data-entry frame budget — Daily Questions',
  (tester) async { … })`.
- Inside the test:
  1. Pump `MyApp` with `locale: Locale('en')` (per `doc/testing/integration_testing.md`
     "Set Explicit Locale" rule).
  2. Drive the app to `/client/data-input`. The simplest reliable path: in
     `setUp`, stub `GetStoredRoleUseCase` to return `AppRole.client()` and let the
     existing `app_router` redirect logic land on `/client/data-input`. This
     mirrors the suite's existing pattern (`integration_suite_test.dart` lines
     159–183) but inverts the stubbed role.
  3. `await tester.pumpAndSettle()` so the questions ListView is fully rendered
     *before* the trace starts. The trace must measure interaction, not initial
     load (initial load is owned by AC-08 cold-start, not the frame-budget
     portion).
  4. Call `await binding.traceAction(() async { ...interaction sequence... },
     reportKey: 'client_data_input_frame_budget')`. See §4 for the interaction
     sequence rationale.
  5. After `traceAction` returns, read the produced summary JSON. The path
     follows the framework convention:
     `build/integration_response_data/client_data_input_frame_budget.timeline_summary.json`
     — but `traceAction` returns a `Map<String, dynamic>` directly via
     `binding.reportData`, so the test parses
     `binding.reportData!['client_data_input_frame_budget']`. Asserting on the
     in-memory map (not the file) avoids file-IO timing flakes.
  6. Two `expect()` calls:
     - `average_frame_build_time_millis <= 16.0`
     - `missed_frame_build_budget_count == 0`

**WHY comments needed** (`///` per CLAUDE.md §5):
- **At the test-level docstring**: why this surface (data-entry, not therapist
  screens) — pointer to PERSONA-015 + AC-08; why this `reportKey`
  (`client_data_input_frame_budget` matches the route slug + the metric name).
- **Inline, above the interaction sequence**: why this sequence (taps + scroll
  rather than typing), justified against §4.
- **Inline, above the assertions**: why 16 ms / 0 missed (pointer to §5).
- **Inline, above `pumpAndSettle()` before `traceAction`**: why settle first
  (excluding cold-start from the frame-budget measurement, which is AC-08's
  cold-start half).

### 3.2 `integration_test/perf/README.md` (new)

A short (~40 line) runbook scoped to the `perf/` folder. Sections:

- What this folder is (`flutter drive`-only perf tests; NOT included in the
  normal `flutter test integration_test` suite).
- How to run the data-entry test on the A40:
  ```
  flutter drive \
    --driver=test_driver/integration_test.dart \
    --target=integration_test/perf/data_entry_frame_budget_test.dart \
    --profile \
    -d <a40-device-id>
  ```
- Where the timeline JSONs land (`build/integration_response_data/*.json`).
- What "pass" looks like (test exits 0; the assertions on the summary fields
  succeed).
- What "fail" looks like and pointer to the doc/testing/ doc for interpretation.

**WHY**: README in `integration_test/perf/` exists because this is a
non-obvious convention — `flutter drive` is a different runner from
`flutter test`, and the folder is intentionally excluded from
`integration_suite_test.dart`. Without the README, the next contributor will
try to add this folder to the suite and break it.

### 3.3 `test_driver/integration_test.dart` (new — only if not already present)

The standard `flutter drive` driver shim. One-liner that imports
`integration_test_driver.dart` and calls `integrationDriver()`. **Open
question**: verify whether `test_driver/integration_test.dart` already exists
in the repo — if it does, do not touch it; if it doesn't, create it (10 lines).
Implementation engineer must check on first action.

### 3.4 `doc/testing/frame_budget_measurement_methodology.md` (new)

Sibling of `doc/testing/cold_start_measurement_methodology.md` — same structure,
different gate. Sections:

- **Purpose**: defines the reproducible procedure for measuring data-entry
  frame budget on the A40 and the gate criteria for G7's dynamic frame-budget
  surface.
- **Reference device**: pointer to `cold_start_measurement_methodology.md` for
  the A40 spec (do not duplicate).
- **Measurement setup**: device prep (same checklist as cold-start: charger,
  airplane mode, screen on, force-stop the app); build command (`flutter drive
  … --profile`).
- **Per-run execution**: the `flutter drive` command line.
- **Capturing the result**: parsing the summary JSON; how the test self-asserts
  but the raw timeline file is still archived for evidence.
- **Minimum run count for baseline**: 3 runs (frame budget is more reproducible
  than cold start since the test sequence is deterministic; cold-start needed
  10 because of JIT/cache variance, which is not in play here).
- **Threshold rationale**: link to §5 below. The thresholds (16 ms, 0 missed)
  are *not* calibrated from measurements like cold-start — they are physical
  upper bounds (60 fps frame budget) and a hard zero (no jank is the bar).
- **Gate check (G7 — dynamic, frame-budget half)**: pass = test exits 0 on
  the A40 in profile mode.
- **When to re-run**: same triggers as cold-start (Flutter SDK upgrade,
  data-entry surface change, device replacement).
- **Interaction with REQ-PROC-002 AC-04**: see §6 of this plan.

**WHY** (inline `(reason)` per skill convention, since `doc/` is not Dart
code): pointers inline to PERSONA-015's "fragile-state quick entries" framing
and to REQ-PROC-046 Example 5.

### 3.5 `doc/testing/README.md` (modify)

Add one row to the table:

| `frame_budget_measurement_methodology.md` | G7 dynamic frame-budget gate — A40 setup, thresholds, run command | Running or interpreting the frame-budget gate; adding a new perf integration test |

No other changes.

---

## 4. Interaction Sequence to Trace

The screen is `ClientDataInputRootScreen` → `DataInputView`, which renders a
`ListView.builder` of `QuestionCard`s. Each card has a `LikertInput`
(`DSLikertScale` from the design system) plus Skip / Confirm `TextButton`s.

**Persona alignment** (PERSONA-015 "fragile-state quick entries"): the user's
real interaction is selecting a Likert value on a card and confirming. Typing
is *not* the dominant input pattern on this screen — there is no `TextField` in
the current implementation (`question_card.dart` + `likert_input.dart` confirm).
The goal.md's hypothetical "type into a text field" step does not apply to the
current surface; the plan substitutes Likert-tap + Confirm-tap.

**Chosen sequence** (inside `traceAction`):

1. `tester.tap(find.byKey(ValueKey('likert_<question_id>')).first)` — tapping
   into the first card's Likert scale. (The widget tree currently sets the key
   `'likert_<id>'` in `data_input_detail_view.dart`.)
2. `await tester.pump()` — one frame to register the BLoC event
   (`SubmitAnswerEvent`) and rebuild the card with `isConfirmEnabled: true`.
3. `tester.tap(find.text(l10n.confirmButton).first)` — tapping Confirm.
4. `await tester.pump()` — register the second `SubmitAnswerEvent`.
5. Scroll the list down by ~200 px to exercise list-rebuild cost
   (`tester.drag(find.byType(ListView), const Offset(0, -200))`).
6. `await tester.pump()` — let the scroll settle.
7. Repeat steps 1–4 on the **second** card (different `ValueKey`) so the trace
   captures more than a single rebuild.

**Why this sequence**:
- Covers the three frame-cost classes on this screen: BLoC-driven rebuild
  (Likert tap → state change), button state transition (Confirm enable/disable),
  ListView scroll. Each is a frame-budget risk.
- Avoids `pumpAndSettle()` *inside* `traceAction` — `pumpAndSettle` waits for
  *all* frames to be quiet, which would mask a single jank frame. Discrete
  `pump()` calls let `traceAction` see each frame.
- Deterministic: no random IDs, no time-dependent assertions, no real-clock
  waits. The same sequence runs identically every invocation.
- Bounded duration (~7–10 frames at 60 fps ≈ 150 ms) — small enough that the
  test is fast on a release-candidate gate, large enough that a single
  jank-frame regression shows up in `missed_frame_build_budget_count`.

**Risk**: question IDs are not currently known statically. The questions come
from the BLoC's `LoadQuestionsEvent` handler. The test will need to await the
`DataInputState.questions` list being non-empty before tapping — implementation
engineer should `pumpUntil` the first `QuestionCard` is findable before starting
`traceAction`. Recorded as an implementation note, not an architectural
problem.

---

## 5. Threshold Rationale

| Metric | Threshold | Justification |
|--------|-----------|---------------|
| `average_frame_build_time_millis` | ≤ 16.0 | 60 fps = 16.67 ms per frame. The A40 display is 60 Hz (Super AMOLED, confirmed in `cold_start_measurement_methodology.md`). Average ≤ 16 ms is the Flutter-canonical frame budget; exceeding it means the average frame missed the next vsync. |
| `missed_frame_build_budget_count` | == 0 | A single dropped frame on the data-entry screen, in PERSONA-015's "fragile-state quick entry" context, is the regression we are gating. Allowing N > 0 here would mean accepting jank that the persona explicitly names as the value at stake. Note: this is per the *measured action*, which is a deterministic ~10-frame interaction, not the entire app lifetime — the 0 is therefore a realistic bar, not a perfection-or-bust trap. |

These thresholds are **physical bounds** (60 Hz refresh rate), not calibrated
from measurement runs. This is a different shape from the cold-start threshold,
which *was* calibrated against the A40 because cold start has irreducible
variance from JIT / cache / OS scheduler. Frame-build during a deterministic
interaction has no equivalent source of variance — if the A40 cannot do 16 ms
on this sequence, the data-entry surface has a real performance problem and
the gate failing is the correct outcome.

If Phase 2 reveals that the A40 *cannot* hit 16 ms even on a healthy build —
i.e. the baseline run fails — the goal.md is explicit: do **not** silently
relax the threshold. Create a remediation task; surface the offending widget
via the timeline JSON in DevTools.

---

## 6. Test-Determinism Gate Handling (REQ-PROC-002 TQ4 / AC-04)

**The question**: REQ-PROC-002 TQ4 (10 consecutive runs, no flakes) is a
release-candidate gate. Does the new perf test risk flapping it?

**Analysis**:

- TQ4 is executed by `flutter test --test-randomize-ordering-seed=random`. This
  runner discovers `*_test.dart` files under `test/` and `integration_test/`
  **based on the import-tree of the entry point being run**, not by folder
  walk. `integration_test/integration_suite_test.dart` (the current suite) does
  not import `integration_test/perf/data_entry_frame_budget_test.dart`, so the
  perf test is **not** part of any `flutter test`-based run.
- The perf test only runs under `flutter drive` against the A40 (or an A40
  emulator). `flutter drive` is invoked separately and is not part of the TQ4
  determinism cycle.
- Conclusion: **TQ4 is not affected by this task**. No exclusion config needed;
  the natural runner separation already handles it.

**Defensive note added to `doc/testing/frame_budget_measurement_methodology.md`**:
the perf test must remain outside `integration_suite_test.dart`'s import graph.
A future contributor adding the perf test to the suite would break this
isolation; the README in `integration_test/perf/` calls this out explicitly.

**Cross-pollination check** with `scripts/integration_test_runner/run_individual_integration_tests.ps1`:
that script uses a manual test-name array (per `integration_testing.md`
"Maintain Individual Runner Script"). The perf test name should **not** be
added to that array — it's not a `flutter test` test. Phase 1 documentation
explicitly states this.

---

## 7. Phase 2 Mechanism (Option Choice)

**Chosen: Option (b)** — create a follow-up impl task scoped to "Phase 2 — A40
baseline run and archive for TASK-PROC-046-10".

**Why (b) over (a)** — `automation/pending_feedback/`:

1. **The sibling task pattern**: the cold-start calibration sibling
   (`2026-05-10_analyze_calibrate-cold-start-galaxy-a40 (completed)`) was its
   own analyze-type task, separate from any "set up cold-start gate" task. The
   pattern in this requirement family is one task per device-bound unit of
   work, not pause-on-feedback inside a single task.
2. **`pending_feedback/` is for decisions, not actions**: the actual examples
   in `automation/pending_feedback/` (TASK-PROC-006-02, TASK-PROC-027-01) are
   the developer answering open questions in free-form text — not running a
   command on a physical device and pasting JSON. The `answer.md` mechanism is
   not designed to receive ~200 KB of timeline JSON as the resume prompt.
3. **Phase 2 may need its own iteration**: if the baseline fails, Phase 2 spawns
   a remediation task. That's a natural unit-of-work boundary; trying to do all
   of it in a single resumed session is awkward.
4. **`awaiting:` on this task would be unbounded**: Option (a) effectively
   leaves TASK-PROC-046-10 open with `awaiting: ["physical A40 run by
   developer"]` for an unknown duration. The task should close once its Phase-1
   ACs are met; the dependency on the device is then visible as a separate
   queued task, not as an indefinitely-open one.

**Mechanics**: at the end of Phase 1, the implementation engineer invokes
`task-create-code` (the goal is "real code work" — running on a device,
archiving JSONs, possibly fixing perf code) with:

- Name: `2026-05-18_impl_a40-baseline-run-for-data-entry-frame-budget`
- Parent requirement: REQ-PROC-046
- `covers.acceptance_criteria: [AC-08]` (frame-budget portion)
- `after: [TASK-PROC-046-10]` — this task must complete first
- Scope: run the test on the A40, archive `*.timeline.json` + `*_summary.json`
  in this Phase-1 task's `plans_and_protocols/` (cross-task archive is fine —
  the cold-start sibling did the same), record measured numbers in the
  follow-up task's `plans_and_protocols/`, create a remediation task if the
  gate fails.
- `awaiting: ["physical A40 attached on Windows host"]` — this is the natural
  block; visible in `top_blocked_task.py` output.
- `opus_recommended: false` — pure execution, not architectural reasoning.

The follow-up task ID is allocated by `task-create-code`; the implementation
engineer records it back into this plan's protocol when created.

---

## 8. Open Questions

1. **`test_driver/integration_test.dart` existence**: §3.3. Implementation
   engineer must check whether this driver shim already exists. If yes, do not
   touch; if no, create. Trivial either way.
2. **First `QuestionCard` key**: §4 assumes the first Likert key is
   `ValueKey('likert_<id>')` where `<id>` is the question's domain ID. The
   plan's interaction sequence uses `.first` rather than a specific ID — this
   works because the BLoC loads a deterministic list. If a future change makes
   the question list non-deterministic, the test must be updated.
3. **DE locale**: the screen's AppBar title is hardcoded `'Daily Questions'`
   (English literal, not localized in current code — see `data_input_detail_view.dart`
   line 47). The interaction uses `find.text(l10n.confirmButton)`. Locale is
   set to `'en'` per the integration-testing guideline. No conflict, but worth
   noting that this screen has incomplete localization — *not* in this task's
   scope, but a `// TODO` or noted in the follow-up task is reasonable.
4. **Canon alignment for `reportKey`**: the concept canon
   (`requirements_user_needs/concept_canon/concept_canon.yaml`) has no concept
   for "Daily Questions" or "data input" as of 2026-05-18. The chosen
   `reportKey` `client_data_input_frame_budget` is therefore code-level (matches
   the route slug and lib path), not canon-derived. If a `CONCEPT-DATA-INPUT`
   or `CONCEPT-DAILY-QUESTIONS` concept is added later by REQ-PROC-049 work,
   the `reportKey` may want to be revisited for canon alignment — but it is
   *not* a user-facing string so the `check_canon.py` audit will not flag it
   today. No blocker.

---

## 9. Estimated File Count and Complexity

**Files affected: 5** (4 new + 1 modified):
1. `integration_test/perf/data_entry_frame_budget_test.dart` (new, ~120 lines)
2. `integration_test/perf/README.md` (new, ~40 lines)
3. `test_driver/integration_test.dart` (new only if absent, ~10 lines)
4. `doc/testing/frame_budget_measurement_methodology.md` (new, ~80 lines)
5. `doc/testing/README.md` (modified, +1 row)

**Plan-size-gate justification**: `code-complex` has a soft cap at 4 files. This
plan exceeds it by one because:
- The doc index update (file 5) is a one-line change paired structurally with
  file 4 — they cannot be split into a separate task without losing the
  discoverability link.
- File 3 may not even be created (depends on existing repo state).

The plan's real footprint is **the test file + one new doc file + a tiny
README**. This is within `code-complex`'s intent. Splitting is not warranted.

**Complexity classification**: Medium. The test source is straightforward
(~120 lines of well-bounded Flutter integration test code); the
documentation is sibling-structure to an existing doc; the only architectural
decision is the Phase-1/Phase-2 split, which this plan resolves.

**Estimated implementation time**: 2–3 hours for Phase 1.

---

## 10. Risks

| Risk | Mitigation |
|------|------------|
| The interaction sequence (§4) misses a real frame-budget hot path | Phase 2 baseline will reveal this; if the run is "too easy" (all metrics near 0), expand the sequence in a follow-up. |
| `traceAction` API surface changes between Flutter SDK versions | Pin the assertion to documented field names; add a WHY comment naming the Flutter version the field names were valid in. |
| First `QuestionCard` not rendered when `traceAction` starts (BLoC still loading) | `pumpUntil` a `QuestionCard` finder is non-empty *before* `traceAction`. Implementation engineer must include this. |
| The perf test is accidentally added to `integration_suite_test.dart` later | README in `integration_test/perf/` explicitly forbids it; `doc/testing/frame_budget_measurement_methodology.md` repeats the warning. |
| Phase 2 never happens (developer forgets) | The follow-up task in the queue with `awaiting: ["physical A40 attached on Windows host"]` is surfaced by `top_blocked_task.py`; the session-start blocked-task notification reminds the developer. |

---

## 11. Approval Checklist (for the user)

Before implementation engineer starts:

- [ ] Confirm Option (b) is the right Phase-2 mechanism (vs. Option (a)
      `pending_feedback`).
- [ ] Confirm the interaction sequence (§4) is representative of the
      persona's real usage. *(If "users will type free-text entries here in 0.0.2",
      the interaction needs expansion now; if "Likert-only is v1 reality",
      the current sequence is correct.)*
- [ ] Confirm the thresholds (§5) — 16 ms / 0 missed — are the project's
      desired bar, not a relaxed variant.
- [ ] Confirm file count (5) is acceptable given the soft-cap justification.

After approval, implementation engineer proceeds to write the test, create the
docs, and queue the Phase-2 follow-up task.

---

**Follow-up task**: TASK-PROC-046-15 created 2026-05-18
Path: `requirements_tasks/process/AI_rules/coding_standards/code_quality/tasks/2026-05-18_impl_a40-baseline-run-for-data-entry-frame-budget/`
