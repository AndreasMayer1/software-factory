# Ideation Report (Phase 3) — TASK-PROC-004-02

Dogfooding REQ-PROC-004's seven techniques on the HOW. Divergent; **no self-censorship** — filtering happens in synthesis. Each idea tagged by feasibility: (a) doable now, (b) significant effort, (c) breakthrough/external.

## Technique 1 — Cross-domain mapping
- **I1 (Manufacturing / kanban)** (a): the gap-ledger is a WIP board; each gap is a card pulled through `open→in_progress→answered`. Termination = empty board. Directly reuses the factory's existing "tracker in plans_and_protocols" idiom.
- **I2 (Compilers — fixpoint iteration)** (a): run ideation passes until the ledger reaches a *fixpoint* (no new gaps added, none closed). Classic dataflow-analysis termination. Gives a precise "no gaps remain" definition.
- **I3 (Genetics — diversity via isolated demes)** (b): run divergence branches as isolated populations (ADHD), then "migrate" best ideas between them in a merge step. Anti-anchoring by construction.
- **I4 (Journalism — the 5 W's as breadth checklist)** (a): seed the breadth axis of the ledger with a fixed question scaffold so "sub-questions never opened" is detectable against a template.
- **I5 (Civil engineering — load testing)** (a): inversion-as-stress-test; deliberately ask "what gap would embarrass us most?" to seed depth gaps.

## Technique 2 — Association chains
- core: *pause* → checkpoint → savepoint (DB) → **the answer.md sentinel is already a savepoint** → orchestrator resume is already a restore → **I6 (a): the completeness loop's continuation = same orchestrator-resume mechanism as the user gate**, just with an *auto-answer* ("CONTINUE") instead of a human one.
- core: *gap* → hole → negative space → **I7 (b): represent coverage as the analyze-phase scope map minus answered items** (gap = scope − coverage), making gap-detection a set-difference rather than a vibe.
- core: *creativity* → randomness → seed → PRNG seed → **I8 (a): inject a per-branch "random stimulus" token from a curated wordlist file** so divergence is reproducible and auditable.

## Technique 3 — Inversion ("make it fail spectacularly")
- **F1**: the loop never terminates on an inherently open question → invert → **I9 (a): hard max-iteration cap bound by effort** (Quick 1, Standard 2, Deep 3–4), backed by the 75%-in-2-rounds evidence.
- **F2**: critic rewrites correct content into wrong (oscillation) → invert → **I10 (a): critic may ONLY append gap rows, never edit settled synthesis.**
- **F3**: two gates confuse the user → invert → **I11 (a): unify into ONE gate that fires only at effort-appropriate moments** (synthesis-ready OR capped-with-open-gaps).
- **F4**: agent self-certifies "done" but is biased → invert → **I12 (b): a separate reviewer-role agent certifies emptiness**, reusing the han-adversarial-validator pattern.
- **F5**: context pollution makes main session expensive → invert → **I13 (a): divergence + gap-detection run in sub-agents; main session only holds the ledger + final docs.**
- **F6**: nobody reads the wild ideas (the original complaint) → invert → **I14 (a): the gate file leads with "most unusual idea" + cluster map, per the observability-gap finding.**

## Technique 4 — Analogical reasoning (solved problem elsewhere)
- **I15 (a)**: **`requ-verify-flow-coverage` is already this loop** — Phase-1 per-gap extraction files + Phase-2 synthesis with "CONFIRMED GAPS / NEEDS USER DECISION". Adapt its structure rather than invent.
- **I16 (a)**: **verify-quality's `cycle_state.json` + 5-cycle back-pressure** is already a bounded-iteration-with-escalation loop. The completeness loop is the same shape: iterate, count, escalate-to-human at cap.
- **I17 (b)**: GPT-Researcher's breadth/depth params → expose `breadth`/`depth` knobs derived from effort tier.

## Technique 5 — SCAMPER (on the existing requ-explore skill)
- **Substitute** (a) **I18**: replace requ-explore's single gather→synthesis with gather→**ideate→gate→synthesize**.
- **Combine** (a) **I19**: combine the ideation gate and the completeness escalation into one `pending_feedback` write with a `mode:` field (`ideation_review` | `gap_escalation`).
- **Adapt** (a) **I20**: adapt `should_use_agents.py` thresholds to decide inline-vs-branch-agents for divergence.
- **Modify/Magnify** (b) **I21**: magnify the Seeds section of the explore template into a full divergence sub-protocol.
- **Put to other uses** (a) **I22**: the same ideation protocol serves code-complex's architecture planning and ux-create-flow.
- **Eliminate** (a) **I23**: eliminate a *dedicated* ideation skill entirely — express it as a **protocol doc** that existing skills `Read` and follow (no new always-loaded skill, honors token economy).
- **Rearrange/Reverse** (b) **I24**: reverse order — run a cheap gap-detector FIRST to decide whether divergence is even needed (skip ideation for low-unknown tasks).

## Technique 6 — Random stimulus
- random word **"thermostat"** → **I25 (a): the loop is a thermostat with a setpoint** = effort-derived target coverage; it runs until measured coverage ≥ setpoint OR max-iter. Closed-loop control framing for termination.
- random word **"passport"** → **I26 (b): each idea/gap carries a "stamp" of which frame/branch produced it**, so synthesis can detect mono-frame blind spots (all gaps from one frame ⇒ breadth hole).
- random word **"compost"** → **I27 (a): discarded ideas are not deleted but kept in a `## Discarded` heap with reasons** (REQ-PROC-004 already wants this) — and re-surfaced if a later gap matches.

## Technique 7 — Feasibility spectrum (per major direction = "the vehicle")
- (a) **I28 — Protocol-section vehicle**: a single `doc/process/ideation_protocol.md` + a tiny reusable `*-reviewer` agent for gap-detection; skills opt in by reading the protocol. Cheapest; no new always-loaded skill.
- (b) **I29 — Dedicated `ideate` skill** that orchestrates phases, spawns branch agents, writes the gate file.
- (b) **I30 — Reusable `ideation-explorer` agent** invoked by any skill; isolated context, returns ledger + synthesis. The user's original instinct.
- (c) **I31 — A custom API wrapper** that calls the Anthropic API directly with temperature 0.9 per-phase, bypassing the CLI limitation. (Blocked by C1/C5; documented for when the factory gains direct API calls.)
- (c) **I32 — A persistent "ideation server"** that holds divergence state across sessions and streams gaps. Over-engineered; parked.

## Most interesting / most unusual
- **Most unusual: I31** (direct-API temperature wrapper) — currently blocked but the only path to a real temperature knob; worth recording as a future unlock.
- **Most interesting: I6 + I16 + I15** — the factory *already contains* the completeness loop (orchestrator resume = continuation; cycle_state back-pressure = bounded loop; requ-verify-flow-coverage = gap extraction→synthesis). The implementation may be mostly *composition of existing parts*, not new machinery.
- **Sharpest definition: I2/I25** — fixpoint / thermostat framing gives "no gaps remain" an operational meaning instead of a vibe.
