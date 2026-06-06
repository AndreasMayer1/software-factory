# Plan: claude-create-agent / claude-modify-agent skill pair (TASK-PROC-044-01-01)

Session: 24743901 (gmail, automated). Approach: **inline** (deliverables are skill files;
shape is clear from the existing `claude-create-skill` / `claude-modify-skill` pair).

## Deliverables

1. `.claude/skills/claude-create-agent/SKILL.md` (+ `contract.yaml`) — created via `claude-create-skill`.
2. `.claude/skills/claude-modify-agent/SKILL.md` (+ `contract.yaml`) — created via `claude-create-skill`.
3. `.claude/skills/INDEX.md` — new entries + AC-05 "governed meta-skill set" subsection.
4. `.claude/factory_flows.md` — assessed; updated only if a new input type/edge is introduced.

## AC → mechanism mapping (what the skill bakes in)

- **AC-01 governed authoring** — `claude-create-agent` enforces, before writing the file:
  1. **collision check** — name vs Claude built-ins (general-purpose, statusline-setup, output-style-setup, Explore, Plan, Task, claude), Han imports (`han-*`, e.g. `han-adversarial-validator`), and existing `.claude/agents/*.md`. Colliding → reject.
  2. **`allowed_tools` intent-class heuristic** — table mapping intent class → narrowest tool set; read-only reviewer = `Read, Grep, Glob` (+`Bash(git *)` if needed); bare `*` only with a recorded justification line (mirrors `tools: "*"` rule in claude-create-skill).
  3. **when-to-create gate** — disqualifying questions (could an existing agent/skill do this? is it just one session step?); create only if it passes.
  4. **agent-vs-session suitability** — per TASK-PROC-032-10 file 13 §5 (own context window, parallelizable, read-heavy fan-out, isolation).
- **AC-02 required sections** — both skills guarantee: role identity ≤50 tokens + `## Domain Vocabulary`, `## Anti-Patterns`, `## Protocols`, `## Output`, `## Rules`.
- **AC-03 Domain-Vocabulary aid** — instruction block: 10–25 expert-tier terms, "15-year practitioner test", strong reject-shallow language, MAY delegate web/research lookup to a spawned general-purpose agent (never inline WebSearch). Home of capability D9.
- **AC-04 contract integration** — both skills emit/maintain their own `.claude/skills/<name>/contract.yaml` (required by `check_skill_contracts.py`); agents authored through the pair emit a sidecar `.claude/agents/<name>.contract.yaml`. The when-to-create gate REFERENCES the split rubric in `claude-create-skill` §"Phase Split Decision" (REQ-PROC-044 AC-03) rather than restating it.
- **AC-05 single ownership** — INDEX.md gains a "Capability-Authoring Meta-Skills (governed set)" subsection listing the six skills, each cross-linking its governing AC (REQ-PROC-044-01 AC-01..05; REQ-PROC-042 ordering rules; REQ-PROC-043 write-script) — cross-link, no restatement.

## Decisions

- Agent contract location: sidecar `.claude/agents/<name>.contract.yaml` (agents are flat `.md`; no per-agent folder). The skill-contract lint only globs `.claude/skills/*/contract.yaml`, so this introduces no lint regression; the convention is documented in the skill so `-02` can apply it.
- Split rubric is canonically in `claude-create-skill`; agent skills reference it (no duplication) — satisfies AC-04 "reference not re-derive".
- Body length: target ≤60 lines per SKILL.md (claude-create-skill rule). Domain-Vocabulary aid + section template are the load-bearing content.

## Out of scope (per goal)
- Applying sections/vocabulary to the six existing agents → TASK-PROC-044-01-02.
- Retro-justifying `ui-scribble-*` agents → deferred (YAGNI).

## Verify
- `python3 scripts/quality/check_skill_contracts.py` PASS (both new contracts valid).
- Both SKILL.md present, frontmatter valid, INDEX.md + factory_flows.md synced.
