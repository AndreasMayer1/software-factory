---
skill: task-resolve
mode: interactive
decision: "redirected"
task_id: TASK-PROC-069-03
captured_at: 2026-06-05
---

# Question

Proposed plan: CLAUDE.md L157 edit, contract.yaml inline, task-resolve in Phase 3, no review point

# Developer Answer

1. CLAUDE.md needs no claude-route edit — drop "L157" (it's an error). There
  are exactly two claude-route refs in CLAUDE.md:
  - L154 (§4 Default Workflow) — already says task-start … delegates to 
  claude-route. Already migrated in 069-02. ✓ 
  - L157 (§4 Session model) — "Manual sessions: claude-route tells the user to 
  run /model opus." Per decision D-D the opus-check stays in claude-route
  (synthesis §5: "Kept in claude-route: … opus-check"). So this line is correct
  as-is. Changing it to "task-start tells the user" would mis-describe where
  the opus-check lives. Leave L157 alone.
  
  2. contract.yaml is misplaced in Phase 1 (inline) — move it into Agent A 
  (Phase 2). Narrowing claude-route's contract is (a) coupled to the SKILL.md
  shrink and (b) owned by claude-modify-skill (its step 4b handles
  contract.yaml). Editing it inline both violates the "skill modifications MUST
  go through claude-modify-skill" rule and splits one coupled change across
  two contexts. It belongs in the same claude-modify-skill call that shrinks
  the SKILL.md.

  3. task-resolve shouldn't be in Phase 3 — it's 4 skills, not 5. Its only
  claude-route ref is line 8 — "routed here by claude-route when 
  writes_requirements is not set" — which is claude-route's surviving 
  internal-router role (it keeps the type→skill match, including that branch).
  It stays. And §2/§3 are already rewritten (the agent-rules work, from my
  session). So task-resolve needs no migration edit at all; Phase 3 =
  task-derive-from-requ, task-complete, verify-quality, task-create-code.

  Recommendation (not an error): add one review point for the claude-route 
  shrink. It's the single load-bearing structural change — mode removal plus
  contract narrowing — and it's easy to silently drop the verification-task
  shortcut (step 3b) or the opus-check (step 5). Have Agent A return the
  SKILL.md + contract diff for a quick look. "Review: none" is right for the
  trivial text edits, but under-weights this one.

  On AC-06: the conclusion "resume path logic is already correct" matches what
  I see — L1610's _should_resume resumes the exact in_progress session
  (task-start already ran in it), and the fresh path launches "Do next task" (→
  task-start). So no automated path bypasses task-start. Two notes: confirm
  L1610 explicitly rather than pre-asserting it, and the L2121 comment edit is
  right — "bypassed claude-route" → "bypassed task-start", since task-start now
  owns the session_id write that the resume-UUID depends on.

  Net: strong plan, rule update validated. Fix the three file-state mismatches
  (drop CLAUDE.md/L157, move contract.yaml to Agent A, drop task-resolve from
  Phase 3) and I'd add the one diff-review on the claude-route shrink.

# Rationale Captured

Developer corrected three scope errors and added a review point for the structural claude-route shrink
