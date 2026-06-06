# Efficiency Analysis & Real-World Verification

Date: 2026-05-23

## Part 1: File Read Efficiency — Old vs New

### Scenario: Release flow with feat_qr_data_transfer (19 ACs, ~8 impl tasks)

**Old mechanism** (release-begin-impl → monolithic Phase 2c → task-create-code):

| Step | Who reads requirements.md | Context | Read # |
|---|---|---|---|
| Phase 1 (scope check) | release-begin-impl | Main session | 1 (frontmatter) |
| Phase 2 (epic agent) | epic_data_transfer agent | Agent context | 2 (full) |
| Phase 2c (monolithic planner) | ONE agent reads ALL 5 requirements | Agent context (500-1000 lines from ALL reqs) | 3 (full) |
| Orchestration session 1 (6 tasks) | task-create-code Phase 1 | Session context | 4 (full, read once per session) |
| Orchestration session 2 (2 tasks) | task-create-code Phase 1 | Session context | 5 (full, read once per session) |

**Total reads of feat_qr_data_transfer/requirements.md: 5** (1 frontmatter + 4 full)
**Monolithic agent context load: ~600 lines** (all 5 requirements in one agent)

---

**New mechanism** (release-begin-impl → per-req task-derive-from-requ agents → task-create-code plan-driven):

| Step | Who reads requirements.md | Context | Read # |
|---|---|---|---|
| Phase 1 (scope check) | release-begin-impl | Main session | 1 (frontmatter) |
| Phase 2 (epic agent) | epic_data_transfer agent | Agent context | 2 (full) |
| Phase 2c (per-req agent) | task-derive-from-requ agent for this feature | Agent context (~120 lines, this req only) | 3 (full) |
| Orchestration session 1 (6 tasks) | task-create-code Phase 0A | Plan-driven — **no requirements.md read** | — |
| Orchestration session 2 (2 tasks) | task-create-code Phase 0A | Plan-driven — **no requirements.md read** | — |

**Total reads of feat_qr_data_transfer/requirements.md: 3** (1 frontmatter + 2 full)
**Per-agent context load: ~120 lines** (one requirement per agent)

---

### Comparison

| Metric | Old | New | Change |
|---|---|---|---|
| Reads of requirements.md | 5 | 3 | **-40%** |
| Monolithic agent context | ~600 lines (all reqs) | ~120 lines (one req) | **-80%** |
| Orchestration session reads | 2 (one per session) | 0 (plan-driven) | **-100%** |

### Scenario: Ad-hoc single task creation

| Metric | Old (task-create-code standalone) | New (task-derive-from-requ quick mode) | Change |
|---|---|---|---|
| Reads of requirements.md | 1 | 1 | Same |
| User interactions | 2-3 (ACs? confirm?) | 1 (approve plan) | Fewer |

### Scenario: Ad-hoc 3 tasks, different sessions

| Metric | Old (3 × task-create-code) | New (task-derive-from-requ full mode) | Change |
|---|---|---|---|
| Reads of requirements.md | 3 (one per session) | 1 (one read, 3 tasks inline) | **-67%** |

### Where new mechanism reads MORE

Only one case: when task-derive-from-requ Phase 1 reads related requirements
(after:/blocks: chain). The old mechanism doesn't read related requirements at
all during task creation — it relies on propose_after.py for dependency detection
without reading the full related requirement files.

This is intentional: the extra reads in Phase 1 produce better dependency
ordering and cross-requirement awareness. The cost (~2-3 extra file reads) is
small and pays for itself in quality.

---

## Part 2: Real-World Test — feat_qr_data_transfer

### What exists

**Requirement**: REQ-FUNC-007-12, 19 ACs across 4 groups:
- Client QR Transfer Screen: AC-01 through AC-09
- Therapist QR Receive Screen: AC-10 through AC-14
- Shared Navigation: AC-15 through AC-19
- (AC-06, AC-08, AC-09 cross-assigned to "Adaptive Scanner Settings" package)

**Existing tasks**: 4 tasks, ALL with empty `covers:` fields:
- TASK-FUNC-007-12-01: qr-transfer-foundation (effort M)
- TASK-FUNC-007-12-02: client-qr-transfer-screen (effort M)
- TASK-FUNC-007-12-03: therapist-qr-receive-screen (effort M)
- TASK-FUNC-007-12-04: qr-transfer-navigation (effort S)

### What task-derive-from-requ would find

**Phase 1 (Gather):**
1. Read requirements.md → 19 ACs
2. Read 4 existing task frontmatter → ALL have empty covers: fields
3. Coverage state: **UNKNOWN** — tasks exist but don't declare which ACs they cover
4. Related requirements: REQ-FUNC-007-04 (adaptive settings), REQ-FUNC-007-05
   (client data model), REQ-FUNC-007-10 (file transfer)

**Phase 2 (Analyze):**

This is where it gets interesting. task-derive-from-requ must handle:

**Problem A: Existing tasks with empty coverage.**
The tasks LOOK like they cover certain ACs by name:
- "qr-transfer-foundation" → probably AC-01 (fountain code pipeline), maybe AC-08 (frame rate)
- "client-qr-transfer-screen" → probably AC-01-AC-09
- "therapist-qr-receive-screen" → probably AC-10-AC-14
- "qr-transfer-navigation" → probably AC-15-AC-19

But we can't KNOW without reading the full goal.md bodies. The covers: field
is empty. Should task-derive-from-requ:
  (a) Infer coverage from task names/scope and fill in the covers: fields?
  (b) Treat all 19 ACs as uncovered and plan new tasks?
  (c) Ask the user?

**Answer**: (a) with user confirmation. Phase 2 reads the full goal.md bodies
(not just frontmatter) of existing tasks to infer coverage. Presents inferred
coverage to user: "Based on scope descriptions, I believe these tasks cover
these ACs. Correct?" After confirmation, updates the covers: fields.

This is a REPAIR operation that the old mechanism never did. It's valuable:
the 4 existing tasks probably DO cover most ACs but the metadata is missing.

**Problem B: Cross-package ACs.**
AC-06, AC-08, AC-09 have target_package "Adaptive Scanner Settings" while the
other 16 have "QR Transfer Send". Should tasks cross package boundaries?

The existing tasks all have target_package "QR Transfer Send". This means
AC-06/AC-08/AC-09 are either:
  (a) Covered by the existing tasks but the package assignment is wrong
  (b) Not covered and need tasks in the "Adaptive Scanner Settings" package
  (c) Covered by a task in a different requirement (feat_adaptive_transfer_settings)

task-derive-from-requ should check: do tasks exist under
feat_adaptive_transfer_settings that cover these ACs? If not, either plan tasks
there or flag the gap.

**Problem C: No verification task.**
19 ACs, 4 tasks, 0 verification tasks. task-derive-from-requ would mandate one.

**Phase 3 (Plan) — Expected output:**

Assuming existing tasks cover AC-01-AC-19 after repair:

| Task | ACs | Status | Action |
|---|---|---|---|
| qr-transfer-foundation | AC-01, AC-08 (inferred) | Exists — repair covers: | Update covers: |
| client-qr-transfer-screen | AC-02-AC-07, AC-09 (inferred) | Exists — repair covers: | Update covers: |
| therapist-qr-receive-screen | AC-10-AC-14 (inferred) | Exists — repair covers: | Update covers: |
| qr-transfer-navigation | AC-15-AC-19 (inferred) | Exists — repair covers: | Update covers: |
| **verification-qr-transfer** | ALL ACs | **New** | Create via task-create-code |

Coverage matrix:
```
AC-01 → qr-transfer-foundation
AC-02 → client-qr-transfer-screen
AC-03 → client-qr-transfer-screen
AC-04 → client-qr-transfer-screen
AC-05 → client-qr-transfer-screen
AC-06 → client-qr-transfer-screen (⚠ cross-package: Adaptive Scanner Settings)
AC-07 → client-qr-transfer-screen
AC-08 → qr-transfer-foundation (⚠ cross-package: Adaptive Scanner Settings)
AC-09 → client-qr-transfer-screen (⚠ cross-package: Adaptive Scanner Settings)
AC-10 → therapist-qr-receive-screen
AC-11 → therapist-qr-receive-screen
AC-12 → therapist-qr-receive-screen
AC-13 → therapist-qr-receive-screen
AC-14 → therapist-qr-receive-screen
AC-15 → qr-transfer-navigation
AC-16 → qr-transfer-navigation
AC-17 → qr-transfer-navigation
AC-18 → qr-transfer-navigation
AC-19 → qr-transfer-navigation
VERIFY → verification-qr-transfer (NEW)
```

**Phase 4 (Review):**
Present to user with cross-package warnings and verification task.
User decides: accept inferred coverage? Create verification task?

### What this test case reveals

1. **AC-09 (incremental decomposition) is critical.** Real requirements often
   have existing tasks with incomplete metadata. task-derive-from-requ must
   handle repair, not just greenfield decomposition.

2. **Inferred coverage needs user confirmation.** Automating coverage inference
   from task names is useful but unreliable. The skill should propose, not assert.

3. **Cross-package ACs need explicit handling.** When ACs span packages, the
   coverage matrix should flag this and ask: is the AC covered by a task in this
   package, in the other package, or in both?

4. **The verification task is the most consistent value-add.** Every test case
   (REQ-PROC-046, REQ-PROC-001, feat_qr_data_transfer) had zero verification
   tasks. task-derive-from-requ would add one in every case.

### Issues found from this test case

**Issue 9: Coverage repair for existing tasks.**

The requirement mentions incremental decomposition (AC-09: "reads existing tasks,
computes current coverage, and plans tasks only for uncovered ACs"). But it
doesn't address the case where existing tasks have EMPTY covers: fields.

task-derive-from-requ needs a repair mode: read existing task bodies, infer
coverage, propose covers: updates, get user confirmation, write the updates.
This is NOT new task creation — it's metadata repair. It should be part of
Phase 1 (Gather) or Phase 2 (Analyze).

**Issue 10: Cross-package AC handling.**

When ACs have different target_package values, task-derive-from-requ needs to
decide: should it create tasks in the AC's package or the requirement's package?
The current plan format doesn't address this. A task covering AC-06
(target_package: "Adaptive Scanner Settings") should probably have
target_package: "Adaptive Scanner Settings", not "QR Transfer Send".

This means one task-derive-from-requ run might create tasks in MULTIPLE packages.
The coverage matrix should group by package and show which package each task
belongs to.
