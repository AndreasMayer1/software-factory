---
id: REQ-PROC-065-04
status: placeholder
stakeholder: developer
created: 2026-06-02
market_research_refs: [] # No relevant findings — internal process tooling
---

# Task State Machine

## Overview

The valid task states and valid transitions that govern a task's lifecycle from creation to terminal state.

## Purpose

The task state machine is currently documented in REQ-PROC-008 AC-20 (Orchestrator Workflow), where it was added as a workaround because no lifecycle-specific requirement existed. Its canonical home is here. This placeholder marks where the state machine will be formally specified.

Known states (from REQ-PROC-008 AC-20): `pending` → `in_progress` → `completed` (terminal). Also valid: `blocked` (external blocker), `cancelled`/`superseded`/`deprecated` (terminal). The retired status `active` was migrated to `in_progress` + `pending_feedback/question.md`.

## Deferred (YAGNI)

### Full requirement authoring
**Why deferred:** The state machine is currently stable and enforced by `next_tasks.py` and `generate_status_overview.py`. A formal requirement will prevent drift as scripts evolve.
**Reopen when:** A new task state or transition is proposed, or a script is modified that enforces lifecycle rules — write the full requirement first.
**Source:** epic_task_lifecycle creation, 2026-06-02.
