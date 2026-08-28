"""Cost ledger for Skill-Test Playground child sessions.

Parses the JSON envelope emitted by `claude -p --output-format json` and
accumulates per-run cost + duration into a ledger.  Enforces a hard
max_budget_usd cap: emits a WARNING when a run would exceed the cap and
refuses to start the run if the cumulative spend already exceeds it.

JSON envelope shape (verified PASS in TASK-PROC-073-01-01 spike):
  {
    "total_cost_usd": 0.2706,
    "duration_ms": 12345,
    ...
  }

Why a hard cap rather than a soft warning:
  An unbounded test run against the real claude API can accumulate
  significant cost before an operator notices.  The cap makes the budget
  explicit and requires a conscious decision to raise it.
  Source: TASK-PROC-068-04 goal.md#AC-08

ADVISORY: Skeleton-stage regression verdicts are ADVISORY pending the
~100 paired-fixture validity floor (T-corpus + T-maturity).  This ledger
records costs faithfully but consumers must not treat single-run results
as statistically significant.
"""

# tier: B  # reusable library imported by run_skeleton; no long-lived state

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

_LOG = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ADVISORY_NOTE = (
    "ADVISORY: Skeleton-stage regression verdicts are ADVISORY pending the "
    "~100 paired-fixture validity floor (T-corpus + T-maturity will address)."
)

_COST_KEY = "total_cost_usd"
_DURATION_KEY = "duration_ms"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class RunCost:
    """Cost record for a single child session run."""

    run_id: str
    total_cost_usd: float
    duration_ms: int
    timestamp: str  # local-timezone ISO string


@dataclass
class CostLedger:
    """Accumulates cost records across multiple runs within a budget cap."""

    max_budget_usd: float
    runs: list[RunCost] = field(default_factory=list)

    @property
    def total_cost_usd(self) -> float:
        """Sum of all recorded run costs."""
        return sum(r.total_cost_usd for r in self.runs)

    @property
    def total_duration_ms(self) -> int:
        """Sum of all recorded run durations in milliseconds."""
        return sum(r.duration_ms for r in self.runs)

    @property
    def is_over_budget(self) -> bool:
        """True if cumulative cost exceeds max_budget_usd."""
        return self.total_cost_usd > self.max_budget_usd

    def to_dict(self) -> dict[str, Any]:
        """Serialise ledger to a JSON-compatible dict with advisory note."""
        return {
            "advisory": ADVISORY_NOTE,
            "max_budget_usd": self.max_budget_usd,
            "total_cost_usd": round(self.total_cost_usd, 6),
            "total_duration_ms": self.total_duration_ms,
            "over_budget": self.is_over_budget,
            "run_count": len(self.runs),
            "runs": [
                {
                    "run_id": r.run_id,
                    "total_cost_usd": r.total_cost_usd,
                    "duration_ms": r.duration_ms,
                    "timestamp": r.timestamp,
                }
                for r in self.runs
            ],
        }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


class BudgetExceeded(RuntimeError):
    """Raised when the cumulative cost already exceeds max_budget_usd.

    Why raised rather than warned:
      A soft warning would allow the run to proceed even after the budget
      is exhausted.  A hard exception ensures the operator is notified and
      must explicitly raise the cap or stop the run.
    """

    def __init__(self, spent: float, cap: float) -> None:
        self.spent = spent
        self.cap = cap
        super().__init__(
            f"Budget cap exceeded: spent ${spent:.4f} of ${cap:.4f} max. "
            "Raise max_budget_usd or stop the run."
        )


def parse_cost_envelope(json_output: str) -> tuple[float, int]:
    """Parse total_cost_usd and duration_ms from claude JSON output.

    Args:
        json_output: Raw stdout from `claude -p --output-format json`.

    Returns:
        Tuple of (total_cost_usd, duration_ms).

    Raises:
        ValueError: If required keys are missing or the JSON is malformed.
    """
    try:
        data = json.loads(json_output)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON envelope from claude: {exc}") from exc

    missing = [k for k in (_COST_KEY, _DURATION_KEY) if k not in data]
    if missing:
        raise ValueError(
            f"Claude JSON envelope missing required keys: {missing}. "
            f"Got keys: {list(data.keys())}"
        )

    cost = float(data[_COST_KEY])
    duration = int(data[_DURATION_KEY])
    return cost, duration


def check_budget(ledger: CostLedger) -> None:
    """Raise BudgetExceeded if the ledger is already over budget.

    Call this BEFORE launching a new run to gate on cumulative spend.

    Args:
        ledger: The current cost ledger.

    Raises:
        BudgetExceeded: If ledger.total_cost_usd > ledger.max_budget_usd.
    """
    if ledger.is_over_budget:
        raise BudgetExceeded(ledger.total_cost_usd, ledger.max_budget_usd)


def record_run(
    ledger: CostLedger,
    run_id: str,
    json_output: str,
) -> RunCost:
    """Parse JSON envelope, warn if this run pushes over budget, append to ledger.

    Args:
        ledger: The ledger to append the run to.
        run_id: Unique identifier for this run (e.g. session UUID).
        json_output: Raw stdout from `claude -p --output-format json`.

    Returns:
        The RunCost record that was appended.

    Side-effects:
        Logs a WARNING if the new cumulative total exceeds max_budget_usd.
        Does NOT raise BudgetExceeded here — the run already completed;
        use check_budget() BEFORE launching to prevent over-budget starts.
    """
    cost, duration = parse_cost_envelope(json_output)
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
    run = RunCost(
        run_id=run_id,
        total_cost_usd=cost,
        duration_ms=duration,
        timestamp=timestamp,
    )
    ledger.runs.append(run)

    if ledger.is_over_budget:
        _LOG.warning(
            "WARNING: budget cap exceeded after run %s. "
            "Cumulative cost: $%.4f / $%.4f max.",
            run_id,
            ledger.total_cost_usd,
            ledger.max_budget_usd,
        )

    return run
