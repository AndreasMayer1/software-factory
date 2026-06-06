# Protocol: TASK-PROC-032-12 Execution

Session: 923f7c3f-6d7b-421c-a96d-9f579526711e (main session)

## Phase 1 — AC-28: De-provisionalize heuristics corpus

**Background agent** (a74349ba350852000) completed phases 1A and 1B.

### 1A — doc/presentation/heuristics/README.md
- Removed the 6-line PROVISIONAL status block (lines 3-8)
- File now opens directly with `## Purpose` — no provisional caveat

### 1B — .claude/agents/ui-scribble-heuristics-reviewer.md
- Replaced: `> Corpus status: PROVISIONAL pending the REQ-PROC-032 requ-explore reconciliation…`
- With: `> Corpus status: **Canonical** (reconciled 2026-05-31, TASK-PROC-032-12). Apply the documented checks; do not invent beyond them.`

**Reconciliation verdict**: All five heuristic files (nielsen_usability.md, universal_design.md, microinteractions.md, dark_patterns.md, motion_as_function.md) have correct overlap notes and scope boundaries. No double-ownership with persona-walker or rule-reviewer. Corpus was ready to be canonical.

## Phase 2 — AC-29: Auto-review brief + structural diff

**File**: `.claude/skills/ui-scribble-auto-review/SKILL.md`
**Change**: Inserted step 4.5 after step 4 (Regenerate):
- Computes structural diff between v{n} and v{n+1}
- Emits `scribbles/v{n+1}/auto_review_brief.md` with focus areas + diff summary table
- Injects diff toggle HTML into changed screens' `<body>` with diff-added/diff-changed/diff-removed classes
- Updated return step (step 6) to include `auto_review_brief_path`

**Phase split**: Score 2/4 — inline step, tightly coupled to regeneration output. No split.

## Phase 3 — AC-30: Persona-conflict surfacing

**File**: `.claude/agents/ui-scribble-persona-walker.md`
**Change**: Added `## Cross-persona conflict check` section after the per-persona walk:
- Records incompatible constraints: `{persona_a, persona_b, screen_file, element, constraint_a, constraint_b}`
- Determines resolution scope: DDR (within-scribble trade-off) vs. upstream routing (flow/VCD change needed)
- Output now includes `conflict_points[]`

**Additional**: Added all required §4 governed sections (Domain Vocabulary, Anti-Patterns, Protocols, Output, Rules) — these were absent pre-edit.
**Contract sidecar created**: `.claude/agents/ui-scribble-persona-walker.contract.yaml`

## Phase 4 — AC-31: Iteration-fatigue rail

**File**: `.claude/skills/ui-scribble-iterate/SKILL.md`
**Change**: Added `### Fatigue check` subsection at the start of Phase 3:
- Triggers at n ≥ 6 with unresolved gaps
- Interactive: presents pause recommendation with 3 options (proceed / pause+requ-explore / approve as-is)
- Automated: writes `scribbles/fatigue_warning.md` and routes to pending_feedback
**Also added**: fatigue threshold note to `## Constraints`

**Phase split**: Score 1/4 — inline guard. No split.

## AC Coverage

| AC | File changed | Satisfied by |
|----|-------------|--------------|
| AC-28 | README.md, heuristics-reviewer.md | PROVISIONAL removed; agent caveat → Canonical |
| AC-29 | ui-scribble-auto-review/SKILL.md | Step 4.5 with brief + diff toggle |
| AC-30 | ui-scribble-persona-walker.md, contract.yaml | Cross-persona conflict check section |
| AC-31 | ui-scribble-iterate/SKILL.md | Phase 3 fatigue check + threshold constraint |
