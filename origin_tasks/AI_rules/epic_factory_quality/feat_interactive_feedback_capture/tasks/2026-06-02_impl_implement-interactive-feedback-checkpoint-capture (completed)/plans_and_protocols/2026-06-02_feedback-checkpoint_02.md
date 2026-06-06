---
skill: claude-modify-skill
mode: interactive
decision: "revised"
task_id: TASK-PROC-044-03-01
captured_at: 2026-06-02
---

# Question

Skill step said to write verbatim words to a temp file, with a fixed /tmp/feedback_answer.txt example.

# Developer Answer

"Write the developer's words **verbatim** to a temp file" => where shall the llm create that temp file?

# Rationale Captured

Use mktemp: unique per decision, under /tmp (OUTSIDE the working tree so the Commit step can't stage it), via a quoted heredoc to preserve exact bytes.
