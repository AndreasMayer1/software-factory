---
skills_used:
  - claude-route
  - requ-explore
  - task-complete
  - claude-commit
---

# Synthesis — Design of the `task-start` Skill (Wrapper over `claude-route`)

Task: TASK-PROC-069-01 (explore/design). Date: 2026-06-05. Parent: REQ-PROC-069 (placeholder — no `requirements.md` yet).
Origin: TASK-PROC-032-29 Round-1 synthesis §8 (last row) + §9 D-3 → "task-start wraps claude-route; both, separated"
→ user decision: own task. This is that task.

Inputs read & grounded against (file → what was extracted):
- `claude-route/SKILL.md` (full): Modes A/B/C, Mode-A steps 1–6 (frontmatter validate, in_progress mark, session
  metadata, INDEX read, type→skill match, opus-check, dispatch).
- `CLAUDE.md` §4 "Default Workflow" (the single normative "invoke claude-route" instruction) + §"Automated Mode".
- `scripts/tasks/create_orchestration_task.py` L260–300: the chain materialises an *orchestration goal.md* whose
  ACs name **task-create / task-create-code / ui-create-scribble** (creation skills) in zero-param mode — it does
  **not** call claude-route. Execution of created tasks happens later via "Do next task".
- Heads of `code-simple`, `code-complex`, `code-test`, `task-resolve`: the duplicated REQ-PROC-044 entry pre-check;
  per-skill goal.md + doc/ reads; the Presentation-only Sketch Gate.
- `claude-automated-mode/SKILL.md` L148–157: pending_feedback has a MANDATORY pre-condition that the entry skill
  already marked `in_progress` and wrote `session_id`.
- Migration-surface grep (below, §6).

This record is self-contained; a follow-on impl task can build `task-start` from it without replaying the session.
Developer-owned choices are marked **[DEV-DECISION]**.

---

## 0. The reframing that changes the design

The seed framing ("task-start adds context loading + pre-flight checks on top of claude-route") implies task-start
is a *fat* layer. Grounding says the opposite about context loading and something sharper about pre-flight:

**Finding A — claude-route is already 80% a pre-flight skill.** Mode-A steps 1, 2, 2a, 2b (read goal.md, validate /
complete frontmatter, mark `in_progress` + `started`, write `session_id`/`session_account` in automated mode) are
**not routing** — they are pre-flight. Only steps 3–6 (read INDEX, match type→skill, opus-check, invoke) are
routing. So "wrap claude-route with pre-flight" partly means **relocating** work that already lives in claude-route,
not inventing new work.

**Finding B — the genuinely new, genuinely missing pre-flight is pre-condition *gating*.** Three guards exist
nowhere on the execution path today:
1. **Schema validity of goal.md** — enforced, but only inside 9 execution skills as a *duplicated* copy-paste
   (REQ-PROC-044 entry pre-check); `task-resolve` and `requ-explore` have **no** such guard. Uneven.
2. **`awaiting:` empty** — `is_awaiting_answer.py` exists but is only consulted during *task selection*
   (claude-route Mode C), never as a gate when a task is named directly ("Do TASK-XXX").
3. **`after:` dependencies completed** — `next_tasks.py` filters blocked tasks out of *selection*, but a direct
   "Do TASK-XXX" bypasses that filter entirely.

**Finding C — context loading is a trap.** Making task-start *read and pass down* goal.md/protocol.md content
fights two existing invariants: (a) CLAUDE.md file-based-memory rule mandates that *every agent reads goal.md +
latest protocol.md itself*; (b) context is per-session/per-agent — task-start cannot pre-warm a downstream agent's
context. So task-start must **verify readability + parse frontmatter for gating only**, and leave the substantive
read to the execution skill. (Answers Seed 2 decisively: "verify, don't pass down.")

**Net:** `task-start` is a **thin gate-and-relocate layer**, not a fat new stage. Its real value is (1) one
canonical pre-condition gate replacing 9 scattered copies + 2 missing guards, and (2) a clean home for the
already-existing pre-flight steps so claude-route can shrink to a pure router.

---

## 1. task-start phases (the design)

`task-start <ref>` where `<ref> ∈ {goal.md path | TASK-ID | "next task"[+--type impl] | free-text description}`.

| Phase | Name | Responsibility | On failure |
|-------|------|----------------|------------|
| **P0** | Resolve reference | Turn `<ref>` into a concrete `goal.md` path. TASK-ID → `grep "task_id:"`; "next task" → `next_tasks.py` selection loop (today's claude-route Mode C); description → interactive disambiguation (today's Mode B); path → use as-is. | No match → tell user / (automated) skip to next candidate. |
| **P1** | Load & validate | Confirm goal.md exists; run `validate_against_schema.py <goal> goal_metadata.yaml` (the REQ-PROC-044 guard, **once, here**); parse frontmatter (status, after, awaiting, opus_recommended). | Missing/off-schema → HALT with the exact REQ-PROC-044 error; do not route. |
| **P2** | Pre-condition gates | (a) `status` not `completed` (re-entry guard; `pending`/`in_progress` both proceed — in_progress = resume). (b) `awaiting:` empty (else task is parked on a developer answer). (c) `after:` deps all `completed`. See §3 for each gate's failure policy. | Per §3 — HALT, warn+confirm, or route to pending_feedback. |
| **P3** | Mark started | If `status: pending`/absent → set `in_progress` + `started: <today>` (today's Mode-A step 2a). Automated mode → also write `session_id`/`session_account` (today's Mode-A step 2b). **This ordering is load-bearing** for pending_feedback (claude-automated-mode L148–157). | — |
| **P4** | Delegate to claude-route | Call `claude-route` with the now-validated, in_progress goal.md **path**. claude-route does type→skill match + opus-check + dispatch only. | claude-route's own output. |

P0–P3 are the "pre-flight wrapper"; P4 is the hand-off. The opus-check stays in claude-route (it is routing-adjacent
— it decides whether dispatch may proceed) **or** moves to P2; either is defensible — see [DEV-DECISION D-B].

---

## 2. Exact boundary with claude-route

```
                 ┌─────────────────────────── task-start ───────────────────────────┐
"Do X"  ──ref──▶ │ P0 resolve → P1 validate → P2 gate → P3 mark in_progress(+session)│ ──path──▶ claude-route
                 └──────────────────────────────────────────────────────────────────┘            │ match type→skill
                                                                                                  │ opus-check
                                                                                                  ▼ invoke execution skill
```

- **task-start input:** a task reference (any of 4 forms). **task-start output:** either a HALT (with reason), or an
  invocation of `claude-route <validated-goal.md-path>`.
- **claude-route input contract (narrowed):** a goal.md that is guaranteed to exist, be schema-valid, be
  `in_progress`, and have passed pre-condition gates. claude-route therefore **drops Mode-A steps 1, 2, 2a, 2b**
  (now owned by task-start), **drops Modes B and C** (selection/disambiguation now P0 in task-start), and keeps a
  single mode: *given a ready goal.md path, match type→skill, opus-check, invoke.* claude-route shrinks to ~Mode-A
  steps 3–6.
- **Who calls whom:** task-start → claude-route → execution skill. claude-route is never the user-facing entry
  anymore; it is an internal routing component. (Direct `claude-route <path>` still works for advanced/manual use,
  but the documented path is task-start.)

This is the "both, separated" the Round-2 synthesis resolved: **both skills exist; task-start = pre-flight + entry,
claude-route = router.** The seam is *pre-flight ↔ routing*, and it is drawn so that no responsibility is
duplicated across the two.

---

## 3. Pre-conditions & failure behaviour

| Gate | Source of truth | Interactive failure | Automated failure | Recommendation |
|------|-----------------|---------------------|-------------------|----------------|
| goal.md schema-valid (P1) | `validate_against_schema.py` | HALT, show error, stop | HALT, stop session (orchestrator logs) | **Hard-block.** Non-negotiable; it is REQ-PROC-044 already. |
| `status != completed` (P2a) | frontmatter | Warn "already completed — re-run anyway?" → confirm | Skip to next candidate | **Warn+confirm** interactive / **skip** automated. |
| `awaiting:` empty (P2b) | `is_awaiting_answer.py` | HALT "task is parked on developer answer `<note>`" | Skip to next candidate (it is awaiting input, not runnable) | **Hard-block / skip.** Generalises Mode-C's per-candidate check to a universal gate. |
| `after:` deps completed (P2c) | frontmatter `after:` + each dep's status | Warn "depends on unfinished `<TASK>` — proceed anyway?" → confirm | Skip (ordering already keeps it out of `next_tasks.py`; a direct pick is an override) | **Warn+confirm** interactive / **skip** automated — **[DEV-DECISION D-A]** (hard-block vs warn). |

**Explicitly OUT of task-start (wrong phase):**
- **`.git/index.lock` stale check** — a *commit-time* concern owned by task-complete + the CLAUDE.md retry
  protocol. A task starts long before it commits; gating start on a commit-time lock is mis-placed. Leave it where
  it is.
- **Reading protocol.md / passing context down** — Finding C; execution skills + their agents own that read.

---

## 4. Automated mode

task-start is the single execution entry in **both** modes — automated sessions reach a task the same way
interactive ones do: the autorun loop launches a session that runs "Do next task" (CLAUDE.md §4), which is
task-start. The dual-signal detection is the existing one (`CLAUDE_AUTOMATED_MODE=1` **and** `automation/.automated_mode`).

Mode-conditional behaviour, all already present in claude-route today and **relocated** to task-start:
- **P3 session metadata** (`session_id`, `session_account`) written only in automated mode (today Mode-A step 2b).
- **opus-check skipped** in automated mode (orchestrator already launched with the right `--model`).
- **Gate failures** route to *skip-next-candidate* / pending_feedback rather than interactive prompts.

**Load-bearing constraint (must not regress):** `claude-automated-mode` L148–157 requires that, before any
`pending_feedback/<TASK>/question.md` is written, the entry skill has already marked the task `in_progress` and
written `session_id`. Because task-start does P3 *before* P4 (and before any downstream skill could escalate),
this contract is preserved — but the follow-on impl task MUST update `claude-automated-mode`'s wording from
"`claude-route` marks the task in_progress and writes session_id" to "`task-start` …". (Migration item, §6.)

**Not replaced:** the orchestration *creation* chain (`create_orchestration_task.py`) still names
task-create / task-create-code to **create** task workspaces. task-start governs **starting/executing** an
already-created task, not creating one. Keep these two concerns distinct — task-start is not inserted into the
creation chain.

---

## 5. Does claude-route need changes? Yes — it shrinks.

claude-route is **not** left untouched (a purely additive task-start would duplicate frontmatter/in_progress work
on every call). Under the recommended seam:
- **Removed from claude-route:** Mode-A steps 1, 2, 2a, 2b; Mode B; Mode C. (All become task-start P0–P3.)
- **Kept in claude-route:** read INDEX, match `type`+content→skill, verification-task shortcut, opus-check,
  one-line "→ Using `skill`" + invoke.
- claude-route's `contract.yaml` required-input becomes "a validated, in_progress goal.md path" (today it accepts
  raw refs and does the validation itself).

**[DEV-DECISION D-B] — seam depth.** Two viable shapes:
- **B1 Clean seam (recommended):** relocate as above. Cleaner long-term, single owner per responsibility, but edits
  claude-route + its contract + every caller (§6).
- **B2 Thin additive:** task-start does only the *new* gates (P1 validate + P2 gates), then calls claude-route
  **unchanged** (claude-route keeps doing frontmatter/in_progress/selection). Lowest migration risk; cost = both
  skills touch frontmatter (in_progress marking is idempotent, so harmless), and selection/disambiguation stay in
  claude-route. Recommend B1 but B2 is a safe incremental first step that can converge to B1 later.

---

## 6. CLAUDE.md change + full migration surface

**CLAUDE.md §4 "Default Workflow" new wording (proposed):**
> When user says "Do [path/to/goal.md]", "Do [task id]", or "Do next task" without specifying a skill: invoke
> **`task-start`** with the path, task ID, or instruction. `task-start` resolves the reference, runs pre-flight
> pre-condition checks (schema-valid goal.md, not already completed, not awaiting a developer answer, dependencies
> satisfied), marks the task `in_progress`, then delegates type-detection and skill dispatch to `claude-route`.

(Also update the §"Session-specific guidance" and §4 "Session model" lines that name claude-route, and the
"Do next task" routing note.)

**Migration surface — every hard reference to `claude-route` (grep-grounded 2026-06-05):**

| File | Reference kind | Action under B1 |
|------|----------------|-----------------|
| `CLAUDE.md` | §4 normative "invoke claude-route" | Re-point to task-start (above). |
| `.claude/skills/INDEX.md` | catalogue entry | Add task-start; re-describe claude-route as internal router. |
| `.claude/factory_flows.md` | flow doc | Update entry-point flow to task-start → claude-route. |
| `.claude/skills/claude-route/SKILL.md` + `contract.yaml` | the skill itself | Shrink per §5; narrow contract input. |
| `.claude/skills/claude-automated-mode/SKILL.md` (L148–157) | "claude-route marks in_progress / writes session_id" | Re-point to task-start (load-bearing, §4). |
| `.claude/skills/task-resolve/SKILL.md` | mentions route fallback | Update reference. |
| `.claude/skills/task-derive-from-requ/SKILL.md`, `task-create-code/SKILL.md`, `task-complete/SKILL.md`, `verify-quality/SKILL.md` | incidental mentions | Update text where they name the entry point. |
| `.claude/schemas/goal_metadata.yaml`, `pending_question.yaml` | doc/comment refs | Update comments. |
| `scripts/automation/orchestrate.py`, `terminate_session.sh`, `optimize/create_optimize_cycle_task.py`, `tests/test_next_tasks.py` | automation drives "Do next task" / assumes claude-route side-effects | Audit: anything depending on claude-route marking in_progress now depends on task-start. |

**The 9 duplicated REQ-PROC-044 entry pre-checks** (code-simple/complex/test/bugfix, task-create-code,
task-derive-from-requ, ui-verify-flutter, ui-improve-flutter, task-complete): once task-start owns the canonical
gate, these become redundant **on the task-start path**. **[DEV-DECISION D-C]:** remove them (DRY, single gate) vs
keep them as cheap defense-in-depth (skills can still be invoked directly, e.g. "Use code-simple skill for …",
bypassing task-start). **Recommend keep** — the guard is ~3 lines, idempotent, and direct-invocation is a
supported path; task-start becomes the *canonical* gate without making the others unsafe to call alone.

---

## 7. Relationship to REQ-PROC-069 (this task's writes_requirements flag)

REQ-PROC-069 has **no `requirements.md`** — only this task folder under `workflows/task_execution_entry/`. The
goal's Output + ACs describe a *design synthesis* (the TASK-PROC-032-29 pattern), not direct requirement authoring.
So authoring REQ-PROC-069 is itself a **user-gated next step**, not a forced pre-write. The natural REQ-PROC-069
would be a *living/process* requirement (`status: active`) governing "the canonical task-execution entry point",
with ACs phrased as end-states, e.g.:
- "A single skill is the documented entry point for executing any created task; it is reached identically in
  interactive and automated sessions."
- "Before any execution skill runs, the task's goal.md is schema-valid, not completed, not awaiting a developer
  answer, and its dependencies are satisfied."
- "Type-detection and skill dispatch are owned by exactly one routing component, distinct from the pre-flight
  entry point."
- "No execution skill duplicates the canonical pre-condition gate as its sole enforcement." (tune per D-C)

This is a recommendation for the user to confirm (§9), not yet written.

---

## 8. Decisions that need the developer **[DEV-DECISION]**

> **Resolved by the developer 2026-06-05:** **D-B → B1 clean seam** (relocate Mode-A pre-steps + Modes B/C into
> task-start; shrink claude-route to a pure router). **D-C → Keep** the 9 duplicated entry pre-checks as
> defense-in-depth. **D-E → Author REQ-PROC-069 now** (done this session:
> `workflows/task_execution_entry/requirements.md`, `status: active`). D-A (after-deps = warn+confirm/skip) and
> D-D (opus-check stays in claude-route) stand on their recommendations; the impl task may revisit. These
> resolutions are encoded in REQ-PROC-069's Acceptance Criteria + Developer Guidelines.


- **D-A — `after:`-deps failure policy** (§3 P2c): hard-block vs warn+confirm (interactive). *Recommend
  warn+confirm* — a direct "Do TASK-X" on a blocked task is sometimes a deliberate override; automated path already
  skips via `next_tasks.py`.
- **D-B — seam depth** (§5): B1 clean seam (relocate Mode-A pre-steps + Modes B/C into task-start, shrink
  claude-route) vs B2 thin additive (claude-route unchanged). *Recommend B1*, optionally reached via B2 first.
- **D-C — duplicated entry pre-checks** (§6): remove the 9 copies vs keep as defense-in-depth. *Recommend keep.*
- **D-D — opus-check home** (§1 P4): leave in claude-route vs move to task-start P2. *Recommend leave in
  claude-route* (it gates dispatch, which is routing's job) — minor.
- **D-E — author REQ-PROC-069 now** (§7): write the governing requirement in this task vs spin a follow-on
  `requ-explore`. This is the AC-6 "next step" gate — the user states it.

---

## 9. What remains uncertain (honest)

- **Automated execution path beyond "Do next task"** (§4): I grounded that the *creation* chain names
  task-create(-code) and that autorun launches "Do next task" sessions, but I did not exhaustively trace every
  orchestrate.py branch that may launch an execution session by another route (resume paths, L1610/L2121). If any
  automated path reaches an execution skill *without* going through "Do next task", task-start would not be on it
  and that path would skip the new gates. The migration audit (§6, orchestrate.py row) must confirm there is
  exactly one execution entry.
- **B2→B1 idempotency** (§5): "in_progress marking is idempotent, so double-marking is harmless" is true for the
  status flip, but if both task-start and an unshrunk claude-route write `started:`/`session_id`, the *second*
  write could overwrite a value — needs a one-line check (write-if-absent) if B2 is chosen.
- **Direct skill invocation prevalence** (§6, D-C): the keep-vs-remove call hinges on how often skills are invoked
  directly (bypassing task-start). I did not measure this; if direct invocation is rare/deprecated, removing the
  9 copies becomes attractive. Empirical, unmeasured.
- **Whether claude-route Mode B (free-text disambiguation) belongs in task-start at all** (§1 P0): folding
  interactive disambiguation into a "pre-flight" skill slightly widens task-start's remit beyond pure pre-flight.
  Defensible (it is still "resolve the reference") but a purist might keep Mode B in claude-route. Minor.

---

## 10. Acceptance-criteria self-check (this task's goal.md)
- [x] At least one synthesis round produced — this document.
- [x] Defines the problem space in terms not fully known at creation — the **gate-and-relocate** reframing (§0):
  claude-route is already 80% pre-flight; the only *new* work is pre-condition *gating* (schema/awaiting/after),
  and context-loading is a trap (Finding C). The seam is *pre-flight ↔ routing* (§2), not "thin vs fat wrapper".
- [x] Decisions requiring user input identified and framed to decide — §8 D-A…D-E.
- [x] Honest about what remains uncertain — §9.
- [x] User has approved the final synthesis and stated what to do next — approved 2026-06-05; next step = author
  REQ-PROC-069 now (§8 resolution).
- [x] The action stated by the user as the next step was performed — REQ-PROC-069 authored at
  `workflows/task_execution_entry/requirements.md` (`status: active`, AC-01…AC-06).
