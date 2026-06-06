---
id: REQ-PROC-032-05
status: active
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
effort: M
stakeholder: developer
created: 2026-02-28
updated: '2026-06-06'
after: []
blocks: []
market_research_refs: []
trackable_items:
  acceptance_criteria:
    - id: AC-01
      name: Scribble-Currency Invariant holds continuously
      description: 'No coding task is in a runnable state while the scribble of any
        requirement it covers is missing, unapproved, or stale relative to that requirement''s
        current committed version. This single invariant holds at every point in a
        release''s life: at release start it is satisfied because the scribble gate
        withholds coding decomposition until scribbles are approved, and mid-release
        it remains satisfied because a requirement edit that invalidates a covered
        scribble leaves every dependent coding task non-runnable until a refreshed
        approved scribble exists. The invariant is a standing property of the system,
        not a one-time checkpoint — it is equally verifiable at t=start and t=mid-release
        by inspecting the currency of each coding task''s covered scribbles.'
    - id: AC-02
      name: Standing SCI audit detects every violation
      description: A standing, script-driven SCI audit resolves, for every coding
        task, the scribble of each requirement it covers and asserts that scribble
        is approved and its contributing_requirements commit is at or ahead of the
        requirement's current committed version. Any coding task whose covered scribble
        is missing, unapproved, or behind the requirement's commit is reported as
        an SCI violation. The audit runs as a blocking gate at release finalization
        and is also runnable standalone at any time. It is distinct from and additive
        to the storage-mirror parity check (which only detects orphaned scribble paths,
        not currency).
    - id: AC-03
      name: Five-edge staleness rot-graph each with a detector
      description: 'Scribble staleness is governed by exactly five staleness edges,
        each with a named detector: (1) requirement → scribble, triggered by a LOCKED-IN
        requirement edit, detected by a stale_since marker set on the affected scribble
        at requirement-edit time; (2) scribble → coding task, triggered by a scribble
        re-approval or supersession, detected by the SCI audit; (3) domain-code →
        data-bound scribble, triggered by a domain value-object edit and active only
        for code-first design-units, detected by a domain-commit comparison in the
        SCI audit; (4) scribble → dependent scribble, triggered by an outward-entry-surface
        change on approval, detected by the lazy-wavefront cascade detector; (5) scribble
        → verification verdict, triggered by a scribble being stale at verification
        time, detected by the verification reader''s currency check. No staleness
        path exists outside these five edges for the current design.'
    - id: AC-04
      name: Loopback-as-task taxonomy L1–L6
      description: 'Every scribble-workflow loopback resolves to one of six classes
        (L1 flow re-adjust, L2 requirement edit, L3 missing entry in a seam-owner
        requirement, L4 auto-review non-convergence, L5 cross-requirement UI cascade,
        L6 mid-release requirement edit from technical unworkability), and the resolution
        is mechanical: a loopback that mutates a normative-upstream artifact (a flow
        or a requirement) is owned by a NEW task in a fresh session that blocks the
        affected scribble; a loopback that only refreshes the derived scribble within
        the same requirement, on a scribble that was never approved, stays the same
        task and advances to the next version. Equivalently: un-approved scribble
        ⇒ same task, new version; approved-then-invalidated scribble ⇒ new scoped
        scribble-refresh task. Each class names its owning skill, its task-vs-version
        disposition, and its termination guard.'
    - id: AC-05
      name: Lazy-wavefront cross-requirement cascade
      description: Cross-requirement UI cascade is resolved lazily, one hop at a time,
        with no precomputed global UI-dependency graph. When a scribble re-approves
        with a changed outward entry surface (the screen identity, route, or entry
        affordance other features name as their opener moved), its direct depth-1
        dependents — scribbles whose entry reference resolves to a screen of that
        scribble, queried from live flow_positions rather than any cache — each receive
        a scoped scribble-refresh task ordered after the origin refresh. The wave
        advances one hop per approval and terminates because most refreshes are entry-context-only
        and do not move the dependent's own outward surface; a per-cascade visited
        set keyed on the cascade origin guarantees no scribble is re-enqueued within
        one wave. A scribble's purely internal edits (copy, a non-entry element) do
        not trigger the cascade.
    - id: AC-06
      name: Two-stage cascade width breaker with measured-on-fixture defaults
      description: 'The cascade carries a two-stage width breaker. At a soft threshold
        of cumulative dependents the gate is annotated with a wide-cascade-in-progress
        notice while auto-creation of refresh tasks continues; at a hard threshold
        auto-creation stops and the situation escalates to the developer through the
        existing back-pressure / pending_feedback channel with the dependency sub-graph
        walked so far. The two thresholds are configurable; their shipped defaults
        are a soft value of 3 and a hard value of 7, designated as starting values
        to be tuned against the measured width of the first fixture cascade. The breaker
        honours the bounded-recovery principle: recovery is bounded and human-escalated,
        never unbounded auto-creation.'
    - id: AC-07
      name: L3 coverage assertion and chain-length alert
      description: The depth-1, non-recursive requirement-source check for a missing
        entry (L3) is sound only when every Presentation requirement carries a scribble
        or a source-check; this coverage assertion is itself checked, so that a Presentation
        requirement lacking a scribble or source-check is surfaced rather than silently
        allowing the depth-1 check to miss a gap. Additionally, a source-gap chain
        (one requirement's entry depending on another's, transitively) longer than
        a defined length raises a soft alert that logs and surfaces the chain without
        blocking, making a degenerate requirement graph visible.
    - id: AC-08
      name: Entry-context spine emitted, reviewed, and reconciled
      description: 'Each scribble screen carries entry/exit information-model facts:
        entry-surface type, entry-point multiplicity (surfaced as an explicit design
        decision when greater than one), and the back/close destination; where a screen''s
        container is size-variant, the chosen container dimension and its rationale
        are carried as well. Each screen emits a resolvable entry reference at one
        of three tiers — a sibling scribble at the predecessor flow step (Tier 1),
        an integration-test screenshot of an already-built opener (Tier 2), or an
        explicitly flagged open design decision (Tier 3) — sourced from the requirement,
        never fabricated by the generator: a requirement lacking its outer entry point
        is treated as a requirement gap routed to requirement authoring. A reviewer
        asserts these facts and the entry reference are present, internally consistent,
        and (for a size-variant container) size-appropriate. A bounded reconciliation
        check confirms the claimed entry matches the actual router or its Tier-2 screenshot
        only when the entry screen already exists in the codebase; greenfield entries
        skip reconciliation.'
    - id: AC-09
      name: Scribble coverage and ordering
      description: 'A flow→scribble coverage report lists, per flow, which steps and
        requirements have a scribble and which do not, and resolves each scribble''s
        entry references to a PROP-8 tier, flagging true Tier-3 gaps; the report spans
        both the functional flow-derived requirements and the chrome-owning non-functional
        design-system requirements, and is advisory. Every requirement that specifies
        renderable screens or components carries a scribble task, auto-assigned at
        decomposition rather than relying on plan-author memory, while pure rule,
        token, and pattern requirements are excluded. Scribble tasks are ordered so
        a basis exists at execution: the ordering edge follows only the primary forward
        entry path (back, close, and cross-navigation edges are never ordering edges)
        and reaches depth-1 only. Each direct opener''s basis resolves to a sibling
        scribble, else a current integration-test screenshot, else a blocking basis-scribble
        task; a screenshot used as basis must be validated current or is treated as
        missing. A Tier-3-only entry is surfaced at the approval gate as a conscious
        designing-before-opener decision rather than hard-blocked.'
    - id: AC-10
      name: App-shell launch-map requirement and two-tier seam detection
      description: 'The cross-feature launch seam — the outer entry point by which
        each feature is reached from the rest of the app — is owned by a single app-shell
        / feature-launch-map requirement that declares the primary destinations and
        where each feature''s entry hangs, serving as the canonical Tier-1 target
        that feature scribbles resolve their entry context against; feature requirements
        needing the launch surface take a foundation dependency on it so it is authored
        first. Seam ownership gaps are detected in two tiers: a local provisional
        pass during flow-derivation raises a foundation_gap for any screen whose outer
        entry point no requirement owns, and a global authoritative pass during full
        flow-coverage verification deduplicates those independent requests into the
        one launch-map requirement and confirms ownership against the assembled written
        requirement set; the scribble-time requirement-source check is the final backstop
        for any seam still missed.'
    - id: AC-11
      name: Domain-to-design conditional edge and data-bound detector
      description: 'A scribble is data-bound when its requirement''s presentation-facet
        or both-facet acceptance criteria reference a domain value-object or entity
        that itself has behaviour-facet criteria in the same design-unit. A data-bound
        scribble carries an ordering relationship to the domain task that defines
        that value-object: a soft ordering preference by default, hardened to a blocking
        dependency only for code-first design-units where the data model is genuinely
        undecidable before implementation, with a human override available at the
        approval gate. This conditional edge is the only path by which domain code
        constrains design, and it reuses the facet tags and the design-unit map without
        introducing new metadata.'
    - id: AC-12
      name: Acceptance-criterion facet tagging
      description: 'Every acceptance criterion of a Presentation-touching requirement
        carries a facet tag of presentation, behaviour, or both, determining its wave:
        a presentation facet is locked by the scribble, a behaviour facet becomes
        a coding task, and a both-tagged criterion appears in both — its presentation
        facet locked by the scribble and its behaviour facet a coding task ordered
        after that scribble. The tag is produced by an automatic heuristic followed
        by human confirmation, and on ambiguity it fails safe to presentation so that
        an ambiguous criterion always passes through the scribble gate (erring toward
        more design review, never less). A facet-tag audit records the automatic tag
        alongside the human-confirmed tag per criterion.'
    - id: AC-13
      name: Generative readers block, referential readers flag
      description: A reader of a stale scribble is treated by whether it generates
        a downstream artifact or merely references the scribble. A generative reader
        — a coding task that consumes the scribble as its UI contract, a dependent
        scribble that generates a wireframe from the shared entry surface, and the
        verification reader that produces a pass/fail verdict against the scribble
        — is blocked by an ordering edge on the refresh task and, if already running,
        surfaces as an SCI violation. A referential reader — the flow composite index,
        the scribble index, release notes, the approval trail, and the coverage report
        — renders the scribble with a stale-since flag and is never blocked. The verification
        reader blocks by default while exposing an explicit advisory override that
        runs and labels its verdict as made against a stale target.
    - id: AC-14
      name: Soft-SCI is a sign-off-gated mode, default off
      description: Soft-SCI — allowing a coding task to proceed against a stale scribble
        with its output marked provisional and a mandatory re-verification enforced
        when the scribble refreshes — exists only as an explicit configurable mode
        that is off by default and can be enabled only with recorded developer sign-off.
        While off (the default), the Scribble-Currency Invariant is a hard blocking
        invariant. The mode's existence preserves a liveness escape hatch for densely-coupled
        releases without making the relaxation of the correctness guarantee a silent
        default.
  sections:
    - id: SEC-18
      name: Consistency and Scribble-Layer Model
      heading: '## Consistency and Scribble-Layer Model'
---

# Consistency Sci Layer


## Consistency and Scribble-Layer Model

The scribble is the locked-in design contract a coding task consumes. For that contract to be trustworthy across a whole release — through mid-release requirement edits, cross-feature cascades, and the discrepancy window between a requirement change and its scribble catching up — the system holds a single consistency invariant and a small, closed set of staleness edges around it. This section defines the end state of that consistency layer. [AC-01..AC-14]

**The Scribble-Currency Invariant (SCI).** No coding task is runnable while the scribble of any requirement it covers is missing, unapproved, or stale relative to that requirement's current committed version. This is one invariant observed at two times: at release start the scribble gate withholds coding decomposition until scribbles approve (the "hard gate"), and mid-release a requirement edit that invalidates a covered scribble keeps dependent coding tasks non-runnable until a refreshed approved scribble exists (the "discrepancy-window governance"). The gate and the mid-release governance are the same mechanism, so currency is verifiable identically at t=start and t=mid-release. [AC-01]

A standing, script-driven **SCI audit** resolves each coding task's covered scribbles and asserts each is approved and at or ahead of its requirement's commit; any missing, unapproved, or behind scribble is an SCI violation that blocks release finalization. The audit is additive to the storage-mirror parity check, which only detects orphaned paths. [AC-02]

**The five-edge staleness rot-graph.** Staleness propagates along exactly five edges, each with a detector: (1) requirement→scribble (`stale_since` set on a LOCKED-IN requirement edit); (2) scribble→coding task (the SCI audit); (3) domain-code→data-bound scribble, active only for code-first design-units (a domain-commit comparison in the SCI audit); (4) scribble→dependent scribble on an outward-entry-surface change (the lazy-wavefront detector); (5) scribble→verification verdict (the verification reader's currency check). No staleness path exists outside these five. [AC-03]

**Treatment of stale-scribble readers.** A reader that *generates* a downstream artifact from a stale scribble blocks (an ordering edge on the refresh task; already-running ⇒ SCI violation): the covering coding task, a dependent scribble, and the verification verdict. A reader that only *references* the scribble flags it (`stale_since` banner, no block): the flow composite index, the scribble index, release notes, the approval trail, the coverage report. The verification reader blocks by default but exposes an explicit advisory override that runs and labels its verdict as made against a stale target. [AC-13]

**Loopback-as-task (L1–L6).** A loopback that mutates a normative-upstream artifact (a flow or a requirement) is owned by a NEW task in a fresh session that blocks the affected scribble; a loopback that only refreshes the derived scribble within the same requirement, on a never-approved scribble, stays the same task and bumps the version. In one line: un-approved ⇒ same task, new version; approved-then-invalidated ⇒ new scoped refresh task. The six classes are L1 flow re-adjust, L2 requirement edit, L3 missing entry in a seam-owner requirement, L4 auto-review non-convergence, L5 cross-requirement UI cascade, and L6 mid-release technical unworkability — each with its owning skill, task-vs-version disposition, and termination guard. [AC-04]

**Lazy-wavefront cross-requirement cascade.** There is no precomputed global UI-dependency graph (it would rot, since every scribble regenerates independently). When a scribble re-approves with a *changed outward entry surface* — the opener screen's identity, route, or entry affordance moved — its direct depth-1 dependents (resolved from live `flow_positions`, never a cache) each get a scoped refresh task ordered after the origin refresh. The wave advances one hop per approval and dies where a refresh does not move the dependent's own outward surface; a per-cascade visited set prevents re-enqueueing. [AC-05]

A **two-stage width breaker** bounds the wave: a soft threshold annotates the gate ("wide cascade in progress") while auto-creation continues; a hard threshold stops auto-creation and escalates to the developer via the existing back-pressure channel with the walked sub-graph. Both thresholds are configurable; the shipped defaults are soft 3 / hard 7, designated starting values to be tuned against the first measured fixture cascade. Recovery stays bounded and human-escalated, never unbounded auto-creation. [AC-06]

**L3 coverage assertion.** The depth-1, non-recursive entry source-check is sound only if every Presentation requirement has a scribble or source-check; that coverage assertion is itself checked so a Presentation requirement lacking either is surfaced. A source-gap chain longer than a defined length raises a soft, non-blocking alert that makes a degenerate requirement graph visible. [AC-07]

**Entry-context spine (PROP-8).** Each scribble screen carries entry-surface type, entry-point multiplicity (an explicit decision when >1), the back/close destination, and — for a size-variant container — the chosen container dimension and its rationale. Each screen emits a resolvable, requirement-sourced entry reference at one of three tiers (sibling scribble at the predecessor step / integration-test screenshot of a built opener / explicitly flagged open decision); a requirement lacking its outer entry is a requirement gap, never fabricated. A reviewer asserts these facts are present, consistent, and size-appropriate. A bounded reconciliation confirms the claimed entry matches the actual router or its screenshot only when the entry screen already exists; greenfield skips it. [AC-08]

**Coverage and ordering (PROP-9 / PROP-11).** A flow→scribble coverage report lists, per flow, covered vs uncovered steps/requirements and resolves entry references to a tier, spanning both functional and chrome-owning non-functional requirements; it is advisory. Every requirement specifying renderable screens carries an auto-assigned scribble task (pure rule/token/pattern requirements excluded). Ordering edges follow only the primary forward entry path (back/close/cross-nav are never ordering edges) and reach depth-1 only; each direct opener's basis resolves to a sibling scribble, else a current screenshot, else a blocking basis-scribble task (a screenshot used as basis must be validated current). A Tier-3-only entry is surfaced at the gate as a conscious decision rather than hard-blocked. [AC-09]

The **cross-feature launch seam** is owned by one app-shell / feature-launch-map requirement declaring primary destinations and each feature's entry hang-point — the canonical Tier-1 target; feature requirements needing the launch surface take a foundation dependency on it. Seam-ownership gaps are detected in two tiers — a local provisional `foundation_gap` at flow-derivation, then a global authoritative dedup-and-confirm at full flow-coverage verification — with the scribble-time requirement-source check as the final backstop. [AC-10]

**Domain→design conditional edge and facet tagging.** Every acceptance criterion of a Presentation-touching requirement carries a facet tag — `presentation`, `behaviour`, or `both` — determining its wave: presentation is locked by the scribble, behaviour is a coding task, both appears in both (its behaviour facet a coding task after the scribble). The tag is auto-heuristic then human-confirmed, failing safe to `presentation` on ambiguity so an ambiguous criterion always passes through the scribble gate; an audit records auto vs confirmed tag per criterion. A scribble is **data-bound** when its presentation/both criteria reference a domain value-object that itself has behaviour criteria in the same design-unit; it then carries a soft ordering preference to that domain task, hardened to a blocking dependency only for code-first design-units, with a human override at the gate. This is the only path by which domain code constrains design. [AC-11, AC-12]

**Soft-SCI mode.** Soft-SCI — letting a coding task proceed against a stale scribble with `provisional` output and a mandatory re-verify on refresh — exists only as a configurable mode that is **off by default** and enableable only with recorded developer sign-off. While off, SCI is a hard blocking invariant. The mode keeps a liveness escape hatch for densely-coupled releases without making the correctness relaxation a silent default. [AC-14]

