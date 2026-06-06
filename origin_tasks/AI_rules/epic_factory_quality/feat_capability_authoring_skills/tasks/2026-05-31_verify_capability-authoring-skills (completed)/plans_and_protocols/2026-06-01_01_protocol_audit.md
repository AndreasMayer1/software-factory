---
skills_used:
  - claude-automated-mode
  - claude-route
  - requ-verify-flow-coverage   # routed here by verification_task flag; flow-coverage machinery N/A — audited directly
  - task-create                 # to file the gap fix-task
  - task-complete
  - claude-commit
---

# Protocol: Audit capability-authoring skills + six agents against REQ-PROC-044-01

Task: TASK-PROC-044-01-03 · Session: fb24c177 · 2026-06-01 · Mode: automated · model: opus

## Routing note

`claude-route` step 3b routes any `verification_task: true` goal to
`requ-verify-flow-coverage`. That skill's machinery (flow → requirement coverage
matrix) does not apply here: this is an **AC-audit of shipped skills/agents**, and
the goal.md Scope is a complete self-contained audit procedure. Audited directly as
orchestrator per that procedure; evidence below.

## Method

Audited the **shipped artifacts** (not the impl tasks' claims), per goal objective:
- skills: `.claude/skills/claude-create-agent/{SKILL.md,contract.yaml}`,
  `.claude/skills/claude-modify-agent/{SKILL.md,contract.yaml}`
- agents (six): architecture-advisor, implementation-engineer, opus-advisor,
  quality-checker, setup-optimizer, test-engineer (`.md` + `.contract.yaml` each)
- registry: `.factory/registry/artifacts.yaml`
- index: `.claude/skills/INDEX.md`
- live exercise: authored throwaway `plan-reviewer` agent + contract through the
  `claude-create-agent` gates, verified, then deleted (clean).

## Per-AC findings

### AC-01 (governed authoring) — PASS
`claude-create-agent` encodes every required gate:
- §1 when-to-create gate (4 disqualifying questions) + agent-vs-session suitability
  check (TASK-PROC-032-10 file 13 §5), cross-linked to the split rubric (not restated).
- §2 naming: step 1 format check; step 2 role validation against closed set
  {writer, transformer, reviewer, classifier} with **zero/multi-role → stop-and-ask**;
  step 3 expertise validation against the artifact registry + Artifact-Establishment
  Gate; step 4 collision check (built-ins / `han-*` / existing agents) as a sub-rule
  after 1–3.
- §3 `allowed_tools` intent-class table; bare `*` only with a recorded justification;
  "never grant Write/Bash/Edit to a reviewer".
`claude-modify-agent` re-asserts §2–§4 on every edit (incl. full step 1–4 rename path).

**Live demonstration** (throwaway `plan-reviewer`, then deleted):
- Collision check: proposed names `general-purpose`/`Explore`/`Plan` rejected as
  built-ins; `test-engineer` rejected as existing project agent.
- Expertise `plan` is REGISTERED → no establishment-gate escalation; role `reviewer`
  in the closed set.
- Tool class = read-only reviewer → `Read, Grep, Glob` (no Write/Bash/Edit).
- Role identity 13 tokens (≤50); five sections present and ordered; contract.yaml
  valid (`contract_version: 1`, registered tokens `plan`,`goal`).

### AC-02 (required sections) — **GAP (confirmed)**
- Role identity ≤50 tokens: PASS for all six (6–19 words each).
- Sections: each agent has literal `## Domain Vocabulary` + `## Anti-Patterns` only.
  **None** carries literal `## Protocols`, `## Output`, `## Rules`. Procedural content
  lives under `**When spawned**` / `## Phase N` / `**Output**` (bold) instead.
- The port task (TASK-PROC-044-01-02) goal Out-of-Scope said: add `## Protocols`/
  `## Output`/`## Rules` **"only ... if claude-modify-agent's structural check finds
  them missing."** They *were* missing as literal headings; the session judged the
  content "already encoded under existing headings" and skipped them (scope decision
  recorded in its protocol). Against the **literal AC-02** this is a gap.
- Contrast: the freshly-authored throwaway carried all five sections — the pair
  produces the full structure on create, but the modify backfill stopped at two.
→ Fix-task filed (normalize the six agents to the five-section structure, preserving
  content; add `## Rules` where genuinely absent).

### AC-03 (Domain-Vocabulary aid) — **PARTIAL / GAP**
- Shipped vocab quality: PASS. 15–17 terms each (within 10–25), genuinely
  expert-tier and domain-distinct (e.g. afferent/efferent coupling Ca/Ce,
  anti-corruption layer, MECE decomposition, abductive inference, suppression
  hygiene, mutation score, Goodhart's law, test-double taxonomy). Format = single
  comma-separated plain-text line, no bullets/bold — matches the
  han-adversarial-validator reference model. No shallow/common-web padding.
- Aid spec completeness: GAP. `claude-create-agent §5` codifies count + 15-year
  practitioner test + shallow-rejection + lookup delegation, but **omits** the two
  remaining AC-03 clauses: the **format directive** (single comma-separated
  plain-text line; no bullets/bold/inline explanations) and the **han-adversarial-
  validator reference-model** pointer. A future invocation could emit bulleted vocab
  and still satisfy §5 as written.
→ Fix-task filed (add the format directive + reference-model cite to §5).

### AC-04 (contract integration) — PASS
- Both new skills carry valid `contract.yaml` (`contract_version: 1`, purpose,
  derived_from, produces, quality_criteria).
- All six modified agents carry `<name>.contract.yaml` sidecars (valid YAML).
- Split rubric referenced, not re-derived: both SKILLs and `claude-modify-agent §4`
  point to `claude-create-skill §"Phase Split Decision"`.

### AC-05 (single ownership) — **GAP (minor)**
- `.claude/skills/INDEX.md` §"Capability-Authoring Meta-Skills (governed set —
  REQ-PROC-044-01 AC-05)" lists all six required skills, each cross-linking a
  governing AC (no restatement). Core requirement met.
- Defect: the table includes a **7th** row, `claude-write-hook`, while the prose says
  "These six"; and that row's governing-AC cell is **not** an AC cross-link
  ("hooks are factory infrastructure; … `scripts/tests/test_hooks.py`"), violating
  AC-05's "each ownership entry cross-links the existing ACs."
→ Fix-task filed (reconcile count/prose; give write-hook a governing reference or
  scope it out of the AC-05 set).

## Outcome
3 gaps (1 substantive AC-02, 2 minor AC-03/AC-05) → bundled into one fix-task with
one AC per gap. AC-01 and AC-04 pass. No AC ticked optimistically.
