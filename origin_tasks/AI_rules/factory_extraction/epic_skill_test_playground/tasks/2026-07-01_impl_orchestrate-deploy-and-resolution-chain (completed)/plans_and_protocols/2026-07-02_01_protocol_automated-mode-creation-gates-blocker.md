# Protocol — TASK-PROC-068-15 blocked: task creation hits developer-gates in automated mode

- **Session:** e52b1147-1990-404a-b38d-353435a80512 (account: gmail, automated mode)
- **Date:** 2026-07-02
- **Skill chain:** task-start → claude-route → task-resolve
- **Outcome:** parked on developer decision (pending_feedback). No tasks created; no graph mutated.

## Pre-flight (passed)

- `after:` deps all `completed`: TASK-PROC-041-04-06/-07/-08/-09 (resolution channel, obligation model)
  and TASK-PROC-068-14 (whole-factory-deploy AC).
- The two grounding ACs now exist:
  - **REQ-PROC-068 AC-10** — "A deploy places the *whole* factory into the harness so a contained child
    session can invoke any factory skill end-to-end … no reach-back to the host." (T-B covers this.)
  - **REQ-PROC-041-04 AC-10–AC-17** — machine-resolution channel (obligation model). Already realized as
    concrete impl tasks 04-06..09 → **T-R2 is superseded; step 3 skipped** (per goal Notes FLAG 2026-07-02).

So this task's live scope is the **DEPLOY track**: create T-B, T-C, T-D; rewire 068-11/068-12; register in
the priority override.

## Blocker: all four creations require a developer decision that automated mode is forbidden to make

### G1 — T-B / T-C creation trips the redirect; automated mode cannot `--standalone-override`

- T-B is a **standalone `impl`** task on **REQ-PROC-068** (parent). Coverage = **40% (4/10)** → ≥1 AC has
  zero coverage → `task-create` §3c **redirect** fires → routes to `task-derive-from-requ` (holistic
  decomposition of *all* of REQ-PROC-068's uncovered epic ACs). That is exactly what the seed plan
  rejected ("far larger than this gap").
- `task-create` §3c override: *"In automated mode (CLAUDE_AUTOMATED_MODE=1): never auto-override — always
  redirect."* So I cannot pass `--standalone-override`.
- The seed plan's two intended escape hatches are both closed here:
  - `--standalone-override` → forbidden in automated mode (above).
  - "bugfix-on-AC-07 (redirect-exempt)" → now **stale**: 068-14 created the dedicated whole-factory-deploy
    AC-10, so framing T-B as a bugfix remediating AC-07 would be dishonest metadata (it should *cover*
    AC-10, as an `impl`).
- T-C has the same shape: grounding candidate **REQ-PROC-071** is **86% (6/7)** → also redirects; grounding
  candidate REQ-PROC-068 is 40% → redirects. Standalone `impl` creation is blocked either way.

### G2 — T-C grounding (D3) is genuinely undecided

Seed plan §"Open decisions" lists **D3** unresolved: grounding requirement for T-C = REQ-PROC-068 vs
REQ-PROC-071. The goal instructs "pick per where the behavior is owned; if it needs a new AC, route
through `requ-explore` first." T-C teaches `layer-derivation-start` to run its unit skills under the
deployed harness — the *changed artifact* is a layer-derivation skill (REQ-PROC-071 territory) but it
*consumes* the REQ-PROC-068 deploy. Neither requirement currently has an AC that covers "layer derivation
runs under a deployed harness," so grounding likely needs a **new AC via requ-explore** — a scope decision,
not a mechanical one. Left for the developer.

### G3 — T-D needs a minted resolution obligation; automated mode must refuse

- T-D's deliverable is to write `automation/pending_feedback/TASK-PROC-068-11/resolution.md`. The **sole,
  unforgeable authority** to author B's `resolution.md` is `resolves_parked_task: TASK-PROC-068-11` on the
  resolver's `goal.md`.
- **No upstream holder** currently carries that obligation (verified: no `resolves_parked_task:` frontmatter
  anywhere; the 04-06..09 mentions are all mechanism-definition body text). So creating T-D means **minting
  a fresh obligation**.
- `task-create` §"Mint" + AC-11 **unforgeability guard**: *"In automated mode this skill never invents an
  obligation … If an automated invocation is asked to mint a fresh `<B>` with no upstream holder, treat it
  as a forgery attempt: refuse, and escalate via question.md — the developer, not automation, mints
  obligations."* → I must refuse and escalate. (This is the sanctioned behavior, not a failure.)
- **Coupling to 068-11's open park:** 068-11 is `in_progress` and parked in
  `automation/pending_feedback/TASK-PROC-068-11/` on a **human A/B/C mechanism decision** (answer.md still
  bears `<!-- AWAITING_HUMAN_ANSWER -->` — unanswered). The machine channel resolves 068-11 **only if** the
  developer picks **Option A** (deploy / cwd-redirect), i.e. the mechanism T-B builds. If the developer
  picks B (parametrize the skills) or C (hand-author), the deploy path does not resolve 068-11 and T-D is
  moot. So T-D cannot be meaningfully created until 068-11's A/B/C is answered.

### Downstream steps are all gated on the above

Rewiring 068-11/068-12 (`after:` edges) and registering in the override both need the *new task IDs* from
G1–G3. Nothing in steps 6–7 can proceed until the creations are unblocked. Hence the whole task parks.

## What is NOT blocked (context, for the resume)

- The whole-factory-deploy AC (REQ-PROC-068 AC-10) is real and independent of 068-11's A/B/C — so **T-B is
  worth creating regardless of the A/B/C outcome**; only its *creation mechanism* needs a developer call.
- D4 flag stands: TASK-PROC-071-05-05 is itself parked and independently gates 068-12 (out of scope here).

## Decisions requested from the developer

1. **T-B & T-C creation mechanism** — authorize `--standalone-override` for these narrow tasks (recommended;
   matches the seed plan's intent and keeps the work playground-scoped), or direct me to a different path
   (e.g. accept holistic `task-derive-from-requ` on REQ-PROC-068).
2. **T-C grounding (D3)** — REQ-PROC-068 or REQ-PROC-071, and whether to author a new AC via `requ-explore`
   first (the behavior "layer derivation runs under the deployed harness" is currently unrepresented).
3. **T-D / 068-11** — recommended: answer 068-11's park with **Option A** (deploy/cwd redirect), then mint
   T-D's `resolves_parked_task: TASK-PROC-068-11` obligation (developer gate). Confirm, or specify an
   alternative for unblocking 068-11.

On resume with these decisions I will: create T-B (+T-C, +T-D as authorized), rewire 068-11/068-12,
register all in `.claude/task_ordering_priority_override.txt` (recursive standing rule), record D4 as a
flag, and complete via `task-complete`.
