"""Concrete acceptance oracles + harvestability pre-flight boundary calls for
build/maintain-mode (REQ-PROC-068 AC-18/AC-19/AC-22).

build.py's completion gate is parameterized by INJECTED predicates (AC-17): a
`Callable[[str], bool]` acceptance oracle over the isolated-copy path answering
"did the derivation actually finish?", and a `Callable[[str], bool]`
structural-degeneracy inspector answering "is at least one unit with REAL
authoring pairs left non-terminal?" (the AC-18 ABANDONED-vs-INCONCLUSIVE
narrowing, D1). Both are wired in by `build.main()` (or a cold resume
reconstructing them from the run-registry record). This module also hosts the
single boundary call into `backfill_orchestration.harvestability_preflight`
(AC-22) that `build.run_harvestability_preflight` delegates to — the SAME
teaching-linter object `layer-derivation-start` calls at author time (one
implementation, no drift).

Why this module is separate from build.py:
  Keeping the ChainState-specific oracle, inspector, and pre-flight call OUT of
  build.py preserves AC-17's "layer-derivation is one instance, not the
  hard-coded case" property — build.py never imports layer-derivation, so
  `"ChainState" not in dir(build)` holds. The layer_derivation package uses flat
  sibling imports (`import anchor_span_engine`) that require its own directory
  on sys.path, so the import is done here (and only here) with the same
  sys.path convention the layer-derivation tests use.
"""

# tier: B  # reusable library; imported by build.py's oracle/pre-flight wiring + tested directly

import sys
from collections.abc import Callable, Sequence
from pathlib import Path

# The layer_derivation package resolves its siblings (anchor_span_engine, …) by
# directory-on-sys.path rather than as a dotted package, so importing
# backfill_orchestration requires its directory on sys.path first — the same
# convention scripts/tests/test_backfill_orchestration.py uses.
_LAYER_DERIVATION_DIR = (
    Path(__file__).resolve().parent.parent / "factory" / "layer_derivation"
)


def chainstate_complete_predicate(
    chain_state_relpath: str,
) -> Callable[[str], bool]:
    """Build a completion predicate that is True iff the copy's ChainState is fully derived.

    The returned predicate loads the layer-derivation ChainState file at
    ``<workspace>/<chain_state_relpath>`` and returns True only when EVERY unit is
    in a COMPLETED terminal — DONE (authored + content-gated) OR VACUOUS_COMPLETE
    (a structurally zero-authoring-pair no-op span, REQ-PROC-071-06 AC-09). Treating
    the union of DONE and VACUOUS_COMPLETE as "derivation finished" is deliberate: a mandatory no-op
    span has nothing to author, so a chain whose only non-DONE units are vacuous IS
    finished. A PENDING unit (child stopped early) or an ESCALATED unit (a real
    blocker) still means the derivation did NOT finish, so an all-escalated chain
    reports not-complete — the gate never harvests an unfinished, escalation-blocked
    derivation. A missing chain-state file also returns False (cannot confirm
    completion → not complete).

    Args:
        chain_state_relpath: Path to the ChainState JSON file RELATIVE to the
            isolated-copy root (the workspace the gate hands the predicate).

    Returns:
        A `Callable[[str], bool]` suitable as build.py's `completion_predicate`.
    """

    def _predicate(workspace: str) -> bool:
        state_path = Path(workspace) / chain_state_relpath
        if not state_path.is_file():
            return False
        # Lazy sys.path insert + import so build.py never couples to the
        # layer_derivation package at module import time (AC-17).
        if str(_LAYER_DERIVATION_DIR) not in sys.path:
            sys.path.insert(0, str(_LAYER_DERIVATION_DIR))
        import backfill_orchestration as bo  # type: ignore[import-not-found]  # runtime sys.path insert above; flat-sibling convention

        state = bo.load_chain(state_path)
        if not state.units:
            return False
        completed_terminals = (bo.UnitStatus.DONE, bo.UnitStatus.VACUOUS_COMPLETE)
        return all(unit.status in completed_terminals for unit in state.units)

    return _predicate


def real_authoring_unfinished_predicate(
    chain_state_relpath: str,
) -> Callable[[str], bool]:
    """Build the AC-18 structural-degeneracy inspector for classify_run_outcome's D1 narrowing.

    Answers: "is at least one unit with REAL authoring pairs (i.e. NOT a
    structurally zero-authoring-pair span) left short of a completion-satisfying
    terminal (DONE or VACUOUS_COMPLETE)?" AC-18 narrows *abandoned* to require at
    least one such real-authoring unit non-terminal; a run whose only unfinished
    units are structurally degenerate no-op spans must never be blamed on the
    skill under test (a mandatory no-op span the spec structure forced is not a
    completion failure of the skill).

    Why `vacuous_proof is None` is the real-authoring test:
        `UnitEntry.vacuous_proof` is set ONLY by the mechanism's own structural
        zero-authoring-pair proof (plan_chain / the R2 anchor proof), never by a
        caller or a child session — a unit WITH authoring pairs always carries
        `vacuous_proof=None` (backfill_orchestration.py:356-361). `load_chain`
        (called below) already migrates a legacy un-migrated degenerate span
        (parked at PENDING/ESCALATED without the stamp, D1's "in practice this
        state is only reachable from legacy un-migrated state") to
        VACUOUS_COMPLETE wherever the migration heuristic can prove degeneracy;
        an ambiguous case migrate_chain leaves un-migrated is therefore treated
        as real-authoring here too — the SAME fail-safe direction the inspector
        as a whole is built on (bias toward "may be unfinished", never toward a
        false "nothing real is unfinished").

    A missing or unreadable ChainState file fails SAFE — returns True — so an
    unreadable/absent state can never silently downgrade a run from ABANDONED to
    INCONCLUSIVE; INCONCLUSIVE must be provably reached (a proven-vacuous
    remainder), not merely defaulted to on missing evidence.

    Args:
        chain_state_relpath: Path to the ChainState JSON file RELATIVE to the
            isolated-copy root (the workspace the gate hands the predicate).

    Returns:
        A `Callable[[str], bool]` suitable as build.py's `degeneracy_inspector`.

    Source: requirements_tasks/process/AI_rules/factory_extraction/
        epic_skill_test_playground/tasks/
        2026-07-15_impl_harvestability-preflight-and-vacuous-classification/
        plans_and_protocols/2026-07-18_01_plan_preflight-and-classification.md#d1
    Tests: scripts/tests/test_playground_acceptance_oracles.py
    """

    def _inspector(workspace: str) -> bool:
        state_path = Path(workspace) / chain_state_relpath
        if not state_path.is_file():
            return True
        # Lazy sys.path insert + import so build.py never couples to the
        # layer_derivation package at module import time (AC-17).
        if str(_LAYER_DERIVATION_DIR) not in sys.path:
            sys.path.insert(0, str(_LAYER_DERIVATION_DIR))
        import backfill_orchestration as bo  # runtime sys.path insert above; flat-sibling convention (mypy already resolves this module via chainstate_complete_predicate's import above, so no import-not-found suppression is needed here)

        try:
            state = bo.load_chain(state_path)
        except (OSError, ValueError, KeyError, TypeError):
            # Malformed/unreadable state — cannot confirm degeneracy shape, so
            # fail safe (same direction as the missing-file branch above).
            return True
        completed_terminals = (bo.UnitStatus.DONE, bo.UnitStatus.VACUOUS_COMPLETE)
        return any(
            unit.vacuous_proof is None and unit.status not in completed_terminals
            for unit in state.units
        )

    return _inspector


def harvestability_preflight_verdict(
    fixed_layers: Sequence[str],
) -> tuple[bool, tuple[str, ...]]:
    """Boundary call into `backfill_orchestration.harvestability_preflight` (AC-22).

    Parses each raw layer-name string into the layer_derivation package's own
    `Layer` enum, then calls the SAME `lint_spec`/`harvestability_preflight`
    object `layer-derivation-start` calls at author time — one implementation,
    author-time and plan-time can never drift (see backfill_orchestration.py's
    own module docstring for the spec-authoring surface, AC-10).

    Args:
        fixed_layers: Raw fixed_layers name strings from a build/maintain spec.

    Returns:
        `(predicted_harvestable, errors)` — errors is empty iff predicted_harvestable
        is True. An unknown layer name is reported as a single error and
        `predicted_harvestable=False` (a spec that cannot even resolve its
        layers is doomed, same fail-safe direction as every other pre-flight
        rejection).
    """
    if str(_LAYER_DERIVATION_DIR) not in sys.path:
        sys.path.insert(0, str(_LAYER_DERIVATION_DIR))
    import backfill_orchestration as bo  # runtime sys.path insert above; flat-sibling convention (mypy already resolves this module via chainstate_complete_predicate's import above, so no import-not-found suppression is needed here)

    try:
        layers = [bo.Layer(name) for name in fixed_layers]
    except ValueError as exc:
        return False, (f"unknown layer name in fixed_layers: {exc}",)
    result = bo.harvestability_preflight(layers)
    return result.predicted_harvestable, result.errors
