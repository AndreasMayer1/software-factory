---
task_id: TASK-PROC-047-01
type: explore
parent_requirement: REQ-PROC-047
urgency: 2
urgency_reason: U2-NEW_CAPABILITY
impact: 4
impact_reason: I4-FACTORY_SCALABILITY
status: blocked
effort: L
created: 2026-04-27
after: []
awaiting: ["factory_stability_confirmation"]
awaiting_note: "Blocked until the Software Factory is confirmed to work reliably overall in practice before investing in expanding to new projects."
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Write the requirement for a 'Setup New Project' skill that dynamically initializes a new factory-enabled project by interviewing the user and mapping information to the correct factory locations."
release_description: ""
opus_recommended: true   # reason: define-phase explore — requires architectural judgment across all skills, file contracts, and the factory-flow top-down model
writes_requirements: true
worktree_path: ""
requirements_version:
  commit: ""
  file: ../requirements.md
---

# Goal: Write Requirement for "Setup New Project" Skill

## Objective

Analyze the full Software Factory skill landscape and write the `requirements.md` for a new
**"Setup New Project" skill** (working name: `setup-new-project` or `project-init`).

The skill's purpose: given a completely empty factory-enabled project (skills folder + process
requirements present, everything else absent), it guides the user through initial project setup
by collecting information via interview or file input, and populates the correct factory locations
(doc/, requirements_user_needs/, CLAUDE.md extensions, etc.).

This task must NOT write the skill itself — only the requirement that will govern its later
implementation.

## Context: What the Skill Must Eventually Do

The following captures the initial design intent (not final ACs — those emerge from this
exploration):

### Core Behavior
- **Dynamic exploration phase**: The skill must NOT hardcode what files to create. Instead, it
  scans the existing skill landscape (`.claude/skills/`, `doc/`, `CLAUDE.md`) at runtime to
  discover which file/folder contracts each skill expects — then derives the setup checklist from
  that scan.
- **User interview**: The skill asks the user for project information, or preferably reads
  user-provided files. Two input tracks:
  1. Technical: framework (Flutter, React, …), architecture style (Clean Architecture, DDD, …),
     design system, VCS (GitHub URL, etc.)
  2. Business/UX: what the app is for, who the users are, high-level goals — fed into the
     user-needs hierarchy (Persona → Scenario → Flow)
- **Factory-flow mapping**: Information is NOT blindly filed. The skill must understand the
  top-down factory flow (`factory_flows.md`) and route each piece of input to the right level:
  - Tech choices → `doc/architecture/`, `doc/presentation/`, etc.
  - User needs → `requirements_user_needs/` (personas, scenarios)
  - Functional ideas → flagged as needing `requ-explore` before becoming requirements
  - Design decisions → `doc/` + potentially VTR records
- **Gap detection**: When the user provides information that cannot yet be grounded in the
  factory-flow hierarchy (e.g., feature ideas without a user need), the skill flags this and
  creates a follow-up task instead of silently filing it.
- **Task generation**: At the end of setup, the skill creates an ordered list of follow-up tasks
  for all gaps and next steps (e.g., "write persona for [user group]", "add architecture doc for
  [tech choice]"), so the user immediately sees what work remains.

### What the Exploration Must Discover
The skill's exploration phase needs to find and understand:
1. Every skill in `.claude/skills/` — what files/folders it reads from and writes to
2. `doc/` subdirectory structure — what guidelines live where and what each expects
3. `factory_flows.md` — the authoritative top-down product-change chain
4. `requirements_user_needs/` structure — persona/scenario/flow file contracts
5. CLAUDE.md — conventions that new projects inherit

### What the Requirement Must Define
The requirement (REQ-PROC-047) should cover:
- Acceptance criteria for the skill's behavior (interview, mapping, gap detection, task creation)
- The exploration protocol (how the skill discovers contracts dynamically, not hardcoded)
- Input formats the skill accepts (voice transcript, markdown file, YAML config, free text)
- Skill invocation pattern (how a user triggers it in a new project)
- Boundaries: what the skill does itself vs. what it delegates to existing skills
  (e.g., does it call `requ-explore` directly, or just create a task for it?)
- Failure modes and how the skill communicates uncertainty to the user

## Scope

### In Scope
- Analyzing ALL existing skills to understand their file/folder contracts
- Analyzing `doc/` structure to understand what a fully set-up project looks like
- Writing `REQ-PROC-047/requirements.md` with full acceptance criteria and trackable items
- Proposing a skill name and invocation pattern

### Out of Scope
- Implementing the skill (separate impl task later)
- Modifying existing skills
- Deciding the final skill name (that is an AC for this requirement to answer)

## Acceptance Criteria

- [ ] All existing skills analyzed for their file/folder read/write contracts
- [ ] `doc/` structure fully mapped (what lives where, what a new project needs)
- [ ] `factory_flows.md` constraints documented (what levels exist, what order)
- [ ] Gap types identified (tech-without-doc, feature-without-userneed, etc.)
- [ ] `REQ-PROC-047/requirements.md` written with:
  - [ ] Full acceptance criteria (with AC IDs and trackable_items)
  - [ ] Skill invocation pattern defined
  - [ ] Input formats specified
  - [ ] Delegation boundaries specified (which sub-skills the setup skill calls vs. tasks it creates)
  - [ ] Skill name proposed and justified

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| Factory stability confirmation | external | Unblocking condition — see awaiting_note |

## Notes

- The skill must be adaptive: when new skills are added to the factory in the future, the setup
  skill should pick them up automatically via its exploration phase — not require manual updates.
- Priority of information: user-provided files > voice/text interview > defaults.
- The factory-flow constraint is non-negotiable: feature requests from the user must be routed
  through user needs first, not directly into requirements.
- This task itself is a good test case: as you explore the skill landscape, you are doing
  exactly what the setup skill's exploration phase would do — document what surprised you.
