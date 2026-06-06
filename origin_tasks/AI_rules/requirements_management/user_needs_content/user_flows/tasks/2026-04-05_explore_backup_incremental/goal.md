---
task_id: TASK-PROC-027-09
type: explore
parent_requirement: REQ-PROC-027
urgency: 2
urgency_reason: U2-FUTURE
impact: 3
impact_reason: I3-UX
status: pending
effort: S
created: 2026-04-05
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Explore incremental backup support for FLOW-011 (Backup & Migration)"
related_flows:
  - FLOW-011
requirements_version:
  commit: ""
  file: ../requirements.md
---

# Explore: Incremental Backups

## Objective

Decide whether the app should support incremental backups (backing up only data that has changed since the last backup) and, if so, whether this is user-visible or fully transparent.

## Context

FLOW-011 (Backup & Migration) currently models backups as full snapshots of all user data. For users with large data sets or limited storage, full backups on every run may be slow and wasteful. Incremental backups would reduce backup duration and file size.

However, "incremental" can mean two different things from a UX perspective:

1. **Transparent incremental**: The app silently performs incremental operations; the user sees only "Backup complete" with no change to the flow.
2. **Visible incremental**: The app exposes progress detail (e.g., "12 new entries backed up"), file-size feedback, or an explicit user setting to enable/disable incremental mode.

The choice affects FLOW-011's backup progress step and potentially adds a settings touchpoint.

This decision affects:
- Whether FLOW-011 needs a progress or summary step showing what was backed up
- Whether a backup-settings screen needs an incremental toggle
- Restore complexity: incremental backups require a base snapshot + delta chain, which complicates the restore path in FLOW-011

## Key Questions

1. Is backup speed/file size a real pain point for the target users, or is it a premature optimization?
2. If incremental is added, should it be transparent or user-visible?
3. Does incremental backup require a change to the backup file format (versioned chunks vs. single archive)?
4. How does incremental affect the restore flow — does the user need to understand the concept of a base + deltas?

## Out of Scope

- Specific algorithm or data-structure choices for tracking changed records (technical concern).
- Cloud sync (separate requirement; incremental is relevant there too but handled separately).
