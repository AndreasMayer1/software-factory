# Protocol: Define New Scenario Categories

**Task**: TASK-PROC-027-13
**Date**: 2026-02-14
**Agent**: Claude Opus 4.6
**Status**: Complete

---

## 1. Naming Decisions & Gemini Deviations

### Category 1: Data Preservation / Backup

| Aspect | Gemini Suggestion | My Decision | Reasoning |
|--------|-------------------|-------------|-----------|
| Stage | (under management) | (under management) | Agreed — data preservation is data management |
| Category ID | `management.preservation` | `management.preservation` | Accepted — "preservation" is a clear noun, fits convention |
| Canonical name | (none suggested) | `protect_data_from_loss` | Follows verb_object_qualifier pattern; clearly distinct from `archive_and_retrieve_data` |
| Sub-categories | `device_loss_recovery`, `migration`, `long_term_storage` | None (single category) | **DEVIATION**: Sub-categories are scenario variants, not structural categories. The existing index has no sub-sub-categories. |

**Key distinction**: `archive_and_retrieve` = intentional long-term filing after use. `preservation` = preventing accidental loss (device failure, theft, damage, migration).

### Category 2: Intervention / Crisis Support

| Aspect | Gemini Suggestion | My Decision | Reasoning |
|--------|-------------------|-------------|-----------|
| Stage | `intervention.support` (ambiguous level) | `intervention` (new top-level stage) | **DEVIATION**: Intervention sits outside the linear data flow (triggered by emotional state). Deserves own stage. |
| Category 1 | `acute_coping` | `intervention.coping` | Slightly broader name; merged with `resource_activation` |
| Category 2 | `safety_protocol` | `intervention.safety` | Shortened; clear enough |
| Category 3 | `resource_activation` | (merged into `intervention.coping`) | **DEVIATION**: Hope box / uplifting images are a FORM of coping. Not distinct enough for own category. |

**Placement rationale**: Existing data flow is creation → distribution → capture → analysis → management. Intervention doesn't follow this sequence — it's triggered by emotional state at any point. New stage, not a sub-category of an existing one.

### Category 3: Plan Modification

| Aspect | Gemini Suggestion | My Decision | Reasoning |
|--------|-------------------|-------------|-----------|
| Stage | `adaptation` | `modification` | **DEVIATION**: "adaptation" doesn't match noun style. Compare: creation, distribution, capture, analysis, management — all concrete nouns. "modification" is more concrete. |
| Category ID | `adaptation.plan_modification` | `modification.collaborative` / `modification.autonomous` | **DEVIATION**: Removed redundant "plan_modification" — the stage already implies protocol modification. |
| Canonical 1 | `collaborative_adjustment` | `modify_protocol_collaboratively` | Follows word standardization: "collaboratively" (not "with_client"), "protocol" (not "plan") |
| Canonical 2 | `autonomous_adjustment` | `modify_protocol_autonomously` | Consistent verb_object_qualifier pattern |
| Third category? | Not suggested | Noted as gap | Therapist-only modification (between sessions, without client) is a potential third variant |

**Key distinction**: `creation.prepare_protocol` = designing FROM SCRATCH. `modification.*` = adjusting an EXISTING protocol in use.

### Category 4: Template / Knowledge Sharing

| Aspect | Gemini Suggestion | My Decision | Reasoning |
|--------|-------------------|-------------|-----------|
| Stage | `exchange` | `sharing` | **DEVIATION**: "exchange" implies bidirectional, which isn't always the case. "sharing" is concrete and matches noun style. |
| Category ID | `exchange.knowledge_transfer` | `sharing.peer_exchange` / `sharing.independent_discovery` | **DEVIATION**: "knowledge_transfer" is academic jargon. More concrete names. |
| Canonical 1 | `peer_to_peer_sharing` | `share_template_with_peer` | Follows verb_object_qualifier pattern |
| Canonical 2 | `self_discovery` | `discover_template_independently` | More specific; self_discovery is too broad |

**Key distinction**: `management.share_externally` = sharing FILLED DATA with third parties. `sharing.*` = sharing BLANK TEMPLATE BLUEPRINTS.

---

## 2. Open Question Decisions

### lifecycle.setup (Onboarding) — REJECTED

**Reasoning**:
1. `distribution.instruct_client` covers therapist-guided setup
2. `distribution.receive_protocol` covers client receiving and beginning to use
3. The "setting up without a therapist" gap is directly addressed by new `sharing.independent_discovery` — Lisa finding what to track IS the missing piece, not the technical setup
4. Physical/technical setup friction (downloading app, finding pen, making space) is a BARRIER within existing categories, documented in persona barriers and scenario pain points
5. Gemini's examples (Sophie's download frustration, Elias's privacy refusal) are barrier descriptions, not scenario categories

**Conclusion**: The meaningful gap (finding structure without guidance) is covered by `sharing.independent_discovery`. The friction of physical/technical setup is a cross-cutting concern (barrier), not a scenario category.

### lifecycle.destruction (Data Deletion) — ACCEPTED as `management.destruction`

**Reasoning**:
1. NOT a new stage — it's data management (one endpoint of the data lifecycle)
2. Clearly distinct from `archive_and_retrieve` (keeping ≠ eliminating)
3. NOT covered by existing categories:
   - `archive_and_retrieve` = preserving and retrieving → opposite intent
   - `share_externally` = sending to others → different action entirely
4. Strong emotional drivers make this distinct from routine editing:
   - Privacy panic (Elias: partner saw phone → delete everything)
   - Shame-driven selective deletion (Jana: ripping out pages)
   - Therapeutic closure (end of therapy → ritual destruction)
5. Both medium-specific (shredding paper, deleting app data) and emotionally charged

**Conclusion**: Accepted as `management.destruction` with canonical name `destroy_data_intentionally`.

---

## 3. Persona Check: Template Sharing

### Lisa (PERSONA-005, self_user) — NEEDS UPDATE

**Current state**: Persona mentions "Get guidance on WHAT to track (psychoeducation) since no therapist explains the model" in Jobs to Be Done. Status quo lists "No guidance on what to document" as a pain point.

**Gap**: The need to actively DISCOVER and EVALUATE tracking templates/structures is not explicitly captured. Lisa doesn't just need "guidance" — she needs to FIND concrete templates (in books, apps, forums) and determine if they're suitable for her situation. This is a distinct action from receiving psychoeducation.

**Urgency**: HIGH — Lisa has no therapist to provide structure. Template discovery is her primary onboarding path.

**Action**: Flag as gap in `sharing.independent_discovery` category. Do NOT modify persona in this task.

### Dr. Sarah (PERSONA-001, therapist) — GAP EXISTS

**Current state**: Persona mentions maintaining Word templates, printing them, and representing the PiA/Beginner cluster. Jobs include "Prepare customized tracking protocols without rewriting standard elements."

**Gap**: Sharing templates WITH colleagues or receiving templates FROM colleagues is not documented. The implicit cluster "The Beginners: Therapists in training (PiA) seeking security through standardized protocols" implies a mentoring/sharing dynamic that the persona doesn't capture explicitly. Dr. Sarah would share best-practice templates during supervision or with practice partners.

**Urgency**: MEDIUM — documented in existing workflow but not as an explicit need.

**Action**: Flag as gap in `sharing.peer_exchange` category.

### David (PERSONA-008, self_user) — NEEDS UPDATE

**Current state**: Persona extensively documents "Shiny Object Syndrome" — 20+ apps installed and abandoned. He's always seeking the perfect system.

**Gap**: The persona frames template/system discovery as a PROBLEM (compulsive app-hopping, novelty addiction) rather than acknowledging the underlying NEED to find a suitable tracking structure. David's "browsing" behavior in a template store would feed his novelty-seeking — this is both a need (finding the right template) and a risk (endless browsing instead of tracking).

**Urgency**: HIGH — but dual-natured. The template discovery category should capture both the legitimate need AND the risk of novelty-seeking.

**Action**: Flag as gap in `sharing.independent_discovery` category.

### Prof. Dr. Weber (PERSONA-011, therapist) — OUT OF SCOPE

**Current state**: Persona explicitly values individual, handcrafted approaches. Anti-traits include "Not interested in shortcuts to insight (values the slow process)."

**Assessment**: Weber would NOT use template sharing. He designs each patient's journal individually as a clinical act. Using standardized templates would contradict his therapeutic philosophy. His persona accurately reflects this.

**Urgency**: NEGATIVE — template sharing contradicts his core values.

**Action**: No gap. Note as "out of scope" in protocol only.

---

## 4. Summary of Changes to SCENARIO_INDEX.md

### Added under existing `management` stage:
1. `management.preservation` — protect_data_from_loss
2. `management.destruction` — destroy_data_intentionally

### New stages added:
3. `intervention` (Stage 6) with:
   - `intervention.coping` — access_coping_resources
   - `intervention.safety` — follow_safety_protocol
4. `modification` (Stage 7) with:
   - `modification.collaborative` — modify_protocol_collaboratively
   - `modification.autonomous` — modify_protocol_autonomously
5. `sharing` (Stage 8) with:
   - `sharing.peer_exchange` — share_template_with_peer
   - `sharing.independent_discovery` — discover_template_independently

### Total: 8 category entries, 3 new stages, 2 additions to existing stage

### Version: 1.1 → 1.2
