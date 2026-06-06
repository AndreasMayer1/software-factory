# Skill Index - Software Factory

## Quick Reference: What do I want to do?

| I want to... | Skill | Command |
|-------------|-------|--------|
| Execute a task (ID, path, or "next task") | `task-start` | `/task-start` |
| Document a value trade-off | `vcd-log-tradeoff` | `/vcd-log-tradeoff` |
| Document/explore requirements | `requ-explore` | `/requ-explore` |
| Assign packages to unassigned requirements | `requ-assign-packages` | `/requ-assign-packages` |
| Begin implementation of a release | `release-begin-impl` | `/release-begin-impl` |
| Finalize implementation phase of a release | `release-begin-impl-finalize` | `/release-begin-impl-finalize` |
| Show where you are in the release workflow | `release-status` | `/release-status` |
| Execute a release (/release) | `release` | `/release` |
| Plan a release (assign packages to versions) | `release-plan` | `/release-plan` |
| Decompose requirement into impl tasks | `task-derive-from-requ` | `/task-derive-from-requ` |
| Create a Dart code task (lib/test/integration_test) | `task-create-code` | `/task-create-code` |
| Check if a blocked task can proceed | `task-unblock-check` | `/task-unblock-check` |
| Close a bugfix task (cleanup + complete) | `task-complete-bugfix` | `/task-complete-bugfix` |
| Start or resume a bugfix (slim or worktree mode) | `code-bugfix` | `/code-bugfix` |
| Implement something small | `code-simple` | `/code-simple` |
| Implement something large | `code-complex` | `/code-complex` |
| Write tests (TDD) | `code-test` | `/code-test` |
| Manage design tokens | `doc-update-tokens` | `/doc-update-tokens` |
| Modify task ordering rules | `claude-modify-ordering-rules` | `/claude-modify-ordering-rules` |
| Produce one improvement task from an optimize event | `claude-optimize` | `/claude-optimize` |
| Score the optimizer loop's effectiveness (deterministic) | `claude-optimize-audit` | `/claude-optimize-audit` |
| **Not sure?** | `task-start` | `/task-start` |
| Go AFK, keep cache warm | `brb` | `/brb` |
| Write a git commit message | `claude-commit` | `/claude-commit` |
| Run quality gates as blocking checks | `verify-quality` | `/verify-quality` |
| Install an OS-level tool | `claude-install-os-tool` | `/claude-install-os-tool` |
| Brief on tool-output bug #63966 + 7-day upstream check (every Opus session) | `claude-watch-tool-reliability` | `/claude-watch-tool-reliability` |

---

## Skill Categories

### code-* (Flutter/Dart Code)
| Skill | When to use |
|-------|-------------|
| **code-simple** | Small changes (1-3 files, one layer) |
| **code-complex** | Large changes (4+ files, multiple layers, architecture impact) |
| **code-bugfix** | Bugfix workflow — slim mode (scripts/non-Flutter) or worktree mode (Flutter/Dart) |
| **code-test** | Write tests (TDD workflow) |
| **code-run-integration** | Run integration tests individually |

### requ-* (Requirements)
| Skill | When to use |
|-------|-------------|
| **requ-explore** | Document new requirement or explore/complete existing ones — **MUST be used to add or modify requirements** |
| **requ-derive-from-flow** | Analyze user flow(s) to find requirement gaps; reads notes.md for developer intent |
| **requ-assign-packages** | Bulk-assign target_package to unassigned requirement ACs; propagates to tasks |
| **requ-apply-market** | Apply market research findings to requirements |
| **requ-merge** | Merge requirement docs (called by task-complete) |
| **requ-verify-flow-coverage** | Verify and remediate flow–requirement coverage gaps after exploration tasks complete |

### release (Release Workflow)
| Skill | When to use |
|-------|-------------|
| **release-status** | Show where you are in the release workflow (run anytime) |
| **release-begin-impl** | Begin implementation of a release: verify requirements, activate release, create orchestration task |
| **release-begin-impl-finalize** | Post-creation review of an active release: coverage audit, after-chain reconciliation, semantic validation, user gate, finalize |
| **release** | Orchestrate full release: pre-flight check, git merge/tag/push, release notes, mark released |
| **release-plan** | Assign packages to versions in RELEASE_BACKLOG.md; update statuses |

### ui-* (UI Design)
| Skill | When to use |
|-------|-------------|
| **ui-scribble-iterate** | Generate and iterate structural HTML wireframe scribbles before Flutter implementation (orchestrator) |
| **ui-scribble-auto-review** | _(orchestrated by ui-scribble-iterate)_ Auto-review a scribble version and regenerate to fix gaps |
| **ui-scribble-feedback-classify** | _(orchestrated by ui-scribble-iterate)_ Classify scribble feedback and route to rule, requirement, or regeneration |
| **ui-scribble-approve-handoff** | _(orchestrated by ui-scribble-iterate)_ On scribble approval, emit the Flutter implementation handoff |
| **ui-create-scribble-improve** | Autonomously improve `ui-scribble-iterate` skill via vision-evaluated iteration loop |
| **ui-verify-flutter** | Verify Flutter implementation matches approved scribble (structural + rule check) |
| **ui-visual-validate** | Vision-compare integration-test screenshots against the approved scribble + verification_seeds (advisory, non-blocking) |
| **ui-improve-flutter** | Iterate visual quality of implemented Flutter screens (colors, spacing, polish) |

### ux-* (User Needs)
| Skill | When to use |
|-------|-------------|
| **ux-write-persona** | Create or update a persona — with cascade scan for scenario and flow impact |
| **ux-write-scenario** | Create or update a scenario — with cascade scan for flow coverage |
| **ux-write-canon-concept** | Add/update/rename canon concepts; required for new user-facing concepts |
| **ux-create-flow** | **Entry point for all new flow work** — detect mode, dispatch to sub-skills |
| ~~ux-flow-draft~~ | *(internal — do not call directly, use ux-create-flow)* |
| ~~ux-flow-complete~~ | *(internal — do not call directly, use ux-create-flow)* |
| ~~ux-flow-approve~~ | *(internal — do not call directly, use ux-create-flow)* |
| **ux-validate-rule** | Validate human UX proposals against personas |
| **vcd-log-tradeoff** | Document a Value Trade-off Record inline in an artifact |

### task-* (Task Lifecycle)
| Skill | When to use |
|-------|-------------|
| **task-derive-from-requ** | Decompose requirement into tasks with coverage matrix — **mandatory for requirements with ACs** |
| **task-create** | Initialize any task workspace (generic) — **MUST be used to create tasks** |
| **task-create-code** | Create Dart code task (lib/, test/, integration_test/) — **MUST be used to create code tasks** |
| **task-complete** | Mark task done, merge docs, update parent requirement — **MUST be used to complete tasks** |
| **task-complete-bugfix** | Remove debug artifacts from bugfix, then complete task |
| **task-repair-meta** | Audit and repair metadata across requirements_tasks |
| **task-unblock-check** | Investigate whether a blocked task can be unblocked |
| **task-start** | Canonical execution entry point — resolves ref (path/ID/"next task"/free-text), gates pre-conditions, marks in_progress, delegates to claude-route |
| **task-resolve** | Fallback for open-ended impl or non-requirement explore tasks with no specialized skill (docs, skills, analysis) |
| **verify-quality** | Run the project quality gates as blocking checks (five-cycle back-pressure protocol). Invoked by `task-complete` and the Stop / pre-commit hooks. |

### doc-* (Design Specification)
| Skill | When to use |
|-------|-------------|
| **doc-update-guidelines** | Synthesize doc/ guideline updates from protocols |
| **doc-split** | Split an oversized doc/ file (≥600 lines) into topic-cohesive parts |
| **doc-update-tokens** | Add/modify design tokens and manage build workflow |
| **doc-lookup-dependencies** | Look up API docs before emitting a dependency call (REQ-PROC-053 AC-02) |

### claude-* (Factory Infrastructure)
| Skill | When to use |
|-------|-------------|
| **claude-route** | Internal router — type-detection + skill dispatch (called by task-start; use `/claude-route` for advanced manual routing) |
| **claude-optimize** | Consume one `.factory/optimize/events/` event and produce one auto-blocked improvement task (or a documented no-op) |
| **claude-optimize-audit** | Score the optimizer loop's effectiveness with a deterministic 10-point rubric + unblock-rate + revert-rate (separate skill — G-INV-3) |
| **claude-create-skill** | Create a new project skill |
| **claude-create-agent** | Create a governed `.claude/agents/*.md` file — **MUST be used to create agents** |
| **claude-write-script** | Create or modify a script in /scripts AND run Python quality gates — **MANDATORY for EVERY edit to `scripts/**/*.py` or `scripts/**/*.ps1`** (no exceptions for one-line / "trivial" / bugfix edits) |
| **claude-write-hook** | Create or modify a hook script in `.claude/hooks/` — **MUST be used for all hook work** (new hooks, modifications, wiring into settings.json) |
| **claude-modify-skill** | Modify an existing skill, sync INDEX.md and factory_flows.md |
| **claude-modify-agent** | Modify an existing agent, keep it governed — **MUST be used to modify agents** |
| **claude-modify-ordering-rules** | Modify or initialize task ordering rules |
| **claude-ask** | Research question with the session's model |
| **claude-log** | Persist work to long-term memory (called by every agent) |
| **claude-save-checkpoint** | Save context for session restart |
| **claude-install-os-tool** | Before installing any OS-level tool (apt, pip --system, brew, npm -g) |
| **claude-commit** | Write a compliant commit message and commit staged changes — **MUST be used to commit changes** |
| **claude-resume-agent** | Resume a stopped or killed background agent |
| **claude-autorun** | Start, stop, status, or resume the automation orchestrator |
| **claude-automated-mode** | Load automated mode rules for unattended session execution |
| **brb** | Auto-triggered by "brb"/"afk"; starts keepalive only when LLM goes idle |

---

## Capability-Authoring Meta-Skills (governed set — REQ-PROC-044-01 AC-05)

These six meta-skills author the factory's own building blocks; their output quality is factory quality.
They are owned by REQ-PROC-044-01. Each entry **cross-links** the AC that already governs it — no restatement.

| Meta-skill | Authors | Governing AC (cross-link, not duplicated) |
|------------|---------|-------------------------------------------|
| **claude-create-skill** | new skill | REQ-PROC-044-01 AC-04 (split rubric, §"Phase Split Decision") |
| **claude-modify-skill** | existing skill | REQ-PROC-044-01 AC-04 (split rubric) |
| **claude-create-agent** | new agent | REQ-PROC-044-01 AC-01/AC-02/AC-03 (naming, sections, Domain-Vocabulary aid) |
| **claude-modify-agent** | existing agent | REQ-PROC-044-01 AC-01/AC-02 (re-assert governed end-state) |
| **claude-write-script** | `scripts/**` script | REQ-PROC-043 (scripts organization + Python gates) |
| **claude-write-hook** | `.claude/hooks/*.sh` + `settings.json` wiring | hooks are factory infrastructure; test coverage enforced via `scripts/tests/test_hooks.py` |
| **claude-modify-ordering-rules** | `.claude/task_ordering_rules.yaml` | REQ-PROC-042 (intelligent task ordering) |

---

## Release Workflow

Run `/release-status` at any time to see which stage you are at and the recommended next step.

| Phase | Step | Skill | When |
|-------|------|-------|------|
| A — Requirements | 1 | `requ-explore` | Document requirements for the release |
| A — Requirements | 2 | `release-plan` | Assign ACs/sections to packages in RELEASE_BACKLOG.md |
| A — Requirements | 3 | `requ-derive-from-flow` | *(if needed)* Derive requirements from user flows |
| A — Requirements | 4 | `requ-assign-packages` | Bulk-assign `target_package` to unassigned ACs |
| B — Begin Impl | 5 | `release-begin-impl` | Verify requirements, activate release, create orchestration task |
| C — Autorun | 6 | `/autorun` | Autorun iteratively creates and executes impl tasks |
| C2 — Finalize Impl | 6.5 | `release-begin-impl-finalize` | After autorun reports all packages covered; semantic review + user gate before /release |
| D — Release | 7 | `release` | Pre-flight → smoke test → merge/tag/push → release notes |

---

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        REQUIREMENTS                              │
│  ┌────────────────┐                                              │
│  │  requ-explore  │ ──→ Document requirement                     │
│  └────────────────┘                                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        TASK CREATION                             │
│  ┌──────────────────┐                                            │
│  │ task-create-code │ ──→ Create task from requirement           │
│  └──────────────────┘     (WHAT, not HOW)                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       IMPLEMENTATION                             │
│  ┌─────────────┐   ┌──────────────┐                             │
│  │ code-simple │   │ code-complex │                              │
│  └─────────────┘   └──────────────┘                             │
│           │                │                                     │
│           └────────┬───────┘                                     │
│                    ↓                                             │
│           Create plan (HOW)                                      │
│                    ↓                                             │
│           Implement → verify-quality → task-complete             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        TESTING                                   │
│  ┌───────────┐                                                   │
│  │ code-test │ ──→ TDD workflow (parallel or after)              │
│  └───────────┘                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## FAQ

### When `code-simple` vs `code-complex`?

| code-simple | code-complex |
|-------------|--------------|
| 1-3 files | 4+ files |
| One layer (Domain OR Presentation) | Multiple layers |
| Pattern already exists | New pattern needed |
| Low risk | Architecture impact |

**When in doubt**: Start with `code-simple`, the skill will suggest `code-complex` if needed.

### When do I need `task-create-code`?

**Always before implementing**, when:
- The implementation won't happen immediately
- You want to document the scope
- The requirement is complex

**Not needed** for immediate small fixes or trivial changes.

### When to use `ux-write-persona` / `ux-write-scenario` vs. direct edit?

**Use `ux-write-persona`** for: creating or significantly modifying personas (runs cascade scan automatically).
**Use `ux-write-scenario`** for: creating or significantly modifying scenarios (runs cascade scan automatically).
**Use `ux-create-flow`** for: creating new flows or modifying approved flows (resets review status, notifies scenarios).

**Use direct edit for:** typo fixes, small wording changes.

### What does quality checking do?

The `quality-checker` agent checks: code follows doc/ guidelines, no forbidden imports, tests exist, WHY comments for non-obvious code.
