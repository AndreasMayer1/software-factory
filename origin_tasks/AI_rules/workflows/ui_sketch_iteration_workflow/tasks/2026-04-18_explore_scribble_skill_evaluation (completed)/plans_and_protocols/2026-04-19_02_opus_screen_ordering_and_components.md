---
agent: claude-opus-4-7
date: 2026-04-19
task: TASK-PROC-032-02
status: complete
supersedes_scope_of: 2026-04-18_01_protocol_evaluation_findings.md  # complements, does not supersede
topic: "Screen ordering across distributed requirements; cross-requirement iteration; component library"
---

# Scribble Skill — Screen Ordering, Cross-Requirement Iteration, and Component Library

## Executive Summary

The current `ui-create-scribble` skill is correct in concept but incomplete for this project's **decomposition reality**: a single user-facing flow is implemented by many requirements, spanning multiple epics and features, and many UI elements (bottom nav, app bar, crisis-safety bar, mood-entry card) are **inherently cross-requirement**. The per-requirement `scribbles/v*/` folder is the right atomic unit for the **approval** artifact, but not the right unit for **flow context** or for **component reuse**.

The cleanest resolution — fitting the existing HTML/CSS/no-build-system constraint, the `user_flows/<flow>/flow.md` existing artifact, and the T1/T2/T3 tier system — is to introduce **three complementary concepts** beside the existing per-requirement scribble folder:

1. **Flow position metadata** in each scribble's `metadata.yaml` that anchors each screen to one or more flow+step coordinates (e.g. `flow: FLOW-001, step: 3`). This replaces numeric sort keys as the source of truth for ordering and lets the skill compute position without rewriting already-approved files.
2. **A flow-level composite `index.html`** per flow (under `requirements_user_needs/user_flows/<flow>/scribbles/index.html`) that is **generated** by walking all per-requirement scribbles and iframing their screens in flow-step order. No per-requirement scribble ever needs to know what "comes before" or "comes after" it.
3. **A shared scribble component library** at `requirements_tasks/_scribble_components/` using the standard HTML5 `<template>` element inlined via a single tiny script (`components.js`). Per-requirement scribbles reference components by ID. When a T1/T2 rule changes a shared component, only the library file is edited; all dependent scribbles automatically reflect the change on next browser open.

These three additions:
- **Do not** invalidate any approved scribble when a neighbouring screen is added later.
- **Do not** require renumbering screen files across requirements.
- **Do** preserve the tier system's governance guarantees (Haiku impact check, `doc-update-guidelines`, human approval for T1/T2 changes).
- **Do** give `ui-verify-flutter` and `ui-improve-flutter` a stable, whole-flow view for cross-screen checks.

REQ-PROC-032 needs four new acceptance criteria (AC-16..AC-19) and two new sections (SEC-12 Flow Ordering & Composite Index, SEC-13 Shared Component Library). The `ui-create-scribble` skill.md needs a new Phase 1 read-step (load flow and component library) and a new Phase 5a (regenerate flow-level composite). The Rule Update Protocol (SEC-07) needs a new Step 3b: "extend impact check to approved scribbles that depend on the shared component".

---

## 1. Screen Ordering Strategy

### 1.1 The problem, restated

The filesystem convention `01_home.html`, `02_entry.html` implies a **total ordering that the requirement cannot know**. In this project:

- Requirements are features under epics; features do not own user-facing flows.
- User flows (`FLOW-001`..`FLOW-004`, many more planned) are the authoritative sequence of steps. Each flow step maps to a screen and to an epic/feature.
- A later feature (e.g. `feat_voice_input`) inserts a new screen between two already-approved screens of a different feature (`feat_quick_entry`).

A numeric prefix (`01_`, `02_`, `03_`) baked into the filename is fragile under this pattern — inserting a screen between `01_` and `02_` forces either renumbering (breaking links, git history, review continuity) or collision (two `02_` files).

### 1.2 Core decision: numeric prefix is a **local** sort key, not a flow position

Keep the `NN_<name>.html` convention **within a single requirement's scribble** — it gives reviewers a sensible read-through order when opening that requirement's folder in isolation. But stop treating it as the flow-wide ordering authority.

Introduce a **flow-position coordinate** stored in each screen file's component-mapping block header AND in `metadata.yaml`:

```yaml
# metadata.yaml
screens_covered:
  - file: 01_quick_entry.html
    name: "Quick Entry Screen"
    flow_positions:
      - flow: FLOW-001
        step: 2
        role: primary           # primary | supporting | adaptive-variant
  - file: 02_voice_input_active.html
    name: "Voice Input Active"
    flow_positions:
      - flow: FLOW-001
        step: 3
        role: primary
```

And at the top of the screen HTML:

```html
<!--
  SCREEN: Voice Input Active — active whisper-level voice capture
  REQUIREMENT: REQ-FUNC-002 (feat_voice_input)
  VERSION: v2
  FLOW-POSITIONS:
    FLOW-001 step 3 (primary)
    FLOW-001 step 4 (adaptive-variant: "Voice Input (Capturing)")
  ...
-->
```

This is exactly analogous to how `flow.md` already models flows — see `quick_night_entry/flow.md` lines 58–69, the "Happy Path" table with columns `#`, `User Action`, `UI State/Screen`, `Related Epic/Feature`. The scribble metadata reverses the link: from screen-file back to flow step.

### 1.3 Question A — how to handle insertion

**Scenario**: `feat_quick_entry` approved (`01_home.html`, `02_entry.html`, mapped to FLOW-001 steps 1 and 2). Now `feat_voice_input` is being scribbled, needs to go between them (FLOW-001 step 3, between original steps 1–2 renumbered to 1 and 4 — or better: the flow already defines step 3 as "Voice Input Active").

**Concrete algorithm for the Phase 1 generation agent**:

1. Read `goal.md`. Extract `parent_requirement` and `user_needs.implements_flows[].id` + `steps[]` (these are already standard frontmatter — see `feat_qr_data_transfer/requirements.md` lines 14–18 for the pattern).
2. For each `(flow, step)` pair in `implements_flows`:
   - Read `requirements_user_needs/user_flows/<flow>/flow.md`.
   - Extract the "Happy Path" table. For each step the current requirement claims, take the value in column `UI State/Screen`. That is the canonical screen name.
3. Before generating HTML, **check whether any other requirement already owns a scribble for the same `(flow, step)` coordinate**. This is done by grep over `requirements_tasks/**/scribbles/*/metadata.yaml` for `flow: FLOW-00X` and `step: N`.
   - If an approved scribble owns `(FLOW-001, step 2)` already, and the current requirement also claims step 2, that means one of two things:
     - **Same screen** (bottom-nav-in-all-requirements case) → do not re-scribble; **reference** the existing screen via `reuses_screen:` in metadata.yaml (see §1.4).
     - **Adaptive variant** (e.g. same step, different protocol type) → generate a new screen file, mark `role: adaptive-variant` in flow_positions, and write a `variant_of:` field pointing to the canonical scribble. (The Transfer Detail Screen gap #9 in `_clusters/flexible_data_transfer/requirements_matrix.md` is exactly this: one shared component reused across FLOW-003 and FLOW-004; and FLOW-003 Client Data View is adaptive for Weber/Sarah/Turan protocol types.)
   - If no other scribble owns that coordinate, generate normally.
4. Within the requirement's own scribble folder, order files by `min(flow_positions.step)` across all flow_positions, then by name. That produces the `NN_` prefix for local browsing.

**Answer to the three sub-questions of A**:

- **Screen numbering**: Prefixes are **recomputed** each version inside that requirement's own folder. They are cosmetic. When a new screen is inserted *in a new requirement's folder*, no existing file is renamed — the flow-position coordinate in metadata is the truth, and the flow-level composite `index.html` (§3) sequences everything correctly without touching numbered filenames.
- **Iterating on approved scribbles**: An approved scribble stays `status: approved` even when a later requirement inserts a new flow step before it. The approved scribble is a record of *that requirement's contribution*; it is not a record of "the whole flow as it stood on date X".
- **Cross-requirement consistency**: `feat_voice_input` does **not** re-scribble home.html. It generates only the one screen it contributes (voice_input_active.html), and declares `flow_positions` that the flow-level composite uses to slot it in between home and entry. Home.html remains owned by `feat_quick_entry`.

### 1.4 Question B — how the skill knows the correct cross-requirement ordering

The skill **reads `flow.md`**, full stop. Two concrete rules:

- **MUST read before Phase 1 generation**: For every flow listed in `goal.md`'s `user_needs.implements_flows`, load the corresponding `flow.md` Happy Path table. This is already implicit in the existing skill ("reads requirements.md and personas") but is not made explicit; it needs to be a first-class input.
- **MUST NOT invent ordering**: If a screen's flow_positions are not derivable from `flow.md`, the skill stops and asks the human whether (a) the flow needs an Exception entry added, (b) the screen is a T3 adaptive variant of an existing flow step, or (c) the screen has no flow coordinate (rare — e.g. a settings sub-screen that the flow does not model step-by-step).

This enforces a clean discipline: **UI screens that exist must also exist as flow steps, or as explicit flow exceptions, or as T3 adaptive variants of a flow step**. That is actually an existing informal rule (every requirement already has `user_needs.implements_flows[].steps[]`); we are making it operational for scribbles.

### 1.5 Question C — already answered in §3

Per-requirement `index.html` stays (it's already mandatory per AC-01 and REQ-PROC-032 SEC-03). A **flow-level composite** is added next to each flow. See §3 below.

### 1.6 Reusable / "appears on all screens" components (bottom nav, app bar, crisis-safety bar)

These are a **different animal** from sequential screens. They are not steps in any flow; they are UI chrome that appears on many screens regardless of step. Two complementary answers:

- **As components**: they live in the shared component library (§4) and are included in every screen HTML that renders them.
- **As screens**: they do not get their own flow_positions. The requirement that owns them (e.g. `feat_bottom_nav` under `epic_navigation`) produces exactly one scribble file for the component and declares `role: chrome` in `metadata.yaml`:

```yaml
screens_covered:
  - file: 01_bottom_nav.html
    name: "Bottom Navigation Bar"
    flow_positions: []
    role: chrome
    component_library_entry: c_bottom_nav
```

The flow-level composite never tries to slot a chrome file into a flow step sequence; it displays chrome-role screens in a separate "Chrome & global components" section of the composite.

---

## 2. Cross-Requirement Iteration Protocol

### 2.1 Problem surface

Two distinct triggers for cross-requirement regeneration, each with its own protocol:

- **Trigger A: T1/T2 rule update** changes a shared component or a universal constraint (e.g. "all FilledButton minimum height goes from 48dp to 52dp"). This is already partly handled by the Rule Update Protocol (SEC-07 Step 3 Haiku impact check) but the check currently scans **implemented requirements only** (requirements whose tasks are completed). It does not scan **approved scribbles** that will become implementations later.
- **Trigger B: New requirement inserts a new flow step** between existing approved scribbles' steps (e.g. `feat_voice_input` inserts step 3 between FLOW-001 steps 2 and 4 as originally numbered). This does not touch any approved scribble's HTML — the insertion is handled by metadata and the composite index (§1, §3).

Trigger A is the hard case. Trigger B is already solved by §1.

### 2.2 Protocol for Trigger A — T1/T2 rule change affecting shared components

Extend SEC-07 Step 3 (Impact check) to cover scribbles, not just implementations:

**SEC-07 Step 3 — expanded**:

> The Haiku impact agent runs two searches:
>
> 1. (existing) Grep `requirements_tasks/**/requirements.md` for Presentation Layer scope on already-completed tasks → list of already-implemented requirements affected by the rule.
>
> 2. (new) Grep `requirements_tasks/**/scribbles/v*/metadata.yaml` for `status: approved` entries → list of approved scribbles affected by the rule. For each, enumerate:
>    - Which rule IDs (e.g. `t1_touch_targets`) appear in `rules_applied` — these scribbles reference the rule directly.
>    - Which `component_library_entry` IDs appear in the scribble's screens — if the rule affects a shared component (e.g. c_bottom_nav), all scribbles using that component are affected.
>
> 3. (new) Grep `requirements_tasks/_scribble_components/**/metadata.yaml` for components that list this rule in their `rules_applied` field → shared components affected.

Developer then decides, for each affected scribble:

- **Re-scribble now** (create `vN+1/` with the new rule applied) — for scribbles that are on the active implementation path.
- **Mark as stale, re-scribble when the implementation task starts** — for scribbles approved but implementation not yet scheduled. The scribble's metadata.yaml gets a `stale_since:` field and a `pending_rules:` list.
- **Component-only update** — if the rule affects only a shared component, update the component library entry; all dependent scribbles automatically reflect it (no per-scribble regeneration needed for the shared parts). This is the most common case and the biggest payoff of the component library.

### 2.3 Step-by-step protocol (developer view)

```
1. Developer approves new T1/T2 rule in ui-create-scribble feedback cycle.
   │
   ▼
2. Skill invokes doc-update-guidelines → rule anchored in doc/presentation/design/
   │
   ▼
3. Skill spawns Haiku impact agent (expanded scope — §2.2):
   - implemented requirements affected
   - approved scribbles affected (direct rule reference)
   - shared components affected
   - transitively: scribbles using affected shared components
   │
   ▼
4. Skill presents a 4-column table to developer:
     | Affected artifact | Type | Reason | Suggested action |
   Types: impl | scribble (direct) | scribble (via component) | component
   Actions: re-scribble now | mark stale | component-update-only | accept-as-deviation
   │
   ▼
5. Developer classifies each row. Options:
   (a) re-scribble now → spawn scribble-regen agent per affected requirement
   (b) mark stale → add stale_since + pending_rules to metadata.yaml
   (c) component-only → edit _scribble_components/<id>/component.html in place;
       bump component version; dependent scribbles see new version on next open
   (d) accept-as-deviation → write T3 override DDR in the affected scribble's metadata
   │
   ▼
6. Skill executes (a) and (c) in parallel (each re-scribble is its own agent);
   writes stale markers for (b); writes DDRs for (d).
   │
   ▼
7. task-complete commits: one commit per affected scribble,
   one commit for the component update, one commit for the rule itself.
```

### 2.4 "Stale" lifecycle

A scribble marked `stale_since: YYYY-MM-DD` with `pending_rules: [t1_touch_targets]` is still `status: approved` — approved means "the approving developer accepted this design at that point in time with the rules then in force". Stale means "a rule has changed since; the scribble should be refreshed before implementation begins".

The `code-simple`/`code-complex` integration (AC-06) needs one new precondition check: before starting implementation from an approved scribble, check `stale_since`. If set, prompt: "This scribble is stale since <date> — pending rules: [...]. Re-scribble first, or accept staleness as deviation?".

### 2.5 Question D — which scribbles get regenerated when a T1/T2 rule changes

Summary answer: **all three categories** that the expanded Haiku check identifies (§2.2):

1. Scribbles that directly reference the changed rule in `rules_applied` (obvious case).
2. Scribbles whose screens include a shared component whose library entry references the changed rule (transitive case).
3. Scribbles whose tier-3 rules or DDRs contradict the new T1/T2 rule (conflict case — human resolves via DDR).

The pre-existing impact-check-on-implemented-requirements is kept; the scribble check is **additive**.

### 2.6 Question E — should shared UI patterns live in a shared library

**Yes** (see §4 for mechanics). Why this is the right answer rather than duplication:

- Eliminates most regeneration churn. Bottom nav changes once; 40+ scribbles all reflect it on next open with zero agent work.
- Keeps per-requirement scribbles focused on what that requirement contributes, not on rendering chrome.
- Gives `ui-verify-flutter` a stable selector: the Flutter implementation of the bottom nav is verified once against `_scribble_components/c_bottom_nav/`, not per-requirement.
- Mirrors the Clean Architecture conviction that shared presentation concerns live in a shared module.

The cost is adding one library file per component and one include line per screen that uses it — strictly cheaper than duplicating HTML across scribbles.

---

## 3. Index.html Architecture

### 3.1 Recommendation

**Both**, with different owners and different regeneration triggers:

| index | Owner | Location | Scope | Regenerated by |
|---|---|---|---|---|
| per-requirement `index.html` | the scribble-generating agent | `requirements_tasks/<category>/<req>/scribbles/v<n>/index.html` | only screens in that requirement | every version bump of that scribble |
| flow-level composite `index.html` | a deterministic script + agent | `requirements_user_needs/user_flows/<flow>/scribbles/index.html` | all screens across all requirements that serve that flow | any time a scribble serving that flow is added/updated/approved |

The per-requirement index already exists (AC-01, SEC-03). The flow-level composite is new.

### 3.2 Why a flow-level composite is necessary

Without it, reviewing "does the Quick Night Entry flow hang together visually?" requires the reviewer to open 4+ separate browser tabs from 4+ different requirement folders, in the right order, with no way to see FLOW-001's step flow as a sequence. The developer cannot verify cross-screen continuity (persona conflict check 2, the "holistic flow continuity" item in `persona_design_bridge.md` Section 6 — "AI designs screens in isolation. Misses logical breaks across screens").

A flow-level composite gives one URL that displays all of FLOW-001 in sequence. It is regenerated deterministically and is **not** an approval artifact — it is a read-through view.

### 3.3 Implementation — pure HTML, no build system

The composite is a single `index.html` per flow, generated by walking the filesystem. The content is deliberately simple: for each flow step, embed the canonical scribble screen for that `(flow, step)` as an `<iframe>` with the screen's HTML file as src.

```html
<!-- requirements_user_needs/user_flows/quick_night_entry/scribbles/index.html -->
<!DOCTYPE html>
<meta charset="utf-8">
<title>FLOW-001 — Composite Scribble</title>
<style>
  body { font-family: system-ui; margin: 0; background: #f4f4f4; }
  .step { margin: 24px; padding: 16px; background: white; border-radius: 8px; }
  .step h2 { font-size: 14px; color: #666; margin: 0 0 8px; }
  .step iframe { width: 390px; height: 844px; border: 1px solid #ccc; }
  .meta { font-size: 12px; color: #888; margin-top: 8px; }
  .chrome { background: #fff8e1; }
</style>

<div class="step">
  <h2>Step 1 · Home Screen (Night Mode)</h2>
  <iframe src="../../../../requirements_tasks/functional/client/epic_data_input/feat_night_mode/scribbles/v3/01_home_night_mode.html"></iframe>
  <div class="meta">
    Owner: REQ-FUNC-XXX (feat_night_mode, v3, approved 2026-03-15)
    Rules: t1_dark_mode, t1_discrete_identity
  </div>
</div>

<div class="step">
  <h2>Step 2 · Quick Entry Screen</h2>
  <iframe src="../../../../requirements_tasks/functional/client/epic_data_input/feat_quick_entry/scribbles/v2/01_quick_entry.html"></iframe>
  ...
</div>

<div class="step chrome">
  <h2>Chrome · Bottom Navigation</h2>
  <iframe src="../../../../requirements_tasks/functional/client/epic_navigation/feat_bottom_nav/scribbles/v1/01_bottom_nav.html"></iframe>
</div>
```

**Browser compatibility**: file:// iframes work across Chrome, Firefox, Safari, Edge — the exact path used to view scribbles today. No build step.

### 3.4 Regeneration algorithm

Add a small, deterministic script — `scripts/generate_flow_scribble_index.py` — that:

1. Reads `requirements_user_needs/user_flows/<flow>/flow.md` and extracts Happy Path steps.
2. Grep-scans `requirements_tasks/**/scribbles/v*/metadata.yaml` for `status: approved` AND `flow_positions[] .flow == <flow>`.
3. For each step of the flow, selects the single canonical scribble file (role: primary). Lists any variants/adaptive in a sub-section.
4. Emits the composite `index.html` as plain HTML (no templating engine — just Python string concat, same spirit as existing scripts like `generate_status_overview.py`).

Scribble skill calls this script in **Phase 5a** (new), right after a scribble is approved, for each flow the scribble serves.

### 3.5 Tradeoffs considered and rejected

| Alternative | Why rejected |
|---|---|
| Single **global** `index.html` listing all flows and all screens | Breaks readability once the app has 20+ flows; composite per flow is the right unit. |
| Per-requirement index **stores flow order** | Fragile under insertion; duplicates flow.md as source of truth. |
| Scribble agent generates the composite inline | Non-deterministic and expensive (agent tokens per composite); a script is O(ms). |
| No composite, rely on reviewer clicking through tabs | Loses the "flow continuity" review gate; personas and rules are per-screen but the flow is between-screens. |

### 3.6 Per-requirement index stays

Per-requirement `index.html` is still mandatory (AC-01). It is the single-scribble review artifact. The flow-level composite is the cross-scribble review artifact. Both are needed.

---

## 4. Component Library Design

### 4.1 Should it exist

**Yes.** Required by the reuse pattern already emerging in requirements (`_clusters/flexible_data_transfer/requirements_matrix.md` Gap #9 "Transfer Detail Screen (shared component)" is a literal example of a shared UI component spanning requirements).

### 4.2 Location and structure

```
requirements_tasks/
  _scribble_components/           # sibling of functional/, process/, etc.
    README.md                     # usage, maintenance protocol
    components.js                 # single 40-line vanilla-JS include script
    components.css                # reset + baseline styles used across components
    c_app_bar/
      component.html              # <template id="c_app_bar">...</template>
      metadata.yaml               # component ID, version, rules_applied, flutter_widget
      examples/
        c_app_bar_default.html    # how it renders standalone (for review)
        c_app_bar_with_action.html
    c_bottom_nav/
      component.html
      metadata.yaml
    c_mood_slider/                # app-specific component
      component.html
      metadata.yaml
    c_emotion_chip/
    c_habit_tile/
    c_crisis_safety_bar/          # referenced by REQ-FUNC-021
    c_transfer_detail/            # Gap #9 shared across FLOW-003/004
    ...
```

Naming convention: `c_<name>` for all entries. `c_` prefix prevents collision with CSS class or any future document conventions. One folder per component, each self-contained.

### 4.3 HTML/CSS technique — `<template>` + tiny include script

Standard HTML5 `<template>` elements are the correct mechanism: they are not rendered by the browser when declared, they carry their own DOM, and they can be cloned into a host element at runtime via a 3-line JS snippet.

**Per-component file** (`c_bottom_nav/component.html`):

```html
<template id="c_bottom_nav">
  <style>
    /* local styles — scoped by wrapping element */
    .c-bottom-nav { display:flex; border-top:1px solid #ccc; background:#fff; }
    .c-bottom-nav .item { flex:1; min-height:48px; display:flex; align-items:center;
                          justify-content:center; font-size:12px; color:#444; }
    .c-bottom-nav .active { color:#000; border-top:2px solid #000; }
  </style>
  <nav class="c-bottom-nav"><!-- NavigationBar (M3) -->
    <div class="item">Home</div>
    <div class="item active" aria-current="page">Entry</div>
    <div class="item">Insights</div>
    <div class="item">Settings</div>
  </nav>
</template>
```

**Single include script** (`_scribble_components/components.js` — ~40 lines, no dependencies):

```js
// Why: per-scribble inclusion without a build system. Vanilla JS, no framework.
(async function () {
  // find all <div data-component="c_xxx"> and replace with library content
  const hosts = document.querySelectorAll('[data-component]');
  for (const host of hosts) {
    const id = host.dataset.component;
    const relPath = host.dataset.libPath || '../../../../_scribble_components';
    try {
      const res = await fetch(`${relPath}/${id}/component.html`);
      const html = await res.text();
      const doc = new DOMParser().parseFromString(html, 'text/html');
      const tpl = doc.querySelector(`template#${id}`);
      if (!tpl) { host.innerHTML = `<em>missing: ${id}</em>`; continue; }
      host.appendChild(tpl.content.cloneNode(true));
    } catch (e) { host.innerHTML = `<em>fetch failed: ${id}</em>`; }
  }
})();
```

**Per-screen usage** (`01_home_night_mode.html`):

```html
<!DOCTYPE html>
<meta charset="utf-8">
<title>Home Screen — Night Mode</title>
<!--
  SCREEN: Home — night-mode landing
  REQUIREMENT: REQ-FUNC-XXX
  VERSION: v3
  FLOW-POSITIONS: FLOW-001 step 1 (primary)
  COMPONENTS USED: c_app_bar, c_bottom_nav, c_quick_entry_tile
  ...
-->
<link rel="stylesheet" href="../../../../_scribble_components/components.css">

<div data-component="c_app_bar"></div>

<main>
  <!-- page-specific content, directly inline —
       only the cross-cutting chrome goes through the library -->
  <h1>Tonight</h1>
  <div data-component="c_quick_entry_tile"></div>
</main>

<div data-component="c_bottom_nav"></div>

<script src="../../../../_scribble_components/components.js"></script>
```

**Browser behaviour**: opening the file with `file://` in any modern browser executes the include script; components appear inline. The relative path works because every scribble lives at a fixed depth (`requirements_tasks/<category>/<req>/scribbles/v<n>/*.html`) from `_scribble_components/`.

**Why not iframe-per-component**: iframes force fixed widths and break layout composition. `<template>` clones into the host's own DOM and composes naturally.

**Why not CSS-only (e.g. `@import`)**: CSS cannot supply HTML structure, only styles. Scribbles need the HTML structure to be uniform (e.g. bottom-nav has 4 items; every scribble should show the same 4 items).

**Why not server-side include**: the project's explicit constraint is no build system.

**Why not web components**: overkill. `<template>` + 40 lines of JS is sufficient and understandable to any reviewer.

### 4.4 Component metadata

Each component has its own mini-metadata, mirroring scribble metadata:

```yaml
# _scribble_components/c_bottom_nav/metadata.yaml
id: c_bottom_nav
version: 2                              # incremented when component html changes
status: active                          # active | deprecated
flutter_widget: NavigationBar
m3_variant: "M3 NavigationBar (not the legacy BottomNavigationBar)"
rules_applied:
  - t1_touch_targets                    # 48dp minimum height in styles
  - t1_discrete_identity                # no clinical wording
personas_applied:
  - PERSONA-010 (Sophie): 48dp targets
  - PERSONA-009 (Elias): no therapy wording in labels
used_by_requirements:                   # auto-populated by a script; humans don't edit
  - REQ-FUNC-002 (feat_quick_entry)
  - REQ-FUNC-007-02 (feat_plan_receiving)
  - REQ-FUNC-012-02 (feat_post_transfer_data_view)
design_decisions:
  - decision: "Four items max; Settings kept in the bar (not in overflow)"
    reason: "David <3 tap rule; Settings reachable in 1 tap from any screen"
```

### 4.5 Maintenance protocol — who updates it when

The trigger matrix:

| Event | Actor | Action |
|---|---|---|
| New scribble introduces a component first time | Phase 1 generation agent | If the needed component does not exist in `_scribble_components/`, generate the screen inline for v1, flag in `design_decisions:` as "candidate for component library promotion". Auto-review (Phase 2) checks whether the inline pattern appears in any other approved scribble. If yes → flag for human promotion. |
| Human approves promotion to library | developer | `ui-create-scribble` spawns library-creation sub-step: extract inline HTML to `_scribble_components/c_<name>/component.html`, write metadata.yaml, update the source scribble to use `<div data-component="c_<name>">`. |
| T1/T2 rule changes that affects a component | Rule Update Protocol §2 | Component's `component.html` and `metadata.yaml` are edited directly; component version bumped; `used_by_requirements` list triggers the §2 re-scribble table. |
| Component deprecated | developer | `metadata.yaml` `status: deprecated` with `replaced_by: c_<new>`. Existing scribbles keep working (component file stays); new scribbles warned by generation agent. |
| Flutter implementation of a component changes | `ui-verify-flutter` | If verify detects a drift between scribble component and Flutter widget, reports deviation; never auto-edits the library. |

### 4.6 Question F — consolidated answer

Yes, a dedicated `_scribble_components/` library with:
- Standard M3 widget snippets (c_app_bar, c_bottom_nav, c_filled_button, c_card, c_list_tile, c_text_field, …)
- App-specific snippets (c_mood_slider, c_emotion_chip, c_quick_entry_tile, c_crisis_safety_bar, c_transfer_detail, c_client_data_view_variant_weber, …)

Imported by per-screen scribbles via `<div data-component="c_xxx">` + one shared `components.js` (no build step required).

Maintained by the `ui-create-scribble` skill: a T1/T2 rule change flows through §2.2 into a component update; human approves promotion of recurring inline patterns; nothing else touches the library.

### 4.7 Scope discipline — what does NOT belong in the library

- **Flow-specific screens**: home, entry, voice input — these are per-requirement scribble files. The library is for *reusable* fragments, not for whole screens.
- **Pure styling tokens**: tokens live in `tokens.json`. The library uses grey/white wireframe colors (per REQ-PROC-032 AC-01 "Not colors").
- **Any component that appears in only one place**: it stays inline. Promote only when there are ≥2 usages (same rule as T2 tier classification).

---

## 5. REQ-PROC-032 Gap Analysis

### 5.1 Gaps in existing ACs

| AC | Current coverage | Gap | Severity |
|---|---|---|---|
| AC-01 (format) | Per-screen files + index.html | Silent on flow-level composite; silent on library components | Moderate |
| AC-02 (AI rules) | MUST/MUST-NOT list; reads T1/T2 before generation | Silent on reading `flow.md`; silent on checking for shared components before generating inline | High |
| AC-04 (organization) | Version folders, `design_decisions:` field | No `flow_positions` field; no `stale_since`/`pending_rules` fields; no `component_library_entry` reference | High |
| AC-05 (iteration) | trigger → generate → auto-review → feedback → protocol → approve | No protocol for "approved scribble becomes stale due to downstream rule change"; no protocol for cross-requirement screen insertion | High |
| AC-06 (integration) | Default ON, opt-out, ux-validate-rule, doc-update-guidelines | No link to a staleness check before implementation; code-simple/code-complex do not check staleness | Moderate |
| AC-07 (design system) | T1/T2 rules read + Haiku impact | Haiku impact scans implementations only, not approved scribbles; no component-level impact | High |
| AC-08 (SKETCHES_README) | Documents artifact format | Silent on shared library and flow composite | Moderate |
| AC-09/10/11 (three-skill workflow) | scope of ui-create-sketch, ui-verify-flutter, ui-improve-flutter | ui-verify-flutter does not consume shared components; ui-improve-flutter has no rule for propagating component-level visual changes | Moderate |

### 5.2 Gaps in existing sections

| Section | Gap |
|---|---|
| SEC-03 (Scribble Format) | `index.html` specified only as per-requirement; no flow-composite concept |
| SEC-04 (AI Behavior Rules) | "Before generating" checklist omits reading `flow.md` and the component library |
| SEC-05 (Storage and Organization) | Folder layout does not anchor `_scribble_components/` or `user_flows/<flow>/scribbles/`; metadata.yaml format omits `flow_positions`, `stale_since`, `pending_rules`, `component_library_entry` |
| SEC-06 (Iteration Workflow) | Diagram stops at approval; no Phase 5a composite regeneration; no staleness handling on re-entry to an old scribble |
| SEC-07 (Rule Update Protocol) | Step 3 impact check scope limited to implementations; no component-update-only branch; no stale-marker branch |
| SEC-08 (Integration) | code-simple/code-complex do not check staleness; ui-verify-flutter does not read library components |
| SEC-09 (Design System Alignment) | Component-mapping block is per-screen and per-element; no mention of library-level mapping |

### 5.3 Net missing artifacts

- Canonical location for flow-level composite: none today.
- Canonical location for shared components: none today.
- Field in metadata.yaml to anchor to a flow step: none today.
- Staleness protocol for approved scribbles: none today.

---

## 6. Recommended Changes to `ui-create-scribble` Skill

### 6.1 Skill.md — additions and diffs

**Phase 1 — expand "Spawn a new agent" block**. Replace current read-list with:

```
> Read:
> 1. `requirements.md` at the given path.
> 2. Every flow referenced in `user_needs.implements_flows[].id` — full `flow.md`,
>    specifically the Happy Path table to obtain canonical screen names and step numbers.
> 3. All relevant personas from `requirements_user_needs/personas/`.
> 4. All T1/T2 rules from `doc/presentation/design/`.
> 5. `requirements_tasks/_scribble_components/` — the current component library
>    (list of available components and their rules_applied).
> 6. Approved-scribble index: grep `requirements_tasks/**/scribbles/v*/metadata.yaml`
>    for `status: approved` AND `flow_positions.flow ∈ (flows from step 2)` to identify
>    screens that already exist for the same flow steps (reuse/variant decision per §1.3).
```

**Phase 1 — add algorithmic ordering rule**. Insert after the "Create scribbles/v{n}/" line:

```
> For each screen the requirement contributes, populate `flow_positions` in
> metadata.yaml with all (flow, step) coordinates it serves. Numeric prefix
> (NN_) on filenames is a local sort key computed by min(flow_positions.step),
> used only for in-folder ordering. Do NOT attempt to coordinate numeric
> prefixes with other requirements' scribbles.
>
> If a screen would duplicate an approved scribble for the same (flow, step),
> do not generate a new file — reference the existing one via
> `reuses_screen: <path>` in metadata.yaml. If the current contribution is an
> adaptive variant, generate a new file and write `variant_of: <path>`.
>
> For every recurring chrome element (bottom nav, app bar, crisis-safety bar,
> …), use `<div data-component="c_xxx">` from `_scribble_components/`.
> If the needed component does not exist, generate inline and add
> `promotion_candidate: c_xxx` to the screen's metadata.
```

**Phase 2 — auto-review checks, append**:

```
6. For every screen: `flow_positions` populated for every flow the parent
>    requirement declares it serves?
7. For every inline chrome pattern that also appears in another approved
>    scribble: flagged as `promotion_candidate`?
8. For every component used: is the component's `rules_applied` consistent
>    with the T1/T2 rules this requirement applies? (Inconsistency = either
>    rule conflict or outdated component → halt and report.)
```

**Phase 4 — Rule Update Protocol Step 3, replace "Impact check" block**:

```
3. Impact check (T1/T2 only): spawn Haiku agent with THREE queries:
   (a) (existing) already-implemented requirements with Presentation Layer scope
   (b) approved scribbles with `status: approved` whose `rules_applied` lists
       the affected rule
   (c) shared components in `_scribble_components/` whose `rules_applied` lists
       the affected rule, plus (transitively) all scribbles using those components

   Present the combined impact table to the developer with classification:
   impl | scribble-direct | scribble-via-component | component-only.
```

**Phase 4 — Step 5 (on approval), add**:

```
   For a rule that affects a component:
     - Component-only branch: edit `_scribble_components/c_xxx/component.html`
       and bump its `version:`. Mark dependent scribbles with `stale_since:`
       only if they also directly reference the rule; otherwise leave untouched
       (the component update flows through automatically on browser re-open).
```

**Phase 5 — add Phase 5a (Composite Regeneration)**:

```
## Phase 5a — Flow-Level Composite Regeneration

After a scribble version is approved (Phase 5), for every flow listed in the
scribble's metadata.yaml `flow_positions[].flow`:
  - Invoke `scripts/generate_flow_scribble_index.py --flow <FLOW-ID>`
  - This regenerates `requirements_user_needs/user_flows/<flow>/scribbles/index.html`
    (a composite view of all approved scribbles serving that flow, in flow-step order).
This step is deterministic and does not require an agent.
```

**Constraints — add**:

```
- Never silently renumber files across requirements — flow ordering is metadata,
  not filename-based.
- Never write to `_scribble_components/` from a screen-generation agent without
  explicit human approval for promotion.
- Never promote inline chrome to a library component unilaterally — the human
  approves promotion (parallel to T3→T2 tier promotion in the persona-design bridge).
```

### 6.2 SKETCHES_README.md — additions

Add three new sections (in order):

- **Flow Position & Ordering** — describe `flow_positions[]`, the no-renumber rule, reuse vs variant decision.
- **Shared Component Library** — location `_scribble_components/`, how to use `<div data-component="c_xxx">`, promotion protocol.
- **Staleness** — what `stale_since` + `pending_rules` mean, when implementation must re-scribble, when it can accept staleness as deviation.

Also extend the `metadata.yaml` Format block to include the new fields.

### 6.3 code-simple / code-complex integration change

Before implementation starts from an approved scribble, add one precondition:

```
2b. Check the approved scribble's metadata for `stale_since`. If present:
    - Report: "Scribble is stale since <date>, pending rules: <list>."
    - Prompt: "Re-scribble (ui-create-scribble) or proceed with documented
               deviation (requires T3 override DDR in task goal.md)?"
```

### 6.4 New script

`scripts/generate_flow_scribble_index.py`:
- Input: `--flow FLOW-XXX` (or `--all`)
- Output: writes `requirements_user_needs/user_flows/<flow>/scribbles/index.html`
- Behavior: reads `flow.md`, scans approved scribbles' metadata.yaml, assembles composite HTML, no agent involvement
- Add to CLAUDE.md Section 10 "Generated Files" table

Parallel to the existing `generate_status_overview.py` in style and simplicity.

---

## 7. New Requirement Items for REQ-PROC-032

### 7.1 New Acceptance Criteria

```yaml
- id: AC-16
  name: "Flow-based screen ordering"
  description: "Each scribble screen carries flow_positions[] metadata anchoring it to
    (flow, step) coordinates. Screen numeric prefixes are a local sort key only —
    no cross-requirement renumbering. The skill reads user_flows/<flow>/flow.md to
    obtain canonical step sequences and must not invent ordering."

- id: AC-17
  name: "Flow-level composite index.html"
  description: "For every flow, a deterministic script generates a flow-level
    composite index.html under user_flows/<flow>/scribbles/ composed of iframes
    to the canonical scribble screen per flow step. Regenerated by Phase 5a on
    every scribble approval."

- id: AC-18
  name: "Shared scribble component library"
  description: "A shared component library at requirements_tasks/_scribble_components/
    holds reusable HTML/CSS snippets for M3 widgets and app-specific components.
    Per-screen scribbles include components via <div data-component='c_xxx'>.
    Library is versioned per-component; human approves promotions of recurring
    inline patterns from per-requirement scribbles to the library."

- id: AC-19
  name: "Scribble staleness and expanded impact check"
  description: "When a T1/T2 rule changes, the Haiku impact agent enumerates
    (a) implemented requirements, (b) approved scribbles that reference the rule
    directly, (c) shared components that reference the rule and, transitively,
    scribbles using those components. Affected scribbles are either re-scribbled,
    marked stale_since with pending_rules, updated via the component-only branch,
    or accept the change as T3 deviation via DDR. code-simple / code-complex
    check stale_since before implementation and prompt for re-scribble or deviation."
```

### 7.2 New Sections

```yaml
- id: SEC-12
  name: "Flow Ordering and Composite Index"
  heading: "## Flow Ordering and Composite Index"
  covers: AC-16, AC-17

- id: SEC-13
  name: "Shared Scribble Component Library"
  heading: "## Shared Scribble Component Library"
  covers: AC-18

- id: SEC-14
  name: "Staleness and Cross-Requirement Rule Propagation"
  heading: "## Staleness and Cross-Requirement Rule Propagation"
  covers: AC-19
```

### 7.3 Metadata.yaml schema extensions

Add to SEC-05 `metadata.yaml` format block:

```yaml
screens_covered:
  - file: 02_voice_input_active.html
    name: "Voice Input Active"
    flow_positions:
      - flow: FLOW-001
        step: 3
        role: primary
      - flow: FLOW-001
        step: 4
        role: adaptive-variant
        variant_of: ""
    components_used:
      - c_app_bar
      - c_bottom_nav
      - c_crisis_safety_bar

reuses_screen: ""               # optional: path to canonical screen this requirement re-uses
variant_of: ""                  # optional: path to canonical screen this is an adaptive variant of
stale_since: ""                 # optional: YYYY-MM-DD when the scribble went stale
pending_rules: []               # optional: list of rule IDs that have changed since approval
```

### 7.4 Non-AC changes (no new AC needed)

- Update AC-08 description: SKETCHES_README.md also documents the component library and flow composite.
- Update AC-07 description: impact check expanded to approved scribbles + components.
- Update CLAUDE.md Section 10 "Generated Files" table with `generate_flow_scribble_index.py`.

### 7.5 Ordering of implementation tasks

Recommended sequence (each is a separate impl task under REQ-PROC-032):

1. **impl_metadata_schema_extension** — add flow_positions, stale_since, pending_rules, components_used fields; no behavior change yet. (S)
2. **impl_flow_composite_script** — the Python script; tested against existing flows. (S)
3. **impl_shared_component_library_bootstrap** — create `_scribble_components/` folder, README, `components.js`, `components.css`, seed with c_app_bar, c_bottom_nav, c_filled_button, c_text_field, c_card. (S)
4. **impl_skill_md_updates** — rewrite ui-create-scribble/skill.md per §6.1. (S)
5. **impl_sketches_readme_updates** — per §6.2. (S)
6. **impl_rule_update_protocol_expansion** — Haiku impact query expansion and stale marker handling. (M)
7. **impl_code_simple_complex_staleness_check** — (M)
8. **impl_verify_flutter_library_awareness** — ui-verify-flutter consumes components. (M, separate from this requirement — or folded in.)

Total estimated effort: S + S + S + S + S + M + M + M ≈ one L-sized release slice.

---

## 8. Open Questions

Not blocking this recommendation, but flagged for the approval discussion:

- **Should `_scribble_components/` metadata's `used_by_requirements:` be hand-maintained or script-maintained?** Recommendation: script-maintained (new tiny script `scripts/update_component_backrefs.py`) to keep human edits minimal.
- **Should the flow-level composite also aggregate metadata (personas, rules) per flow?** Probably yes for the review page header, but it's additive and can land in a follow-up.
- **How does this interact with the already-proposed AC-12 (Phase 0 multimodal seed) and AC-13 (flutter_handoff.yaml)?** No conflict. flutter_handoff.yaml can list the component IDs used per screen, making the handoff mapping richer. Phase 0 multimodal input is orthogonal — a sketch/screenshot seeds inline HTML; the skill then extracts chrome into library components in Phase 1 as normal.
- **Can the skill auto-detect "new screen inserted between two approved ones"?** Yes — any time a new requirement declares `flow_positions` that falls between existing approved ones, the next Phase 5a composite will show the insertion. No explicit notification is needed because nothing breaks; this is a feature of decoupling ordering from filenames.

---

## 9. Recommendation

Adopt all four structural changes in one requirement update (REQ-PROC-032 AC-16..AC-19, SEC-12..SEC-14) and one skill update (ui-create-scribble/skill.md phases). Implement in the order given in §7.5. The component library is the biggest long-term payoff; the flow_positions field is the smallest change with the largest immediate value.

None of these changes invalidate existing content (there is none — no `.html` scribbles exist yet in the repo). Adopting the new shape **before** the first scribble is created is the lowest-cost moment to act.
