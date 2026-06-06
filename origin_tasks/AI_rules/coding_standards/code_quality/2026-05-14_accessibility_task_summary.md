# Accessibility Commitments Inventory Across Pending Tasks

Source: per-goal.md scan to surface implicit / under-specified accessibility commitments
relative to REQ-PROC-046 AC-07 (which now enforces the full REQ-NFUNC-002 active set).
Date: 2026-05-14.

## Per-Task Paragraphs

### 1. TASK-FUNC-007-12-02 — Client QR Transfer Screen
Path: `requirements_tasks/functional/shared/epic_data_transfer/feat_qr_data_transfer/tasks/2026-04-21_impl_client-qr-transfer-screen/goal.md`.
Frontmatter: `target_package: "QR Transfer Send"`, `status: pending`. Goal explicitly names
**WCAG 2.3.1** (flashing/seizure safety) via the ≤3 Hz frame-timer cap (AC-07/AC-08 cross-reference)
and references the WCAG cap flag from `ClientTransferConfig`. The troubleshooting hint (AC-07) is
required to be visually separated and "neutral in tone" — a soft accessibility commitment but not
phrased against any AC of REQ-NFUNC-002. Not named: semantic labels (AC-09a) for the Discard/Complete
buttons or QR animator, text scaling (AC-11) at 200% on a full-screen QR layout that includes a
slider and progress text, contrast (WCAG AA) for the bottom-anchored banner, focus order, or
screen-reader handling of the live-updating frame counter. Surface is a primary interactive screen,
so all of these plausibly apply. Verdict: **partially covers** (motion only).

### 2. TASK-FUNC-007-12-01 — QR Transfer Foundation (Domain + Data)
Path: `requirements_tasks/functional/shared/epic_data_transfer/feat_qr_data_transfer/tasks/2026-04-21_impl_qr-transfer-foundation/goal.md`.
Frontmatter: `target_package: "QR Transfer Send"`, `status: pending`. Explicitly names the
**WCAG 2.3.1 invariant** (3 Hz cap unconditionally when OS Reduce Motion is active on either device)
through the `wcagCapActive` flag on `ClientTransferConfig`. This is the strongest motion commitment
in the set. Not named — but also less applicable, since this is a Domain/Data-only task with no
widget surface: semantic labels, text scaling, contrast, focus order do not apply. The only
accessibility surface here is motion-safety, and it is covered. Verdict: **fully covers** (given the
layer scope).

### 3. TASK-FUNC-007-01-07 — QR Transfer Screen Detection UX
Path: `requirements_tasks/functional/shared/epic_data_transfer/feat_therapist_transfer_ui/tasks/2026-04-29_impl_qr-transfer-screen-detection-ux/goal.md`.
Frontmatter: `target_package: "QR Transfer Receive"`, `status: in_progress`. Explicitly names
**WCAG 2.3.1** for the success animation (≤3 Hz, no strobing — AC-20) and **OS Reduce Motion**
fallback (AC-19) with a shared `AccessibilityPreferencesService`. Also names a non-shaming notice
(AC-17) — a UX-tone commitment rather than a measurable a11y AC. Not named: semantic labels for the
"Transfer complete" static indicator or the persisted grey-zone notice banner (AC-09a), text scaling
(AC-11) for the notice text, contrast for the static indicator and the persisted notice banner.
Surface includes user-facing notices on a detail screen, so labels/scaling/contrast plausibly apply.
Verdict: **partially covers** (motion + Reduce Motion strong; labels/scaling/contrast absent).

### 4. TASK-FUNC-005-04 — Phase 3 Advanced Features (Plan Evaluation)
Path: `requirements_tasks/functional/shared/epic_evaluation/plan_evaluation_view/tasks/2026-01-04_impl_phase3-advanced-features/goal.md`.
Frontmatter: `target_package: "Plan Data Analysis"`, `status: blocked` (no user flow yet). One
accessibility-adjacent commitment: multi-day comparison uses "distinct line styles for accessibility"
(addresses color-only-distinction / WCAG 1.4.1 in spirit, but no AC reference). Not named: semantic
labels (AC-09a) for tabs, filters, zoom controls, capsules, popouts; text scaling (AC-11) across
a chart-heavy layout with RangeSlider and dropdowns; contrast (WCAG AA) for chart elements,
dashed/pattern reference lines, and Tree/Simple theme variants; keyboard / focus order through
SegmentedButton + dropdown + slider clusters; screen-reader access to chart data points (a known
hard case for `CustomPaint`). Surface is one of the densest interactive screens in the app. Verdict:
**gap**.

### 5. TASK-FUNC-005-05 — PlanEvaluationView meta-task
Path: `requirements_tasks/functional/shared/epic_evaluation/plan_evaluation_view/tasks/2026-01-04_impl_plan-evaluation-view/goal.md`.
Frontmatter: `target_package: "Plan Data Analysis"`, `status: blocked`. Same single
accessibility-adjacent line as Phase 3 ("Multi-day comparison uses distinct line styles for
accessibility"). Acceptance criteria list mentions "Responsive layout for different screen sizes"
which touches text-scaling-adjacent concerns but is not the same commitment. Not named: semantic
labels, text scaling at 200%, WCAG AA contrast, focus management, screen-reader access to
`CustomPaint` chart, accessible mode toggle, accessible date navigator. Given this is the umbrella
task for the entire evaluation feature (15–25 files across all layers), the omission set is broad.
Verdict: **gap**.

### 6. TASK-PROC-046-07 — Inventory screens without widget tests
Path: `requirements_tasks/process/AI_rules/coding_standards/code_quality/tasks/2026-05-10_analyze_inventory-screens-without-widget-tests/goal.md`.
Frontmatter: no `target_package` (process task), `status: pending`. Explicitly names the
**four `AccessibilityGuideline` checks** that REQ-PROC-046 AC-07 enforces (via `tester.ensureSemantics()`):
`androidTapTargetGuideline`, `iOSTapTargetGuideline`, `labeledTapTargetGuideline`,
`textContrastGuideline` (the four-check pattern is the explicit subject). The task itself is a pure
inventory, so the only commitment that applies is to *measure* coverage of those four guidelines.
It does not need to enumerate per-screen labels/scaling/motion — that is the backfill's job. Verdict:
**fully covers** (for the scope of an inventory task).

### 7. TASK-PROC-046-08 — Create widget-test backfill tasks
Path: `requirements_tasks/process/AI_rules/coding_standards/code_quality/tasks/2026-05-10_impl_create-widget-test-backfill-tasks/goal.md`.
Frontmatter: no `target_package` (process task), `status: pending`. Explicitly names the same
four `AccessibilityGuideline` checks as the per-task scope each generated backfill task must assert.
Does not name text scaling (AC-11), motion-safety (AC-20 / WCAG 2.3.1), reduce-motion fallback
(AC-19), or non-tap-target semantic labels beyond what `labeledTapTargetGuideline` covers. Since
REQ-PROC-046 AC-07 now references the *full* REQ-NFUNC-002 active set, a backfill that only
asserts the four built-in `AccessibilityGuideline` checks will not satisfy the full AC — text
scaling, contrast on non-tap elements, reduce-motion handling, and explicit semantic labels on
non-interactive content are not covered by those four built-ins. Verdict: **partially covers**.

## Aggregate Gaps

Across the 7 tasks (4 feature impl tasks, 1 foundation, 2 process):

- **5 of 7** tasks do not mention **semantic labels (AC-09a)** for interactive elements. The two
  exceptions are the two process tasks (-07, -08), which assert `labeledTapTargetGuideline` only —
  a narrower commitment than full AC-09a semantic labels on non-tap targets.
- **6 of 7** tasks do not mention **text scaling (AC-11) at 200%**. Only the QR Foundation task is
  exempt by layer scope.
- **6 of 7** tasks do not mention **WCAG AA contrast (AC-10)** for theme variants or chart elements.
  The QR Foundation task is again exempt by layer.
- **4 of 7** tasks do not mention any **WCAG 2.3.1 / motion-safety** commitment despite three of
  them being presentation-layer screens. The exceptions are the two QR tasks (-12-01, -12-02) and
  the QR Detection UX task (-01-07).
- **5 of 7** tasks do not mention **focus order or screen-reader navigation**. The two process
  tasks address tap-target labelling only.
- **2 of 7** tasks (the Plan Evaluation pair, -005-04 and -005-05) name **zero accessibility ACs**
  from REQ-NFUNC-002 explicitly. They are the largest-surface tasks in the set and are currently
  blocked on a missing user flow, so the gap may be remediated when the flow lands.
- The two **process backfill tasks** themselves cover only the four built-in `AccessibilityGuideline`
  checks. Promoting REQ-PROC-046 AC-07 to enforce the *full* REQ-NFUNC-002 active set means the
  backfill template needs to additionally assert text scaling, non-tap-target semantic labels,
  reduce-motion fallback, and contrast on non-tap-target content — extending each generated test
  beyond `tester.ensureSemantics()`.

The dominant gap is therefore non-motion accessibility (labels on non-tap content, text scaling,
contrast) on user-facing screens, plus the process-task template that does not yet generalise past
the four built-in tap-target/contrast guidelines.
