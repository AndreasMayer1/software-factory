# Developer initial input — seed bed (verbatim intent)

Captured 2026-07-14 (interactive). Read as a seed bed, not a spec.

## What prompted this task

After TASK-PROC-068-26 hit the degenerate-span / harvest-oracle blocker and I applied a per-task
Option-A workaround to 068-26 and 068-12, the developer asked, in sequence:

- "Is the escalation in that case the right thing? Does the spec template not explanatory enough?"
- On the spec: "how is the spec created? the user does not write it by hand, he uses a llm to do it.
  how does the llm know what to do? do we need a skill for that?"
- On correctness: "I would expect that layer derivation refuses to start without the mandatory layers
  present anyways."
- On placement: "doc/. is not the correct place for that (it only contains product level guidance)."
- Directive to create the prevention work: "please create #1 + #2 as one mechanism task. and add its
  id to the override file." (#1 = root-cause disposition fix; #2 = harvestability pre-flight.)
- On grounding: after being asked "do they include requirement changes?", the developer directed:
  "The task must also modify the requ if needed and do a ideation."

## The intent, distilled

1. The mechanism's ESCALATED disposition for a degenerate (zero-authoring-pair) span is suspect — it
   conflates "no-op/skip" with "blocked", and the strict all-DONE harvest oracle then refuses to harvest
   a legitimately-complete chain. Fix the root cause.
2. Add a plan-time guardrail so a spec that can never harvest fails loudly at plan time, not after a
   wasted deployed run ("plan-success ≠ harvestable").
3. The spec is authored by an LLM, not the developer, and there is no governed template/skill teaching
   the span↔unit model. Provide that guidance in the skill/mechanism layer — NOT `doc/` (product-level
   only). Decide skill-vs-extend-`layer-derivation-start`.
4. This must be grounded: do a proper ideation on the design, and modify the requirement(s) if needed
   (the disposition change collides with the HIGH-consequence AC-18 blame clause; the pre-flight and
   authoring surface are net-new capabilities). Then emit the impl.

## Open tensions to explore (not answers)

- Fix locus: mechanism vacuous-DONE vs. oracle tolerance vs. don't-emit-a-unit-for-a-zero-pair-span.
- How to clarify AC-18/AC-19 so a degenerate no-op is excluded from "abandoned" without weakening the
  real "skill-under-test silently under-finished" guarantee.
- The smallest reliable authoring artifact (template / contract / skill).
