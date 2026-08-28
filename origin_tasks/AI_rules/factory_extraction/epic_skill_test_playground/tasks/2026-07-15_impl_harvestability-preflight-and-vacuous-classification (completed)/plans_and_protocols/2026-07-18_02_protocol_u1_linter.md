# Protocol — U1: linter D2 (all-degenerate → reject) + D3 item 2 (unreachable-authored-terminal check)

Task: `../goal.md` (TASK-PROC-068-30) · Unit: U1 of `2026-07-18_01_plan_preflight-and-classification.md`.
Agent ID: `a98fcd27308f8969b` (implementation-engineer subagent).

## Scope executed

Per the plan's U1 row and the dispatcher instructions, ONLY these two files were touched:
- `scripts/factory/layer_derivation/backfill_orchestration.py` — `lint_spec` (+ its alias
  `harvestability_preflight` untouched — same object) and `SpecLintResult` docstrings.
- `scripts/tests/test_backfill_orchestration.py` — AC-10/AC-22 test class `TestSpecAuthoringSurface`.

`scripts/playground/*` was NOT touched (out of U1 scope; that is U2–U4).

All edits were routed through the `claude-write-script` skill (invoked once at the start of the
implementation, per project law — no direct Edit/Write on `scripts/**` without it).

## What changed

### D2 — all-degenerate spec: warning → blocking error

`lint_spec`'s `elif all(d.vacuous for d in derived):` branch used to `warnings.append(...)` and leave
`predicted_harvestable=True`. It now `errors.append(...)` with a teaching message that:
- states the doomed-spec verdict and cites AC-22 explicitly ("all-degenerate rejection — a doomed
  spec, not a warning");
- names every degenerate span's `unit_id` (e.g. `[span-0, span-1, ... span-5]`) so the author can see
  WHICH spans drove the verdict, per the dispatcher's teaching-quality requirement;
- tells the author to check `fixed_layers` (unchanged advice from the predecessor's warning text).

Because this branch now populates `errors` instead of `warnings`, `ok = not errors` becomes `False`
and `predicted_harvestable = bool(derived) and not errors` becomes `False` automatically — no change
needed to the trailing `predicted_harvestable` computation.

### D3 item 2 — unreachable-authored-terminal check (new `else` branch)

Added a new branch (only reached when `derived` is non-empty and NOT all-vacuous) that, for every
non-vacuous `DerivedSpanUnit`, iterates its `authoring_pairs` and calls `authoring_skill_for(pair)`
(the SAME function `build_directive` at line ~1021 already uses to resolve the dispatched skill — no
new/duplicate mapping was added). If `authoring_skill_for` returns `None` for any pair, appends a
blocking error naming the span index, its `unit_id`, and the unmapped `layer_pair` value, citing
AC-22 / ADV-sg-02.

**Important finding recorded for the next unit and future maintainers**: under the CURRENT
`AUTHORING_SKILL_BY_PAIR` map, this branch is structurally unreachable via any real `fixed_layers`
input. `_layer_pairs_for_span` (the function `derive_span_units` calls to build `authoring_pairs`)
already filters its output to `p.value in AUTHORING_SKILL_BY_PAIR` (line ~676) BEFORE the pairs ever
reach `DerivedSpanUnit.authoring_pairs`. So any pair absent from the map (currently only
`task_code`, intentionally excluded — code authoring out of scope) never appears in
`authoring_pairs` in the first place; it makes the span look `vacuous=True` (folded into the D2
all-degenerate case) rather than "real-but-unreachable". The new check is therefore a **defensive
invariant**, not dead-but-reachable logic: it guards against `AUTHORING_SKILL_BY_PAIR` and the
filter inside `_layer_pairs_for_span` ever diverging (e.g. a future edit that adds a new `LayerPair`
to one map but not the other, or a future refactor of `authoring_skill_for`'s lookup logic). This
matches AC-22's literal text ("a spec with a real span that can never reach an authored terminal —
e.g. no authoring skill registered for its pair") exactly, even though today's concrete map makes it
unreachable in practice. Verified this by direct interactive inspection of
`derive_span_units([Layer.FLOW])` and `derive_span_units(list(Layer))` — see test file for the
reachability workaround used to exercise the branch (monkeypatching `authoring_skill_for` only,
leaving the upstream filter's own dict read untouched).

### Docstring updates (item c)

- `lint_spec`'s docstring no longer says the build.py pre-flight is "out of scope here" — it now
  states `lint_spec` IS the AC-22 harvestability pre-flight predicate, that build.py's pre-flight
  (future unit) imports and calls this SAME function, and lists the (now four) doomed classes:
  no-spans-resolved, mismatched-arity, all-degenerate (AC-22, was "harvestable-but-warned" — now
  corrected), and real-span-with-unmapped-pair (ADV-sg-02, new).
- `SpecLintResult`'s docstring no longer cites "an all-degenerate spec" as a `warnings` example
  (that case moved to `errors`); it now states `warnings` is reserved for future non-blocking
  findings and no current check populates it.
- The `harvestability_preflight = lint_spec` alias comment ("build.py's pre-flight later") was left
  as-is — still accurate, since build.py's call site (U3) has not landed yet within this task.

## Final `lint_spec` / `SpecLintResult` contract (for the next unit — U2/U3/U4)

```python
def lint_spec(
    fixed_layers: Sequence[Layer], span_units: Sequence[Any] | None = None
) -> SpecLintResult: ...

harvestability_preflight = lint_spec  # same object, unchanged alias
```

`SpecLintResult` fields (unchanged shape, `to_dict()` unchanged):
- `ok: bool` — `True` only when `errors` is empty.
- `predicted_harvestable: bool` — `bool(derived) and not errors`. **Now `False` for an
  all-degenerate spec and for a real span with an unmapped layer pair** (previously `True` for the
  former).
- `errors: tuple[str, ...]` — blocking. Now includes (in addition to the pre-existing
  no-spans-resolved / mismatched-arity messages): the all-degenerate message (lists every degenerate
  `unit_id`) and, per-span, the unmapped-layer-pair message (names `span {index} ({unit_id})` and the
  `layer_pair` value).
- `warnings: tuple[str, ...]` — **now always empty** under every current code path (no check
  populates it any more); the field is retained on the dataclass for forward-compatibility, not
  removed.
- `derived: tuple[DerivedSpanUnit, ...]` — unchanged.

**Call contract for U3 (build.py pre-flight call site)**: call `harvestability_preflight(fixed_layers,
span_units)` (or `lint_spec` directly — same object) exactly as `layer-derivation-start` does. Treat
`result.ok is False` (equivalently `not result.predicted_harvestable`, since `predicted_harvestable`
is now `False` whenever `ok` is `False`, and additionally `False` when `derived` is empty even if
`errors` somehow ended up empty — but that combination cannot occur given the current logic) as the
doomed-spec verdict requiring the distinct doomed-spec exit code and NO deployed run. `result.errors`
is the teaching-quality message list to surface to the developer/log.

## Tests

`scripts/tests/test_backfill_orchestration.py::TestSpecAuthoringSurface`:
- `test_all_degenerate_spec_warns_but_is_harvestable` → renamed/rewritten to
  `test_all_degenerate_spec_is_rejected_ac22`. Asserts `not result.ok`, `not
  result.predicted_harvestable`, `not result.warnings`, an error containing "degenerate", and that
  the error names both `span-0` and `span-5` (teaching-quality — which spans drove the verdict).
  Docstring cites AC-22 and records the D2 divergence from the predecessor
  (TASK-PROC-071-06-10: warn → AC-22: reject), per the dispatcher's explicit citation requirement.
- New `test_real_span_with_unmapped_layer_pair_is_rejected(monkeypatch)` — exercises the new D3-item-2
  branch via `monkeypatch.setattr(bo, "authoring_skill_for", lambda _pair: None)` against
  `bo.lint_spec([fl.Layer.FLOW])` (2 real non-vacuous spans). Asserts rejection and that the error
  names `"span 0"` and contains `"no authoring skill is registered"`. Docstring explains WHY the
  monkeypatch seam was needed (see "Important finding" above).
- Pre-existing tests unaffected: `test_lint_accepts_derived_arity`,
  `test_mismatched_arity_mapping_is_rejected`, `test_empty_fixed_layers_is_rejected`,
  `test_teaching_gate_and_preflight_are_one_implementation`,
  `test_teaching_gate_and_preflight_agree_on_the_battery` (still passes — both names resolve to the
  same function object, so any change is visible identically through both), `test_derive_spec_cli_*`,
  `test_lint_cli_rejects_mismatched_arity`.

## Gate outcome

`scripts/quality/check_python_gates.sh` — **ALL GREEN**:
- G1 lint (ruff): PASS
- G2 type (mypy): PASS (320 source files, no issues)
- G3 tests (pytest): PASS — 3219 passed, 17 skipped (pre-existing PyYAML-not-installed skips,
  unrelated), 6 xfailed (pre-existing known limitations, unrelated)
- G4 no-handrolled-YAML: PASS
- G5 print discipline: PASS
- G6 complexity: PASS
- G7 canonical-library: PASS

No new findings introduced; no back-pressure cycles needed. `dart fix --apply` not applicable
(Python-only change).

## Not done in U1 (explicitly out of scope, for the next unit)

- `scripts/playground/acceptance_oracles.py` / `scripts/playground/build.py` — degeneracy inspector +
  `classify_run_outcome` narrowing (D1) — **U2**.
- `scripts/playground/build.py` — pre-flight call site, distinct doomed-spec exit code, harvestable
  stamp persistence + `-start` revalidation (D4) — **U3**.
- `scripts/playground/build_resume.py` — resume revalidation (D4) — **U4**.
- Tests for AC-18/19/22 EGP referents in `scripts/tests/test_playground_*.py` — **U5**.
- Option-A workaround retirement (D5), `contract.yaml` EGP disposition — **U6**.

No commit was made (per dispatcher instruction — "Do NOT commit").
