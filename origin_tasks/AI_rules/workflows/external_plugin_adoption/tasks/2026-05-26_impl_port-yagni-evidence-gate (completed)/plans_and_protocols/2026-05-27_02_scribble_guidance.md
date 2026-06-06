# YAGNI Gate — Scribble Skill Application Guidance

**For:** TASK-PROC-032-09 (editing `ui-create-scribble`)
**Written by:** TASK-PROC-055-02 session 60b73e52

---

## How the YAGNI Evidence Gate Applies to Scribble Phase 2 Auto-Review

The YAGNI gate ported in this task has a direct application in the `ui-create-scribble`
skill's Phase 2 auto-review of generated screen states.

### Gate 1 — Inclusion (evidence test for screen states)

Before committing any generated screen state, the skill should check: "Is there evidence
in the requirement or flow that:
(a) this state can actually occur (a code path leads to it), AND
(b) the system has the information available to render it (the required data exists at that
    point in the flow)?"

Accepted evidence forms:
- A named flow step or scenario that triggers this state
- A requirement AC that requires handling this case
- A data model field whose presence enables the rendering

States lacking both (a) and (b) are speculative and should be flagged, not silently generated.

### Gate 2 — Shape (simpler-variant test for screen states)

When a state is evidenced, ask whether a simpler variant satisfies the same evidence.
Annotate over-elaborate states rather than generating them at full complexity.

### Deferred Format for Scribble (HTML comment convention)

States failing Gate 1:
```html
<!-- state-deferred: [reason — what evidence is missing]
     reopen-when: [named trigger — e.g. "when the API returns X", "when flow step N is defined"] -->
```

States failing Gate 2 (over-elaborate but evidenced):
```html
<!-- state-simplify: [simpler variant that satisfies the same evidence] -->
```

### Integration Point in ui-create-scribble

The gate should run as a sub-step in Phase 2 (auto-review), after states are generated
but before they are committed to the scribble output. Suggested placement:

> After generating all screen states from the flow/requirement, and before writing the
> final scribble: for each state, run the two-gate check. Add `<!-- state-deferred: ... -->`
> or `<!-- state-simplify: ... -->` comments inline. Never silently drop a state — always
> use the comment to make the deferral visible.

### User Override

Any flagged state can be promoted by the user. The comment makes cost visible; it does
not veto the user. The override rationale is noted next to the comment.

---

## Reference: Standard Deferred Format (from this task)

The same gate in planning skills uses this format in plan documents:
```markdown
## Deferred (YAGNI)

### {item name}
**Why deferred:** [missing evidence]
**Reopen when:** [named trigger]
**Source:** [where the hypothetical originated]
```

The scribble variant above (`<!-- state-deferred: ... -->`) is the HTML-comment equivalent
for inline use within scribble markup.
