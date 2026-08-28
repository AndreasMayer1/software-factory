"""Walking skeleton: deploy → run → git-reset → cost for the Skill-Test Playground.

Single fixture, single-cell loop.  Orchestrates:
  0. create_workspace()  — copy the persistent test_harness_app seed into a
                           throwaway workspace dir (under the host project's
                           gitignored .worktree/)
  1. deploy_candidate()  — snapshot the whole host factory into the workspace
  1b. init_workspace_git() — git-init the workspace as its own repo (reset baseline)
  2. check_budget()      — gate on cumulative spend before each run
  3. run_with_hung_detection() inside wrap_with_containment() — child session
  4. record_run()        — parse cost+duration from JSON envelope
  5. reset_harness()     — git-reset the workspace to its baseline commit
  6. destroy_workspace() — remove the workspace (always, via try/finally)
  7. emit ledger         — JSON to stdout with ADVISORY note

Why the ephemeral workspace (TASK-PROC-068-11): the persistent test_harness_app
tree lives IN-TREE under the host factory project and is not its own git repo
— `git reset --hard` there would resolve to the ENCLOSING flutter_app repo.
Each run instead deploys/executes/resets against a throwaway, git-initialized
workspace seeded from test_harness_app; the persistent tree is only ever read
from (create_workspace), never reset or deployed into.  See
scripts/playground/workspace.py's module docstring for the full rationale.

ADVISORY: Skeleton-stage regression verdicts are ADVISORY pending the
~100 paired-fixture validity floor (T-corpus + T-maturity will address).

Output contract:
  Prints one JSON object to stdout:
    {
      "advisory": "ADVISORY: ...",
      "max_budget_usd": <float>,
      "total_cost_usd": <float>,
      "total_duration_ms": <int>,
      "over_budget": <bool>,
      "run_count": <int>,
      "runs": [ { "run_id": ..., "total_cost_usd": ..., ... } ]
    }
  Writes progress/errors to stderr via logging.
  Exit 0 on success, 1 on error.

Usage:
    python3 scripts/playground/run_skeleton.py \\
        --harness-dir /path/to/test_harness_app \\
        --host-project-dir /path/to/flutter_app \\
        --session-uuid <uuid> \\
        --prompt "Invoke the claude-automated-mode skill..." \\
        [--jsonl-dir /path/to/jsonl/dir] \\
        [--max-budget-usd 1.00] \\
        [--model claude-sonnet-4-5]
"""

# tier: C  # one-shot CLI; no imported callers outside tests

import argparse
import json
import logging
import os
import sys
import uuid as _uuid_mod
from dataclasses import dataclass
from typing import Any

from scripts.playground.containment import (
    AuthConfigUnavailable,
    ContainmentUnavailable,
    wrap_with_containment,
)
from scripts.playground.cost_ledger import (
    BudgetExceeded,
    CostLedger,
    check_budget,
    record_run,
)
from scripts.playground.deploy import deploy_candidate
from scripts.playground.launch_adapter import (
    LaunchDeps,
    LaunchRequest,
    run_with_hung_detection,
)
from scripts.playground.reset import HarnessNotClean, HarnessNotOwnRepo, reset_harness
from scripts.playground.workspace import (
    WorkspaceError,
    create_workspace,
    destroy_workspace,
    init_workspace_git,
)

_LOG = logging.getLogger(__name__)

DEFAULT_MAX_BUDGET_USD = 2.00
DEFAULT_MODEL = "claude-sonnet-4-5"


# ---------------------------------------------------------------------------
# Fixture configuration (groups params to stay within PLR0913 ≤ 5)
# ---------------------------------------------------------------------------


@dataclass
class FixtureConfig:
    """Configuration for a single-fixture skeleton run.

    Why a dataclass: run_single_fixture had 9 parameters (PLR0913 violation: >5).
    These fields are all fixture-level configuration, not independent concerns.
    Grouping them into FixtureConfig reduces the public signature to ≤5 params.
    """

    harness_dir: str
    host_project_dir: str
    session_uuid: str
    prompt: str
    # None means "derive the default from the ephemeral workspace path once
    # it exists" (see run_single_fixture Step 5) — the workspace does not
    # exist yet when the CLI parses --jsonl-dir, so the default can no longer
    # be resolved at parse time (TASK-PROC-068-11 Change 4).
    jsonl_dir: str | None = None
    max_budget_usd: float = DEFAULT_MAX_BUDGET_USD
    model: str = DEFAULT_MODEL


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Walking skeleton: deploy → run → reset → cost (single fixture)."
    )
    p.add_argument(
        "--harness-dir",
        required=True,
        help=(
            "Absolute path to the persistent test_harness_app product tree "
            "(seed for the ephemeral run workspace). NOT a git repository "
            "and no longer the reset target — each run copies it into a "
            "throwaway workspace that IS git-initialized and IS reset."
        ),
    )
    p.add_argument(
        "--host-project-dir",
        required=True,
        help="Absolute path to the host factory project (source of .claude/skills/).",
    )
    p.add_argument(
        "--session-uuid",
        default=None,
        help="Pre-assigned session UUID.  Defaults to a fresh uuid4.",
    )
    p.add_argument(
        "--prompt",
        required=True,
        help="Prompt passed to claude -p.",
    )
    p.add_argument(
        "--jsonl-dir",
        default=None,
        help=(
            "Directory where the child session writes its JSONL file.  "
            "Defaults to the CCS shared context-groups path for the ephemeral "
            "run workspace (not --harness-dir; the child's cwd is the workspace)."
        ),
    )
    p.add_argument(
        "--max-budget-usd",
        type=float,
        default=DEFAULT_MAX_BUDGET_USD,
        help=f"Hard budget cap in USD.  Default: {DEFAULT_MAX_BUDGET_USD}.",
    )
    p.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Claude model to use.  Default: {DEFAULT_MODEL}.",
    )
    return p


# ---------------------------------------------------------------------------
# Core loop (extracted for testability — pure logic, injectable deps)
# ---------------------------------------------------------------------------


def run_single_fixture(
    cfg: FixtureConfig,
    *,
    launch_deps: LaunchDeps | None = None,
    probe_fn: object = None,
) -> dict[str, Any]:
    """Deploy → run → reset → cost for one fixture.  Returns ledger dict.

    Injectable launch_deps and probe_fn allow tests to mock subprocess calls.

    Args:
        cfg: Fixture configuration (harness paths, prompt, budget, model).
        launch_deps: Injectable I/O boundaries for the child session launcher.
        probe_fn: Injectable containment probe for tests.
    """
    ledger = CostLedger(max_budget_usd=cfg.max_budget_usd)

    # Step 0: create the ephemeral run workspace, seeded from the persistent
    # test_harness_app tree.  Everything below runs against `workspace`, never
    # against cfg.harness_dir directly (TASK-PROC-068-11 Change 4) — see
    # scripts/playground/workspace.py's module docstring for why.
    _LOG.info("Step 0: creating ephemeral workspace from %s", cfg.harness_dir)
    workspace = create_workspace(cfg.host_project_dir, cfg.harness_dir, cfg.session_uuid)

    try:
        # Step 1: deploy candidate factory into the workspace
        _LOG.info("Step 1: deploying candidate factory into %s", workspace)
        deploy_candidate(cfg.host_project_dir, workspace)

        # Step 1b: make the workspace its own git repo — the baseline
        # reset_harness() restores to after the child session runs.
        _LOG.info("Step 1b: git-init workspace baseline: %s", workspace)
        init_workspace_git(workspace)

        # Step 2: gate on budget before launching
        _LOG.info("Step 2: checking budget (cap: $%.4f)", cfg.max_budget_usd)
        check_budget(ledger)

        # Step 3: build contained child command
        base_cmd = _build_claude_cmd(cfg.session_uuid, cfg.prompt, cfg.model)
        kwargs: dict[str, object] = {}
        if probe_fn is not None:
            kwargs["probe_fn"] = probe_fn
        contained_cmd = wrap_with_containment(base_cmd, workspace, **kwargs)  # type: ignore[arg-type]  # probe_fn type-erasure intentional for test injection

        # Step 4: child env keeps the REAL HOME and inherited
        # CLAUDE_CONFIG_DIR (AC-12) — NOT scrub_env's workspace redirect.
        # Why: the jail now binds ~/.claude (+ ~/.ccs, if present) at their
        # real absolute paths (containment._auth_config_binds), so the child
        # can only authenticate if HOME still points at the real home
        # (/home/vscode) and CLAUDE_CONFIG_DIR still names the active CCS
        # account instance — both of which `dict(os.environ)` inherits
        # unchanged from the parent. Redirecting HOME to the workspace (as
        # scrub_env does) would make native `claude` AND `ccs` look for
        # config under the workspace, where neither exists, and both would
        # fail with "Not logged in" even though the binds are present.
        child_env = dict(os.environ)

        # Step 5: launch child session.  jsonl_dir defaults to the CCS path
        # derived from the workspace (the child's actual cwd) — not from
        # cfg.harness_dir, which the child never runs in.
        jsonl_dir = cfg.jsonl_dir or _derive_jsonl_dir(workspace)
        _LOG.info("Step 3: launching child session %s", cfg.session_uuid[:8])
        result = run_with_hung_detection(
            LaunchRequest(
                cmd=contained_cmd,
                env=child_env,
                session_uuid=cfg.session_uuid,
                jsonl_dir=jsonl_dir,
            ),
            deps=launch_deps,
        )
        _LOG.info(
            "Child session finished: rc=%d reason=%s", result.returncode, result.reason
        )

        # Step 6: record cost from stdout JSON envelope
        _LOG.info("Step 4: recording cost")
        record_run(ledger, cfg.session_uuid, result.stdout)

        # Step 7: git-reset the workspace to its baseline commit (AC-07).
        # Safe now: the workspace IS its own repo root (reset.py's own-repo
        # guard would refuse cfg.harness_dir, which is not).
        _LOG.info("Step 5: resetting workspace to clean state")
        reset_harness(workspace)
        _LOG.info("Workspace reset complete")

        return ledger.to_dict()
    finally:
        # Always torn down — a crash mid-run must never leave a
        # `playground_ws_*` directory (or, worse, a half-run) behind.
        destroy_workspace(workspace)


def _build_claude_cmd(session_uuid: str, prompt: str, model: str) -> list[str]:
    """Build the claude -p command list for a child session."""
    return [
        "claude",
        "--dangerously-skip-permissions",
        "--output-format", "json",
        "--model", model,
        "--session-id", session_uuid,
        "-p", prompt,
    ]


def _derive_jsonl_dir(run_dir: str) -> str:
    """Derive the CCS JSONL directory for the child's cwd (run_dir).

    Why: CCS names the project directory by replacing '/' with '-' in the
    absolute path of the child's cwd.  The playground needs to watch the
    child's JSONL in this derived directory for hung-detection.  run_dir is
    the ephemeral workspace (TASK-PROC-068-11), not cfg.harness_dir — the
    child never runs with harness_dir as its cwd.  The base CCS path itself
    ("/home/vscode/.ccs/...") is NOT derived from the child's HOME env var —
    it is a fixed constant (AC-12 keeps the child's HOME as the real host
    home anyway), so only the project-name segment tracks run_dir.
    """
    # Convert absolute path to CCS project-directory name convention
    normalized = run_dir.rstrip("/")
    ccs_project_name = normalized.replace("/", "-")
    return os.path.join(
        "/home/vscode/.ccs/shared/context-groups/default/projects",
        ccs_project_name,
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """CLI entry point.  Returns exit code."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [playground] %(levelname)s %(message)s",
        stream=sys.stderr,
    )

    parser = _build_parser()
    args = parser.parse_args(argv)

    session_uuid = args.session_uuid or str(_uuid_mod.uuid4())

    cfg = FixtureConfig(
        harness_dir=args.harness_dir,
        host_project_dir=args.host_project_dir,
        session_uuid=session_uuid,
        prompt=args.prompt,
        # None (not resolved here) — the ephemeral workspace this would
        # derive from does not exist until run_single_fixture creates it.
        jsonl_dir=args.jsonl_dir,
        max_budget_usd=args.max_budget_usd,
        model=args.model,
    )

    try:
        ledger_dict = run_single_fixture(cfg)
        print(json.dumps(ledger_dict, indent=2))  # documented CLI output contract (see module docstring Output:)
        return 0

    except BudgetExceeded as exc:
        _LOG.error("Budget cap exceeded: %s", exc)
        return 1
    except ContainmentUnavailable as exc:
        _LOG.error("Containment unavailable: %s", exc)
        return 1
    except AuthConfigUnavailable as exc:
        _LOG.error("Auth config unavailable: %s", exc)
        return 1
    except HarnessNotOwnRepo as exc:
        _LOG.error("Reset target is not its own git repo: %s", exc)
        return 1
    except HarnessNotClean as exc:
        _LOG.error("Harness not clean after reset: %s", exc)
        return 1
    except WorkspaceError as exc:
        _LOG.error("Ephemeral workspace lifecycle failed: %s", exc)
        return 1
    except (OSError, ValueError, RuntimeError) as exc:
        _LOG.error("Skeleton run failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
