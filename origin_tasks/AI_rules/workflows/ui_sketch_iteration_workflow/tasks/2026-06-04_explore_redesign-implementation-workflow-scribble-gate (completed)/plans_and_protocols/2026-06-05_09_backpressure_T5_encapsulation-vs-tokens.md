# Back-pressure report — T5: skill encapsulation / single-responsibility vs token-efficiency

Task: TASK-PROC-032-29. Date: 2026-06-05.
Developer's words: *"encapsulation: are our phases defined by the skills encapsulated (enough)? and with
single responsibilities? but of course it still holds: token efficiency, that's more important, but we need
to make the trade off decisions explicit in the requ that describe the skills."*

Grounded against Round-1 synthesis §2 (3-skill topology + `--scope` mode on `task-derive-from-requ`), §9 D-0
(the `create_orchestration_task.py` L276 `ui-create-scribble` routing string that matches no real skill), and
the eval substrate §3 cross-cutting theme ("almost every fix anchors to machinery that already exists —
enhancements, not new subsystems").

---

## Level 1 — the topic as a whole

### The rationale being pressured
*"Skills should be encapsulated with single responsibilities — but token-efficiency is more important, so
where they conflict, token-efficiency wins; just record the trade-off in the requirement."*

### The one correction to the rationale (load-bearing)
"Token-efficiency is more important" is true **except where the encapsulation loss creates a correctness
risk** — and we already have proof it can:

> **D-0** is an encapsulation/clarity failure. `create_orchestration_task.py` L276 routes `task_type: scribble`
> to the skill string `ui-create-scribble`, **which does not exist** (the real skill is `ui-scribble-iterate`).
> A routing table that silently names a non-existent skill is exactly what under-encapsulation produces — the
> producer of the string and the consumer of the string drifted apart with no contract binding them, and
> nothing caught it. Today's chain would fail to run any scribble task.

So the correct principle is **tokens win *unless* the clarity loss risks correctness** — not "tokens always
win." D-0 is the empirical cost of the latter.

### What speaks against the "tokens-always-win" framing
1. **Under-encapsulation has already cost correctness (D-0).** An invariant that says "optimise tokens, lose
   clarity" with no floor will keep producing D-0-class bugs (silent contract drift between a producer and a
   consumer that no longer share an enforced interface).
2. **"Encapsulated enough" is unmeasurable as stated** — there is no test, so the question can't be answered,
   only asserted. It needs an operational definition.
3. **The redesign introduces the most-likely-to-rot seam.** `task-derive-from-requ` gaining a
   `--scope {presentation,code}` flag is the classic "two skills hiding in one coat" smell — a mode flag that
   switches a skill between two genuinely different responsibilities (decompose-for-design vs decompose-for-
   code). This is precisely the kind of seam where token-efficiency and encapsulation collide.

### Where token-efficiency genuinely wins (and the trade-off is right)
The `--scope` flag *should* stay one skill, because the two modes share heavy machinery: reading the
requirement, parsing ACs, knowing the plan format (REQ-PROC-058), the design-unit map. Splitting into two
skills (`derive-design-tasks` / `derive-code-tasks`) would re-load all of that twice → more tokens, and two
copies of the plan-format knowledge to keep in sync (a *new* drift surface). So here the single-skill choice
is correct — **but it must be recorded as a conscious trade-off**, not left implicit, precisely because it is
the seam most likely to drift (the next D-0 candidate).

### How to make "encapsulated enough" measurable
Propose an operational test (cheap, auditable):
> A skill is **encapsulated enough** if (a) its single responsibility fits in one sentence, and (b) its inputs
> and outputs are nameable as **artifacts** — it consumes artifact X, produces artifact Y. Where a skill
> carries more than one responsibility for token reasons, it must declare each artifact-in→artifact-out pair.

The factory already has the substrate: `.factory/registry/artifacts.yaml` + `scripts/factory/render_factory_map.py`
(which skills produce/consume which artifacts). Encapsulation can be **checked against the registry** — a skill
whose artifacts-in/out can't be expressed in the registry is under-specified. This turns "enough?" from a
judgement call into a registry-completeness check, and would have caught D-0 (the producer emits a `task_type`
artifact value with no consumer skill registered for it).

### How to make the trade-off explicit in the requirement (the developer's actual ask)
Standardise a **skill-design trade-off record**, analogous to the existing `vcd-log-tradeoff` (which records
persona-value conflicts inline in an artifact). Concretely:
- Add an AC to **REQ-PROC-035** (release/orchestration skills) and **REQ-PROC-058** (task-creation plan
  format): *every skill states its single responsibility in one sentence; where it carries more than one for
  token-efficiency, the requirement records (i) the responsibilities fused, (ii) the encapsulation sacrificed,
  (iii) why tokens won, (iv) the drift risk and its mitigation (the enforced contract / registry entry).*
- For the redesign's specific cuts, write the records now:
  - **begin → derive-code → finalize as 3 skills, not 1:** encapsulation *win* (each holds only its wave's
    context — the strongest token argument too: a single skill would hold design+code context at once). No
    trade-off sacrificed; record it as a clean split.
  - **`task-derive-from-requ --scope`:** token *win* over a 2-skill split; encapsulation sacrificed = one
    skill carries two decomposition responsibilities; mitigation = a shared core with two thin scope branches
    + an enforced plan-format contract + registry entry per scope. Record it explicitly as the deliberate
    trade-off the developer asked to see.

### Net position
- Adopt the principle **tokens win unless clarity loss risks correctness** (D-0 is the proof of the
  exception).
- Make "encapsulated enough" the **artifact-in→artifact-out registry test**, not a vibe.
- Standardise a **skill-design trade-off record** as an AC in REQ-PROC-035/058; write the records for the
  redesign's cuts now.

---

## Level 2 — chapter by chapter

### "are our phases defined by the skills encapsulated (enough)?"
- **Pressure:** unanswerable without a test. Mostly yes for the 3-skill bracket (clean wave boundaries);
  weakest at the `--scope` seam.
- **Action:** adopt the artifact-in→artifact-out registry test; run it against the redesigned skills; the
  `--scope` seam passes only if both scopes have explicit registry entries.

### "and with single responsibilities?"
- **Pressure:** the 3-skill split is single-responsibility (begin=design wave, derive-code=code wave,
  finalize=audit). `task-derive-from-requ --scope` is *not* single-responsibility — it is two, deliberately
  fused.
- **Action:** allow the fusion, but only with a recorded trade-off and an enforced contract; do not pretend
  it is single-responsibility.

### "but of course it still holds: token efficiency, that's more important"
- **Pressure:** *more important, not absolute.* D-0 is the counter-example where token-driven
  under-encapsulation already produced a latent correctness bug.
- **Action:** encode the bounded principle (tokens win unless clarity loss risks correctness) in the
  requirement, with D-0 cited as the rationale.

### "we need to make the trade off decisions explicit in the requ that describe the skills"
- **Pressure:** fully agree; today these decisions are implicit in skill code (which is how D-0 hid).
- **Action:** standardise the skill-design trade-off record (AC in REQ-PROC-035/058); write the records for
  the redesign cuts; make it auditable via the artifact registry.

---

## Residual uncertainty (honest)
- **The artifact registry may not yet model `task_type`-style routing values** (the D-0 locus). If the
  registry can't express "this skill emits a plan entry whose `task_type` must resolve to a registered skill,"
  the registry test won't catch D-0-class bugs. Whether the registry is expressive enough for routing
  contracts is unverified — may need an extension before it can serve as the encapsulation check.
- **The trade-off record risks becoming ceremony.** If every skill must carry a trade-off paragraph, the
  cheap/obvious skills get boilerplate. Mitigation: only *fused-responsibility* skills must carry the full
  record; single-responsibility skills carry just the one-sentence responsibility. The threshold ("when is a
  record required") needs a clean rule.
- **Whether token-efficiency and encapsulation actually conflict as often as assumed** is unexamined. The
  3-skill split shows they often *align* (smaller context = both fewer tokens and cleaner responsibility). The
  genuine conflict cases may be rarer than the framing implies — possibly only the `--scope` seam in this
  whole redesign. If conflicts are rare, the trade-off record is a light-weight, occasional artifact, not a
  pervasive tax.
