---
proposal_id: direct-styling-baseline-exemptions
proposal_type: grep_gates
proposed_at: 2026-05-24
proposed_by_model: claude-sonnet-4-6
source_task: TASK-NFUNC-002-02
status: pending_review
---

## Reason

`check_no_direct_styling.sh` reports 14 violations in `lib/features/`.
These are pre-existing hardcoded `TextStyle`, `ButtonStyle`, `Color`, and
`Colors.*` usages written before the gate was introduced. They represent
accumulated styling debt, not regressions from TASK-NFUNC-002-02.

Key violating files:
- `role_selection_form.dart` — `ButtonStyle(`
- `therapist_receive_screen.dart` — multiple `TextStyle(`, `Colors.green`
- `in_person_tab_content.dart` — `TextStyle(`
- `data_beam_tier_selector.dart` — `TextStyle(fontSize: 10)` (×3)
- `data_beam_qr_animator.dart` — `Colors.white`
- `plan_detail_view.dart` — `Colors.grey.shade100` (×4)

Fixing all 14 requires migrating to the design-system token classes
(`AppColors`, `AppTextStyles`, etc.), estimated 1–2 person-days.

## Proposed change

**Option A (preferred):** Create a dedicated styling-migration task and add
currently-violating files to `direct_styling_exclusions.txt` until each file
is migrated. Files are removed from the exclusion list when migrated.

**Option B:** Add only the most egregious violators to the exclusion list
(those with ≥3 violations per file) and fix the rest immediately.

## Expected effects

- Option A: gates pass; no new direct-styling in any file not on the list.
- Option B: partial fix; requires ~0.5 person-day of migration now.

## Alternatives considered

1. **Fix all 14 violations in TASK-NFUNC-002-02** — rejected. Out of scope;
   requires design-system token audit for each migrated style.
2. **Raise the violation threshold** — rejected. The gate should be strict;
   the problem is the pre-existing baseline.
