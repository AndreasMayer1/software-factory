# `analysis_options/` proposals

Use this folder for proposed changes to `analysis_options.yaml`:

- Enabling or disabling a specific lint rule.
- Changing a rule's severity (`info` / `warning` / `error`).
- Adjusting `analyzer.errors:` per-rule overrides.
- Adding or removing entries from `analyzer.exclude:`.
- Adopting or dropping a lint-set dependency (e.g. `very_good_analysis`,
  `bloc_lint`, `clean_architecture_kit`).

Not for this folder:
- Custom non-analyzer scripts → `grep_gates/`.
- Numeric thresholds (complexity ≤ 20, etc.) → `thresholds/`.
- Brand-new gates that do not yet have a `check_*.sh` → `new_gates/`.

See the parent `README.md` for the proposal-file format.
