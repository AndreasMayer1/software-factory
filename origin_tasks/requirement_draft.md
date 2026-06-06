# Software Factory Extraction — Vision Requirement (Draft)

**Status:** Early Vision
**Stage:** Pre-Exploration (shape not yet researched or validated)
**Depends On:** Stable, proven factory workflows AND completion of the process/ folder restructuring (TASK-PROC-045-09 and its derived impl tasks)

---

> **Note on document structure:** This document intentionally does NOT follow the project's
> standard requirement format (frontmatter, ACs, task structure). This is by design —
> the factory extraction is a structural evolution that reaches across multiple projects
> and repositories. When the extraction is executed, it will establish its own requirement
> and task conventions inside the factory repository. For now, a free-form document is
> the right format to capture early-stage vision and open questions for the exploration task.

---

> **Important:** This document captures the initial intent and the developer's framing.
> The exploration task (see `tasks/`) must research the technical mechanisms, define
> boundaries, and produce an actionable implementation plan. Many open questions remain.
> Treat this as a starting point, not a specification.

---

## Core Vision

The Software Factory — the set of skills, agents, hooks, scripts, process requirements,
and guidelines that govern *how* software is built — currently lives inside the Mood Tracker
app's repository. This is pragmatically correct today, because the factory grew from
and was shaped by this project.

The long-term goal is **decoupling**: the factory becomes its own repository, independently
versioned and maintained. Any project (starting with this one) can then *use* the factory
as a dependency, with an explicit update mechanism. The factory adapts to the project's
technology and domain, not the other way around.

---

## Why This Matters

- **Reusability**: the same factory process can be applied to new projects (e.g. the future
  Stakeholder Contribution Platform) without copy-paste or manual re-synchronization.
- **Clarity of ownership**: factory improvements benefit all projects that depend on it;
  app-specific decisions stay in the app.
- **Independent cadence**: the factory can evolve on its own schedule; app work is not
  entangled with factory meta-work.
- **Reduced cognitive load**: developers working on the app see only app requirements and
  tasks; factory internals are encapsulated.

---

## Scope and Constraints

- **Separate repository**: the factory lives in its own repo, governed by its own git
  history, issues, and CI.
- **Consumption mechanism TBD**: likely Claude Code's plugin/extension mechanism, but
  compatibility with other AI toolchains (Cursor, Windsurf, …) is a goal.
- **Update mechanism required**: projects must be able to pull factory updates without
  manual file copying. The mechanism must interact correctly with Claude Code (and ideally
  with other tools).
- **This project first**: the Mood Tracker app is the first consumer and the primary
  driver of requirements for the factory's public interface.
- **Not a big-bang rewrite**: extraction follows a Strangler Fig approach; factory content
  is moved out incrementally after the process/ folder restructuring defines clean
  module boundaries.

---

## Preliminary Boundary Map (Input for Exploration)

This is the developer's first-cut categorization. The exploration task MUST validate and
refine this map before any extraction begins.

### Clearly Factory

| Artifact | Location today | Notes |
|---|---|---|
| Skills | `.claude/skills/` | Already in `.claude/` — may translate directly to a plugin |
| Agents | `.claude/agents/` | Same as skills |
| Hooks | `.claude/settings.json` hook definitions | Need to reconcile with project-specific hooks |
| CLAUDE.md content (factory rules) | `CLAUDE.md` | Currently mixes factory constitution + project context; needs splitting |
| Process requirements (most of `process/`) | `requirements_tasks/process/` | See "Boundary Challenges" |
| Factory scripts | `scripts/` (subset) | Separate from app-build scripts; see "Boundary Challenges" |
| `doc/` guidelines (technology-general parts) | `doc/` | e.g. design token rules apply to any project; Flutter-specific parts are debatable |

### Clearly Project-Specific

| Artifact | Location today | Notes |
|---|---|---|
| Functional requirements | `requirements_tasks/functional/` | App features |
| Non-functional requirements | `requirements_tasks/non-functional/` | App quality constraints |
| User needs, personas, flows | `requirements_user_needs/` | App-domain knowledge |
| Flutter app source code | `lib/`, `test/`, `integration_test/` | App code |
| App-specific build scripts | `scripts/` (subset) | e.g. bundle size check, Windows integration test launcher |
| Beyond-this-app vision | `requirements_tasks/beyond_this_app/` | Future projects, not factory |
| Windows dev environment setup | `requirements_tasks/process/AI_rules/dev_infrastructure/` | Hardware/OS-specific to this dev setup |

### Boundary Challenges (Exploration Must Resolve)

1. **`scripts/` folder split**: Many scripts are factory tooling (task management,
   requirement management, release scripts). Others are project-specific (app quality
   checks, bundle size analysis). The factory scripts must be extractable; the project
   scripts stay. Boundary is not always obvious.

2. **Process requirements**: Most of `process/AI_rules/` describes the factory. But some
   requirements describe tools/infrastructure specific to this project (e.g. the Windows
   dev environment, specific CI decisions). The process/ folder restructuring
   (TASK-PROC-045-09) will create cleaner module boundaries — extraction should happen
   after that restructuring is complete or at least planned.

3. **`doc/` guidelines**: Some guidelines are technology-general (design tokens concept,
   clean architecture principles). Others are Flutter-specific (specific library choices,
   dart analysis rules). Technology-general parts belong in the factory but must be
   configurable/overridable per project. Flutter-specific parts stay in the project —
   or preferably live in a "Flutter adapter" layer of the factory.

4. **CLAUDE.md**: The current file mixes (a) factory constitution (session start checklist,
   prime directives, workflow enforcement, quality gates), (b) project context (architecture
   stack, domain info, folder map). The factory must own part (a); each project owns
   part (b). The extraction mechanism must compose them: Claude Code (and other tools)
   must see the merged result.

5. **Factory purpose requirement (REQ-PROC-057 / TASK-PROC-057-01)**: The factory's apex
   purpose requirement is being defined. That work should converge with the extraction:
   if the factory becomes a standalone repository, its purpose requirement belongs there,
   not in the app's requirements_tasks/.

---

## Open Questions

1. **Claude Code plugin mechanism**: How exactly do plugins work in Claude Code? What can
   they provide (skills, hooks, CLAUDE.md fragments)? What is the contract between a
   plugin and the host project?
2. **Other AI tools**: Can the same package be consumed by Cursor, Windsurf, or plain
   API-based agents? If not, is a lowest-common-denominator interface feasible?
3. **Update mechanism**: How does a project pull factory updates? Git submodule? npm/pub
   package? Direct script? What triggers an update? What breaks if the factory changes
   incompatibly?
4. **CLAUDE.md composition**: Is there a native mechanism to compose multiple CLAUDE.md
   files (e.g. plugin-level + project-level)? If not, what generation/merge step is needed?
5. **Scripts distribution**: How are factory scripts delivered to a project? Bundled with
   the plugin? Referenced from the factory repo? Installed locally?
6. **`doc/` split and configurability**: How does the factory expose technology-general
   guidelines? Are they templated? Are per-project overrides supported?
7. **Factory's own CI/CD**: Once extracted, what does the factory's own test suite look
   like? How do we know a factory change doesn't break an existing consumer project?
8. **Process folder restructuring dependency**: Does the extraction need to wait for the
   full restructuring (TASK-PROC-045-09 and all derived tasks)? Or can the extraction
   plan be drafted in parallel and the extraction itself happen after?
9. **Factory versioning and consumer pinning**: Should consumers pin to a specific factory
   version? How are breaking changes communicated?
10. **Cold-start**: How does a brand-new project initialize with the factory? What is
    the onboarding experience?

---

## Open Questions — Self-Definition, Distribution & Manuals

> Added 2026-06-02 from a design discussion on replacing the hand-authored
> `.claude/factory_flows.md` with contract-derived output. These questions concern how the
> factory **specifies, documents, and distributes itself**, and they refine the Boundary Map above.

The factory's artifacts fall into four buckets distinguished by **audience** and by whether
they ship into a consumer project:

| Bucket | Content | Audience | Ships to consumer? |
|---|---|---|---|
| **A. Self-specs / rationale** | *why* skills are shaped this way: developer persona, why-this-path flows, the `REQ-PROC-*` that justify skill shape | factory **maintainers** | No |
| **B. Runtime** | skills, agents, hooks, factory scripts, technology-general `doc/` guidelines | the running system | **Yes — this is the install** |
| **C. Consumer specs** | the app being built (its personas, requirements, user-needs) | the consumer project | Authored locally, not delivered |
| **D. User manuals** | *how to use* the factory: routing tables, release workflow, onboarding/concepts | factory **users** (developers) | **Yes — ships alongside B** |

Litmus for the A vs B/D boundary: *"Does a consumer's agent need this at runtime to build the
consumer's app?"* → ships (B/D). *"Is it only needed to understand or evolve the factory itself?"*
→ stays home (A). The boundary is enforced by the package/plugin **manifest** (what is included),
not by folder naming — so internal folder names can be reused freely between factory and consumer.

11. **Does the factory get its own user-needs layer?** The factory already self-hosts from
    requirements down (`REQ-PROC-*` describe it, `TASK-PROC-*` implement it, REQ-PROC-057 defines
    its apex purpose). The missing layer is *user-needs above requirements*: a "developer-as-user"
    persona, scenarios (the input types — Feature Request, Bug Fix, Scope Change… each is an
    occasion of use), and flows (the input→code paths). This is **self-hosting, not vicious
    circularity** — the existing hand-built factory is the bootstrap. Should this layer be
    authored, and when (see timing note)?

12. **Namespace separation for factory user-needs.** If bucket A includes a developer persona and
    factory scenarios/flows, they must not co-mingle with the app's personas (amina, hanna, …). The
    `ux-*` skills are currently domain-coupled to the app (concept_canon, SCENARIO_INDEX, ID
    prefixes). What parallel namespace / canon does the factory's own user-needs layer need so the
    same `ux-*` / `requ-*` tooling can be self-applied? (The requirements layer already self-applies
    via the `REQ-PROC` prefix; the user-needs layer does not yet.)

13. **`.claude/factory_flows.md` is a manual (bucket D), not a maintainer design doc.** Its readers
    are users choosing which skill to invoke. It should be reconstituted as a **composition**:
    generated reference chapters (the flow map, the input→path table, the decision-gate index —
    `render_factory_map.py` and `render_user_input_gates.py` are already manual-chapter generators)
    plus a thin authored concepts/getting-started narrative carrying the irreducible "why."
    Replacing the hand-authored file with contract-derived output additionally requires: contracts
    to declare **entry-points / input-types** (a new contract field + an input-type registry,
    mirroring `.factory/registry/artifacts.yaml`), and flipping the LAW reference in CLAUDE.md §1 to
    the generated output. Governed by REQ-PROC-044 (artifact model).

14. **How much "why" does the user manual carry?** Design rationale (A, maintainer) vs user
    documentation (D, user) is an audience split, but the line is not crisp: a factory user benefits
    from enough "why" to *follow* the top-down discipline rather than fight it, while deep per-gate
    justifications stay maintainer-only. Where exactly does the manual's "why" stop?

15. **Timing — author now or at extraction?** Split *capture* from *structure*. The **structure**
    (instantiating the factory's user-needs layer, flipping `factory_flows.md` to generated) waits
    for extraction: it depends on the namespace decision (Q12), the `ux-*` domain-coupling, and the
    "No Intermediate Reorganization" decision below. The **capture** (this discussion) is recorded
    here now, while the rationale is fresh.

16. **Extraction is an artifact cleanup, not a file move — and it must be done carefully.** Every
    existing artifact must be audited against the A/B/C/D buckets and may change *role*, not just
    path — so the cleanup has to be deliberate, artifact by artifact, never a mechanical sweep. The
    clearest example is `.claude/factory_flows.md`: today it is named and shaped as a "flow"
    artifact, but post-extraction it *is* a user manual (bucket D). It will likely relocate, be
    renamed, and split into generated + authored parts (Q13); its current name and location become
    misleading. The extraction plan must therefore include a **per-artifact pass** that
    re-classifies, renames, and relocates each artifact according to what it has actually become —
    and verifies no information is lost in the move. This generalizes the folder-level point in "No
    Intermediate Reorganization" below from *folders* to *artifacts and their roles*.

**Considered and dropped: a unified `specs/` folder.** Merging `requirements_tasks/` and
`requirements_user_needs/` into one `specs/` folder was considered and rejected: task
protocols/plans live *next to* their tasks (execution memory, not specification), so folding tasks
under a "specs" label conflates spec with execution. The current structure stands; any folder
renaming/unification is deferred to the extraction itself, and the eventual name is its own open
exploration item.

---

## Open Questions — Self-Deployment & Artifact Validation

> Added 2026-06-02 from a design discussion on how the extracted factory **deploys itself**
> and how its own artifacts get **tested**. Verbatim seed:
> `requirements_tasks/process/AI_rules/factory_extraction/tasks/2026-05-28_explore_software-factory-extraction/plans_and_protocols/2026-06-02_01_user_input_deployment_and_testing.md`.
> These questions sharpen Open Questions 3, 5 (update/distribution) and especially **OQ7
> (factory's own CI/CD)**, which this section largely *is*.

### Part 1 — The factory is its own first consumer (self-deployment)

Because the factory self-hosts (Q11: it carries its own user-needs → requirements → tasks),
it must also *run* on itself. But Claude Code only loads skills/agents/hooks from the
tool-defined locations (`.claude/`). So the extracted factory needs two locations for the
same content:

- a **source-of-truth output folder** (the "`lib/`" of the factory) — what maintainers edit, and
- a **deployed copy under `.claude/`** — what the running tool actually loads.

A **deploy step** keeps them in sync (lowest form: a script copying changed files; higher
form: a build that also composes CLAUDE.md and filters by the A/B/C/D manifest).

The key realization: **this deploy step is not extra work — it *is* the install/update
mechanism (OQ3/OQ5) applied to the factory itself.** The factory dogfoods its own
distribution; self-deployment becomes a free, continuous integration test of the consumer
install path. Refined questions:

17. **Where is the source output folder and what is its relation to `.claude/`?** Is deploy a
    pure copy (source format == deployed format), or a *build* (CLAUDE.md composition, manifest
    filtering, generated manual chapters per Q13)? If a build, the source and the deployed copy
    are not byte-identical and the deployed copy is a **generated artifact**.

18. **The drift hazard.** Today `.claude/skills/*` *is* the source of truth, edited in place by
    `claude-create-skill`/`claude-modify-skill`. After extraction, the deployed `.claude/` copy
    must become **generated and non-authoritative** (add it to CLAUDE.md's "Generated Files — Do
    NOT Edit Manually" table) so nobody edits the deployed copy and loses the change on the next
    deploy. The skill-authoring tools must then write to the *source* folder and trigger redeploy.
    What guards against editing the deployed copy (git-ignore? read-only marker? a pre-commit
    check)?

### Part 2 — The validation asymmetry (the larger problem)

The factory's value proposition for **app code** is: requirements → tasks → code →
*automated oracles* (unit/widget/integration tests + back-pressure quality gates) → bounded
iteration loop. The developer defines requirements and reviews once; the LLM iterates against
the oracles. **Low developer-in-the-loop.**

For the factory's **own LLM-driven artifacts** (skills, agents, prose contracts/guidelines)
there is today **no oracle**. You cannot `flutter analyze` a skill's behavior; the only
validation is a developer manually using the skill and judging the result — so the developer
is *permanently* in the loop. This contradicts the factory's own value proposition and is the
single biggest risk in "the factory develops the factory." Establishing an oracle is what
would let factory self-development enjoy the same low-developer-in-the-loop property the factory
gives to app development — directly serving REQ-PROC-057 (factory apex purpose).

**Scope of the gap.** It is *only* the LLM-driven artifacts. **Scripts are already testable**
(real code; Python gates G1–G5 and a large `scripts/quality/check_*` suite already apply) — and
the factory's "everything-a-script-can-do-is-a-script" rule deliberately maximizes this
testable surface. Skill *interfaces* are also already linted (`scripts/quality/check_skill_contracts.py`
validates each `contract.yaml`'s produces/consumes). The untested part is whether an *invocation*
of a skill/agent actually **produces a correct artifact**.

**Without an oracle there is no back-pressure signal** for factory artifacts, so the iteration
loop cannot self-terminate on quality — it can only terminate on developer review. Building the
oracle is the precondition for a factory-artifact analogue of the back-pressure protocol.

19. **Two complementary test strategies — and they isolate different variables.**
    - **(A) Retrospective replay against real history.** The optimizer already logs
      (skill, task, commit) usage (`claude-optimize` / `.factory/optimize/`). Harvest real
      invocations: checkout the parent commit, branch into a throwaway worktree, deploy the
      *candidate* factory, re-run the skill on the same input, compare to the historically
      committed outcome. **Confounds:** (i) **model drift** — an older historical run vs. a newer
      model measures the *model*, not the *skill*; mitigate by pinning the original model *if still
      available* (golden transcripts therefore have a shelf life as models retire); (ii) **LLM
      non-determinism** — exact-diff is hopeless, the comparison must be semantic/rubric-based
      (see Q21); (iii) **input replayability** — re-running needs the full occasion of use,
      including interactive decision-gate answers (`pending_feedback/answer.md`), so each fixture
      is a *recorded, replayable bundle*, not just a commit hash. Best for **integration-level**
      regression against realistic inputs.
    - **(B) A dedicated synthetic test bench** shipped inside the factory repo. A small, stable
      target project the factory operates on. A bare calculator app is likely **too simple** —
      many skills (`requ-explore`, `ux-create-flow`, the scribble pipeline) need domain richness
      to even activate, so the bench probably needs **tiers** (a trivial target for context-free
      skills; a richer reference mini-app with personas/flows for the full pipeline) and must
      exercise the different **input-types** the factory recognizes (Feature Request, Bug Fix,
      Scope Change … — the factory's own "scenarios" per Q11). **Advantage over (A): no model
      confound** — baseline and candidate are both run with the *same current model*, a clean
      head-to-head A/B that isolates the *skill* variable. Cost: less real-world diversity.
    - **Synthesis:** (B) is the fast pre-merge CI gate (controlled, cheap, model-stable); (A) is
      periodic deeper validation against real-world inputs. They are complementary, not rivals.

20. **Unit vs. integration for skills.** *Unit* = a single skill/agent invoked on a fixture and
    checked against its contract. *Integration* = a whole **sequence** of skill uses (e.g. a full
    requirement→tasks→scribble→handoff chain) run end-to-end to verify the skills still compose
    after a change. The integration corpus is exactly what strategy (A) harvests from real history
    and what (B) can script on the bench.

21. **The oracle problem — what is "pass"?** The developer's instinct ("the requirements and the
    tasks that created the skill already define the expected minimum quality — maybe that's
    enough") is right; the work is to **operationalize** those ACs into something runnable, exactly
    as app ACs are operationalized into Dart tests. The oracle is a spectrum, cheapest-first:
    1. **Deterministic structural assertions** — file presence, frontmatter fields, registry/parity
       consistency. Much of this already exists (`check_skill_contracts.py`, `check_scribble_parity.py`,
       `render_factory_map.py`, the consistency checkers). First line of defence; robust; no LLM.
    2. **Contract-derived checklists** — each skill's ACs turned into a machine- or judge-checkable
       checklist, **co-located with the skill** and authored when the skill is created/modified. This
       is the "test file" the developer described.
    3. **LLM-as-judge rubric** — for the irreducibly qualitative part ("does this generated flow
       actually make sense for this input?"). Risks: judge non-determinism, judge-model drift,
       grading-its-own-homework. Mitigate with a pinned judge model + explicit rubric + threshold,
       and start **advisory** (trend, not hard gate) — exactly how `ui-visual-validate` is already
       positioned.

22. **TDD for the factory.** The project mandates tests-before-implementation for code. The
    analogue: **no skill is "done" without a test spec** — a contract-derived checklist (Q21.2)
    plus at least one fixture invocation on the bench (Q19B). This would extend
    `claude-create-skill` / `claude-modify-skill` to require/scaffold the spec, making artifact
    testing a first-class part of factory authoring rather than an afterthought.

**Precedent already in the repo (do not reinvent):** the scribble pipeline is *already* an
automated quality loop for an LLM-driven factory artifact — `ui-scribble-auto-review` fans out to
judge agents (rule-reviewer, heuristics-reviewer, persona-walker), `ui-create-scribble-improve`
runs a vision-evaluated iteration loop, and the `quality-checker` agent does `doc/`-judgment-level
review of code. The validation framework above is largely a **generalization of that existing
pattern** from one corner of the factory to skills/agents at large.

---

## Vision Input — Citizen Developers, Ethics & Multi-Persona

> Added 2026-06-05 from a developer vision discussion. Verbatim seed:
> `requirements_tasks/process/AI_rules/factory_extraction/tasks/2026-05-28_explore_software-factory-extraction/plans_and_protocols/2026-06-05_02_user_input_factory-vision-and-extraction-methodology.md`.
> This is **scope-defining vision**, recorded here as seed for the exploration to *place*. Much of
> it likely belongs to **REQ-PROC-057 (factory apex purpose)** and to the **user-needs
> artifact-creation skills**, not to extraction mechanics per se. Captured here so the boundary
> work doesn't lose it; the exploration must decide the correct home for each item and must not
> treat any of it as already-decided scope.

The stated **end goal**: a product anyone can use to create software — **enabling citizen
developers**. The single-developer/Flutter context the factory serves today is one persona, not
the ceiling. Three threads follow:

23. **A GUI surface.** First concrete step named: render the **user-needs artifacts in a browser**.
    Today every artifact is text-in-repo, authored and read through the coding tool. A browser view
    of personas/scenarios/flows is the seed of a non-CLI consumption surface — and the first thing a
    non-developer ("citizen developer") persona would need. *Open:* is this factory scope or a
    separate downstream product? Does it read the repo directly or a generated export?

24. **A harm/ethics checker in the user-needs artifact-creation skills.** The premise: *the designer
    and product manager is responsible for all harm caused by the produced software.* Requirements
    the developer stated for such a checker:
    - It lives **in the artifact-creation skills** (where personas/scenarios/flows are authored), not
      as an afterthought gate.
    - It surfaces harmful outcomes **objectively and non-patronizingly** — present the harm, don't
      lecture.
    - There is **a line that, once crossed, makes the LLM refuse to continue.**
    - It must **suggest no-harm alternatives that still serve the personas** — refusal alone is not
      the deliverable; a served-need-without-harm path is.
    - Scope of harm to consider is broad: **effects on other people, animals, and resources, now and
      in the future**, across **all categories — from increasing inequality to genocide.**
    - *Open:* where is the refusal line drawn and who calibrates it? How does "objective, not
      patronizing" become a checkable rubric (cf. the LLM-as-judge oracle work in Q21)? Is this one
      checker skill, or a cross-cutting concern woven through `ux-write-persona` / `ux-write-scenario`
      / `ux-create-flow`? This intersects the factory's **own** ethics posture, so it likely belongs
      to REQ-PROC-057 with a hook into the authoring skills.

25. **Multi-persona support — and what "out of the box" means.** Today the factory hard-assumes a
    **single** context, and that assumption is baked into countless skills/docs. The current context,
    stated explicitly (this is the *de facto* boundary of "what the factory supports today"):
    offline-only Flutter app (no server); Windows + WSL + devcontainer; **Claude Code only**, multiple
    **Pro-plan** accounts (so **no token-cost optimization** has been done — an API-priced user would
    feel that); **everything in one repository** (no Jira, no Figma, no external artifact store — by
    deliberate design, because round-tripping artifacts out to external AI tooling and back wasn't
    judged worth it); and **the developer wears every role** (PM, PO, market research, UX/UI,
    engineering). Consequence the developer accepts: a non-Claude-Code user gets something that **does
    not work out of the box** — adaptation is required, but "the factory improves itself" is expected
    to make that tractable. *Open:* which of these assumptions are **configuration points** the
    extraction must expose (tool target, plan/cost profile, role-split, repo topology) vs. genuine
    fixed constraints? This directly sharpens **OQ on technology-general vs. technology-specific
    configurability** and the **other-toolchain** ambition already in this draft.

---

## Extraction Methodology — Reverse-Engineering User Needs From Implementation

> Added 2026-06-05 from the same discussion (same verbatim seed file as above). This section is the
> **how** of the extraction itself — the developer's proposed methodology — and is squarely in this
> task's scope. It is a method proposal to be pressure-tested, not a fixed plan.

**The governing constraint: minimal developer-in-the-loop at high quality.** The developer cannot
sit and watch. The plan must front-load the decisions so that *execution* asks almost nothing. So
the first deliverable of the extraction plan is itself a list of **decide-up-front** items —
explicitly named: *which personas, which scenarios, how to structure the requirements, and how to
author the currently-missing requirements.* (Mirrors the Ralph-loop "strong rules / when to ask /
when not to ask" need below — same automation problem.)

**The core inversion (and the central methodological bet).** The normal factory flow is top-down:
persona → scenario → flow → requirement → task → code. Here the **code already exists**, so the
factory must run **partly in reverse**: read the implementation and *infer* the user needs behind
it. Crucially this is **not** a pure reversal — the developer's proposed order interleaves both
directions:

26. **Personas first, then implementation analysis.** Author personas top-down *first*; then walk the
    implementation and, for each significant piece, reason *which persona benefits and how*. ("Implementation"
    = skills **plus** the artifacts they drive: agents, scripts, hooks.) The persona set is the lens
    that makes the inference disciplined rather than arbitrary.

27. **Intermediate artifact: "tasks the user wants to perform."** The first inference product is **not**
    scenarios directly but a flatter collection of *jobs the user wants done* (the developer flags "user
    needs" as an awkward term here). Scenarios are then **synthesized by combining/clustering** these
    jobs — this is the explicit anti-fragmentation step.

28. **Scenarios — present-tense, grounded, and deliberately coarse.** Two departures from the app
    project: **(a)** *no "before the solution" scenarios* — for the factory, scenarios describe how the
    developer **actually works with** the factory today; **(b)** some can be **empirically grounded** in
    real usage (the optimizer's usage logs / git history record genuine past invocations), so a subset of
    scenarios is evidence-backed rather than hypothesized. The hard sub-problem the developer calls out:
    **how many scenarios, at what altitude, with how large the gaps** — i.e. an explicit **coverage
    target** must be set, because the real failure mode is writing ~100 over-fine scenarios that help
    nobody.

29. **User flows — same logic, maximize coverage-per-flow.** Derive flows from implementation + scenarios;
    deliberately make each flow **as large as still-coherent** so one flow covers as much implementation as
    possible. Goal: **as few flows as possible** without becoming an incomprehensible catch-all. Needs a
    stated rule for "large enough but still sensible," parallel to the scenario coverage target.

30. **Requirements — derive, then reconcile against reality, then restructure, then map, then fill.** From
    flows, derive requirements that describe *what is actually implemented*; **double-check** each against
    the live implementation (drift check). Then the genuinely **new** capability the factory lacks today:
    **restructure the existing (large) requirement corpus** — a proposed new structure exists but must be
    made **specific** — then **map flows onto the restructured requirements**, which is precisely what
    **surfaces the gaps** (implemented-but-unspecified behavior). Fill those gaps. *Note:* this restructure
    couples tightly to TASK-PROC-045-09 and to this draft's "No Intermediate Reorganization" stance — the
    reorg the draft defers is the reorg this methodology now needs; the exploration must reconcile the two.

31. **Tasks for already-built work — a new "completed-at-creation" capability, reusable for brownfield.**
    Tasks must be authored **already marked completed**, since the code exists. This needs a **new skill**
    (`task-create` / `task-derive-from-requ` assume not-yet-built work). The developer's insight: this is
    **not a one-off** — it is exactly what **any brownfield adoption** of the factory needs, so build it as
    a **reusable** capability, not throwaway extraction glue. The factory *is* the first brownfield case.

32. **Why duplicate the spec at all (the load-bearing rationale).** Even though it duplicates working code,
    the requirement+task layer is mandatory because of the factory's own compiler metaphor: **requirements =
    what, tasks = how, implementation = disposable compiler output.** Tasks — not the code — are the single
    source of truth. Without the spec holding it in place, **LLMs delete what they don't understand and the
    implementation drifts.** The spec is the anti-drift anchor. (This is the same conviction that motivates
    the whole extraction; it is the justification for accepting the duplication cost.)

33. **Driving it: the Ralph loop is an enabler, not the point.** The Ralph-loop mechanism was built to keep
    the LLM grinding through the many extraction steps; the *prior* task (TASK-PROC-066-02) deliberately
    explores **whether** it helps before committing. Its open dependency is **rule strength** — what to
    build, when to stop, **when to ask the developer vs. when not to** — without which autonomy fails.
    **But the requirement is loop-agnostic:** Ralph or not, the binding constraint is "automate as much as
    possible because the developer won't watch." The methodology above must therefore be expressible as
    **decisions-front-loaded + execution-near-silent**, whatever drives the iterations.

---

## Relationship to Existing Work

| Item | Relationship |
|---|---|
| TASK-PROC-045-09 (process/ restructuring) | Prerequisite for extraction: clean module boundaries needed first |
| TASK-PROC-057-01 (factory purpose) | The factory's apex requirement; should migrate to factory repo once defined. Likely home for the citizen-developer goal, the harm/ethics checker, and the multi-persona vision (OQ23–25) |
| TASK-PROC-066-02 (Ralph-loop explore) | Hard predecessor; explores whether/how the loop drives the extraction. The methodology (OQ26–33) must stay loop-agnostic — automation is the constraint, Ralph is one means |
| beyond_this_app/stakeholder_contribution_platform | First downstream consumer once extraction is done |
| REQ-PROC-060 (dependency admission) | Will apply to factory-as-dependency in consumer projects |

---

## Decided: No Intermediate Reorganization

Before the factory extraction happens, there will be **no cosmetic folder reorganization** within this repository (e.g. moving `automation/` under `.factory/`, or splitting `scripts/` into factory vs. app subfolders). Reasons:

- The effort is non-trivial: hundreds of path references in skills, scripts, and hooks would need updating.
- The extraction itself will reorganize everything anyway — a preparatory shuffle creates work twice.
- The right moment for a folder-level cleanup is *as part of* the extraction process, once TASK-PROC-045-09 has established clean module boundaries.

Additionally, **app specifications stay co-located** with the app code (no separate repository for `requirements_tasks/functional/`, `requirements_user_needs/`, etc.). Cross-repo task references and path dependencies in the scripts layer would create synchronization friction with no meaningful benefit at this scale.

---

## Research Areas (For Exploration Task)

- Claude Code plugin architecture (official docs, source, community examples)
- Alternative AI tool extension mechanisms (Cursor rules, Windsurf, Cline, etc.)
- Git submodule vs. package manager vs. file-sync for factory delivery
- CLAUDE.md fragment composition patterns
- Multi-repo monorepo hybrid patterns (factory as library)
- Semantic versioning for AI-agent configuration packages
