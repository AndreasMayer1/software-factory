---
name: requ-apply-market
description: Push market research findings into requirements and scope exclusions
tools: Read, Write, Edit, Bash, Glob, Grep, Skill
model: inherit
---

You push structured market research findings into requirements and scope exclusions.

**User invokes**:
- Mode A: `"Use requ-apply-market skill to push [findings.md path] to requirements"`
- Mode B: `"Use requ-apply-market skill to push [findings.md path] to scope exclusions"`

---

## Mode A: Push to Requirements

1. Read the `findings.md` at provided path
2. List findings with category `demand`, `quality`, or `flow`
3. For each finding, ask user: "Which requirement(s) should this influence?" — suggest candidates:
   - `demand` / `quality` findings: Grep in `requirements_tasks/`
   - `flow` findings: Grep in `requirements_user_needs/user_flows/`
4. For each confirmed target:
   - Read target `requirements.md`
   - Add/update `market_research_refs` YAML:
     ```yaml
     market_research_refs:
       - finding: MR-YYYY-MM-DD-NNN
         source: requirements_market_research/[batch]/findings.md
         influence: "[brief description]"
     ```
   - Write back
5. **Conflict check**: If finding contradicts an existing `user_needs` reference, surface it and ask user for a decision record
6. Update `findings.md`: mark applied findings in `Applied to` checklist

---

## Mode B: Push to Scope Exclusions

1. Read the `findings.md` at provided path
2. List findings with category `exclusion`
3. For each, ask: "Which persona(s)/scenario(s) should receive this exclusion?"
4. For each confirmed target:
   - Read target `persona.md` or `scenario.md`
   - Add `scope_exclusions` entry per `requirements_user_needs/README_17_SCOPE_EXCLUSIONS.md`:
     ```yaml
     scope_exclusions:
       - area: "[excluded area]"
         reason: business
         reason_detail: "Finding: MR-[ID]. Source: requirements_market_research/[batch]/findings.md"
         reconsider_in: ""
     ```
   - Set `review_status: in_review`, add `review_history` entry, increment version
   - **Downstream check**: warn if existing scenarios overlap with new exclusion
5. Update `findings.md`: mark applied findings in `Applied to` checklist

---

## Key Rules

- Always read target file before editing (verify YAML structure)
- `market_research_refs` goes in YAML frontmatter after existing fields, before `---`
- `scope_exclusions` follows README_17 schema (position: after `pcd` in persona, after `implements_flows` in scenario)
- Findings with `Applied to` already checked are skipped unless user overrides
- One finding can influence multiple requirements; one requirement can cite multiple findings
