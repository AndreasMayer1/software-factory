# User's Initial Input — Verbatim

Preserved as written, including the user's framing, typos, and emphasis. This is
the seed bed for the exploration — not a specification.

---

> do we already have a requirement that describes when and how the dependencies of the project get updated? when the llm can do it autonomously? Is it done by creating a new task? is it done after every release? what frequency is good? what trigger fits? how to make sure the updates do not break anything? how and when to fix the broken things and move away from deprecations? how to decide to move to a new package if an old one does not work anymore? how to decide to which packe to move?
> also: (maybe another requirement) how to decide on new dependencies? when is it allowed to install a new one? what is the llm allowed to to autonomously? how to make sure only safe packages are used?
>
> Im sure there are even more questions in that domain... pleas eread what we already have. and find the gaps.

---

## Assistant's Preliminary Gap Analysis (offered in the same conversation, BEFORE this exploration begins)

The assistant's first-pass response — to be treated as **one possible shape** of the answer, not as the answer itself. The exploration must validate, restructure, expand, or refute it.

**What exists already:**

- `REQ-PROC-056` — Dependency Supply-Chain Safety. Defines the **intake gates** (DG1 min-age 7d, DG2 advisory clearance, DG3 evidence artifact, DG4 composability) that any version pin landing in `pubspec.yaml` / Python manifests / npm manifests must pass. Scope is limited to *which version of an already-decided dependency is admissible at the moment of intake*. Explicitly out of scope: re-evaluation cadence, whether a dependency should exist at all, deprecation handling, replacement decisions.
- `REQ-PROC-046` (code quality), `REQ-PROC-002` (testing), `REQ-PROC-052` (privacy/security) — the gate set that catches **breakage** when an update is made, but says nothing about *when* updates happen or *how to remediate* within an update workflow.

**Provisional four-requirement decomposition (assistant's first guess):**

1. **Update cadence + workflow** — When and how existing dependencies get refreshed. Trigger model (time-based vs. event-based vs. opportunistic). Whether an update is a dedicated `impl` task, a release-pipeline step, or a free-standing automation loop. LLM autonomy boundary. Regression-confirmation contract beyond the existing quality gates. Partial-update bookkeeping when some bumps fail the REQ-PROC-056 gates.
2. **Deprecation + replacement** — When `dart fix --apply` deprecation warnings, abandoned-maintainer signals, or "the package no longer fits" decisions trigger action. Selection rule for the replacement (download count, maintainer activity, license, transitive footprint, capability surface). How and when migration work is scoped.
3. **New-dependency admission** — When is adding a *new* top-level dependency allowed at all? Justification gate ("write it yourself vs. pull a package" — threshold, security-critical domains). Required pre-add evaluation (maintainer reputation, license compatibility, transitive footprint, capability surface). LLM autonomy boundary for new dependencies vs. version updates.
4. **Package-level safety beyond version (sibling to REQ-PROC-056)** — Maintainer-takeover risk, license compatibility (esp. for sensitive-data app), capability check (does the package even *have* network/telemetry surface that could conflict with SP1/SP2 later?), abandonment/staleness as a safety signal in its own right.

**Open meta-questions the exploration must address:**

- Are these four the right cuts, or is the natural decomposition different (e.g. one combined "dependency lifecycle" requirement; or two — admission + lifecycle; or five — splitting "package-level safety" further into licensing and capability)?
- Are there dimensions completely missing from the assistant's first-pass list? (User explicitly suspects there are — *"I'm sure there are even more questions in that domain"*.)
- Where does the existing REQ-PROC-056 boundary actually need to grow vs. where do new requirements need to be created?
- What is the LLM-autonomy taxonomy — what dependency operations are "fully autonomous", "autonomous with recorded evidence", "require human pre-authorization", "forbidden"? This taxonomy probably spans all four (or more) proposed requirements and may itself warrant a shared section.
