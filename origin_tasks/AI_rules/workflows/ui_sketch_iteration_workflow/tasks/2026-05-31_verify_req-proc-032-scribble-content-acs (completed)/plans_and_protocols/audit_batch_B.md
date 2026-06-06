# Audit Batch B — REQ-PROC-032 AC-28..AC-31

Auditor: agent (batch B) · 2026-06-02 · AUDIT-ONLY
Standard: producer artifact specifies behavior correctly AND consumers read it as the AC says.
Adversarial: a gesture without operative threshold/diff/reconciliation → PARTIAL.

---

## AC-28 — Heuristics corpus reconciled and canonical

Verdict: COVERED

- No PROVISIONAL marker anywhere in `doc/presentation/heuristics/` — `grep -n "PROVISIONAL|provisional"` returns "No matches found" across all six files (`README.md`, `nielsen_usability.md`, `universal_design.md`, `microinteractions.md`, `dark_patterns.md`, `motion_as_function.md`).
- All five required corpus areas present and content-complete:
  - Nielsen: `doc/presentation/heuristics/nielsen_usability.md:20-217` (H1–H10, each with Principle / What to check / Red flag) + checklist `nielsen_usability.md:221-232`.
  - Universal Design: `doc/presentation/heuristics/universal_design.md:23-166` (UD1–UD7) + checklist `:171-177`.
  - Microinteractions (Saffer): `doc/presentation/heuristics/microinteractions.md:20-98` (Trigger/Rules/Feedback/Loops&Modes) + checklist `:103-108`.
  - Dark patterns: `doc/presentation/heuristics/dark_patterns.md:30-145` (9 patterns) + checklist `:161-169`.
  - Motion-as-function: `doc/presentation/heuristics/motion_as_function.md:30-93` (M1–M4) + decoration test `:96-110` + checklist `:115-121`.
- NO double-ownership — ownership boundaries are explicit and binding:
  - README "What this corpus is NOT" table assigns persona-trait constraints to `persona-walker`, T1/T2 specifics to `rule-reviewer`, WCAG specifics to `../accessibility/`, and instructs "Do NOT re-check here" / "defer to the owning surface": `doc/presentation/heuristics/README.md:14-28`.
  - Per-file deferral notes reinforce this: `nielsen_usability.md:14-17` (H3/H5/H9 → t2_destructive_actions + t1; "Do not restate dp values or persona tap budgets"), `nielsen_usability.md:153-156` (H7 budget owned by t1_interaction_budget + persona-walker), `universal_design.md:14-19` (WCAG → accessibility; dp/budget → t1 + persona-walker), `universal_design.md:75-77` and `:159-161`, `dark_patterns.md:19-22` (destructive placement → t2; deception axis owned here), `motion_as_function.md:22-24`.
- Reviewer applies it as canonical doctrine:
  - `.claude/agents/ui-scribble-heuristics-reviewer.md:12` — "Corpus status: **Canonical** (reconciled 2026-05-31, TASK-PROC-032-12). Apply the documented checks; do not invent beyond them."
  - Corpus listed as "your only source of doctrine": `.claude/agents/ui-scribble-heuristics-reviewer.md:10-19`.
  - Scope boundary binding the README table and forbidding re-report of persona-walker / rule-reviewer / accessibility concerns: `.claude/agents/ui-scribble-heuristics-reviewer.md:24-28`.

---

## AC-29 — Auto-review brief and inter-version diff

Verdict: COVERED

- (a) Auto-review brief telling the reviewer what to focus on:
  - `ui-scribble-auto-review` emits `scribbles/v{n+1}/auto_review_brief.md` with "What changed this round", "What to focus on: specific screens or elements needing reviewer attention", and per-flow walk instructions: `.claude/skills/ui-scribble-auto-review/SKILL.md:33-39`.
  - Returned to caller as `auto_review_brief_path`: `:47`.
- (b) Inter-version structural diff between prior and new version — an actual mechanism, not just prose:
  - Diff computed: "which screens are new, changed, or unchanged; for changed screens, which annotated elements/states/components were added, modified, or removed": `.claude/skills/ui-scribble-auto-review/SKILL.md:34`.
- Diff viewable via a TOGGLE in the scribble HTML that visually highlights changed elements:
  - Concrete injected HTML toolbar with `<input type="checkbox" id="diff-toggle" onchange="document.body.classList.toggle('diff-on',this.checked)">`: `.claude/skills/ui-scribble-auto-review/SKILL.md:42`.
  - Concrete CSS that visually highlights: `.diff-on .diff-added{outline:2px solid #4caf50}` / `.diff-changed{outline:2px dashed #2196f3}` / `.diff-removed{opacity:0.35;text-decoration:line-through}`: `:43`.
  - Affected elements get `class="diff-added"/"diff-changed"/"diff-removed"`; unchanged screens receive no diff markup: `:44-45`.
- Brief links to the diff:
  - Diff summary table rows for changed screens link `<screen_file.html>#diff-toggle`: `.claude/skills/ui-scribble-auto-review/SKILL.md:38` (anchor matches the injected `id="diff-toggle"` at `:42`).

Note (observation, not a gap): the brief is produced only after even-version regeneration in Phase 2, matching the AC ("After regenerating an even version").

---

## AC-30 — Persona-conflict surfacing with DDR link

Verdict: COVERED

- persona-walker surfaces screen-level conflicts and does NOT silently choose one persona:
  - Cross-persona conflict check records `{persona_a, persona_b, screen_file, element, constraint_a, constraint_b}`: `.claude/agents/ui-scribble-persona-walker.md:30-32`.
  - Anti-pattern explicitly forbids the silent-choice failure mode: "Silently choosing one persona over another when a conflict exists": `.claude/agents/ui-scribble-persona-walker.md:45`.
- Marks the conflict point + DDR link OR routes upstream — operative two-way reconciliation, not a gesture:
  - DDR scope: "set `resolution: \"ddr_needed\"`; recommend creating `scribbles/v{n}/ddr_<screen_abbrev>_<element_abbrev>.md` listing the conflict and two or more resolution options": `.claude/agents/ui-scribble-persona-walker.md:33-34`.
  - Upstream scope (flow/VCD/requirement change): "set `resolution: \"upstream_routing\"`; ... routed through `requ-explore` on the owning requirement": `.claude/agents/ui-scribble-persona-walker.md:35`.
  - Output contract carries `resolution: "ddr_needed" | "upstream_routing"` per conflict (empty array if none): `.claude/agents/ui-scribble-persona-walker.md:58`; `conflict_points: []` when none `:37`.
  - Domain vocabulary names DDR + upstream routing as first-class: `.claude/agents/ui-scribble-persona-walker.md:14`.
- "persona-walker OR heuristics review" — the AC's disjunction is satisfied by the persona-walker path; the heuristics reviewer feeds the same merged finding set in auto-review:
  - Both reviewers fan out in parallel and their findings merge into one set: `.claude/skills/ui-scribble-auto-review/SKILL.md:14-17`, `:28`.
- Upstream alternative honored at orchestration level (flow-flaw → revision task via `ux-create-flow`): `.claude/skills/ui-scribble-auto-review/SKILL.md:26`.

Note (observation, not a gap): the conflict-surfacing logic and the DDR/upstream branch are authored on the persona-walker side. The heuristics-reviewer agent itself does not independently emit a `conflict_point`; it contributes findings to the merge. Because AC-30 uses "or" (persona-walker OR heuristics review) and the persona-walker path fully implements mark-conflict + DDR-link + upstream-route, the AC is operatively satisfied. If a future reading requires heuristics-only conflicts to also carry an explicit DDR/upstream branch, that would be a separate enhancement.

---

## AC-31 — Iteration-fatigue detection

Verdict: COVERED

- ui-scribble-iterate detects iteration beyond a CONCRETE numeric threshold without convergence:
  - Defined numeric threshold: "If n ≥ 6 AND the gap summary from Phase 2 contains unresolved gaps (no convergence yet)": `.claude/skills/ui-scribble-iterate/SKILL.md:77`.
  - Restated as a hard rail: "Iteration-fatigue threshold: v6 with unresolved gaps → Phase 3 fatigue check surfaces a pause recommendation": `.claude/skills/ui-scribble-iterate/SKILL.md:108`.
- Surfaces a recommendation to pause and run requ-explore on the underlying requirement:
  - Interactive: notice recommends "pause and run `requ-explore` on the underlying requirement to clarify it first", with options (a) proceed, (b) Pause — run requ-explore, (c) approve as-is: `.claude/skills/ui-scribble-iterate/SKILL.md:78-80`.
  - Automated mode: writes `{SCRIBBLE_BASE}fatigue_warning.md`, routes to `pending_feedback`, terminates — "Do not iterate past the threshold without human confirmation": `.claude/skills/ui-scribble-iterate/SKILL.md:81`.
- Convergence condition is operative (not vague): the threshold gates on BOTH version count (n ≥ 6) AND presence of unresolved gaps in the Phase-2 gap summary; if `n < 6 OR no unresolved gaps` it proceeds normally: `.claude/skills/ui-scribble-iterate/SKILL.md:83`.

---

## Summary

| AC | Verdict |
|----|---------|
| AC-28 | COVERED |
| AC-29 | COVERED |
| AC-30 | COVERED |
| AC-31 | COVERED |

Count: COVERED 4 · PARTIAL 0 · NOT_COVERED 0 (of 4).
