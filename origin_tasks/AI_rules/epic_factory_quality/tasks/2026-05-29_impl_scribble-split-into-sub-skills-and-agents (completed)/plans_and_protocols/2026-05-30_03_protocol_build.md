---
task_id: TASK-PROC-044-07
date: 2026-05-30
author: orchestrator (live interactive session, Opus 4.8)
skills_used:
  - claude-route
  - task-resolve
  - claude-create-skill
  - claude-modify-skill
  - task-complete
  - claude-commit
---

# Build protocol — SCRIBBLE-SPLIT

## Decisions locked
- Blocker 1 (heuristics corpus): resolved via option **1a** — corpus authored first by a
  background subagent (agent `a6a78f8c10f49efe9`, with WebSearch). DONE.
  Files: `doc/presentation/heuristics/{README,nielsen_usability,universal_design,microinteractions,dark_patterns,motion_as_function}.md` (859 lines). See `02_protocol_heuristics_corpus.md`.
- Blocker 2 (rewiring surface): rewire all ~8 references, not just the 4 named in the goal.

## Decision (user, 2026-05-30): agent creation = MANUAL
`claude-create-agent`/`claude-modify-agent` do not exist (NEW-SKILL bundle D22, from
TASK-PROC-032-10's deferred set — never sequenced before 044-07). goal.md §4 explicitly
authorizes manual creation as the fallback. User chose "Manual now". TODO afterward: log
claude-create-agent + claude-modify-agent (NEW-SKILL bundle) as their own task.

## Build order (bottom-up so references resolve)
1. [x] 6 agent files in `.claude/agents/` — DONE (ui-scribble-generator 119L, rule-reviewer,
       heuristics-reviewer, persona-walker, feedback-classifier, handoff-emitter)
   - ui-scribble-generator (Phase 1 generation prompt)
   - ui-scribble-rule-reviewer (ACs / T1-T2 / sections / component-map / info-model / exception / domain-concepts)
   - ui-scribble-heuristics-reviewer (applies doc/presentation/heuristics/ corpus)
   - ui-scribble-persona-walker (persona embodiment walk)
   - ui-scribble-feedback-classifier (classify feedback + tier + screen scope)
   - ui-scribble-handoff-emitter (emit flutter_handoff.yaml)
2. [ ] 3 sub-skills via claude-create-skill (+ contract.yaml each):
   - ui-scribble-auto-review (Phase 2; fans out to the 3 reviewers)
   - ui-scribble-feedback-classify (Phase 4)
   - ui-scribble-approve-handoff (Phase 5)
3. [ ] claude-modify-skill: ui-create-scribble → ui-scribble-iterate (slim orchestrator)
4. [ ] Rewire consumers: factory_flows.md, INDEX.md, task-derive-from-requ, task-create,
       code-simple, code-complex, ui-verify-flutter, ui-create-scribble-improve
       (+ verify ui-improve-flutter)
5. [ ] Lint: scripts/quality/check_skill_contracts.py
6. [ ] Smoke test (trace one invocation path)
7. [ ] claude-log, doc-update-guidelines, task-complete

## Mid-build reassessment (user, 2026-05-30) — STRUCTURE-ONLY
User flagged a possible sequencing conflict with the in-progress TASK-PROC-032-10
(scribble-contract-and-ux-review exploration). Investigated:
- 032-10 frontmatter `after:` includes 044-07; its **iteration-6 protocol (today, Opus 4.8)**
  ratifies the EXACT split shape built here (§2) and states the content bundles can only be
  finalized once 044-07's structure lands. → **044-07 structural split is correctly
  sequenced, not premature.**
- External-boundary rollout (044-12) targets EXTERNAL interfaces + adds additive
  `input_modality:`; does NOT refactor internal scribble contracts. → no build-then-refactor.
- BUT 032-10 iter-6 §4: 044-07 delivers STRUCTURE only. Scribble CONTENT (Q2-CONTRACT;
  Q1-AGENTS = what heuristics-reviewer/persona-walker enforce — Han UX-review port, Question
  Log, Affordance/Dark-Pattern/anti-pattern guards, embodiment, iteration-fatigue, inter-
  version diff, review brief) is designed in 032-10 iters 1–4 and must be folded into
  REQ-PROC-032 via requ-explore→derive. → the heuristics corpus I authored OVERSTEPPED;
  marked PROVISIONAL.

User decision: **finish 044-07 as structure-only**; defer content to a REQ-PROC-032
requ-explore pass.

## Final state
- [x] 6 agents · [x] 3 sub-skills + contracts · [x] orchestrator renamed (git mv, history kept)
- [x] INDEX updated · [x] factory_flows renamed · [x] consumers rewired (code-simple/-complex,
      ui-verify-flutter, ui-create-scribble-improve, task-create, task-derive-from-requ,
      ux-write-canon-concept contract, schema comments)
- [x] heuristics corpus marked PROVISIONAL (README banner + reviewer-agent caveat)
- [x] **Contract lint: PASS — 63 contracts, 0 violations**
- [x] **Structural smoke: PASS** (orchestrator→3 sub-skills+generator; auto-review→3 reviewers;
      no orphan; zero dangling refs)
- Smoke AC note: full LIVE pipeline run deferred — it would exercise provisional content;
  structural trace is the right level for structure-only completion.

## FOLLOW-UPS to seed (logged, not done here)
1. **REQ-PROC-032 requ-explore pass** — fold Q2-CONTRACT + Q1-AGENTS content (from 032-10
   iters 1–4) into REQ-PROC-032 ACs aligned to the new ui-scribble-* producers; reconcile/
   replace the provisional heuristics corpus; then task-derive-from-requ. (Unblocks 032-10 closure.)
2. **claude-create-agent + claude-modify-agent** (NEW-SKILL bundle D22, from TASK-PROC-032-10)
   — agents were hand-written here per goal §4 fallback; the skill is still owed.
3. **ui-create-scribble-improve multi-file retarget** — post-split, scribble quality is shaped
   by the generator + 3 reviewer agents + auto-review sub-skill; the improve loop's single-file
   assumption (now repointed to ui-scribble-generator.md) should be extended to the reviewer set.

## Content provenance (current ui-create-scribble SKILL.md → new homes)
- Phase 0 (multimodal seed)            → ui-scribble-iterate (orchestrator)
- Phase 1 (generate, lines 27-139)     → ui-scribble-generator agent
- Phase 2 (auto-review, lines 141-174) → ui-scribble-auto-review sub-skill + 3 reviewer agents
- Phase 3 (await review)               → ui-scribble-iterate
- Phase 4 (feedback, lines 182-226)    → ui-scribble-feedback-classify sub-skill + classifier agent
- Phase 5 (approval, lines 228-256)    → ui-scribble-approve-handoff sub-skill + handoff-emitter agent
- Phase 5a (flow index, lines 258-268) → ui-scribble-iterate
- Iteration pattern + Constraints      → ui-scribble-iterate
