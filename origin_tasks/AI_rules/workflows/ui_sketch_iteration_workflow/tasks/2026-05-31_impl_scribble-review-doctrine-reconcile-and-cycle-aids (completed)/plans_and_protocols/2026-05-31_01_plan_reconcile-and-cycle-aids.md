# Plan: TASK-PROC-032-12 — Scribble Review Doctrine Reconcile and Cycle Aids

## Objective

Four ACs targeting two doc/ files, two skill files, and two agent files:

| AC | Target | Change |
|----|--------|--------|
| AC-28 | `doc/presentation/heuristics/README.md` + `ui-scribble-heuristics-reviewer` agent | De-provisionalize corpus; drop PROVISIONAL caveat |
| AC-29 | `ui-scribble-auto-review` skill | Add even-version auto-review brief + inter-version structural diff toggle |
| AC-30 | `ui-scribble-persona-walker` agent | Add screen-level two-persona conflict surfacing with DDR link or upstream routing |
| AC-31 | `ui-scribble-iterate` skill | Add iteration-fatigue rail with requ-explore recommendation |

## Source files read during planning

- `doc/presentation/heuristics/README.md` — PROVISIONAL marker on lines 3-8
- `doc/presentation/heuristics/nielsen_usability.md` — solid, no double-ownership issues
- `doc/presentation/heuristics/universal_design.md` — solid
- `doc/presentation/heuristics/microinteractions.md` — solid
- `doc/presentation/heuristics/dark_patterns.md` — solid
- `doc/presentation/heuristics/motion_as_function.md` — solid
- `.claude/agents/ui-scribble-heuristics-reviewer.md` — PROVISIONAL caveat in corpus section
- `.claude/agents/ui-scribble-persona-walker.md` — no cross-persona conflict logic
- `.claude/skills/ui-scribble-auto-review/SKILL.md` — 6 steps; no brief/diff step
- `.claude/skills/ui-scribble-iterate/SKILL.md` — no fatigue rail

## Reconciliation verdict for AC-28

The five heuristic files are already well-structured with proper overlap notes / "What this corpus is NOT" sections that defer to:
- `persona-walker` and `rule-reviewer` for persona-specific and T1/T2 binding detail
- `../accessibility/` for WCAG specifics

No double-ownership exists. The corpus is ready to be canonical. The PROVISIONAL marker in README.md and the agent caveat are the only changes needed.

## Phase 1 — AC-28: De-provisionalize

1. Edit `doc/presentation/heuristics/README.md`:
   - Remove lines 3-8 (the `> **STATUS: PROVISIONAL (2026-05-30).**` block)

2. Invoke `claude-modify-agent` for `ui-scribble-heuristics-reviewer`:
   - Remove the provisional caveat block: `> Corpus status: PROVISIONAL pending ...`
   - Replace with a positive statement: `> Corpus status: **Canonical** (reconciled 2026-05-31). Apply the documented checks; do not invent beyond them.`

## Phase 2 — AC-29: Auto-review brief + structural diff

Invoke `claude-modify-skill` for `ui-scribble-auto-review`:
- After current step 4 (Regenerate), insert a new step **4.5 — Auto-review brief + structural diff**:

```
4.5 **Auto-review brief + structural diff** (even versions only):
After v{n+1} is generated:
- Compute a structural diff between v{n} and v{n+1}: which screens are new, changed, or unchanged; for changed screens, which annotated elements/states/components were added, modified, or removed.
- Emit `scribbles/v{n+1}/auto_review_brief.md` containing:
  - **What changed this round**: gaps that were addressed and how.
  - **What to focus on**: specific screens or elements that need reviewer attention; any gaps carried forward with rationale.
  - **Diff summary**: a per-screen table (screen | status: unchanged/changed/added | key changes), each "changed" row linking to `<screen_file.html>#diff-toggle`.
- For each changed screen's HTML, inject a diff toggle immediately after `<body>` and mark changed/added/removed elements:
  ```html
  <div class="diff-toolbar"><label><input type="checkbox" id="diff-toggle" onchange="document.body.classList.toggle('diff-on',this.checked)"> Show changes from v{n}</label></div>
  <style>#diff-toggle~* .diff-added{outline:2px solid #4caf50;outline-offset:2px} #diff-toggle~* .diff-changed{outline:2px dashed #2196f3;outline-offset:2px} #diff-toggle~* .diff-removed{opacity:0.35;text-decoration:line-through} body:not(.diff-on) .diff-added, body:not(.diff-on) .diff-changed, body:not(.diff-on) .diff-removed{outline:none;opacity:1;text-decoration:none}</style>
  ```
  Wrap each changed/added/removed element with `class="diff-changed"` / `class="diff-added"` / `class="diff-removed"`.
  Unchanged screens receive no diff markup.
- Add `auto_review_brief_path: scribbles/v{n+1}/auto_review_brief.md` to the return value passed to `ui-scribble-iterate`.
```

- Renumber: old step 5 becomes step 6, old step 6 becomes step 7. Update the return step to include `auto_review_brief_path`.

## Phase 3 — AC-30: Persona-conflict surfacing

Invoke `claude-modify-agent` for `ui-scribble-persona-walker`:
- After the per-persona walk section, add a **## Cross-persona conflict check** section:

```
## Cross-persona conflict check

After completing the walk for all personas, compare their per-screen constraints:

For each screen: if persona A's PRIMARY constraint and persona B's PRIMARY constraint are INCOMPATIBLE on the same element (e.g. A requires a 2-line label but B requires a single-word label; A requires high information density but B requires maximum simplicity; A needs 64dp tap targets everywhere but B's flow suggests smaller dense controls):

1. Record: `{persona_a, persona_b, screen_file, element, constraint_a, constraint_b, conflict_type}`
2. Determine resolution scope:
   - **DDR scope**: the conflict can be resolved within this scribble as a documented design trade-off → include in the `conflict_points[]` output with `resolution: "ddr_needed"` and a recommendation to create `scribbles/v{n}/ddr_<screen>_<element>.md`.
   - **Upstream scope**: resolution requires separate flows, a VCD boundary change, or a requirement scope change → include with `resolution: "upstream_routing"` and note it must go through `requ-explore` on the upstream requirement.

When no cross-persona conflicts exist: note `"cross_persona_conflicts": []`.
```

- Update the **On exit** output format to include `conflict_points[]`.

## Phase 4 — AC-31: Iteration-fatigue rail

Invoke `claude-modify-skill` for `ui-scribble-iterate`:
- Add a **FATIGUE_THRESHOLD** constant note near the top: `(iteration-fatigue threshold: v6+)`
- At the start of **Phase 3 (Await User Review)**, add a fatigue check before presenting to the developer:

```
### Fatigue check (Phase 3 only; run before presenting to developer)
If n ≥ 6 AND the gap summary from Phase 2 contains unresolved gaps:
  - **Interactive mode**: present a fatigue notice to the developer:
    > Iteration-fatigue notice: This scribble is at v{n} with unresolved gaps. Continuing to iterate risks generating noise instead of resolving a genuine requirement ambiguity. Recommendation: pause and run `requ-explore` on the underlying requirement to clarify it before generating v{n+1}. Options: (a) Proceed, (b) Pause — run requ-explore, (c) Approve as-is (open gaps acknowledged).
  - **Automated mode** (`CLAUDE_AUTOMATED_MODE=1`): write `scribbles/fatigue_warning.md` with the above, route to `pending_feedback`, and terminate — do not iterate past the fatigue threshold without human confirmation.
If n < 6 OR no unresolved gaps: proceed normally.
```

## Execution approach

- Inline (main session) for README.md edit (AC-28 part 1)
- `claude-modify-agent` invocations for agent changes (AC-28 part 2, AC-30)
- `claude-modify-skill` invocations for skill changes (AC-29, AC-31)
- No code files; no quality gates needed (process/doc artifacts only)
- Commit via `task-complete`
