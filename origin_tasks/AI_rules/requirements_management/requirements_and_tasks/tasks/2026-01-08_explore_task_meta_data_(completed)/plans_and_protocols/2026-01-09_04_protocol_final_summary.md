# Final Protocol: Task Meta Data Exploration

**Date**: 2026-01-09
**Status**: Completed

---

## Summary

This exploration task investigated and defined standardized meta information for requirements.md and goal.md files. The work was done across two sessions with multiple exploration agents.

## Deliverables

### 1. Meta Information Specification (Complete)

Updated `requirements_and_tasks/requirements.md` with comprehensive specification:

- **YAML Frontmatter Templates**: For both requirements.md and goal.md
- **ID Generation Rules**: REQ-[CATEGORY]-[NUMBER] and TASK-[REQ-ID]-[NN]
- **Priority System**: Two-dimensional URGENCY (0-5) + IMPACT (0-5) with reason codes
- **Status Lifecycles**: For both requirements and tasks
- **Effort Scale**: T-shirt sizing (XS, S, M, L, XL)
- **Coverage Tracking**: trackable_items + covers bidirectional linking

### 2. Priority System Design

Based on user's discussion with Gemini:

| Dimension | Scale | Example Codes |
|-----------|-------|---------------|
| URGENCY | 0-5 | U5-BLOCK, U4-DEP, U3-SPRINT, U2-FREE, U1-COSM, U0-HOLD |
| IMPACT | 0-5 | I5-MVP, I4-USP, I3-STD, I2-JOY, I1-INV, I0-NONE |

**Score Calculation**: Priority = (URGENCY × 10) + IMPACT

### 3. Bidirectional Linking System

Designed in response to user's question about tracking requirement coverage:

**In requirements.md:**
```yaml
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "Description"
  sections:
    - id: SEC-01
      name: "Section Name"
      heading: "## X. Heading"
```

**In goal.md:**
```yaml
covers:
  acceptance_criteria: [AC-01, AC-02]
  sections: [SEC-01]
```

**Key Design Decisions:**
- IDs are immutable (never change even if text changes)
- Coverage computed at query time (not stored in requirements)
- Supports both AC-based and section-based tracking

### 4. Implementation Tasks (Bonus)

Created 3 implementation tasks for the actual migration:

| Task | Folder | Effort | Dependencies |
|------|--------|--------|--------------|
| **Foundation & Tooling** | `2026-01-09_impl_meta_info_foundation/` | M | None |
| **Requirements Migration** | `2026-01-09_impl_meta_info_requ_migration/` | L | Task 1 |
| **Tasks Migration** | `2026-01-09_impl_meta_info_task_migration/` | L | Task 2 |

**Scope:**
- 37 requirements.md files to migrate
- 49 goal.md files to migrate
- Validation and coverage report scripts to build
- setup-task skill to update

## Investigation Reports

Detailed findings are documented in:

1. `2026-01-08_01_protocol_investigation.md` - Initial exploration summary
2. `2026-01-08_02_report_meta_information_investigation.md` - Full meta info design report
3. `2026-01-08_03_protocol_requirement_task_linking.md` - Bidirectional linking investigation

## Agents Used

| Agent ID | Type | Purpose |
|----------|------|---------|
| ae09352 | Explore/Opus | Initial meta information investigation |
| ac022a4 | Explore/Opus | Bidirectional linking investigation |

## Key Insights

1. **Process requirements are already implemented** - Migration is bookkeeping, not investigation
2. **~60% of requirements have acceptance criteria** - Can use AC-based tracking for most
3. **Section-based tracking** needed for table-based requirements without explicit AC
4. **Coverage computed at query time** - Avoids synchronization issues
5. **ID immutability is critical** - Once assigned, IDs never change

## Next Steps

Execute the 3 implementation tasks in order:
1. Foundation & Tooling (creates tools for migration)
2. Requirements Migration (adds frontmatter to all requirements.md)
3. Tasks Migration (adds frontmatter and covers to all goal.md)

---

**Exploration Task Complete**
