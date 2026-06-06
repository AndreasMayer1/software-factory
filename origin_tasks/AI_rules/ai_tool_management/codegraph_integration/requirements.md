---
id: REQ-PROC-038
status: active
created: 2026-03-14
stakeholder: developer
after: []
blocks: []
market_research_refs: [] # No relevant findings identified — internal AI workflow tooling
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "CodeGraph CLI is installed globally and `codegraph --version` returns a version string"
      target_release: ~
    - id: AC-02
      text: "`.codegraph/` directory exists in project root with an initialized and up-to-date knowledge graph index"
      target_release: ~
    - id: AC-03
      text: "Skill is present at `.claude/skills/codegraph/skill.md` with correct name/description frontmatter"
      target_release: ~
    - id: AC-04
      text: "`code-complex` skill invokes `codegraph context` before spawning the architecture-advisor agent"
      target_release: ~
    - id: AC-05
      text: "`code-bugfix` skill invokes `codegraph context` before Opus bug investigation planning"
      target_release: ~
    - id: AC-06
      text: "`requ-explore` skill invokes `codegraph context` in Phase 1.5 before the Glob/Grep exploration loop"
      target_release: ~
  sections:
    - id: SEC-01
      name: "Integration Points in Code Skills"
      target_release: ~
    - id: SEC-02
      name: "Index Maintenance"
      target_release: ~
---

# CodeGraph Integration for AI Workflow

## Overview

CodeGraph is a semantic code intelligence tool that builds a local SQLite knowledge graph from the project codebase using tree-sitter parsing. It provides symbol search (`codegraph query`), task-aware context building (`codegraph context`), and code structure analysis — all locally without API keys.

This requirement governs how and when AI agents in this project use CodeGraph to reduce token consumption and improve codebase navigation quality.

## Purpose

AI agents currently navigate the codebase using Glob (file pattern matching) and Grep (content search), then Read files one by one. For complex tasks, this requires multiple round-trips before an agent understands which files are relevant.

CodeGraph collapses this into a single command: `codegraph context "<task description>"` returns semantically related code nodes, their source, and relationships — often covering the full relevant scope in one call.

**Primary benefit**: Fewer tool calls → lower token cost → faster context building → better planning quality for complex tasks.

## Setup State

| Artifact | Location | Status |
|----------|----------|--------|
| CodeGraph CLI | global npm | v0.6.2 installed |
| Knowledge graph | `.codegraph/` | Initialized (1,457 files / 15,775 nodes) |
| Skill | `.claude/skills/codegraph/skill.md` | Installed |

The `.codegraph/` directory is in `.gitignore` (each developer initializes locally). The skill file is version-controlled.

## When to Use

Use `codegraph context` **before** spawning exploration agents or doing manual Glob/Grep exploration when:
- Exploring which files are relevant to a task description
- Understanding code relationships across multiple files
- Investigating a bug (find affected code areas)
- Looking for existing implementations of a pattern

Use `codegraph query` as a faster alternative to Grep when:
- Searching for a specific symbol (class, function, method) by name
- Finding where a symbol is defined or used

## When NOT to Use

| Situation | Use instead |
|-----------|-------------|
| Finding files by path pattern | `Glob` |
| Finding all tests in a directory | `Grep` |
| The `.codegraph/` directory is missing | Run `codegraph init -i` first, or fall back to Glob/Grep |
| Searching documentation/markdown | `Grep` |
| Symbol search returns no results | `Grep` as fallback |

## Behavior (SEC-01): Integration Points in Code Skills

### code-complex (Highest Priority)

Before spawning the `architecture-advisor` agent, run:

```bash
codegraph sync  # ensure index is fresh
codegraph context "<task description>" --max-nodes 30
```

Pass the output to the architecture-advisor agent as initial context. This reduces the number of Glob/Grep/Read calls the agent needs to orient itself.

### code-bugfix (High Priority)

During bug investigation (before producing the fix plan), run:

```bash
codegraph context "<bug description>" --max-nodes 20
```

Include the output in the plan's context.

### requ-explore (Medium Priority)

In Phase 1.5 (Analyze Implementation), before Glob/Grep exploration:

```bash
codegraph context "<requirement topic>" --max-nodes 20
```

Use results to narrow which files to Read for concrete examples.

### code-simple / code-test (Low Priority)

After reading goal.md, optionally run:

```bash
codegraph context "<task name>" --max-nodes 10
```

Skip if task is clearly self-contained (goal.md already specifies exact file to edit).

## Behavior (SEC-02): Index Maintenance

The knowledge graph must stay fresh to be useful.

- **After significant code changes**: run `codegraph sync` (incremental, only changed files)
- **If results seem stale**: run `codegraph sync` before `codegraph context`
- **Full re-index**: `codegraph index --force` (rare — only if index is corrupted)
- **Automatic sync**: install git hooks with `codegraph hooks install` (optional, keeps index updated on commit)

## Developer Guidelines

### Decision Guide

| Task | Command |
|------|---------|
| Understand code relevant to a task | `codegraph context "<description>"` |
| Find a symbol by name | `codegraph query "<name>"` |
| Check what is indexed | `codegraph status` |
| Update after code changes | `codegraph sync` |

### Graceful Degradation

If `codegraph` is not installed or `.codegraph/` is missing, agents fall back to Glob/Grep without error. CodeGraph is an enhancement, not a hard dependency.

### Adding to New Skills

When writing a new skill that does codebase exploration, add a "CodeGraph First" step before any Glob/Grep loop:

```bash
# Optional: build semantic context before manual exploration
codegraph context "<task-description>" --max-nodes 20
```

## Acceptance Criteria

- AC-01: CodeGraph CLI is installed globally and `codegraph --version` returns a version string
- AC-02: `.codegraph/` directory exists in project root with an initialized and up-to-date index
- AC-03: Skill is present at `.claude/skills/codegraph/skill.md` with correct frontmatter
- AC-04: `code-complex` skill invokes `codegraph context` before spawning architecture-advisor
- AC-05: `code-bugfix` skill invokes `codegraph context` before Opus planning
- AC-06: `requ-explore` skill invokes `codegraph context` in Phase 1.5 before Glob/Grep loop

## Related Requirements

- `requirements_tasks/process/AI_rules/ai_tool_management/roo_code_deprecation/` — prior AI tool management precedent
- `requirements_tasks/process/AI_rules/coding_standards/context_window/requirements.md` — context efficiency rules

## References

- CodeGraph GitHub: https://github.com/colbymchenry/codegraph
- Skill source: `.claude/skills/codegraph/skill.md`
- Integration plan: `requirements_tasks/process/AI_rules/ai_tool_management/codegraph_integration/tasks/2026-02-07_explore_codegraph_integration/plans_and_protocols/2026-03-14_01_plan_codegraph_integration.md`
