# External-Interface Compatibility Analysis (Round 4)

**Task:** TASK-PROC-044-02 · **Date:** 2026-05-29 · **Model:** Opus 4.7
**Input:** developer feedback file `06_feedback.md` raising the "edge of the factory" concern
**Decision needed:** does the proposed internal contract mechanism extend gracefully to external interfaces, OR does it need a different design — and if different, do we know enough NOW to avoid rework?

> Bottom line up front: a separate sibling exploration task is the right home for external-interface contracts, **but** a small compatibility check belongs in THIS task's Round 3 to confirm the internal mechanism won't paint us into a corner. The check passes — the internal format extends cleanly to all 7 surveyed external interfaces — so no rework risk is introduced by proceeding with the internal rollout. Internal-first is safe.

---

## §1 — Inventory: the factory's external interfaces

Information that crosses the factory boundary, in or out, that is NOT skill-to-skill internal:

| # | Interface | Direction | Current channel | Format |
|---|---|---|---|---|
| **E1** | Developer-question response | dev → factory (pull) | `automation/pending_feedback/{TASK_ID}/answer.md` | Free-form markdown matching `TEMPLATE_answer.md` |
| **E2** | Developer-initiated change (product intake) | dev → factory (push) | `product-intake` skill invocation; goal.md authored by `task-create` | Free-form natural language → routed through Persona/Scenario/Flow/Requirement gates |
| **E3** | Developer notes (raw feedback) | dev → factory (push, async) | `automation/inbox.md`, `automation/REFACTOR_ISSUES.md`, `notes.md` alongside flow.md | Free-form markdown |
| **E4** | LLM web research (LLM → web → factory) | factory → web → factory | `WebSearch`/`WebFetch` tools; `ctx7` CLI; bashed `curl` | HTML, JSON, markdown — heterogeneous |
| **E5** | OS-level tooling install | factory → OS → factory | `claude-install-os-tool` skill; `apt`, `pip`, `npm`, `pub` | Network fetch + binary install; tier-A tracking required (REQ-PROC-051) |
| **E6** | Dependency admission (top-level pubspec/manifest) | factory → developer (gate) | `automation/dependency_reviews/` per REQ-PROC-060 | Structured YAML review request |
| **E7** | Produced code → release → user | factory → end-user | `release` skill produces tag + release notes; binary distribution outside factory | Flutter app artifacts (`.apk`, `.exe`, `.app`, web bundle) |
| **E8** | Runtime telemetry / metrics from running app | end-user → factory (none today) | Hypothetical — not currently implemented in this project | TBD |
| **E9** | Optimize-event channel (in-factory but produced by external observers like git hooks, CI logs) | bash hooks / CI → factory | `.factory/optimize/events/*.json` | Structured JSON; consumed by `claude-optimize` |

E8 is hypothetical — listed for completeness only; out of scope.

---

## §2 — Each interface against the internal contract format

The internal contract format from Round 3 D-2 has these fields:

```yaml
contract_version: 1
purpose: ...
derived_from: { required: [], optional: [] }   # each item has source: external|skill:<name>
produces: { required: [], conditional: [] }
quality_criteria: [...]
may_invoke: [...]
side_effects: [{target, action, note}]
preconditions: [...]
postconditions: [...]
```

For each external interface, does this format extend cleanly?

### E1 — Developer-question response

**Trivial fit.** The pending_feedback channel is already file-based and follows a template. Adding a contract.yaml-like declaration would just formalize what TEMPLATE_question.md already implies. The internal format extends with **zero new fields** — the question.md becomes a `produces:` item of the asking skill; the answer.md becomes a `derived_from: { source: external }` item of the resuming skill.

### E2 — Developer-initiated change (product intake)

**Good fit with one extension.** Product-intake's input is **natural language**, not a file. The internal format's `path_or_field` accommodates this by allowing a synthetic origin like `path_or_field: "conversation:intent-statement"` with `source: external`. Slightly stretched but works. A **new field** worth considering: `input_modality: file|frontmatter|conversation|invocation_arg` — explicit kind annotation. This is purely additive and doesn't break the internal-only contracts.

### E3 — Developer notes (raw feedback)

**Same as E1.** Inbox/notes files are already paths; they fit `derived_from: { source: external }` exactly as written.

### E4 — Web research

**Partial fit; needs a discipline.** `WebFetch` returns HTML/JSON that isn't a file path until cached. The internal format's `path_or_field` can hold a URL pattern (e.g. `https://docs.something.com/api/*`) but the consumer's pre-check can't verify URL response shape statically — the response is by-definition variable. This is the same problem the `doc-lookup-dependencies` skill already solves: it caps lookups per task (REQ-PROC-053) and treats web responses as "informational, not authoritative."

**The compatibility implication**: web inputs need a different *postcondition* style. Internal contracts can say "input is a yaml conforming to schema X." Web contracts say "input was fetched from an allowlisted URL pattern; downstream code does not assume schema conformance." This is a **different quality_criteria pattern**, not a different format. The format extends.

### E5 — OS-level tooling install

**Fit, with the same caveat as E4.** `claude-install-os-tool` and the install commands inside agents fetch from external package registries. The format accommodates: `derived_from: { path_or_field: "apt:package-name", source: external, schema: null }`. A package install has no readable post-state to validate without OS introspection, so quality_criteria say "binary exists at expected location" and "binary's --version output matches expected." Same shape, different content.

### E6 — Dependency admission

**Trivial fit.** This IS a structured contract already (`automation/dependency_reviews/`). The internal format extends to it directly — `dependency_reviews/{TASK_ID}/request.yaml` becomes a `produces:` item of the asking skill and `derived_from:` item of the resuming skill, with `source: external` because the developer is the responder.

### E7 — Produced code → release

**Fit, but the postcondition story changes.** The output is no longer a file in `lib/`; it's an artifact bundle (`.apk`, web build). The internal format extends: `produces: [{path_or_field: "build/app/outputs/flutter-apk/*.apk", schema: null}]`. The schema is null because the artifact is binary. Quality_criteria become "build succeeded" / "smoke test passed" / "size within budget" — bounded checks, not schema conformance.

### E8 — Runtime telemetry

**Hypothetical; would fit by analogy to E9.** Same pattern as event files.

### E9 — Optimize-event channel

**Fit.** Already structured JSON. Internal format extends to it: producers of events declare them in `side_effects:`; `claude-optimize`'s `derived_from:` lists them.

---

## §3 — What the survey reveals

### 3.1 The format extends cleanly to all 7 (8 if you count E9)

No external interface requires a fundamentally new field or a structurally different schema. Each one fits the existing `derived_from`/`produces` with either:
- `source: external` (developer/OS/web/user) and `schema:` either pointing to a known shape or `null` for unstructured/binary inputs
- A small additive field `input_modality:` (only needed for E2 product-intake's "conversation" input — not a blocker; can be added later)

This means **the internal mechanism does not paint us into a corner.**

### 3.2 The differences are in `quality_criteria` style, not format

External interfaces shift the *kind* of postcondition checks:
- **Internal**: "output yaml conforms to `.claude/schemas/X.yaml`" — strict
- **External**: "command exited 0", "URL fetched", "build artifact exists at path", "developer answered" — bounded checks of external state

These are different *contents*, not different *fields*. Same format, different quality_criteria values.

### 3.3 Two new threads emerge — separate concerns

External-interface work, if and when undertaken, includes:

**Thread A — Standardize external-interface declarations.** Even if every external interface already fits the contract format, today they're not declared anywhere. Authoring contract.yaml-equivalents for the 7-9 external interfaces would surface gaps (e.g. is `WebFetch` allowlisted? are dependency installs reviewed?). This is a **policy/governance** exercise more than a mechanism design.

**Thread B — Define the postcondition vocabulary for external state.** A controlled vocabulary of "external-state checks" — `command_exited_zero`, `url_returned_2xx`, `file_exists_at_path`, `developer_responded`, `package_installed_at_version`. The internal format references it via `quality_criteria:`. This is the only piece of new design work, and it's small (one YAML file enumerating the vocabulary + maybe 6-10 small validator scripts).

Both threads are **independent of the internal mechanism's rollout**. Wave 1 can land without either; they get added later without altering existing contracts.

---

## §4 — Should we do the work NOW or as a sibling task?

### Cost of doing it now (in this task)

- Add ~40 contract.yaml-style declarations for the 7-9 external interfaces (~600 lines of YAML)
- Define the external-state check vocabulary (~100 lines)
- Write ~6 small validator scripts
- Document the inventory + policy

Estimated 1-2 sessions of focused work. Not trivial.

### Cost of doing it as a sibling exploration task

- Spawn a new explore task under REQ-PROC-044 (or a new requirement for external interfaces)
- Same content as above, but isolated context — fresh session can focus solely on external interfaces
- Allows internal-rollout Wave 1 to start in parallel

### Risk of NOT doing it now

The compatibility check above says: **none, structurally.** The internal format extends. The only theoretical risk is if a future external-interface design decides "actually, we want a fundamentally different declaration style" — but that's bad design, not a mechanism limitation. Any sane external-interface design would re-use the internal format with the additive `input_modality:` field.

### Recommendation

**Sibling task, not in-scope here.** Reasons:
1. The compatibility check confirms zero rework risk on the internal side
2. External interfaces are a different audience (policy/governance) — different cognitive load than internal mechanism design
3. The user's instinct in feedback file 06 — "probably that's uh another requirement" — is correct

**Concrete next step**: add an 8th follow-up task **FU-8** to the Phase 4 set: *"Explore external-interface contracts for the factory boundary (E1–E9), reusing the internal contract format defined by REQ-PROC-044 + producing the external-state postcondition vocabulary."* Effort: M. Independent of FU-1..FU-7.

---

## §5 — Amendment to Round 3 D-2

Add this paragraph to D-2 in the round-3 synthesis under "Why this combination satisfies the developer's transparency goal":

> **External-interface compatibility note**: the format extends to factory-boundary interfaces (developer questions, product intake, web research, OS installs, dependency admission, code release, optimize events) without modification — only two additive fields may be needed (`input_modality:` for natural-language inputs) and the `quality_criteria:` value vocabulary expands for external-state checks. See `plans_and_protocols/2026-05-29_07_external_interfaces.md`. External-interface declarations are out of scope for this task; FU-8 explores them as a sibling effort.

---

## §6 — Honest caveats

1. **The survey is sample-driven.** I enumerated the 7 (+ E8/E9) interfaces I could name from the current factory. There may be channels I missed (e.g. SSH/SCP file transfers in some automated workflow; signed package verification; git remote interactions). FU-8 will produce an exhaustive inventory.

2. **The "fits cleanly" verdict rests on the internal format remaining stable.** If Wave 2 surfaces a real-world need to add `derived_from.modality:` or `quality_criteria.kind:` enums, those land in the internal format first and then carry to external. No external-side surprises.

3. **The format-extends claim does NOT mean external contracts are easy to author.** It means the *schema* extends. The hard work is enumerating the external interfaces with discipline (what URL allowlist? what package allowlist? what user-input-modalities are valid?) — that's the bulk of FU-8.

4. **Could the external work change the internal format anyway?** Yes, in theory. But this risk exists for any sequencing decision. The compatibility check above reduces the risk to "additive field additions only" — which means existing contracts written under the v1 format remain valid under any future v2.
