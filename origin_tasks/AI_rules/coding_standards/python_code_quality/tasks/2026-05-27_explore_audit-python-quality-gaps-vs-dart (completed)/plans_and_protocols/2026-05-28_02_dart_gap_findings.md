# Dart Gap Findings — Reverse Comparison from Python Audit

Date: 2026-05-28
Task: TASK-PROC-051-05

## Purpose

After auditing Python code-quality gaps against Dart protections, this document records the reverse: dimensions the Python audit surfaced that Dart's existing guidelines also leave unaddressed. These are findings for a follow-up task; no Dart doc/ files are edited here.

## Findings

### F1. No magic-value gate (Dart equivalent of PLR2004)

**What**: Dart has no analyzer rule or custom gate flagging magic numbers/strings in comparisons. `analysis_options.yaml` does not include a rule equivalent to `PLR2004`. The Flutter analyzer does not ship one.

**Risk**: Magic values like `Duration(milliseconds: 300)` or `if (retryCount > 3)` in `lib/` lack named constants. The intent is hidden and the value is duplicated across call sites without a single source of truth.

**Severity**: Low. The Dart SLOC ≤ 50 limit naturally constrains function size, making magic values more visible. Clean Architecture layer separation means domain logic (where magic values are most dangerous) is isolated and testable. But the gap exists.

**Recommendation**: Add judgment-level guidance to `doc/architecture/` or `doc/cross_cutting_standards/` noting that meaningful numeric/string literals should be named constants. No gate — the false-positive rate on a Dart magic-value rule would be high due to widget constructor arguments (`padding: 16.0`, `maxLines: 3`).

### F2. No branch-count or return-count gate

**What**: Dart AC-02 measures cyclomatic complexity (CC ≤ 20) but not branch count or return-statement count independently. Python's `PLR0912` (branches ≤ 12) and `PLR0911` (returns ≤ 6) have no Dart equivalents.

**Risk**: Low. CC ≤ 20 subsumes most branch-heavy functions. A function with 15 branches almost certainly exceeds CC 20. The independent gates are redundant in the presence of a CC gate.

**Recommendation**: No action needed. Dart's CC gate covers this adequately.

### F3. No explicit guidance on function decomposition strategies

**What**: `doc/architecture/` and `doc/presentation/` describe architectural layers and patterns but do not have a section on WHEN and HOW to decompose a function that exceeds the SLOC/CC limits. The mechanical gate (AC-02) catches violations but doesn't guide the developer toward the right decomposition.

**Risk**: Medium. Without guidance, the decomposition response to a gate failure may be mechanical splitting (extract arbitrary chunks into helpers) rather than responsibility-driven decomposition. The common pitfall in REQ-PROC-046 already warns about this ("Splitting a function only to satisfy SLOC") but doesn't provide positive guidance.

**Recommendation**: Add a short section to `doc/architecture/` or `doc/cross_cutting_standards/` describing decomposition strategies: extract-by-responsibility (one function per concern), extract-by-abstraction-level (high-level orchestration calls lower-level helpers), extract-by-testability (side-effecting parts separate from pure logic). This would complement the mechanical gate with judgment-level guidance.

### F4. No local-variable-count constraint

**What**: Neither Dart nor Python currently gates the number of local variables per function. Python's `PLR0914` (max-locals, default 15) has no Dart equivalent.

**Risk**: Low. The SLOC ≤ 50 limit in Dart naturally constrains locals — a 50-line function rarely has 15 local variables. In Python, the larger allowed function size means more locals accumulate.

**Recommendation**: No Dart action needed. The SLOC gate is sufficient.

## Summary

| Finding | Severity | Action recommended |
|---|---|---|
| F1 Magic values | Low | Judgment-level doc guidance; no gate |
| F2 Branch/return count | Low | No action (CC gate covers) |
| F3 Decomposition strategies | Medium | Add doc guidance section |
| F4 Local-variable count | Low | No action (SLOC gate covers) |

Only F1 and F3 warrant follow-up work. Neither is urgent — the existing Dart gates (AC-02) provide strong mechanical protection, and the gap is in judgment-level guidance, not enforcement.
