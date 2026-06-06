# User Initial Input — TASK-PROC-045-06

(Captured verbatim from the spawning agent's instructions; the user's intent
was relayed without edits.)

Update REQ-PROC-045 to add a new acceptance criterion defining the
keyword-grep mechanism for cross-reference completeness detection in
requirements.md files. This mechanism is invoked by requ-explore Phase 1.4
(already exists) and by task-derive-from-requ Phase 1.5 (new per
REQ-PROC-058 AC-17).

The mechanism: derives 2-4 search terms from a requirement's topic (domain
nouns, action verbs, component names), greps
requirements_tasks/functional/, non-functional/, and process/, surfaces
semantic matches NOT already cross-referenced in the target requirement's
after:, blocks:, or ## Related Requirements section.

Implementation may be a script (preferred per deterministic-first principle)
or inline skill instructions — to be decided by impl tasks.
