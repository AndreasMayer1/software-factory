---
task_id: TASK-PROC-027-08
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
scope_description: "Explore external storage (SD card) support for FLOW-011 (Backup & Migration)"
related_flows:
  - FLOW-011
requirements_version:
  commit: ""
  file: ../requirements.md
---

# Explore: Backup to External Storage (SD Card)

## Objective

Decide whether the app should support saving backups to external storage (SD cards) on Android devices.

## Context

FLOW-011 (Backup & Migration) currently assumes backup files are written to the app's internal storage or a user-chosen location via the system file picker. On Android, many mid- and low-range devices rely on SD cards for additional storage capacity. If the app targets users who manage large amounts of mood data over long periods, backup file sizes could become relevant, and external storage becomes a practical option.

This decision affects:
- The storage-location-selection step in FLOW-011 (does the user get to choose between internal and external?)
- The selection UI (picker vs. pre-selected vs. explicit SD card option)
- Android permissions required (READ/WRITE_EXTERNAL_STORAGE, or scoped storage via SAF on API 29+)
- Whether the flow needs a fallback path when no SD card is present

## Key Questions

1. Do the target users (see personas) realistically use SD cards for storage on Android?
2. Should the flow expose a storage-location-selection step, or silently use whatever the system file picker returns?
3. If SD card support is added, what is the minimum Android API level we need to handle for scoped storage compatibility?
4. Does adding SD card support require a dedicated FLOW-011 variant or just a conditional step?

## Out of Scope

- iOS: iOS does not support user-accessible SD cards; this question is Android-only.
- Cloud backup destinations (separate concern).
- Implementation details of SAF (Storage Access Framework) integration.
