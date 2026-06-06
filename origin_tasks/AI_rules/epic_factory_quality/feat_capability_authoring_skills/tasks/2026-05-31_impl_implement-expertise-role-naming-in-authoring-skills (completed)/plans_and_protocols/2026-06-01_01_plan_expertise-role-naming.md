# Plan: Implement {expertise}-{role} naming in authoring skills

## Approach: inline (2 skill files, clear shape)

## Context

Both `claude-create-agent` and `claude-modify-agent` already have:
- The Artifact-Establishment Gate for unknown expertise tokens
- Collision check against built-ins, han-*, existing agents

**Missing** (what this task adds):
1. Format constraint: name = `{expertise}-{role}`, role is always the last hyphen-delimited segment
2. Role must be in closed set {writer, transformer, reviewer, classifier}
3. Zero-or-multi-role case: skill stops and asks developer to clarify
4. Collision check repositioned as a sub-rule executed AFTER format validation passes

## Phases

### Phase 1 — Modify `claude-create-agent` §2 Naming
- Add format check step before expertise gate and collision check
- Add role validation with 2×2 axis explanation
- Add zero/multi-role stop behavior
- Explicitly label collision check as sub-rule (runs after format + expertise validation pass)
- Use `claude-modify-skill` (no direct SKILL.md edits per AC requirement)

### Phase 2 — Modify `claude-modify-agent` rename path
- Update step 3 §2 naming re-assertion to reference new format check
- Explicitly require format validation before the collision sub-check on rename
- Use `claude-modify-skill`

## Name format interpretation

The format `{expertise}-{role}` is split on the LAST hyphen:
- `{role}` = last segment (no hyphens)
- `{expertise}` = everything before the last hyphen (may itself contain hyphens, e.g. `ui-scribble`)

This is consistent with the existing §2 wording "everything before the final -{role}".

## Files changed

- `.claude/skills/claude-create-agent/SKILL.md`
- `.claude/skills/claude-modify-agent/SKILL.md`
