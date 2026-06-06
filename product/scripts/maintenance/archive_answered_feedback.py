#!/usr/bin/env python3
"""Prune answered_feedback entries older than N days.

Walks automation/answered_feedback/ and deletes subdirectories (one per TASK-ID)
whose mtime exceeds the age threshold. Git preserves full history.

Output: summary line to stdout: "Examined N entries — deleted M."
"""
# tier: C  # one-shot maintenance CLI, no imported callers, single-purpose invocation

from __future__ import annotations

import argparse
import shutil
from datetime import datetime, timedelta
from pathlib import Path

DEFAULT_DAYS = 30
DEFAULT_ANSWERED_DIR = "automation/answered_feedback"


def _entry_mtime(entry: Path) -> datetime:
    try:
        return datetime.fromtimestamp(entry.stat().st_mtime).astimezone()
    except OSError:
        mtimes = [
            datetime.fromtimestamp(f.stat().st_mtime).astimezone()
            for f in entry.rglob("*")
            if f.is_file()
        ]
        return max(mtimes) if mtimes else datetime.fromtimestamp(0).astimezone()


def collect_stale_entries(answered_dir: Path, threshold_dt: datetime) -> list[Path]:
    """Return subdirs of answered_dir whose mtime is older than threshold_dt."""
    if not answered_dir.is_dir():
        raise FileNotFoundError(f"answered_feedback dir not found: {answered_dir}")
    return [
        entry
        for entry in sorted(answered_dir.iterdir())
        if entry.is_dir() and _entry_mtime(entry) < threshold_dt
    ]


def prune_entries(entries: list[Path], *, dry_run: bool, verbose: bool) -> int:
    """Delete or report stale entries. Returns count processed."""
    count = 0
    for entry in entries:
        if verbose or dry_run:
            prefix = "[dry-run] would delete" if dry_run else "deleting"
            print(f"  {prefix}: {entry.name}")
        if not dry_run:
            shutil.rmtree(entry)
        count += 1
    return count


def archive_answered_feedback(
    answered_dir: Path, *, days: int, dry_run: bool, verbose: bool
) -> tuple[int, int]:
    """Run one archive pass. Returns (examined, pruned)."""
    threshold_dt = datetime.now().astimezone() - timedelta(days=days)
    all_entries = [e for e in sorted(answered_dir.iterdir()) if e.is_dir()]

    if verbose:
        for entry in all_entries:
            age_days = (datetime.now().astimezone() - _entry_mtime(entry)).days
            print(f"  {entry.name}: {age_days} days old")

    stale = [e for e in all_entries if _entry_mtime(e) < threshold_dt]
    pruned = prune_entries(stale, dry_run=dry_run, verbose=verbose and not dry_run)
    return len(all_entries), pruned


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prune answered_feedback entries older than N days."
    )
    parser.add_argument(
        "--days",
        type=int,
        default=DEFAULT_DAYS,
        help=f"Age threshold in days (default: {DEFAULT_DAYS})",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print without deleting")
    parser.add_argument(
        "--answered-dir",
        default=DEFAULT_ANSWERED_DIR,
        help=f"Path to answered_feedback dir (default: {DEFAULT_ANSWERED_DIR})",
    )
    parser.add_argument("--verbose", action="store_true", help="Print each entry examined")
    args = parser.parse_args()

    answered_dir = Path(args.answered_dir)
    try:
        examined, pruned = archive_answered_feedback(
            answered_dir,
            days=args.days,
            dry_run=args.dry_run,
            verbose=args.verbose,
        )
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1) from exc

    verb = "would delete" if args.dry_run else "deleted"
    suffix = " (dry-run)" if args.dry_run else ""
    print(f"Examined {examined} entries — {verb} {pruned}{suffix}.")


if __name__ == "__main__":
    main()
