# Plan: Group 5 — Add Context-Window Rule to CLAUDE.md §7

**Task**: TASK-PROC-035-08, Group 5 (independent)
**Verification**: V7 check from goal.md

---

## 1. Insertion Point

**File**: `/workspaces/private_mood_tracker/flutter_app/CLAUDE.md`

Insert after **line 251** (the `**Code Analysis**` line), before the `**Finding artifacts by ID**` line.

Current line 251:
```
**Code Analysis**: Use `codegraph context "<task>"` before Glob/Grep when exploring code.
```

The new rule goes on line 252 (blank line separator), line 253 (new rule text).

---

## 2. Exact Text to Insert

Insert one blank line after line 251, then add:

```
**Context-Window Rule**: Skills reading requirement files must call `scripts/should_use_agents.py` before deciding to read inline. Hard threshold: 30KB total OR 5 files. Structural fan-out phases always use agents regardless of size.
```

---

## 3. Result (lines 251–254 after edit)

```
**Code Analysis**: Use `codegraph context "<task>"` before Glob/Grep when exploring code.

**Context-Window Rule**: Skills reading requirement files must call `scripts/should_use_agents.py` before deciding to read inline. Hard threshold: 30KB total OR 5 files. Structural fan-out phases always use agents regardless of size.

**Finding artifacts by ID**: All artifacts (flows, scenarios, personas, requirements, etc.) store their ID as `id: <ID>` in YAML frontmatter. Search: `grep -rl "id: FLOW-003" requirements_user_needs/`
```

---

## 4. Verification Command (V7)

```bash
grep "should_use_agents" /workspaces/private_mood_tracker/flutter_app/CLAUDE.md && echo "V7 PASS"
```

Expected output: the matching line followed by `V7 PASS`.
