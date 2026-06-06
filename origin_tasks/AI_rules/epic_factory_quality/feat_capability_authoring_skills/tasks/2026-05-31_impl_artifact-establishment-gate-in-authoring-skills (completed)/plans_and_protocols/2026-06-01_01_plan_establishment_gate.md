# Plan: Artifact-Establishment Gate in Authoring Skills

## Context

AC-06 of REQ-PROC-044-01 requires that when an authoring skill emits a `produces:`/
`derived_from:` token, or composes an agent-name expertise segment, absent from
`.factory/registry/artifacts.yaml`, it eagerly proposes a registry entry the developer
ratifies before authoring proceeds.

## What a "token" means in contracts

The lint script (`scripts/quality/check_artifact_token_resolve.py`) validates that:
- Skill contracts: each `path:` value in `produces:` / `derived_from:` entries is a top-level key in `artifacts.yaml` (e.g. `skill`, `goal`, `plan`)
- Agent contracts: each string value in `produces:` / `derived_from:` / `consumes:` is a top-level key
- Agent names: the expertise segment (e.g. `scribble` in `scribble-reviewer`) is a registry key

So contracts should reference TOKEN NAMES (registry keys), not raw file paths.
The baseline (`artifact_token_baseline.txt`) suppresses all legacy raw-path violations.

## Scope of changes

Four SKILL.md files need a new "Artifact-Establishment Gate" section and step:

| Skill | What to add |
|---|---|
| `claude-create-skill` | Step 4b: write contract.yaml; gate section |
| `claude-modify-skill` | Step 4b: update contract if tokens change; gate section |
| `claude-create-agent` | §2 expertise gate + §6 contract gate; gate section |
| `claude-modify-agent` | Step 2 expertise gate (on rename) + step 4 contract gate; gate section |

## Gate procedure (canonical)

1. Read `.factory/registry/artifacts.yaml` — collect known token names (top-level YAML keys).
2. For each proposed token (produces/derived_from path value; agent expertise segment) not in the known set:
   - **Interactive**: propose entry (token name, path glob, one-line definition);
     developer ratifies / renames-to-existing / rejects; append only on ratification; refuse duplicate/alias.
   - **Automated** (`$CLAUDE_AUTOMATED_MODE=1`): write `automation/pending_feedback/<TASK_ID>/question.md`
     with the proposal; copy `TEMPLATE_answer.md`; stop — never auto-append.
3. Proceed only when every proposed token is in the registry.

## Decisions

- Gate is inlined in each skill (not a sub-skill): score 1/4 on split rubric (only S3 is yes).
- Contract format: `path:` values ARE the token names (not raw file paths). This is what the lint validates. New contracts written through the skills should use token names.
- In create-skill: add a step 4b for contract.yaml (currently missing from the SKILL.md).
- INDEX.md / factory_flows.md: no change needed — skill descriptions unchanged, no new artifact connections.
