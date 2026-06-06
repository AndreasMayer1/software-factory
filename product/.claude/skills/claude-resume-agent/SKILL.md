---
name: claude-resume-agent
description: Resume a stopped or killed (background) agent
---

Resume a stopped or killed (background) agent — either via native mechanism or by reconstructing context and spawning a replacement.

## Steps

1. **Find the agentId** — check conversation context first (task notification or prior message usually contains it). If unknown:
   ```
   find /home/vscode/.ccs /home/vscode/.claude -name "agent-*.jsonl" 2>/dev/null | xargs ls -lt 2>/dev/null | head -20
   ```
   Most recent file starting with `agent-a` → strip `agent-` prefix and `.jsonl` suffix = agentId.

2. **Try native resume** — use ToolSearch to check if `SendMessage` is available:
   - If available: attempt `SendMessage` with `to: "<agentId>"` and the continuation instruction.
   - If it succeeds: done.

3. **Fallback — spawn a single continuation agent** (reads context and continues work directly):

   Spawn a subagent with this task:
   > "You are resuming a stopped agent. Do the following in order:
   >
   > **Phase 1 — Reconstruct context** (read both files before doing anything else):
   > - **IMPORTANT**: Always read both files fully — even if the agent appeared to terminate immediately (e.g. rate limit), partial work may still be present.
   > 1. Transcript: `find /home/vscode/.ccs /home/vscode/.claude -name "agent-<agentId>.jsonl" 2>/dev/null`
   >    → Find the first user message = original task (read verbatim, no truncation).
   > 2. Output file: `<path from task notification>`
   >    → Identify what was completed and where the agent stopped. If empty, assume nothing done.
   >
   > **Phase 2 — Continue the work**:
   > Execute the original task from where it stopped. Skip already-completed steps."
