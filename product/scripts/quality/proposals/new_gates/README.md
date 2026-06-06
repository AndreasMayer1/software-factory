# `new_gates/` proposals

Use this folder when proposing an entirely new gate that no existing
`scripts/quality/check_*.sh` (or `check_*.py`) covers, and that is not just
a configuration of the analyzer:

- A new architectural constraint (e.g. "no direct DB calls outside repository
  layer").
- A new privacy / security check beyond REQ-PROC-052 SP1–SP6.
- A new test-quality check beyond REQ-PROC-002 TQ1–TQ4.
- A new code-quality check beyond REQ-PROC-046 G1–G8.

The `## Proposed change` body MUST specify:

- The exact script path the gate will live under (`scripts/quality/check_<name>.sh`
  or `.py`).
- The CI hook-up: per-change vs per-release-candidate cadence.
- The matching requirement (existing AC or new AC) and a draft AC text.

Brand-new gates require updating the relevant requirement document — the
proposal file should call this out explicitly so the user sees the full
scope before accepting.

Not for this folder:
- A modification to an existing gate → `grep_gates/`.
- A numeric tweak to an existing threshold → `thresholds/`.
- An analyzer-config change → `analysis_options/`.

See the parent `README.md` for the proposal-file format.
