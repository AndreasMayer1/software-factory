---
id: REQ-PROC-065-03
status: placeholder
stakeholder: developer
created: 2026-06-02
market_research_refs: [] # No relevant findings — internal process tooling
---

# Task Creation From Requirement Skill

## Overview

Requirements for the task-creation mechanism aspects of the `task-derive-from-requ` skill: how the skill produces task workspaces from a requirement's acceptance criteria.

## Purpose

The `task-derive-from-requ` skill exists and is documented in `.claude/skills/task-derive-from-requ/SKILL.md`. Its **planning and decomposition strategy** is governed by REQ-PROC-058 (Implementation Task Planning). This placeholder covers the **creation-mechanism** aspects (how goal.md is produced, how coverage is assigned, how IDs are allocated) — the boundary with REQ-PROC-058 will be clarified when the full requirement is written.

## Deferred (YAGNI)

### Full requirement authoring
**Why deferred:** The creation-mechanism is stable. The planning-strategy side already has a requirement (REQ-PROC-058). Writing the creation-side requirement in isolation risks duplicating REQ-PROC-058.
**Reopen when:** A change to the skill's task-creation output format, ID allocation, or goal.md structure is planned — do so jointly with a REQ-PROC-058 boundary review.
**Source:** epic_task_lifecycle creation, 2026-06-02.
