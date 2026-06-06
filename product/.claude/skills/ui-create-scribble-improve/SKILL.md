---
name: ui-create-scribble-improve
description: Autonomously improve scribble generation via vision-evaluated iteration loop
tools: "*"
model: inherit
---

You autonomously improve `.claude/agents/ui-scribble-generator.md` (the scribble generation agent, post TASK-PROC-044-07 split) by generating scribbles, evaluating them with vision, and applying targeted fixes — without user feedback during the loop.

## Step 0 — Task Bootstrap (if called without goal.md path)

If no goal.md path argument was passed:
- Invoke `task-create` skill: new task under REQ-PROC-032-02, type `impl`, effort `L`
- Use urgency/impact from REQ-PROC-032 frontmatter
- After task is created, continue with Step 1 using the new goal.md path

## Step 1 — Worktree Setup

```bash
DATE=$(date +%Y%m%d)
BRANCH="improve/scribble-skill-$DATE"
WORKTREE="$(git rev-parse --show-toplevel)/../scribble-improve-worktree"
git worktree add "$WORKTREE" -b "$BRANCH"
```

All skill edits, scribble generation, and commits happen inside `$WORKTREE`.

Create `[task_folder]/plans_and_protocols/iteration_log.md` with header:
```markdown
# Scribble Skill Improvement Log
branch: improve/scribble-skill-{DATE}
worktree: {WORKTREE}
started: {YYYY-MM-DD}

## Fixtures
(populated in Step 2)

## Iterations
(populated in Step 3)
```

## Step 2 — Fixture Selection

Grep `requirements_tasks/functional/**/requirements.md` for `personas_served:` (non-empty). Select 3:
- **Simple**: requirement with 1-2 screens (short AC list, single flow step)
- **Medium**: requirement with 3-5 screens (multi-step AC list)
- **Complex**: requirement that references a user flow (`implements_flows:` populated)

Write selected fixture paths and rationale to `iteration_log.md` under `## Fixtures`.

## Step 3 — Iteration Loop (max 5 iterations)

After each iteration, check termination:
- Average score across all fixtures ≥ 25.6/32 → done (target reached)
- No criterion improved for 2 consecutive iterations → done (plateau)
- Iteration count = 5 → done (budget exhausted)

On termination: append `## Final Summary` to `iteration_log.md` and print: `Branch ready for PR: $BRANCH`

### Sub-agent A — Generator (spawn one per fixture, run in parallel)

Each generator agent receives a fresh context window. Pass:
- Path to `$WORKTREE/.claude/agents/ui-scribble-generator.md` (current version under improvement)
- Path to fixture's `requirements.md`
- Paths to relevant personas under `requirements_user_needs/personas/`
- Paths to all T1/T2 rules under `doc/presentation/design/`

Agent task:
> Follow the Phase 1 rules in the provided skill.md. Generate a scribble into `$WORKTREE/scribbles/{fixture_short_name}/v{n}/` (not the fixture's own scribbles/ folder — this is a test workspace). Produce: `index.html`, one `NN_<screen>.html` per screen, `metadata.yaml`, `feedback.md`.
> Also: consult `concept_canon.yaml` for label alignment; annotate canonical labels with `<!-- canon: CONCEPT-X -->`.

### Sub-agent B — Vision Evaluator (spawn one per generated scribble, sequential per fixture)

Each evaluator agent receives a fresh context window. Pass the generated HTML files as vision input (read each `.html` file) and the fixture's `requirements.md`.

Agent task:
> Score the scribble against the 16-criterion rubric. For each criterion score 0 (missing), 1 (partial), or 2 (complete). Write one sentence of evidence per criterion. Output to `$WORKTREE/evaluations/evaluation_{fixture_short_name}_iter{N}.yaml`:

```yaml
fixture: {short_name}
iteration: {N}
total: {sum}/32
criteria:
  component_mapping_block: {0|1|2}
  component_mapping_block_evidence: "..."
  persona_constraints_applied: {0|1|2}
  persona_constraints_applied_evidence: "..."
  wireframe_level: {0|1|2}
  wireframe_level_evidence: "..."
  ac_coverage_demonstrated: {0|1|2}
  ac_coverage_demonstrated_evidence: "..."
  md3_widget_labels_correct: {0|1|2}
  md3_widget_labels_correct_evidence: "..."
  screen_hierarchy_legible: {0|1|2}
  screen_hierarchy_legible_evidence: "..."
  flow_positions_accuracy: {0|1|2}
  flow_positions_accuracy_evidence: "..."
  t1_t2_rules_enforced: {0|1|2}
  t1_t2_rules_enforced_evidence: "..."
  md3_navigation_pattern: {0|1|2}
  md3_navigation_pattern_evidence: "..."
  md3_dialog_pattern: {0|1|2}
  md3_dialog_pattern_evidence: "..."
  states_happy_and_empty: {0|1|2}
  states_happy_and_empty_evidence: "..."
  states_loading_and_error: {0|1|2}
  states_loading_and_error_evidence: "..."
  a11y_semantic_roles: {0|1|2}
  a11y_semantic_roles_evidence: "..."
  a11y_easy_language: {0|1|2}
  a11y_easy_language_evidence: "..."
  component_library_references: {0|1|2}
  component_library_references_evidence: "..."
  ux_heuristics_sampled: {0|1|2}
  ux_heuristics_sampled_evidence: "..."
```

**16-Criterion Rubric** (32 points total):

| # | Criterion | What to check |
|---|---|---|
| A1 | component_mapping_block | Block present in all files; every interactive element in body has a mapping entry using current M3 widget names |
| A2 | persona_constraints_applied | Every cited PERSONA-ID has ≥1 observable enforcement in HTML body (style, label text, structural choice) — not comment-only |
| A3 | wireframe_level | Greyscale only; no saturated hex colors, no box-shadow, no transitions, no animations, border-radius ≤12px |
| A4 | ac_coverage_demonstrated | Every AC has ≥1 HTML body element that visually demonstrates it — not just a comment reference |
| A5 | md3_widget_labels_correct | Labels present AND contextually correct per M3 hierarchy (FilledButton for primary, NavigationBar not BottomNavigationBar, correct AppBar variant) |
| A6 | screen_hierarchy_legible | Primary action most prominent; destructive visually subordinate; heading levels correctly reflect content hierarchy |
| A7 | flow_positions_accuracy | flow_positions present with non-null step_numbers and all cited files exist (auto-2 if no flow reference) |
| A8 | t1_t2_rules_enforced | Every cited rule has ≥1 observable enforcement in body HTML; no rule cited but contradicted by body styling |
| B1 | md3_navigation_pattern | Nav widget matches structural role: NavigationBar for primary destinations, AppBar+back for detail, no nav bar on modals |
| B2 | md3_dialog_pattern | Correct dialog type (AlertDialog/SimpleDialog/ModalBottomSheet); cancel action comes FIRST in dialog actions |
| C1 | states_happy_and_empty | Every list/collection screen has populated + empty state; empty state has explanation + CTA |
| C2 | states_loading_and_error | Every async screen has loading + error state panels; error messages in plain language with recovery action |
| D1 | a11y_semantic_roles | Custom div interactive elements have `<!-- aria: role=..., label="..." -->` annotation; icons marked decorative or informative |
| D2 | a11y_easy_language | All label text plain and direct for cognitive-constraint personas; action labels describe outcomes (auto-2 if no cognitive persona) |
| E1 | component_library_references | components.js script tag present; patterns matching library components have `<!-- uses: c_xxx -->` in mapping block |
| F1 | ux_heuristics_sampled | Async operations show status indicator; terminology consistent across screens; destructive actions have confirmation step |

### Sub-agent C — Improvement Planner (one per iteration, after all B agents complete)

Receives: all `evaluation_*_iter{N}.yaml` files from the current iteration.

Agent task:
> 1. Compute per-criterion average across all fixtures.
> 2. Identify the single criterion with the lowest average score from the 16-criterion rubric (total: 32 points).
> 3. Formulate ONE atomic, concrete change to `skill.md` text that would raise that criterion's score. The change must: target only `skill.md` (not scribble files or test fixtures), not require external tools, not break Phase 1-5 for `draft_generator: none` + no `inputs/`.
> 4. Write `$WORKTREE/proposals/proposed_change_iter{N}.md`:

```markdown
# Proposed Change — Iteration {N}
target_criterion: {criterion_name}
current_avg_score: {X}/2
expected_score_delta: +{Y}
worst_fixture: {fixture_short_name}

## Change
[Exact text to add/replace in skill.md — include before/after if modifying existing text]

## Rationale
[One paragraph: why this change addresses the criterion gap]
```

### Sub-agent D — Skill Updater (one per iteration, after C completes)

Receives: `proposed_change_iter{N}.md` and the worktree path.

Agent task:
> 1. Apply the proposed change to `$WORKTREE/.claude/agents/ui-scribble-generator.md`.
> 2. Spawn a new Generator sub-agent (same as A) for the worst-scoring fixture only — generating `v{n+1}/` into `$WORKTREE/scribbles/{worst_fixture}/v{n+1}/`.
> 3. Spawn a new Vision Evaluator sub-agent (same as B) on the regenerated scribble — writing `evaluation_{worst_fixture}_iter{N}_recheck.yaml`.
> 4. Compare recheck total vs. original total for that fixture:
>    - If recheck total ≥ original total: `cd $WORKTREE && git add .claude/agents/ui-scribble-generator.md && git commit -m "improve(scribble-skill): iter{N} — {criterion_name} (+{delta})"` (run add and commit as separate commands)
>    - If recheck total < original total: `cd $WORKTREE && git checkout .claude/agents/ui-scribble-generator.md` (revert); log "REVERTED: change did not improve score"
> 5. Append to `[task_folder]/plans_and_protocols/iteration_log.md`:

```markdown
## Iteration {N}
criterion_targeted: {name}
proposed_change: proposals/proposed_change_iter{N}.md
fixture_scores_before: {fixture1}={X}/32, {fixture2}={Y}/32, {fixture3}={Z}/32
fixture_scores_after_recheck: {worst_fixture}={W}/32
outcome: committed | reverted
```

> **Step D-5: Component candidate harvest**
>
> After the skill.md commit (or revert), parse all screen HTML files in `$WORKTREE/scribbles/{worst_fixture}/v{n+1}/` for:
> - `<!-- component-candidate: c_xxx -->` annotations
> - `<!-- uses-candidate: c_xxx -->` annotations (confirms c_xxx appears in multiple screens)
>
> For each unique `c_xxx` found as a `component-candidate` AND confirmed by a `uses-candidate` annotation in a different screen:
>
> 1. **Check existence**: Does `requirements_tasks/_scribble_components/c_xxx/` exist?
>
> 2. **If missing — create**:
>    - Create `requirements_tasks/_scribble_components/c_xxx/component.html` with the HTML fragment extracted from the first screen (structural pattern, stripped of screen-specific content, parameterized with placeholder labels)
>    - Create `requirements_tasks/_scribble_components/c_xxx/metadata.yaml`:
>      ```yaml
>      component: c_xxx
>      flutter_widget: [widget name from COMPONENT MAPPING block]
>      material3_variant: "[variant if known, or 'standard']"
>      tier: T2
>      rules_applied: []
>      last_updated: [today]
>      description: "[one-line description]"
>      personas_applied: []
>      ```
>
> 3. **If exists — check compatibility**: Compare structure to new usage. If new usage introduces additional required fields: update `component.html` with compatible superset, bump `last_updated`, append `changelog:` entry `{date, change, reason}`.
>
> 4. **Commit component changes** (run add and commit as separate commands):
>    ```bash
>    cd $WORKTREE
>    git add requirements_tasks/_scribble_components/
>    git commit -m "chore(scribble-components): iter{N} — add/update c_xxx from {worst_fixture}"
>    ```
>
> 5. **Log to iteration_log.md**: Add a `## Component Changes — Iteration {N}` subsection listing each component created or updated.

## Constraints

- Improvement Planner MUST NOT propose: changes to scribble artifacts, changes to `ui-verify-flutter` or `ui-improve-flutter`, changes requiring new external tools, more than one change per iteration
- Generator MUST write to `$WORKTREE/scribbles/` not to `requirements_tasks/`
- All git operations run inside `$WORKTREE` (not main working tree)
- `CLAUDE_AUTOMATED_MODE=1` check: if automated mode is active, skip any interactive prompts in sub-agents
