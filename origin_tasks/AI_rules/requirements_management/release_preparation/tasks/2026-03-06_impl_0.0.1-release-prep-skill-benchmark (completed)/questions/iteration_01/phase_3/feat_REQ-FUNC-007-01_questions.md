# Phase 3 Questions — REQ-FUNC-007-01 (Therapist Transfer UI)

**Date**: 2026-03-06
**Agent**: Phase 3 Feature Agent

---

## Summary of What Was Done

Created TASK-FUNC-007-01-01 covering SEC-04 (Transfer Flow - Local), AC-01, AC-02, and AC-05 for the 0.0.1 release.

AC-12 was confirmed already covered by TASK-FUNC-007-01-00 (the explore task covers AC-08 through AC-13 per its frontmatter).

---

## Questions

### Q1: Encryption Step in SEC-04 vs. 0.0.1 Scope

**Concern**: SEC-04 section 4.3 (QR Animation Logic) describes AES-256-GCM encryption as step 3 of the chunking pipeline:

> "Encrypt compressed data with contact-specific key (AES-256-GCM)"

However, RELEASES.md 0.0.1 explicitly excludes **"Encryption of any kind"**.

The goal.md for TASK-FUNC-007-01-01 was written with the assumption that the encryption step is **omitted** in 0.0.1 (serialize → compress → chunk → QR, no encrypt). Is this the correct interpretation, or should SEC-04 be updated to clarify the unencrypted 0.0.1 variant of the chunking pipeline separately?

**Impact**: If the task is implemented without encryption and the requirements text is not updated, an implementer reading SEC-04 could misread it as requiring encryption in 0.0.1.

**Suggested resolution**: Either (a) add a `> 0.0.1 note:` inline in SEC-04 section 4.3 stating that encryption is skipped in 0.0.1, or (b) split the section into 0.0.1 and 0.0.2 subsections.

---

### Q2: AC-01 and AC-02 Section Mismatch

**Concern**: AC-01 ("Dialog opens as modal/fullscreen") and AC-02 ("Three tabs navigate between transfer modes") are marked `target_release: "0.0.1"` in the ACs list, but SEC-01 (Dialog Structure) has `target_release: "0.1.0"`.

This means: the ACs that define the dialog shell are 0.0.1, but the section that specifies the dialog structure detail is 0.1.0.

TASK-FUNC-007-01-01 was written to implement the minimum dialog shell needed to host the Data Beam flow (responsive breakpoints and tab bar) without the full SEC-01 specification. Is this the right approach, or should SEC-01's `target_release` be changed to `"0.0.1"` to align with AC-01 and AC-02?

---

### Q3: Client Name Input in 0.0.1 (No DB)

**Concern**: AC-05 (animation slider) and SEC-04 4.1 (auto-start) reference "client name entered AND key found" as the trigger to start Data Beam. In 0.0.1 there is no key storage (RELEASES excludes "Client profiles stored on therapist side").

Should the 0.0.1 implementation:
- (a) Show the client name field but skip key lookup (always treat as "key found" for the unencrypted PoC)?
- (b) Omit the client name field entirely for 0.0.1 and just show the Data Beam unconditionally?
- (c) Another approach?

This affects the scope of TASK-FUNC-007-01-01.
