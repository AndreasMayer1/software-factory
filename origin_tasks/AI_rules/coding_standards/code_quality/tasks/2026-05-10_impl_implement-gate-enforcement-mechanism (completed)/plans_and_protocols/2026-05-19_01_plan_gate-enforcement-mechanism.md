# Plan: Implement gate enforcement mechanism

## Approach: inline (single-author multi-file write)

Why not agents: the deliverable is a closed set of skill/agent/settings files
whose shape is fully specified in `goal.md`. No open-ended investigation; no
parallel exploration helpful.

## Layers and target files

| Layer | File | Action |
|-------|------|--------|
| 1 — Aggregate gate runner | `scripts/quality/run_per_change_gates.sh` | NEW — orchestrates per-change gates, exits non-zero on RED |
| 1b — Release-cadence runner | `scripts/quality/run_release_gates.sh`   | NEW — adds bundle-size + determinism |
| 2 — Agent | `.claude/agents/quality-checker.md` | EXTEND — invoke runners, return RED/GREEN with exit code semantics |
| 3 — Skill | `.claude/skills/verify-quality/skill.md` | NEW — five-cycle counter, pending_feedback escalation, clean-tree pre-check |
| 4 — Hooks | `.claude/settings.json` | EXTEND — Stop hook + PreToolUse(Bash:"git commit*") hook |
| 5 — task-complete | `.claude/skills/task-complete/skill.md` | EXTEND — invoke verify-quality before marking complete |
| 6 — INDEX.md | `.claude/skills/INDEX.md` | EXTEND — list verify-quality under task-* / claude-* category |

## Five-cycle counter

- File: `<task-folder>/plans_and_protocols/cycle_state.json`
- Schema: `{ "task_id": "TASK-...", "cycle_count": 0, "last_result": "...",
  "first_red_at": "..." }`
- Reset rules: (a) task transition (new task has its own `plans_and_protocols/`),
  (b) explicit user clear, (c) GREEN result deletes the file.

## Per-change vs release-cadence gates

Per-change (must run on every Stop / pre-commit):
- `flutter analyze` (if Dart changed)
- `flutter test` (if `lib/` or `test/` changed; in automated container mode the
  agent reports test-status only — full Flutter test runs live on the bridge)
- `scripts/quality/check_quality_gates.sh` (the aggregate runner that already
  bundles SP1–SP4, AC11, AC12, complexity, type-naming, arch-imports,
  no-direct-styling, test-smells, folder-taxonomy)
- `scripts/quality/check_critical_path_coverage.py` (G3 critical-path coverage)

Release-cadence (only when invoked with `--release` flag):
- `scripts/release/check_bundle_size.py` (G8)
- `scripts/quality/check_test_determinism.sh` (TQ4)
- Mutation tooling (TQ-MUT), property tests — orchestrated by `release` skill

## Hooks

- `Stop` hook: when the agent finishes and any `lib/`, `test/`, or
  `integration_test/` file was modified during the response → invoke
  `verify-quality` (per-change mode). Hook bypassed when `SKIP_QUALITY_GATES=1`.
- `PreToolUse(Bash:"git commit*")` hook: invoke `verify-quality` and block the
  commit on non-zero exit. Bypass: `SKIP_QUALITY_GATES=1` and only with
  explicit user authorization recorded in the commit message.

## Acceptance-criteria mapping

| AC | Delivered by |
|----|--------------|
| AC-10 wiring of every per-change gate | Layer 1 + Layer 2 |
| Exit-code semantics | Layer 1 + Layer 2 |
| skill exists + five-cycle counter + escalation | Layer 3 |
| CLAUDE.md / INDEX.md references resolve | Layer 6 |
| Stop + commit hooks | Layer 4 |
| task-complete refuses on RED | Layer 5 |
| Bypass mechanism documented | Layer 3 (skill) + Layer 4 (hook code) |
| Smoke test demonstrates full chain | Documented in skill.md as a self-test stanza |
| Counter resets on task transition | Layer 3 (the counter file lives in `plans_and_protocols/`, so a new task starts with a fresh folder) |

## Out of scope (per goal.md)

- Gate-script implementations (sibling tasks).
- New gates beyond REQ-PROC-046 / 052 / 002.
- CI / GitHub Actions integration.
- Caching strategy for unchanged inputs (follow-up).
