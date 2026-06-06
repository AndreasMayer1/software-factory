---
task_id: TASK-PROC-046-17
type: explore
parent_requirement: REQ-PROC-046
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
effort: S
created: 2026-05-22
completed: 2026-05-22
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Remove Stop hook; add env-var fast-skip for the pre-commit gate run; update REQ-PROC-046 'When This Requirement Does NOT Apply' section accordingly."
release_description: ""
opus_recommended: false
writes_requirements: true
requirements_version:
  commit: 03c4ec5c
  file: ../requirements.md
---

# Goal: Remove Stop hook and add env-var fast-skip for the pre-commit gate run

## Objective

The verify-quality `Stop` hook, introduced by TASK-PROC-046-11, fires on every
end-of-turn and re-runs the full per-change gate set whenever the working tree
contains any modified file under `lib/`, `test/`, or `integration_test/` — even
when the current session did not produce those modifications. The check is
"is the tree dirty?", not "did I dirty the tree?". The hook therefore enters an
infinite oscillation in any session that opens against an already-dirty tree:
hook fires → gates run → returns `additionalContext` → the LLM's next turn
says "okay" → end-of-turn fires the hook again → loop.

This exploration enters the problem space of *where verification of the
back-pressure gates legitimately belongs* and *how to short-circuit redundant
runs* — without weakening the back-pressure protocol that REQ-PROC-046 AC-10
makes mandatory.

## Background

The enforcement mechanism shipped with TASK-PROC-046-11 has three triggers, all
invoking the same gate set:

1. **`Stop` hook** (`.claude/settings.json`) — fires on every Claude Code
   end-of-turn; uses `git diff --name-only` over the full tree as the in-scope
   check; returns gate failures as `additionalContext` to the next LLM prompt.
2. **`PreToolUse(Bash:"git commit*")` hook** — fires when the LLM tries to
   commit; uses `git diff --name-only --cached` (staged set) as the in-scope
   check; denies the commit on RED. (This scope fix was applied by the
   TASK-PROC-046-13 answer, but only to the pre-commit hook; the `Stop` hook
   still uses the full-tree check.)
3. **`task-complete` skill step 2a** — invokes `verify-quality` directly;
   refuses to mark the task `status: completed` on RED.

Across the project's history, the LLM has never failed to call `task-complete`
at task end. The third trigger therefore reliably runs verify-quality once at
the end of every code task. The pre-commit hook then re-runs the full gate set
when `task-complete`'s step 5 (the commit) is reached. The doubled run wastes
30 s – 2 min per task. The `Stop` hook adds a third run that re-runs the same
gates on every turn including the one-word "okay" reply that follows.

The agreed direction (from the conversation that produced this task):

- **Drop the `Stop` hook entirely.** The two remaining triggers (pre-commit
  hook + `task-complete` step 2a) preserve REQ-PROC-046 AC-10's "never declared
  complete while RED" property: `task-complete` refuses to set `status:
  completed`, and any subsequent commit attempt is blocked by the pre-commit
  hook. There is no realistic path where bad code reaches `develop`.
- **Add a content-hash fast-skip via environment variable** to the pre-commit
  hook. `verify-quality`, when it concludes GREEN, exports
  `QUALITY_GREEN_HASH=<git stash create -u hash>`. The pre-commit hook reads
  the env var, recomputes `git stash create -u` on its own current view of the
  tree, and skips the gate run if the hashes match — the exact tree state was
  already verified GREEN in this process tree.
- **PRE/POST atomicity tripwire** inside `verify-quality`: capture the
  stash-create hash *before* the gate run and again *after*. Only export
  `QUALITY_GREEN_HASH` if the two match. This rejects cache writes corrupted by
  a concurrent session editing the shared worktree mid-run, in the safe
  direction (no false-greens leak; we just don't get a fast-skip in that turn).

The env-var route is sufficient because the user does not commit manually —
every commit flows through `task-complete`'s step 5, which runs in the same
process tree as the verify-quality call from step 2a. Sessions that share a
worktree but live in separate processes don't share env vars; they fall back
to a full gate run, which is the correct conservative behaviour.

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-05-22_00_user_initial_input.md`

Read it as a seed bed, not a spec.

For complete requirements at task creation time:
```
git show 03c4ec5c:requirements_tasks/process/AI_rules/coding_standards/code_quality/requirements.md
```

Current requirements: ../requirements.md

## How to Approach This

Use design thinking as the guiding process — empathize before defining,
diverge before converging, let questions lead, iterate.

A single read of the requirement won't be enough. The text in §"When This
Requirement Does NOT Apply" calls out both hooks explicitly; the Behaviour
section enumerates the gates but is silent on triggers; AC-10 names the
"never declared complete while RED" invariant but does not pin the trigger
choice. The exploration's job is to pin down exactly which words must change,
and to surface any second-order text — for example, in the Common Pitfalls,
the Examples, or the References — that load-bears on the Stop hook's
existence.

Surface surprises. The most valuable discoveries are the ones that were not
anticipated when the task was framed.

## Seeds

- **Where in REQ-PROC-046 is the Stop hook actually referenced?** Walk the
  file linearly. Note every reference. Decide for each whether it's load-
  bearing (i.e. removing the Stop hook invalidates the surrounding claim) or
  incidental (an enumeration that just needs the entry trimmed).

- **Does the auto-bypass paragraph (§"When This Requirement Does NOT Apply",
  bullet about zero staged files) need to mention the env-var route at all?**
  The env-var fast-skip is not a "scope auto-bypass" — it's a "this state was
  already verified" optimization. Different mental model. Could be its own
  bullet, or its own short subsection, or referenced from the verify-quality
  skill instead of the requirement. Where does each placement belong?

- **AC-10's invariant**: "never declared complete while RED". With the Stop
  hook gone, is there any path the requirement asserts is gate-protected that
  is now unprotected? Read the AC verbatim and walk the failure modes.

- **`verify-quality` skill** (`.claude/skills/verify-quality/skill.md`) has its
  own §"Notes on hook integration" naming the `Stop` hook. Identify every
  downstream document that references the hook and inventory the changes
  required.

- **The on-disk content-hash cache alternative** was rejected by the user
  during the brainstorm. Briefly note *why* it was rejected (env var is
  simpler given user never commits manually) so a future agent doesn't
  re-litigate it.

- **Concurrent sessions on the shared worktree**: the env-var route is
  process-tree-scoped; a second simultaneous session's commit doesn't see the
  first's env var and falls back to a full gate run. Is this correct? Are
  there edge cases (e.g. a sub-shell of the same session that loses the env
  var) where this becomes annoying?

- **The escalation path at cycle 5** still works under the new model
  (`task-complete` step 2a invokes verify-quality which writes the pending-
  feedback file directly). Walk the flow once to confirm — escalation is the
  load-bearing safety net and must not be silently broken.

## Execution Model

Gather raw material — read the requirement linearly, walk the related files,
follow the references. Synthesize iteratively; multiple gathering rounds may
be needed before the scope of the requirement edit is clear.

The session's model is fixed at launch (Opus when `opus_recommended: true`,
Sonnet otherwise). This task is `opus_recommended: false` — the scope is
narrow and the engineering work is mostly mechanical text editing once the
analysis is done.

**Web research**: probably not needed for this task. If a seed requires
external knowledge (e.g. git stash-create semantics under concurrent index
writes), delegate to a `general-purpose` agent; do not run WebSearch inline.

## Output

A clear specification of the REQ-PROC-046 `requirements.md` text edits
needed:
- the exact bullet in §"When This Requirement Does NOT Apply" that must lose
  the "Stop hook" mention,
- a new or updated bullet that documents the env-var fast-skip as a
  scope-derived non-application of the gate run,
- any other lines anywhere in the file that load-bear on the Stop hook's
  existence and need parallel updates,
- the corresponding edits required in `.claude/settings.json` (remove the
  Stop hook entry; modify the pre-commit hook to consult `QUALITY_GREEN_HASH`),
- the corresponding edits required in `.claude/skills/verify-quality/skill.md`
  (export the env var on GREEN; PRE/POST atomicity; update §"Notes on hook
  integration"),
- the corresponding edits required in `.claude/skills/task-complete/skill.md`
  step 2a if any are needed for the env var to propagate to step 5's commit,
- the corresponding edits required in `CLAUDE.md` §7 if any of the documented
  enforcement mechanism is now stale,
- the corresponding edits to `automation/pending_feedback/TASK-PROC-046-13/answer.md`
  if its in-scope-fix description (currently mentioning only the commit-hook
  scope fix) needs an addendum noting the Stop hook removal.

The output is qualitative: a future implementer reading this task should
understand which files to touch and roughly what the diff looks like, without
needing to redo the analysis.

## Acceptance Criteria

- [x] Exploration produced at least one synthesis round of REQ-PROC-046 text
- [x] Every reference to the `Stop` hook in REQ-PROC-046 and its load-bearing
      downstream documents (verify-quality skill, task-complete skill,
      CLAUDE.md §7, settings.json) is identified and classified (load-bearing
      vs. incidental). Findings: one line (`requirements.md:75`) is the only
      load-bearing reference in the requirement itself; downstream references
      live in `verify-quality/skill.md:24,26,244` and `CLAUDE.md:276,278`.
      Historical references in TASK-PROC-046-11's completed task folder are
      not edited (they record what was built, not what currently exists).
- [x] The fast-skip mechanism is specified concretely enough that downstream
      impl can proceed: **NOTE — the original "env var" framing was withdrawn
      after Phase 1 investigation surfaced that env vars set inside one Claude
      tool call do not propagate to a later hook subshell in this architecture
      (only session-level env like `SKIP_QUALITY_GATES`, set before `claude`
      launches, propagates).** The mechanism is instead a one-line cache file
      `.git/quality_green_hash` containing the `git stash create -u` tree hash
      written by `verify-quality` on GREEN, with PRE/POST atomicity (only
      write if pre-run hash == post-run hash, rejecting concurrent-edit races
      on the shared worktree). The pre-commit hook reads the file, recomputes
      its own hash, and skips the gate run on match. Order of evaluation in
      the pre-commit hook: (1) `SKIP_QUALITY_GATES=1` manual bypass, (2)
      zero-Dart-files-staged auto-bypass, (3) cache-hash fast-skip, (4) full
      gate run. User picked option (α) over option (β) "drop optimization
      entirely".
- [x] The output is honest about what remains uncertain: cache writes happen
      only on GREEN (not on RED). The cache file's lifetime is bounded only
      by the next GREEN write or by manual cleanup — there is no automatic
      eviction. Concurrent sessions sharing the worktree can race on the file
      but only in the safe direction (PRE/POST tripwire rejects writes from
      a concurrent-edit interval).

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |
