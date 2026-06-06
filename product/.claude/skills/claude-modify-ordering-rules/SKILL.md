---
name: claude-modify-ordering-rules
description: Modify or initialize .claude/task_ordering_rules.yaml
tools: Read, Write, Edit, Bash, Glob, Grep
model: inherit
---

You modify `.claude/task_ordering_rules.yaml` or initialize it for a new project. Scope is the rule file only — not the engine scripts under `scripts/task_ordering/`.

## Mode selection

```bash
test -f .claude/task_ordering_rules.yaml && echo MODIFY || echo INIT
```

## MODIFY workflow

1. **Read state** — current rule file + the change request. Note current `schema_version`.

2. **Classify change** (first match wins):

| Kind | Signal | Breaking? |
|---|---|---|
| Signal reorder | `ranking_signals` position change | yes → bump schema |
| Layer removal | `layers[*]` removed | yes → bump schema |
| Top-level key added/removed | new/removed top-level key | yes → bump schema |
| New layer | `layers[+]` | no |
| New flag or heuristic | `special_flags[+]` / `dependency_heuristics[+]` | no |
| Rationale / description edit | prose-only | no |

3. **Propose diff**
   - Write proposal to `.claude/task_ordering_rules.yaml.proposed`
   - Show `diff -u .claude/task_ordering_rules.yaml .claude/task_ordering_rules.yaml.proposed`
   - **If any `ranking_signals` entry changes position**: print the old and new `rationale:` + `rationale_source:` for each affected entry so the user reviews the original reasoning before approving
   - **If a new `ranking_signals` entry is added without `rationale:\` + `rationale_source:`**: reject the diff and fix before continuing

4. **Simulate (mandatory — never skip)**

   ```bash
   python3 scripts/task_ordering/simulate.py --proposed-rules .claude/task_ordering_rules.yaml.proposed --verbose
   ```

   Show output verbatim. Highlight `⚑SHIFT` rows (≥5 places), `UNCLASS` rows, and the Summary counts.

5. **Approve or reject** — ask user [Apply / Discard / Restart from step 2]:
   - **Apply**:
     1. `python3 scripts/task_ordering/validate_rules.py --rules .claude/task_ordering_rules.yaml.proposed` — if exit ≠ 0, STOP and show errors
     2. `mv .claude/task_ordering_rules.yaml.proposed .claude/task_ordering_rules.yaml`
     3. Update `updated:` to today; bump `schema_version` if the change is breaking (per step 2)
     4. `git add` then `git commit` as SEPARATE commands (CLAUDE.md §7): `chore(ordering): <kind>: <summary>`
   - **Discard**: `rm .claude/task_ordering_rules.yaml.proposed`
   - **Restart**: discard and loop to step 2

6. **Propagate** — surface dependents to the user:
   - `grep -rl "task_ordering_rules\|classify_layer\|rank_tasks" .claude/skills/`
   - Remind: update `.claude/factory_flows.md` only if the change introduces a new INPUT TYPE or ARTIFACT CONNECTION (most ordering edits do not)

## INIT workflow (rule file absent)

1. Spawn `opus-advisor` agent with this self-contained prompt:

   > Scan `requirements_tasks/`, `requirements_user_needs/`, `lib/`, and `test/` plus goal.md frontmatter (type, parent_requirement, target_package, source_gap, writes_requirements, scribble_task, verification_task, ...). Propose a starter `task_ordering_rules.yaml`:
   > - layer taxonomy with sparse `order` integers (10s)
   > - `path_glob` + `scope_key` per layer
   > - initial `ranking_signals` (each with `rationale:` and `rationale_source:`)
   > - minimal `special_flags`
   >
   > Write YAML to `plans_and_protocols/01_starter_rules.yaml` with a short taxonomy-rationale section.

2. Read the agent's output; present the proposed YAML + taxonomy rationale to the user; ask for approval.
3. On approval: copy to `.claude/task_ordering_rules.yaml`, run `validate_rules.py`, commit.
4. On rejection: adjust with the user and loop to step 2.

## Validation (enforced by validate_rules.py)

schema_version present & supported · layer required fields (name/order/match) · unique layer `order` values · unique layer names · `path_glob` sparsity (warn only) · `consumes:` references name an existing layer
