---
task_id: TASK-PROC-034-05
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
scope_description: "Update the requ-explore skill to read RELEASES.md and prompt the user for target_release per trackable item (acceptance criterion or section), then compute the top-level target_release as the earliest among all assigned items."
requirements_version:
  commit: c8c9ac7
  file: ../requirements.md
---

# Goal: Update requ-explore Skill — Per-Item Release Assignment

## What

Extend `.claude/skills/requ-explore/skill.md` with release version assignment logic that runs during Phase 2 (Synthesis & Writing), immediately after the requirement document is drafted.

## Scope

### New Step in requ-explore Workflow

After drafting the requirement content (Phase 2.2 / 2.3), add a **Release Assignment** step before finalizing the document:

1. **Read `requirements_tasks/RELEASES.md`** — parse the `releases` list from YAML frontmatter to get all known versions with names and descriptions
2. **For each trackable item** (AC or section) in the new requirement:
   - Present the list of available releases to the user (version + name)
   - Ask which release this trackable item targets (or "unassigned / skip")
   - Add `target_release: "X.Y.Z"` to that item in the YAML
3. **Compute top-level `target_release`**: set to the earliest release among all assigned trackable items (using semver ordering). If none assigned, omit the top-level field.
4. **Write the result** into the `requirements.md` YAML frontmatter

### Per-Item Approach (From the Start)

The per-item approach is the primary and only approach. The top-level `target_release` is always derived — never set independently. If a requirement has no trackable items, ask once for a single top-level release assignment.

### When to Skip

- If the requirement is purely internal process tooling (e.g., another AI skill update) and the user indicates "unassigned", skip without error
- When updating an existing requirement: preserve existing `target_release` values on trackable items; only prompt for new/unassigned items

### Behavior Rules (from REQ-PROC-034 SEC-04)

| Situation | Behavior |
|-----------|----------|
| New requirement with trackable items | Ask per item |
| Existing requirement, item already has release | Preserve; do not ask again |
| Existing requirement, item has no release | Ask |
| RELEASES.md not found | Warn user; skip release assignment |

## Key File

`.claude/skills/requ-explore/skill.md` — read the full skill before modifying. Insert the new step at the correct phase, following the existing step numbering and style conventions.

## Important Constraints

- Skills are token-sensitive: keep the new text concise. Use inline `(reason)` notes, not Dart-style `///` comments.
- Do not add lengthy explanations — the skill must remain lean.

## Out of Scope

- Changes to task-create / task-create-impl (TASK-PROC-034-06)
- Script changes (TASK-PROC-034-03, -04)
