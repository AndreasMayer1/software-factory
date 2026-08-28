# Protocol 24 — Background run interrupted by session-process teardown; retry foreground

Agent: main session (automated), session ec060365-1ed5-4d49-98ce-cce64740eaf8 (resumed), account web.

## What happened

The protocol-23 background launch (`bw3iu2b6u`) was resumed by the orchestrator with:
"No completion record was found for this background shell command from the previous session. It
may have been stopped (via the UI, Monitor timeout, or agent teardown...) or it may have been
running when the previous Claude Code process exited."

Inspection confirmed **no destructive loss** (unlike the original TASK-PROC-068-11 incident this
task exists to fix upstream): `/tmp/harness_redrive_run.log` stopped right after "Step 3: launching
contained child session" — no JSONL transcript for the isolated workspace exists at all, and the
seeded persona/scenario files in the leftover `/tmp/playground-build-v_hw428u/` all share one mtime
(the seed-copy time) — the contained child never produced any output before being killed. The
driver process itself was dead (not in `ps`), and its `finally: shutil.rmtree` never ran (process
was killed, not a clean Python exit) — cleaned up manually.

## Root-cause correction to protocol 23's reasoning

Protocol 23 reasoned that staying "attentive" (a background Bash call I don't exit while waiting on)
would sidestep the delegated-work incident pattern (parent exits, worker orphaned). That reasoning
assumed my session's own process stays alive continuously between tool calls. It does not, in this
harness: automated-mode sessions get cycled/resumed as new processes between turns (confirmed by
this very interruption), and a `run_in_background` Bash job is tied to the controlling process —
when that process is torn down, the backgrounded child dies with it (no true OS-level detachment
via `setsid`/`nohup`/`disown` was used). So the child died not because I exited deliberately, but
because the harness recycled my process while the background job was still tied to it.

**Correction — run foreground, not background, this time.** Historical precedent (protocol 16) put
the child's real runtime at ~5 min / ~$1.73 / 40 turns, comfortably under the Bash tool's 600s
foreground ceiling... wait, the tool's max is 600000ms = **600 seconds = 10 minutes**, giving ~2x
margin over the historical ~5 min. Running foreground means the whole deploy→seed→child→harvest
sequence completes (or times out) within one single blocking tool call in the *current* turn — no
window in which the child can be orphaned by a session-process cycle between turns. This is simpler
and more robust here than either (a) another background attempt (same teardown risk) or (b) the full
REQ-PROC-041-06 delegated-work descriptor (which, on inspection, doesn't actually fit this task: its
`compute_verdict` DONE-oracle is existence+non-empty of `declared_outputs`, but this task's target
files **already exist and are already non-empty** before any re-derivation runs — it's an
in-place-iteration task, not fresh-artifact creation, so the oracle would report DONE trivially
without the child having done anything).

## Retry

Same driver (`/tmp/harness_redrive_driver.py`), same prompt (`/tmp/harness_redrive_prompt.txt`) —
both idempotent/reusable (a fresh `session_uuid`/isolated dir is minted each run). Re-launched
**foreground** with a timeout just under the tool's 600s ceiling. If it times out or hits a
rate/session limit: per `claude-automated-mode`, no retry-loop — leave task `in_progress`, re-emit
the limit line verbatim (or state the timeout plainly), terminate; let the orchestrator resume.
