# Protocol: Add AC-11 Cross-Reference Detection to REQ-PROC-045

## Investigation Summary

- Read REQ-PROC-045 in full (existing 10 ACs, 5 sections, status: active).
- Read REQ-PROC-058 AC-17 (defines `task-derive-from-requ` Phase 1.5 cross-reference completeness gate; explicitly defers detection mechanism to REQ-PROC-045).
- Read `.claude/skills/requ-explore/SKILL.md` Phase 1.4 (mechanism already used informally during requirement authoring).

The mechanism exists in skill instructions but had no requirement-level home. REQ-PROC-058 `blocks: [REQ-PROC-045]` tracked the gap.

## Changes Applied

### YAML
- Added AC-11 to `trackable_items.acceptance_criteria` describing the cross-reference completeness detection mechanism.
- Added SEC-06 "Cross-Reference Completeness Detection" to `trackable_items.sections`.
- Added `updated: 2026-05-24` (no prior `updated:` field).

### Body
- Added a new `## Cross-Reference Completeness Detection` section (between "## LLM Judgment Checklist" and "## Developer Guidelines") describing:
  - The three reference channels (`after:`, `blocks:`, `## Related Requirements`)
  - The detection contract (inputs, output)
  - The two invocation points (requ-explore Phase 1.4 and task-derive-from-requ Phase 1.5)
  - Implementation latitude (script vs. inline skill — deferred to impl tasks)
- Added REQ-PROC-058 entry to `## Related Requirements` explaining the ownership split: REQ-PROC-058 owns the classification gate; REQ-PROC-045 owns the detection mechanism.

### Preserved
- All existing ACs (AC-01 through AC-10) intact.
- All existing sections (SEC-01 through SEC-05) intact.
- All existing prose unchanged.

## Synthesis

The AC follows the end-state pattern: it describes the mechanism's contract (inputs, output, invocation points) rather than dictating how to build it. The script-vs-inline-skill decision is explicitly deferred to impl tasks — REQ-PROC-058 Developer Guidelines already prefer scripts, so that bias propagates without needing duplication in this AC.

The split with REQ-PROC-058 is clean: detection is structural (REQ-PROC-045's domain — it already governs structural quality), classification is task-creation-time policy (REQ-PROC-058's domain — it gates decomposition). Future implementation can satisfy AC-11 with a single shared script used by both callers without crossing the REQ-PROC-045/058 boundary.

## What Remains Uncertain

Term-derivation heuristic ("2–4 domain nouns, action verbs, component names") is intentionally loose. A future impl task may want to make it more prescriptive (e.g. specify minimum precision/recall, list which YAML fields seed the terms). That refinement belongs in the impl tasks, not in the requirement.

The output contract names "REQ-ID, matching file path, matching snippet" as sufficient context but does not pin a structured artifact format. If both callers end up wanting the same machine-readable format, a future iteration may tighten this.

## Approval

Alignment task with well-defined inputs (REQ-PROC-058 AC-17 + `requ-explore` Phase 1.4). No user-facing decisions surfaced beyond the defer-to-impl latitude already in the goal description. Proceeding to task-complete.
