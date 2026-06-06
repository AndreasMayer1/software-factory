# Independent Verification — Migration Fidelity (orchestrator-run)

Run by the orchestrator (not the migration agent) to avoid trusting a single
self-written harness. Method is deliberately different from `verify.py`.

## Golden
`git show 9a73678c:…/ui_sketch_iteration_workflow/requirements.md` (blob cf51a2ba).

## Check A — AC specification (PyYAML multiset)
Parsed `trackable_items.acceptance_criteria` from golden and from all 7 feature
files. Compared the **multiset of `(name, description)` pairs** (renumbering-agnostic).
- golden: 70 ACs, 70 unique pairs.
- features: 70 ACs total (F01=5,F02=4,F03=17,F04=14,F05=14,F06=12,F07=4).
- **Result: multiset byte-identical. PASS.**

## Check B — section prose
Extracted every `##`/`###` block from golden body and from the union of
epic+feature bodies; compared prose (whitespace-normalized to isolate non-spec
boundary newlines).
- missing from new: NONE.
- prose mismatches: NONE.
- only new section: `## Features` (epic child-index scaffolding — expected).
- **Result: every golden section's prose identical. PASS.**

## Also re-ran the agent's own `verify.py` → ALL CHECKS PASS (empty diff).

## Conclusion
Specification preserved with zero drift through the epic+feature split.
Renumbering, new feature frontmatter, the epic `## Features` index, and
boundary whitespace are the only changes — all in the allowed-transform set.
Safe to proceed to the reference-rewrite phase.

Scripts: `/tmp/indep_verify.py`, `/tmp/indep_verify2.py` (throwaway, orchestrator-run).
