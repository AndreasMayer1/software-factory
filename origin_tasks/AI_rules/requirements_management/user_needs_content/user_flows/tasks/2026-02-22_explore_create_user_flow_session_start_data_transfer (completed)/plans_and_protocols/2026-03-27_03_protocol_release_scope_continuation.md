# Protocol: FLOW-003 release_scope — Continuation

**Date**: 2026-03-27
**Context limit reached** — this session ends here. Continue in a new session from this file.

---

## What happened in this session

1. User requested adding missing release packages to FLOW-003.
2. Discovered that `target_packages` (mapping to existing RELEASE_BACKLOG.md IDs) was the wrong concept for flow-level authoring — flows describe new features that don't have backlog entries yet.
3. Refactored the release planning pipeline across 5 skills:
   - `ux-flow-draft`: `target_packages` → `release_scope` (flow-internal chunks with label/covers/priority integer)
   - `requ-derive-from-flow`: goal.md gets `suggested_release_chunk`
   - `requ-explore`: propagates `suggested_release_chunk` → `release_chunk` in requirement YAML
   - `task-create-impl`: step 3.3b inherits `release_chunk` from parent requirement
   - `release-plan`: new Action 4b discovers unformalized chunks and drives formal package creation
4. Opus advisor reviewed the pipeline and found 5 issues — all fixed and committed.

All changes are committed on branch `develop`.

---

## Open: FLOW-003 release_scope still missing

FLOW-003 (`requirements_user_needs/user_flows/session_start_data_transfer/flow.md`) has no `release_scope` field yet. It needs to be added to the YAML frontmatter.

The flow's current `review_status` is `aligned` and must be reset to `in_review` when the YAML is updated.

### Proposed release_scope for FLOW-003

```yaml
release_scope:
  - label: "Core Transfer"
    covers: "Happy path Steps 1–6 (QR Transfer Screen, animated QR, webcam reception, visualization open)"
    priority: 1
  - label: "File Transfer"
    covers: "Exception 4.3"
    priority: 2
  - label: "Remote Sessions"
    covers: "Exceptions 4.4, 4.5"
    priority: 2
  - label: "Transfer Setup Edge Cases"
    covers: "Exceptions 1.1, 2.1, 2.2 (app not installed, pairing failure, no data)"
    priority: 3
  - label: "Transfer Execution Edge Cases"
    covers: "Exceptions 3.1, 3.2, 4.1, 4.2 (no-share, scope control, QR failure, interrupted)"
    priority: 3
  - label: "Paper + Parallel Delivery"
    covers: "Exception 4.6"
    priority: 4
  - label: "Storage & Compatibility"
    covers: "Exceptions 5.1, 5.2, 6.1 (storage full, app not ready, version mismatch)"
    priority: 4
```

User had not yet confirmed or adjusted this proposal when context limit was reached.

---

## Next steps

1. Present the `release_scope` proposal above to the user and ask for confirmation or adjustment.
2. After user confirms: edit `flow.md` YAML frontmatter — add `release_scope` block, set `review_status: in_review`, add `review_history` entry (seq: N+1, from: aligned, to: in_review, reviewer: LLM, notes: "Added release_scope — returning to in_review."), update `updated: 2026-03-27`.
3. Update FLOW_INDEX.md entry for FLOW-003 if status changed.
4. Commit: `git commit -m "ux(FLOW-003): add release_scope, return to in_review"`
5. Ask user if flow is content complete → if yes, invoke `ux-flow-complete`.
