#!/usr/bin/env bash
set -euo pipefail

# Patch empty session_id in pending_feedback question.md files before terminating.
# Why: sessions that bypass task-start never write session_id to goal.md, so
# claude-automated-mode reads SESSION_ID="" and writes session_id: "" to question.md.
# find_answered_feedback rejects empty session_id as malformed → infinite loop.
# This structural backstop runs at every session exit, requiring zero new LLM compliance.
python3 - <<'PYEOF'
import os
import re
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
feedback_dir = os.path.join(project_root, "automation", "pending_feedback")
session_id = os.environ.get("CLAUDE_SESSION_ID", "").strip()

if not os.path.isdir(feedback_dir):
    sys.exit(0)

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def get_frontmatter_value(content, key):
    """Extract a YAML frontmatter scalar value for the given key."""
    m = re.search(r"^" + re.escape(key) + r":\s*(.*)\s*$", content, re.MULTILINE)
    if not m:
        return ""
    return m.group(1).strip().strip('"').strip("'")

def set_frontmatter_value(content, key, value):
    """Set or insert a YAML frontmatter key: value (quoted string)."""
    quoted = f'"{value}"'
    pattern = r"^" + re.escape(key) + r":.*$"
    if re.search(pattern, content, re.MULTILINE):
        return re.sub(pattern, f'{key}: {quoted}', content, flags=re.MULTILINE)
    # Insert after first '---' line
    return re.sub(r"^(---\s*\n)", r"\1" + f"{key}: {quoted}\n", content, count=1)

def set_status_in_progress(content):
    """Change status: pending to status: in_progress in YAML frontmatter."""
    return re.sub(r"^(status:\s*)pending\s*$", r"\1in_progress", content, flags=re.MULTILINE)

for entry in os.scandir(feedback_dir):
    if not entry.is_dir():
        continue
    question_path = os.path.join(entry.path, "question.md")
    if not os.path.exists(question_path):
        continue
    try:
        q_content = read_file(question_path)
    except OSError:
        continue

    existing_sid = get_frontmatter_value(q_content, "session_id")
    if existing_sid:
        continue  # already has a session_id — nothing to patch

    # Determine patch value
    patch_value = session_id if session_id else "NEW_SESSION_REQUIRED"

    # Patch question.md
    q_patched = set_frontmatter_value(q_content, "session_id", patch_value)
    write_file(question_path, q_patched)
    print(f"[terminate] Patched session_id in {question_path} → {patch_value}")

    # Find and patch corresponding goal.md via task_id
    task_id = get_frontmatter_value(q_content, "task_id")
    if not task_id:
        continue

    req_dir = os.path.join(project_root, "requirements_tasks")
    import subprocess
    result = subprocess.run(
        ["grep", "-rl", f"^task_id: {task_id}", req_dir, "--include=goal.md"],
        capture_output=True, text=True
    )
    for goal_path in result.stdout.strip().splitlines():
        if not goal_path.endswith("goal.md"):
            continue
        try:
            g_content = read_file(goal_path)
        except OSError:
            continue

        changed = False
        existing_goal_sid = get_frontmatter_value(g_content, "session_id")
        if not existing_goal_sid:
            g_content = set_frontmatter_value(g_content, "session_id", patch_value)
            changed = True

        goal_status = get_frontmatter_value(g_content, "status")
        if goal_status == "pending":
            g_content = set_status_in_progress(g_content)
            changed = True

        if changed:
            write_file(goal_path, g_content)
            print(f"[terminate] Patched session_id/status in {goal_path} → {patch_value}")
        break
PYEOF

# Send SIGTERM to the parent process group (Claude Code session).
# Targets the specific session's process group via PPID — avoids killing
# unrelated claude sessions that run in separate process groups.
PGID=$(ps -o pgid= -p "$PPID" | tr -d ' ')
kill -TERM -- "-${PGID}"
