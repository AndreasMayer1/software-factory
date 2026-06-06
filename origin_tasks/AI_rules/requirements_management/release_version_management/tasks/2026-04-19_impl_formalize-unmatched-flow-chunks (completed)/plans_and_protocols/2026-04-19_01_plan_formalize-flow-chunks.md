# Plan: Formalize Unmatched Flow Chunk Labels

**Task**: TASK-PROC-034-13  
**Date**: 2026-04-19

## Deliverable

10 new entries added to `requirements_tasks/RELEASE_BACKLOG.md` — all `status: planned`, `assigned_release: null`.

## Approved Package Names

| # | Chunk Label | Flow | Package Name |
|---|---|---|---|
| 1 | Scope Controls & Interrupted Transfer | FLOW-004 | Transfer Content Selection |
| 2 | Audio Export | FLOW-004 | File Transfer Audio |
| 3 | Silent Failure Mitigations & Device Resilience | FLOW-004 | Transfer Failure Recovery |
| 4 | Returning Client & Re-transfer | FLOW-002 | Returning Client Delivery |
| 5 | Session Variants | FLOW-002 | Instruction Session Variants |
| 6 | Phase 2 Edge Cases | FLOW-002 | Client Adoption Edge Cases |
| 7 | File Transfer | FLOW-003 | QR File Transfer Fallback |
| 8 | Setup & Pairing | FLOW-003 | Transfer Onboarding Exceptions |
| 9 | Remote Sessions | FLOW-003 | Remote QR Sessions |
| 10 | Edge Cases & Resilience | FLOW-003 | QR Transfer Resilience |

## Naming Issues Resolved

- #2: "Audio File Transfer" → "File Transfer Audio" (user preference: extends file transfer concept)
- #1: "Transfer Scope Controls" → "Transfer Content Selection" (user preference: clearer U1)
- #6: "First Entry Edge Cases" → "Client Adoption Edge Cases" ("Entry" overloaded in codebase = data diary entries)
- #8: "Transfer Setup & Pairing" → "Transfer Onboarding Exceptions" (collision with existing "Transfer Pairing" — 2 shared content words)
- #3: "Transfer Resilience Mitigations" → "Transfer Failure Recovery" (U1 fail — "mitigations" is jargon)
- #10: "Transfer Edge Cases" → "QR Transfer Resilience" (U1/U5 fail — too vague)

## Skill Fix Applied

`release-plan` Action 4b step 5 updated to require reading `requirements_tasks/package_assignment_rules.md` and running U1–U5 tests before proposing names.
