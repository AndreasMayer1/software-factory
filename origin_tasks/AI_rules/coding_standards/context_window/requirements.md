---
id: REQ-PROC-001
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: in_progress
effort: M
stakeholder: developer
created: 2025-08-31
after: []
blocks: []
market_research_refs: [] # No relevant findings identified
trackable_items:
  sections:
    - id: SEC-01
      name: "User Story"
      heading: "# User Story"
  acceptance_criteria:
    - id: AC-01
      name: "Tasks declare a sizing signal at creation"
    - id: AC-02
      name: "Synthesis-dependent tasks are flagged"
    - id: AC-03
      name: "High-volume tasks have model escalation, a split, or a fan-out plan"
    - id: AC-04
      name: "Open-scope tasks document an agent fan-out plan"
    - id: AC-05
      name: "Heavy multi-read skills defer to agents over the per-task budget"
    - id: AC-06
      name: "requ-explore refuses re-entry in the same session"
    - id: AC-07
      name: "Iterative-fix tasks use model escalation unless ≤ 3 named files"
    - id: AC-08
      name: "CLAUDE.md §7 documents the four signals and their composition"
---

# User Story

As a developer I want the context window of the AI stay as small as possible such that it is able to solve the task because it has exactly the information it needs, not more and not less. If the context window is too full the AI forgets information, if it is too emtpy, it might not have all required information. 

## Acceptance Criteria

These ACs operationalise the User Story by defining what "the AI's context
window stays sized to fit the task" looks like in practice. The four
signals referenced (S1–S4) are defined in CLAUDE.md §7 and recapitulated
below.

**Splitting-first principle**: Task splitting and agent fan-out are always the preferred response to high volume or broad scope. Model escalation is reserved for tasks where reasoning complexity or irreducible synthesis context cannot be reduced by splitting. The specific criteria for when escalation is warranted are defined in the `task-create` skill (not here) so they can be updated as model capabilities evolve without touching this requirement.

- **AC-01** — Every new task's `goal.md` declares at least one of:
  `expected_tool_calls` (estimated count of Bash + Read + Edit calls
  the task will make at runtime) or `skill_chain_depth` (count of
  heavy-skill invocations). The value is visible to creation-time
  tooling so a gate can act on it.
- **AC-02** — Every task whose deliverable requires the executing
  session to hold multiple input domains simultaneously has
  `synthesis_dependent: true` in `goal.md` with a one-line
  justification. (Default is `false`; the field is omitted in that
  case.)
- **AC-03** — No task with `expected_tool_calls > 60` or
  `skill_chain_depth ≥ 4` has both `opus_recommended: false` *and* no
  documented agent fan-out plan. At least one of three end states
  holds: model escalation is flagged (`opus_recommended: true`); the task has been split into child
  tasks; or `goal.md` contains a named fan-out plan describing which
  agents are spawned, what they distill, and what they return.
- **AC-04** — No task with **open scope** (the file set is
  pattern-defined — e.g. "all types named `*Key`", "every feature
  under `feat_*`" — rather than named in `goal.md`) lacks a documented
  agent fan-out plan in `goal.md`.
- **AC-05** — Heavy skills that perform multi-file read passes
  (currently `requ-explore`, `task-resolve`, `task-create`,
  `release-begin-impl`) defer to agents for read-set scans when the
  per-task read budget is exceeded. This budget is distinct from the
  release-level threshold in `scripts/util/should_use_agents.py`,
  which governs release-scope scans only.
- **AC-06** — `requ-explore` refuses a second invocation in the same
  session and instructs the caller to spawn a fresh agent per
  invocation. A task that legitimately requires multiple
  `requ-explore` runs achieves this via fan-out, not in-session
  re-entry.
- **AC-07** — Tasks that drive a `verify-quality` iteration loop on
  changes under `lib/` have `opus_recommended: true` in `goal.md`
  unless the changed file set is named in `goal.md` and contains
  ≤ 3 files. (Prefer splitting the task first; escalation applies only
  when the iterative-fix loop is inherent to the work, not merely large.)
- **AC-08** — CLAUDE.md §7 ("Context-Window Rule") documents the four
  signals — S1 expected tool-call volume, S2 scope openness, S3
  synthesis dependency, S4 iterative-fix loop — and their composition
  into a sizing decision, so every skill applies them consistently.

### Signals recap (authoritative form in CLAUDE.md §7)

- **S1 — Expected tool-call volume**: count of Bash + Read + Edit
  calls the task will make at runtime. Calibrated bands: < 30 OK;
  30–60 flag for model escalation if iteration loops are also
  expected; > 60 must split, plan fan-out, or escalate — splitting
  is always preferred.
- **S2 — Scope openness**: closed (file set named in scope) vs open
  (file set pattern-defined). Open scope requires a fan-out plan or
  a split-by-code-partition.
- **S3 — Synthesis dependency**: the deliverable's quality depends on
  the executing session holding multiple input domains at once.
  Synthesis-dependent tasks stay monolithic and use model escalation;
  agents are used only for breadth surveys that return distilled summaries.
- **S4 — Iterative-fix loop**: the task hands off to `verify-quality`
  or otherwise enters a RED → fix → re-verify cycle. High-iteration
  tasks consume far more tool-call budget than their goal.md scope
  suggests.

### What this requirement does **not** mandate

- A specific numeric byte threshold. Empirical data from the
  2026-05-16 autorun shows the JSONL-size cliff overlaps between
  successful and overflow sessions (a 800 KB session completed; a
  546 KB session overflowed). Sizing is decided by signals, not by
  a single byte cap.
- A replacement for mid-session `/compact` recovery. The
  `plans_and_protocols/` file-based memory system (CLAUDE.md §1)
  is the authoritative recovery path; the ACs above govern the
  *prevention* path (task sizing at creation and runtime).

## Related Requirements

- [REQ-PROC-008](../../workflows/orchestrator_workflow/requirements.md) — Orchestrator workflow manages context budget via agent fan-out; complements the prevention-path signals defined here.
- [REQ-PROC-058](../../requirements_management/implementation_task_planning/requirements.md) — task-derive-from-requ consumes the S1–S4 sizing signals defined here when planning tasks; REQ-PROC-058 already cross-references REQ-PROC-001 one-way and this is the reciprocal link.

---
## Version History
Consolidated from:
- 2025-08-31_requirement.md (original)
Consolidation date: 2026-01-04
Pre-migration commit: 1d3a2f9
