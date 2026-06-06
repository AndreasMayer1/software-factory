---
proposal_id: complexity-baseline-exemptions
proposal_type: thresholds
proposed_at: 2026-05-24
proposed_by_model: claude-sonnet-4-6
source_task: TASK-NFUNC-002-02
status: pending_review
---

## Reason

`check_complexity.py` reports 99 violations across `lib/`. These are
pre-existing functions that were written before the complexity gate was
introduced by TASK-PROC-046-03. The violations span multiple features and
represent accumulated technical debt, not regressions introduced by
TASK-NFUNC-002-02.

Notable examples from the gate output:
- `role_selection_form.dart:23 build: sloc 62 exceeds 50`
- `onboarding_screen.dart:28 build: sloc 76 exceeds 50`
- `therapist_receive_bloc.dart:36 _onChunkScanned: sloc 115 exceeds 50`
- `TherapistReceiveScanning: parameters 8 exceeds 4`

Fixing all 99 violations would require a dedicated refactoring task
(estimated 3–5 person-days). Blocking all other tasks on this baseline
is counterproductive.

## Proposed change

**Option A (preferred):** Create a dedicated task (e.g.
`TASK-PROC-046-NN_impl_complexity-baseline-remediation`) and add the
99 currently-violating functions to a `complexity_baseline_exclusions.txt`
allowlist that `check_complexity.py` reads. New functions added after today
are NOT on this list and ARE fully gated. Functions are removed from the
allowlist as they are refactored.

**Option B:** Raise SLOC threshold from 50 to 80 temporarily while the
refactoring task runs.

**Option C:** Accept current baseline as technical debt, do not change the
gate. All future functions must comply; fix existing violations opportunistically.

## Expected effects

- Option A: gates pass for existing code; new code is still gated.
- Option B: gates pass but allows future functions up to 80 SLOC.
- Option C: gates remain RED until all 99 violations are fixed.

## Alternatives considered

1. **Fix all 99 violations in TASK-NFUNC-002-02** — rejected. Scope creep;
   TASK-NFUNC-002-02 is an accessibility backfill task, not a complexity
   reduction task.
2. **Disable the complexity gate** — rejected. The gate has value for new
   code; the problem is the pre-existing baseline, not the gate itself.
