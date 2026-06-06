# Plan: Update task-create-code skill (TASK-PROC-058-05)

Date: 2026-05-25
Approach: inline (single deliverable, clear shape)

## Deliverable

`.claude/skills/task-create-code/SKILL.md` — updated via `claude-modify-skill`.

## What Is Already Correct

- Phase 0A plan-driven discovery exists
- propose_after.py scoped to `requirement_then_implementation` in plan-driven mode (lines 134-151)
- AC-13 enforcement (WHAT not HOW) present throughout
- Plan conformance check (Phase 6) handles plan-driven mismatch escalation

## Required Changes

### 1. Redirect Logic (AC-10)

Add a new section `## Redirect Logic (AC-10) — Standalone Mode Only` **before** Phase 0.
Logic mirrors task-create §3c exactly:
- Skip if plan-driven, bugfix, explore, define, analyze, review
- Trigger if: standalone + impl/verify + parent has uncovered ACs
- Check via coverage_report.py + grep
- Redirect: print message, invoke task-derive-from-requ
- Override: `--standalone-override` (automated: never auto-override)

### 2. Phase 0A: requirements_version + stale-plan check (AC-12 consumer)

In step 3 (authoritative defaults list):
- Change `effort → used directly (skip Phase 2.3 estimation)` → `effort → accepted as baseline; Phase 2 still runs to refine (see AC-15)`
- Add `requirements_version → used for stale-plan detection (step 3.5)`

Add **step 3.5** after step 3:
- Compare plan's `requirements_version.commit` against `git log -1 --format=%h -- [req_path]`
- If mismatch: interactive → warn + ask (proceed/abort/re-plan); automated → write question.md + stop
- If match: continue silently

### 3. Phase 2.3: Escalation for plan-driven sizing mismatch (AC-15)

After the size table, add a **Plan-driven mode escalation** block:
- If plan effort is S/M but file analysis reveals Large → Split NOW
- Interactive: ask user (split / promote to Opus / override)
- Automated: write question.md in plans_and_protocols/ and stop
- Note in Automated Mode table under "When auto-accept is NOT safe"

### 4. Phase 4.1: Skip user confirmation in plan-driven mode (AC-11/AC-15)

Add note to Phase 4.1:
- Plan-driven mode: skip Phase 4.1 (plan was approved upstream)
- This generalizes the automated mode row to all plan-driven executions

### 5. Automated Mode table — new rows

Add:
| Redirect in standalone mode | Ask user | Always redirect (never auto-override) |
| Stale plan check mismatch | Ask user proceed/abort | Write question.md + stop |
| Phase 2.3 plan-driven mismatch | Ask user | Write question.md + stop |

## Mandatory Tooling

Use `claude-modify-skill` per CLAUDE.md.
