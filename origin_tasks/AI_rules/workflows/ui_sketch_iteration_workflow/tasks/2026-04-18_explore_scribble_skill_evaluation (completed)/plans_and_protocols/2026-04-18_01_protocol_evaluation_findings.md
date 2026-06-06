---
agent: claude-opus-4-7
date: 2026-04-18
task: TASK-PROC-032-02
status: complete
---

# Evaluation: Is `ui-create-scribble` Still State-of-the-Art?

## 1. Executive Summary

The `ui-create-scribble` skill is **partially outdated in its generation mechanics but structurally ahead of the market in persona-constraint tracking and tiered rule anchoring**. The mainstream has moved from "AI generates an HTML wireframe, developer reads it, then writes Flutter code" toward "AI generates Flutter widgets directly from prompts or sketches" (Google Stitch, Claude Design, direct prompt-to-code). However, every prompt-to-code tool surveyed treats UI as generic SaaS/consumer patterns — none of them track the accessibility, motor, and cognitive constraints of named personas, and none anchor design decisions into a tiered rule system. Those two properties are this project's architectural moat and the reason the skill should not be replaced. **Recommendation: UPDATE**, not replace — modernize the input side (multimodal, optional Stitch/Claude Design as draft generators) and the output side (structured Flutter handoff prompt), while preserving the scribble artifact, auto-review loop, and Rule Update Protocol as-is.

## 2. Current Approach Assessment

### 2.1 Honest Strengths (2026 perspective)

1. **Persona-constraint tracking is unique.** No surveyed tool embeds `PERSONA-002 (Max): blank-field paralysis → structured prompts only` or `PERSONA-007 (Hanna): absolute darkness → true black backgrounds` directly into the design artifact. Every commercial alternative produces generic designs and expects the team to retrofit accessibility afterwards.
2. **Tiered rule anchoring (T1/T2/T3) is unique.** The skill's rule-update protocol with Haiku impact check and explicit human approval before a rule becomes T1/T2 is a form of governed design-system evolution that no tool replicates. Stitch, Claude Design, and Locofy all assume the design system exists upstream and is static for a given session.
3. **HTML-as-LLM-context is still valid.** MockFlow's WireframePro MCP (new in 2026) validates the premise — they now explicitly export wireframes as structured AI prompts for Claude Code. HTML/CSS remains well-represented in training data and is the lowest-friction structural format an LLM can reason about.
4. **Disposability and co-location.** Committing scribbles next to `requirements.md` creates a permanent design-decision trail. Flutter-native tools (Stitch, Locofy) produce production code that then becomes the only record — there is no separate "design artifact" to reference later.
5. **Auto-review loop.** Automatic regeneration after every odd version, checking ACs/personas/rules before the user is asked to review, catches structural gaps that every "single-shot prompt-to-code" tool misses entirely.
6. **Integration with sibling skills.** `ux-validate-rule`, `doc-update-guidelines`, and `requ-explore` interlock cleanly with the scribble workflow. External tools live outside this ecosystem.

### 2.2 Honest Weaknesses (2026 perspective)

1. **Blank-page problem.** The current flow assumes text-only input ("read requirements.md, generate HTML"). Developers frequently have a rough sketch, a screenshot from a reference app, or a napkin drawing they'd like to seed v1 from. Claude's vision capabilities (used widely in 2026) are not leveraged.
2. **No integration with Flutter-native generators.** Google Stitch exports Flutter widgets natively with design-system import and 5-screen canvas. For screens where Stitch produces a usable starting point in seconds, the skill currently insists on generating HTML from scratch — slower and with less Flutter-specific fidelity.
3. **Indirect Flutter handoff.** After approval, the scribble's component-mapping block is human-readable guidance. The Flutter implementation agent reads `scribble.html` and infers widgets. In 2026, MockFlow's pattern is to emit a **structured prompt** (YAML/JSON: element → widget → constraints) that the implementation agent consumes directly. The current skill does neither — it produces HTML for humans, not context for agents.
4. **No awareness of Claude Design.** Claude Design (launched 2026-04-17 — one day before this evaluation) generates wireframes from prompts and can export directly to Claude Code. It is the closest analog to `ui-create-scribble` and lives in the same vendor pipeline the project already uses. The skill does not mention it and cannot delegate to it.
5. **No Flutter Widget Previews loop.** Flutter 3.35 (August 2025) ships Widget Previews for validation without full-app builds. The three-skill workflow verifies *after* implementation (`ui-verify-flutter`) but doesn't use Previews as an intermediate structural check.
6. **Per-version full regeneration is expensive.** Auto-review regenerates the entire scribble even when only one screen changed. Fine for small features; costly for 8-screen flows.

## 3. Alternatives Landscape

| Approach | Iteration Speed | Flutter Fidelity | Design System Alignment | Persona Constraint Tracking | Skill-Ecosystem Integration | Cost / Complexity |
|---|---|---|---|---|---|---|
| **Current HTML scribble** | Medium (agent per version, full regen) | Low–Medium (HTML→Flutter via mapping table; structural only) | Medium (component mapping + T1/T2 rules read from `doc/`) | **Strong** (HTML comments with persona IDs; auto-review verifies) | **Strong** (native to `ux-validate-rule`, `doc-update-guidelines`, `requ-explore`) | Low (no external tools, no licenses) |
| **Google Stitch → Antigravity / Claude Code (MCP)** | Very High (text/sketch → Flutter widgets directly) | **High** (native Flutter export; design-system import since Mar 2026) | Medium–High (imports design system once per session) | **None** (no persona model) | None (requires new MCP wiring; orthogonal to current skills) | Medium (Gemini cloud dependency, MCP setup, governance decisions) |
| **Claude Design → Claude Code handoff** | Very High (same vendor as Claude Code; already in the pipeline) | Medium (generates HTML/visuals; Flutter rendering still needs our context) | Medium (depends on prompt context and loaded tokens) | **None** (generic UI patterns) | **High potential** (single-vendor pipeline; can be invoked from within existing agents) | Low (already using Claude Code; no new vendor) |
| **Figma + Locofy** | Low–Medium (requires Figma design first; Lightning/Classic modes) | **Very High** (production Flutter/Dart code, design-token accurate) | **Very High** (Figma is the design system source of truth) | None | None (tool-external; `requirements_tasks/` and `doc/` are invisible to it) | High (Figma license, Locofy subscription, team workflow shift) |
| **Direct prompt-to-code (Claude Code + CLAUDE.md + tokens, skip design artifact)** | Very High (skip structural step) | Medium–High (with good context loaded) | Medium–High (tokens + design rules in context) | Weak (personas referenced in CLAUDE.md but no structured design artifact) | Low (no design artifact to iterate on; review happens on code only) | Low |

### 3.1 What the comparison reveals

- **No tool dominates on every axis.** Stitch wins on Flutter fidelity + iteration speed. Figma+Locofy wins on design-system alignment. The current skill wins on persona tracking and ecosystem integration. None wins on all five.
- **Persona tracking is the only column where the current skill is alone.** Every commercial tool scores None. This is not a feature gap in the commercial tools — it is a deliberate product decision: they target teams that have not built persona-grounded design rules.
- **"Skill-ecosystem integration" is the second column where the current skill leads.** External tools cannot invoke `ux-validate-rule` or update `doc/presentation/`. Adopting one would mean rebuilding the governance layer outside that ecosystem, or accepting that new rules are not governed.

## 4. Community Experience Summary

Practitioners in 2025–2026 cluster into four adoption patterns, per the surveyed sources:

1. **Prompt-to-code enthusiasts** (Bolt.new, Lovable, v0, DreamFlow): skip design artifacts entirely, iterate on live code. Works well for React/Web; emerging for Flutter (DreamFlow). Pain point: output looks generic; accessibility and consistency are afterthoughts ("the purple design aesthetic" Addy Osmani references).
2. **Design-to-code teams** (Figma + Locofy / Stitch): keep a dedicated design surface, export to code. Works well when a designer and developer are on the same team. Pain point: design system drift between Figma and production code remains unsolved for mobile.
3. **Context-first teams** (Addy Osmani's 2026 workflow, Claude Code guides): invest in CLAUDE.md, design tokens, and architectural conventions. No separate design artifact — the "design" is encoded in prompts + tokens. Pain point: no way to review structure before code is written.
4. **Structured-wireframe-as-LLM-context teams** (MockFlow MCP, academic WireGen research): use a mid-fidelity artifact (HTML/wireframe) specifically as structured context for the LLM, not as a human-facing mockup. Pain point: maintaining the artifact's fidelity to requirements as the design evolves.

The `ui-create-scribble` skill sits most naturally in **cluster 4 with elements of cluster 3**. This is a small but growing cluster — the MockFlow 2026 MCP launch and Anthropic's Claude Design launch both validate this direction.

Key pain points that persist across all clusters and apply to this project:
- **Persona grounding is not solved by tools.** Teams that care about accessibility/cognition/motor constraints still hand-annotate.
- **Design system evolution is governed by humans.** No tool will invent a new T1 rule correctly; they apply existing ones.
- **Multi-screen consistency.** Tools that generate one screen at a time (Uizard, v0) drift; tools that generate canvases (Stitch 5-screen, Figma Make) drift less. The scribble's `index.html` + auto-review is solving the same problem from a different angle.

## 5. Recommendation: **UPDATE**

**Keep the skill. Do not replace it.** The two properties that justify its existence in this project — persona-constraint tracking and tiered rule anchoring with governed evolution — are not available in any surveyed tool, and they are central to this project's identity (seven custom personas PERSONA-001…PERSONA-007; `doc/presentation/design/` tier structure; Clean Architecture with Material 3 + BLoC).

However, the generation-side mechanics and handoff-side mechanics are both behind 2026 state-of-the-art. **Update the skill** to modernize these two edges while preserving the middle (the scribble artifact, auto-review, and rule protocol).

### 5.1 Why not replace with Google Stitch?

Stitch produces higher-fidelity Flutter output faster. But:
- It has no concept of `PERSONA-007` darkness requirements — you would layer our rules *on top* of Stitch output, which is what the scribble format already does.
- It lives outside `requirements_tasks/` and `doc/`; new rules cannot flow through `doc-update-guidelines`.
- It introduces a Gemini cloud dependency in a project currently using Claude Code as primary orchestrator.
- Adopting it wholesale would mean rebuilding the governance layer (rule tiers, persona validation, impact check) from scratch.

Stitch is a **better draft generator** than blank-page HTML generation, not a better skill.

### 5.2 Why not replace with Claude Design?

Claude Design launched **one day before this evaluation** (2026-04-17). Maturity is unknown. It lives in the same vendor pipeline as Claude Code, which is attractive. But the same objection as Stitch applies: it does not track personas or anchor rules.

Claude Design is a **candidate component** inside the updated skill, not a replacement.

### 5.3 Why not replace with direct prompt-to-code?

This is the most tempting option — the current conversation already uses Claude Code, and with CLAUDE.md + design tokens, Flutter widgets can be generated directly. But:
- **No intermediate structural review.** Bugs that would have been caught in an HTML scribble review now surface only during code review or runtime.
- **No auto-review of persona constraints.** A Flutter widget agent does not naturally re-check whether all seven personas' constraints are satisfied.
- **No design decision record.** Decisions encoded in code are lost to `git blame`; decisions encoded in `metadata.yaml` survive as queryable design history.

Direct prompt-to-code is appropriate for **trivial UI changes** (the current `skip_scribble: true` opt-out already handles this).

## 6. Concrete Next Steps (if UPDATE is approved)

The following five changes should be packaged as implementation tasks under REQ-PROC-032. They are ordered by value-to-effort ratio, highest first.

### Change 1 — Phase 0: Accept Multimodal Input (High value, Low effort)

**What**: Before Phase 1 (HTML generation), the skill checks whether goal.md or the task folder contains:
- `inputs/sketch.{png,jpg,pdf}` — a hand-drawn sketch or napkin drawing
- `inputs/reference.{png,jpg}` — a screenshot from a reference app or competitor

If present, the Phase 1 generation agent receives these as vision input alongside `requirements.md` and personas. Claude's vision capability extracts layout structure, which informs the HTML scribble. If absent, Phase 1 proceeds as today.

**Why**: Solves the blank-page problem for complex screens. Developers frequently have a rough visual idea before they can describe it in words. This is consistent with 2026 community practice where multimodal input is standard.

**Source support**: Claude vision is widely adopted for screenshot-to-wireframe and screenshot-to-code workflows in 2026 (MockFlow MCP, Claude App Builder blog, Claude Design launch).

**Spec change**: Add `## Phase 0 — Optional Multimodal Seed` to skill.md. Update REQ-PROC-032 with a new AC: "AC-12: Optional multimodal input seed (sketch/screenshot) is accepted via `inputs/` folder and informs Phase 1 generation."

### Change 2 — Structured Flutter Handoff Prompt (High value, Medium effort)

**What**: After approval (Phase 5 today), the skill emits `scribbles/v{approved}/flutter_handoff.yaml` containing, per screen:

```yaml
screen: 01_home_night_mode
elements:
  - html_selector: "header.app-bar"
    flutter_widget: AppBar
    material3_variant: "surface tint"
    persona_constraints:
      - PERSONA-007: dark surface, no tint override
    rules_applied:
      - t1_touch_targets
      - t1_dark_mode
    data_binding: "from HomeBloc state.title"
  - html_selector: "button.primary.submit"
    flutter_widget: FilledButton
    ...
```

This file is consumed directly by the Flutter implementation agent (code-simple/code-complex) as structured context, alongside the human-readable HTML scribble.

**Why**: The current handoff is implicit ("Flutter agent, read the HTML and infer"). 2026 practice (MockFlow MCP) emits a structured prompt so the implementation agent gets unambiguous context. Reduces implementation drift and makes `ui-verify-flutter` easier (it can mechanically compare handoff spec vs actual widgets).

**Source support**: MockFlow's 2026 WireframePro MCP pattern; explicit recommendation of structured prompts for Claude Code.

**Spec change**: Add Phase 6 "Emit Flutter Handoff" to skill.md. Add AC-13 to REQ-PROC-032. Update `ui-verify-flutter` skill to consume `flutter_handoff.yaml` instead of parsing HTML comments.

### Change 3 — Optional Stitch / Claude Design as Draft Generator (Medium value, Medium effort)

**What**: In Phase 1, before agent A generates HTML from scratch, the skill checks a new config flag `draft_generator` in goal.md:
- `claude_design` — invoke Claude Design with requirements summary, import returned HTML into scribble format, then annotate with personas and T1/T2 rules in a second pass.
- `stitch` — if configured, invoke Google Stitch via MCP, convert Flutter widget output back into HTML scribble for the persona/rule annotation layer.
- `none` (default) — current behavior, generate from scratch.

In all cases, the **output is still a scribble** (HTML + component mapping + persona annotations + metadata.yaml). The external tool is a faster-first-draft generator, not a replacement.

**Why**: For teams and features where Claude Design or Stitch produces a usable draft, this cuts the first-iteration time from minutes to seconds. The persona/rule annotation layer remains ours.

**Source support**: Claude Design export to HTML (directly compatible); Stitch Flutter output can be reverse-mapped to HTML structure via the existing component mapping table.

**Spec change**: Add `draft_generator` field to goal.md YAML schema. Add Phase 1a "Draft Generation (optional)" to skill.md. Document in SKETCHES_README.md. Add AC-14.

### Change 4 — Diff-Based Regeneration (Medium value, Medium effort)

**What**: When only specific feedback items require a regeneration (e.g., "the dark mode contrast on screen 03 is wrong"), the auto-review / next-version agent regenerates **only the affected screen files**, not the whole scribble. `metadata.yaml` tracks per-screen version numbers.

**Why**: Current full-regeneration is expensive for 8-screen features and can introduce unrelated drift. Diff-based regeneration reduces agent tokens per iteration and preserves unchanged screens verbatim.

**Source support**: General 2026 practice in LLM coding workflows (Addy Osmani, Cursor) favors surgical edits over full regeneration.

**Spec change**: Extend metadata.yaml format to track per-screen versions. Update Phase 2 auto-review to classify feedback as "affects screen X" vs "affects all screens". Add AC-15.

### Change 5 — Flutter Widget Previews as Intermediate Check (Low value, Low effort)

**What**: Between implementation and `ui-verify-flutter`, the Flutter implementation agent runs `flutter widget-previews` on the new widgets and captures screenshots. `ui-verify-flutter` then has both the HTML scribble and actual rendered previews to compare.

**Why**: Widget Previews (Flutter 3.35, Aug 2025) let us verify rendered output without a full app build. Catches visual regressions that pure code review misses. Low marginal cost since widget_previews is built-in.

**Source support**: Flutter 3.35 release notes; Code With Andrea newsletter August 2025.

**Spec change**: Minor update to `ui-verify-flutter` skill and workflow docs. No REQ-PROC-032 AC change needed (it's an internal quality improvement).

### 6.1 What explicitly NOT to change

- **Auto-review loop after odd versions** — unique safety net, preserve.
- **Tier classification T1/T2/T3 with Haiku impact check** — unique governance, preserve.
- **Persona constraint annotations in HTML comments** — unique tracking, preserve.
- **`design_decisions:` field in metadata.yaml** — unique continuity mechanism, preserve.
- **Co-location with `requirements.md`, committed to git** — unique audit trail, preserve.
- **`skip_scribble: true` opt-out for trivial changes** — preserve; direct prompt-to-code is the right path for those.

### 6.2 Follow-up implementation tasks to spawn

1. `impl_phase_0_multimodal_input` — Change 1, ~S
2. `impl_flutter_handoff_yaml` — Change 2, ~M
3. `impl_optional_draft_generators` — Change 3, ~M (Claude Design first; Stitch as later option)
4. `impl_diff_based_regen` — Change 4, ~M
5. `impl_widget_previews_integration` — Change 5, ~S

Total effort estimate: ~M+ (one medium feature pass or two small sessions).

### 6.3 Requirement update needed

REQ-PROC-032 is currently `status: active`. It remains `active` (living document). Add AC-12 through AC-15 and new sections for Phase 0, handoff format, and draft generator. `requ-explore` should handle this separately after the recommendation is approved.

## 7. Sources

### Tools and launches
- [Google Stitch Labs](https://stitch.withgoogle.com/) — AI design tool, Gemini-powered
- [Google Stitch AI: Vibe Design and 5-Screen Canvas (2026)](https://tech-insider.org/google-stitch-ai-design-tool-march-2026-update/) — March 2026 update details
- [Google Stitch: Complete Guide (ALM Corp)](https://almcorp.com/blog/google-stitch-complete-guide-ai-ui-design-tool-2026/) — framework export list
- [Introducing Stitch (Google Developers Blog)](https://developers.googleblog.com/stitch-a-new-way-to-design-uis/)
- [Stitch + Antigravity + Flutter (DEV Community)](https://dev.to/techwithsam/stitch-antigravity-flutter-build-apps-with-ai-agents-in-2026-2pei) — MCP integration to Flutter+Dart
- [Claude App Builder Breakthrough (Blockchain News, 2026)](https://blockchain.news/ainews/claude-app-builder-breakthrough-5-free-prompts-to-generate-mobile-apps-from-screenshots-2026-analysis) — Claude Design launch 2026-04-17
- [Claude Design Tutorial: Decks & Wireframes (ComputingForGeeks)](https://computingforgeeks.com/claude-design-tutorial-prototypes-decks-wireframes/)
- [From Claude Code to Figma (Figma Blog)](https://www.figma.com/blog/introducing-claude-code-to-figma/) — production code → editable Figma designs
- [MockFlow: Export Wireframes as AI Prompt for Claude Code](https://mockflow.com/updates/export-wireframes-as-ai-prompt-for-agentic-tools-like-claude-code)
- [MockFlow WireframePro MCP Server](https://mockflow.com/mcp/wireframepro/)
- [Locofy / Penpot / Figma → Flutter](https://www.dhiwise.com/post/how-to-convert-figma-design-to-flutter-code)
- [FlutterFlow AI](https://www.flutterflow.io/ai)

### Comparative analysis and ecosystem
- [AI Prototyping & UX Tools (2026): Design to Working App (vibecoding.app)](https://vibecoding.app/blog/ai-prototyping-ux-tools) — three paradigms framework
- [AI wireframe generators compared: Visily, UX Pilot, Uizard, Figma Make (LogRocket)](https://blog.logrocket.com/ux-design/visilys-ai-wireframing-prototyping/)
- [8 Best AI Wireframe Generators in 2026 (FlowStep)](https://flowstep.ai/blog/ai-wireframe-generators-a-step-by-step-guide/)
- [Best AI for UI/UX Design in 2026 (Banani)](https://www.banani.co/blog/ai-for-ui-design-and-wireframes)
- [AI Design-to-Code Tools: The Complete Guide for 2026 (Banani)](https://www.banani.co/blog/ai-design-to-code-tools)
- [Vibe Design in 2026 (Muzli)](https://muz.li/blog/vibe-design-in-2026-what-ai-generated-ui-means-for-your-work/)
- [Top 10 Wireframing Tools for Fast UX Design (Magic Patterns)](https://www.magicpatterns.com/blog/wireframing-tools)

### Flutter ecosystem (2025–2026)
- [2025: The Year Flutter Met the AI Singularity (Somnio Software)](https://somniosoftware.com/blog/2025-the-year-flutter-met-the-ai-singularity---a-complete-tech-wrap-up)
- [Flutter 2026 Review: UI Thread Merge, GenUI, Cross-Platform (Intercode)](https://intercode.com/blog/flutter-2026-technical-review)
- [My take on Flutter in 2026 (Tomáš Repčík)](https://tomasrepcik.dev/blog/2025/2025-12-14-flutter-2026/)
- [Flutter 3.35, Widget Previews, Flutter MCP Server (Code With Andrea, Aug 2025)](https://codewithandrea.com/newsletter/august-2025/)
- [Claude Code × Flutter: Complete Guide (Claude Lab)](https://claudelab.net/en/articles/claude-code/claude-code-flutter-app-development-complete-guide)

### LLM workflow practice
- [Addy Osmani: My LLM coding workflow going into 2026](https://addyosmani.com/blog/ai-coding-workflow/) — context-first discipline
- [Building AI-driven workflows with Claude Code and Codex CLI (UX Collective)](https://uxdesign.cc/designing-with-claude-code-and-codex-cli-building-ai-driven-workflows-powered-by-code-connect-ui-f10c136ec11f)

### Academic / research
- [Designing with Language: Wireframing UI Design Intent with Generative LLMs (arXiv 2312.07755)](https://arxiv.org/html/2312.07755v1) — WireGen; HTML/CSS wireframes as LLM output format
- [Using LLMs to generate UX Wireframes (Sony Interactive Entertainment)](https://sonyinteractive.com/en/news/blog/using-llms-to-generate-ux-wireframes/)
