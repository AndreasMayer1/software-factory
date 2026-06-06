---
task_id: TASK-PROC-067-01
type: bugfix
parent_requirement: REQ-PROC-067
urgency: 4
urgency_reason: U4-BLOCK
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-06-01
effort: M
created: 2026-06-01
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-02, AC-03, AC-05]
  sections: []
scope_description: "Mitigate Claude Code #63966 empty-tool-output regression and remove local aggravators (hook stdin hygiene, per-tool hook load, CRLF line endings)."
release_description: ""
opus_recommended: false  # reason: config/hooks remediation with a clear, bounded fix set — no architectural judgment required
worktree_path: ""
requirements_version:
  commit: 84880bc2
  file: ../requirements.md
---

# Goal: Ensure that AC-02, AC-03 and AC-05 of REQ-PROC-067 (Claude Code Usability) work correctly

## Objective

Mitigate the Claude Code empty-tool-output regression ([anthropics/claude-code#63966](https://github.com/anthropics/claude-code/issues/63966)) that surfaced on 2026-06-01 in long-running Opus 4.8 sessions on CLI 2.1.159, and remove the local configuration aggravators that compound it. This is the first remediation task under REQ-PROC-067 (Claude Code Usability).

The upstream platform bug itself cannot be fixed here; this task delivers the in-project mitigations and aggravator removal, and records the version-awareness note.

## Bug Report

**Steps to reproduce:**
1. Run a long Opus 4.8 session (CLI 2.1.159) with many parallel tool calls (Bash/Read/Edit/MCP), e.g. session `5b7178b8` (2026-05-31).
2. Issue tool calls in parallel batches and continue for an extended period.

**Expected behavior:**
Each tool call's result is delivered to the model complete and in order; the agent acts on real output.

**Actual behavior:**
Tool-call results render empty / `(No content)` in the live UI, then flush late and out of order. The transcript JSONL keeps the correct output (data is not lost — delivery and ordering are broken). The agent perceives "empty" output, inserts shell-liveness probes (`echo hello`, `echo PROBE2`, `printf MARKER`), and falls back to redirect-to-`/tmp`-then-Read and Python edits — ~30 wasted calls in the observed session. CRLF-garbled `grep`/`cat` output on `requirements_tasks/**` triggered the first false "empty" perception.

**Environment:** Devcontainer (WSL2 ext4), Claude Code CLI 2.1.159, model claude-opus-4-8. Upstream issue reproduced on 2.1.154 / 2.1.158; OPEN, no upstream fix.

**Logs:** Session transcript `5b7178b8-1a1d-41e1-981d-16d672d21741.jsonl` (assistant's own inline diagnosis: "output-flushing quirk … CRLF … switched to Python"). Upstream: #63966 (documents the same `/tmp`-redirect + `echo PROBE` workarounds).

## Requirements Summary

REQ-PROC-067 asserts Claude Code usability as a hard factory dependency. This task addresses:
- **AC-02** — every hook in `.claude/settings.json` drains its stdin before exit (no EPIPE/SIGPIPE under the 2.x stdin-payload contract).
- **AC-03** — no hook runs on a broader tool-event scope than its function requires.
- **AC-05** — version-controlled text files use LF, enforced by `.gitattributes`, so tool output is un-garbled on every host.
- **Partial AC-01 / AC-04** — record the active-version regression and the mitigation in effect (version pin and/or reduced parallel batch size). Full operator-surfacing of version regressions is left to a follow-up task under REQ-PROC-067.

For complete requirements at task creation time:
```
git show 84880bc2:requirements_tasks/process/AI_rules/ai_tool_management/claude_code_usability/requirements.md
```
(Requirement is newly created in this change set; if the hash predates it, read the working copy.)

Current requirements: ../requirements.md

## Scope

### In Scope
- Harden every `.claude/hooks/*.sh` to read and discard stdin before any early exit (especially the catch-all `post_tool_use_inbox.sh`, which currently never reads stdin).
- Reduce per-tool-call hook overhead: re-scope or gate the per-`Read` logging hooks added 2026-05-31 (`pre_read_log_event.sh`, `post_read_log_bytes.sh`) so they do not fire a shell+jq on every Read unless genuinely needed.
- Add/extend `.gitattributes` to enforce LF on repository text files; normalize existing CRLF under `requirements_tasks/**`.
- Record CLI-version awareness for #63966: an operator-facing note plus the mitigation actually in effect (version pin and/or reduced parallel tool-batch size).

### Out of Scope
- Fixing the upstream platform bug #63966 itself (not in our control).
- Full automated operator-surfacing of known-bad CLI versions (AC-04 in full) — separate follow-up task under REQ-PROC-067.
- Any `lib/`, `test/`, or `integration_test/` Dart code change.

## Acceptance Criteria

- [x] Every hook command referenced in `.claude/settings.json` reads and discards stdin before exiting on all code paths (verified by inspection of each `.claude/hooks/*.sh`). [AC-02]
- [x] No hook fires on a broader tool-event scope than its function requires; the per-`Read` logging hooks are either justified for all Reads or re-scoped/gated. [AC-03]
- [x] `.gitattributes` enforces LF for repository text files, and existing CRLF under `requirements_tasks/**` is normalized to LF (a fresh `grep`/`cat` on a sample file shows no `\r`). [AC-05]
- [x] The active CLI version's #63966 status and the mitigation in effect are recorded where an operator will see them. [partial AC-01/AC-04]
- [x] All hook changes were made via the `claude-write-hook` skill; `.claude/settings.json` gate hooks were not hand-edited.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

- **Governed files**: hook scripts MUST be changed via the `claude-write-hook` skill. Do NOT hand-edit the gate hooks wired into `.claude/settings.json`.
- This is process/config work (`.claude/hooks/`, `.gitattributes`) — not Dart. If any temporary probe is added, prefix diagnostics with `[DIAG-*]` and open temporary blocks with `// TEMPORARY:` per CLAUDE.md §7.
- Workflow: use the `code-bugfix` skill in slim mode (scripts/config), not the Flutter worktree variant.
- Evidence trail for this bug is in the 2026-06-01 investigation (session `5b7178b8`) and upstream issue #63966.
