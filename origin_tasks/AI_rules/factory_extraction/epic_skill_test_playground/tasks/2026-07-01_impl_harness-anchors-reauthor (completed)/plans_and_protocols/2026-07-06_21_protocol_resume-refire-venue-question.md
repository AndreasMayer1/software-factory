# Protocol 21 — Resume after 041-06-05 verified: re-surface the A/B/C venue question

Agent: main session (automated), session ec060365-1ed5-4d49-98ce-cce64740eaf8, account web.

## What changed since protocol 20

`TASK-PROC-041-06-05` (delegated-LLM-work contract verify) is now `completed` — confirmed 12/12 ACs
pass (commit `a16de5e2`). All three `after:` dependencies (`068-16`, `066-13`, `041-06-05`) are
`completed`. Working tree confirmed clean of this task's residue (harness anchors intact at HEAD,
no stray deletions).

## Why this session parks again instead of proceeding

Protocol 20 gated the task on the fix specifically so the **A/B/C venue question from protocol 19**
could be asked "fix-protected" rather than answered against the unfixed orchestrator — it did not
answer that question. The question itself is unchanged and still a genuine human decision:

- Remaining substance owed (checkpoint-18): re-derive both personas + both scenarios via the real
  `ux-write-persona`/`ux-write-scenario` skills against the deepened Driver–Context spine guidance.
- The only mechanism to author into the harness tree is the contained bwrap/nested-`claude`
  playground child (protocols 13–19) — expensive (~$1.7–2 / ~40 turns), previously hit account
  session limits mid-run twice, and self-approves unless reset.
- Developer's checkpoint-18 "live test" framing implies they want to *observe* the re-authoring —
  which an unobserved automated run defeats.

This is a cost / venue / hard-to-reverse call, not something to self-authorize. Re-asking it now
that the gate condition is satisfied, per protocol 19's original A/B/C options (verbatim, unchanged).

## Action

Park via `pending_feedback` (exit 2). Task left `in_progress` (session_id/session_account/started
already recorded by `task-start`). Full A/B/C option text: see protocol 19 (not restated in the
question to keep it token-light).
