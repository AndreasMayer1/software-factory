# User Initial Input — 2026-05-16

Verbatim seed material from the conversation that led to this task. Not a spec.
Read it as a seed bed, not a spec.

---

**Trigger turn — observation of the failure pattern:**

> the tasks should auto split if they are too large and they should use agents.
> check if those 2 mechanisms failed and need improvement

**Task creation request (after diagnostic discussion):**

> write a new task to fix the task size / task split problem. the task must also
> update/write a requirement: I want the tasks to be executable and not hit the
> prompt size limit.

**Critical nuance (added mid-creation):**

> for the new task it is important that it performs a good exploration and
> thinks through all cases. we can't just blindly use agents everywhere or
> split up any task. sometimes it is required to have a lot of context
> knowledge to produce good results. sometimes having agents re reading all
> files again and again is just a waste of tokens.

---

## Triggering event (factual context)

Autorun on 2026-05-16 produced two session failures with this Claude API error:

```
API Error: Extra usage is required for 1M context · enable extra usage at
claude.ai/settings/usage, or use --model to switch to standard context
```

The user has no "Extra usage" entitlement on any account. Sonnet auto-upgrades
to its 1M-context variant when a session approaches the 200K-token ceiling;
without the entitlement, Anthropic refuses the upgrade and the session exits 1.

Affected tasks:

- **TASK-PROC-049-08** — multi-part `impl`: author canon README + update CLAUDE.md
  + invoke `requ-explore` once per affected requirement (4–5 named). Fresh launch
  failed at 7 min wall-clock with a ~588 KB JSONL.
- **TASK-PROC-052-04** — `analyze`: audit all of `lib/` for cryptographic
  key-material storage. Fresh launch failed at 4 min wall-clock with a ~287 KB
  JSONL.

Both tasks were sized `effort: S` and had `opus_recommended: false`.

## Diagnostic findings already established in conversation

Two mechanisms were intended to prevent this; both were partially wired:

1. **Auto-split at task creation**
   - `task-create-code` has Small/Medium/Large rules with "Split NOW" at Large.
     Applies to code tasks only.
   - `task-create` (general) sizes effort XS–XL but has no rule that reads scope
     text and flags "lists N independent deliverables → split".
   - Both failing tasks listed N independent deliverables and were sized `S`.

2. **Agent fan-out via `scripts/util/should_use_agents.py`**
   - CLAUDE.md §7 mandates: "Skills reading requirement files must call
     `should_use_agents.py` before deciding to read inline. Hard threshold:
     30 KB total OR 5 files."
   - Grep across `.claude/skills/`: only `release-begin-impl` actually calls it.
   - `requ-explore` and `task-resolve` have their own heuristics; neither
     defers to the structural check.

The orchestrator side has been patched separately (recognises the new error
string and auto-promotes the task to Opus on the next iteration). That handles
the *consequence*. This task addresses the *cause*: tasks must be sized so they
*can* execute in a 200K-token sonnet session without forcing reflex splits or
wasteful agent fan-out.

## What the user explicitly does NOT want

- A simple "if scope has ≥N deliverables, split" rule that fragments tasks
  whose pieces share an unwritten mental model.
- A simple "if files > N, fan out" rule that makes agents re-read material
  the main session would have read anyway, doubling the token bill.

The exploration must produce a framework that handles both failure modes
(oversize → error; over-fragmented → quality loss + token waste).
