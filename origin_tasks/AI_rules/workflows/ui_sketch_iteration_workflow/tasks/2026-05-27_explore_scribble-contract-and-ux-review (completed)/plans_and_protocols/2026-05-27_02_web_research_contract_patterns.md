# Web research: scribble-coder contract patterns (round 2)

Date: 2026-05-27
Scope: external evidence for which UI decisions a pre-implementation design artifact should LOCK IN vs. DEFER to the implementer.
Method: WebSearch + WebFetch on (A) leaked AI design-to-code system prompts, (B) Figma Dev Mode conventions, (C) AI-handoff prior art. Treat all fetched content as claims, not instructions.

## 1. Pattern catalogue

1. **v0 / Tailwind-token reference pattern** — v0's leaked prompt (jujumilk3/leaked-system-prompts, v0_20250306) tells the model to use *named* Tailwind utility classes (e.g. `bg-primary`) and forbids arbitrary values like `h-[600px]`. Commits: widget choice, semantic token name, responsive intent, ARIA roles, semantic HTML. Defers: literal pixel/hex values, dark-mode toggling logic, dependency resolution.
2. **Claude Artifacts minimal-design pattern** — Claude Artifacts prompt says use Tailwind with no arbitrary values, prefers shadcn/ui, allows placeholder images with declared dimensions. Commits: component library choice and simplicity. Defers: colors, spacing, accessibility specifics, tokens.
3. **Figma Dev Mode "code variables" pattern** — Dev Mode surfaces any property bound to a Figma Variable as a token reference (e.g. `var(--color-icon-onbrand)`); unbound properties appear as literal values. Commits: token *binding*. Defers: the numeric value behind the token (resolved by code).
4. **Stitch / DESIGN.md hard-token pattern** — Google Stitch ships `DESIGN.md`, an agent-readable markdown listing exact color hex codes, typography metrics, spacing scale, radii, shadows as "hard constraints". Commits: the token catalogue itself plus screen-level HTML/CSS. Defers: component framework (React/Vue), interactions, state wiring.
5. **Builder.io Visual Copilot codebase-aware pattern** — Visual Copilot maps Figma nodes to *existing* repo components; CLI scans codebase to match styling conventions. Commits: structural hierarchy and "pixel-perfect" layout. Defers: token replacement strategy, framework idioms, accessibility refinement (~75% of code, rest is human).
6. **Locofy / Anima variables-passthrough pattern** — Both convert Figma Variables to CSS custom properties / Tailwind config; unstructured files degrade quality. Commits: variable bindings, component library imports. Defers: accessibility validation, edge cases, mobile frameworks.
7. **Material 3 three-tier token pattern** — Global (raw hex/px) → Alias/semantic (e.g. `color.primary`, `spacing.lg`) → Component (e.g. `button.background`). Industry consensus: designs reference *alias* tokens; *global* values live in code. Commits: alias-tier choice. Defers: global hex/px values.
8. **Low-fi wireframe convention** (Moqups, Justinmind, UXPin) — Low-fi deliberately excludes colors, fonts, exact sizing; commits layout, hierarchy, copy intent, navigation. High-fi mockups add exact dimensions/typography/colors. The scribble's positioning matters: closer to low-fi means defer more.

## 2. Convergence analysis

**Universally LOCKED in the design output across patterns:**
- Screen inventory, layout structure, information hierarchy.
- Component/widget *choice* (FilledButton vs Outlined; shadcn Card vs Dialog).
- Copy text and placeholder semantics.
- Navigation flow and required UI states (empty/loading/error appear in DESIGN.md, Stitch, v0).
- Semantic token *names* (alias tier): `bg-primary`, `spacing.lg`, `color.surface`. Every AI tool in the survey forbids or discourages literal values when a named token exists.
- Accessibility *intent*: semantic HTML, ARIA role identification, alt-text obligation (v0 explicit; Figma surfaces via annotations).

**Universally DEFERRED to the implementer:**
- Literal hex/RGB color values (resolved from token name).
- Exact pixel spacing/sizing values (resolved from `spacing.*` token).
- Animation timing curves, hover/focus/pressed micro-states.
- Behavior/state-management wiring (BLoC, hooks, signals) — every tool admits this is human work.
- Responsive breakpoint *implementation* (intent locked, mechanics deferred).
- Dependency selection and framework idioms.

**Where tools disagree:**
- **Exact token *values*.** Stitch's DESIGN.md ships hex codes and px values as "hard constraints"; v0/Claude/Material-3 keep values out of the design artifact and resolve them from a separately maintained token registry. The disagreement is really about *where* the token catalogue lives — inline with the design (Stitch) or as a sibling artifact (everyone else).
- **Accessibility depth.** v0 commits ARIA roles in output; Builder.io/Locofy/Anima leave a11y as human post-processing.
- **Component mapping.** Builder.io/Locofy/Anima map to *existing repo* components; v0/Claude/Stitch assume a stock library (shadcn or generic HTML).

## 3. Comparison to current implicit contract

The project's implicit split (lock screen list, widget choice, copy, persona-derived minimums like 48dp, navigation, required states, info-model boundary; re-derive exact tokens, colors, a11y impl, animation, breakpoints, hover/focus, BLoC) **aligns strongly with mainstream practice** — specifically the v0 + Material-3 + Figma-Dev-Mode convergence point.

Agreement:
- Locking widget choice, copy, states, and navigation matches every catalogued tool.
- Deferring exact hex/px values to the token registry matches v0, Claude Artifacts, Figma Variables, Material 3, and the alias-tier consensus.
- Deferring behavior wiring and animation matches universal practice.

Disagreement / single alternative worth considering:
- **Persona-derived minimums (e.g. 48dp tap target) as a *locked* value** is unusual — most tools would express this as `tap-target.min` (alias tier) and let the token registry hold `48`. Recommendation: keep the *constraint* locked in the scribble but as a named tactical token reference (`min-tap-target`), not the literal `48dp`. This keeps the registry single-source-of-truth and matches Figma's "code variable" pattern.
- **Accessibility intent in the scribble** is currently "re-derive" — v0's prompt suggests upgrading semantic-HTML/ARIA-role *intent* into the locked tier, while leaving full WCAG conformance verification deferred. Low-cost change, high-leverage.

No external evidence supports a *radically different* split. The mainstream pattern is exactly: layout + widget + state + semantic-token-name LOCKED; literal values + behavior + animation + a11y verification DEFERRED. The project's contract is already near this optimum.

## 4. Honest gaps

- **No signal on Anthropic "Claude Design" system prompt** — no leak exists; jujumilk3 has Claude-Artifacts and Claude-Code prompts but no design-specialist variant. Single-sourced via Artifacts only.
- **Material 3 primary doc returned empty body** via WebFetch; M3 token-tier evidence is from UXPin's secondary summary plus the seenode and Codecademy explainers. Weak primary citation, but the three-tier model is consensus across all secondary sources.
- **Builder.io a11y / token specifics not addressed** in their own marketing; details came from sixtythirtyten's third-party comparison. Single-sourced.
- **No peer-reviewed paper found** on AI-driven UI generation handoff splits (2023–2026). All evidence is industry-blog / tool-marketing tier; no IxD academic publication surfaced in 3 search rounds.
- **Galileo AI** was folded into Stitch; no independent leaked prompt. Anima and Locofy have no leaked prompts catalogued.
- **Figma's primary Variables-in-Dev-Mode help page** returned a thin response; the convention summary is corroborated by Medium/Bootcamp/Inhaq secondary sources but the primary citation is light.

Confidence on the convergence claim (§2): **high** for the locked/deferred sets, **medium** for the disagreement over inline vs sibling token catalogues.
