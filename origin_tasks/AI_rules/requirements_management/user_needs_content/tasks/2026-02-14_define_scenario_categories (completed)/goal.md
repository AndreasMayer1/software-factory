---
task_id: TASK-PROC-027-13
type: define
parent_requirement: REQ-PROC-027
urgency: 4
urgency_reason: U4-IMPL
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-02-14
effort: M
created: 2026-02-14
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Define and add 4 new scenario category stubs to SCENARIO_INDEX.md; evaluate Gemini suggestions critically; check persona coverage for template sharing"
requirements_version:
  commit: edb2b1e
  file: ../requirements.md
---

# Goal: Define New Scenario Categories in SCENARIO_INDEX.md

## Objective

Add 4 new scenario category stubs to `requirements_user_needs/SCENARIO_INDEX.md`.
No new scenarios are to be created — only the category/sub-category definitions
(id, canonical_name, display_name, description, applicable_roles, instances: [],
gaps: []) for each new category.

Also: evaluate whether the 2 additional categories Gemini suggests
(`lifecycle.setup` and `lifecycle.destruction`) should be added.

Finally: check existing personas and determine whether the "template sharing"
need should be added to any of them.

---

## Categories to Add

### 1. Data Preservation / Backup  (new sub-category under `management` stage)

**Context:** Users fear losing all tracked data when they lose their device,
switch to a new phone, or damage their notebook. Status-quo solutions differ by
medium:
- Paper users: fireproof safe, scanning into praxissoftware backup
- Notes-app users: rely on OS backup (iCloud, Google Drive) — often
  accidentally or without explicit intent
- Paper+scan hybrid: scanned images in the praxissoftware or a cloud folder

**Gemini suggestion:** `management.preservation` with sub-categories:
- `device_loss_recovery`: recovering after loss/theft (phone, notebook)
- `migration`: moving to a new device or system
- `long_term_storage`: archiving completed therapy cycles

**Questions for the agent to evaluate / challenge:**
- Is "preservation" the right parent name? Compare to existing sibling
  categories `management.archive_and_retrieve` and `management.share_externally`.
  Does it fit or should it be `management.backup_and_recovery`?
- Are three sub-categories needed or would one parent category cover enough?
- How does this differ from `management.archive_and_retrieve`? (archive =
  intentional filing of old data; preservation = emergency recovery, migration)
  Make sure descriptions are clearly distinct.

---

### 2. Intervention / Crisis Support  (new top-level stage OR sub-category)

**Context:** Some tracking instruments include more than data collection — they
also provide instructions to follow in difficult moments:
- Skill cards: printed cards with DBT/CBT coping techniques, carried in wallet
- Emergency-action instructions: "If you notice serious medication side effects
  → call the praxis immediately"
- Safety-plan items: "If you feel suicidal → call [number]"
- These are NOT filled out by the user but consulted/followed in a crisis

**Gemini suggestion:** `intervention.support` with sub-categories:
- `acute_coping`: using skill cards or coping technique lists during distress
- `safety_protocol`: following emergency/suicidal-crisis instructions
- `resource_activation`: accessing hope box, uplifting images, etc.

**Questions for the agent to evaluate / challenge:**
- Is this a new top-level STAGE or a sub-category of an existing stage?
  The current data flow is: creation → distribution → capture → analysis →
  management. Intervention sits outside this linear flow — it's triggered by
  emotional state, not by a step in the process. Recommend treating as a
  new stage `intervention` at the same level as the others.
- Is "intervention.support" the right name? The category covers both
  crisis (safety_protocol) and routine coping (acute_coping). Consider
  `intervention.access_support_resources` or just the sub-categories
  directly under `intervention`.
- `resource_activation` (hope box) — is this really a different category from
  `acute_coping`, or should it be a variant? Evaluate.
- Consider whether there is also a "preparation" sub-category: the therapist
  or client sets up the skill card / safety plan in the first place. This
  might overlap with `creation.prepare_protocol`.

---

### 3. Plan Modification  (new top-level stage)

**Context:** The tracked data analysis often leads to adjustments to the
"homework" protocol — adding a column, removing a confusing row, rewording
a question. This can happen:
- In the therapy session: therapist crosses out a column and writes a new one;
  prints a revised sheet; pastes a sticky-note addendum
- Between sessions (autonomous): client covers a stressful column with tape,
  invents their own shorthand, stops filling out certain rows by decision or
  frustration

**Gemini suggestion:** `adaptation.plan_modification` with sub-categories:
- `collaborative_adjustment`: modification together with therapist in session
- `autonomous_adjustment`: modification by the client alone

**Questions for the agent to evaluate / challenge:**
- "adaptation" as the stage name — does it match the verb-noun style of other
  stages? Compare: `capture`, `analysis`, `management`, `distribution`. The
  existing stages use nouns, not action-words. Consider `modification` as the
  stage name instead of `adaptation.plan_modification`.
- Proposed stage: `modification` with sub-categories:
  - `modification.collaborative`: in-session adjustment (therapist + client)
  - `modification.autonomous`: client-side adjustment alone
- Are these two sub-categories sufficient, or is there a third for
  therapist-only modification (therapist adjusts the template before
  the next session, without the client present)?
- Clarify the boundary with `creation.prepare_protocol`: creating a protocol
  FROM SCRATCH vs. modifying an EXISTING one — this is the key distinction.

---

### 4. Template / Knowledge Sharing  (new top-level stage)

**Context:** Therapists and clients sometimes share not just filled-out data,
but the *plan templates themselves* — the structure of what to track, when,
how, and why. Status-quo:
- Therapists: copy templates from VT therapy manuals (photocopying), share
  verbally with colleagues, adapt published CBT worksheets
- Clients/self-users: discover tracking structures in self-help books,
  ratgeber apps, online communities
This is about sharing the *blueprint*, not the *filled data*.

Future vision (for context only — NOT to be written in scenarios):
The app plans XML export/import for plan templates, or a free "template store".

**Gemini suggestion:** `exchange.knowledge_transfer` with sub-categories:
- `peer_to_peer_sharing`: therapist→therapist template sharing
- `self_discovery`: client/self-user searching for suitable tracking structure

**Questions for the agent to evaluate / challenge:**
- Is "exchange" the right stage name? Consider `sharing` or `template_sharing`
  as more concrete alternatives, keeping the verb-noun pattern.
- Is "knowledge_transfer" the right sub-category name? It's broad. Consider
  `share_template_with_colleague` and `discover_template_independently`.
- Check: Is there a meaningful distinction between "sharing" and "discovering"
  worth making into separate sub-categories, or is this one category
  `sharing.templates` with role-based variants?

**Persona check required (for each persona below, the agent must read the
persona's persona.md and determine whether to add the template-sharing need):**

| Persona | File | Gemini assessment | Your task |
|---------|------|-------------------|-----------|
| Lisa (Waitlist Bridger) | `requirements_user_needs/personas/lisa_waitlist_bridger/persona.md` | High urgency — she must find a tracking structure without a therapist | Verify: does her current persona.md already reflect this? If not, flag as gap in persona |
| Dr. Sarah | `requirements_user_needs/personas/dr_sarah/persona.md` | Medium — shares with colleagues, uses manuals | Same |
| David (Structure Seeker) | `requirements_user_needs/personas/david_structure_seeker/persona.md` | High — shiny-object syndrome, always seeking perfect system | Same |
| Prof. Dr. Weber | `requirements_user_needs/personas/prof_dr_weber/persona.md` | Low/Negative — prefers individual work | Same |

For each persona: note the verdict (needs update / already covered / out of
scope) and list it in a gap entry in the new category, if applicable. Do NOT
modify personas in this task — only note the gap.

---

### 5. (Open Question) lifecycle.setup — Onboarding Hurdles

**Gemini suggestion:** Add a new category for the friction of initially
setting up a tracking system (downloading app, getting first blank form,
understanding what to write). Relevant for Sophie (ADHD setup barrier),
Elias (privacy refusal at first encounter), Lisa (no therapist guiding her).

**Agent decision required:**
- Is this already covered by `distribution.instruct_client` (therapist side)
  and `distribution.receive_protocol` (client side)?
- Or is "setting up without a therapist" a genuinely different scenario
  category that doesn't fit under distribution?
- Recommend or reject this category with reasoning.

---

### 6. (Open Question) lifecycle.destruction — Data Deletion / End of Therapy

**Gemini suggestion:** Add a category for intentionally destroying tracked data
(shredding paper at end of therapy, panic-deleting app data when feeling unsafe,
selective removal of sensitive entries). Relevant for Elias (privacy fears),
Jana (shame-driven selective deletion).

**Agent decision required:**
- Is this already covered by `management.archive_and_retrieve` (the "throwing
  away" path) or `management.share_externally`?
- Or does the emotional/intentional destruction aspect make it distinct enough?
- Recommend or reject this category with reasoning.

---

## Scope

### In Scope
- Adding 4 confirmed category stubs to SCENARIO_INDEX.md (with all required
  fields: id, canonical_name, display_name, description, applicable_roles,
  instances: [], gaps)
- Making a documented decision on categories 5 and 6 (add or reject, with
  reasoning) and adding them if accepted
- Checking 4 named personas for template-sharing need and documenting gaps
- Critically evaluating Gemini's naming suggestions (don't adopt blindly)
- Following SCENARIO_INDEX.md naming conventions exactly:
  - stage names: nouns, snake_case
  - sub-category ids: `[stage].[sub]`
  - canonical_names: verb_object_qualifier
  - Word standardization per index header

### Out of Scope
- Creating any new scenario documents (folder + scenario.md files)
- Modifying existing persona.md files
- Creating user flows
- Implementing any app features

## Acceptance Criteria

- [ ] 4 new category stubs added to SCENARIO_INDEX.md with all required fields
- [ ] Each new stage/sub-category has a clear, distinct description that does
      NOT overlap with existing categories
- [ ] Gemini's naming suggestions are evaluated — deviations from Gemini are
      documented with reasoning
- [ ] Decisions on `lifecycle.setup` and `lifecycle.destruction` are documented
      with rationale; accepted ones are added to the index
- [ ] Persona check for template-sharing is complete for all 4 named personas;
      gaps noted in category stubs where applicable
- [ ] All names follow SCENARIO_INDEX.md word standardization and snake_case
      conventions

## Notes

**Key naming rule** (from SCENARIO_INDEX.md header):
- Stages: noun (capture, analysis, management, distribution, creation)
- Sub-category ids: `[stage].[sub_category_noun]`
- canonical_names: `[verb]_[object]_[qualifier]` (snake_case)
- Word list: transfer, protocol, capture, collaboratively, spontaneously, data

**Distinction clarification needed:**
- `management.archive_and_retrieve` ≠ `management.preservation`
  Archive = intentional long-term filing after therapy session
  Preservation = avoiding accidental loss (device change, fire, theft)
- `creation.prepare_protocol` ≠ `modification.collaborative`
  Creation = designing from scratch
  Modification = adjusting an existing protocol in use

**Gemini context:** The Gemini analysis is a starting point — it should be
questioned, not adopted verbatim. The agent is expected to propose better names
where the existing conventions suggest improvements. requirements_tasks\process\AI_rules\requirements_management\user_needs_content\tasks\2026-02-14_define_scenario_categories\gemini_suggestions.md
