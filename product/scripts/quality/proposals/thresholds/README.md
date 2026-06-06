# `thresholds/` proposals

Use this folder for proposed numeric-bound changes — tightenings or
loosenings:

- Complexity bounds (cyclomatic ≤ 20, params ≤ 4, SLOC ≤ 50, nesting ≤ 5).
- Coverage % thresholds (G3 critical-path ≥ 90 %, TQ2 mutation kill ≥ 80 %).
- Cold-start performance budget (currently 7 500 ms on Galaxy A40).
- Frame-build budget (currently 16 ms avg / 0 missed frames).
- Bundle-size budgets (APK ≤ 30 MB, AAB ≤ 50 MB).
- Five-cycle back-pressure bound itself (REQ-PROC-046 AC-10).

The `## Reason` body MUST include data backing the new value: measured
percentiles, historical violation counts, or a citation to a published
finding. A threshold proposal without numbers will be rejected.

Not for this folder:
- Adding a brand-new gate that introduces a brand-new threshold → file in
  `new_gates/` instead and call out the threshold inside the body.

See the parent `README.md` for the proposal-file format.
