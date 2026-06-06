---
name: claude-write-hook
description: Create or modify a Claude Code hook script. MUST be used for all hook work.
tools: [Read, Edit, Write, Bash]
model: inherit
---

Create or modify a hook script in `.claude/hooks/` and keep `settings.json` and `scripts/tests/test_hooks.py` in sync.

## Steps

1. **Write or update the hook script** at `.claude/hooks/<name>.sh`
   - Naming: `{pre|post}_{event}_{purpose}.sh` (e.g. `pre_edit_scripts_reminder.sh`)
   - Make executable: `chmod +x .claude/hooks/<name>.sh`
   - Hook receives tool-event JSON on stdin — read with `jq -r '.tool_input.<field> // ""'`
   - Always exit 0 unless intentionally blocking (use deny JSON instead of non-zero exit)
   - Use `printf '%s\n'` for JSON output — never `echo`

2. **Wire into `settings.json`** (`.claude/settings.json`)
   - Add or update the hook entry under the correct event (`PreToolUse` / `PostToolUse` / `SessionStart` / `Stop`)
   - Use absolute path: `/workspaces/private_mood_tracker/flutter_app/.claude/hooks/<name>.sh`
   - PostToolUse hooks: append `2>/dev/null || true`
   - PreToolUse hooks that only emit advisory JSON: no `|| true` needed (script always exits 0)
   - PreToolUse hooks that may deny: no `|| true` (must control own exit)

3. **Update `scripts/tests/test_hooks.py`** via the `claude-write-script` skill
   - Add a `Test<ScriptStemCamel>` class with tests covering: matching path → expected output, non-matching path → silent exit 0, edge cases (empty path, missing key)
   - Run quality gates: `scripts/quality/check_python_gates.sh`

4. **Verify** the hook logic by tracing the command manually with sample JSON:
   ```bash
   echo '{"tool_input":{"file_path":"scripts/foo.py"}}' | bash .claude/hooks/<name>.sh
   ```

## hookSpecificOutput shape (PreToolUse only)

```json
{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"..."}}
```
To deny a tool call:
```json
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"..."}}
```

## Hook event / matcher reference

| Event | Matcher examples | Stdin field |
|---|---|---|
| PreToolUse | `"Edit\|Write"`, `"Bash"`, `"Read"` | `.tool_input.file_path` / `.tool_input.command` |
| PostToolUse | `"Edit\|Write"`, `"Read"` | `.tool_result` + `.tool_input.*` |
| SessionStart | _(no matcher)_ | session metadata |
