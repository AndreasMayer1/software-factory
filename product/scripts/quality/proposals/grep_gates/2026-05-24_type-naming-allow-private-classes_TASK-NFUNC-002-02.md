---
proposal_id: type-naming-allow-private-classes
proposal_type: grep_gates
proposed_at: 2026-05-24
proposed_by_model: claude-sonnet-4-6
source_task: TASK-NFUNC-002-02
status: pending_review
---

## Reason

`check_type_naming.sh` requires every `class` declaration under `lib/` to
match `^[A-Z][a-zA-Z0-9]*...$` — a regex that starts with an uppercase
letter. This flags the standard Flutter convention of private inner classes
(prefixed with `_`), such as `_PlanDetailsFormState`, `_ScannerBody`, etc.

These private classes appear in 22 locations and are idiomatic Flutter: State
subclasses, private helper widgets, private BLoC event types. They are not
a naming violation — they are deliberate encapsulation.

The gate was introduced by TASK-PROC-046-03 to replace DCM's
`prefer-correct-type-name` rule. DCM's original rule also excluded
private classes from the check.

## Proposed change

In `scripts/quality/check_type_naming.sh`, extend the scan to skip class
declarations that begin with `_` (private classes):

```diff
-    while IFS= read -r raw; do
+    while IFS= read -r raw; do
+        # Skip private classes — underscore prefix is standard Flutter convention.
+        class_name="${raw##* class }"
+        class_name="${class_name%%[^A-Za-z0-9_]*}"
+        [[ "$class_name" == _* ]] && continue
```

Or equivalently, filter at the grep level:
```diff
-grep -nE '^\s*class\s+[A-Za-z_][A-Za-z0-9_]*' "$file"
+grep -nE '^\s*class\s+[A-Z][A-Za-z0-9_]*' "$file"
```
(The `[A-Z]` at the start already excludes `_`-prefixed names if the grep
 pattern is anchored correctly — verify against the existing script logic.)

## Expected effects

- 22 current violations removed.
- Future State subclasses, private helper widgets, and private BLoC events
  will no longer be flagged.
- Public class names still enforced (uppercase start, suffix suffix allowlist).

## Alternatives considered

1. **Rename all 22 private classes to public** — rejected. Exposes internals
   that are correctly private; violates Flutter convention and widget-testing
   patterns.
2. **Add each class to an exclusion list** — rejected. Unmaintainable; grows
   with every new private class.
3. **Keep gate as-is, annotate each violation** — rejected. Silencing a
   linter for idiomatic code erodes the gate's signal-to-noise ratio.
