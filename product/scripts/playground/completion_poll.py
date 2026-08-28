"""Dynamic-interval completion polling for build-mode outer sessions (REQ-PROC-068 AC-16).

The outer build-mode/resume session learns of an in-progress child's completion by
self-polling — there is no push notification from the contained child session.
SP-4/IDEA-35 (U6) rejects a FIXED poll interval (e.g. a hard-coded 15 minutes):
a run with little estimated work left should be checked soon, and a run with a
lot of work left should not be hammered every few seconds. `compute_poll_interval`
scales the wait with the caller-supplied remaining-work estimate (e.g. remaining
ChainState units for a layer-derivation child), clamped to a sane floor/ceiling
so it neither busy-polls nor silently reverts to the old fixed 15-minute wait —
900s is deliberately kept as the CEILING, not the constant, per the plan's
"Constants / defaults" section.

`poll_until_complete` is the outer-session self-poll primitive (SOL-02 D5(a)):
it loops calling an injected `is_complete` predicate, sleeping the dynamically
computed interval in between, until complete or (optionally) a max-polls bound
is hit — the same injectable-sleep pattern as launch_adapter.py's hung-detection
loop, so tests never touch the real clock (doc/python/dependency_injection.md).
"""

# tier: B  # reusable helper; imported by playground-build-resume's completion wait

import time
from collections.abc import Callable
from dataclasses import dataclass

DEFAULT_FLOOR_SECS = 60
DEFAULT_CEILING_SECS = 900
DEFAULT_SECS_PER_UNIT = 60


def compute_poll_interval(
    remaining_units: float,
    *,
    floor_secs: int = DEFAULT_FLOOR_SECS,
    ceiling_secs: int = DEFAULT_CEILING_SECS,
    secs_per_unit: int = DEFAULT_SECS_PER_UNIT,
) -> int:
    """Scale the next poll wait to the estimated remaining work, clamped to [floor, ceiling].

    Why: a fixed-interval poll either wastes wall-clock time on a nearly-done
    run (waiting the full ceiling when one unit remains) or hammers a run with
    many units left (a short fixed interval repeated across a multi-hour
    derivation). Scaling by `remaining_units * secs_per_unit` and clamping keeps
    both ends bounded: a non-positive estimate (0, unknown-as-0, or negative)
    is treated as "check again soon" (the floor), never a shorter-than-floor
    busy-poll and never an unbounded wait past the ceiling.
    Source: requirements_tasks/process/AI_rules/factory_extraction/
      epic_skill_test_playground/tasks/2026-07-09_impl_build-mode-run-registry-and-resume/
      plans_and_protocols/2026-07-09_01_plan_run-registry-and-resume.md#Deliverable 3
    Tests: scripts/tests/test_completion_poll.py
    """
    if remaining_units <= 0:
        return floor_secs
    return max(floor_secs, min(ceiling_secs, int(remaining_units * secs_per_unit)))


@dataclass
class PollLimits:
    """Pure polling configuration (grouped to keep poll_until_complete's signature <= 5 params).

    Mirrors launch_adapter.py's SessionConfig/LaunchRequest split: interval/
    bound configuration lives here (values), the injectable sleep callable
    stays a separate parameter (a boundary, not configuration).
    """

    floor_secs: int = DEFAULT_FLOOR_SECS
    ceiling_secs: int = DEFAULT_CEILING_SECS
    secs_per_unit: int = DEFAULT_SECS_PER_UNIT
    max_polls: int | None = None  # None = poll indefinitely until is_complete


def poll_until_complete(
    is_complete: Callable[[], bool],
    remaining_units_fn: Callable[[], float],
    *,
    sleep: Callable[[float], None] = time.sleep,
    limits: PollLimits | None = None,
) -> bool:
    """Loop until `is_complete()` is True, sleeping a dynamically-scaled interval between checks.

    The outer-session self-poll primitive (AC-16, SOL-02 D5(a)): each tick calls
    `is_complete`; if not yet complete, it measures `remaining_units_fn()` and
    sleeps `compute_poll_interval(...)` before the next tick. `max_polls`
    (in `limits`) bounds the loop for tests and for any caller wanting an
    explicit give-up point; the default (None) polls indefinitely, matching a
    real outer session that has nothing else useful to do but wait.

    Args:
        is_complete: Zero-arg predicate — True when the watched run is done.
        remaining_units_fn: Zero-arg callable returning the current estimated
            remaining-work count (e.g. remaining ChainState units).
        sleep: Injectable sleep boundary (tests pass a no-op; production
            defaults to time.sleep — never mock.patch'd, per
            doc/python/testing.md's frozen-clock/sleep-injection rule).
        limits: Poll interval/bound configuration; defaults to PollLimits().

    Returns:
        True if `is_complete()` returned True before max_polls was reached;
        False if max_polls polls elapsed without completion.
    """
    cfg = limits or PollLimits()
    polls = 0
    while True:
        if is_complete():
            return True
        if cfg.max_polls is not None and polls >= cfg.max_polls:
            return False
        interval = compute_poll_interval(
            remaining_units_fn(),
            floor_secs=cfg.floor_secs,
            ceiling_secs=cfg.ceiling_secs,
            secs_per_unit=cfg.secs_per_unit,
        )
        sleep(interval)
        polls += 1
