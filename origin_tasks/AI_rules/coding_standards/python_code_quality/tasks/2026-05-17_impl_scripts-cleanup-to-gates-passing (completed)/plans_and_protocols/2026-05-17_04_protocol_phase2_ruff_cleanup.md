# Phase 2 protocol — G1 ruff lint cleanup

**Agent ID**: agent-a409789e698d45c3e
**Date**: 2026-05-17
**Scope**: TASK-PROC-051-04 Phase 2 — bring `uv run bash scripts/quality/ruff_check.sh` to a clean pass.
**Exit state**: `All checks passed!` · `pytest scripts/tests/ scripts/automation/tests/ -q` → **541 passed, 0 failed**.

## Baseline (captured before any edits this session)

`uv run bash scripts/quality/ruff_check.sh 2>&1 | tail -3`
→ **975 errors**, 147 fixable, 643 hidden-unsafe fixes.
(Slightly lower than the 981 noted in the original plan — Phase 1 YAML migration deleted ~120 lines of hand-rolled parsing code in 21 files, which incidentally removed a handful of pre-existing lint findings.)

## Pass 1 — safe `--fix`

`uv run ruff check --fix scripts/`
→ 977 errors detected, **151 auto-fixed**, 826 remaining.
Tests after Pass 1: **541 passed**.

Rule families resolved in Pass 1: I001 (isort), F401 (unused-import — initial pass), and assorted style auto-fixables.

## Pass 2 — selective `--unsafe-fixes`

Reviewed `uv run ruff check --diff --unsafe-fixes scripts/` (~3 500 lines of diff). Key finding:
**F841 unsafe-fix is dangerous in this codebase.** Ruff "fixes" a real-bug pattern (`item_indent = indent + 2` where `item_indent` is dead) by deleting the LHS only, leaving the bare expression `indent + 2` as a no-op statement. That keeps the dead computation in code instead of removing it. Skipped F841 from the unsafe-fix batch.

Applied selectively:

```
uv run ruff check --fix --unsafe-fixes \
  --select UP006,RUF059,RUF015,RUF005,C408,C401,B007,RET504,SIM222,RUF013,E731 \
  scripts/
```
→ **620 fixed**, 273 remaining.
Tests after Pass 2: **541 passed**.

Rule families resolved in Pass 2: UP006 (569 PEP-585 annotations `List`→`list`), RUF059 (unused unpacked vars), RUF015 (`next(iter(...))` over `list(...)[0]`), RUF005 (collection literal concat), C408/C401 (unnecessary collection calls), B007 (unused loop var), RET504 (unnecessary assign-before-return), SIM222 (`expr or True`), RUF013 (implicit Optional), E731 (lambda-assignment). All of those left tests at 541 pass.

Second pass-1-style `--fix` invocation then removed 69 F401 unused-imports surfaced by the unsafe-fix typing rewrites → **204 errors remaining**.

## Pass 3 — triage of remaining findings

Worked through the remaining ~200 findings rule-family-by-rule-family. Final state: **All checks passed!**

### Fixes (no suppression)

- **F841 unused-variable** — manually inspected 11 sites; all were genuinely dead. Removed assignments in:
  `scripts/artifacts/generate_user_needs_status.py` (`epic_ids`, `category_id`),
  `scripts/automation/tests/test_orchestrate.py` (`call_count`),
  `scripts/release/release_readiness.py` (`terminal_statuses`, `task_package`),
  `scripts/requirements/coverage_report.py` (`status`, `icon`),
  `scripts/requirements/sync_task_packages.py` (3× `item_indent` — never read after assignment in any of the IN_COVERS/IN_AC/IN_SEC state-machine branches),
  `scripts/task_ordering/simulate.py` (`task_by_id`),
  `scripts/tasks/parse_task_creation_plan.py` (`in_code_fence`, `fence_marker` — left over from an earlier code-fence-handling refactor),
  `scripts/tests/test_doc_governance.py` (`goal_path`),
  `scripts/tests/test_top_blocked_task.py` (`ids`),
  `scripts/tests/test_update_doc_references.py` (`written`, `claude_md_path`),
  `scripts/user_needs/generate_flow_scribble_index.py` (`rel`).
  One remaining F841 in `scripts/tests/test_yaml_frontmatter.py:169` was the "captured for reference" `real_rename` in a crash-mid-rename test; renamed to `_real_rename` so the underscore-prefix convention silences the rule without losing the intent.
- **F811 redefined-while-unused** — `scripts/artifacts/generate_id_registry.py` had two `scan_vtr_records` definitions (line 163 old single-pass version, line 545 new parallel-grep version). Removed the older shadowed definition entirely (dead).
- **F402 import-shadowed-by-loop-var** — `scripts/requirements/validate_meta.py` shadowed the `dataclasses.field` import with a `for field in required_fields` loop in two places. Renamed the loop variable to `field_name` at both sites.
- **E741 ambiguous-variable-name** — eight sites used `l` as a loop variable (almost all over `splitlines()`). Renamed all to `line`: `scripts/automation/orchestrate.py:1866`, `scripts/automation/tests/test_orchestrate.py:4818/4850` (replace_all in test file), `scripts/release/check_release_preconditions.py:130/294`, `scripts/release/execute_release.py:77/85`, `scripts/tasks/next_tasks.py:126`.
- **E702 multiple-statements-on-one-line-semicolon** — two `i = idx[0]; idx[0] += 1` patterns in `scripts/automation/tests/test_orchestrate.py`. Split onto separate lines.
- **E722 bare-except** — ten sites across `scripts/artifacts/generate_user_needs_status.py` (5) and `scripts/requirements/validate_meta.py` (5). All replaced with `except Exception:` (`replace_all` per file, grouped by indentation). No exception type narrowing because the catch sites are intentionally broad fallbacks around malformed-frontmatter parsing.
- **SIM102 collapsible-if** — six sites collapsed into single `and`-joined conditions: `scripts/artifacts/generate_status_overview.py:721`, `scripts/artifacts/generate_technical_release_notes.py:216`, `scripts/requirements/validate_meta.py:790/820`, `scripts/tasks/parse_task_creation_plan.py:524`, `scripts/user_needs/check_canon.py:494`.
- **SIM108 if-else-block-instead-of-if-exp** — seven sites converted to ternaries: `scripts/artifacts/generate_user_needs_status.py` (3 — Dr./Dr. med. short-name extraction and persona-applicability cell), `scripts/artifacts/update_doc_references.py:185/194` (path absolutisation), `scripts/tasks/create_orchestration_task.py:383` (plan-coverage fallback), `scripts/tasks/summarize_plan.py:93` (DFS leaf case).

### Suppressions added (each with inline reason per AC-13)

All suppressions are written as `# noqa: <CODE>[, <CODE>...] -- <reason>` or as a file-level `# ruff: noqa: <CODE>...` block followed by a multi-line comment naming each code and why. Em dash `—` was avoided inside noqa reason text because it triggers RUF002/RUF003 itself in some contexts; double-hyphen `--` is used instead.

File-level (`# ruff: noqa: ...`):
- `scripts/artifacts/generate_status_overview.py` — RUF001, RUF002 (MULTIPLICATION SIGN `×` is intentional in human-readable priority formulas `Urgency × 10 + Impact` across docstrings and report bodies).
- `scripts/automation/orchestrate.py` — RUF002, RUF003 (en dash for scenario ranges `S1–S26`; set-theory `∩` `∪` in the Jaccard-similarity docstring).
- `scripts/automation/tests/test_orchestrate.py` — SIM115, RUF002, RUF003, E402, SIM117. SIM115 because test fakes use `lambda p, c: open(p, "w").write(c)` lambdas to wire DI'd I/O; SIM117 because nested `with mock.patch(...)` blocks make per-mock failure attribution legible; E402 because Categories I/J/etc. have their imports under their own banner comments rather than at the top.
- `scripts/automation/tests/test_orchestrate_yaml_migration.py` — SIM115 (same DI lambda rationale).
- `scripts/release/release_readiness.py` — RUF002 (en dash for stage range `0–5`).
- `scripts/tasks/top_blocked_task.py` — RUF002 (multiplication sign in priority formula).
- `scripts/tests/test_create_orchestration_task.py` — RUF001 (en dash inside release-name fixtures like `"Alpha – Data Transfer"` matching real `RELEASE_BACKLOG.md` content).

Each file-level block also lists `RUF100` with the reason that file-level noqa is intermittently false-positively flagged by `RUF100` for codes whose finding ruff cannot statically attribute back to the directive.

Per-line:
- `scripts/automation/orchestrate.py:62` — `from util.yaml_frontmatter import ...  # noqa: E402` (sys.path mutation just above this import; carried over from prior code, reason text added per AC-13).
- `scripts/automation/orchestrate.py:3182` — `lock_fd = open(lock_path, "w")  # noqa: SIM115, RUF100` (advisory lock held for process lifetime; existing site, reason text upgraded).
- `scripts/automation/orchestrate.py:3208–3209` — production deps wiring lambdas (`read_file`/`write_file`) suppressed SIM115/RUF100; DI contract owns the I/O.
- `scripts/task_ordering/simulate.py:21/25/29` — three `# noqa: E402` reasons added to imports under a sys.path mutation.
- `scripts/tasks/create_orchestration_task.py:317` — fcntl lock-file open suppressed SIM115/RUF100; closed in `finally`.
- `scripts/tests/test_yaml_frontmatter.py:169` — re-styled as `_real_rename` underscore-prefix; the prior `# noqa: F841` directive was replaced with self-explanatory naming.

### Pre-existing suppressions audited (AC-13)

Before any edits:
- `scripts/automation/orchestrate.py:62` (E402), `scripts/automation/orchestrate.py:3175` (SIM115), `scripts/task_ordering/simulate.py:21–23` (E402), `scripts/tests/test_yaml_frontmatter.py:169` (F841). The 3175 site already carried `— kept open for lifetime of process`. The other four had `noqa` without `— reason`; reason text added (and the F841 site rewritten via underscore-prefix, as above).

## Proposed rule-change follow-ups

None. The cleanup pass did not surface a finding family that suggests the rule is wrong for the codebase. The bulk-suppressed cases (test-DI lambdas, mid-file category-banner imports, mathematical glyphs in docstrings) are local conventions in specific files, not patterns the codebase should adopt globally.

One latent observation worth recording for a future task (NOT acted on here, NOT a rule-change proposal):
- `scripts/artifacts/generate_id_registry.py` still defines `_grep_files` (line 142) after the parallel-grep rewrite made it dead. Ruff does not flag unused private module-level functions, so this is not blocking the gate. Leaving for a future dead-code sweep rather than expanding scope here.

## Verification (final)

`uv run bash scripts/quality/ruff_check.sh 2>&1 | tail -3` →
```
warning: No `requires-python` value found in the workspace. Defaulting to `>=3.12`.
warning: No `requires-python` value found in the workspace. Defaulting to `>=3.12`.
All checks passed!
```

`uv run pytest scripts/tests/ scripts/automation/tests/ -q 2>&1 | tail -5` →
```
.....................................                                    [100%]
541 passed in 22.56s
```

No test regressions. No `pyproject.toml`, `scripts/quality/*`, `CLAUDE.md`, or `scripts/util/yaml_frontmatter.py` modifications. No git commits made.

## Files modified this phase (per `git diff --name-only`)

Sources of truth for the cleanup are reflected by the changed file list — the protocol does NOT exhaustively enumerate every modified file because Pass 1 + Pass 2 auto-fixes touched ~45 files via ruff `--fix`, but the conceptual change boundaries are captured above.
