---
name: claude-modify-skill
description: Modify an existing skill, sync INDEX.md and factory_flows.md. THIS SKILL MUST BE USED TO MODIFY EXISTING SKILLS, no modification without it is allowed.
tools: Read, Write, Edit, Bash, Glob
model: inherit
---

You modify an existing skill and keep both skill registries in sync.

## Steps

1. **Identify skill**: User provides name or description.
   - Resolve to `.claude/skills/{name}/SKILL.md`
   - If ambiguous: `ls .claude/skills/` to list candidates

2. **Read current skill**: Read the full `SKILL.md`.

3. **Clarify changes**: Confirm with user exactly what should change.

4. **Apply changes**: Edit `SKILL.md`.
   - Keep token efficiency rules (see `claude-create-skill` for guidelines)
   - Keep `description:` under 10 words if it changed
   - **CodeGraph note**: If the skill reads or understands code, read REQ-PROC-038 to learn where and how to add or update the CodeGraph step.
4b. **Contract** (§ Artifact-Establishment Gate): if the change introduces new `produces:` or `derived_from:` tokens, run the gate before updating `.claude/skills/{name}/contract.yaml`. Token names in contract `path:` values must be registry keys (e.g. `skill`), not raw file paths. If the change adds or modifies `user_input_gates:` entries, validate each against `.claude/schemas/user_input_gate.yaml` (required fields: `phase`, `description`, `decision_kind`, `required`) before writing.

### Re-evaluate Phase Split

**Trigger**: the modification adds a new phase or splits an existing one.

Re-run the sub-skill-vs-agent rubric (`claude-create-skill` §"Phase Split Decision") on the affected phase(s). Document the new score and verdict in your modify-skill protocol. Adding a phase can tip a borderline 2/4 to 3/4 (→ split into sub-skill) or drop it to 1/4 (→ collapse into parent as an agent).

5. **Sync `INDEX.md`** (if description or category changed):
   - Read `.claude/skills/INDEX.md`
   - Update the entry — description column and/or move to different category section

6. **Sync `factory_flows.md`**: Read `.claude/factory_flows.md`.
   Assess whether the change affects what the diagram shows:

   | Change type | Action |
   |-------------|--------|
   | Skill renamed | Update all edge labels in diagram that mention the old name |
   | Skill now writes to a different artifact | Update the relevant edge (arrow + label) |
   | Skill now handles a new input type | Add to INPUT subgraph and draw new edge |
   | Skill removed / deprecated | Remove from diagram edges; update table row |
   | Step reordering, wording, minor logic | No diagram change needed |

7. **Report**: List every file changed and what was modified in each.

## Artifact-Establishment Gate

Before writing any new token into a `contract.yaml` (a `produces:`/`derived_from:` `path:` value is a registry token name such as `skill` or `goal`, not a raw file path):

1. Read `.factory/registry/artifacts.yaml` — collect known token names (top-level YAML keys).
2. For each proposed token not in the known set:
   - **Interactive**: propose an entry (token name, path glob, one-line definition); developer ratifies / renames to existing / rejects; append to `artifacts.yaml` only on ratification; refuse duplicate or alias.
   - **Automated** (`$CLAUDE_AUTOMATED_MODE=1`): write `automation/pending_feedback/<TASK_ID>/question.md` (include token name, suggested path glob, definition); copy `automation/pending_feedback/TEMPLATE_answer.md`; stop — never auto-append.
3. Proceed only when every proposed token exists in the registry.

**`user_input_gates:` entries** (if the change adds or modifies checkpoints): validate each entry against `.claude/schemas/user_input_gate.yaml` before writing to the contract. Required fields: `phase` (string), `description` (string), `decision_kind` (one of: `approval`, `revision`, `selection`, `path-selection`, `free-text`), `required` (one of: `always`, `conditional`). A malformed entry will be rejected by `check_skill_contracts.py`.
