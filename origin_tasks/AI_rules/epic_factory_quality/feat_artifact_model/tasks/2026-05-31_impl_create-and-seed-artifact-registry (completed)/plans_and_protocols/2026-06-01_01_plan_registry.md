# Plan: Create and Seed Artifact Registry

Date: 2026-06-01
Task: TASK-PROC-044-02-01
Session: 40e18891-b72a-4500-8d18-bf63a9cd3fd4

## Approach

Agent-assisted investigation (69 contract files + factory map) → inline draft creation →
developer ratification via pending_feedback.

## Investigation findings

Sources scanned:
- `.claude/skills/*/contract.yaml` (59 files)
- `.claude/agents/*.contract.yaml` (9 files)
- `scripts/factory/render_factory_map.py` output: 167 artifact nodes, 242 total nodes, 479 edges
- CLAUDE.md §10 Information Map

Raw artifact paths from contracts: ~120 unique paths (produces + derived_from union).
After deduplication and normalization: ~45 distinct artifact types grouped into 9 categories.

## Token design rationale

1. Tokens are single-word or short hyphenated identifiers (e.g. `goal`, `handoff`, `concept-canon`).
2. Tokens must be usable in agent names (REQ-PROC-044-01 AC-01) — no slashes, no path syntax.
3. Path field uses glob syntax matching the actual filesystem patterns from contracts.
4. No two tokens describe the same artifact (no-overlap rule from AC-01, AC-04).
5. Variants that are sub-files of the same logical artifact are folded into one token
   (e.g. all `scribbles/v*/` files → `scribble` token with glob `**/scribbles/v{n}/`).

## Files to create

1. `.factory/registry/artifacts.yaml` — 45 tokens across 9 groups (DRAFT — requires ratification)
2. `.factory/README.md` — lifecycle split + subfolder inventory + .claude/ exclusion (AC-05)

## Pruning protection (AC-05)

`.gitignore` already has `.factory/session_logs/` but NOT `.factory/registry/`.
No pruning script targets `registry/`. No further action needed beyond committing the file.

## Developer ratification gate

The seeded token set must NOT be auto-finalized. After creating the draft files, this session
writes a `pending_feedback` question listing all tokens for the developer to confirm/rename/reject.
The developer edits `answer.md`; the orchestrator resumes; then task-complete is called.
