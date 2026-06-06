# CodeGraph Integration Plan

**Date**: 2026-03-14
**Task**: TASK-PROC-012-01
**Status**: Setup complete, requirements written

---

## Setup Completed

| Step | Status | Details |
|------|--------|---------|
| CodeGraph CLI installed | DONE | v0.6.2 via `npm install -g @colbymchenry/codegraph` |
| Project initialized | DONE | `codegraph init -i` in project root |
| Skill installed | DONE | Copied from `codegraph-skill-main/SKILL.md` → `.claude/skills/codegraph/skill.md` |

**Index stats (after init):**
- Files: 1,457 (418 Dart, 679 C, 338 C++, 9 Python, 6 Swift, 5 Kotlin, 2 JS)
- Nodes: 15,775 | Edges: 27,208 | DB size: 41.23 MB
- Status: up to date

---

## Skills Integration Analysis

### High-Value Integration Points (Add CodeGraph Context Step)

These skills do heavy codebase exploration before spawning agents:

#### 1. `code-complex` — architecture-advisor agent (HIGHEST VALUE)
- **Where**: Step 2 (Plan) — before spawning architecture-advisor agent
- **What to add**: Run `codegraph context "<task description>" --max-nodes 30` and pass results to the architecture-advisor agent prompt
- **Why**: Architecture-advisor does extensive Glob/Grep/Read. CodeGraph context in one call often covers the relevant code without file-by-file reading.

#### 2. `code-bugfix` — bug investigation (HIGH VALUE)
- **Where**: Resume run Step 3 (collect new information) — before Opus planning
- **What to add**: Run `codegraph context "<bug description>" --max-nodes 20` and include in the context passed to `claude-workflow-opus`
- **Why**: Bug investigation requires fast symbol lookup and understanding of code relationships — exactly what CodeGraph excels at.

#### 3. `requ-explore` — codebase analysis step (MEDIUM VALUE)
- **Where**: Phase 1.5 (Analyze Implementation) — before Glob/Grep exploration
- **What to add**: Run `codegraph context "<requirement topic>" --max-nodes 20` as first step
- **Why**: Finding existing implementations of a pattern is expensive via Glob+Read; CodeGraph surfaces relevant files immediately.

#### 4. `code-simple` / `code-test` — lightweight context (LOW-MEDIUM VALUE)
- **Where**: Step 2 (Read & Assess) — after reading goal.md
- **What to add**: Run `codegraph context "<task name>" --max-nodes 10` for quick orientation
- **Why**: Even for small tasks, knowing which existing files are related saves at minimum one Glob round-trip.

### Skills Where CodeGraph Adds No Value
- `requ-*` (non-implementation): text/document oriented, no code exploration
- `ux-*`, `vcd-*`: persona/scenario work, no code
- `task-*`: lifecycle management, no code exploration
- `doc-update-tokens`: token file editing, no structural exploration
- `release`, `requ-prep-release`: process automation

---

## Implementation Recommendations

### Pattern to Add to Code Skills

Add this **before** any Glob/Grep/Read exploration or before spawning exploration agents:

```bash
# Build semantic context for the task (before manual exploration)
codegraph sync  # ensure index is fresh
codegraph context "<task description>" --max-nodes 20
```

### Decision Guide: CodeGraph vs. Traditional

| Situation | Use CodeGraph | Use Glob/Grep |
|-----------|--------------|---------------|
| "What files are related to feature X?" | YES — `codegraph context "X"` | Only as fallback |
| "Where is symbol Foo defined?" | YES — `codegraph query "Foo"` | If codegraph returns nothing |
| "Find all files matching *.dart" | NO | YES — Glob |
| "Find all tests in test/" | NO | YES — Grep |
| ".codegraph/ missing" | Init first or skip | YES |

### Maintenance

- Run `codegraph sync` after significant code changes (incremental, fast)
- Git hooks can automate this: `codegraph hooks install`
- Full re-index if needed: `codegraph index --force`

---

## Next Steps (Future Implementation Tasks)

1. Modify `code-complex` skill to add CodeGraph context step before architecture-advisor
2. Modify `code-bugfix` skill to add CodeGraph context in bug investigation
3. Modify `requ-explore` skill to add CodeGraph context in Phase 1.5
4. Optionally: modify `code-simple` / `code-test` for lightweight context
5. Consider installing git hooks: `codegraph hooks install`
