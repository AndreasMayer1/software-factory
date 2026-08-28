# User Initial Input (verbatim)

Captured 2026-06-11. The user's unedited thinking that prompted this task. Read it as
a seed bed, not a spec.

---

Die andere Dimension ist, zu sagen, wie wollen wir überhaupt Skills testen? Wir haben ja
den Plan, und das kannst du nachschauen, den Skill Test Playground planen wir. Und da
wollen wir ja eine App erstellen, die benutzt wird, um Skills zu testen. Das funktioniert
für Skills, die bestimmte Tests auch erlauben. Wo wir eigentlich wissen, was das Ergebnis
sein wird. Es gibt aber auch Skills, die sind ergebnisoffen, wie zum Beispiel der neue
Ideation Workflow. Wie könnten wir einen Test dafür definieren, der tatsächlich durch ein
LLM überprüfbar ist?

[Die erste Dimension des Ausgangs-Inputs — ein interactive_required-Flag für Tasks, die
interaktiv laufen müssen — ist in einem Schwester-Task unter REQ-PROC-069
(task_execution_entry) festgehalten.]

---

## Orchestrator notes added at capture time (context, not spec)

- The Skill-Test Playground epic (REQ-PROC-068) already prescribes, in **AC-04**, that each
  workflow test carries a `run_instructions` file + a **non-boolean quality-scale outcome
  rubric** that the six measurement probes (feat_measurement_instrumentation, REQ-PROC-068-05)
  feed. This task does not invent a new mechanism — it *refines AC-04* for the specific hard
  case the user raised: **open-ended skills** whose output has no single correct answer.
- Discussion seed offered by the orchestrator (a candidate three-layer shape, NOT a decision):
  1. **Deterministic structural invariants** (no LLM): did the skill emit the artifacts it must
     (e.g. ideation: ledger YAML, correct frames × techniques, post-check PASS, criteria panel,
     gate written)? Cheap, hard pass/fail. Ideation already runs such deterministic post-checks.
  2. **Rubric-scored quality via LLM-as-judge**: quality dimensions invariant across topics even
     when content is open-ended — e.g. coverage, non-redundancy, criteria soundness, synthesis
     fidelity, gate honesty — each scored 1–5 against *anchored* level descriptions. Result is
     "quality ≥ threshold", not "correct/incorrect".
  3. **Golden-trace differential / regression**: freeze a reference run (ledger + gate) for a
     fixed topic + seed; on skill change, re-run and have an LLM judge compare new-vs-reference —
     "at least as good, and did the intended improvement appear?"
- The load-bearing trick proposed: make the criteria about **process and the artifact's internal
  consistency**, not content correctness. "Did it explore widely, score coherently, represent
  itself honestly at the gate" is LLM-checkable; "is this the right idea" is not — and is the
  human's job at the gate, not the test's.
- Bridge to the sibling task (REQ-PROC-069 interactive_required): part of an open-ended skill's
  value is the human-in-the-loop gate. For an *automated* test, let an LLM play a developer
  persona walking the gate and score the *quality of the interaction* ("did the gate give the
  simulated user enough to decide well?") rather than the final artifact.
