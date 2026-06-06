---
date: 2026-03-01
version: 01
type: plan
task_id: TASK-PROC-026-06
agent_id: architecture-advisor-sonnet-4-6-2026-03-01-T6
---

# Annotation Strategy Plan: Retroactive Persona Justifications for 13 Design System Requirements

## Overview

This plan defines the annotation structure, template, persona-mapping strategy, and
annotation order for adding persona justifications and tier classifications to all 13
existing design system requirement files.

The files themselves are NOT changed in their rules. Only new sections are added to
document who is served by each rule and why.

**Output**: 13 modified requirement files in `requirements_tasks/non-functional/ui_ux_design_system/`

**Primary source for mappings**: `doc/presentation/design/persona_design_bridge.md` (Section 1 trait table)

---

## 1. Annotation Structure

### Where in Each File

Each requirement file uses a numbered section heading pattern (e.g., `## 1. Overview`,
`## 7. Acceptance Criteria`). The annotation block is added as a **new section at the
END of the file, before the Version History block**.

Why at the end: The rules, acceptance criteria, and implementation details are the
primary content that developers read. The annotation is secondary context for
traceability. Inserting it at the end avoids disrupting established section numbering
and does not interfere with existing references to sections by number.

The section heading number follows the last numbered section in each file. For example,
if a file ends at `## 10. References`, the annotation goes in as `## 11. Persona
Justifications`.

**Exception**: Files that use unnumbered headings (main_navigation, in_detail_navigation,
responsive_layout_master_detail) — these use different section patterns. For these, add
the annotation block before the final `---` separator and the Version History block,
using the same unnumbered `## Persona Justifications` heading.

### Version History Block

The Version History block is always the last block in every file. The annotation section
is inserted ABOVE it, not below it.

---

## 2. Annotation Template

The following template is used for EVERY file. All four subsections are required.

```markdown
## [N]. Persona Justifications

**Tier**: [T1 | T2]
**Provenance**: Pre-Framework, Human-Defined

### Who This Serves

| Persona | Trait Category | Key Design Connection |
|---------|---------------|----------------------|
| PERSONA-XXX (Name): [brief trait] | [Trait category name] | [What requirement rule this trait drives] |
| ... | ... | ... |

### Why These Rules Exist (Trait Summary)

[2-4 sentences connecting the dominant trait categories to the most important rules
in this specific requirement. Plain prose. No lists. Written for a future developer
or AI who asks "why does this rule exist?"]

### Conflicts and Trade-offs

[Either: "No significant persona conflicts." OR a brief note on any known tension
between personas served differently by this requirement's rules.]
```

**Notes on the template**:
- The "Who This Serves" table uses PERSONA-IDs, not just names.
- Trait category names match exactly the 8 categories in `persona_design_bridge.md` Section 1.
- The "Why These Rules Exist" text is the armor against future rule weakening.
- The "Conflicts and Trade-offs" section prevents silent removal of rules that serve a minority persona.

---

## 3. Tier Classification for All 13 Files

Based on reading each requirement and applying the T1/T2 definition from the bridge document:

- **T1 (System-level)**: Universal constraint that applies across ALL screens.
- **T2 (Pattern-level)**: Rules for a recurring pattern across 2+ screens, but not universal.

| Requirement File | Tier | Classification Reasoning |
|-----------------|------|--------------------------|
| `accessibility/requirements.md` | T1 | Touch targets (48dp), WCAG AA, Simple Mode — these apply to every interactive element in the app |
| `ux_writing/requirements.md` | T1 | Tone, language patterns, error message format — applies to every string in the app |
| `loading_error_handling/requirements.md` | T1/T2 | Loading timing rules (T1: universal), confirmation dialog pattern (T2: destructive-action screens). File gets T1 as primary + note on T2 sub-rules |
| `theming/growth_tree_theme/requirements.md` | T1 | The theme system itself is the global design system — every component references it |
| `navigation_patterns/main_navigation/requirements.md` | T2 | Defines the application shell pattern; it's a recurring structural pattern, not a per-screen universal rule |
| `navigation_patterns/in_detail_navigation/requirements.md` | T2 | Adaptive overlay pattern used in multiple features but not on every screen |
| `navigation_patterns/responsive_layout_master_detail/requirements.md` | T2 | Master-detail pattern used wherever lists of domain entities exist |
| `components/collapsible_form_section/requirements.md` | T2 | Progressive disclosure component used in multiple forms but not universally |
| `components/context_help/requirements.md` | T2 | Used in multiple screens but not every screen |
| `components/leaf_popout/requirements.md` | T2 | Component used across multiple features but not a system-universal rule |
| `components/skeleton/requirements.md` | T2 | Loading placeholder pattern for initial content loads |
| `components/toast/requirements.md` | T2 | Error/success feedback component pattern (not on every screen, but recurring) |
| `components/time_range_selector/requirements.md` | T2 | Date/time input pattern for analytics/reporting screens |

**Note on loading_error_handling T1/T2**: The timing thresholds (<300ms, 300ms-2s) and
the "errors MUST always be displayed" rule are T1 (universal). The confirmation dialog
sub-pattern is T2. The file will be annotated as T1 with an inline note that the
confirmation dialog section follows T2 scope.

---

## 4. Persona-to-Requirement Mapping

This section defines which personas and trait categories apply to each of the 13 files.
The implementation engineer uses this mapping to fill the "Who This Serves" table without
needing to re-analyze each requirement.

### T1 Files (Universal Rules)

#### accessibility/requirements.md

| Persona | Trait Category | Key Design Connection |
|---------|---------------|----------------------|
| PERSONA-014 (Jana): hands shake during crisis | Motor constraints | 48dp minimum touch target requirement |
| PERSONA-010 (Sophie): motor imprecision, input paralysis | Motor constraints + Cognitive load | 48dp targets + Simple Mode toggle |
| PERSONA-013 (Nina): fatigue-reduced coordination on bad days | Motor constraints | 48dp minimum touch target requirement |
| PERSONA-002 (Max): cognitive load overwhelm | Cognitive load | Simple Mode removes visual complexity |
| PERSONA-007 (Hanna): WCAG contrast needed in dark environments | Environmental light | WCAG AA contrast requirements |
| All client personas | Motor constraints + Cognitive load | Universal: accessibility benefits all users with varying abilities |

**Why these rules**: Touch target minimums come directly from motor constraint personas.
Simple Mode was explicitly designed for the Sophie cluster (seniors, users with reduced
motor precision). WCAG AA contrast serves both the low-vision users (Phase 2) and
environmental light users (Hanna, Lisa, Lena) who need readable screens in non-ideal light.

**Conflicts**: None. All accessibility rules benefit all users with no known adverse effects.

---

#### ux_writing/requirements.md

| Persona | Trait Category | Key Design Connection |
|---------|---------------|----------------------|
| PERSONA-002 (Max): shame from failure language | Emotional sensitivity | No guilt language, empathetic tone |
| PERSONA-008 (David): shame-spiral risk from negative framing | Emotional sensitivity | Positive framing requirement |
| PERSONA-014 (Jana): shame after crisis episodes | Emotional sensitivity | No triggering terms, empathetic tone |
| PERSONA-010 (Sophie): emotional fragility with streaks | Emotional sensitivity | No judgmental language |
| PERSONA-013 (Nina): fatigue makes ambiguous text worse | Cognitive load | Simple language, short sentences |
| PERSONA-008 (David): 3-tap mental model | Cognitive load | Concrete actions, no abstract concepts |
| All users in mental health context | Emotional sensitivity | Sensitive context = no triggering terms |

**Why these rules**: The mental health context of this app means language errors have
heightened consequences. Standard UX writing advice (be clear, be direct) gains urgency
when the subject matter is mental health. Personas like Max, David, and Jana have
explicit traits around emotional sensitivity to failure-framing language.

**Conflicts**: Empathetic tone vs. not being patronizing — the guidelines address this
explicitly in section 4.4. The balance is respecting user autonomy while maintaining
warmth.

---

#### loading_error_handling/requirements.md

**Primary Tier**: T1 (timing rules and error visibility are universal)
**Sub-rule Tier**: T2 for confirmation dialog pattern (applies to destructive-action screens)

| Persona | Trait Category | Key Design Connection |
|---------|---------------|----------------------|
| PERSONA-008 (David): <3 taps, 3-second window | Time-to-capture | <300ms no indicator (avoid friction), timing thresholds |
| PERSONA-013 (Nina): loading state anxiety on bad cognitive days | Cognitive load | Skeleton loading maintains layout, reduces reorientation cost |
| PERSONA-014 (Jana): crisis = seconds, no room for error | Time-to-capture + Motor constraints | Confirmation dialogs prevent accidental destructive actions |
| PERSONA-002 (Max): shame/paralysis from errors | Emotional sensitivity | Always display errors with actionable message (no silent failures) |
| PERSONA-010 (Sophie): overwhelm from unexpected states | Cognitive load | Skeleton maintains layout stability, no surprises |

**Why these rules**: The <300ms threshold exists because showing a loading indicator
for a fast operation creates more cognitive disruption than the wait itself — David's
strict time-to-capture window makes this acutely important. The "errors MUST always be
displayed" rule prevents Max (and others with anxiety) from being left in an unknown
state. Confirmation dialogs compensate for the absence of an undo function (MVP
constraint), protecting Jana and others during high-stress moments.

**Conflicts**: Timing rule favors speed (David) vs. confirmation dialogs add a step
(Jana in crisis). Resolution: confirmation dialogs apply only to irreversible destructive
actions, not to normal operations.

---

#### theming/growth_tree_theme/requirements.md

| Persona | Trait Category | Key Design Connection |
|---------|---------------|----------------------|
| PERSONA-007 (Hanna): "White/bright apps are unusable", partner asleep | Environmental light + Privacy/discreteness | Dark mode requirement, discrete appearance |
| PERSONA-009 (Elias): therapy notebook appearance screams therapy | Privacy/discreteness | Non-clinical app identity, Simple Mode option |
| PERSONA-006 (Michael): cannot use mental health app at work | Privacy/discreteness | Neutral color palette, non-clinical icon |
| PERSONA-010 (Sophie): Simple Mode for seniors/users preferring minimal UI | Cognitive load + Motor constraints | Simple Mode (no organic graphics) requirement |
| PERSONA-002 (Max): complex visual themes increase cognitive load | Cognitive load | Simple Mode option |
| PERSONA-005 (Lisa): privacy from roommates + late-night usage | Privacy/discreteness + Environmental light | Dark mode + discrete appearance |

**Why these rules**: The Growth/Tree theme establishes the app's identity — positive,
non-clinical, non-wellness-pastel, associated with growth. Simple Mode exists because
the tree theme's organic complexity is wrong for users with cognitive or motor constraints
(Sophie cluster) and for users who need maximum discreteness (Elias, Michael). Dark mode
is not a nice-to-have: Hanna cannot use a bright app in her usage context.

**Conflicts**: Tree Theme (distinctive, memorable identity) vs. Discreteness need
(Elias, Michael). Resolution: Simple Mode + non-clinical icon are the discreteness
mitigation. The growth metaphor itself is not clinical.

---

### T2 Files (Pattern Rules)

#### navigation_patterns/main_navigation/requirements.md

| Persona | Trait Category | Key Design Connection |
|---------|---------------|----------------------|
| PERSONA-001 (Dr. Sarah): Windows desktop, efficient workflow | Sensory/environmental adaptation | Large-screen Navigation Rail (not BottomNav) |
| PERSONA-012 (Dr. Turan): "3 minutes to decide", needs dense scan | Data density + Time-to-capture | Navigation structure enables quick section switching |
| PERSONA-011 (Prof. Weber): desktop office context | Sensory/environmental adaptation | Responsive navigation adapts to desktop |
| PERSONA-008 (David): <=3 taps to complete action | Time-to-capture | Bottom nav pattern ensures critical sections reachable in 1 tap |

**Why these rules**: Navigation is the primary wayfinding structure. Therapist personas
(Dr. Sarah, Dr. Turan, Prof. Weber) use desktops — the Navigation Rail pattern makes
this professional workflow efficient. Client personas (David, Hanna, Jana) need critical
sections reachable in minimum taps — the bottom navigation on mobile achieves this.

**Conflicts**: No significant conflicts. The adaptive pattern (BottomNav on mobile,
Rail on larger) serves both user groups.

---

#### navigation_patterns/in_detail_navigation/requirements.md

| Persona | Trait Category | Key Design Connection |
|---------|---------------|----------------------|
| PERSONA-001 (Dr. Sarah): desktop usage, efficient sub-element navigation | Sensory/environmental adaptation | Side sheet on large screens maintains therapist workflow context |
| PERSONA-012 (Dr. Turan): 3-minute decision window | Time-to-capture + Data density | Side sheet on desktop keeps parent context visible alongside detail |
| PERSONA-014 (Jana): crisis = seconds, no complex navigation | Time-to-capture + Motor constraints | Full-screen dialog on mobile = clear focused interaction |
| PERSONA-008 (David): fewer taps | Time-to-capture | Adaptive overlay avoids navigation away from parent (no back-nav cost) |

**Why these rules**: The adaptive overlay pattern keeps users in context — therapists
on desktop see both the list and the detail side-by-side. Client users on mobile get a
clear full-screen for focused editing. This avoids forcing context-switching on users
(especially David and Jana) who cannot afford the cognitive cost of re-orienting after
navigating away.

**Conflicts**: No significant conflicts. Screen-size adaptation handles the different
needs.

---

#### navigation_patterns/responsive_layout_master_detail/requirements.md

| Persona | Trait Category | Key Design Connection |
|---------|---------------|----------------------|
| PERSONA-001 (Dr. Sarah): desktop, parallel scan of list + detail | Sensory/environmental adaptation + Data density | Master-detail side-by-side on large screens |
| PERSONA-012 (Dr. Turan): 3-minute decision window, dense scan | Data density + Time-to-capture | Auto-selection on large screens avoids extra tap to open first item |
| PERSONA-008 (David): every tap costs attention budget | Time-to-capture | Auto-selection rule reduces steps to first item |
| PERSONA-011 (Prof. Weber): desktop professional context | Sensory/environmental adaptation | Desktop layout respects professional workflow |

**Why these rules**: The master-detail pattern maximizes information density for
therapist users who scan many entities (clients, plans) in parallel. The auto-selection
rule on large screens saves one tap for therapist power users without adding confusion
for mobile users (disabled on small/medium screens).

**Conflicts**: Data density (therapist need: dense) vs. simplicity (client need: minimal).
Resolution: master-detail is used primarily for therapist-facing screens. Client-facing
screens use simpler linear navigation.

---

#### components/collapsible_form_section/requirements.md

| Persona | Trait Category | Key Design Connection |
|---------|---------------|----------------------|
| PERSONA-002 (Max): "White Sheet Syndrome" — blank forms overwhelm | Cognitive load | Hide optional fields by default, reduce visible form complexity |
| PERSONA-008 (David): "Wall of Awful" — large forms trigger avoidance | Cognitive load | Progressive disclosure — essential fields visible, rest collapsed |
| PERSONA-010 (Sophie): open-ended questions trigger paralysis | Cognitive load | Collapse advanced/optional options until user requests them |
| PERSONA-014 (Jana): tunnel vision in crisis — only critical options | Cognitive load + Time-to-capture | Collapsed sections means fewer distractions on critical paths |

**Why these rules**: Progressive disclosure via collapsible sections is a direct
mitigation for cognitive load personas. Showing all options at once triggers overwhelm
(Max's "White Sheet Syndrome", David's "Wall of Awful"). The component exists precisely
to let users who need simplicity skip optional fields without encountering them.

**Conflicts**: No conflicts. All personas benefit from reduced complexity. Advanced users
can still expand sections.

---

#### components/context_help/requirements.md

| Persona | Trait Category | Key Design Connection |
|---------|---------------|----------------------|
| PERSONA-002 (Max): needs scaffolding to avoid blank-field paralysis | Cognitive load | Context help reduces uncertainty about what fields mean |
| PERSONA-010 (Sophie): open-ended questions trigger overwhelm | Cognitive load | Help text explains purpose without requiring prior knowledge |
| PERSONA-013 (Nina): brain fog makes unfamiliar UI confusing | Cognitive load | Context help available without leaving screen |
| PERSONA-014 (Jana): crisis state — help must be reachable without navigation | Time-to-capture + Cognitive load | Help is inline (no navigation to help screen needed) |

**Why these rules**: Context help is available without leaving the current screen,
which is critical for users with cognitive load constraints (Max, Sophie, Nina) who
cannot afford the reorientation cost of navigating to a help section and back.
The 48dp touch target requirement ensures Jana and Sophie can trigger help even with
motor constraints.

**Conflicts**: No conflicts.

---

#### components/leaf_popout/requirements.md

| Persona | Trait Category | Key Design Connection |
|---------|---------------|----------------------|
| PERSONA-009 (Elias): app must not look clinical in public | Privacy/discreteness | Organic leaf visual is brand-distinctive, not clinical/medical |
| PERSONA-010 (Sophie): Simple Mode preference | Cognitive load | Simple Mode fallback to standard Material popout |
| PERSONA-002 (Max): organic visual metaphors align with growth/tree theme | Cognitive load | Consistent theme reduces relearning cost |
| PERSONA-014 (Jana): touch target for dismiss must meet 48dp | Motor constraints | Dismiss (tap outside) pattern is large-area, no precise targeting required |

**Why these rules**: The leaf-shaped popout is a brand-identity element — it makes the
app look like a growth/garden tool, not a medical tracker. This directly serves the
privacy/discreteness need (Elias, Michael, Lisa). Simple Mode fallback ensures the
organic visual doesn't impose complexity on users who opted out of it.

**Conflicts**: Organic animation (Tree Theme) vs. cognitive simplicity. Resolution:
Simple Mode replaces organic animation with standard Material fade for users who chose it.

---

#### components/skeleton/requirements.md

| Persona | Trait Category | Key Design Connection |
|---------|---------------|----------------------|
| PERSONA-013 (Nina): brain fog — unexpected blank screens are disorienting | Cognitive load | Skeleton maintains layout continuity during load |
| PERSONA-008 (David): any disruption to flow breaks the attention thread | Cognitive load + Time-to-capture | Skeleton prevents the "app is broken?" moment |
| PERSONA-010 (Sophie): unexpected states trigger overwhelm | Cognitive load | Skeleton sets correct layout expectations before content arrives |
| PERSONA-007 (Hanna): 3 AM usage — disorientation from blank screens is worse | Time-to-capture | Skeleton reduces time-to-useful-state perception |

**Why these rules**: The skeleton's "no layout shift" rule is not aesthetic — it is
a cognitive load mitigation. Users like Nina (brain fog) and David (ADHD) lose their
place when content appears and suddenly moves other elements around. The skeleton
prevents this. The same appearance in both Tree Theme and Simple Mode ensures the
loading state is not a jarring contrast.

**Conflicts**: No conflicts.

---

#### components/toast/requirements.md

| Persona | Trait Category | Key Design Connection |
|---------|---------------|----------------------|
| PERSONA-002 (Max): error messages must have actionable next step | Emotional sensitivity + Cognitive load | Two-part error message pattern (what happened + what to do) |
| PERSONA-008 (David): errors must not create spiral | Emotional sensitivity | Empathetic, non-blaming error message content |
| PERSONA-014 (Jana): errors in crisis must be scannable instantly | Time-to-capture + Motor constraints | Simple fade-in (no organic animation), swipe dismiss |
| PERSONA-013 (Nina): repeated errors amplify cognitive fatigue | Cognitive load | Auto-dismiss (4s) prevents persistent anxiety-inducing message |

**Why these rules**: The intentional absence of organic animation in Toast is
significant — it was explicitly chosen (requirement section 3.2) because error states
require rapid comprehension. Decorative animation slows reading in stress. The two-part
message structure aligns with UX Writing Guidelines and ensures Max and David get a
clear path forward rather than a dead-end error message.

**Conflicts**: Auto-dismiss (4s) may be too fast for some cognitive load users. Mitigated
by the swipe-to-dismiss alternative (manual control) and the "maximum 1 visible at a time"
rule (no stacking anxiety).

---

#### components/time_range_selector/requirements.md

| Persona | Trait Category | Key Design Connection |
|---------|---------------|----------------------|
| PERSONA-008 (David): time-to-capture is <3 taps | Time-to-capture | BottomSheet on mobile (one swipe to open, no navigation) |
| PERSONA-012 (Dr. Turan): dense scan, 3-minute window | Data density + Time-to-capture | Dialog on desktop enables efficient date range selection in context |
| PERSONA-001 (Dr. Sarah): desktop-first workflow | Sensory/environmental adaptation | Dialog presentation on desktop fits professional workflow |
| PERSONA-014 (Jana): 48dp touch targets in all states | Motor constraints | Touch target minimum applies to all weekday toggles and controls |

**Why these rules**: The adaptive presentation (BottomSheet on mobile, Dialog on
desktop) matches usage context. Therapist users (Dr. Turan, Dr. Sarah) access this
component on desktop during a brief appointment window — the Dialog gives them full
context without covering other content. The 48dp touch target requirement is a T1 rule
applied here — the weekday toggle buttons are particularly small by default and must
be explicitly overridden.

**Conflicts**: No conflicts.

---

## 5. Annotation Order

The 13 files are annotated in this order, designed to handle dependencies and build
momentum with the clearest mappings first:

**Wave 1 — T1 files (foundations)**:
1. `accessibility/requirements.md` — Simplest mapping; persona connections are most obvious
2. `ux_writing/requirements.md` — Emotional sensitivity mapping; builds tone for the rest
3. `theming/growth_tree_theme/requirements.md` — Privacy + dark mode; clear trait connections
4. `loading_error_handling/requirements.md` — Most complex (T1 + T2 sub-rules); do after simpler T1s

**Wave 2 — T2 navigation patterns**:
5. `navigation_patterns/main_navigation/requirements.md` — Foundation for in-detail and master-detail
6. `navigation_patterns/responsive_layout_master_detail/requirements.md` — Builds on main navigation context
7. `navigation_patterns/in_detail_navigation/requirements.md` — Uses context from both navigation files

**Wave 3 — T2 components (simpler mappings)**:
8. `components/skeleton/requirements.md` — Cognitive load; straightforward
9. `components/toast/requirements.md` — Emotional sensitivity; straightforward
10. `components/collapsible_form_section/requirements.md` — Cognitive load; well-defined purpose
11. `components/context_help/requirements.md` — Cognitive load; depends on leaf_popout concept
12. `components/leaf_popout/requirements.md` — Privacy + brand; more judgment required
13. `components/time_range_selector/requirements.md` — Most niche; do last

**Rationale for order**: T1 files first because their universal scope makes judgment
easier (if it's T1, every persona feels it). Navigation patterns before components
because the master-detail/adaptive patterns inform why certain component choices were
made. Components ordered from most obvious (skeleton, toast) to most requiring judgment
(leaf_popout design intent, time_range_selector scope).

---

## 6. Key Decisions and Trade-offs

### Decision 1: Annotation Goes at End, Not at Top

**Options considered**:
A. Add annotation block at the TOP of the file (before main content)
B. Add annotation block at the END (before Version History)
C. Embed per-rule annotations inline throughout the file

**Choice**: Option B (end of file).

**Why**: These are retroactive annotations on files with established section numbering.
Option A would require re-numbering all sections. Option C would bury persona context
inside technical spec sections where developers don't expect it. Option B is non-disruptive
and creates a single canonical location for traceability lookup.

### Decision 2: Section Heading Numbered vs Unnumbered

**For files with numbered sections** (most files): Use the next sequential number.

**For files with unnumbered sections** (main_navigation, in_detail_navigation,
responsive_layout_master_detail — these use `## Overview`, `## Implementation`, etc.):
Use `## Persona Justifications` (unnumbered, matching the file's existing style).

**Why**: Consistency within each file's existing convention is more important than
cross-file uniformity.

### Decision 3: No Per-Rule PERSONA-ID Annotations (Only Section-Level)

**Options considered**:
A. Annotate individual rules with PERSONA-IDs inline (e.g., `> PERSONA-014: 48dp minimum`)
B. Single "Persona Justifications" section at end of file

**Choice**: Option B (section-level).

**Why**: Inline per-rule annotations would make the requirement files significantly
harder to read for developers. The persona justification section serves a different
audience (traceability reviewers, future AI agents doing retroactive analysis) than the
main content (implementing developers). Separation of concerns.

### Decision 4: What "Pre-Framework, Human-Defined" Means

The provenance marker `Pre-Framework, Human-Defined` means:
1. These rules PREDATE the persona-design bridge methodology (created before 2026-02-08).
2. They were defined by a human (not derived by AI from persona traits).
3. The annotation is RETROACTIVE — we are connecting existing rules to personas, not
   deriving new rules from personas.

This distinction matters because future annotations created AFTER the bridge methodology
will be marked differently (e.g., `AI-Derived, [date]` or `Human-Defined, [date]`).

### Decision 5: Trade-off Annotation for Narrow-Persona Rules

Some rules serve a narrow set of personas (e.g., Simple Mode primarily serves the
Sophie cluster and cognitive load personas). The "Conflicts and Trade-offs" subsection
is used to flag this explicitly so future agents do not incorrectly infer that a rule
serves ALL users and therefore conclude it's "over-engineered" if they don't see broad
persona coverage.

---

## 7. Risks

**Risk 1: Incorrect persona-to-rule connections**

Some connections require judgment (e.g., is Toast's "no organic animation" about
Time-to-capture or Cognitive load?). The bridge document provides the 8 categories as
the mapping framework, reducing but not eliminating subjectivity.

Mitigation: Use the exact phrasing from the bridge document's trait table. Flag
uncertain connections with a brief inline note.

**Risk 2: Missing a persona that applies**

With 13 personas and 13 files, exhaustive coverage cannot be guaranteed without reading
every persona file again.

Mitigation: The bridge document's Section 1 table (verified against all persona files
during TASK-PROC-026-03) is the authoritative source. This plan uses that table as the
mapping oracle. Additional persona-to-file connections found during implementation should
be added — the mapping in section 4 above is minimum coverage, not maximum.

**Risk 3: Disrupting existing file structure**

The files have established section numbering referenced in YAML frontmatter (for files
using `sections:` tracking items) and in cross-references from other files.

Mitigation: Annotations go at end of file. Section numbers for existing sections are
not changed. New section numbers are sequential from the last existing section.
Files using non-numbered sections use unnumbered `## Persona Justifications` heading.

**Risk 4: Version History block gets separated from end of file**

The annotation block is placed BEFORE Version History, not after. If implementation
places it after, Version History is no longer the final block.

Mitigation: Plan makes this explicit: "before the Version History block". Implementation
must verify position.

---

## 8. Files to Modify

All 13 files are in `requirements_tasks/non-functional/ui_ux_design_system/`:

```
accessibility/requirements.md
ux_writing/requirements.md
loading_error_handling/requirements.md
theming/growth_tree_theme/requirements.md
navigation_patterns/main_navigation/requirements.md
navigation_patterns/in_detail_navigation/requirements.md
navigation_patterns/responsive_layout_master_detail/requirements.md
components/collapsible_form_section/requirements.md
components/context_help/requirements.md
components/leaf_popout/requirements.md
components/skeleton/requirements.md
components/toast/requirements.md
components/time_range_selector/requirements.md
```

**No other files are modified by this task.**

The persona-design bridge document (`doc/presentation/design/persona_design_bridge.md`)
is read-only for this task. No doc/ files are modified.

---

## Log

- **Date**: 2026-03-01
- **Agent ID**: architecture-advisor-sonnet-4-6-2026-03-01-T6
- **Status**: Plan complete, awaiting user review and approval
- **Files read**:
  - `requirements_tasks/.../retroactive_requirement_annotation/goal.md`
  - `requirements_tasks/.../persona_design_bridge (completed)/plans_and_protocols/2026-03-01_01_plan_persona_design_bridge.md`
  - `doc/presentation/design/persona_design_bridge.md` (Sections 0, 5, 4, 1)
  - All 13 requirement files in `requirements_tasks/non-functional/ui_ux_design_system/`
- **Next action**: Implementation engineer reads this plan + goal.md, then modifies each
  file in the annotation order defined in Section 5 using the template in Section 2 and
  the persona mappings in Section 4.
