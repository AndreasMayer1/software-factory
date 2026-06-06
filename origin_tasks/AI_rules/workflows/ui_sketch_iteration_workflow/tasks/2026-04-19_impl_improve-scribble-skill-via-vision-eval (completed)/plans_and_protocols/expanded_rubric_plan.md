# Expanded Evaluation Rubric Plan
# ui-create-scribble-improve — Next Iteration Design

**Authored**: 2026-04-19
**Context**: All 3 fixtures scored 16/16 on first attempt. The current 8-criterion rubric is a presence-only
checklist. This plan designs a quality-sensitive replacement that cannot be trivially gamed.

---

## Why the Current Rubric Fails

Reading the evaluation YAMLs reveals the pattern: every criterion scores 2 because it asks "does X exist?"
not "is X correct?"

| Criterion | What scored 2 | Why it was too easy |
|-----------|--------------|---------------------|
| component_mapping_block | Block present, elements listed | Never checks if mapping is *accurate* |
| persona_constraints_annotated | PERSONA-IDs appear in comments | Never checks if constraint was *applied* in the HTML |
| wireframe_level | No #1976D2 hex colors | Never checks CSS complexity, real shadows, hover states |
| ac_coverage | Each AC mentioned in ≥1 screen | Never checks if the screen *demonstrates* the AC |
| flutter_widget_labels | [FilledButton] appears | Never checks if FilledButton is the *right choice* |
| screen_hierarchy_legible | Reviewer can follow structure | Subjective; generator always produces legible structure |
| flow_positions_metadata | Array present in metadata.yaml | Never checks step number accuracy |
| t1_t2_rules_applied | Rule IDs in comments | Never checks if the rule constraint is visible in the HTML |

The problem is that a generator agent that copies the component mapping block format verbatim and pastes
PERSONA-IDs into comments will score 16/16 without actually making correct design decisions.

---

## Design Principles for the New Rubric

1. **Every criterion must have an observable failure mode** — something a generator could plausibly get wrong
2. **Score 2 requires demonstrated correctness**, not mere presence
3. **Score 0 should be achievable** — if a fixture never scores 0 on a criterion, that criterion adds no signal
4. **Keep criteria independent** — avoid double-counting the same observable
5. **Cap at ~16 criteria** — beyond that, evaluators lose reliability (attention dilution)
6. **Total points: 32** — maintains 80% target at a meaningful threshold (25.6/32)

---

## Expanded Rubric: 16 Criteria, 32 Points Maximum

### DIMENSION A — Structural Completeness (refined from current 8, 12 points)

These retain the existing 8 criteria but tighten 0/1/2 to require demonstrated quality.

---

#### A1 — `component_mapping_block` (max 2 pts)

**What to check**: Each screen HTML file has a `<!-- COMPONENT MAPPING -->` block AND every interactive
element in the body has a corresponding mapping entry. Cross-reference: count distinct interactive HTML
elements in `<body>`, verify each appears in the mapping block.

| Score | Threshold |
|-------|-----------|
| 0 | Block absent from ≥1 screen file, OR ≥3 elements in body have no mapping entry |
| 1 | Block present in all files; 1–2 elements unmapped OR mapping uses wrong widget name (e.g. `ElevatedButton` instead of `FilledButton` for M3 primary action) |
| 2 | Block present in ALL files; EVERY interactive element mapped; all widget names use current M3 terminology (FilledButton not ElevatedButton, NavigationBar not BottomNavigationBar) |

**Generator skill change that improves a low score**: Add explicit instruction: "After writing each screen's
body, audit the COMPONENT MAPPING block — for every `<button>`, `<input>`, `<select>`, `<a>`, `<div
class='...-item'>` element in the body, verify it has a mapping entry using current M3 widget names."

---

#### A2 — `persona_constraints_applied` (max 2 pts)
*(renamed from `persona_constraints_annotated` — "applied" is the key word)*

**What to check**: For each PERSONA-ID cited in the component mapping block header, find at least one place
in the screen's HTML body where the constraint is visibly enforced — not just mentioned. Examples of
"visibly enforced": `min-height: 48px` style on a list item (PERSONA-014 tremors), plain-language label
text with no jargon (PERSONA-002 cognitive load), explicit absence of clinical wording (PERSONA-009
discrete identity).

| Score | Threshold |
|-------|-----------|
| 0 | PERSONA-IDs appear only in comments; no HTML structure or label text reflects any persona constraint |
| 1 | ≥1 persona constraint is visibly enforced in HTML; ≥1 cited persona has comment only, no HTML enforcement |
| 2 | EVERY cited persona has ≥1 observable enforcement in HTML body (style, label text, structural choice, or explicit structural absence) |

**Generator skill change**: Add instruction: "For each persona applied, identify their primary constraint
category (motor/cognitive/privacy/environmental). Then find the HTML element that must embody that constraint
and add the constraint to both the comment and the element's style or label text."

---

#### A3 — `wireframe_level` (max 2 pts)
*(same name, tighter definition)*

**What to check**: No production styling. Specifically: no hex colors outside greyscale range (#000–#fff
greyscale only — no saturation), no CSS `box-shadow` with visible blur, no CSS transitions or animations,
no `border-radius` above 16px (signals polished card design), no font-size declarations that replicate
MD3 type scale precisely (e.g., `font-size: 14px; letter-spacing: 0.0107em` is production-level).

| Score | Threshold |
|-------|-----------|
| 0 | Any saturated hex color (#1976D2, pastel pink, etc.) OR CSS animations OR box-shadow with visible elevation |
| 1 | Greyscale only; but uses highly specific pixel values that mimic production design (precise letter-spacing, exact MD3 type scale) OR uses border-radius >16px suggesting visual polish intent |
| 2 | Greyscale only; font sizes use round numbers (0.8rem, 1rem, 1.2rem); border-radius ≤12px; no shadows; no transitions |

**Generator skill change**: Add to MUST-NOT list: "Do not add `box-shadow`, `transition`, `animation`,
`letter-spacing` with decimal precision, or `border-radius` above 12px — these signal production polish intent,
not wireframe quality."

---

#### A4 — `ac_coverage_demonstrated` (max 2 pts)
*(renamed from `ac_coverage` — "demonstrated" is the key word)*

**What to check**: Each AC in requirements.md must be *demonstrated* in at least one screen, not merely
referenced in a comment. "Demonstrated" means: if AC-04 says "opt-in exclusion boundary," the screen
must visually show the boundary (e.g., a row stating entries excluded, an empty section with explanation)
— a comment saying `<!-- AC-04 covered here -->` without any body HTML showing it scores 0 for that AC.

| Score | Threshold |
|-------|-----------|
| 0 | ≥2 ACs have only a comment reference; no HTML body element demonstrates the AC |
| 1 | All ACs referenced; 1 AC has comment reference only without demonstrating HTML; OR 1 AC not referenced at all |
| 2 | Every AC has ≥1 HTML body element (label, input, state variant, structural absence) that visually demonstrates it |

**Generator skill change**: Add instruction: "Before finalizing a screen, list each AC it covers. For each
AC, identify the specific HTML element that makes the AC visible to a reviewer. If no such element exists,
add one."

---

#### A5 — `md3_widget_labels_correct` (max 2 pts)
*(replaces `flutter_widget_labels` — correctness not just presence)*

**What to check**: Labels present AND contextually correct per MD3 hierarchy. Specifically:
- Primary action on a screen → `[FilledButton]` not `[ElevatedButton]` or `[OutlinedButton]`
- Secondary action → `[OutlinedButton]` or `[TextButton]` (not `[FilledButton]`)
- Destructive action → `[TextButton]` (red) in dialog, never `[FilledButton]`
- Bottom navigation → `[NavigationBar]` not `[BottomNavigationBar]` (deprecated M2)
- List navigation items → `[NavigationDestination]` (child of NavigationBar)
- App bar → correct variant annotated: `[CenterAlignedTopAppBar]` for simple screens,
  `[LargeTopAppBar]` for content-dense screens

| Score | Threshold |
|-------|-----------|
| 0 | Widget labels absent from ≥2 screen files, OR uses M2 widget names (BottomNavigationBar, ElevatedButton for primary) |
| 1 | Labels present; 1–2 incorrect widget hierarchy choices (e.g. FilledButton for secondary action, or AppBar without variant annotation) |
| 2 | All interactive elements labelled; MD3 hierarchy correct: primary=Filled, secondary=Outlined/Text, nav=NavigationBar with NavigationDestination children, correct AppBar variant named |

**Generator skill change**: Add MD3 widget hierarchy table to Phase 1 instructions (see skill update
section below).

---

#### A6 — `screen_hierarchy_legible` (max 2 pts)
*(same name, tighter scoring — currently everyone scores 2)*

**What to check**: Information hierarchy is reflected in HTML heading levels AND visual weight. Check:
- Primary action button is the visually largest/most prominent button on screen
- HTML uses `<h1>`, `<h2>`, `<h3>` (or equivalent section-label + card hierarchy) that matches content importance
- Destructive actions are visually subordinate to primary actions (not same size/style)
- Section groupings use consistent structural patterns (all cards, or all sections — not mixed without reason)

| Score | Threshold |
|-------|-----------|
| 0 | Primary action and secondary action are indistinguishable in size/weight; OR heading levels used backward (h3 for primary label, h1 for footnote) |
| 1 | Clear primary/secondary distinction exists but ≥1 screen has destructive action styled same as primary OR section nesting is inconsistent across screens |
| 2 | Every screen: primary action most prominent; secondary visually subordinate; destructive distinguishable; heading levels correctly reflect content hierarchy |

---

#### A7 — `flow_positions_accuracy` (max 2 pts)
*(replaces `flow_positions_metadata` — accuracy not just presence)*

**What to check**: If requirement has no flow reference → skip (score 2 automatically, not applicable).
If flow reference exists: (a) `flow_positions[]` present in metadata.yaml, (b) step_numbers are plausible
given the flow's documented steps (not all 0 or null), (c) each screen file cited in flow_positions
actually exists in the scribble folder.

| Score | Threshold |
|-------|-----------|
| 0 | flow_positions absent when requirement has flow reference; OR ≥2 cited screen files don't exist |
| 1 | flow_positions present; step_numbers are null/placeholder for ≥1 entry that has a known flow step; OR 1 cited file missing |
| 2 | flow_positions present; all step_numbers are non-null integers or have documented rationale for null; all cited files exist |

---

#### A8 — `t1_t2_rules_enforced` (max 2 pts) — replaces `t1_t2_rules_applied`
*(same name change pattern — enforced means visible constraint, not comment)*

**What to check**: For each T1/T2 rule cited in the component mapping block, find observable enforcement
in the HTML body. Enforcement examples:
- `t1_touch_targets`: every interactive element has `min-height: 48px` in style
- `t1_dark_mode`: if requirement serves PERSONA-007, dark backgrounds used (greyscale dark, not #f5f5f5)
- `t2_destructive_actions`: destructive buttons placed outside primary action row (dashed overlay panel shown)
- `t1_interaction_budget`: no "Save" button on auto-save screens

| Score | Threshold |
|-------|-----------|
| 0 | Rule IDs appear only in comments; body HTML shows no evidence of the rule constraint |
| 1 | ≥1 rule has visible enforcement; ≥1 cited rule has comment only with contradicting HTML (e.g. cites t1_touch_targets but a button has `height: 32px`) |
| 2 | Every cited rule has ≥1 observable enforcement point in body HTML; no rule cited but contradicted by body styling |

---

### DIMENSION B — MD3 Widget Appropriateness (new, 4 points)

---

#### B1 — `md3_navigation_pattern` (max 2 pts)

**What to check**: Navigation widget choice matches the screen's structural context.
- App with ≤5 destinations on mobile → `[NavigationBar]` (bottom)
- App with >5 destinations or tablet layout → `[NavigationRail]` or `[NavigationDrawer]`
- Hierarchical navigation (detail screens, modals) → `[AppBar]` with back button, NOT NavigationBar
- Modal sheets → no navigation bar (full-screen modal doesn't repeat bottom nav)
- Tab-based sub-navigation within a destination → `[TabBar]` + `[TabBarView]`

| Score | Threshold |
|-------|-----------|
| 0 | NavigationBar appears on a modal/dialog screen; OR NavigationRail used on mobile single-column layout; OR tabs used for primary destinations instead of NavigationBar |
| 1 | Navigation widget choice is defensible but not optimal (e.g. NavigationBar with 6 destinations) |
| 2 | Every screen's navigation widget matches its structural role; modal screens have no repeated nav bar |

**Generator skill change**: Add navigation pattern decision table to Phase 1 instructions.

---

#### B2 — `md3_dialog_pattern` (max 2 pts)

**What to check**: When a dialog or confirmation overlay is shown:
- Confirmation with a single choice (yes/cancel) → `[AlertDialog]`
- Selection from a list of items → `[SimpleDialog]`
- Complex form input → `[ModalBottomSheet]`
- Destructive action confirmation → `[AlertDialog]` with TextButton (cancel) + FilledButton or ElevatedButton (confirm) — NOT two FilledButtons
- Dialog cancel button position: cancel/dismiss action comes FIRST in actions list (leftmost/topmost)

| Score | Threshold |
|-------|-----------|
| 0 | Any dialog shown but wrong type used (SimpleDialog for binary choice; AlertDialog for list selection); OR destructive confirmation uses two FilledButtons |
| 1 | Dialog type correct but cancel/dismiss button not positioned first in actions |
| 2 | All dialogs use correct type; cancel comes first; destructive confirm uses appropriate button style |

**Generator skill change**: Add dialog pattern rules to Phase 1 instructions.

---

### DIMENSION C — State Coverage (new, 4 points)

---

#### C1 — `states_happy_and_empty` (max 2 pts)

**What to check**: Every screen that displays a list or collection must show both:
1. A populated state (happy path — the default screen)
2. An empty state (first use, zero items) — either as a separate screen file or as an annotated
   sub-panel within the screen (dashed overlay panel pattern from existing scribbles)

Empty state must include: an explanation of why it's empty AND a call-to-action to populate it.

| Score | Threshold |
|-------|-----------|
| 0 | List/collection screens show populated state only; no empty state variant shown or annotated |
| 1 | Empty state shown for some but not all list screens; OR empty state shown without a call-to-action |
| 2 | Every list/collection screen has both populated and empty state; empty state has explanation + CTA |

**Generator skill change**: Add to MUST-DO list: "For every screen that shows a list or collection,
include an empty state variant as an annotated dashed overlay panel below the screen, showing what the
screen looks like on first use with zero items."

---

#### C2 — `states_loading_and_error` (max 2 pts)

**What to check**: Every screen that performs async operations (loading data, submitting a form, waiting
for QR scan, initiating transfer) must show:
1. A loading state (progress indicator, skeleton, or annotated loading placeholder)
2. An error state (network failure, validation error, or operation failure) with plain-language message
   and recovery action

Error message language must be plain (no "Error 403", no "IOException", no technical codes).

| Score | Threshold |
|-------|-----------|
| 0 | Async screens show only success state; no loading or error variant shown |
| 1 | Loading state shown but no error state; OR error state present but uses technical error language ("Connection refused", error codes) |
| 2 | Both loading and error states shown for every async screen; error messages in plain language with recovery action (retry, go back, contact support) |

**Generator skill change**: Add to MUST-DO list: "For every screen that involves a wait (QR scan, data
load, transfer in progress), add a loading state panel and an error state panel as annotated overlays.
Error messages must be written in plain language: 'Something went wrong — tap to try again' not 'Error 503'."

---

### DIMENSION D — Accessibility Annotations (new, 6 points)

Note: At wireframe level, accessibility means *annotating intent*, not implementing ARIA. The evaluator
checks for structured HTML comments that make a11y intent explicit for the implementation agent.

---

#### D1 — `a11y_semantic_roles` (max 2 pts)

**What to check**: Interactive elements that are NOT standard HTML buttons/inputs (i.e., custom `<div>`
elements styled as buttons, toggles, cards with tap actions) have a semantic role annotation:
`<!-- aria: role=button, label="Accept transfer" -->` or similar.
Standard `<button>` and `<input>` elements do not need this — their HTML semantics are sufficient.
Also check: decorative vs informative image distinction annotated for any icon/image placeholders.

| Score | Threshold |
|-------|-----------|
| 0 | ≥3 custom div-as-interactive-element have no semantic role annotation |
| 1 | Most custom interactive elements annotated; 1–2 missing; OR icons not distinguished (decorative vs informative) |
| 2 | All custom interactive elements have `<!-- aria: role=..., label="..." -->` annotation; icon placeholders marked as decorative or informative |

**Generator skill change**: Add to component mapping block instructions: "For each custom div element
that acts as a button, card, or interactive control, add `<!-- aria: role=button, label='[action]' -->`
immediately above the element. Mark icon placeholders with `<!-- icon: decorative -->` or
`<!-- icon: informative, label='[description]' -->`."

---

#### D2 — `a11y_easy_language` (max 2 pts)

**What to check**: For personas with documented cognitive constraints (blank-field paralysis, anxiety,
cognitive narrowing, low literacy signals in persona file) — check that:
- All label text in the HTML body uses plain language (no jargon, no technical terms, no clinical wording)
- Action labels describe the outcome, not the mechanism ("Save and continue" not "Submit POST")
- Error/warning messages are plain ("Something went wrong" not "Validation failed")
- Instructional text (info boxes, empty states) uses short sentences

This criterion applies ONLY when ≥1 persona with cognitive constraints is in `personas_applied`. If no
such persona: score 2 automatically (not applicable).

| Score | Threshold |
|-------|-----------|
| 0 | Personas with cognitive constraints cited; ≥2 label texts in body use jargon, clinical language, or technical terms |
| 1 | Most labels are plain; 1 label uses inappropriate language; OR instruction text uses long complex sentences (>2 clauses) |
| 2 | All label text plain and direct; action labels describe outcomes; error messages in plain language; OR no cognitive-constraint persona cited (N/A → 2) |

**Generator skill change**: Add to Phase 1 instruction for persona processing: "For each persona with
cognitive, anxiety, or literacy constraints: audit every label text in the HTML body. Replace technical
terms with plain alternatives. Action buttons must say what happens ('Keep private' not 'Confirm'), not
what the system does."

---

#### D3 — `a11y_touch_target_enforcement` (max 2 pts)

**What to check**: Distinguish from A2 (which checks persona application broadly). This criterion checks
specifically that EVERY interactive element — not just the ones in prominent positions — has either:
(a) `min-height: 48px` in inline style, OR (b) a comment `<!-- touch-target: 48dp -->` immediately above
the element, OR (c) uses a component (`[ListTile]`, `[FilledButton]`) whose default meets 48dp.

The current rubric only checks if touch targets are "annotated" — this checks if they are *universally*
applied including secondary/tertiary elements (overflow icons, chip rows, footnote links).

| Score | Threshold |
|-------|-----------|
| 0 | ≥3 interactive elements (buttons, links, toggles, list items) have neither a 48dp style nor annotation |
| 1 | Most elements meet 48dp; 1–2 small interactive elements (chip, icon button, footnote link) without 48dp annotation |
| 2 | Every interactive element has 48dp style, 48dp annotation, or uses a widget whose default meets 48dp; chips in chip rows individually meet 48dp |

**Generator skill change**: Add to wireframe quality rules: "Every interactive element — including chips,
icon buttons in overflow menus, and navigation items — must have `min-height: 48px` in its inline style
or an immediate `<!-- touch-target: 48dp -->` comment. No exceptions except elements explicitly labelled
as non-interactive."

---

### DIMENSION E — Component Library Integration (new, 4 points)

---

#### E1 — `component_library_references` (max 2 pts)

**What to check**: When a screen uses a pattern that matches an existing component in
`requirements_tasks/_scribble_components/` (currently: c_navigation_bar, c_app_bar, c_filled_button,
c_mood_entry_card), the screen HTML should either:
(a) Use `<div data-component="c_navigation_bar"></div>` (actual component reference), OR
(b) Include `<!-- uses: c_navigation_bar -->` in the component mapping block header

Also check: does the screen HTML have a `<script src="/requirements_tasks/_scribble_components/components.js">` tag?

| Score | Threshold |
|-------|-----------|
| 0 | Screen uses NavigationBar, AppBar, or FilledButton patterns with NO reference to corresponding components AND no components.js script tag |
| 1 | components.js script tag present; ≥1 component used without `uses:` reference; OR references present but no script tag |
| 2 | components.js script tag present; every pattern matching a library component has a `<!-- uses: c_xxx -->` reference in the mapping block |

**Generator skill change**: Add to Phase 1 component mapping block instructions: "Load
`/requirements_tasks/_scribble_components/components.js` in each screen. For each pattern that matches a
library component (NavigationBar → c_navigation_bar, AppBar → c_app_bar, FilledButton → c_filled_button,
mood entry card → c_mood_entry_card), add `<!-- uses: c_xxx -->` to the COMPONENT MAPPING block header."

---

#### E2 — `component_candidate_identification` (max 2 pts)

**What to check**: When a screen uses a NEW reusable pattern not yet in the component library — a
pattern that appears in ≥2 screens within the same scribble — the generator should tag it as a
component candidate: `<!-- component-candidate: c_transfer_scope_card -->`.

Also check: when a candidate is identified, does it appear consistently across the screens that use it
(same HTML structure pattern)?

| Score | Threshold |
|-------|-----------|
| 0 | ≥1 pattern appears in 3+ screens with no `component-candidate` annotation; OR screen uses a pattern but annotates it differently in each screen |
| 1 | Repeated patterns identified as candidates but annotation is inconsistent (different candidate names for same pattern) |
| 2 | All repeated patterns (≥2 screens) tagged as component-candidate with consistent name; OR scribble has no repeated patterns (N/A → 2) |

**Generator skill change**: Add to Phase 1 instructions: "After generating all screens, scan for
structural patterns that appear in ≥2 screens (same HTML structure for a card, row, or control group).
Tag each repeated pattern with `<!-- component-candidate: c_[descriptive_name] -->` on first occurrence,
and `<!-- uses-candidate: c_[same_name] -->` on subsequent occurrences."

---

### DIMENSION F — UX Heuristics Sampler (new, 2 points)

This dimension samples 3 of Nielsen's 10 heuristics that are most checkable at wireframe level without
subjectivity. Only applicable heuristics score — average across applicable ones, rounded to nearest integer.

---

#### F1 — `ux_heuristics_sampled` (max 2 pts)

**Three checkable heuristics**:

**H1 — Visibility of system status**: Any async operation (loading, transfer, scan) has a visible
status indicator on the screen (progress bar, spinner placeholder, status text). Not required for
instant operations.

**H4 — Consistency and standards**: Terminology is used consistently across all screens in the same
scribble. If "Transfer" is used on screen 2, not "Send" on screen 3 for the same action. Widget
patterns for the same action type are consistent.

**H5 — Error prevention**: Destructive actions have a confirmation step shown in the scribble (per
t2_destructive_actions). Forms that will have validation show what the invalid state looks like.

Score each applicable heuristic 0–1, average, then multiply by 2.

| Score | Threshold |
|-------|-----------|
| 0 | 2+ applicable heuristics completely unaddressed |
| 1 | Most applicable heuristics addressed; 1 with notable gap |
| 2 | All applicable heuristics addressed; status shown, terminology consistent, destructive actions gated |

**Generator skill change**: Add to MUST-DO list: "(a) Show loading/progress state for every async
operation. (b) Use the same label for the same action across all screens in the scribble. (c) Show
confirmation dialogs for destructive actions."

---

## Full Rubric Summary Table

| ID | Criterion | Dimension | Max | Can score 0? | Primary failure mode |
|----|-----------|-----------|-----|--------------|---------------------|
| A1 | component_mapping_block | Structural | 2 | Yes | Elements in body not in mapping block |
| A2 | persona_constraints_applied | Structural | 2 | Yes | Comments only, no HTML enforcement |
| A3 | wireframe_level | Structural | 2 | Yes | Saturated colors, shadows, animations |
| A4 | ac_coverage_demonstrated | Structural | 2 | Yes | ACs mentioned but not shown in HTML |
| A5 | md3_widget_labels_correct | Structural | 2 | Yes | M2 names or wrong hierarchy |
| A6 | screen_hierarchy_legible | Structural | 2 | Yes | Primary/destructive same visual weight |
| A7 | flow_positions_accuracy | Structural | 2 | Yes | Null step_numbers, missing files |
| A8 | t1_t2_rules_enforced | Structural | 2 | Yes | Rules cited but HTML contradicts them |
| B1 | md3_navigation_pattern | MD3 Widget | 2 | Yes | Nav bar on modal screens |
| B2 | md3_dialog_pattern | MD3 Widget | 2 | Yes | Wrong dialog type or cancel order |
| C1 | states_happy_and_empty | State Coverage | 2 | Yes | No empty state for list screens |
| C2 | states_loading_and_error | State Coverage | 2 | Yes | No error state for async screens |
| D1 | a11y_semantic_roles | Accessibility | 2 | Yes | Custom divs with no aria annotation |
| D2 | a11y_easy_language | Accessibility | 2 | Yes (if persona applicable) | Jargon in labels for cognitively constrained personas |
| E1 | component_library_references | Component Library | 2 | Yes | No components.js, no uses: refs |
| F1 | ux_heuristics_sampled | UX Heuristics | 2 | Yes | Missing status/consistency/error prevention |

**Total: 16 criteria, 32 points maximum**

Note: D3 (`a11y_touch_target_enforcement`) is removed as a standalone criterion — it is absorbed into A2
(persona_constraints_applied) and A8 (t1_t2_rules_enforced), which both check for t1_touch_targets
enforcement. Adding D3 would double-count the same observable.

E2 (`component_candidate_identification`) is kept as it checks new-pattern identification, which is
distinct from E1's library reference check.

---

## Revised Termination Threshold

**Current**: 12.8/16 = 80% (16-point scale)

**New threshold**: **25.6/32 = 80%** (32-point scale, same percentage)

The percentage stays at 80% to maintain the same bar proportionally. However, the new rubric is
fundamentally harder — a generator that trivially satisfied all 8 old criteria will likely score
approximately 18–22/32 on the new rubric (56–69%), not 80%. This gives 5 full iterations of
meaningful improvement space before the budget is exhausted.

**Plateau detection** (unchanged): If no criterion improves for 2 consecutive iterations → stop.
With 16 criteria, plateau is less likely to be a false positive — the old rubric's plateau detection
was vacuous because all criteria were at ceiling.

---

## Criteria Excluded and Why

The following criteria from the original brief were considered and deliberately excluded:

### Nielsen's Heuristics 2, 3, 6, 7, 8, 9, 10 (partial)
**Excluded**: Too subjective for automated vision evaluation. "Match between system and real world"
(H2) requires domain knowledge to assess. "Flexibility and efficiency" (H7) requires knowing the user's
expertise level. "Aesthetic and minimalist design" (H8) is explicitly what scribbles are NOT trying to
demonstrate. The 3-heuristic sampler in F1 captures the most mechanically checkable ones.

### Focus order annotation
**Excluded**: Tab/focus order is an implementation concern, not a wireframe concern. A wireframe cannot
meaningfully specify tab order beyond the visual layout order. This belongs in `doc/presentation/accessibility_guidelines.md`
for the implementation phase, not in scribble evaluation.

### Motion sensitivity annotations per persona
**Excluded**: Only one T2 rule (t2_crisis_mode) relates to motion. The `t1_t2_rules_enforced` criterion
(A8) already checks if crisis-mode personas have their rules enforced. Adding a separate motion criterion
would be redundant and apply to almost no fixtures.

### Color independence (shape/label vs color alone)
**Excluded**: At wireframe level, scribbles are already greyscale-only (enforced by A3). A greyscale
wireframe is by definition color-independent. This criterion adds no signal in the context of a
greyscale-enforced format.

### Screen reader distinction (decorative vs informative images)
**Partially included**: Folded into D1 (`a11y_semantic_roles`) which requires icon placeholder
annotation. A standalone criterion would double-count.

### Interaction budget / ≤3 tap verification
**Excluded**: Verifiable only dynamically. A static wireframe cannot demonstrate that an interaction
takes ≤3 taps — the evaluator cannot count taps from HTML. This is a `ui-verify-flutter` concern.

---

## Updated Sub-agent D Component Workflow

Sub-agent D (Skill Updater) must be extended to handle component creation alongside skill.md edits.

### Extended Sub-agent D Task

After applying the proposed skill.md change and committing (or reverting), Sub-agent D performs an
additional component library pass:

**Step D-5: Component candidate harvest**

For the worst-scoring fixture's latest generated screens (the recheck version), parse all screen HTML
files for:
- `<!-- component-candidate: c_xxx -->` annotations
- `<!-- uses-candidate: c_xxx -->` annotations (confirms c_xxx appears in multiple screens)

For each unique `c_xxx` found as a `component-candidate`:

1. **Check existence**: Does `requirements_tasks/_scribble_components/c_xxx/` exist?

2. **If missing — create**:
   - Create `requirements_tasks/_scribble_components/c_xxx/component.html` containing the HTML fragment
     extracted from the first screen that uses it (the structural pattern, stripped of screen-specific
     content, parameterized with placeholder labels)
   - Create `requirements_tasks/_scribble_components/c_xxx/metadata.yaml`:
     ```yaml
     component: c_xxx
     flutter_widget: [widget name from COMPONENT MAPPING block]
     material3_variant: "[variant if known, or 'standard']"
     tier: T2   # default; promote to T1 if pattern is system-wide
     rules_applied: []  # populate from the screen's T1/T2 rules section
     last_updated: [today]
     description: "[one-line description]"
     personas_applied: []  # populate from screen's PERSONAS APPLIED section
     ```

3. **If exists — check compatibility**: Read existing `component.html`. Compare structure to the
   new usage. If the new usage introduces additional required fields or structural changes:
   - Update `component.html` with the compatible superset structure
   - Bump `last_updated` in `metadata.yaml`
   - Append a `changelog:` entry: `{date, change, reason}`

4. **Commit component changes** alongside or after the skill.md commit:
   ```bash
   cd $WORKTREE
   git add requirements_tasks/_scribble_components/
   git commit -m "chore(scribble-components): iter{N} — add/update c_xxx from {worst_fixture}"
   ```
   Run `git add` and `git commit` as separate commands.

5. **Log to iteration_log.md**: Add a `## Component Changes` subsection to the iteration entry:
   ```markdown
   ## Component Changes — Iteration {N}
   - c_xxx: created (from pattern in {worst_fixture}/v{n+1}/02_screen.html)
   - c_yyy: updated (incompatible new field: chip count badge)
   ```

### Component creation constraint

Sub-agent D MUST NOT create components for patterns that appear in only one screen within the recheck
fixture. The `component-candidate` annotation itself signals the generator's intent, but Sub-agent D
must verify actual multi-screen usage (both `component-candidate` and `uses-candidate` annotations
present) before creating a new component.

---

## Priority Order for Implementation

Ordered by expected quality delta (highest first) — i.e., which changes most improve real scribble
quality relative to implementation cost.

| Priority | Criteria Group | Rationale |
|----------|---------------|-----------|
| 1 | C1 + C2 (State Coverage) | Currently zero empty/loading/error states. This is the largest gap between a "passing" scribble and a complete design specification. Every async screen needs these — high payoff. |
| 2 | A2 → A2 (persona constraints applied) + A8 (rules enforced) | The "annotation → enforcement" shift. Currently comments float free from HTML. Making each persona constraint and each rule produce an observable HTML element dramatically raises scribble utility. |
| 3 | A5 (MD3 widget labels correct) | Wrong M2 terminology (ElevatedButton, BottomNavigationBar) is a silent error that causes implementation divergence. Easy for generator to fix once given the lookup table. |
| 4 | B1 + B2 (MD3 navigation + dialog patterns) | Incorrect dialog/nav choices cause implementation rework. Moderately complex to check but directly improvable via a pattern table in skill.md. |
| 5 | D2 (easy language) | Most impactful for cognitively constrained personas. Requires generator to audit label text per-persona — new reasoning step. |
| 6 | E1 + E2 (component library) | Reduces duplication and improves cross-requirement consistency. Lower immediate quality delta but cumulative benefit grows as library expands. |
| 7 | D1 (semantic role annotations) | Important for implementation agent. Lower priority because current scribbles already use standard HTML elements that carry implicit semantics. |
| 8 | A4 (AC coverage demonstrated) | Refinement of existing criterion — the delta from "referenced" to "demonstrated" is real but smaller than the state coverage gap. |
| 9 | F1 (UX heuristics) | Partially covered by other criteria already (error prevention by B2 + C2, consistency by A5+A6). The sampler adds value but lower delta than direct improvements. |
| 10 | A6 (hierarchy legible, tighter) + A3 (wireframe, tighter) + A7 (flow accuracy) + A1 (mapping complete) | These are refinements of existing criteria where current performance is already good. Tightening definitions adds signal but yields smaller score movement per iteration. |

---

## Skill Update Plan: What Changes in Each Skill File

### Changes to `ui-create-scribble/skill.md`

These changes improve the generator so that future scribbles score well on the new rubric.

**Change 1 (Priority 1 — State Coverage)**
In Phase 1 MUST-DO list, add after item 8 ("Include state variants when relevant"):
> 9a. For every screen that displays a list or collection: add an empty state variant as a dashed-border
> annotated panel immediately below the screen (outside the device frame), showing what the screen looks
> like with zero items. Include one explanation label and one call-to-action button.
>
> 9b. For every screen that involves a wait (data load, QR scan, form submit, transfer in progress):
> add a loading state panel (show a `[CircularProgressIndicator]` placeholder) and an error state panel
> (show a plain-language error message + `[TextButton] Try again`) as annotated overlays.
> Error messages must use plain language: "Something went wrong — tap to try again" not "Error 503".

**Change 2 (Priority 2 — Persona enforcement + Rule enforcement)**
In Phase 1 MUST-DO list, replace current item 6 ("Apply persona constraints") with:
> 6. For each persona in `personas_applied`: identify their PRIMARY constraint type. Then find the HTML
> element that must embody that constraint and enforce it:
> - Motor constraint (tremors, reduced precision) → every interactive element gets `min-height: 48px`
>   (or 64px in crisis flows) in inline style
> - Cognitive constraint (ADHD, depression, anxiety) → audit every label text; replace jargon with plain
>   alternatives; action buttons must say outcomes not mechanisms
> - Privacy constraint → find labels that could expose sensitive context; replace with neutral alternatives
> - Environmental constraint (darkness, public space) → apply appropriate background styling or copy
>
> For each T1/T2 rule cited in the RULES APPLIED section: find the specific HTML element the rule
> constrains and make the constraint visible in that element's style or label text. A rule comment without
> a corresponding HTML enforcement is incomplete.

**Change 3 (Priority 3 — MD3 widget naming)**
In Phase 1, after the MUST-DO list, add a MD3 Widget Hierarchy Reference Table:
> **M3 Widget Hierarchy (use these names, not M2 alternatives)**
>
> | Role | Correct M3 label | NEVER use |
> |------|-----------------|-----------|
> | Primary action | [FilledButton] | [ElevatedButton] for primary |
> | Secondary action | [OutlinedButton] | [FilledButton] for secondary |
> | Tertiary / text action | [TextButton] | |
> | Destructive confirm | [FilledButton] (in dialog only, red) | [FilledButton] inline with primary |
> | Destructive cancel | [TextButton] (comes FIRST in dialog) | |
> | Bottom nav (mobile, ≤5 dest) | [NavigationBar] + [NavigationDestination] | [BottomNavigationBar] |
> | Side nav (tablet/large screen) | [NavigationRail] | [NavigationBar] on tablet |
> | Overflow nav | [NavigationDrawer] | |
> | Simple top bar | [CenterAlignedTopAppBar] | [AppBar] (unspecified variant) |
> | Content-heavy top bar | [LargeTopAppBar] | |
> | Confirmation (binary) | [AlertDialog] | [SimpleDialog] for yes/no |
> | Selection from list | [SimpleDialog] | [AlertDialog] for list choice |
> | Complex form | [ModalBottomSheet] | [AlertDialog] for multi-field input |
> | Sub-destination tabs | [TabBar] + [TabBarView] | [NavigationBar] for sub-tabs |

**Change 4 (Priority 4 — Navigation and Dialog patterns)**
In Phase 1 MUST-DO list add:
> 11. Navigation pattern: determine whether each screen is (a) a primary destination, (b) a detail/secondary
> screen, or (c) a modal/overlay. Primary destinations show [NavigationBar]. Detail screens show [AppBar]
> with BackButton — do NOT repeat the NavigationBar. Modals show no navigation bar.
>
> 12. Dialog pattern: when showing a confirmation overlay, select dialog type from the M3 Widget Hierarchy
> table above. Always place the cancel/dismiss action FIRST (leftmost) in dialog actions.

**Change 5 (Priority 6 — Component library)**
In Phase 1 MUST-DO list add:
> 13. At the top of each screen HTML, add:
> `<script src="/requirements_tasks/_scribble_components/components.js"></script>`
>
> In the COMPONENT MAPPING block, add a `LIBRARY COMPONENTS` section:
> ```
> LIBRARY COMPONENTS USED
> ========================
> <!-- uses: c_navigation_bar --> (if NavigationBar pattern used)
> <!-- uses: c_app_bar -->        (if AppBar pattern used)
> <!-- uses: c_filled_button -->  (if FilledButton used as primary CTA)
> <!-- uses: c_mood_entry_card --> (if mood entry card pattern used)
> ```
>
> After all screens are generated, scan for structural patterns appearing in ≥2 screens.
> Tag each with `<!-- component-candidate: c_[descriptive_name] -->` on first occurrence and
> `<!-- uses-candidate: c_[same_name] -->` on repeats.

**Change 6 (Priority 5 — Easy language for cognitive personas)**
In Phase 1 MUST-DO list add:
> 14. For each persona with cognitive, anxiety, or literacy constraints cited in `personas_applied`:
> audit every label, heading, button text, and info-box text in the HTML body.
> Replace: technical terms, clinical wording, multi-clause sentences, passive voice.
> Keep: short active sentences, outcome-focused button labels, explicit explanations of consequences.
> Example: "Make transferable" not "Confirm scope change"; "Keep private" not "Disable sharing".

### Changes to `ui-create-scribble-improve/skill.md`

**Change 1 — Replace rubric section**
Replace the current "8-Criterion Rubric" table and the evaluation YAML template with the 16-criterion
rubric defined in this plan. Update the evaluation YAML format:

```yaml
fixture: {short_name}
iteration: {N}
total: {sum}/32
criteria:
  component_mapping_block: {0|1|2}
  component_mapping_block_evidence: "..."
  persona_constraints_applied: {0|1|2}
  persona_constraints_applied_evidence: "..."
  wireframe_level: {0|1|2}
  wireframe_level_evidence: "..."
  ac_coverage_demonstrated: {0|1|2}
  ac_coverage_demonstrated_evidence: "..."
  md3_widget_labels_correct: {0|1|2}
  md3_widget_labels_correct_evidence: "..."
  screen_hierarchy_legible: {0|1|2}
  screen_hierarchy_legible_evidence: "..."
  flow_positions_accuracy: {0|1|2}
  flow_positions_accuracy_evidence: "..."
  t1_t2_rules_enforced: {0|1|2}
  t1_t2_rules_enforced_evidence: "..."
  md3_navigation_pattern: {0|1|2}
  md3_navigation_pattern_evidence: "..."
  md3_dialog_pattern: {0|1|2}
  md3_dialog_pattern_evidence: "..."
  states_happy_and_empty: {0|1|2}
  states_happy_and_empty_evidence: "..."
  states_loading_and_error: {0|1|2}
  states_loading_and_error_evidence: "..."
  a11y_semantic_roles: {0|1|2}
  a11y_semantic_roles_evidence: "..."
  a11y_easy_language: {0|1|2}
  a11y_easy_language_evidence: "..."
  component_library_references: {0|1|2}
  component_library_references_evidence: "..."
  ux_heuristics_sampled: {0|1|2}
  ux_heuristics_sampled_evidence: "..."
```

**Change 2 — Update termination threshold**
Replace `12.8/16` with `25.6/32` in Step 3 termination check.

**Change 3 — Update Sub-agent D**
Extend Sub-agent D task with the "Step D-5: Component candidate harvest" workflow defined above.

**Change 4 — Update Sub-agent C scoring**
Sub-agent C (Improvement Planner) now averages across 16 criteria (32 points total). Update its task
description: "Compute per-criterion average across all fixtures. Identify the single criterion with the
lowest average score from the 16-criterion rubric (total: 32 points)."

---

## Implementation Agent Instructions

An implementation engineer can execute this plan with two file edits:

**File 1**: `/workspaces/private_mood_tracker/flutter_app/.claude/skills/ui-create-scribble/skill.md`
- Apply Changes 1–6 to the Phase 1 section (MUST-DO list additions + M3 Widget Hierarchy table)

**File 2**: `/workspaces/private_mood_tracker/flutter_app/.claude/skills/ui-create-scribble-improve/skill.md`
- Apply Changes 1–4 (replace rubric, update threshold, extend Sub-agent D, update Sub-agent C)

The changes are additive to Phase 1 (no deletions from existing MUST-DO list, only additions) and
surgical replacements in the improve skill (rubric table, YAML template, threshold value, Sub-agent D task).

After editing both files: run `ui-create-scribble-improve` skill to validate that the new rubric
produces non-ceiling scores on the existing fixtures (expected: 18–24/32, not 32/32).

---

## Quality Verification Checklist

After implementation:

- [ ] Re-run improve loop on same 3 fixtures; no fixture scores 32/32 on first attempt
- [ ] At least 2 criteria score below 2 on at least 1 fixture (rubric is not trivially satisfied)
- [ ] Sub-agent D creates or updates a component when `component-candidate` annotation found
- [ ] Termination threshold changed to 25.6/32 in improve skill
- [ ] MD3 Widget Hierarchy table present in create-scribble skill Phase 1
- [ ] State coverage instructions (empty + loading + error) present in create-scribble MUST-DO list
- [ ] Generator produces dashed overlay panels for empty/error states (verify in generated HTML)

---

## Risks

**Risk 1 — Rubric too hard (floor effect)**
If the new rubric consistently scores 0–6/32, the improve loop will thrash without convergence.
Mitigation: D2 (easy language) auto-scores 2 when no cognitive persona is cited; A7 (flow accuracy)
auto-scores 2 when no flow reference exists. These N/A cases prevent floor. Monitor first run.

**Risk 2 — Evaluator hallucination on quality criteria**
The old rubric's success was partly due to binary presence checks (easy to verify). Quality criteria
(e.g., "is MD3 hierarchy correct?") require evaluator judgment. Vision evaluators may disagree across
runs.
Mitigation: Every scoring rule has concrete observable thresholds (count elements, check specific CSS
properties, check specific words) to minimize evaluator discretion. The evidence field requirement
forces the evaluator to cite specific HTML.

**Risk 3 — Component creation conflicts**
If Sub-agent D creates a component that later conflicts with a human-authored component, the metadata
will diverge.
Mitigation: Sub-agent D checks existence before creating. Existing components are only updated when
structural incompatibility is detected, not on every iteration. `changelog:` field tracks all changes.

**Risk 4 — Token cost increase**
16 criteria × 3 fixtures × evidence per criterion = significantly larger evaluation YAML. Each
evaluator agent context grows.
Mitigation: Evidence field capped at one sentence per criterion (enforced in agent task description).
Total YAML size increase: ~2× the current size — acceptable given the quality signal gain.
