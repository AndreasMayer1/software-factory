#!/usr/bin/env python3
"""Monitor: a skill file edited and (Stage 2) subsequently used (REQ-PROC-006 IMPL-C).

Two-stage monitor (SEC-01: "Both stages are valid operational modes"):

- Stage 1 (active): fire `skill_changed_and_used` (confidence Low) for each skill
  file edited in a recent commit, on the edit alone. Higher false-positive rate.
- Stage 2 (active since IMPL-H / TASK-PROC-006-13): reads protocol `skills_used:`
  frontmatter from recently-committed protocol.md files; when an edited skill
  appears in any session's `skills_used:`, confidence is raised to Medium.

Each (skill_path, commit) edit fires once; idempotent within a 48-hour cooldown.
Consumes git history only — committed, project-local. No session JSONL (G-INV-2).
"""

# tier: B  # imported by run_monitors.py and its tests

from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

_OPTIMIZE_DIR = str(Path(__file__).resolve().parent)
if _OPTIMIZE_DIR not in sys.path:
    sys.path.insert(0, _OPTIMIZE_DIR)

_SCRIPTS_DIR = str(Path(__file__).resolve().parents[1])
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

import monitor_common as mc  # type: ignore[import-not-found]  # noqa: E402 -- sys.path mutated above; mypy cannot follow runtime path manipulation
from util.yaml_frontmatter import (  # type: ignore[import-not-found]  # noqa: E402 -- sys.path mutated above; mypy cannot follow runtime path manipulation
    FrontmatterError,
    read_frontmatter,
)

EVENT_TYPE = "skill_changed_and_used"
WINDOW = timedelta(hours=48)
COOLDOWN = timedelta(hours=48)

# Stage 2 enabled by IMPL-H (TASK-PROC-006-13): protocol `skills_used:` field is
# now written by task-complete, so evidence-based confidence upgrade is active.
_STAGE2_ENABLED = True


def _stage2_used_skills(
    now: datetime,
    git: mc.GitRunner = mc.real_git,
    project_root: Path = mc.PROJECT_ROOT,
) -> set[str]:
    """Stage 2 evidence: skill paths confirmed exercised in a session.

    Scans protocol.md files committed within WINDOW that carry a `skills_used:`
    YAML frontmatter list.  Returns the set of `.claude/skills/<name>/SKILL.md`
    relative paths for every skill name found, so detect() can upgrade matching
    events to confidence Medium.
    """
    since_iso = (now - WINDOW).isoformat()
    out = git(
        [
            "log",
            f"--since={since_iso}",
            "--name-only",
            "--diff-filter=AM",
            "--pretty=format:",
            "--",
            "requirements_tasks/",
        ]
    )

    skill_names: set[str] = set()
    seen: set[str] = set()
    for line in out.splitlines():
        rel = line.strip()
        basename = rel.rsplit("/", 1)[-1]
        if "/plans_and_protocols/" not in rel or "protocol" not in basename or not basename.endswith(".md"):
            continue
        if rel in seen:
            continue
        seen.add(rel)
        path = project_root / rel
        if not path.exists():
            continue
        try:
            doc = read_frontmatter(path)
        except (OSError, FrontmatterError):
            continue
        names = doc.metadata.get("skills_used")
        if isinstance(names, list):
            skill_names.update(str(n) for n in names if n)

    return {f"{mc.SKILLS_DIR_REL}/{name}/SKILL.md" for name in skill_names}


def detect(now: datetime, git: mc.GitRunner = mc.real_git) -> list[mc.Event]:
    """Return one event per (skill_path, commit) edited in the window."""
    since_iso = (now - WINDOW).isoformat()
    commits = mc.skill_commits_in_window(since_iso, git)
    used = _stage2_used_skills(now, git) if _STAGE2_ENABLED else set()
    events: list[mc.Event] = []
    for path in sorted(commits):
        is_used = path in used
        confidence = mc.CONFIDENCE_MEDIUM if is_used else mc.CONFIDENCE_LOW
        for sha in commits[path]:
            events.append(
                mc.Event(
                    event_type=EVENT_TYPE,
                    confidence=confidence,
                    fingerprint=f"{path}@{sha}",
                    created=now,
                    payload={
                        "skill_path": path,
                        "commit": sha,
                        "stage": 2 if is_used else 1,
                    },
                )
            )
    return events


def run(
    now: datetime | None = None,
    git: mc.GitRunner = mc.real_git,
    events_dir: Path = mc.EVENTS_DIR,
) -> list[Path]:
    """Detect recent skill edits and emit at most one event per (path,commit)/cooldown."""
    now = now or mc.utc_now()
    written: list[Path] = []
    for event in detect(now, git):
        path = mc.emit_once(event, COOLDOWN, now, events_dir)
        if path is not None:
            written.append(path)
    return written
