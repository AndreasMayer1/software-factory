# Audit — Batch D (AC-37..AC-41)

REQ-PROC-032 scribble-content ACs. Verification standard: producer artifact specifies
behavior correctly and consumers read it as the AC states. Draft-only scribble means
approval/handoff runtime instances are legitimately absent — judged against emitter/skill
spec. Storage mirror + metadata fields + lint scripts must already be operative.

## AC-37 "Scribble storage mirrors lib/features/"

Verdict: COVERED

- Parity lint exists and RUNS clean. `python3 scripts/quality/check_scribble_parity.py` →
  exit 0, output: 9 coverage-gap WARNINGs (lib/features leaves without a scribble) and
  `scribble-parity: 9 warning(s)`. No ERROR lines, no stale-path errors.
- Bidirectional divergence checked: `scripts/quality/check_scribble_parity.py:86-90`
  flags stale scribble feature_path with no matching `lib/features/` node (ERROR);
  `:92-97` flags lib leaf with no scribble (WARNING). `--strict` promotes warnings to
  errors (`:136-139`).
- NO legacy co-located scribble dirs. `find requirements_tasks -path '*/scribbles/v*' -type d | grep -v '^requirements_tasks/scribbles/'`
  → no output, exit 1 (grep no-match). Existing scribble is at the MIRRORED location:
  `requirements_tasks/scribbles/therapist/data_transfer/v1` and `/v2` (ls confirmed).
- `lib/core/ -> _core/` mapping documented: `requirements_tasks/SKETCHES_README.md:199`
  (`_core/  ← mirrors lib/core/`) and `:209` ("(or `_core/` for `lib/core/`)"); schema
  `.claude/schemas/scribble_metadata.yaml:50-52`.
- SKETCHES_README Storage section: `requirements_tasks/SKETCHES_README.md:174` ("centralized
  mirror of lib/features/, not co-located"), `:179` ("mirrors lib/features/<feature_path>/").
- Consumers resolve via feature_path mirror (not hardcoded co-located path):
  - ui-scribble-generator: `.claude/agents/ui-scribble-generator.md:8`, `:226-228`
    (`requirements_tasks/scribbles/<feature_path>/v{n}/`).
  - ui-scribble-iterate: `.claude/skills/ui-scribble-iterate/SKILL.md:20-22`
    (`SCRIBBLE_BASE = requirements_tasks/scribbles/<feature_path>/`), with REQ-ID search
    fallback `:23`.
  - ui-verify-flutter: `.claude/skills/ui-verify-flutter/SKILL.md:19-31` (feature_path
    mirror first, REQ-ID search fallback).
  - code-simple Sketch Gate: `.claude/skills/code-simple/SKILL.md:42` (feature_path first,
    REQ-ID search second, legacy co-located only as tertiary `(c)` fallback).
  - code-complex Sketch Gate: `.claude/skills/code-complex/SKILL.md:35` (same precedence).

Note (non-blocking): consumers retain a `(c) legacy fallback: [requirement]/scribbles/`
tier. AC says locate "not a hard-coded co-located path" — feature_path mirror is the
primary path; legacy is a graceful last-resort, not the hardcoded primary. No co-located
dirs exist to match it. Acceptable.

## AC-38 "Per-flow navigation captured"

Verdict: COVERED

- Schema exists: `.claude/schemas/flow_navigation.yaml` — `edges` (required, min 1) with
  `from`/`to`/`trigger` (`:45-70`), `escape_paths` (`:88-117`), `back_stack_policy`
  (`:119-126`). Location `requirements_user_needs/user_flows/<flow_slug>/flow_navigation.yaml`
  (`:6`).
- Emitter emits + maintains it: `.claude/agents/ui-scribble-handoff-emitter.md:104-111`
  (per unique flow_id: find flow folder, ordered screens, derive forward edges with
  triggers, escape paths, emit `{flow_folder}/flow_navigation.yaml`, validate against
  schema). "updated on every emitter run" `.claude/schemas/flow_navigation.yaml:12`,
  `:128-137` (last_updated/emitted_by). Trigger mandatory: emitter `:41`, `:141`.
- flutter_handoff points to it: emitter `:113-123` adds `flow_navigation_files:` block
  with one `{flow_id, path}` per emitted file; Rule `:142`.
- ui-verify-flutter reads it: `.claude/skills/ui-verify-flutter/SKILL.md:45` (step 2d loads
  each referenced flow_navigation.yaml), Phase 3b `:83-91` (per-edge route check, escape
  path check).
- Coding consumer reads it: code-simple `.claude/skills/code-simple/SKILL.md:49`
  ("Navigation graph (AC-38) ... edges[] define the GoRouter routes ... escape_paths[]
  define required back-navigation"); code-complex `.claude/skills/code-complex/SKILL.md:41`.

## AC-39 "Per-flow walk validation before approval"

Verdict: COVERED

- Walk validation in auto-review (pre-approval; auto-review is Phase 2, approval is Phase 5):
  `.claude/skills/ui-scribble-auto-review/SKILL.md:20-27` (step 1.5) — group flow_positions
  by flow_id, sort by step_number, read flow.md step intent, verify each step's intent is
  supported by a screen and its elements (`:24`).
- Flow-flaw routed upstream via revision channel, not patched: `:26` ("Flow flaw: ... create
  a revision task via the task-create revision sub-procedure (reason: flow_flaw,
  target_skill: ux-create-flow, responder_required: human ...). Do NOT include in the
  scribble gap list."). Scribble-gap path is distinct (`:25`).
- Per-flow one-line human walk instructions in the brief: `:39` ("Per-flow walk instructions
  ... one line per participating flow, e.g.: `Walk FLOW-003: open scribbles/v4/01_...html →
  02_...html → 03_...html`") — names file to open and screens in order. Emitted into
  `scribbles/v{n+1}/auto_review_brief.md` (`:35`).

## AC-40 "Approval trail aggregated across versions"

Verdict: COVERED

- ui-scribble-approve-handoff emits APPROVAL_TRAIL.md as an approval-time artifact:
  `.claude/skills/ui-scribble-approve-handoff/SKILL.md:17` (step 4, "Emit APPROVAL_TRAIL.md
  — write scribbles/APPROVAL_TRAIL.md (sibling of all version folders)"). Gated on
  approval (Phase 5, step 1 sets status: approved).
- Aggregates across ALL versions: `:18` (a — discover all version dirs v1,v2,… ascending).
- Synthesized from per-version feedback.md + briefs + diffs:
  - feedback.md: `:19` (read feedback.md "What Changed" + "Feedback" sections).
  - inter-version diffs: `:20` (c — for each vN>1 summarise gaps_fixed relative to vN-1).
  - per-version metadata incl. design_decisions/gaps_fixed: `:19`.
- Rejected alternatives / trade-offs / locked-decision rationale: structure `:21-43` carries
  per-version Design Decisions (decision + reason), Feedback/What Changed, and a final
  "Locked Decisions (Approved Version)" block `:41` (design_decisions verbatim).

Note: AC names "auto-review briefs" among synthesis sources; step 4 enumerates metadata +
feedback.md + gaps_fixed diffs but does not explicitly read `auto_review_brief.md`. The
gaps_fixed list (the brief's machine substrate) is consumed, so the decision history is
captured. Minor: brief not named as an explicit input. Does not break the AC's intent
(decision history across versions is aggregated). COVERED.

## AC-41 "Contributing-requirements and participating-flows discovery"

Verdict: COVERED

- Discovery script exists and RUNS. `python3 scripts/user_needs/update_scribble_requirements.py --help`
  → exit 0 (usage shown; `--dry-run`, `--lint-only` modes).
- `--lint-only` on the real scribble:
  `python3 scripts/user_needs/update_scribble_requirements.py --lint-only requirements_tasks/scribbles/therapist/data_transfer/v2/metadata.yaml`
  → exit 0, output: `DONE (lint-only): primary=REQ-FUNC-007-01 cross_cutting=[]
  flows=['FLOW-002', 'FLOW-003'] lint=OK`. (Also prints a non-fatal WARNING about an
  unrelated malformed-frontmatter requirements.md in shared/epic_evaluation — skipped, not
  this scribble.)
- Discovery from feature_path + requirements_matrix: `scripts/user_needs/update_scribble_requirements.py:127-152`
  (discover_primary matches requirement whose feature_path == scribble feature_path);
  flows from primary's `user_needs.implements_flows` `:114-124`, `:331`.
- UI-scope heuristic for cross-cutting: `:155-173` (`discover_cross_cutting` — req must have
  non-empty feature_path AND share ≥1 flow with primary).
- Ambiguity flagged, not silently empty: `:136-152` (no candidate or multiple candidates →
  is_ambiguous + reason); `:265-269` writes an `AMBIGUOUS: ... needs human review` comment;
  `:359-361` exits 2.
- Consistency lint primary<->feature_path: `:176-191` (`check_consistency` — primary's
  feature_path must equal scribble feature_path, else LINT ERROR + return 1). Invoked
  unconditionally `:325`.
- REQ-FUNC-007-01 ↔ feature_path therapist/data_transfer: CONFIRMED.
  `requirements_tasks/functional/shared/epic_data_transfer/feat_therapist_transfer_ui/requirements.md:2`
  (`id: REQ-FUNC-007-01`), `:14` (`feature_path: therapist/data_transfer`). Matches
  scribble metadata `feature_path: therapist/data_transfer` → lint=OK.
- Fields ALREADY exist in scribble_metadata schema (NO new frontmatter fields):
  `.claude/schemas/scribble_metadata.yaml:55-62` (contributing_requirements, required,
  min_items 1) and `:153-160` (participating_flows, optional).
- Populated in the real scribble: `requirements_tasks/scribbles/therapist/data_transfer/v2/metadata.yaml:137`
  (`contributing_requirements: [REQ-FUNC-007-01]`), `:138`
  (`participating_flows: [FLOW-002, FLOW-003]`).

Note (non-blocking doc drift): schema `:159` references
`scripts/scribbles/discover_scribble_requirements.py` but the operative script is
`scripts/user_needs/update_scribble_requirements.py`. Stale path in a doc comment only;
does not affect the field definition or AC satisfaction.

## Summary

| AC | Verdict |
|----|---------|
| AC-37 | COVERED |
| AC-38 | COVERED |
| AC-39 | COVERED |
| AC-40 | COVERED |
| AC-41 | COVERED |

COVERED: 5 · PARTIAL: 0 · NOT_COVERED: 0

Observations (non-blocking, not fixes): (1) consumers keep a legacy co-located fallback
tier — harmless, no co-located dirs exist. (2) approve-handoff step 4 does not name
auto_review_brief.md as an explicit synthesis input (uses metadata gaps_fixed instead).
(3) scribble_metadata.yaml:159 cites a stale script path. None block AC satisfaction.
