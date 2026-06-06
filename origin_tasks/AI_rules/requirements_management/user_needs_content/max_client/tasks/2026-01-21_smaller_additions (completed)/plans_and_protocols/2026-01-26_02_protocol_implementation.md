# Implementation Protocol: Max Client Persona and Scenarios Modifications

**Task ID**: TASK-PROC-013-01
**Agent ID**: implementation-engineer-2026-01-26-001
**Date**: 2026-01-26
**Status**: COMPLETED

---

## Summary

Successfully implemented all modifications to the Max Client persona (PERSONA-002) and associated scenarios as specified in the approved plan. The work included:

1. **Persona modifications** (8 sections of changes)
2. **brain_dump_at_night scenario** complete rewrite to status quo
3. **forgotten_protocol_transfer scenario** creation (new)

---

## Files Modified

### 1. persona.md

**Path**: `requirements_user_needs/personas/max_client/persona.md`

**Changes Applied**:

| Section | Change Type | Description |
|---------|-------------|-------------|
| YAML Frontmatter | Update | version 2.0 -> 3.0, updated date, review_status draft -> in_review, added review_history entry |
| Mental Models | Rewrite | Added psychological concepts: "Protection of emotional investment" (Loeffel/energy), "Sovereignty over disclosure" (control over sharing) |
| Functional Jobs | Addition | Added "Prepare for therapy session" and "Separate channel and content" |
| Social Jobs | Addition + Fix | Added "Strengthen therapeutic alliance", fixed app reference ("logs thoughts in the app" -> "wants an outlet for processing thoughts") |
| Pain Points | Addition | Added "Ineffective sessions" (20 min memory reconstruction) |
| Primary Fears | Addition + Fix | Added "Fear of context loss/mixing", removed app-specific voice input worry, fixed "sees the app" -> "sees his notes" |
| Inertia | Fix | Removed "opening the app" references, changed to technology-neutral language |
| Anti-Persona Traits | Fix | Changed "uses the app reactively" -> "tracks reactively", "the app must not punish" -> "any tracking approach must not punish" |
| Environmental Constraints | Rewrite | Converted solution-oriented "Requirements" to need-oriented "Needs" (3 instances) |
| Core Needs | Deletion | Removed "What would make Max adopt a new solution" block (solution-oriented) |
| Version History | Update | Added v3.0 entry |
| Related Scenarios | Addition | Added section linking to both scenarios |

### 2. brain_dump_at_night/scenario.md

**Path**: `requirements_user_needs/personas/max_client/scenarios/brain_dump_at_night/scenario.md`

**Changes Applied**:

- **Complete rewrite** from app-based future state to paper-based status quo
- Updated YAML frontmatter (version 2.0, review_history entry)
- Changed name to "Brain Dump at Night (Status Quo)"
- Rewrote entire Three-Act structure to show paper journal failure:
  - Act 1: Max reaches for notebook at 02:15 AM
  - Act 2: Knocks over glass, can't turn on light, writes blindly
  - Act 3: Gives up, next morning finds illegible scrawls
- Added "Current Status Quo Analysis" section (5 failure points)
- Changed "Derived Needs" from solution features to technology-neutral needs
- Removed all app-specific features (OLED dark mode, voice-to-text, whisper detection, auto-save, etc.)
- Added link to new forgotten_protocol_transfer scenario

### 3. forgotten_protocol_transfer/scenario.md

**Path**: `requirements_user_needs/personas/max_client/scenarios/forgotten_protocol_transfer/scenario.md`

**Created**: New file

**Content**:
- Proper YAML frontmatter (scenario_id SCEN-002-02, review_status draft)
- Goal: Hand over filled "Weekly Anxiety Protocol" to Dr. Sarah
- Context: S-Bahn commute to therapy appointment
- Three-Act Structure:
  - Act 1: Max realizes protocol is on shoe rack at home
  - Act 2: Attempts to reconstruct data on phone, realizes he's fabricating
  - Act 3: Confesses to Dr. Sarah, 30% of session wasted on reconstruction
- Status Quo Analysis (5 failure points)
- Technology-neutral Derived Needs (4 needs)
- Evidence level markers
- Related scenarios section

---

## Translation Notes

The following German concepts from goal.md were translated:

| German | English |
|--------|---------|
| Loeffel (spoons) | Spoons (energy/capacity metaphor) |
| Hoheit ueber die Offenbarung | Sovereignty over disclosure |
| Schutz der emotionalen Investition | Protection of emotional investment |
| Trennung von Kanal und Inhalt | Separate channel and content |
| Therapeutisches Buendnis | Therapeutic alliance |
| Ineffektive Sitzungen | Ineffective sessions |
| Angst vor Kontextverlust | Fear of context loss/mixing |

---

## Quality Verification Checklist

### Persona

- [x] No app-specific references remain
- [x] All sections describe status quo (pen and paper)
- [x] Jobs to Be Done includes therapy preparation, channel separation, therapeutic alliance
- [x] Mental Models includes psychological concepts (emotional investment, disclosure sovereignty)
- [x] Pain Points includes ineffective sessions
- [x] Fears includes context loss/mixing concern
- [x] Evidence level markers are present
- [x] Version updated to 3.0
- [x] Review status updated to in_review
- [x] Review history entry added

### brain_dump_at_night Scenario

- [x] Describes status quo (paper/pen), NOT app
- [x] Three-act structure maintained
- [x] Status quo analysis section present
- [x] Derived needs (not solution features) documented
- [x] Evidence level markers present
- [x] review_status maintained as in_review
- [x] Version updated to 2.0
- [x] Review history entry added

### forgotten_protocol_transfer Scenario

- [x] Complete scenario created per goal.md content
- [x] Proper YAML frontmatter with scenario_id SCEN-002-02
- [x] Three-act structure present
- [x] Status quo analysis section present
- [x] Derived needs documented
- [x] Evidence level markers present
- [x] Review status set to draft

### General

- [x] All changes follow README guidelines (persona definition, scenario definition, technology neutrality)
- [x] German source content properly translated to English
- [x] No emojis added (except evidence markers)
- [x] Cross-references between files are correct

---

## Remaining Issues / Notes

1. **user_flows subdirectory**: The `brain_dump_at_night/user_flows/quick_night_entry/flow.md` file still describes app behavior (OLED dark mode, whisper detection, etc.). This file was **out of scope** for this task but should be flagged for future review or marked as "future state design."

2. **notes_and_feedback.md**: The feedback about keyboard noise has been incorporated into the status quo scenario understanding - the scenario now correctly shows that typing on touchscreen in the dark is difficult (not because of noise, but because of darkness and cognitive load).

---

## Implementation Complete

**Files Modified**: 3
- `requirements_user_needs/personas/max_client/persona.md` (updated)
- `requirements_user_needs/personas/max_client/scenarios/brain_dump_at_night/scenario.md` (rewritten)
- `requirements_user_needs/personas/max_client/scenarios/forgotten_protocol_transfer/scenario.md` (created)

**All quality criteria verified.**

---

**Agent**: implementation-engineer-2026-01-26-001
**Completed**: 2026-01-26
