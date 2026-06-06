---
task_id: TASK-PROC-052-05
type: impl
parent_requirement: REQ-PROC-052
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 3
impact_reason: I3-DOCS
status: completed
effort: S
created: 2026-05-23
started: 2026-05-25
completed: 2026-05-25
session_completed_at: 2026-05-25T13:35:54Z
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-10]
  sections: []
scope_description: "Create or update documentation for SP1-SP6 privacy/security gates and their exception allowlists in a single authoritative location under doc/. Ensure consistency with REQ-PROC-052 requirements.md and the scripts that implement the gates."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: 2c52ed48
  file: ../../requirements.md
session_id: 397d3df8-6597-44c3-85a1-b8d3996c164c
session_account: web

---
# Goal: Document Privacy/Security Gates

## Objective

Create the authoritative documentation for privacy/security gates (SP1-SP6) in a single location under `doc/` so that a contributor or LLM agent can determine, without asking, what is forbidden and what is allowed. This fulfills REQ-PROC-052 AC-10.

## Requirements Summary

REQ-PROC-052 AC-10: "The active set of privacy / security gates and the allow-list for any deliberate exceptions (e.g. permitted non-security uses of SHA-1) are documented in a single authoritative location consistent with this requirement — a contributor or LLM agent can determine, without asking, what is forbidden and what is allowed."

For complete requirements at task creation time:
```
git show 2c52ed48:requirements_tasks/process/AI_rules/coding_standards/privacy_and_security/requirements.md
```

Current requirements: ../../requirements.md

## Scope

### In Scope
- Create `doc/architecture/privacy_security_gates.md` (or `doc/security/` if a new subfolder is warranted) covering:
  - SP1: No network I/O — forbidden imports, QR-only transfer
  - SP2: No telemetry SDKs — named SDK list
  - SP3: No hardcoded secrets — regex set
  - SP4: No weak crypto — SHA-1/MD5 restrictions, justification rules for non-security use
  - SP5: PII redaction in toString() — affected types, sentinel test pattern
  - SP6: Synthetic test data only — fixture rules
- Document the exception allowlist mechanism (SP4 inline justification comments)
- Reference the implementing scripts (`scripts/quality/check_no_*.sh`, `check_weak_crypto.sh`, etc.)
- Ensure consistency with REQ-PROC-052 requirements.md and CLAUDE.md gate table

### Out of Scope
- Modifying gate scripts
- Modifying requirements.md
- Code-quality gates (REQ-PROC-046) or test-quality gates (REQ-PROC-002)

## Acceptance Criteria

- [x] `doc/` contains a file documenting SP1-SP6 gates
- [x] Each gate: purpose, tool, pass condition, exception mechanism
- [x] Content is consistent with REQ-PROC-052 requirements.md
- [x] Content is consistent with the actual scripts in `scripts/quality/`
- [x] CLAUDE.md gate table references this doc

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies — gate scripts already exist and are stable |
