---
task_id: TASK-PROC-036-01
type: impl
parent_requirement: REQ-PROC-036
urgency: 3
urgency_reason: U3-PROC
impact: 4
impact_reason: I4-ENAB
status: completed
completed: 2026-03-11
effort: M
created: 2026-03-10
after: [TASK-PROC-036-02, TASK-PROC-036-03, TASK-PROC-036-04, TASK-PROC-036-05, TASK-PROC-036-06]
awaiting: []
awaiting_note: ""
release_description: "Add /release skill to automate the full release process"
covers:
  acceptance_criteria: []
  sections: [SEC-01, SEC-07]
target_package: "Transfer Data Model"
scope_description: "Create the /release Claude Code skill that orchestrates scripts and AI steps, plus the one-time SETUP_GUIDE.md."
requirements_version:
  commit: 8aeefd9
  file: ../requirements.md
---

# Goal: Release Skill and Setup Guide

## Objective

Create the `/release` Claude Code skill that orchestrates the full release: calls the pre-flight and release scripts, generates release notes (delegating to technical and marketing tasks), presents the marketing draft for user review, and updates RELEASES.md to `released`. Also produce `releases/SETUP_GUIDE.md`.

## Requirements Summary

Covers SEC-01 (Release Skill) and SEC-07 (Manual Setup Guide) of REQ-PROC-036.

The skill's sequence:
1. Run `scripts/check_release_preconditions.ps1` → abort on failure
2. Run `scripts/execute_release.ps1` → merge, tag, push
3. Generate technical release notes (from task metadata)
4. Generate marketing release notes draft (AI-written)
5. Present marketing draft for user review and approval
6. Set active release to `status: released` in RELEASES.md

Current requirements: ../requirements.md

## Scope

### In Scope
- `.claude/skills/release/skill.md`
- `releases/SETUP_GUIDE.md` (GitHub remote setup, Actions secrets, Android signing, pipeline overview, verification steps)
- `releases/README.md` (folder structure and file naming conventions)

### Out of Scope
- The scripts themselves (TASK-PROC-036-02)
- Technical notes generation logic (TASK-PROC-036-03)
- Marketing notes generation logic (TASK-PROC-036-04)
- Task metadata field (TASK-PROC-036-05)
- requ-prep-release changes (TASK-PROC-036-06)
- GitHub Actions workflow file creation (covered in SETUP_GUIDE; developer sets up manually)

## Acceptance Criteria

- [ ] `.claude/skills/release/skill.md` exists and is invocable via `/release`
- [ ] Skill calls `check_release_preconditions.ps1` first; aborts with clear message on failure
- [ ] Skill calls `execute_release.ps1` after successful pre-flight
- [ ] Skill generates both release notes files and presents marketing draft for review
- [ ] Skill waits for explicit user approval of marketing notes before proceeding
- [ ] Skill sets active release to `status: released` in RELEASES.md after approval
- [ ] `releases/SETUP_GUIDE.md` exists with all required sections
- [ ] `releases/README.md` documents folder structure and file naming

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-036-02 | pending | Scripts must exist before skill can call them |
| TASK-PROC-036-03 | pending | Technical notes logic |
| TASK-PROC-036-04 | pending | Marketing notes logic |
| TASK-PROC-036-05 | pending | release_description field must exist in tasks |
| TASK-PROC-036-06 | pending | requ-prep-release must set status: active |
