## Summary for User

- All 4 scope items now have at least one feature requirement and at least one impl task assigned to 0.0.1. The release is structurally covered.
- Three open questions from Phase 3 still require user decisions before implementation can proceed without ambiguity: encryption handling in 0.0.1, client name field behavior (no DB context), and AC-08 scope for REQ-NFUNC-012.
- REQ-FUNC-007-02 (Feat Plan Receiving) is the weakest coverage point at 14% with 12 of 14 ACs still as gaps — the existing task TASK-FUNC-007-02-02 only covers AC-03 and AC-08.

### Open Questions for User

1. **[REQ-FUNC-007-01 Q1] Encryption step in SEC-04 vs. 0.0.1 scope**: SEC-04 section 4.3 describes AES-256-GCM encryption as part of the chunking pipeline, but 0.0.1 explicitly excludes all encryption. Should (a) a `> 0.0.1 note:` be added inline to SEC-04 stating encryption is skipped, or (b) SEC-04 be split into 0.0.1 and 0.0.2 subsections to avoid implementer confusion?
=> (b)

2. **[REQ-FUNC-007-01 Q2] AC-01/AC-02 vs. SEC-01 release mismatch**: AC-01 and AC-02 are `target_release: 0.0.1` but SEC-01 (Dialog Structure detail) is `target_release: 0.1.0`. TASK-FUNC-007-01-01 was scoped to implement the minimum dialog shell only. Is this correct, or should SEC-01's `target_release` be updated to `0.0.1`?
=> minimum dialog shell only is correct.

3. **[REQ-FUNC-007-01 Q3] Client name field behavior without DB**: AC-05 and SEC-04 4.1 reference "client name entered AND key found" as the trigger for Data Beam auto-start. Since 0.0.1 excludes client profiles and key storage, should the implementation (a) show the field but skip key lookup (always treat as "key found"), (b) omit the client name field entirely and show Data Beam unconditionally, or (c) another approach?
=> (b)

4. **[REQ-NFUNC-010 Q1] Scope of `showAdaptiveOverlay()` migration**: Should TASK-NFUNC-010-01 require full migration of the existing `_showAdaptiveDetailOverlay` method in `plan_template_detail_content.dart` to the new utility, or is it sufficient to update only the hardcoded breakpoints (600/1200 → 600/1240)?
=> full migration

5. **[REQ-NFUNC-011] No task created**: REQ-NFUNC-011 status is `implemented` with no pending action items. Coverage tracking shows 0% (0/4 sections) because no task references it. Should a formal "verify implementation" task be created, or is the 0% coverage acceptable given the documented `implemented` status?
=> it is implemented

6. **[REQ-NFUNC-012 Q1] AC-08 scope for 0.0.1**: AC-08 ("All components incrementally support both modes") is `target_release: 0.0.1` but its scope is undefined. Which interpretation applies: (a) narrow — only core shell/navigation and 1-2 representative components (LeafPopout, ContextHelp), (b) broad — all components listed in section 12 of REQ-NFUNC-012, or (c) defer AC-08 to 0.1.0 and update `target_release` accordingly?
=> (a)

---

# Final Coverage Check — 0.0.1

## Scope Item Coverage

| Scope Item | Feature Req | Impl Task(s) | Status |
|---|---|---|---|
| QR code generation (therapist side) | REQ-FUNC-007-01 (Feat Therapist Transfer UI) | TASK-FUNC-007-01-01 (therapist transfer UI shell + Data Beam) | Covered — 59% AC coverage; 3 open questions on implementation details |
| QR code scanning and plan reception (client side) | REQ-FUNC-007-02 (Feat Plan Receiving) | TASK-FUNC-007-02-02 (progress indicator + decline) | Partially covered — 14% AC coverage (AC-03, AC-08 only); 12 ACs remain as gaps |
| Basic plan serialization/deserialization | REQ-FUNC-007-03 (Feat Plan Serialization — new req) | TASK-FUNC-007-03-01 (plan serialization pipeline) | Covered — 83% AC coverage (5/6 ACs); AC-06 gap remains |
| Role selection (Client / Therapist) | Already implemented; user confirmed no new requirement needed | — | Accepted as-is — no task required |

## Remaining Gaps

### 1. REQ-FUNC-007-02 coverage is critically low (14%)

TASK-FUNC-007-02-02 covers only AC-03 (progress indicator) and AC-08 (decline/cancel). The following ACs have no task:

- AC-01, AC-02, AC-04, AC-05, AC-06, AC-07, AC-09, AC-10, AC-11, AC-12, AC-13, AC-14

These ACs cover the full client-side scanning UI, reception flow, and confirmation. For the QR scanning scope item to be considered truly covered, additional tasks are needed. However, since this is a PoC release and TASK-FUNC-007-02 (explore task) is still in_progress, the gap may be intentional — the explore task is expected to produce further impl tasks.

**Verdict on this gap**: Acceptable for now only if TASK-FUNC-007-02 (explore) is expected to produce a follow-up impl task covering the remaining ACs before 0.0.1 ships.

### 2. REQ-FUNC-007-03 AC-06 gap

AC-06 of REQ-FUNC-007-03 (Feat Plan Serialization) has no task coverage. Impact is minor (83% coverage overall) but worth noting.

### 3. REQ-NFUNC-011 coverage shows 0% despite implemented status

REQ-NFUNC-011 is documented as fully implemented, but the coverage report shows 0% because no task references it. This is a tracking artifact, not a real gap.

### 4. REQ-NFUNC-012 AC-08 scope undefined

No task can be created for REQ-NFUNC-012 AC-08 without user clarification on scope (see Open Question 6 above). TASK-NFUNC-012-06 covers only AC-05 (Simple Mode animations), leaving 14 of 15 ACs as gaps.

### 5. REQ-NFUNC-014 has 0% task coverage despite implemented status

REQ-NFUNC-014 (Responsive Layout Master Detail) has `status: implemented` and all 3 sections are `target_release: 0.0.1`, but no tasks reference it. Similar to REQ-NFUNC-011 — tracking artifact.

## Open Questions (detail)

### From feat_REQ-FUNC-007-01_questions.md

**Q1 — Encryption in SEC-04**

SEC-04 section 4.3 describes AES-256-GCM encryption as step 3 of the QR chunking pipeline. RELEASES.md 0.0.1 excludes "Encryption of any kind." TASK-FUNC-007-01-01 was written assuming serialize → compress → chunk → QR (no encrypt). Risk: future implementer reads SEC-04 and assumes encryption is required.

Suggested fix: Add inline `> 0.0.1 note:` to SEC-04 section 4.3, or split into 0.0.1 / 0.0.2 subsections.

**Q2 — AC-01/AC-02 vs. SEC-01 target_release mismatch**

AC-01 ("Dialog opens as modal/fullscreen") and AC-02 ("Three tabs navigate between transfer modes") are `target_release: 0.0.1`. SEC-01 (Dialog Structure specification detail) is `target_release: 0.1.0`. TASK-FUNC-007-01-01 implements the minimum shell to host Data Beam without the full SEC-01 spec. The mismatch creates a risk that a future agent will see the ACs as 0.0.1 but have no section spec to implement against.

**Q3 — Client name field without DB**

AC-05 and SEC-04 4.1 reference "client name entered AND key found" as the Data Beam auto-start trigger. 0.0.1 excludes client profiles and key storage. Three options: (a) show field, skip key lookup; (b) omit field, show Data Beam unconditionally; (c) other. Decision affects TASK-FUNC-007-01-01 scope directly.

### From feat_REQ-NFUNC-001-010-011_questions.md

**Q1 — REQ-NFUNC-010: showAdaptiveOverlay() migration scope**

Should TASK-NFUNC-010-01 require full refactoring of the existing `_showAdaptiveDetailOverlay` method in `plan_template_detail_content.dart` to use the new utility, or only update hardcoded breakpoints (600/1200 → 600/1240)? Full migration is larger scope; breakpoint-only is smaller.

**REQ-NFUNC-011 note**: No task created. Requirement is `status: implemented` with all sections documented. Coverage shows 0% as a tracking artifact. User should confirm if a verification task is needed.

### From feat_REQ-NFUNC-012-014-016_questions.md

**Q1 — REQ-NFUNC-012 AC-08 scope**

AC-08 "All components incrementally support both modes" is `target_release: 0.0.1` with no defined component list. Three options: (a) narrow — implement isTreeTheme check in core shell/navigation + LeafPopout + ContextHelp only; (b) broad — all components in section 12 of REQ-NFUNC-012 must have dual-mode support; (c) defer AC-08 to 0.1.0 by updating `target_release`. No task can be created until this is resolved.

**REQ-NFUNC-014 note**: No task created. Requirement is `status: implemented`. Coverage shows 0% as a tracking artifact.

**REQ-NFUNC-016**: No questions. TASK-NFUNC-016-01 (explore, U5-FOUNDATION) and TASK-NFUNC-016-02 (impl, blocked by 016-01) are in place with full AC coverage.

## Verdict

NOT READY — but structurally sound.

**Reason**: All 4 scope items map to at least one feature requirement and at least one impl task. The release plan is structurally complete. However, 3 of the 6 open questions require user decisions that directly affect task scope or requirements text before implementation can proceed safely:

- Open Question 3 (client name field) blocks implementation of TASK-FUNC-007-01-01
- Open Question 6 (AC-08 scope) blocks any task creation for REQ-NFUNC-012 beyond AC-05
- Open Question 1 (encryption in SEC-04) creates implementer confusion risk if not resolved before TASK-FUNC-007-01-01 is executed

Additionally, REQ-FUNC-007-02 (QR scanning / client side) has only 14% AC coverage, and whether this is acceptable depends on whether TASK-FUNC-007-02 (explore, currently in_progress) will produce a follow-up impl task covering the remaining ACs.

**Minimum required before implementation starts**: Answers to Open Questions 1, 3, and 6.
