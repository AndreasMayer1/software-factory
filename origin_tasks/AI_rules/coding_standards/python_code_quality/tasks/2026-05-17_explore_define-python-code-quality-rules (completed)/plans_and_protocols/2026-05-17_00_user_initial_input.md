# User's Initial Input (verbatim)

> do you think we should split it in multiple files? do you think more/better patterns should be used? currently we only have rules for dart files, cause this is a flutter app. but the orchestartor seems to become a project on its own... do you think we also define rules for python code quality?

> [after agent proposed an explore task]: yes

> maybe we need to update the reuqirements too...

## Context the user provided in the conversation thread

The request emerged from a long pairing session on the autorun orchestrator. During that session we:

- Diagnosed a "system idle-resleep after scheduled wake" bug on Windows and added a `SetThreadExecutionState` babysitter loop to `scripts/windows/sleep_when_autorun_done.ps1`.
- Found and fixed a `session_id`-loss bug in `scripts/automation/orchestrate.py` (the orchestrator launched recovery sessions without writing the new UUID to `goal.md`, so subsequent iterations misclassified the orchestrator's own session as "manual").
- Refactored: introduced `register_session_in_goal` helper, `active_session` context manager, `mark_exhausted` method on RunData (consolidating two parallel tracker sets), `PromoteResult` enum (replacing bool return from `_promote_task_to_opus_for_context_limit`), `make_session_record` factory (centralizing the common fields of session records).
- Changed the `--max-tasks` accounting policy so errors no longer count (only successful sessions consume a slot).
- Threaded `now_utc` through `next_available_account` so tests on frozen clocks don't drift against real wall-clock.

The user then asked whether the orchestrator should be split into multiple files and whether Python code quality rules should be defined. We discussed both. They chose to scope the present task to the rules first; the split is a separate downstream task that should consume these rules.

Then the user wondered whether the existing requirements should be updated too — pointing at REQ-PROC-046 (currently Dart-only but with no explicit language scope), and possibly the broader `coding_standards/` directory organization.

## Read as a seed bed, not a spec

These messages capture intent and the raw thinking — they are NOT the requirement. The exploration's job is to decide:

- What should "Python code quality" actually cover for this repo?
- How should the rules be organized relative to the existing Dart-scoped REQ-PROC-046?
- Should REQ-PROC-046 be clarified, restructured, or left alone?
- What goes into `doc/python/` (if anything)?
- Which patterns already in use in `scripts/automation/orchestrate.py` deserve to be elevated to project canon?
