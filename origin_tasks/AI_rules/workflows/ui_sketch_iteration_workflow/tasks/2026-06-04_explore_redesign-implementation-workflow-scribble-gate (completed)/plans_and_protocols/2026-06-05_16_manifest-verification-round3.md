# Manifest coverage verification — round 3 (ground-truth pass)

Task: TASK-PROC-032-29. Date: 2026-06-05.
Developer ask: *run another verification round once that one is done.* Rounds 1–2 were **documentary** (manifest
vs decisions / change-list / PROPs / F-findings). Round 2 §7 noted those lenses were exhausted and the next
material check is **ground-truth**: does every skill, agent, script, and code-anchor the manifest names
**actually exist as named, in the right place**? A documentary round cannot catch a task pointed at a target
that moved, was renamed, or is the wrong artifact *kind*. Round 3 is that check.

**Verdict:** ground-truth surfaced **1 material gap** (a systematic skill-vs-agent mis-classification across 3
rows) — now remediated — and **confirmed the D-0 bug is real at the exact cited line**. All other named
targets exist as specified.

---

## 1. Existence checks — every named target

| Target (manifest) | Expected kind | Found | Status |
|-------------------|---------------|-------|--------|
| `ui-scribble-iterate` | skill | `.claude/skills/` | ✅ |
| `ui-scribble-auto-review` | skill | `.claude/skills/` | ✅ |
| `ui-scribble-feedback-classify` | skill | `.claude/skills/` | ✅ |
| `ui-verify-flutter` | skill | `.claude/skills/` | ✅ |
| `release-begin-impl` | skill | `.claude/skills/` | ✅ |
| `release-begin-impl-finalize` | skill | `.claude/skills/` | ✅ (rename target real) |
| `task-derive-from-requ` | skill | `.claude/skills/` | ✅ |
| `requ-derive-from-flow` | skill | `.claude/skills/` | ✅ |
| `requ-verify-flow-coverage` | skill | `.claude/skills/` | ✅ (it is a skill, not a script) |
| `claude-create-skill / modify-skill / write-script / modify-agent / create-agent` | skills | `.claude/skills/` | ✅ |
| `ui-scribble-generator` | **agent** (+`.contract.yaml`) | `.claude/agents/` | ⚠️ manifest said "skill" → **R3-GAP-1** |
| `ui-scribble-cross-feature-checker` | **agent** | `.claude/agents/` | ⚠️ manifest said "skill" → **R3-GAP-1** |
| reviewers (`rule-reviewer`, `persona-walker`, `heuristics-reviewer`) | **agents** | `.claude/agents/` | ⚠️ → **R3-GAP-1** |
| `scripts/tasks/create_orchestration_task.py` | script | exists | ✅ |
| `scripts/quality/check_scribble_parity.py` | script | exists | ✅ |
| `.factory/registry/artifacts.yaml` | file (B4/C5 target) | exists (17 KB) | ✅ |
| REQ-PROC-032 / 035 / 058 | requirements | all exist | ✅ |

## 2. D-0 ground-truth (the one bug the plan must fix first)

Confirmed **real and exactly as documented**. `scripts/tasks/create_orchestration_task.py`:
```
275:        if task_type == "scribble":
276:            skill = "ui-create-scribble"      # ← non-existent skill (real skill: ui-scribble-iterate)
277:        elif task_type in ("verify", "verification", "explore"):
279:        elif task_type == "scribble_to_flutter":
```
So today's chain would route every scribble task to a skill string that does not exist. T-C0 is correctly the
**first** task, and the line/behaviour match the manifest's claim precisely. ✅

## 3. R3-GAP-1 — skill-vs-agent mis-classification → remediated

The scribble machinery is split across `.claude/skills/` and `.claude/agents/`. The manifest's first pass
listed three agent targets under `claude-modify-skill`, which is the **wrong governance skill** (agents are
modified via `claude-modify-agent`, created via `claude-create-agent`; the generator also has a
`.contract.yaml` that is part of its output-contract change). This is material because an executor following
the manifest would invoke the wrong tool and the change would be rejected/mis-filed.

**Affected & remediated rows in `13`:**
- **T-C11** — `ui-scribble-cross-feature-checker` is an **agent** → creator now `claude-modify-agent` (checker)
  + `claude-modify-skill` (auto-review, which *is* a skill).
- **T-C12** — `ui-scribble-generator` + the reviewers are **agents** → creator now `claude-modify-agent`
  (generator + reviewers) + `claude-modify-skill` (auto-review).
- **T-C15** — `ui-scribble-generator` (+ its `.contract.yaml`) is an **agent** → creator now
  `claude-modify-agent` (generator + contract) + `claude-write-script` (overlay).

Also added a durable **"Skill vs agent (ground-truth)"** note to the manifest's *How to read this* so the
split — and the `feedback-classify` (skill) vs `feedback-classifier` (agent) trap — is not re-introduced.

## 4. Anchors that were NOT mis-stated (confirmed correct)

- `ui-scribble-feedback-classify` (T-C10) really is a **skill** — correct as `claude-modify-skill`. (The
  similarly-named `ui-scribble-feedback-classifier` is the agent; the manifest targets the right one.)
- `ui-scribble-iterate` / `ui-scribble-auto-review` (T-C16) are **skills** — correct.
- `release-begin-impl-finalize` exists, so the T-C4 rename has a real source.
- `requ-verify-flow-coverage` is a **skill** (round-2 R2-GAP-1 / T-C17 Tier-B home) — correct to modify it,
  and it exists.

## 5. Round-3 verdict & the stopping point

- **Ground-truth: 1 material gap (R3-GAP-1), remediated; D-0 confirmed real; all other targets exist as
  named.** The manifest is now correct against the live `.claude/` + `scripts/` + `.factory/` tree.
- **Three independent verification lenses are now exhausted:** documentary-coverage (round 1), F-findings +
  existence + DAG (round 2), live-artifact ground-truth (round 3). Each found progressively fewer, narrower
  issues: 6 → 3 → 1.
- **Recommendation: stop documentary/ground-truth verification here.** The next genuinely different — and now
  *higher-value* — check is **sufficiency**, which cannot be done by inspecting the plan: it requires
  executing **T-A1/T-A2** (author the requirements) and letting `task-derive-from-requ`'s own coverage matrix +
  the per-requirement verification tasks confirm each task, once derived, fully satisfies its source AC.
  Further re-reads of the manifest will not surface what only requirement-authoring will.

## 6. Honest residual (unchanged across all three rounds)
Verification has established that the plan is **complete** (nothing missing) and **well-formed** (targets real,
DAG valid, governance-tool correct). It has **not** established **sufficiency** (that executing each task fully
discharges its source) — that is downstream, by construction, in the requ-explore + task-derive-from-requ
coverage machinery. No amount of manifest re-reading substitutes for it.
