# Guideline Updates — PII toString() Redaction

**Task**: TASK-PROC-052-03
**Date**: 2026-05-18

## Updates Applied

| File | Change |
|------|--------|
| `doc/architecture/logging.md` | Appended section "Structural PII Redaction in Domain Types (REQ-PROC-052 AC-05)" — convention + sentinel-test contract + procedure for adding a new PII-bearing type. |
| `doc/cross_cutting_standards/logging.md` | Appended a compact cross-cutting rule pointing to the architecture file (single source of truth lives there). |
| `doc/architecture/README.md` | Expanded the `logging.md` topic + read-when columns to mention PII redaction. |

## Why

A new cross-cutting rule was established: every domain type carrying
user-entered free-text must override `toString()` with a redacted form, paired
with a `*_tostring_redaction_test.dart` test asserting the sentinel-content
rule. Future contributors must see this rule when they (a) add logging, or
(b) add a domain type with text fields.

## What Was Considered and NOT Done

- **`doc/testing/`**: the sentinel-test pattern is testing-relevant but the
  contract is already fully described inside the architecture doc under the
  redaction section. Duplicating it in `doc/testing/` would risk drift. The
  architecture doc is the single source of truth.
- **New file under `doc/cross_cutting_standards/`**: rejected in favour of an
  inline section in the existing `logging.md` because the rule is logging's
  structural defence, not a separate concern.
