# `grep_gates/` proposals

Use this folder for proposed changes to existing custom gate scripts
under `scripts/quality/check_*.sh` (or their Python equivalents):

- Adding a new forbidden pattern to an existing check.
- Refining a regex that produces false positives.
- Adding a justification mechanism to an existing rule.
- Removing a pattern that has become obsolete.
- Adjusting an exclusion list (`exclusions.txt` or a per-gate allowlist).

Not for this folder:
- Numeric threshold tightening / loosening → `thresholds/`.
- A wholly new gate (no existing script) → `new_gates/`.
- Pure analyzer-config changes → `analysis_options/`.

See the parent `README.md` for the proposal-file format.
