---
task_id: TASK-PROC-042-10
type: impl
parent_requirement: REQ-PROC-042
urgency: 3
urgency_reason: U3-CTX
impact: 4
impact_reason: I4-QUAL
status: completed
effort: M
created: 2026-04-22
started: 2026-04-23
completed: 2026-04-23
session_completed_at: 2026-04-23T16:47:40Z
session_id: 094be82f-3dd4-40b8-839c-b809a7deb80e
session_account: gmail
after: [TASK-PROC-042-07]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-03, AC-08, AC-09, AC-12, AC-13]
  sections: []
scope_description: "Create .claude/skills/claude-modify-ordering-rules/ skill: read rule file + change, show YAML diff, run simulate.py, require approval before writing; surface rationale fields when signal order changes; include init mode via opus-advisor; trigger from claude-create-skill for new task types"
release_description: ""
opus_recommended: true   # reason: skill design requires careful trade-off reasoning about LLM behavior; surfacing rationale correctly is non-trivial
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: f65d3fca
  file: ../requirements.md
---

# Goal: Create claude-modify-ordering-rules Skill

## Objective

Create the `.claude/skills/claude-modify-ordering-rules/skill.md` skill that allows the factory to evolve its own task ordering rules. The skill handles both incremental rule updates and initial rule file creation for new projects (init mode).

## Requirements Summary

AC-03 (skill to update rules), AC-08 (dry-run via simulate.py), AC-09 (trigger from claude-create-skill), AC-12 (surface rationale fields), AC-13 (init mode for new projects).

For complete requirements at task creation time:
```
git show f65d3fca:requirements_tasks/process/AI_rules/requirements_management/task_ordering/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- Standard workflow (5 steps): Read state → Classify change → Propose diff → Simulate → Approve
- Step 3 must explicitly surface `rationale:` and `rationale_source:` fields for any `ranking_signals` entry whose position in the tuple is proposed to change
- Step 4 is mandatory: always run `simulate.py` before writing
- Step 5: on approval write rule file + commit; on rejection discard and offer restart
- Step 6 (Propagate): remind user to check dependent skills and factory_flows.md
- **Init mode**: triggered when rule file does not exist; uses opus-advisor agent to scan project folder structure and frontmatter, proposes a starter layer taxonomy, presents to user for review before writing
- Validation rules enforced: schema version bump on breaking changes, layer order uniqueness, sparsity recommendation, dependency cycle check, glob sanity
- Trigger instruction for `claude-create-skill`: add a reminder at the end of claude-create-skill to ask "Does this skill produce a new task type? If yes, use claude-modify-ordering-rules to register it"
- Use `claude-switch-opus` for: ranking signal order changes, layer removals, cross-layer dependency heuristic additions

### Out of Scope
- Changes to simulate.py or validate_rules.py (those are done)
- Modifying INDEX.md (TASK-PROC-042-11)

## Acceptance Criteria

- [ ] Skill file exists at `.claude/skills/claude-modify-ordering-rules/skill.md`
- [ ] Standard 5-step workflow documented in skill
- [ ] Init mode documented: opus-advisor scans project, proposes starter rule file
- [ ] Rationale surfacing step explicitly documented for signal order changes
- [ ] simulate.py step is mandatory (cannot be skipped)
- [ ] Validation rules enforced before writing
- [ ] `claude-create-skill` updated with end-of-skill reminder about registering new task types
- [ ] Opus escalation triggers documented

## Dependencies

| Dependency | Notes |
|---|---|
| TASK-PROC-042-07 | simulate.py must exist (skill references it) |

## Notes

Full design reference:
- Part 5: The "Update Ordering Rules" Skill (§5.1–§5.5)
- §10.7: Init mode via opus-advisor
- §10.8: Rationale field surfacing requirement
