# Cross-Reference Gap Analysis — REQ-PROC-059

Generated: 2026-05-28
Target: requirements_tasks/process/AI_rules/llm_work_principles/requirements.md

## Existing Related Requirements (already present, filtered out)

- REQ-PROC-006: Workflow Improvement Automation
- REQ-PROC-044: Software Factory Quality Properties
- REQ-PROC-031: Smart and Cost-Efficient Model Switching
- REQ-PROC-008: Orchestrator Workflow

## Candidate Gaps Requiring Developer Classification

### REQ-PROC-001 — Context Window

- **Path**: `requirements_tasks/process/AI_rules/coding_standards/context_window/requirements.md`
- **Matched terms**: `context`
- **Hit excerpt**: "As a developer I want the context window of the AI stay as small as possible such that it is able to solve the task..."
- **Assessment**: Directly related to principles (b) Token Economy and (e) Just-in-time context loading. REQ-PROC-001 governs keeping the AI context window small — the same goal these two principles serve. This is a genuine semantic relationship.
- **Classification needed**: `hard` | `semantic` | `ignore — <reason>`

### REQ-PROC-038 — CodeGraph Integration

- **Path**: `requirements_tasks/process/AI_rules/ai_tool_management/codegraph_integration/requirements.md`
- **Matched terms**: `context`, `hooks`, `token`
- **Hit excerpt**: "This requirement governs how and when AI agents in this project use CodeGraph to reduce token consumption and improve context..."
- **Assessment**: CodeGraph is a specific tool that implements principles (a) Scripts over instructions and (e) Just-in-time context loading — agents use CodeGraph instead of broad grep, loading semantic context on demand. This is a genuine semantic relationship.
- **Classification needed**: `hard` | `semantic` | `ignore — <reason>`

## Pre-Classified as Ignore (false positives)

All other candidates from the script output were pre-classified as `ignore` with reasoning below:

| REQ-ID | Matched terms | Reason for ignore |
|--------|--------------|-------------------|
| REQ-FUNC-* (all) | context | Functional app requirements; "context" means UI/app context, not LLM context |
| REQ-PROC-002 | context, principles | "principles" refers to F.I.R.S.T. test principles, not LLM work principles |
| REQ-PROC-004 | context | "context" means project context for brainstorming, not LLM context window |
| REQ-PROC-005 | context | "context window" mentioned but requirement is about testing workflow, not principles |
| REQ-PROC-011 | context, principles | "principles" refers to tool-agnostic workflow principles, different topic |
| REQ-PROC-026 | context, principles, token | "token" means design token; "principles" means design principles |
| REQ-PROC-030 | context | "context" means execution context for goal.md files |
| REQ-PROC-030-01 | context | "context" means requirements context for skills |
| REQ-PROC-032 | context, token | "token" means design tokens (UI theme system) |
| REQ-PROC-034 | context | "context" means UI context term |
| REQ-PROC-035 | context | "context" means orchestration context |
| REQ-PROC-036 | token | "token" means personal access token (GitHub auth) |
| REQ-PROC-037 | context | "context" means content context for writing |
| REQ-PROC-039 | context | "context" means UX bridging context |
| REQ-PROC-041 | principles | "principles" refers to cost-efficiency principles (REQ-PROC-031 already listed) |
| REQ-PROC-041-01 | context, hooks, token | "token" means API tokens; "hooks" means session hooks; unrelated |
| REQ-PROC-041-02 | context | "context" means session context groups |
| REQ-PROC-041-04 | context | "context" means feedback context for dev |
| REQ-PROC-043 | context, token | "token" means design tokens |
| REQ-PROC-045 | context, principles | "principles" refers to naming principles |
| REQ-PROC-046 | context | "context" means hardware context (2017 Android) |
| REQ-PROC-048 | context, token | "token" means design tokens; "context" means reading context |
| REQ-PROC-049 | context | "context" means translation context |
| REQ-PROC-051 | context | "context" means exception/code context |
| REQ-PROC-052 | context, token | "token" means auth credentials |
| REQ-PROC-053 | context | "context" means lookup context |
| REQ-PROC-054 | hooks | "hooks" refers to git hooks in dev environment, not enforcement hooks in principle (c) |
| REQ-PROC-055 | context | "context" means plugin adoption context |
| REQ-PROC-056 | context | "context" means supply chain context |
| REQ-PROC-058 | context, token | "token" means design tokens |
