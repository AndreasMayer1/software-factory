---
name: claude-modify-agent
description: Modify a .claude/agents/*.md file; keep it governed. MUST be used to modify agents.
tools: Read, Write, Edit, Bash, Glob
model: inherit
---

You modify an existing agent in `.claude/agents/{name}.md` and bring it up to the governed end-state.
Do NOT hand-edit an agent file outside this skill.

## Steps

1. **Identify**: resolve to `.claude/agents/{name}.md` (`ls .claude/agents/` if ambiguous). Read it fully.
2. **Apply the change** with Edit/Write.
3. **Re-assert the governed end-state** — after any edit, the file MUST still satisfy
   `claude-create-agent` §2–§4 (these definitions are canonical there; do not restate them):
   - **§2 naming** — if renamed, apply the full `claude-create-agent` §2 steps 1–4 in order: (1) format check (`{expertise}-{role}`, role is last segment); (2) role validation against `{writer, transformer, reviewer, classifier}` (zero/multi-role → stop and ask); (3) expertise validation against `.factory/registry/artifacts.yaml` (missing → **Artifact-Establishment Gate** § below); (4) collision check (built-ins, `han-*`, existing agents). Rename the contract sidecar only after all steps pass.
   - **§3 `allowed_tools`** — still the narrowest set for the intent class; a bare `*` keeps/gets its recorded justification.
   - **§4 sections** — role identity ≤50 tokens + `## Domain Vocabulary`, `## Anti-Patterns`, `## Protocols`, `## Output`, `## Rules` all present. If a required section is missing, ADD it (use the `claude-create-agent` §5 Domain-Vocabulary aid for `## Domain Vocabulary`).
4. **Maintain the contract** (AC-04): if the change introduces new `produces:`, `derived_from:`, or `consumes:` tokens, run the **Artifact-Establishment Gate** (§ below) before updating `.claude/agents/{name}.contract.yaml`. Reference `claude-create-skill` §"Phase Split Decision" — do not re-derive the split rubric. **Schemas and templates are NOT artifacts — never list them** in `produces:`/`derived_from:`/`consumes:`: a schema (e.g. `.claude/schemas/*.yaml`) or template is the shape/blueprint of an artifact, not an artifact itself, and its relationship is already implied by the produced/consumed artifact token. Drop such entries rather than registering them.
5. **Report**: list every file changed and what changed in each.

## Artifact-Establishment Gate

Before finalizing a new agent expertise segment (step 3 rename) or writing any new token into `contract.yaml` (step 4):

1. Read `.factory/registry/artifacts.yaml` — collect known token names (top-level YAML keys).
2. For each proposed token (expertise segment; or `produces:`/`derived_from:`/`consumes:` string value) not in the known set:
   - First, confirm it is an artifact at all — a schema or template is never an artifact (see step 4) and must be dropped, not registered.
   - **Interactive**: propose an entry (token name, path glob, one-line definition); developer ratifies / renames to existing / rejects; append to `artifacts.yaml` only on ratification; refuse duplicate or alias.
   - **Automated** (`$CLAUDE_AUTOMATED_MODE=1`): write `automation/pending_feedback/<TASK_ID>/question.md` (include token name, suggested path glob, definition); copy `automation/pending_feedback/TEMPLATE_answer.md`; stop — never auto-append.
3. Proceed only when every proposed token exists in the registry.
