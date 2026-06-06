# Protocol: TASK-PROC-010-13 Planning Phase

## 2026-02-07 [Initial Planning]

**Agent**: architecture-advisor
**Agent ID**: architecture-advisor-2026-02-07-001
**Phase**: Planning (Opus-level analysis with Sonnet execution)

### Action

Created comprehensive high-level implementation plan for integrating SCENARIO_INDEX.md into workflows and skills.

**Context Gathered**:
- Read goal.md (task objectives, acceptance criteria, scope)
- Read SCENARIO_INDEX.md (structure, categories, existing mappings)
- Read create-scenario skill (current workflow, integration points)
- Read modify-user-needs skill (Opus/Standard modes, metadata update logic)
- Read README_4_SCENARIO_DEFINITION.md (scenario template, checklist)
- Read README_7_META_INFO_STANDARDS.md (YAML frontmatter standards)
- Analyzed existing scenario with category/gold_status fields (SCEN-002-01)

**Analysis Performed**:
- Gap analysis between current skills and required functionality
- Architecture strategy for YAML manipulation and bidirectional consistency
- Risk assessment for YAML formatting, backward compatibility, token bloat
- Testing strategy for manual verification and integration testing

**Plan Created**: `2026-02-07_01_high_level_plan.md`

### Outcome

✅ **PASS** - Comprehensive plan created with:

**Scope of Work**:
- 4 files to modify (within CLAUDE.md limit):
  1. `.claude/skills/create-scenario/skill.md` (~80 lines added)
  2. `.claude/skills/modify-user-needs/skill.md` (~30 lines added)
  3. `requirements_user_needs/README_4_SCENARIO_DEFINITION.md` (~150 tokens)
  4. `requirements_user_needs/README_7_META_INFO_STANDARDS.md` (~100 tokens)

**Architecture Strategy**:
- Read-first architecture (skills read index, don't hardcode)
- Bidirectional consistency (index ↔ scenarios)
- Graceful degradation (backward compatibility)
- Minimal documentation (link to index, don't duplicate)

**Key Modifications**:
- create-scenario: Add category selection, index update, gold workflow
- modify-user-needs: Add index maintenance on metadata changes
- READMEs: Minimal additions pointing to SCENARIO_INDEX.md

**WHY Comments Requirements**:
- YAML parsing strategy (string-based to preserve comments)
- Gold workflow timing (ask before creation, not after)
- Index update sequence (scenario first, then index)

**Testing Strategy**:
- Manual verification (no automated tests for documentation work)
- Validation checklist (9 skill integration checks, 5 documentation checks, 5 quality checks)
- 4 manual testing scenarios (new scenario, gold standard, modify gold, backward compat)

**Risks Identified**:
1. YAML parsing breaks formatting (Low probability, mitigated by validation)
2. Skills become too complex (Low probability, isolated changes)
3. Backward compatibility issues (Very low, additive fields)
4. README token bloat (Very low, <250 tokens total)
5. Index sync drift (Low, bidirectional updates)

**Execution Recommendation**:
- Single `implementation-engineer` agent (no Flutter code, consistency important)
- Estimated effort: 5-7 hours (M effort as specified)

### Quality Checks

- [x] All acceptance criteria from goal.md addressed
- [x] Architecture follows SCENARIO_INDEX.md design (TASK-PROC-010-12)
- [x] No breaking changes to existing functionality
- [x] Backward compatibility maintained
- [x] WHY comments identified for non-obvious decisions
- [x] Testing strategy defined (manual verification)
- [x] Risks identified with mitigations
- [x] File count within CLAUDE.md limit (4 files)

### Questions for User Approval

1. **Gold standard prompt**: Should it be mandatory or optional? (Current plan: optional)
2. **Category enforcement**: Prevent creating scenarios without category? (Current plan: yes, enforce)
3. **Auto-suggest category**: Should skill suggest category from keywords? (Current plan: no, manual selection)

### Next Step

**Awaiting user approval** of plan before implementation.

**After approval**:
1. Spawn `implementation-engineer` agent
2. Agent reads this plan + goal.md
3. Agent implements 4 file modifications
4. Agent runs validation checklist
5. Agent performs manual testing
6. Agent logs completion protocol

**Resume command**: `Resume agent architecture-advisor-2026-02-07-001` (if plan needs revision)

---

## Agent Execution Log

| Timestamp | Agent | Action | Status |
|-----------|-------|--------|--------|
| 2026-02-07 | architecture-advisor-2026-02-07-001 | Created high-level plan | ⏸️ Awaiting approval |

---

**Protocol Status**: Active
**Plan Status**: Awaiting User Approval
**Next Agent**: implementation-engineer (pending approval)
