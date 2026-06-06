# Protocol: Migration Progress
**Date**: 2026-03-05
**Task**: TASK-PROC-034-07

---

## Status: IN PROGRESS

### Completed

**Release 0.0.1 — Alpha: Data Transfer** ✅
Files written (target_release added to frontmatter + all trackable items):
- `non-functional/architecture/local_database_technology/requirements.md` (REQ-NFUNC-016) — all ACs → 0.0.1
- `non-functional/architecture/requirements.md` (REQ-NFUNC-001) — all ACs → 0.0.1
- `non-functional/ui_ux_design_system/navigation_patterns/main_navigation/requirements.md` (REQ-NFUNC-011) — all sections → 0.0.1
- `non-functional/ui_ux_design_system/navigation_patterns/responsive_layout_master_detail/requirements.md` (REQ-NFUNC-014) — all sections → 0.0.1
- `non-functional/ui_ux_design_system/navigation_patterns/in_detail_navigation/requirements.md` (REQ-NFUNC-010) — all sections → 0.0.1
- `non-functional/ui_ux_design_system/theming/growth_tree_theme/requirements.md` (REQ-NFUNC-012) — SPLIT: AC-05,08-15→0.0.1 | AC-01,02,03→0.1.0 | AC-04,06,07→0.4.0
- `functional/shared/epic_data_transfer/requirements.md` (REQ-FUNC-007) — SPLIT: AC-07→0.0.1 | AC-01,02,05,06,08→0.0.2 | AC-03,04→0.1.0
- `functional/shared/epic_data_transfer/feat_therapist_transfer_ui/requirements.md` (REQ-FUNC-007-01) — SPLIT: SEC-04,AC-01,02,05,12→0.0.1 | AC-03,04,07→0.0.2 | SEC-01-03,05-09,AC-06,08,10,11,13→0.1.0 | AC-09→0.2.0
- `functional/shared/epic_data_transfer/feat_plan_receiving/requirements.md` (REQ-FUNC-007-02) — SPLIT: AC-03,08→0.0.1 | AC-01,02,06,07,12,13,14→0.0.2 | AC-04,05,09,10,11→0.1.0

### User-Confirmed Decisions (cross-session)

- REQ-FUNC-002 and REQ-NFUNC-012 are **draft** (NOT implemented)
- AC-09 of REQ-FUNC-007-01 (Handout preview) → **0.2.0** (Beta 2, not Beta MVP)
- REQ-NFUNC-012 SPLIT: token system + simple theme → 0.0.1; colors + fruit → 0.1.0; full tree/Rive → 0.4.0
- REQ-FUNC-007-01: SPLIT confirmed (SEC-04 + dialog/beam ACs → 0.0.1; pairing ACs → 0.0.2; polish → 0.1.0)
- REQ-FUNC-007-02: SPLIT confirmed (progress/decline → 0.0.1; pairing → 0.0.2; polish → 0.1.0)
- REQ-FUNC-007 (epic): SPLIT confirmed (AC-07 → 0.0.1; pairing/encryption ACs → 0.0.2; remote/self-test → 0.1.0)
- PROC-* requirements: user confirmed skipping (internal tooling, not shipped)

### Completed (continued)

**Release 0.1.0 — Beta MVP** ✅
Files written:
- `functional/therapist/epic_onboarding/requirements.md` (REQ-FUNC-009) — all ACs → 0.1.0
- `functional/shared/epic_onboarding/requirements.md` (REQ-FUNC-011) — all ACs → 0.1.0
- `non-functional/ui_ux_design_system/components/toast/requirements.md` (REQ-NFUNC-008) — all ACs → 0.1.0
- `non-functional/ui_ux_design_system/loading_error_handling/requirements.md` (REQ-NFUNC-009) — SPLIT: AC-01,02,04-10→0.1.0 | AC-03,11→0.4.0
- `functional/client/epic_plan_management/requirements.md` (REQ-FUNC-013) — SPLIT: SEC-01,02+AC-01-13,18-19→0.1.0 | AC-14-17→1.1.0
- `functional/shared/epic_backup/requirements.md` (REQ-FUNC-015) — SPLIT: AC-01,03-11,13,15→0.1.0 | AC-02,12,14→0.3.0
- `functional/shared/epic_security/feat_session_management/requirements.md` (REQ-FUNC-006-03) — all ACs → 0.2.0

**RELEASES.md** updated: added 1.1.0 "Self-User Mode" release entry.

### User-Confirmed Decisions (0.1.0 session)

- REQ-FUNC-006-03 (Session Management): all → 0.2.0 (not essential to therapist MVP flow)
- REQ-FUNC-015 (Backup): AC-02,12,14 (encryption-related) → 0.3.0; rest → 0.1.0
- REQ-FUNC-013 (Client My Plans): AC-14-17 (plan creation/duplication) → 1.1.0 (not 0.2.0)
- 1.1.0 "Self-User Mode" added to RELEASES.md: first release for self-user personas, enables client plan creation parallel to therapist plans
- feat_education, feat_donations: skipped — no REQ ID assigned, explicitly post-MVP

### Completed (continued)

**Release 0.2.0 — Beta 2: Therapy Flow Depth** ✅
Files written:
- `functional/therapist/epic_plan_management/requirements.md` (REQ-FUNC-014) — SPLIT: SEC-07→0.0.1 | SEC-01,02,03,04,05,05.5,06,08→0.2.0
- `functional/therapist/epic_plan_management/plan_preview/requirements.md` (REQ-FUNC-010) — all AC-01-11→0.2.0
- `functional/therapist/epic_client_management/requirements.md` (REQ-FUNC-016) — all AC-01-06→0.2.0

(Previously completed within 0.2.0 batch:)
- `functional/shared/feat_notification_time_mapping/requirements.md` (REQ-FUNC-017) — 0.2.0
- `functional/shared/feat_per_question_help_text/requirements.md` (REQ-FUNC-018) — 0.2.0
- `functional/therapist/epic_client_management/client_plan_view/requirements.md` (REQ-FUNC-008) — 0.2.0
- `functional/shared/epic_security/feat_session_management/requirements.md` (REQ-FUNC-006-03) — 0.2.0

### User-Confirmed Decisions (0.2.0 session)

- REQ-FUNC-014 SEC-07 (Export) → 0.0.1 (it's the trigger button for data transfer PoC, already exists in 0.0.1)
- REQ-FUNC-014 SEC-06 (Plan Preview) → 0.2.0 (plan creation without preview is not usable enough)
- REQ-FUNC-010, REQ-FUNC-016 → no split, all 0.2.0

### Remaining Releases

**Release 0.0.2 — Alpha: Encryption** (NEXT)
Requirements to write:
- REQ-FUNC-006 (epic, 17 ACs) — SPLIT across 0.0.2/0.1.0/0.2.0/0.3.0
- REQ-FUNC-006-04 (Secure Key Storage, 8 ACs) — all 0.0.2
- REQ-FUNC-006-01 (Database Encryption, 8 ACs) — all 0.0.2
- REQ-FUNC-006-02 (Biometric Auth, 7 ACs) — all 0.0.2
- REQ-FUNC-006-05 (Transfer Encryption, 8 ACs) — all 0.0.2

Proposed REQ-FUNC-006 split:
- 0.0.2: AC-01,02,03,04,07,08,09,10,11,12,15,16
- 0.1.0: AC-06 (privacy overlay when backgrounded)
- 0.2.0: AC-05,17 (session grace period, notification privacy)
- 0.3.0: AC-13,14 (backup encryption)

**Release 0.0.3 — Alpha: Data Entry**
Requirements to write:
- REQ-FUNC-002 (Data Input, draft, 12 ACs) — all 0.0.3
- REQ-NFUNC-003 (Collapsible Form Section, 7 ACs) — all 0.0.3 (needed for data entry UI)
- REQ-NFUNC-006 (Skeleton Component, 6 ACs) — all 0.0.3

**Release 0.0.4 — Alpha: Visualization**
- REQ-FUNC-005 (Plan Evaluation View, in_progress, 12 ACs) — all 0.0.4
- REQ-FUNC-012 (Epic Evaluation, SEC+ACs) — all 0.0.4
- REQ-NFUNC-005 (Leaf Popout, 12 ACs) — 0.0.4 (needed by eval view)
- REQ-NFUNC-004 (Context Help, 6 ACs) — 0.0.4 (needed by eval view)
- REQ-NFUNC-007 (Time Range Selector, 9 ACs) — 0.0.4

**Release 0.1.0 — Beta MVP**
- REQ-FUNC-011 (Shared Onboarding, 9 ACs) — all 0.1.0
- REQ-FUNC-009 (Therapist Post-Onboarding Nav, 4 ACs) — all 0.1.0
- REQ-FUNC-013 (Client My Plans, 2 sections + 19 ACs) — all 0.1.0
- REQ-FUNC-015 (Backup, 15 ACs) — most 0.1.0 (backup encryption ACs → 0.3.0)
- REQ-NFUNC-008 (Toast Component, 7 ACs) — 0.1.0
- REQ-NFUNC-009 (Loading/Error Handling, 11 ACs) — 0.1.0
- REQ-FUNC-006-03 (Session Management, 6 ACs) — 0.1.0 or 0.2.0 (TBD)

**Release 0.2.0 — Beta 2: Therapy Flow Depth**
- REQ-FUNC-014 (Therapist Plan Management, in_progress) — 0.2.0
- REQ-FUNC-016 (Therapist Client Management, 6 ACs) — 0.2.0
- REQ-FUNC-010 (Plan Preview, 11 ACs) — 0.2.0
- REQ-FUNC-018 (Per-Question Help Text, 13 ACs) — 0.2.0
- REQ-FUNC-017 (Notifications, multiple ACs) — 0.2.0
- REQ-FUNC-008 (Client Plan View - Therapist, 5 ACs) — 0.2.0
- REQ-NFUNC-004 (Context Help) — may overlap with 0.0.4 proposal

**Release 0.3.0 — Beta 3: Client Wellbeing** ✅
Files written:
- `functional/client/epic_safety_skills/requirements.md` (REQ-FUNC-001) — all AC-01-04→0.3.0
- `functional/client/epic_self_evaluation/requirements.md` (REQ-FUNC-004) — all AC-01-04→0.3.0
- `functional/client/epic_onboarding/feat_quick_start_mode/requirements.md` (REQ-FUNC-019) — all AC-01-10→0.3.0
- `functional/shared/epic_security/feat_backup_encryption/requirements.md` (REQ-FUNC-006-06) — all AC-01-08→0.3.0

**Release 0.0.5 — Alpha: UI/UX Foundation** ✅ (NEW RELEASE — added to RELEASES.md)
Files written:
- `non-functional/ui_ux_design_system/accessibility/requirements.md` (REQ-NFUNC-002) — SPLIT: AC-01-06→0.0.5 | AC-07-10→1.0.0
- `non-functional/ui_ux_design_system/ux_writing/requirements.md` (REQ-NFUNC-013) — all AC-01-08→0.0.5

**Release 0.4.0 — Beta 4: Production Readiness** ✅
Files written:
- `functional/shared/epic_security/feat_compliance/requirements.md` (REQ-FUNC-006-07) — SPLIT: AC-06,08→0.3.0 | AC-01-05,07→0.4.0
- `non-functional/branding/app_naming/requirements.md` (REQ-NFUNC-015) — all SEC-01-04 + AC-01-05→0.4.0

### User-Confirmed Decisions (0.4.0 session)

- REQ-NFUNC-002 should be BEFORE 0.1.0 → new release 0.0.5 "Alpha – UI/UX Foundation" introduced
- REQ-NFUNC-013 also moved to 0.0.5 (UX writing rules must exist before Beta copy is written)
- REQ-NFUNC-002 AC-07-10 (screen reader, semantic labels, focus order, high-contrast mode) → 1.0.0
- REQ-FUNC-006-07: AC-06 (notification privacy) + AC-08 (onboarding local-data message) → 0.3.0 (privacy concerns for vulnerable users)
- REQ-FUNC-003 (client/epic_onboarding): DEPRECATED, superseded by REQ-FUNC-011 + REQ-FUNC-013
- feat_donations, feat_education: no REQ ID, post-MVP → SKIP
- PROC-* requirements: user confirmed skip (internal tooling)
- REQ-FUNC-042: unknown ID in merged file only → no individual file to process

## ALL REQUIREMENT FILES PROCESSED ✅

**Skipped (intentional):**
- `functional/client/epic_onboarding/requirements.md` — REQ-FUNC-003 (deprecated)
- `functional/shared/feat_donations/requirements.md` — no REQ ID, post-MVP
- `functional/shared/feat_education/requirements.md` — no REQ ID, post-MVP

### Task Propagation ✅
DONE (2026-03-05). All 13 non-completed task goal.md files updated:
- epic_backup/explore_define_requirements → 0.1.0 (earliest covered AC)
- feat_therapist_transfer_ui/explore_update_instruction_view → 0.0.1 (AC-12 earliest)
- epic_data_transfer/explore_add_requirements_tranfer_filled_plan → 0.0.1 (top-level)
- epic_data_transfer/explore_create_impl_tasks_feat_transfer → 0.0.1 (top-level)
- feat_notification_time_mapping/explore_notification_time_mapping → 0.2.0 (top-level)
- feat_per_question_help_text/explore_per_question_help_text → 0.2.0 (top-level)
- plan_evaluation_view/phase1, phase2, phase3, impl → 0.0.4 (earliest covered AC)
- local_database_technology/explore_database_technology_selection → 0.0.1 (covered ACs)
- app_naming/explore_app_naming → 0.4.0 (all covered items)
- therapist/epic_plan_management/explore_add_requirement_plan_detailview → 0.2.0 (SEC-03/04/05)
Skipped: all (completed) and (superseded) task folders.

### Dependency Conflicts Detected
- REQ-FUNC-007 (top-level 0.0.1) depends on REQ-FUNC-006 (0.0.2): INTENTIONAL — 0.0.1 is unencrypted PoC
- REQ-FUNC-007-01 (top-level 0.0.1) depends on REQ-FUNC-006 (0.0.2): INTENTIONAL — same reason
- REQ-FUNC-007-02 (top-level 0.0.1) depends on REQ-FUNC-006 (0.0.2): INTENTIONAL — same reason
