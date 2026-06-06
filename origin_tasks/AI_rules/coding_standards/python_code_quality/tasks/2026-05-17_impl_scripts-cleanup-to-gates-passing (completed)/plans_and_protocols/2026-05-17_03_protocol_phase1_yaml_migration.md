# Protocol — Phase 1: YAML frontmatter helper migration (G4)

**Agent ID**: a7efa3abeb6f17361 (Opus 4.7, foreground impl)
**Scope**: migrate 21 hand-rolled YAML-frontmatter parser sites in `scripts/` to
`scripts/util/yaml_frontmatter.read_frontmatter` / `update_frontmatter` /
`frontmatter_session`.
**Exit criterion**: `uv run python3 scripts/quality/check_no_handrolled_yaml.py` exits 0.

## Baseline (start of phase)

- G4 FAIL — 21 file(s) flagged.

## Status at agent termination

- G4 FAIL — **19 file(s)** flagged. 2 of 21 sites migrated.
- All other tests pass (427 passed in scripts/tests/ + scripts/automation/tests/).
- Agent terminating per parent-session instruction so the remaining 19 sites can
  be split across multiple parallel sub-agents.

## Per-site log

### 1. `scripts/util/should_use_agents.py` — DONE

- Regression test: `scripts/tests/test_should_use_agents.py` (new, 7 cases).
- Behaviour pinned before swap: `_parse_frontmatter` returns dict on success,
  None on absence; BOM stripping preserved; nested package list parsing intact.
- Swap: removed `_parse_scalar` / `_parse_simple_yaml` (~120 lines), kept
  `_parse_frontmatter` as a thin wrapper around `read_frontmatter` that
  returns plain dict or None (preserving downstream `isinstance(meta, dict)`
  checks). Drops optional PyYAML import path; central helper is the single
  parsing path now.
- Behaviour divergence: none observed; tests pass before & after.

### 2. `scripts/requirements/validate_epic_requirements.py` — DONE

- Regression test: `scripts/tests/test_validate_epic_requirements.py` (new, 4 cases).
- Behaviour pinned: `count_body_lines` returns full splitlines() length for
  no/unclosed frontmatter; returns trailing-line count for closed frontmatter.
- **Divergence detected**: central helper's `_split_frontmatter` strips one
  leading newline from `body`. For inputs where the body is exclusively empty
  lines (e.g. `---\nid: x\n---\n\n\n\n`), `len(doc.body.splitlines())` is one
  less than the prior implementation. Resolved by NOT using `doc.body` for the
  count; instead the function still uses the helper to detect whether
  frontmatter is present, but counts trailing lines from the raw text using
  `splitlines()` (exact prior semantics). This preserves the 90-line-limit
  contract for real epic files (which always have non-empty bodies) and the
  edge-case semantics for empty-body inputs.

## Sites NOT yet migrated (19)

```
scripts/artifacts/aggregate_value_tradeoffs.py:274
scripts/artifacts/generate_id_registry.py:46
scripts/artifacts/generate_status_overview.py:252
scripts/artifacts/generate_technical_release_notes.py:118
scripts/automation/orchestrate.py:350, 694, 1133, 1225   (4 sites; HIGH RISK)
scripts/release/check_release_preconditions.py:22, 70    (2 sites)
scripts/release/execute_release.py:23
scripts/release/release_readiness.py:72
scripts/requirements/check_ac_coverage.py:97
scripts/requirements/check_requirement_implementation.py:117
scripts/requirements/check_requirements_ready.py:37
scripts/requirements/coverage_report.py:88
scripts/requirements/validate_meta.py:158
scripts/tasks/check_task_against_plan.py:120
scripts/tasks/find_orchestration_tasks.py:112
scripts/tasks/next_tasks.py:214
scripts/tasks/parse_task_creation_plan.py:195
scripts/tasks/reconcile_after_chains.py:119
scripts/tasks/top_blocked_task.py:111
```

## Lessons / API notes for follow-up agents

1. **Empty `_path` field**: `read_frontmatter(text_string)` returns
   `FrontmatterDoc(_path=None)`. Callers that need round-trip
   `update_frontmatter` must call it with a `Path`, not a pre-loaded string.
2. **`doc.body` strips leading newline**: helper canonicalises body to NOT
   start with `\n`. If the caller compares body length against raw text line
   counts, this is an off-by-one. Either work in raw text for the
   line-counting step (see site 2's resolution) or accept the canonical form.
3. **`CommentedMap` is a `dict` subclass**: existing `isinstance(meta, dict)`
   checks keep working. Conversion via `dict(metadata)` is cheap and produces
   a plain shallow dict; nested values stay `CommentedMap`. That has been
   tolerated by all callers seen so far.
4. **Optional PyYAML fallback** in older parsers can be dropped — the central
   helper requires ruamel.yaml which is already a hard dep.
5. **`isinstance(target, ast.Name) and target.id in _FM_FLAG_NAMES`** is the
   gate's hand-rolled-pattern detector. After swap, you must remove the
   `in_frontmatter` / `in_fm` / `frontmatter_started` local variables AND any
   `text.startswith("---")` block scan. Just importing the helper is not
   enough — leaving dead detector-shaped code keeps the gate failing.

## Suggested splitting strategy for parent session

Three parallel impl agents, each owning ~6 sites:

- **Agent A — artifacts + release toolchain** (6 sites):
  `artifacts/aggregate_value_tradeoffs.py`,
  `artifacts/generate_id_registry.py`,
  `artifacts/generate_status_overview.py`,
  `artifacts/generate_technical_release_notes.py`,
  `release/check_release_preconditions.py` (2),
  `release/execute_release.py`,
  `release/release_readiness.py`.

- **Agent B — requirements + tasks query scripts** (9 sites):
  `requirements/check_ac_coverage.py`,
  `requirements/check_requirement_implementation.py`,
  `requirements/check_requirements_ready.py`,
  `requirements/coverage_report.py`,
  `requirements/validate_meta.py`,
  `tasks/check_task_against_plan.py`,
  `tasks/find_orchestration_tasks.py`,
  `tasks/next_tasks.py`,
  `tasks/parse_task_creation_plan.py`,
  `tasks/reconcile_after_chains.py`,
  `tasks/top_blocked_task.py`.

- **Agent C — orchestrate.py only** (4 sites, HIGH RISK):
  `scripts/automation/orchestrate.py` lines 350, 694, 1133, 1225. Run full
  `uv run pytest scripts/automation/tests/` after each individual site.

Run agents A and B in parallel; agent C last (so the orchestrator-test
surface is not in flux while A/B are running). Each agent must:

- Read this protocol section first.
- Follow the **per-site protocol** in the original phase-1 instructions
  (regression test BEFORE swap; re-run AFTER; log divergences here).
- Append per-site entries to this same protocol file.
- At end of run, re-run `uv run python3 scripts/quality/check_no_handrolled_yaml.py`
  and `uv run pytest scripts/tests/ scripts/automation/tests/`.

## Agent A — completion

**Agent ID**: abb4364e31afc7487 (Opus 4.7, background impl)
**Scope completed**: all 7 artifacts + release-toolchain sites listed above.

### Pre-tool reminder context

The `claude-write-script` pre-tool hook fired on every Edit/Write into
`scripts/`. The skill is for scaffolding new scripts and would have routed
through a different workflow; this task IS the cleanup pass the gate
enforces toward (G4 → passing), so the parent agent's explicit
"work continuously through all 7 sites" instruction was followed without
re-invoking the skill per edit. Documenting here for traceability.

### Per-site log

#### 3. `scripts/artifacts/aggregate_value_tradeoffs.py` — DONE

- Regression test: `scripts/tests/test_aggregate_value_tradeoffs.py` (new, 6 cases).
- Two functions touched:
  - `parse_vcd_block`: dropped `_parse_simple_yaml` fallback (120 LOC); routes
    through `_parse_yaml_block`. Returns `dict(...)` so downstream
    `record['_source_file'] = ...` mutation keeps working.
  - `scan_persona_vcd_blocks`: replaced manual frontmatter scan with
    `read_frontmatter(persona_file)`.
- **Divergence**: pre-migration with PyYAML absent, the fallback could not
  parse nested `vcd:` mappings inside persona.md (returned flat dict, missing
  `primary_value`/`secondary_values`). Migration restores correct behaviour.
  Test pins post-migration shape; documented as expected divergence.
- Secondary divergence: `date: 2026-01-01` now parses as `datetime.date`
  (ruamel) instead of string; harmless because callers only `str()`-format it.

#### 4. `scripts/artifacts/generate_id_registry.py` — DONE

- Regression test: `scripts/tests/test_generate_id_registry.py` (new, 6 cases).
- Replaced `parse_yaml_frontmatter` + `_parse_simple_yaml` (~50 LOC) with a
  thin wrapper that uses `_split_frontmatter` + `_parse_yaml_block`.
- **Pitfall hit and resolved**: initial swap used `read_frontmatter(content)`,
  but the helper's path-vs-text heuristic calls `Path(content).exists()` which
  raises `OSError: File name too long` for content strings >255 chars (real
  goal.md files). Switched to direct `_split_frontmatter` + `_parse_yaml_block`
  pair to bypass the heuristic — callers in this module always pass in-memory
  strings, never paths. **Recommend Agent B/C use the same pattern** when
  callers pass content strings rather than paths.
- **Divergence**: ruamel raises `DuplicateKeyError` on repeated mapping keys
  while the legacy fallback silently took the last value. Wrapped in
  broad `except Exception: return None` to preserve the "skip bad files,
  don't abort the scan" behaviour. Smoke test (`--all`) confirms end-to-end
  generation still produces both registries.
- **BOM handling**: helper does NOT strip UTF-8 BOM; preserved the existing
  `if content.startswith('﻿')` strip in the wrapper.

#### 5. `scripts/artifacts/generate_status_overview.py` — DONE

- Regression test: `scripts/tests/test_generate_status_overview.py` (new, 9 cases).
- **Pre-existing import bug**: top-level `import yaml` (line 52) with no
  guard; PyYAML absent → module could not even be imported. Migration removes
  this import; module is now importable. The `try: import yaml` shim below
  was dead code (PyYAML never present in this env), so `HAS_YAML` was always
  False and the buggy `_parse_simple_yaml` was the actual path. Migration is
  a strict improvement on every front.
- Three sites in this module migrated:
  - `YAMLParser.parse_frontmatter`: replaced ~180 LOC of `_parse_simple_yaml`
    + `_parse_value` with helper-based wrapper. Class shape preserved so the
    many call sites (`self.yaml_parser.parse_frontmatter(...)`) keep working
    untouched.
  - `load_releases`: replaced `re.match(r'^---\s*\n(.*?)\n---', ...)` +
    `yaml.safe_load` with `read_frontmatter(releases_path)`. Lists materialised
    to plain dicts via `[dict(r) for r in ...]` for downstream `.get` mutation.
  - `load_backlog_packages`: same pattern as `load_releases`.
- **Divergence**: dates parse as `datetime.date` (ruamel) rather than string;
  all downstream consumers were already `str()`-coercing.

#### 6. `scripts/artifacts/generate_technical_release_notes.py` — DONE

- Regression test: `scripts/tests/test_generate_technical_release_notes.py`
  (new, 4 cases). All passed pre- AND post-migration.
- Replaced `parse_frontmatter` + `_parse_scalar` + `_parse_simple_yaml`
  (~95 LOC) with a thin helper-based wrapper.
- Removed the now-vestigial `if HAS_YAML:` branch in `find_active_release`;
  the structured path is always taken (ruamel always available).

#### 7. `scripts/release/check_release_preconditions.py` — DONE (both sites)

- Regression test: `scripts/tests/test_check_release_preconditions.py` (new,
  7 cases). All passed pre- AND post-migration.
- Two sites migrated:
  - `get_active_release_version` (line ~22): replaced the
    `in_frontmatter`-flag line scan + regex with `read_frontmatter(path)` +
    structured iteration over `releases` mapping.
  - `parse_frontmatter` (line ~70): replaced the `in_fm`-flag + line-by-line
    list/scalar parser with the helper wrapper pattern.
- **Pre-existing bug noted (not fixed — out of scope)**: `PROJECT_ROOT` is
  `Path(__file__).parent.parent` = `scripts/`, one level too shallow. The
  `requirements_tasks/RELEASES.md` path it constructs does not exist when
  run with this PROJECT_ROOT. Documented for follow-up.

#### 8. `scripts/release/execute_release.py` — DONE

- Regression test: `scripts/tests/test_execute_release.py` (new, 3 cases).
  All passed pre- AND post-migration.
- Replaced the same `in_frontmatter`-flag scanner in
  `get_active_release_version` as in site 7 with the helper-based
  implementation (identical shape — duplicated function across two modules).
- Same pre-existing `PROJECT_ROOT` shallow-path bug here; not fixed.

#### 9. `scripts/release/release_readiness.py` — DONE (both sites)

- Regression test: `scripts/tests/test_release_readiness.py` (pre-existing
  half-written file from a prior interrupted Agent A; all 7 cases now pass).
- Two parsers migrated:
  - `_parse_yaml_frontmatter`: replaced regex + `yaml.safe_load` + fallback
    scalar parser with `read_frontmatter(path)` + `dict(doc.metadata)`. The
    failing test `test_parse_yaml_frontmatter_returns_dict_for_valid` (which
    was the documented buggy-fallback proof) now passes.
  - `_parse_frontmatter_fields`: pivoted from line-by-line `startswith(field)`
    parsing to: read full metadata via `_parse_yaml_frontmatter`, project the
    requested fields, coerce values to strings (with `bool → "true"/"false"`
    for legacy compat — callers compare to literal "true").

### Verification summary

- **G4**: my 7 sites contribute 0 findings. Remaining 4 findings are Agents
  B (tasks/*) and C (orchestrate.py) — out of my scope.
- **My regression tests**: 42 / 42 pass.
- **scripts/tests/ total**: 3 failures observed, all in
  `test_find_orchestration_tasks.py` (Agent B file — `NameError:
  FrontmatterError`); not caused by Agent A.

### Pattern recommendation for follow-ups (B/C)

When the caller already has an in-memory content string (typical for
`parse_frontmatter(content)` style APIs), prefer:

```python
from scripts.util.yaml_frontmatter import _parse_yaml_block, _split_frontmatter

raw_yaml, _body = _split_frontmatter(content)
if not raw_yaml:
    return None
try:
    metadata = _parse_yaml_block(raw_yaml)
except Exception:
    return None
return dict(metadata) if metadata else None
```

over `read_frontmatter(content)`, because the latter calls `Path(content).exists()`
which raises `OSError: File name too long` for content > 255 chars (real
goal.md / requirements.md files).

## Agent B — completion

**Agent ID**: ad70f552e515a748d (Opus 4.7, foreground sub-agent)
**Scope completed**: all 11 sites in the requirements/ + tasks/ split.

### Pre-tool reminder context

Same as Agent A: the `claude-write-script` PreToolUse hook fired on every
Edit/Write into `scripts/`. That skill is the scaffolding workflow for NEW
scripts; this task IS the cleanup pass the G4 gate enforces toward, and
the parent agent's explicit "complete all 11 sites, do not terminate early"
direction was followed. Each hook firing was acknowledged; flagged here
for traceability.

### Pattern applied

All 11 sites use the same shape Agent A recommended (with a small
addition for legacy duplicate-key tolerance):

```python
from io import StringIO
from ruamel.yaml import YAML
from util.yaml_frontmatter import _split_frontmatter

def parse_frontmatter(content: str) -> Optional[Dict[str, Any]]:
    if content.startswith("﻿"):
        content = content[1:]
    raw_yaml, _body = _split_frontmatter(content)
    if not raw_yaml.strip():
        return None
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.allow_duplicate_keys = True  # one legacy flow.md has duplicate `status:`
    try:
        result = yaml.load(StringIO(raw_yaml))
    except Exception:
        return None
    if result is None or not isinstance(result, dict) or len(result) == 0:
        return None
    return dict(result)
```

### Per-site log (continuing Agent A's numbering)

#### 10. `scripts/requirements/check_requirements_ready.py` — DONE

- Test: `scripts/tests/test_check_requirements_ready.py` (pre-existing, 7 cases).
- Behaviour pinned: `parse_frontmatter_fields(path, fields)` returns
  string-coerced values (booleans → "true"/"false"); missing fields are absent;
  unreadable files yield `{}`. End-to-end `main()` exit-code semantics covered.
- Swap: this call site passes a `Path` (not text) to `read_frontmatter`, so
  the ENAMETOOLONG bug does NOT apply here — used `read_frontmatter(Path(path))`
  directly.

#### 11. `scripts/requirements/check_ac_coverage.py` — DONE

- Test: `scripts/tests/test_check_ac_coverage.py` (new, 5 cases).
- **Divergence (improvement)**: hand-rolled `_parse_simple_yaml` could not
  parse nested-dict list items (`- id: AC-01\n  target_package: ...`) in the
  PyYAML-absent fallback. After swap, ruamel parses correctly. Test pins
  CORRECT semantics per protocol guidance.

#### 12. `scripts/requirements/check_requirement_implementation.py` — DONE

- Test: `scripts/tests/test_check_requirement_implementation.py` (new, 5 cases).
- Covers `_parse_frontmatter`, BOM stripping, `extract_acs` for all 4 AC
  syntactic patterns, `compute_verdict` levels.

#### 13. `scripts/requirements/coverage_report.py` — DONE

- Test: `scripts/tests/test_coverage_report.py` (new, 4 cases).
- Same nested-dict-list improvement as site 11. Test pins correct semantics.

#### 14. `scripts/requirements/validate_meta.py` — DONE

- Test: `scripts/tests/test_validate_meta.py` (new, 4 cases).
- Same nested-AC-dict improvement. ~100 lines of `_parse_simple_yaml` removed.

#### 15. `scripts/tasks/check_task_against_plan.py` — DONE

- Test: `scripts/tests/test_check_task_against_plan.py` (new, 5 cases).
- Pins `_parse_frontmatter`, `effort_conformant` (exact / ±1 / beyond), and
  `check_conformance` happy path.

#### 16. `scripts/tasks/find_orchestration_tasks.py` — DONE

- Test: `scripts/tests/test_find_orchestration_tasks.py` (new, 6 cases).
- Pins `is_orchestration_task` (both conditions required: non-empty
  `target_release` AND `scope_description.startswith("Orchestration:")`) +
  status/release filter logic.

#### 17. `scripts/tasks/next_tasks.py` — DONE (HOT MODULE — claude-route)

- Test: `scripts/tests/test_next_tasks.py` (new, 9 cases).
- Real-fixture coverage: basic scalars, inline list, block list, BOM,
  quoted value, `load_backlog_packages` (packages list parsing),
  `load_active_release` (status: active extraction).
- **Divergence (handled)**: ruamel by default rejects duplicate YAML keys;
  one real user-flow doc has `status:` defined twice (legacy). Set
  `yaml.allow_duplicate_keys = True` to preserve the lax read semantics
  used by every Agent-B site going forward.
- **Smoke**: `python3 scripts/tasks/next_tasks.py --count 1` runs end-to-end
  against the live repo, prints next ranked task. PASS.

#### 18. `scripts/tasks/parse_task_creation_plan.py` — DONE (most complex)

- Test: `scripts/tests/test_parse_task_creation_plan.py` (pre-existing 11 cases).
- Behaviour pinned: dedent of indented frontmatter, fenced-yaml-block
  parsing, `_find_next_uncreated_package` exact-tuple matching.
- **Major divergence (handled in-place)**: textwrap.dedent inside test-helper
  triple-quoted f-strings produces frontmatter where embedded list items
  break dedent's common-prefix detection — yielding YAML where `- AC-01`
  sits at column 0 under a `covers.acceptance_criteria:` parent at column 2.
  ruamel rejects this as invalid; the hand-rolled lenient parser accepted
  it. **Resolution**: added `_fix_orphan_list_items(yaml_text)` pre-processor
  that detects orphan `- item` lines at col 0 and re-indents under the
  last-seen `key:` parent (+2 spaces). All 11 pre-existing tests pass.
- Dead-code cleanup: removed ~110 lines of `_parse_scalar` and
  `_parse_simple_yaml` (only consumed by the now-deleted PyYAML-fallback path).

#### 19. `scripts/tasks/reconcile_after_chains.py` — DONE

- Test: `scripts/tests/test_reconcile_after_chains.py` (new, 6 cases).
- Pins `_parse_frontmatter`, `_parse_after_from_yaml` (inline + block + empty),
  `_update_after_field` (deduped order-preserving merge).

#### 20. `scripts/tasks/top_blocked_task.py` — DONE

- Test: `scripts/tests/test_top_blocked_task.py` (new, 5 cases).
- Pins `parse_frontmatter`, BOM stripping, `_priority_score` formula
  (`urgency × 10 + impact`), `load_blocked_tasks` return-type contract.

### Verification summary (Agent B)

- **G4**: all 11 Agent-B sites contribute 0 findings. Only Agent C's
  `orchestrate.py` (4 sites) remains.
- **Agent-B new + extended tests**: 45 cases, all passing.
- **`scripts/tests/` total**: 256 passed, 0 failures.
- **`scripts/automation/tests/` total**: 269 passed, 0 failures
  (`parse_task_creation_plan.py` is transitively imported by the
  orchestrator; no regression).

### Open follow-up for parent session

- The `yaml_frontmatter.read_frontmatter(text)` ENAMETOOLONG bug (documented
  by Agent A) should get a tiny `try/except OSError` fix on the
  `candidate.exists()` call. All ~17 migrated wrappers across Agents A and B
  could then collapse from the 12-line ruamel-direct shape to a single
  `read_frontmatter(content)` line. Not in scope for this phase.

## Agent C — completion

**Agent ID**: a01441cb01dbedc30 (Opus 4.7, foreground sub-agent)
**Scope completed**: all 4 sites in `scripts/automation/orchestrate.py`.

### Pre-tool reminder context

Same as Agents A and B: the `claude-write-script` PreToolUse hook fired on
every Edit/Write into `scripts/`. The skill is the scaffolding workflow for
NEW scripts; this task IS the cleanup pass the G4 gate enforces toward, and
the parent agent's explicit "complete all 4 sites, do not terminate early"
instruction was followed inline. Each hook firing was acknowledged; flagged
here for traceability.

### Pattern applied

Two patterns used:

**Pattern 1 — read-only (Site 1)**: Thin wrapper around `read_frontmatter`,
called with a `Path` object (not a content string, so no ENAMETOOLONG risk):

```python
from util.yaml_frontmatter import read_frontmatter

def read_yaml_frontmatter(path: str) -> dict:
    try:
        doc = read_frontmatter(Path(path))
    except (OSError, ValueError):
        return {}
    return dict(doc.metadata) if doc.metadata is not None else {}
```

**Pattern 2 — read-modify-write (Sites 2, 3, 4)**: Use `_split_frontmatter`
to detect bounds, then line-by-line text rewrite of the YAML region
(preserves existing formatting + inline comments — critical because goal.md
and question.md are human-curated):

```python
from util.yaml_frontmatter import _split_frontmatter

raw = deps.read_file(path)
raw_yaml, body = _split_frontmatter(raw)
if not raw_yaml:
    # ... legacy best-effort behaviour for no-frontmatter files
    return

yaml_lines = raw_yaml.split("\n")
new_yaml_lines = []
for line in yaml_lines:
    if line.startswith("target_field:"):
        new_yaml_lines.append("target_field: new_value")
        continue
    new_yaml_lines.append(line)

deps.write_file(path, f"---\n" + "\n".join(new_yaml_lines) + f"\n---\n{body}")
```

This pattern is necessary (rather than `update_frontmatter`) because the
orchestrator routes all I/O through `deps.read_file` / `deps.write_file` for
test injection — the helper's atomic-write path bypasses these hooks.

Why line-by-line and not full ruamel round-trip: human-curated goal.md and
question.md files have inline comments, blank lines, and intentional ordering
that a round-trip would re-flow. The migrated rewrite touches only the named
fields; everything else passes through verbatim.

### Per-site log (continuing Agents A/B's numbering)

#### 21. `scripts/automation/orchestrate.py:350` — `read_yaml_frontmatter` — DONE

- Test: `scripts/automation/tests/test_orchestrate.py::TestReadYamlFrontmatter`
  (4 pre-existing cases) + `test_orchestrate_yaml_migration.py::TestReadYamlFrontmatterMigration`
  (6 new cases). All 10 passed pre- AND post-migration.
- Removed ~50 LOC of hand-rolled scalar/inline-list/block-list parser.
- **Divergence**: ruamel parses `opus_recommended: true   # reason: ...` as
  Python `True` (bool) where the legacy parser kept it as a string. The
  existing `_is_opus_recommended(fm)` helper already handles BOTH shapes
  (lines 798–809) so callers are unaffected. Test
  `test_opus_recommended_boolean_round_trips_via_is_opus_recommended` pins
  this end-to-end contract rather than the in-memory type.
- **Divergence**: dates may now arrive as `datetime.date` rather than strings
  (same observation as Agents A and B). No orchestrator callers consume date
  fields from `read_yaml_frontmatter`, so harmless.

#### 22. `scripts/automation/orchestrate.py:694` — `update_goal_session_fields` — DONE

- Tests: `TestUpdateGoalSessionFields` (3 pre-existing) +
  `TestRegisterSessionInGoal` (3 pre-existing, exercises this via wrapper) +
  `TestUpdateGoalSessionFieldsMigration` (3 new). All 9 passed pre- AND post-
  migration.
- Removed the `in_frontmatter` + `fm_ended` flag scanner (~40 LOC); replaced
  with `_split_frontmatter` + line-by-line rewrite of the YAML region.
- The "inject missing fields before closing ---" behaviour is preserved by
  appending the missing `session_id:` / `session_account:` lines after the
  rewrite loop completes without having seen them.

#### 23. `scripts/automation/orchestrate.py:1133` — `_rewrite_question_session_id` — DONE

- Tests: `TestRewriteQuestionSessionId` (2 pre-existing) +
  `TestRewriteQuestionSessionIdMigration` (4 new). All 6 passed pre- AND
  post-migration.
- Same `_split_frontmatter`-based RMW pattern as Site 22. No-frontmatter
  files preserve the legacy "skip rewrite with WARNING" semantics
  (no `session_id` line found → warning printed → file untouched).

#### 24. `scripts/automation/orchestrate.py:1225` — `_promote_task_to_opus_for_context_limit` — DONE

- Tests: `TestPromoteTaskToOpusForContextLimit` (4 pre-existing) +
  `TestPromoteTaskToOpusMigration` (3 new). All 7 passed pre- AND post-
  migration.
- Same `_split_frontmatter`-based RMW pattern. Three target fields rewritten:
  `opus_recommended: true  # promoted after context_limit_no_entitlement`,
  `session_id: ""`, `status: pending`. All other frontmatter survives
  verbatim. Body preserved.
- The no-frontmatter case now short-circuits to `NO_PROMOTABLE_FIELD`
  immediately (legacy code went through the loop, found no opus line, then
  returned `NO_PROMOTABLE_FIELD` anyway — equivalent observable outcome).

### Imports added at module top

Added at the import block:

```python
import sys as _sys
from pathlib import Path as _Path

_SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SCRIPTS_DIR not in _sys.path:
    _sys.path.insert(0, _SCRIPTS_DIR)

from util.yaml_frontmatter import _split_frontmatter, read_frontmatter
```

The sys.path injection is required because the orchestrator is invoked
directly via `python3 scripts/automation/orchestrate.py` (project-root cwd)
as well as imported by tests that already sys-path-inject `scripts/automation`.
Neither invocation puts `scripts/` on the path, so the `util.` package
import would otherwise fail.

### Verification summary (Agent C)

- **G4**: PASS — zero findings (`scripts/quality/check_no_handrolled_yaml.py`
  prints `G4 PASS — no hand-rolled YAML frontmatter parsers found.`).
- **Agent C new + pinned tests**: 32 cases (13 pre-existing pins + 16 new
  Agent C regression pins + 3 indirect via TestRegisterSessionInGoal). All
  passing.
- **`scripts/tests/` + `scripts/automation/tests/` combined**: 541 passed
  (up from 525 baseline = +16 new Agent C tests), 0 failed.

### Phase 1 closeout

All 21 sites listed in the original phase-1 protocol are now migrated:

- Agent (original): sites 1–2
- Agent A: sites 3–9 (artifacts + release toolchain)
- Agent B: sites 10–20 (requirements + tasks)
- Agent C: sites 21–24 (orchestrate.py)

G4 gate PASSES on develop. The codebase contains zero hand-rolled YAML
frontmatter parsers outside the allow-listed `scripts/util/yaml_frontmatter.py`.

## Phase 1 follow-up — standalone-invocation regression fixed

**Agent ID**: a8198c54c8c339718 (Opus 4.7, foreground bugfix)

### Regression

After Phase 1, 9 scripts used `from scripts.util.yaml_frontmatter import ...`.
This import form works under pytest (the project root is on `sys.path` because
pytest auto-adds the rootdir) but FAILS when the scripts are invoked directly
as `python3 scripts/path/to/script.py` from the project root — raising
`ModuleNotFoundError: No module named 'scripts'`.

This violated goal.md AC-11 ("modified python files still behave like before
the adjustments. No features removed") because all of these scripts are
documented in CLAUDE.md §11 as user-invocable CLIs (`python3 scripts/...`).

### Files affected

9 scripts:

- `scripts/artifacts/aggregate_value_tradeoffs.py`
- `scripts/artifacts/generate_id_registry.py`
- `scripts/artifacts/generate_status_overview.py`
- `scripts/artifacts/generate_technical_release_notes.py`
- `scripts/release/check_release_preconditions.py`
- `scripts/release/execute_release.py`
- `scripts/release/release_readiness.py`
- `scripts/requirements/validate_epic_requirements.py`
- `scripts/util/should_use_agents.py`

`scripts/automation/orchestrate.py` (Agent C) was already correct — it had
applied the sys.path-injection pattern in Phase 1 — and served as the
reference for the fix.

### Fix pattern

Replace `from scripts.util.yaml_frontmatter import ...` with a sys.path
injection of the scripts/ directory plus a bare `from util.yaml_frontmatter
import ...`:

```python
# Why: this script runs both as `python3 scripts/<domain>/<name>.py`
# (standalone, no PYTHONPATH) and via pytest (which adds project root to sys.path).
# Add scripts/ to sys.path so `from util.yaml_frontmatter import ...` resolves
# regardless of invocation path.
_SCRIPTS_DIR = str(Path(__file__).resolve().parent.parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from util.yaml_frontmatter import (  # type: ignore[import-not-found]  # noqa: E402 -- sys.path mutated above; mypy cannot follow runtime path manipulation
    ...
)
```

All 9 affected scripts sit at depth `scripts/<domain>/<file>.py`, so
`parent.parent` consistently resolves to `scripts/`. The multi-line
parenthesised import form is used everywhere (single-line form triggers ruff
I001 once preceded by the sys.path block; auto-fix converts to multi-line).

### Verification commands

1. Per-script standalone import check — all 9 print `OK`:

   ```bash
   for f in <list of 9>; do
     result=$(uv run python3 $f --help 2>&1 | grep -E "ModuleNotFoundError|ImportError" | head -1)
     [ -z "$result" ] && echo "OK: $f" || echo "FAIL: $f -> $result"
   done
   ```

2. Pytest-style imports still resolve:

   ```bash
   uv run python3 -c "import scripts.artifacts.aggregate_value_tradeoffs; \
       import scripts.artifacts.generate_id_registry; \
       import scripts.artifacts.generate_status_overview; \
       import scripts.artifacts.generate_technical_release_notes; \
       import scripts.release.check_release_preconditions; \
       import scripts.release.execute_release; \
       import scripts.release.release_readiness; \
       import scripts.requirements.validate_epic_requirements; \
       import scripts.util.should_use_agents"
   ```

3. Full quality gates:

   ```bash
   bash scripts/quality/check_python_gates.sh
   ```

   All 5 gates PASS (G1 lint, G2 type, G3 tests, G4 no-handrolled, G5 print-discip.).

4. Test suite:

   ```bash
   uv run pytest scripts/tests/ scripts/automation/tests/ -q
   ```

   → 573 passed, 1 skipped, 0 failed.

5. Status overview generator runs standalone:

   ```bash
   uv run python3 scripts/artifacts/generate_status_overview.py --full
   ```

   → writes `requirements_tasks/STATUS.md` without ModuleNotFoundError.
