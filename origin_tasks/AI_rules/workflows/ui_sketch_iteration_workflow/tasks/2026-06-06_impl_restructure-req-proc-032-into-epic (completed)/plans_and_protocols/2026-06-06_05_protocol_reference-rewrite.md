# Protocol: Reference Rewrite — REQ-PROC-032 Epic Split

**Agent ID**: af41ef045c2469a2d  
**Date**: 2026-06-06  
**Task**: TASK-PROC-032-34

---

## Files Changed

### Category A — Feature body AC references (7 files)

| File | Changes |
|---|---|
| `feat_scribble_core_artifact/requirements.md` | `[AC-37]` → `[AC-05]` |
| `feat_iteration_and_rule_protocol/requirements.md` | `[AC-05]`→`[AC-01]`, `[AC-06,AC-07]`→`[AC-02,AC-03]`, `[AC-06]`→`[AC-02]`, `[AC-07]`→`[AC-03]`, `[AC-08]`→`[AC-04]` |
| `feat_handoff_skills_and_contract/requirements.md` | `[AC-09,10,11]`→`[AC-01,02,03]`, `[AC-21..27]`→`[AC-05..11]`, `[AC-22]`→`[AC-06]`, `[AC-23]`→`[AC-07]`, `[AC-24]`→`[AC-08]`, `[AC-25]`→`[AC-09]`, `[AC-26]`→`[AC-10]` (×2), `[AC-27]`→`[AC-11]`, `[AC-38]`→`[AC-15]`, `[AC-40]`→`[AC-17]`, `[AC-28..31,39]`→`[AC-12..14, REQ-PROC-032-06 AC-01, AC-16]`, `[AC-28]`→`[AC-12]`, `[AC-29]`→`[AC-13]`, `[AC-30]`→`[AC-14]`, `[AC-31]`→`[REQ-PROC-032-06 AC-01]`, `[AC-39]`→`[AC-16]` |
| `feat_scribble_content_extensions/requirements.md` | `[AC-32..36,41]`→`[AC-09..14]`, `[AC-32]`→`[AC-09]`, `[AC-33]`→`[AC-10]`, `[AC-34]`→`[AC-11]`, `[AC-35]`→`[AC-12]`, `[AC-36]`→`[AC-13]`, `[AC-41]`→`[AC-14]` |
| `feat_consistency_sci_layer/requirements.md` | `[AC-42..55]`→`[AC-01..14]`, `[AC-42]`→`[AC-01]`, `[AC-43]`→`[AC-02]`, `[AC-44]`→`[AC-03]`, `[AC-54]`→`[AC-13]`, `[AC-45]`→`[AC-04]`, `[AC-46]`→`[AC-05]`, `[AC-47]`→`[AC-06]`, `[AC-48]`→`[AC-07]`, `[AC-49]`→`[AC-08]`, `[AC-50]`→`[AC-09]`, `[AC-51]`→`[AC-10]`, `[AC-52,53]`→`[AC-11,12]`, `[AC-55]`→`[AC-14]` |
| `feat_carrier_and_auto_review/requirements.md` | `[AC-56..62]`→`[AC-02..08]`, `[AC-56]`→`[AC-02]`, inline `AC-27`→`REQ-PROC-032-03 AC-11` (cross-feature), `[AC-57]`→`[AC-03]`, `[AC-58]`→`[AC-04]`, `[AC-59]`→`[AC-05]`, inline `AC-59`→`AC-05`, `[AC-60]`→`[AC-06]`, `[AC-61]`→`[AC-07]`, `[AC-62]`→`[AC-08]`, `[AC-31,63,64,65,66]`→`[AC-01,09,10,11,12]`, `[AC-63]`→`[AC-09]`, `[AC-31]`→`[AC-01]`, `[AC-64]`→`[AC-10]`, `[AC-65]`→`[AC-11]`, `[AC-66]`→`[AC-12]` |
| `feat_embedded_flow_viewer/requirements.md` | `[AC-67..70]`→`[AC-01..04]`, `[AC-67]`→`[AC-01]`, `[AC-68]`→`[AC-02]`, `[AC-69]`→`[AC-03]`, `[AC-70]`→`[AC-04]` |

### Category B — Completed-task covers retarget (20 goal.md files)

| Task ID | Old parent | Old ACs | New parent | New ACs |
|---|---|---|---|---|
| TASK-PROC-032-01 | REQ-PROC-032 | AC-01..07 | REQ-PROC-032-01 | AC-01,02,03,04 |
| TASK-PROC-032-03 | REQ-PROC-032 | AC-12..19 | REQ-PROC-032-04 | AC-01,02,03,04,05,06,07 |
| TASK-PROC-032-04 | REQ-PROC-032 | AC-01,02,04,05,07,16 | REQ-PROC-032-01 | AC-01,02,04 |
| TASK-PROC-032-05 | REQ-PROC-032 | AC-01,02,04,05,07,16,19 | REQ-PROC-032-01 | AC-01,02,04 |
| TASK-PROC-032-06 | REQ-PROC-032 | AC-18 | REQ-PROC-032-04 | AC-06 |
| TASK-PROC-032-07 | REQ-PROC-032 | AC-20 | REQ-PROC-032-04 | AC-08 |
| TASK-PROC-032-11 | REQ-PROC-032 | AC-21,22,23,26,27 | REQ-PROC-032-03 | AC-05,06,07,10,11 |
| TASK-PROC-032-12 | REQ-PROC-032 | AC-28,29,30,31 | REQ-PROC-032-03 | AC-12,13,14 |
| TASK-PROC-032-13 | REQ-PROC-032 | AC-32 | REQ-PROC-032-04 | AC-09 |
| TASK-PROC-032-14 | REQ-PROC-032 | AC-33 | REQ-PROC-032-04 | AC-10 |
| TASK-PROC-032-15 | REQ-PROC-032 | AC-34 | REQ-PROC-032-04 | AC-11 |
| TASK-PROC-032-17 | REQ-PROC-032 | AC-35 | REQ-PROC-032-04 | AC-12 |
| TASK-PROC-032-18 | REQ-PROC-032 | AC-24,25 | REQ-PROC-032-03 | AC-08,09 |
| TASK-PROC-032-19 | REQ-PROC-032 | AC-36 | REQ-PROC-032-04 | AC-13 |
| TASK-PROC-032-20 | REQ-PROC-032 | AC-21..41 (21 ACs) | REQ-PROC-032-03 | AC-05..17 (13 ACs) |
| TASK-PROC-032-22 | REQ-PROC-032 | AC-37 | REQ-PROC-032-01 | AC-05 |
| TASK-PROC-032-23 | REQ-PROC-032 | AC-38 | REQ-PROC-032-03 | AC-15 |
| TASK-PROC-032-24 | REQ-PROC-032 | AC-39 | REQ-PROC-032-03 | AC-16 |
| TASK-PROC-032-25 | REQ-PROC-032 | AC-40 | REQ-PROC-032-03 | AC-17 |
| TASK-PROC-032-26 | REQ-PROC-032 | AC-41 | REQ-PROC-032-04 | AC-14 |

Excluded (in-flight, not touched): TASK-PROC-032-30, -31, -32, -33.

### Category C — Two external docs

| File | Change |
|---|---|
| `requirements_tasks/SKETCHES_README.md` | `[AC-33]` → `[REQ-PROC-032-04 AC-10]`; `REQ-PROC-032 SEC-05` → `REQ-PROC-032-01 SEC-05`; also `REQ-PROC-032 wins` → `REQ-PROC-032-01 wins` |
| `doc/presentation/coding/folder_structure.md` | Both occurrences of `REQ-PROC-032 AC-37` → `REQ-PROC-032-01 AC-05` |

---

## Verification Output

### Category A — PASS

All 7 feature bodies checked. Max-AC range check confirmed no old global AC numbers remain unqualified in any body:
- F01 (max local AC-05): CLEAN
- F02 (max local AC-04): CLEAN
- F03 (max local AC-17): CLEAN
- F04 (max local AC-14): CLEAN
- F05 (max local AC-14): CLEAN
- F06 (max local AC-12): CLEAN
- F07 (max local AC-04): CLEAN

### Category B — PASS (20/20)

All 20 retargeted tasks verified: every new AC id in `covers.acceptance_criteria` exists in the named `parent_requirement` feature's `trackable_items.acceptance_criteria`.

```
PASS TASK-PROC-032-01 (REQ-PROC-032-01): [AC-01 AC-02 AC-03 AC-04]
PASS TASK-PROC-032-04 (REQ-PROC-032-01): [AC-01 AC-02 AC-04]
PASS TASK-PROC-032-03 (REQ-PROC-032-04): [AC-01 AC-02 AC-03 AC-04 AC-05 AC-06 AC-07]
PASS TASK-PROC-032-05 (REQ-PROC-032-01): [AC-01 AC-02 AC-04]
PASS TASK-PROC-032-06 (REQ-PROC-032-04): [AC-06]
PASS TASK-PROC-032-07 (REQ-PROC-032-04): [AC-08]
PASS TASK-PROC-032-25 (REQ-PROC-032-03): [AC-17]
PASS TASK-PROC-032-18 (REQ-PROC-032-03): [AC-08 AC-09]
PASS TASK-PROC-032-11 (REQ-PROC-032-03): [AC-05 AC-06 AC-07 AC-10 AC-11]
PASS TASK-PROC-032-26 (REQ-PROC-032-04): [AC-14]
PASS TASK-PROC-032-17 (REQ-PROC-032-04): [AC-12]
PASS TASK-PROC-032-23 (REQ-PROC-032-03): [AC-15]
PASS TASK-PROC-032-13 (REQ-PROC-032-04): [AC-09]
PASS TASK-PROC-032-24 (REQ-PROC-032-03): [AC-16]
PASS TASK-PROC-032-12 (REQ-PROC-032-03): [AC-12 AC-13 AC-14]
PASS TASK-PROC-032-15 (REQ-PROC-032-04): [AC-11]
PASS TASK-PROC-032-22 (REQ-PROC-032-01): [AC-05]
PASS TASK-PROC-032-14 (REQ-PROC-032-04): [AC-10]
PASS TASK-PROC-032-19 (REQ-PROC-032-04): [AC-13]
PASS TASK-PROC-032-20 (REQ-PROC-032-03): [AC-05 AC-06 AC-07 AC-08 AC-09 AC-10 AC-11 AC-12 AC-13 AC-14 AC-15 AC-16 AC-17]
```

### Category C — PASS

- `SKETCHES_README.md` line 118: `[REQ-PROC-032-04 AC-10]` present
- `SKETCHES_README.md` line 213: `REQ-PROC-032-01 SEC-05` present
- `folder_structure.md` line 119: `REQ-PROC-032-01 AC-05` present
- `folder_structure.md` line 148: `REQ-PROC-032-01 AC-05` present

---

## Residue Report — Multi-Feature Tasks: Dropped Minority ACs

| Task | Dropped old AC | Maps to feature | New AC |
|---|---|---|---|
| TASK-PROC-032-01 | AC-05 | REQ-PROC-032-02 | AC-01 |
| TASK-PROC-032-01 | AC-06 | REQ-PROC-032-02 | AC-02 |
| TASK-PROC-032-01 | AC-07 | REQ-PROC-032-02 | AC-03 |
| TASK-PROC-032-04 | AC-05 | REQ-PROC-032-02 | AC-01 |
| TASK-PROC-032-04 | AC-07 | REQ-PROC-032-02 | AC-03 |
| TASK-PROC-032-04 | AC-16 | REQ-PROC-032-04 | AC-04 |
| TASK-PROC-032-05 | AC-05 | REQ-PROC-032-02 | AC-01 |
| TASK-PROC-032-05 | AC-07 | REQ-PROC-032-02 | AC-03 |
| TASK-PROC-032-05 | AC-16 | REQ-PROC-032-04 | AC-04 |
| TASK-PROC-032-05 | AC-19 | REQ-PROC-032-04 | AC-07 |
| TASK-PROC-032-12 | AC-31 | REQ-PROC-032-06 | AC-01 |
| TASK-PROC-032-20 | AC-31 | REQ-PROC-032-06 | AC-01 |
| TASK-PROC-032-20 | AC-32 | REQ-PROC-032-04 | AC-09 |
| TASK-PROC-032-20 | AC-33 | REQ-PROC-032-04 | AC-10 |
| TASK-PROC-032-20 | AC-34 | REQ-PROC-032-04 | AC-11 |
| TASK-PROC-032-20 | AC-35 | REQ-PROC-032-04 | AC-12 |
| TASK-PROC-032-20 | AC-36 | REQ-PROC-032-04 | AC-13 |
| TASK-PROC-032-20 | AC-37 | REQ-PROC-032-01 | AC-05 |
| TASK-PROC-032-20 | AC-41 | REQ-PROC-032-04 | AC-14 |
| TASK-PROC-032-03 | AC-13 | REQ-PROC-032-03 | AC-04 |

---

## Ambiguities / Notes

1. `feat_handoff_skills_and_contract` body ref `[AC-28..AC-31, AC-39]` was a range that spanned two features (AC-28–30 + AC-39 in F03; AC-31 in F06). Rewritten as `[AC-12..AC-14, REQ-PROC-032-06 AC-01, AC-16]` — the range is no longer contiguous, which is correct and accurate.

2. `feat_carrier_and_auto_review` had inline (un-bracketed) `AC-27` in body prose ("the AC-27 trace") — cross-feature reference to F03. Rewritten as `REQ-PROC-032-03 AC-11`.

3. `feat_carrier_and_auto_review` had inline (un-bracketed) `AC-59` in body prose ("the overlay (AC-59) draws on") — same-feature reference. Rewritten as `AC-05`.

4. SKETCHES_README.md contained the `[AC-33]` label (unqualified, file is outside any feature) — qualified as `[REQ-PROC-032-04 AC-10]`. The "REQ-PROC-032 wins" text was also updated to `REQ-PROC-032-01 wins` since the SEC-05 canonical spec now belongs to that feature.
