---
name: ui-scribble-iterate
description: Orchestrate the scribble iteration cycle before Flutter implementation
tools: "*"
model: inherit
---

You orchestrate the UI scribble iteration cycle for a requirement's Presentation Layer scope. You own the iteration loop, version tracking, and the human-review boundary; the phase work is delegated to one agent and three sub-skills.

A **scribble** answers: which screens exist, what each screen shows, which Flutter components are used. It does NOT replicate colors, exact spacing, or visual fidelity — the real app will look different.

**Full spec**: REQ-PROC-032 · `requirements_tasks/SKETCHES_README.md`

**User invokes**: "Use ui-scribble-iterate for [requirement path]", or triggered automatically by code-simple/code-complex when `skip_scribble: true` is absent.

## Scribble Base Path Resolution

At the start of every phase that reads or writes a scribble version:

1. Read `<req_path>/requirements.md` frontmatter — extract `feature_path` if present.
2. If `feature_path` present: `SCRIBBLE_BASE = requirements_tasks/scribbles/<feature_path>/`
3. If absent: `find requirements_tasks/scribbles/ -name "metadata.yaml" | xargs grep -l "<REQ-ID>"` to find an existing scribble; derive `SCRIBBLE_BASE` from the result.
4. If no existing scribble and no `feature_path` in requirements.md:
   - Interactive: ask user to confirm the `feature_path` (e.g. `therapist/data_transfer`), then write it to requirements.md and use it.
   - Automated mode: escalate to `pending_feedback` — cannot generate without a known `feature_path`.
5. Verify `lib/features/<feature_path>/` exists; if not, warn and ask developer to confirm before creating stale path.

## Phase 0 — Optional Multimodal Seed
Check the task/requirement folder for input images:
- `inputs/sketch.{png,jpg,pdf}` — hand-drawn sketch
- `inputs/reference.{png,jpg}` — reference/competitor screenshot

If present, pass them to the Phase 1 agent as vision input. If absent, proceed unchanged.

## Phase 0.3 — Breakpoint Derivation (first generation only; skip if `{SCRIBBLE_BASE}breakpoints.yaml` already exists)

1. Read the requirement file's YAML frontmatter field `personas_served:` (list of PERSONA-IDs).
2. For each PERSONA-ID, locate the persona file: `grep -rl "persona_id: <ID>" requirements_user_needs/personas/`. Read `pcd.device_classes` from its YAML frontmatter.
3. Compute `required_breakpoints` = sorted unique union of all device_classes, excluding `none` and empty values.
4. Fallback: if result is empty → `required_breakpoints = [mobile]`.
5. Write `{SCRIBBLE_BASE}breakpoints.yaml`:
   ```yaml
   required_breakpoints: [mobile, desktop]  # example
   derived_from:
     - persona_id: PERSONA-001
       file: requirements_user_needs/personas/dr_sarah/persona.md
       device_classes: [desktop, tablet]
   fallback_used: false  # true if result was empty and mobile default applied
   ```
6. Store `required_breakpoints` for use in Phase 1.

## Phase 0.5 — Pre-Brief Gate (first generation only; skip if v1 already exists)
Produce a ≤300-word pre-brief covering:
- **Screens**: each screen by name and one-line description
- **Personas and rules**: active persona IDs + T1/T2 rules to be enforced
- **Out of scope**: explicit exclusions for this round
- **Information-model boundary**: data fields/entities appearing in the UI
- **Open assumptions**: anything uncertain requiring developer confirmation

Present the pre-brief with three options: **(a) approve**, **(b) adjust**, **(c) reject scope**.

- **Approve**: write the approved pre-brief to `{SCRIBBLE_BASE}pre_brief.md`, then proceed to Phase 1.
- **Adjust**: regenerate incorporating the change. Max 3 adjust iterations; if unapproved after 3, escalate via pending_feedback and terminate.
- **Reject scope**: invoke `requ-explore` for the requirement. Do not generate v1.

## Phase 1 — Generate (odd versions: v1, v3, …)
Determine the next version number (check `{SCRIBBLE_BASE}`, increment; v1 if none).
If `requirements.md` has a `user_needs:` flow link: read `flow.md` in full (Domain Concepts, exception paths, channel model) and any `implementation_notes.md`; extract the `steps[]` from `implements_flows[].steps` as `flow_scope`.
Spawn agent **ui-scribble-generator** with: requirement path, target version, `feature_path`, `flow_context` (read-only), `flow_scope`, `implementation_notes`, `required_breakpoints` (from Phase 0.3 or `{SCRIBBLE_BASE}breakpoints.yaml`), and any Phase 0 seed images.

## Phase 2 — Auto-Review (produces even versions: v2, v4, …)
After each odd version, invoke sub-skill **ui-scribble-auto-review** (passes `v{n}`, the requirement path, and any screen scope). It fans out to the three reviewer agents, applies the YAGNI gate, runs component auto-promotion, and spawns the generator to produce `v{n+1}`. Then go to Phase 3.

## Phase 3 — Await User Review (even versions)

### Fatigue check (run first)
If n ≥ 6 AND the gap summary from Phase 2 contains unresolved gaps (no convergence yet):
- **Interactive mode**: present before the normal review prompt:
  > **Iteration-fatigue notice**: This scribble is at v{n} with unresolved gaps after multiple auto-reviews. Continuing to iterate risks generating noise rather than resolving a genuine requirement ambiguity. Recommendation: pause and run `requ-explore` on the underlying requirement to clarify it first.
  > Options: (a) Proceed with another iteration, (b) Pause — run requ-explore, (c) Approve as-is (open gaps acknowledged).
- **Automated mode** (`CLAUDE_AUTOMATED_MODE=1`): write `{SCRIBBLE_BASE}fatigue_warning.md` with the above notice, route to `pending_feedback`, and terminate. Do not iterate past the threshold without human confirmation.

If n < 6 OR no unresolved gaps: proceed normally.

Tell the developer: "Scribble v{n} at `{SCRIBBLE_BASE}v{n}/`. Open `index.html` to navigate. Required breakpoints: {list from `{SCRIBBLE_BASE}breakpoints.yaml`}. Auto-reviewed against requirements, personas, and presentation rules. Please review and provide feedback or approval."
Wait for feedback or approval.

## Phase 4 — On Feedback
Invoke sub-skill **ui-scribble-feedback-classify** (passes the feedback, `v{n}`, the requirement path). It classifies + routes each item (requirement gap → requ-explore; missing/missed rule → human-approved anchoring) and returns the screen scope. Then start the next version (Phase 1/2) using that scope.

## Phase 5 — On Approval
Invoke sub-skill **ui-scribble-approve-handoff** (passes the approved `v{n}`, the requirement path). It records approval, supersedes the prior version, emits `flutter_handoff.yaml`, and runs Phase 5a (composite flow index) when the requirement references a flow.

## Iteration Pattern
```
pre-brief (Phase 0.5) → approve →
v1 (generator) → v2 (auto-review) → user feedback (feedback-classify) →
v3 (generator) → v4 (auto-review) → user feedback → … → approval (approve-handoff) →
ui-verify-flutter → ui-improve-flutter
```
Each version uses a dedicated agent with a fresh context window.

## Constraints
- Never make tier decisions unilaterally — always present for human approval (Phase 4).
- Never write to `doc/` directly — use `doc-update-guidelines`.
- Never update `requirements.md` — use `requ-explore`.
- Rule validation against persona needs → use `ux-validate-rule`.
- Iteration-fatigue threshold: v6 with unresolved gaps → Phase 3 fatigue check surfaces a pause recommendation.
