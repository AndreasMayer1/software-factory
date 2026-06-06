# Plan: Create claude-modify-ordering-rules Skill

## Approach: Opus (skill design with non-trivial LLM behavior trade-offs)

## Context Gathered

- Rule file: `.claude/task_ordering_rules.yaml` — schema version 1.0, layers with order/match/rationale, ranking_signals with rationale+rationale_source, special_flags, dependency_heuristics
- simulate.py: `python3 scripts/task_ordering/simulate.py --proposed-rules <path> [--current-rules <path>] [--verbose]` — exit 0 always, prints top-20 ranking delta table
- validate_rules.py: `python3 scripts/task_ordering/validate_rules.py [--rules PATH]` — checks schema_version, required layer fields, unique order values, unique names, path_glob sanity (warns), dependency cycle check; exit 0 = OK
- DEFAULT_RULES_PATH: `.claude/task_ordering_rules.yaml`
- claude-create-skill: needs a reminder appended at step 7 (after INDEX.md entry) about registering new task types via claude-modify-ordering-rules

## Deliverables

1. `.claude/skills/claude-modify-ordering-rules/skill.md` — new skill
2. `.claude/skills/claude-create-skill/skill.md` — add end reminder (step 8)
3. Add entry to `.claude/skills/INDEX.md`

## Skill Design Requirements

### Standard Workflow (5 steps)
1. Read state: load current rule file, read goal of proposed change
2. Classify change: categorize (new layer / layer removal / signal reorder / flag addition / heuristic addition / init)
3. Propose diff: show YAML diff; for ranking_signals with position change, surface rationale: + rationale_source:
4. Simulate (mandatory): run `python3 scripts/task_ordering/simulate.py --proposed-rules <tmp-file>` — show output to user
5. Approve/reject: on approval run validate_rules.py, write file, commit; on rejection discard + offer restart
6. Propagate: remind user to check dependent skills and factory_flows.md

### Init Mode
- Triggered when rule file doesn't exist
- Use opus-advisor to scan project folder structure + task frontmatter
- Propose starter layer taxonomy
- Present to user for review before writing

### Opus Escalation Triggers
- Ranking signal order changes
- Layer removals
- Cross-layer dependency heuristic additions

### Validation Before Writing
- Schema version bump on breaking changes
- Layer order uniqueness
- Sparsity recommendation
- Dependency cycle check
- Glob sanity
(all via validate_rules.py)

## Phases

1. Opus drafts skill.md content → quality check against ACs
2. Write skill.md
3. Update claude-create-skill (add step 8 reminder)
4. Update INDEX.md
5. task-complete
