---
proposal_id: test-smells-closure-scanner-limitation
proposal_type: grep_gates
proposed_at: 2026-05-25
proposed_by_model: claude-sonnet-4-6
source_task: TASK-PROC-046-18
status: pending_review
---

## Reason

`check_test_smells.py` sub-checks 1 (missing assertion) and 2 (empty group)
use `scan_blocks()`, a paren-depth scanner that extracts function bodies. The
scanner finds `test(` then locates the matching close-paren of the outer call
and expects a `{` block to follow immediately after.

In the standard Dart test closure pattern:
```dart
test('name', () {
  // body
});
```

After stripping string literals, the scanner finds `test(`, traces through the
paren depth until the final `)` before `;`, then looks for `{` at the position
after `;` — finding nothing. The closure body inside the argument list is
therefore never extracted. Sub-check 1 (missing assertion) and sub-check 2
(empty group) **never fire** on any idiomatic Dart test.

Only sub-check 3 (literal `expect(...length, N)`) works correctly because it
uses a simple regex over the full file content.

Confirmed in tests: `test_check_test_smells.py` → 3 xfail entries
(test_test_without_assertion_flagged, test_empty_group_flagged,
test_main_returns_1_on_smelly_tests).

## Impact

High: sub-checks 1 and 2 are silently non-functional for all real Dart test
files in this project. The gate reports PASS unconditionally for these
sub-checks, giving false confidence.

## Proposed change

Redesign `scan_blocks()` to extract the closure body passed as an argument
to `test()` / `testWidgets()` / `group()`, rather than looking for a block
after the closing paren.

Concretely: after finding `test(` and stepping through the argument list,
detect the `() {` or `() async {` closure argument and extract the body
between the matching `{}` pair. The existing `find_block_end()` helper can
be reused once the correct opening `{` position is identified.

Alternative (simpler but less accurate): switch sub-checks 1 and 2 to
regex-based scanning over the raw file text, similar to how sub-check 3
works.
