# Exploration Synthesis — REQ-PROC-046 (LLM Code-Quality Back-Pressure)

Date: 2026-05-15
Agent: claude-opus-4-7 (automated mode, session 22810811-9b32-4fa4-9e0f-742f2c82c444)

## Status

Exploration converged. The user explicitly closed the iteration loop in
`../../2026-05-14_feedback_03.md` with "Bitte fahre also fort. Du hast ja noch
einige Dinge auch zu erledigen." (Please continue. You still have things to do.)
All open questions raised across three feedback rounds were answered or
explicitly deferred. The resulting artefacts are committed and stable.

## Acceptance-Criteria Check (from goal.md)

- [x] **At least one Opus synthesis round.** Three Opus rounds occurred over
      2026-05-13 → 2026-05-14, each captured in
      `../../2026-05-13_feedback_01_questions.md`,
      `../../2026-05-14_feedback_02_questions.md`, and
      `../../2026-05-14_feedback_03_questions.md`. Each round adapted REQ-PROC-046
      and produced fresh decision proposals.
- [x] **Defines the problem space in terms not fully known at task creation.**
      Several discoveries reshaped the requirement that were not anticipated:
      - The Goodhart's-Law failure mode (LLMs optimising one gate while
        degrading another) → drove the "re-run all gates as a set" rule and the
        "LLM may not silently modify the gate set" constraint.
      - DCM (`dart_code_linter`) is no longer OSS-licensed → forced a baseline
        switch to `very_good_analysis` (TASK-PROC-046-03) and the creation of
        six custom replacement scripts (TASK-PROC-046-14).
      - Coverage-as-a-goal anti-pattern + LLM 17 % baseline finding → led to
        AC-04 being targeted (≥ 90 % only on data-loss-catastrophic paths),
        not global.
      - The bidirectional-SPOT problem (requirement-AC vs. script-rule) → led
        to the explicit Developer-Guidelines rule that **neither side alone is
        single point of truth**, with the requirement winning when in conflict.
      - The proposals-loop pattern (permanent task with generic question.md +
        reset script) → resolved the original "review-task cadence" question
        by making the cadence irrelevant; the loop self-regenerates.
- [x] **Decisions requiring user input were identified and framed clearly.**
      Three rounds of `_questions.md` files raised concrete decisions with
      proposed defaults and alternatives. The user resolved all of them in the
      paired `_feedback_NN.md` answer files. Round 3 closed with no open
      questions remaining in the protocol.
- [x] **Honest about what remains uncertain.** See "Open at completion" below.

## Convergence Summary

REQ-PROC-046 (38 KB, status `active`) defines eight gates (G1 source hygiene,
G2 complexity, G3 test correctness & critical-path coverage, G4 architectural
purity, G5 suppression discipline, G6 accessibility, G7 performance budget,
G8 bundle-size budget) with thirteen acceptance criteria grounded in
PERSONA-015 (longevity-over-velocity, distributive equity) and PERSONA-004
(zero data loss, old-hardware reliability). The back-pressure protocol caps
revision cycles at 5 (LLMLOOP/ICSME 2025 finding) and routes escalation
through the project's standard automation Q&A mechanism rather than inventing
a new channel.

Fourteen child implementation tasks were created in
`../tasks/2026-05-1*_*_*/` covering baseline switch, custom replacement
scripts, gate enforcement, widget-test backfill, coverage backfill, frame-budget
integration tests, bundle-size measurement, CLAUDE.md update, accessibility
audit, doc-guideline audit, and the self-perpetuating quality-rule-proposals
loop.

## User-Approved Design Decisions

- **`very_good_analysis` over DCM** (round 3). 188 OSS rules + `bloc_lint` +
  `clean_architecture_kit`. DCM removed entirely; custom scripts under
  `scripts/quality/` fill the resulting gap.
- **Custom complexity script** rather than DCM metrics (round 3). Thresholds
  carried over: cyclomatic ≤ 20, params ≤ 4, SLOC ≤ 50, nesting ≤ 5.
- **Permanent proposals-loop task** rather than per-round review tasks (round
  3). Generic question.md referencing `scripts/quality/proposals/`, reset
  script restores Q/A files after each run.
- **Bidirectional SPOT** (round 3). Requirements and gate scripts read together;
  requirement-wins on conflict.
- **Five-cycle escalation bound** via the standard `automation/pending_feedback/`
  mechanism (round 1). No new escalation channel.
- **Targeted (not global) coverage** on data-loss-catastrophic paths (round 1),
  ≥ 90 % via lcov.
- **Samsung Galaxy A40 as the named reference device** for G7 dynamic
  measurement (round 2). User owns the hardware physically.
- **Tagging proposals with `proposed_by_model:`** but no automatic archival
  logic for now (round 3 — explicitly deferred until guideline files grow large
  enough to warrant it).

## Open at Completion (honest uncertainties)

- **Periodic trigger for the proposals-loop task.** Currently developer-manual;
  pre-release auto-fire deferred. Recorded in `feedback_03_questions.md` §
  Backlog.
- **`doc-update-guidelines` skill `<!-- Captured: -->` marker.** Small skill
  change deferred until a concrete pattern requires it.
- **English readability metric** (A.1 from round 1). Applies only when English
  localisation lands; no work needed yet.
- **Plan-evaluation tasks lack accessibility ACs** because they are blocked on
  a missing user flow. When that flow exists and unblocks them, AC-07 will
  catch them automatically.
- **AC-08 cold-start budget (3 000 ms on A40) is generous** relative to
  PERSONA-004's 2017 baseline. If the A40 measures notably faster, the budget
  may be tightened; this is an upper bound, not a target.

## Pointers

- Requirement: `../../requirements.md` (REQ-PROC-046)
- Feedback / synthesis history: `../../2026-05-1*_feedback_*.md` and `..._questions.md`
- Web research notes: `../../2026-05-13_websearch_more_checks.md`,
  `../../2026-05-14_research_automation_and_self_regen.md`
- Accessibility task summary: `../../2026-05-14_accessibility_task_summary.md`
- Child implementation tasks: `../tasks/2026-05-1*_*_*/goal.md`

## Why this synthesis lives here

Per CLAUDE.md §1 the file-based memory rule requires every agent to write
findings to `plans_and_protocols/` before exiting. The substantive
synthesis history happened in the requirement folder (one level up) rather
than this task's `plans_and_protocols/`, which is unconventional. This
file consolidates the converged state inside the canonical location and
links back. Future sessions reading `goal.md` can follow the pointers from
here without re-reading the full feedback chain.
