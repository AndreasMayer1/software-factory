# Protocol: Elias Persona Modification - Brain Dump Addition

**Date**: 2026-02-02
**Agent**: modify-user-needs skill
**Task**: TASK-PROC-011-07
**Artifact Modified**: PERSONA-009 (Elias - The Skeptical Guardian)

---

## Objective

Add brain dump journaling behavior to Elias persona based on user research findings. Document that Elias maintains dual tracking: structured anxiety protocol (therapy homework) and unstructured brain dump (private).

---

## User Research Summary

From goal.md:
- Elias (anxiety disorder patient) maintains TWO tracking behaviors
- **Structured anxiety protocol**: Exposure exercise tracking (therapy homework) - shared with therapist
- **Unstructured brain dump**: Private free-form journaling - NOT shared with therapist
- Privacy distinction is critical: brain dump is private by default, but voluntary selective sharing should be possible

---

## Modifications Applied

### 1. Jobs to Be Done - Functional
**Added**:
- "Process overwhelming thoughts and emotions privately (brain dump)" 🟢

### 2. Jobs to Be Done - Emotional
**Added**:
- "Externalize intrusive thoughts without creating discoverable records" 🟢
- "Maintain clear boundary between therapy content and private content" 🟢

### 3. Current Status Quo
**Expanded**: Documented dual tracking system
- **Therapy homework**: Bright blue "THERAPY JOURNAL" notebook (existing)
- **Private brain dump**: Plain black notebook or phone Notes app (NEW)
- Emphasized privacy separation: brain dump is purely for himself, not for therapist

### 4. What Doesn't Work - Pain Points
**Added**:
- "**Dual system overhead**: Maintaining two separate notebooks/systems creates cognitive load and increases chance of mixing them up or losing one" 🟢
- "**Privacy anxiety spillover**: Even his private brain dump notebook triggers paranoia - what if someone sees it and assumes it's therapy-related? The stigma contaminates everything." 🟢

### 5. Trigger & Context Table
**Added row**:
| Trigger | State | Environment |
|---------|-------|-------------|
| Overwhelming anxious thoughts (private) | High emotional distress, rumination spiral | Private space (home, locked room) |

### 6. Barriers - Fears
**Added**:
- "**Boundary violation**: Private journaling being mistaken for therapy content, or accidentally sharing raw personal thoughts with therapist" 🟢

---

## Evidence Level

All new content marked with 🟢 [Data-Grounded: User research TASK-PROC-011-07]

This reflects that the brain dump behavior comes from validated user research, not assumptions.

---

## Metadata Updates

**YAML Frontmatter Changes**:
- `version`: 1.0 → 1.1 (minor content addition)
- `updated`: 2026-01-31 → 2026-02-02
- `review_status`: draft → in_review (requires review after significant additions)
- `review_history`: Added entry documenting user research and modifications

---

## Status Quo Compliance

**Validation**: All modifications describe current state (pre-app) correctly:
- ✅ Documents existing tools (physical notebooks, phone Notes app)
- ✅ Describes current dual system and its friction
- ✅ No app features or solution language
- ✅ Pain points grounded in real limitations of current approach

**User correction applied**: Removed solution-oriented language ("no clear way to mark content") and replaced with status quo description (maintains two separate systems with associated overhead).

---

## Impact Analysis

**Downstream Scenarios**: None exist yet for Elias (no impact)

**Upstream Dependencies**: None (personas are top-level)

**Related Personas**: This dual tracking pattern (therapy homework + private journaling) likely applies to:
- Jana (PERSONA-008): BPD, might journal crisis moments privately while tracking skills usage for therapist
- Sophie (PERSONA-010): ADHD, might brain dump hyperfocus thoughts while tracking medication/sleep for therapist

**Recommendation**: Investigate whether Jana and Sophie also exhibit this dual behavior pattern.

---

## Quality Checks

- [x] YAML frontmatter valid and complete
- [x] Review status set to `in_review`
- [x] Review history entry added with clear notes
- [x] Version incremented appropriately (1.0 → 1.1)
- [x] Evidence markers present for new content (🟢)
- [x] No broken cross-references introduced
- [x] Status quo compliance maintained (no solution language)
- [x] Technology neutrality preserved

---

## Acceptance Criteria Status

From goal.md:

- [x] Elias persona includes brain dump journaling behavior in "Current Status Quo"
- [x] "What doesn't work" section explains why current brain dump solution is inadequate
- [x] "Jobs to Be Done" reflects need for both structured tracking and unstructured journaling
- [x] Privacy distinction between therapy content and private content is explicit
- [x] "Barriers" section includes fear of accidental sharing of private content
- [x] Optional voluntary sharing capability is mentioned (in goal context, not persona - correct per status quo rules)
- [x] All changes maintain existing persona voice and structure
- [x] Version number incremented, review_history updated

---

## Next Steps

1. **User Review**: User should review modifications and approve
2. **Change review_status to approved**: Once user confirms accuracy
3. **Consider creating scenario**: A scenario showcasing Elias's dual tracking behavior
4. **Investigate other personas**: Check if Jana/Sophie also need brain dump additions
5. **Derive functional requirements**: Create requirements for app's privacy/sharing system based on this persona update

---

## Files Modified

- `requirements_user_needs/personas/elias_skeptical_guardian/persona.md`
  - Version: 1.0 → 1.1
  - Status: draft → in_review
  - Lines modified: ~20 additions across 6 sections

---

**Modification Complete**: 2026-02-02
**Protocol Written By**: modify-user-needs skill
**Ready for User Review**: Yes
