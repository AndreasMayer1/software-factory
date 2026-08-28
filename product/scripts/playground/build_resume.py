"""Cold re-attach (read/resume side) for the Skill-Test Playground run registry (REQ-PROC-068 AC-15).

Companion to build.py's WRITE side (write_run_registry_running): a build-mode run can be killed by
a tree-wide usage limit AFTER launch but BEFORE the completion gate runs. This module lets a later,
completely fresh (cold) process discover that preserved run from the registry and re-attach to it —
reusing the PRESERVED workspace and the PERSISTED pre-child baseline — WITHOUT re-running
create_workspace / deploy_candidate / init_workspace_git / sync_product_definition /
snapshot_product_definition (build._prepare_workspace). Only the launch->gate tail
(build.launch_and_gate, the same seam a fresh run drives) is re-run.

Mirrors how `layer-derivation-resume` re-attaches a ChainState chain via
scripts/factory/layer_derivation/backfill_orchestration.py: a control skill reads the durable
file-memory (here, the run-registry record + baseline sidecar) and re-dispatches with no human
path-threading.

Why `resume` re-validates the AC-22 harvestability pre-flight before every relaunch (D4/ADV-sg-06):
    A run's spec (fixed_layers) and the layer-pair -> authoring-skill map it screens against are
    both recomputed FRESH from the record on every resume, never trusted as the persisted
    "harvestable" bool from write time — AC-22 requires "no start or resume path reaches harvest
    without a CURRENT positive pre-flight". `build.resume_run` raises `DoomedSpecError` (caught
    here, EXIT_DOOMED_SPEC) BEFORE `launch_and_gate` runs, so a spec that has become doomed since
    it was preserved can never reach harvest via a resume.

Output:
    `list` subcommand: JSON array of run-registry records to stdout (baseline sidecars excluded).
    `resume` subcommand: JSON manifest object to stdout (same shape as build.py's, minus
    seeded_paths — resume never re-seeds). Exit 0 on success; 1 if no resumable run is found or
    the resumed launch fails; EXIT_DOOMED_SPEC (2, imported from build.py) if the re-validated
    pre-flight is negative; progress/errors go to stderr via logging.
    `fence-check` subcommand: JSON array of the runs (running/preserved) that FENCE a harvest
    deposit into a given test_harness_app tree, to stdout. Exit 0 when the deposit is safe to
    consume/commit (no in-flight run targets it), FENCE_EXIT_FENCED (3) when it is fenced — the
    AC-14 gate the outer-session / task-complete commit flow calls before committing the deposit.
"""

# tier: C  # one-shot CLI, mirrors build.py's own tier despite being test-imported

import argparse
import json
import logging
import os
import sys
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any

from scripts.dev_env.worktree_root import worktree_root
from scripts.playground.build import (
    BASELINE_SIDECAR_SUFFIX,
    EXIT_DOOMED_SPEC,
    RUN_REGISTRY_DIRNAME,
    RUN_STATUS_COMPLETE,
    RUN_STATUS_PRESERVED,
    RUN_STATUS_RUNNING,
    BuildModeConfig,
    DoomedSpecError,
    LaunchAndGateInputs,
    build_acceptance_predicate,
    build_degeneracy_inspector,
    launch_and_gate,
    load_product_definition_globs,
    run_harvestability_preflight,
)
from scripts.playground.containment import ContainmentUnavailable
from scripts.playground.cost_ledger import BudgetExceeded, CostLedger
from scripts.playground.launch_adapter import LaunchDeps
from scripts.playground.workspace import destroy_workspace

_LOG = logging.getLogger(__name__)

# A run is resumable iff the gate never ran to a terminal harvest/discard yet:
# RUNNING = killed before the completion gate; PRESERVED = the gate ran and
# found the run not-yet-complete. Both leave the workspace on disk untouched.
_RESUMABLE_STATUSES = frozenset({RUN_STATUS_RUNNING, RUN_STATUS_PRESERVED})

# Key attached to a loaded record (NOT persisted) so resume_run can write the
# gate's status flip back to the record's OWN file. Deliberately NOT reusing
# the record's existing "registry_path" key -- that key already means the
# ARTIFACTS registry path (cfg.registry_path, .factory/registry/artifacts.yaml)
# inside the record itself; overloading it here would silently break
# load_product_definition_globs downstream (see resume_run).
_SOURCE_PATH_KEY = "_source_path"


# ---------------------------------------------------------------------------
# Read side
# ---------------------------------------------------------------------------


def read_run_record(path: str) -> dict[str, Any]:
    """Load one run-registry record, tagging it with its own source file path.

    The tag (`_SOURCE_PATH_KEY`) is what resume_run passes to launch_and_gate
    as `registry_path` — the run-registry record's OWN file, whose status the
    completion gate flips to complete/preserved. It is synthesized here, never
    written back to disk.
    """
    record: dict[str, Any] = json.loads(Path(path).read_text(encoding="utf-8"))
    record[_SOURCE_PATH_KEY] = str(path)
    return record


def list_runs(registry_dir: str) -> list[dict[str, Any]]:
    """Return every run-registry record under registry_dir, baseline sidecars excluded.

    Globbing `*.json` also matches a baseline sidecar (`<uuid>.baseline.json`,
    written by build.write_run_registry_running) since it too ends in `.json`;
    it is filtered out explicitly so `list`/`find_resumable_run` never
    misinterpret a content-hash baseline map as a run record. Returns an empty
    list when registry_dir does not exist (no runs recorded yet).
    """
    root = Path(registry_dir)
    if not root.is_dir():
        return []
    return [
        read_run_record(str(p))
        for p in sorted(root.glob("*.json"))
        if not p.name.endswith(BASELINE_SIDECAR_SUFFIX)
    ]


def find_resumable_run(registry_dir: str) -> dict[str, Any] | None:
    """Return the first run whose status is resumable AND whose workspace still exists on disk.

    "Resumable" = status in {running, preserved} (see _RESUMABLE_STATUSES) —
    a "complete" run already harvested+discarded and must never be re-attached.
    The on-disk workspace check guards against a stale record whose workspace
    was manually removed out-of-band. Returns None when nothing qualifies.
    """
    for record in list_runs(registry_dir):
        if record.get("status") not in _RESUMABLE_STATUSES:
            continue
        workspace_path = record.get("workspace_path")
        if not workspace_path or not Path(workspace_path).is_dir():
            continue
        return record
    return None


def load_baseline(record: dict[str, Any]) -> dict[str, str]:
    """Load the persisted pre-child baseline snapshot from the record's sidecar ref.

    The record's `baseline_snapshot_ref` points at the `<uuid>.baseline.json`
    file build.write_run_registry_running wrote alongside the record — the
    same relpath->sha256 map snapshot_product_definition would have produced,
    reused here instead of re-snapshotting (AC-15: resume never re-runs the
    prepare-workspace steps, snapshot included).
    """
    ref = record["baseline_snapshot_ref"]
    data: dict[str, str] = json.loads(Path(ref).read_text(encoding="utf-8"))
    return data


# ---------------------------------------------------------------------------
# Deposit fence (AC-14) — gate consumption/commit on verified-complete
# ---------------------------------------------------------------------------

# Exit code the `fence-check` CLI returns when the deposit is FENCED (an
# in-flight run targeting it is still running/preserved, so its test_harness_app/
# deposit may be a partial/incoherent subset). Distinct from 1 (operational
# error) so the outer commit flow can tell "unsafe to commit" from "check failed".
FENCE_EXIT_FENCED = 3


def deposit_blocking_runs(
    registry_dir: str, target_project_dir: str
) -> list[dict[str, Any]]:
    """Return the runs that FENCE a harvest deposit into target_project_dir (AC-14).

    A run fences the deposit while its registry status is still resumable
    (running or preserved) — the completion gate has NOT yet harvested+discarded,
    so test_harness_app/ may hold a partial/incoherent subset of that run's
    harvest. Only a `complete` record means the deposit is the full coherent set.
    Match is on the record's own harvest target (target_project_dir), realpath-
    normalised so a relative/absolute spelling of the same dir still matches; a
    run targeting a DIFFERENT harness tree never fences this one.
    """
    target = os.path.realpath(target_project_dir)
    blocking: list[dict[str, Any]] = []
    for record in list_runs(registry_dir):
        if record.get("status") not in _RESUMABLE_STATUSES:
            continue
        rec_target = record.get("target_project_dir")
        if rec_target and os.path.realpath(rec_target) == target:
            blocking.append(record)
    return blocking


def deposit_is_safe_to_consume(
    registry_dir: str, target_project_dir: str
) -> bool:
    """True iff NO running/preserved run targets target_project_dir (AC-14 fence).

    The load-bearing invariant behind AC-14: nothing may consume or commit the
    test_harness_app/ deposit while a run's record is running or preserved — only
    after complete. This is the single predicate the outer-session / task-complete
    commit flow gates on (exposed as the `fence-check` CLI subcommand).
    """
    return not deposit_blocking_runs(registry_dir, target_project_dir)


# ---------------------------------------------------------------------------
# Orphan-copy cleanup — reclaim a complete run's leaked workspace (AC-14 edge)
# ---------------------------------------------------------------------------


def discard_orphan_copies(registry_dir: str) -> list[str]:
    """Discard workspace copies of COMPLETE runs the gate flipped but never destroyed.

    Edge from _gate_harvest's ordering: it harvests, flips the record to
    complete, THEN destroys the copy. A crash BETWEEN the flip and the destroy
    leaves a `complete` record whose workspace_path still exists on disk — an
    orphan. Such a run has ALREADY deposited its full coherent set, so the copy
    is discarded, NEVER re-harvested (find_resumable_run already skips complete
    records, so this is the only path that reclaims the leaked copy). Returns the
    workspace paths discarded, in first-seen order.
    """
    discarded: list[str] = []
    for record in list_runs(registry_dir):
        if record.get("status") != RUN_STATUS_COMPLETE:
            continue
        workspace_path = record.get("workspace_path")
        if workspace_path and Path(workspace_path).is_dir():
            destroy_workspace(workspace_path)
            discarded.append(workspace_path)
    return discarded


# ---------------------------------------------------------------------------
# Resume — re-attach and drive the launch->gate tail (AC-15)
# ---------------------------------------------------------------------------


def resume_run(
    record: dict[str, Any],
    *,
    launch_deps: LaunchDeps | None = None,
    probe_fn: object = None,
    completion_predicate: Callable[[str], bool] | None = None,
    session_id_factory: Callable[[], str] = lambda: str(uuid.uuid4()),
) -> dict[str, Any]:
    """Re-attach a preserved/running build-mode run and drive it through the completion gate.

    Reconstructs a BuildModeConfig from the record ALONE (no second input —
    the record carries prompt, jsonl_dir, registry_path, workspace_root, and
    max_budget_usd, per build.write_run_registry_running's Deliverable-1
    enrichment) and calls build.launch_and_gate with the RECORDED
    workspace_path/jsonl_dir/baseline.

    This function NEVER calls build._prepare_workspace, and therefore never
    calls create_workspace / deploy_candidate / init_workspace_git /
    sync_product_definition / snapshot_product_definition — AC-15 requires a
    cold re-attach to skip deploy/seed/snapshot entirely and reuse exactly
    what the original (killed) run already produced.

    ``session_id_factory`` mints the child CLI session-id for this relaunch;
    it is injectable so tests can assert a fresh id per relaunch deterministically.

    Raises:
        DoomedSpecError: the AC-22 harvestability pre-flight, RECOMPUTED from the
            record's persisted fixed_layers (never trusted as a stored bool —
            D4/ADV-sg-06 requires a CURRENT verdict), is negative. Raised BEFORE
            launch_and_gate — a doomed resume never reaches the launch->gate tail,
            so it can never reach harvest (AC-22: "no start or resume path
            reaches harvest without a current positive pre-flight").
    """
    # Mint a FRESH child session-id for each relaunch. The record's original
    # session_uuid was already consumed by the interrupted child, and the Claude
    # CLI rejects a reused --session-id ("Session ID <uuid> is already in use.")
    # with EMPTY stdout, which build.py then surfaces as "Invalid JSON envelope"
    # — so before this fix EVERY resume of an already-launched run died here
    # (REQ-PROC-068 AC-15, TASK-PROC-068-23). Only the child CLI session id must
    # be new; the run's durable identity (registry key, workspace name, baseline
    # sidecar) stays the record's original session_uuid, untouched below.
    child_session_uuid = session_id_factory()
    cfg = BuildModeConfig(
        target_project_dir=record["target_project_dir"],
        host_project_dir=record["host_project_dir"],
        workspace_root=record["workspace_root"],
        session_uuid=child_session_uuid,
        prompt=record["prompt"],
        jsonl_dir=record["jsonl_dir"],
        max_budget_usd=record["max_budget_usd"],
        model=record["model"],
        registry_path=record["registry_path"],
        # Reconstruct the SAME acceptance oracle the original run used, from the
        # record alone (write_run_registry_running persisted it) — so a resumed
        # layer-derivation run still certifies completion via its ChainState
        # oracle rather than defaulting to the INCONCLUSIVE fail-safe (AC-19).
        acceptance_oracle_kind=record.get("acceptance_oracle_kind", ""),
        chain_state_path=record.get("chain_state_path", ""),
        fixed_layers=tuple(record.get("fixed_layers") or ()),
    )

    # AC-22/D4: RE-VALIDATE the pre-flight verdict on EVERY resume path, before
    # anything can reach harvest — never trust the record's persisted
    # "harvestable" bool as-is (it was true AT WRITE TIME; the spec/registered
    # authoring skills could have changed since). Reuses run_harvestability_preflight
    # — the SAME predicate run_build_mode's "-start" path gates on — so start and
    # resume can never disagree (one implementation).
    harvestable, preflight_errors = run_harvestability_preflight(cfg.fixed_layers)
    if not harvestable:
        raise DoomedSpecError(preflight_errors)

    globs = load_product_definition_globs(cfg.registry_path)
    baseline = load_baseline(record)
    ledger = CostLedger(max_budget_usd=cfg.max_budget_usd)

    # An explicitly-injected predicate (tests) wins; otherwise rebuild it from the
    # record's oracle spec so resume and fresh-run share one gate contract.
    if completion_predicate is None:
        completion_predicate = build_acceptance_predicate(cfg)

    manifest = launch_and_gate(
        cfg,
        LaunchAndGateInputs(
            workspace=record["workspace_path"],
            globs=globs,
            baseline=baseline,
            registry_path=record[_SOURCE_PATH_KEY],
            jsonl_dir=cfg.jsonl_dir,
            ledger=ledger,
            # Same AC-18 D1 seam a fresh run wires (build_degeneracy_inspector) —
            # resume must not lose the ABANDONED-vs-INCONCLUSIVE narrowing.
            degeneracy_inspector=build_degeneracy_inspector(cfg),
        ),
        launch_deps=launch_deps,
        probe_fn=probe_fn,
        completion_predicate=completion_predicate,
    )
    # seeded_paths is a fresh-run-only concept (the seed step never runs on a
    # resume, AC-15) — set explicitly so the manifest shape stays consistent
    # with build.run_build_mode's, rather than silently omitting the key.
    manifest["seeded_paths"] = []
    return manifest


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _default_registry_dir() -> str:
    """The default durable run-registry dir: <worktree_root>/.playground_runs."""
    return os.path.join(str(worktree_root()), RUN_REGISTRY_DIRNAME)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Read/resume side of the build-mode run registry: discover an "
            "in-progress run and re-attach without re-deploying (AC-15)."
        )
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser(
        "list", help="List run-registry records (baseline sidecars excluded)."
    )
    p_list.add_argument(
        "--registry-dir",
        default=None,
        help="Durable run-registry dir. Defaults to <worktree_root>/.playground_runs.",
    )

    p_resume = sub.add_parser(
        "resume",
        help=(
            "Find the resumable run and re-attach it, skipping "
            "deploy/seed/snapshot entirely (AC-15)."
        ),
    )
    p_resume.add_argument(
        "--registry-dir",
        default=None,
        help="Durable run-registry dir. Defaults to <worktree_root>/.playground_runs.",
    )

    p_fence = sub.add_parser(
        "fence-check",
        help=(
            "Gate the harvest deposit (AC-14): exit 0 if safe to consume/commit "
            "(no running/preserved run targets it), exit 3 if FENCED."
        ),
    )
    p_fence.add_argument(
        "--target-project-dir",
        required=True,
        help="Absolute path to test_harness_app (the harvest deposit to fence-check).",
    )
    p_fence.add_argument(
        "--registry-dir",
        default=None,
        help="Durable run-registry dir. Defaults to <worktree_root>/.playground_runs.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns exit code."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [playground-build-resume] %(levelname)s %(message)s",
        stream=sys.stderr,
    )

    parser = _build_parser()
    args = parser.parse_args(argv)
    registry_dir = args.registry_dir or _default_registry_dir()

    try:
        if args.command == "list":
            records = list_runs(registry_dir)
            print(json.dumps(records, indent=2))  # documented CLI output contract (see module docstring)
            return 0

        if args.command == "fence-check":
            blocking = deposit_blocking_runs(registry_dir, args.target_project_dir)
            print(json.dumps(blocking, indent=2))  # documented CLI output contract (see module docstring)
            return FENCE_EXIT_FENCED if blocking else 0

        # args.command == "resume" (the only other subparser choice).
        # Reclaim any orphaned copy (complete record whose workspace was never
        # destroyed — crash between the gate's flip and destroy_workspace, AC-14
        # edge) before searching for a resumable run.
        discard_orphan_copies(registry_dir)
        record = find_resumable_run(registry_dir)
        if record is None:
            _LOG.error("No resumable build-mode run found in %s", registry_dir)
            return 1
        manifest = resume_run(record)
        print(json.dumps(manifest, indent=2))  # documented CLI output contract (see module docstring)
        return 0

    except DoomedSpecError as exc:
        # AC-22/D4: caught BEFORE the generic RuntimeError clause below
        # (DoomedSpecError subclasses RuntimeError) — a resume whose recomputed
        # pre-flight verdict is negative must return the SAME distinct exit code
        # build.py's own doomed-spec rejection returns, never the generic 1.
        _LOG.error("Resume blocked — pre-flight rejected before harvest: %s", exc)
        return EXIT_DOOMED_SPEC
    except BudgetExceeded as exc:
        _LOG.error("Budget cap exceeded: %s", exc)
        return 1
    except ContainmentUnavailable as exc:
        _LOG.error("Containment unavailable: %s", exc)
        return 1
    except (OSError, ValueError, RuntimeError, KeyError) as exc:
        _LOG.error("Resume failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
