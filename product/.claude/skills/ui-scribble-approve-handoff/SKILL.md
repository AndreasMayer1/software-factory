---
name: ui-scribble-approve-handoff
description: On scribble approval, emit the Flutter implementation handoff
tools: "*"
model: inherit
---

You finalize an approved scribble version: record approval, emit the implementation handoff, and (for flow-linked requirements) refresh the composite flow index. Invoked by `ui-scribble-iterate` (Phase 5) when the developer approves a version.

Inputs from caller: the approved scribble version path `v{n}`, the requirement path.

## Steps

1. Update `scribbles/v{n}/metadata.yaml`: `status: approved`.
2. Update the previous version's `metadata.yaml`: `status: superseded`.
3. **Emit handoff** — spawn `ui-scribble-handoff-emitter` to read every approved screen's COMPONENT MAPPING block + `metadata.yaml` and write `scribbles/v{n}/flutter_handoff.yaml` (per-element HTML-selector → Flutter-widget mapping; schema `.claude/schemas/flutter_handoff.yaml`).
4. **Emit APPROVAL_TRAIL.md** — write `scribbles/APPROVAL_TRAIL.md` (sibling of all version folders) by:
   a. Discovering all version directories under `scribbles/` (v1, v2, …) sorted ascending.
   b. For each version: read `metadata.yaml` (fields: `version`, `date`, `status`, `design_decisions`, `gaps_fixed`) and `feedback.md` (extract "What Changed" section if present, and "Feedback" section).
   c. Inter-version diffs: for each vN>1, summarise what `gaps_fixed` in vN addresses relative to vN-1 (derived from `gaps_fixed` list).
   d. Structure:
      ```
      # Approval Trail — <feature_path>
      Requirement: <req_id>   Approved Version: v{n}   Approved: <date>

      ## Version History
      ### v1 — <date> — superseded
      #### Design Decisions
      - <decision> (<reason>) [screens: …]
      #### Feedback / What Changed
      <content>

      ### v{n} — <date> — approved
      #### What Changed from v{n-1}
      <gaps_fixed summary>
      #### Design Decisions
      - <decision> (<reason>) [screens: …]
      #### Developer Feedback
      <content>

      ## Locked Decisions (Approved Version)
      <design_decisions from approved version, verbatim>
      ```
5. **Phase 5a — flow composite index** (only if the requirement references a user flow):
   ```
   python scripts/user_needs/generate_flow_scribble_index.py --flow <flow_id>
   ```
   (Writes `requirements_user_needs/user_flows/<flow>/scribble_index.html`.) Skip if no parent flow.
6. Report to the developer: "Scribble v{n} approved. Proceed to implementation. After implementation, use `ui-verify-flutter` to check structural match, then `ui-improve-flutter` for visual polish."

## MUST NOT
- Emit `flutter_handoff.yaml` unless `metadata.yaml` status == approved.
- Attempt visual polish or alter screen HTML.
