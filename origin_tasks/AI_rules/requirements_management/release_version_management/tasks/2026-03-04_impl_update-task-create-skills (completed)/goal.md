---
task_id: TASK-PROC-034-06
type: impl
parent_requirement: REQ-PROC-034
urgency: 4
urgency_reason: U4-PLAN
impact: 5
impact_reason: I5-ENAB
status: completed
completed: 2026-03-04
effort: M
created: 2026-03-04
after: [TASK-PROC-034-02]
awaiting: []
covers:
  acceptance_criteria: []
  sections: [SEC-04]
scope_description: "Update task-create and task-create-impl skills to inherit target_release from covered trackable items, or prompt user when inheritance is not possible."
requirements_version:
  commit: c8c9ac7
  file: ../requirements.md
---

# Goal: Update task-create + task-create-impl Skills — Release Inheritance

## What

Extend `.claude/skills/task-create/skill.md` and `.claude/skills/task-create-impl/skill.md` with release version logic that runs during task creation, after the `covers` field is determined.

## Scope

### Logic for Both Skills

After the `covers` field is populated (which references specific ACs or sections from the parent requirement):

1. **Read parent requirement's trackable items** — look up each referenced AC/section to find its `target_release`
2. **If all covered items have `target_release`**: set task's `target_release` to the **earliest** among them (semver comparison). Log the inherited value to the user.
3. **If some covered items are unassigned**: prompt user — "Covered items have mixed release assignments. Which release should this task target?" Present available releases from RELEASES.md.
4. **If `covers` is empty**: prompt user — "No trackable items covered. Which release does this task target?" Present available releases from RELEASES.md.
5. **Write `target_release`** to the task's YAML frontmatter in goal.md

### RELEASES.md Loading

Both skills read `requirements_tasks/RELEASES.md` to get available versions for user prompts. If RELEASES.md does not exist: warn and skip release assignment (do not fail task creation).

### task-rollover

**No changes needed.** The rollover skill copies the entire goal.md YAML verbatim, so `target_release` is preserved automatically.

### Behavior Rules (from REQ-PROC-034 SEC-04)

| Situation | Behavior |
|-----------|----------|
| Covered items all have `target_release` | Auto-inherit earliest (no prompt) |
| Covered items partially assigned | Ask user |
| `covers` is empty | Ask user |
| RELEASES.md missing | Warn + skip |

## Key Files

- `.claude/skills/task-create/skill.md` — read the full skill; insert release step after `covers` determination
- `.claude/skills/task-create-impl/skill.md` — read the full skill; same insertion point

## Important Constraints

- Skills are token-sensitive: keep additions concise
- Do not duplicate content between the two skills — use the same wording wherever possible
- No Dart-style `///` comments

## Out of Scope

- requ-explore skill (TASK-PROC-034-05)
- Script changes (TASK-PROC-034-03, -04)
- Migration of existing tasks (TASK-PROC-034-07)
