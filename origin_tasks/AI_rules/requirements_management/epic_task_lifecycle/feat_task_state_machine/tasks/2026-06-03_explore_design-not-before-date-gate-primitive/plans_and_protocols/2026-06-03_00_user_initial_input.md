# User initial input (verbatim seed)

Captured 2026-06-03 from a live manual session triaging the TASK-PROC-061-05
pending-feedback escalation.

> should we change strategy and let the upgrade check run locally? check requ. check possibilities

> calendar-trigger as standing task with the 1st of next month set in 'awaits'? think about it

> yes

## Context the seed grew out of (orchestrator notes, not part of the seed)

- The monthly dependency review (REQ-PROC-061 AC-01) runs as a remote Claude Code
  cron routine (`monthly-dep-review`, `0 9 1 * *`). It fires in a cloud container
  that has **no Flutter/Dart SDK**, so it queries the pub.dev API and proposes each
  package's `Latest` version — never a real `flutter pub outdated` solve.
- Consequence: 7 of 16 proposed bump targets in TASK-PROC-061-05 were not
  solver-`Resolvable` under the current constraint graph (analyzer ceiling from
  clean_architecture_kit/bloc_lint, Flutter-SDK `meta` pin, win32/package_info_plus
  caps). The "target" column was never validated against `pub solve`.
- The devcontainer DOES have the SDK (`/sdks/flutter/bin/flutter`), and the local
  autorun orchestrator (`automation/orchestrate.py`) already runs there.
- The developer's instinct: make the monthly check a **standing local task** that
  re-arms itself to a future calendar date — but no date-gate primitive exists.
  `scripts/tasks/next_tasks.py` blocks only on status / non-empty `awaiting` /
  `after:` IDs; there is zero date/`today` logic.

Read the quotes above as a seed bed, not a spec.
