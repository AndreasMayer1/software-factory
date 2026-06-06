---
name: claude-create-skill
description: Create a new project skill with correct naming and structure. THIS SKILL MUST BE USED TO CREATE NEW SKILLS, no creation without it is allowed.
tools: Read, Write, Bash, Glob
model: inherit
---

You create a new skill file in `.claude/skills/{name}/SKILL.md`.

## Naming Convention

Format: `{prefix}-{verb}[-{qualifier}]`

| Prefix | Domain | Notes |
|--------|--------|-------|
| `code-` | Flutter/Dart code | Qualifier only — no verb needed (prefix is the action) |
| `requ-` | Requirements | Verbs: explore, derive, apply, merge |
| `ux-` | User needs | Verbs: create, update |
| `task-` | Task lifecycle | Verbs: create, complete, rollover, repair |
| `doc-` | Design specification | Verb: update |
| `claude-` | Factory infrastructure | Verbs: log, save, route, optimize, create |

The `description:` field appears in skill pickers — keep it under 10 words, imperative, verb-first.

## Token Efficiency Rules (write only what the AI would otherwise get wrong)

**Include:**
- Project-specific paths, folder structures, naming conventions
- Decision trees unique to this project
- Step sequences with project-specific ordering or constraints
- Non-obvious rules the AI would not infer from general knowledge

**Never include:**
- How Claude tools work (AI already knows)
- Content already in CLAUDE.md (loaded in every session)
- Prose where a numbered step or table suffices
- Examples when the pattern is already clear from the rule

**Target body length: ≤ 60 lines.** If it grows beyond that, cut prose — never cut decisions.

## Frontmatter Template

```yaml
---
name: prefix-verb-qualifier
description: Imperative phrase, < 10 words
tools: [only tools this skill actually calls]
model: inherit
---
```

`tools: "*"` only for skills that orchestrate other agents. For everything else, list specifically.

## Body Structure

1. **One-line role statement** — "You are a..." or "You [action]..."
2. **Steps** — numbered, imperative, concrete (the core of the skill)
3. **Optional:** decision table (when AI must choose a path), output definition, "when to use" (only if the trigger is non-obvious)

## Phase Split Decision

When a new skill has ≥ 2 proposed phases, score each candidate against the rubric before writing them. **Split into a sub-skill if ≥ 2 signals are YES**; otherwise use an agent invoked by the parent.

| # | Signal | YES if… |
|---|--------|---------|
| S1 | Independently invocable? | Callable without manufacturing parent-held context |
| S2 | Coordinates ≥ 2 agents? | Real fan-out — one agent + wait is a wrapper, not orchestration |
| S3 | Natural human-review point? | Developer pauses/approves at this boundary |
| S4 | File-based artifact crosses boundary? | Producer writes, consumer reads — file is the contract |

**SCRIBBLE-SPLIT example** (TASK-PROC-044-02 Round 1 §3.2):

| Candidate | S1 | S2 | S3 | S4 | Score | Verdict |
|---|:---:|:---:|:---:|:---:|:---:|---|
| ui-scribble-generate | NO | NO | NO | YES | **1/4** | Agent (collapsed into parent) |
| ui-scribble-auto-review | NO | YES | YES | YES | **3/4** | Sub-skill |
| ui-scribble-feedback-classify | NO | YES | YES | YES | **3/4** | Sub-skill |
| ui-scribble-approve-handoff | NO | NO | YES | YES | **2/4** | Sub-skill (handoff IS the contract) |

Record each phase's score and verdict in the creation protocol.

## Creation Steps

1. Agree name with user — confirm prefix, verb, qualifier
2. Check for conflicts: `ls .claude/skills/`
3. Create folder: `mkdir .claude/skills/{name}/`
4. Write `SKILL.md` with frontmatter + body (follow structure above)
   **CodeGraph note**: If the skill reads or understands code, read REQ-PROC-038 to learn where and how to add the CodeGraph step.
4b. **Contract** (§ Artifact-Establishment Gate): identify the token names this skill will emit in `produces:` and `derived_from:` (short names that identify artifact types — these become the `path:` values in the contract, not raw file paths). Run the gate on each token not yet in `.factory/registry/artifacts.yaml`. Write `.claude/skills/{name}/contract.yaml` only after all tokens are registered. If the skill has developer-decision checkpoints, draft each `user_input_gates:` entry and validate it against `.claude/schemas/user_input_gate.yaml` (required fields: `phase`, `description`, `decision_kind`, `required`) before writing.
5. Add entry to `.claude/skills/INDEX.md` in the correct `{prefix}-*` section
6. **Sync `factory_flows.md`**: Read `.claude/factory_flows.md`.
   Does the new skill process a type of user information not yet shown in the diagram?
   - The `I_SKL → SELF` path already covers "new skill/workflow" — no change needed for most skills
   - Only update if the skill introduces an entirely new INPUT TYPE or a new ARTIFACT CONNECTION
     that doesn't map to any existing node or edge in the diagram
7. Tell user: test by invoking `/{name}`
8. **New task type?** If this skill produces a new task type (new frontmatter field, new `type:` value, or new folder pattern that ordering should treat differently), invoke `claude-modify-ordering-rules` to register it in the ordering rules.

## Artifact-Establishment Gate

Before writing any token into a `contract.yaml` (a `produces:`/`derived_from:` `path:` value is a registry token name such as `skill` or `goal`, not a raw file path):

1. Read `.factory/registry/artifacts.yaml` — collect known token names (top-level YAML keys).
2. For each proposed token not in the known set:
   - **Interactive**: propose an entry (token name, path glob, one-line definition); developer ratifies / renames to existing / rejects; append to `artifacts.yaml` only on ratification; refuse duplicate or alias.
   - **Automated** (`$CLAUDE_AUTOMATED_MODE=1`): write `automation/pending_feedback/<TASK_ID>/question.md` (include token name, suggested path glob, definition); copy `automation/pending_feedback/TEMPLATE_answer.md`; stop — never auto-append.
3. Proceed only when every proposed token exists in the registry.

**`user_input_gates:` entries** (if the skill has developer-decision checkpoints): validate each entry against `.claude/schemas/user_input_gate.yaml` before writing to the contract. Required fields: `phase` (string), `description` (string), `decision_kind` (one of: `approval`, `revision`, `selection`, `path-selection`, `free-text`), `required` (one of: `always`, `conditional`). A malformed entry will be rejected by `check_skill_contracts.py`.
