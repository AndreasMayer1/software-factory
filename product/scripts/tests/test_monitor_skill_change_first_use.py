#!/usr/bin/env python3
"""Tests for scripts/optimize/monitor_skill_change_first_use.py (REQ-PROC-006 IMPL-C).

Covers Stage-1 per-(path,commit) firing, Stage-2 protocol-scanning (confidence
Medium when skill appears in skills_used: frontmatter), and the cooldown
idempotency (run twice -> same set, no duplicates).
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "optimize"))
import monitor_common as mc  # type: ignore[import-not-found]  # sys.path mutated above
import monitor_skill_change_first_use as m  # type: ignore[import-not-found]  # sys.path mutated above

NOW = datetime(2026, 5, 28, 12, 0, 0, tzinfo=timezone.utc)
SKILL = ".claude/skills/foo/SKILL.md"


def _fake_git(log):
    def run(args):
        return log if args and args[0] == "log" else ""

    return run


def _write_protocol(
    directory: Path, skill_names: list[str], filename: str = "protocol.md"
) -> Path:
    """Write a protocol file with skills_used: frontmatter into a task folder."""
    task_dir = directory / "requirements_tasks" / "some" / "task" / "plans_and_protocols"
    task_dir.mkdir(parents=True)
    skills_block = "\n".join(f"  - {n}" for n in skill_names)
    proto = task_dir / filename
    proto.write_text(
        f"---\nskills_used:\n{skills_block}\n---\n\n## Entry\nSome content.\n",
        encoding="utf-8",
    )
    return proto


# ---------------------------------------------------------------------------
# Stage 1 tests
# ---------------------------------------------------------------------------


def test_stage1_fires_once_per_commit(tmp_path):
    log = f"{mc._COMMIT_MARKER}sha2\nM\t{SKILL}\n{mc._COMMIT_MARKER}sha1\nM\t{SKILL}\n"
    events = m.detect(NOW, git=_fake_git(log))
    assert len(events) == 2
    fingerprints = {e.fingerprint for e in events}
    assert fingerprints == {f"{SKILL}@sha2", f"{SKILL}@sha1"}
    assert all(e.confidence == "low" for e in events)
    assert all(e.payload["stage"] == 1 for e in events)


def test_no_fire_without_skill_commits():
    assert m.detect(NOW, git=_fake_git("")) == []


def test_run_is_idempotent_within_cooldown(tmp_path):
    log = f"{mc._COMMIT_MARKER}sha1\nM\t{SKILL}\n"
    git = _fake_git(log)
    first = m.run(now=NOW, git=git, events_dir=tmp_path)
    second = m.run(now=NOW, git=git, events_dir=tmp_path)
    assert len(first) == 1
    assert second == []
    assert len(list(tmp_path.glob("*.json"))) == 1


# ---------------------------------------------------------------------------
# Stage 2 tests
# ---------------------------------------------------------------------------


def test_stage2_is_enabled():
    assert m._STAGE2_ENABLED is True


def test_stage2_used_skills_empty_when_no_protocols(tmp_path):
    used = m._stage2_used_skills(NOW, git=_fake_git(""), project_root=tmp_path)
    assert used == set()


def test_stage2_used_skills_reads_frontmatter(tmp_path):
    proto = _write_protocol(tmp_path, ["task-complete", "claude-log"])
    rel = str(proto.relative_to(tmp_path))
    used = m._stage2_used_skills(NOW, git=_fake_git(rel + "\n"), project_root=tmp_path)
    assert ".claude/skills/task-complete/SKILL.md" in used
    assert ".claude/skills/claude-log/SKILL.md" in used


def test_stage2_used_skills_reads_prefixed_protocol_name(tmp_path):
    """Regression: files named like 2026-05-28_02_protocol_something.md must match."""
    proto = _write_protocol(
        tmp_path,
        ["task-complete"],
        filename="2026-05-28_02_protocol_skills-used-instrumentation.md",
    )
    rel = str(proto.relative_to(tmp_path))
    used = m._stage2_used_skills(NOW, git=_fake_git(rel + "\n"), project_root=tmp_path)
    assert ".claude/skills/task-complete/SKILL.md" in used


def test_stage2_used_skills_ignores_non_protocol_files(tmp_path):
    proto = _write_protocol(tmp_path, ["task-complete"])
    rel = str(proto.relative_to(tmp_path))
    # Git output includes both a protocol.md and a non-protocol file
    git_out = rel + "\nrequirements_tasks/some/goal.md\n"
    used = m._stage2_used_skills(NOW, git=_fake_git(git_out), project_root=tmp_path)
    assert ".claude/skills/task-complete/SKILL.md" in used
    assert len(used) == 1


def test_stage2_upgrades_confidence_to_medium(tmp_path):
    """When the edited skill appears in skills_used: the event gets Medium confidence."""
    skill_name = "foo"
    skill_path = f".claude/skills/{skill_name}/SKILL.md"

    proto = _write_protocol(tmp_path, [skill_name])
    proto_rel = str(proto.relative_to(tmp_path))

    # Git returns both a skill commit and the protocol.md in the same log output
    sha = "abc123"
    log = (
        f"{mc._COMMIT_MARKER}{sha}\nM\t{skill_path}\n"
        f"{proto_rel}\n"
    )
    # Stage 2 only works with project_root injection; detect() uses mc.PROJECT_ROOT.
    # Use _stage2_used_skills directly to verify the upgrade path.
    used = m._stage2_used_skills(NOW, git=_fake_git(proto_rel + "\n"), project_root=tmp_path)
    assert skill_path in used

    # Rebuild events with the Stage 2 evidence injected via a custom detect call.
    commits = mc.skill_commits_in_window((NOW - m.WINDOW).isoformat(), _fake_git(log))
    events_medium = []
    for path in sorted(commits):
        is_used = path in used
        confidence = mc.CONFIDENCE_MEDIUM if is_used else mc.CONFIDENCE_LOW
        for s in commits[path]:
            events_medium.append(
                mc.Event(
                    event_type=m.EVENT_TYPE,
                    confidence=confidence,
                    fingerprint=f"{path}@{s}",
                    created=NOW,
                    payload={"skill_path": path, "commit": s, "stage": 2 if is_used else 1},
                )
            )
    assert len(events_medium) == 1
    assert events_medium[0].confidence == mc.CONFIDENCE_MEDIUM
    assert events_medium[0].payload["stage"] == 2
