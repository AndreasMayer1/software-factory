# ARB Parser Coordination Decision

**Task**: TASK-PROC-049-03
**Date**: 2026-05-16
**Author**: automated session 960ff671

---

## 1. Findings from TASK-PROC-046 Read

### TASK-PROC-046-01 — explore_llm-code-quality-backpressure (completed)
Seeds the back-pressure requirement. No ARB parsing or parser module mentioned. Pure exploration of LLM code quality gates concept.

### TASK-PROC-046-02 — analyze_calibrate-cold-start-galaxy-a40 (completed)
Performance calibration study for Galaxy A40 cold-start. Unrelated to linguistic complexity or ARB parsing.

### TASK-PROC-046-08 — impl_create-widget-test-backfill-tasks
Acknowledges G6 linguistic-complexity gate (AC-14) exists as a required check referencing `test/unit/l10n/`, but this task is explicitly out-of-scope for the G6 implementation. No ARB parser designed or proposed.

### TASK-PROC-046-14 — impl_custom-replacement-scripts-for-dcm-rules
Implements six DCM-replacement scripts (complexity, type-naming, architectural, styling, test-smells, folder-taxonomy). Linguistic-complexity sub-check NOT included. No ARB parser designed or proposed.

### File system check
No `scripts/quality/_arb_parser.py` or any ARB-parsing module exists anywhere in the codebase.

---

## 2. Answers to the Two Coordination Questions

**Q1: Has the back-pressure work already defined an ARB-parser module shape?**
**No.** None of the four TASK-PROC-046 tasks specified, prototyped, or even referenced an ARB-parser module. The G6 linguistic-complexity sub-check is mentioned as a deferred future task (not yet created) that will consume `.arb` strings, but no parser interface has been designed on that side.

**Q2: Is the G6 linguistic-complexity sub-check implementation already specified (dictating the parser interface)?**
**No.** G6 is referenced in requirements (REQ-PROC-046 AC-07(e), REQ-NFUNC-002 AC-14) with concrete thresholds (Wiener Sachtextformel ≤ 8 for German, Flesch-Kincaid for English), but no implementation task for G6 has been created. The consuming code does not exist.

---

## 3. Decision

**Decision: CREATE** `scripts/quality/_arb_parser.py` under REQ-PROC-049 (this task).

**Rationale**: Neither TASK-PROC-046 stream has designed or implemented an ARB parser. Both the canon-coherence check (`check_canon.py`, T5/TASK-PROC-049-06) and the future G6 linguistic-complexity check will walk `.arb` strings. Creating the shared module here (under the first consumer to be implemented) avoids duplication and establishes the interface before TASK-PROC-049-06 begins. This is consistent with the v2 synthesis guidance: "Either side can create the module first; whichever does it documents the interface so the other consumes it unchanged."

**Long-term ownership**: `scripts/quality/` — shared quality utility. The module is a read-only ARB parser; neither REQ-PROC-049 nor REQ-PROC-046 owns it exclusively.

**Next consumer**: TASK-PROC-049-06 (`check_canon.py` implementation, T5) imports `iter_arb_entries` to walk ARB string values for canon drift detection.

**G6 consumer**: A future task under REQ-PROC-046 (not yet created) will import `iter_arb_entries` for the Wiener Sachtextformel check. That task must NOT redefine the parser; it reads `scripts/quality/_arb_parser.py` as-is.

---

## 4. Module Interface

File: `scripts/quality/_arb_parser.py`

```python
@dataclass
class ArbEntry:
    key: str                                  # translatable key (no @ prefix)
    value: str                                # string value
    description: str                          # from @key.description, or ""
    placeholders: dict[str, dict]             # from @key.placeholders, or {}
    language_code: str                        # e.g. "en", "de" (from filename)
    source_path: pathlib.Path                 # absolute path to the .arb file

def iter_arb_entries(path: pathlib.Path) -> Iterable[ArbEntry]:
    """Yield one ArbEntry per translatable key in the given .arb file."""
```

`source_path` is added beyond the minimal v2 spec so both consumers can emit precise error locations (file + key) in their output without re-deriving the path.

---

## 5. Cross-Reference Note for T7 (TASK-PROC-049-08)

REQ-PROC-046's `requirements.md` should gain a Related-Requirements entry pointing at REQ-PROC-049 (shared ARB parsing infrastructure). This update is out-of-scope for T2; T7 applies it.
