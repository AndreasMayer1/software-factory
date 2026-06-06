---
name: claude-ask
---

# claude-ask

Answer questions with research using the current session model.

## Workflow

1. **Gather**: Read relevant files, search codebase (main context only — NO agents)
2. **Answer**: Provide researched answer in the session's model

## Usage

`"Use claude-ask skill: [your question]"`

## When to use

- Questions needing research but no planning/implementation
- Want answer in main session context (not agent)
- If the task is flagged `opus_recommended` and you want Opus-quality answers, run `/model opus` first (the orchestrator already does this for automated sessions)
