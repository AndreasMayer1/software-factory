# High-Level Implementation Plan: Smart Model-Switching Integration

**Agent ID**: architecture-advisor (session instance tracking TBD via log-protocol)
**Created**: 2026-01-11
**Task**: TASK-PROC-WF-SMART-001

---

## Executive Summary

This plan outlines the integration of cost-efficient model-switching (Sonnet gather → Opus think → Sonnet execute) into 6 skills and 2 agents. The pattern is already proven in `opus-workflow` skill and uses the `switch-to-opus` skill as the mechanism for model transitions.

**Core Principle**: All changes are OPTIONAL. Default behavior (Sonnet-only) remains unchanged. Users must explicitly invoke Opus mode.

---

## 1. Analysis of Reference Implementation

### 1.1 The `opus-workflow` Pattern

**File**: `.claude/skills/opus-workflow/skill.md`

**Key Mechanism**:
1. **Phase 1**: Spawn Sonnet agent → gathers information (cheap)
2. **Phase 2**: Agent invokes `switch-to-opus` skill → Opus plans with full context (expensive but strategic)
3. **Phase 3**: Return to main conversation (Sonnet) → execution follows Opus plan (cheap)

**Critical Insights**:
- Skills preserve context when invoked (no new context window)
- `switch-to-opus` has `model: claude-opus-4-5-20251101` in frontmatter → automatic switch
- When skill completes, model returns to previous state
- Agents can't nest, but agents CAN invoke skills
- Context window preserved across skill invocations

### 1.2 The `switch-to-opus` Skill

**File**: `.claude/skills/switch-to-opus/skill.md`

**Purpose**:
- Takes over with Opus model while preserving full context from Sonnet
- Creates detailed plan/analysis file
- Returns control with plan path and summary

**Key Properties**:
- `model: claude-opus-4-5-20251101` → forces model switch
- No new context window (skill invocation)
- Writes plan to `plans_and_protocols/[date]_01_opus_plan.md`
- Returns: plan path, summary, execution details

**When to Use**:
- Heavy reasoning needed (strategic planning, complex analysis)
- After information gathering is complete
- Context window has room (gathered info + plan won't overflow)

---

## 2. Integration Strategy by Component

### 2.1 Skills Overview

| Skill | Opus Integration Point | Complexity | Risk |
|-------|----------------------|------------|------|
| complex-implementation | Via architecture-advisor agent | Medium | Low |
| create-impl-task | Step 3.3 (goal.md writing) | Low | Low |
| explore-requirements | Phase 3 (synthesis & writing) | Medium | Medium |
| test-implementation | Via test-engineer agent | Low | Low |
| update-guidelines | TBD (instructions pending) | Low | Low |
| verify-quality | TBD (instructions pending) | Low | Low |

### 2.2 Agents Overview

| Agent | Opus Integration Point | Complexity | Risk |
|-------|----------------------|------------|------|
| architecture-advisor | After Phase 1 (context gathering) | Medium | Medium |
| test-engineer | Phase 1: Steps 3-4 (analysis & plan) | Low | Low |

---

## 3. Detailed Modification Plan

### 3.1 Architecture-Advisor Agent

**File**: `.claude/agents/architecture-advisor.md`

**Current Flow**:
1. Read Context (goal.md, doc/, codebase)
2. Analyze (layers, files, patterns)
3. Plan (create plan file)
4. Output (use log-protocol, return plan path)

**Modified Flow** (when Opus mode enabled):
1. Read Context (goal.md, doc/, codebase) — **SONNET**
2. **NEW**: Invoke `switch-to-opus` skill — **MODEL SWITCH**
3. Analyze (with full context) — **OPUS**
4. Plan (create plan file with deeper reasoning) — **OPUS**
5. **switch-to-opus completes** — **MODEL RETURNS TO SONNET**
6. Output (use log-protocol, return plan path) — **SONNET**

**Implementation Details**:
```markdown
**When spawned with Opus mode enabled**:

1. **Phase 1 - Read Context** (Sonnet):
   - goal.md (understand task)
   - doc/architecture.md (architecture rules)
   - doc/domain.md or doc/presentation.md (layer-specific rules)
   - Current codebase (analyze affected files)

2. **Phase 2 - Switch to Opus** (if Opus mode requested):
   - Invoke `switch-to-opus` skill
   - Skill will perform analysis and planning with Opus
   - Skill creates `plans_and_protocols/[date]_01_high_level_plan.md`
   - Skill returns with plan path and summary

3. **Phase 3 - Finalize** (Sonnet):
   - Use log-protocol skill (save agent ID)
   - Output: "Plan created at [path]. Please review and approve."

**When spawned WITHOUT Opus mode** (default):
   - Execute original flow (Phase 1 becomes Phase 1-2, Phase 2 becomes Phase 3)
```

**WHY Comments Needed**:
- WHY: Conditional model switching pattern allows cost optimization while preserving quality
- Source: requirements_tasks/.../2026-01-11_impl_update_claude_skills/plans_and_protocols/2026-01-11_01_plan_skill_updates.md#3.1

**Changes Required**:
1. Add frontmatter note about optional Opus mode
2. Add conditional logic for Opus invocation
3. Update phase numbering to account for new phase
4. Preserve backward compatibility (default = no Opus)

---

### 3.2 Complex-Implementation Skill

**File**: `.claude/skills/complex-implementation/skill.md`

**Current Flow**:
1. Setup (setup-task)
2. Plan (spawn architecture-advisor)
3. Plan Size Check
4. User Approval
5. Implement (spawn implementation-engineer)
6. Quality (verify-quality)
7. Log (log-protocol)
8. Complete (complete-task)
9. Commit

**Modified Flow** (when Opus mode enabled):
- Step 2 changes: Pass Opus mode flag to architecture-advisor agent
- Architecture-advisor handles Opus internally
- No other changes needed

**Implementation Details**:
```markdown
**Optional Opus Mode**: This skill can use Opus for strategic planning while keeping costs low for execution.

**User invokes**:
- Standard: "Use complex-implementation skill for [task name] in [path]"
- With Opus: "Use complex-implementation skill with opus for [task name] in [path]"

2. **Plan**: Spawn architecture-advisor agent:
   - **If Opus mode**: Add instruction "Use Opus for planning phase"
   - Reads goal.md + relevant doc/ guidelines
   - Analyzes codebase
   - Creates high-level plan in plans_and_protocols/
   - Uses log-protocol skill (with agent ID)
```

**WHY Comments Needed**:
- WHY: Optional Opus mode delegation to architecture-advisor enables strategic planning without changing skill structure
- Source: requirements_tasks/.../2026-01-11_impl_update_claude_skills/plans_and_protocols/2026-01-11_01_plan_skill_updates.md#3.2

**Changes Required**:
1. Add frontmatter note about optional Opus mode
2. Add conditional instruction passing to architecture-advisor
3. Document invocation syntax for Opus mode
4. Preserve backward compatibility

---

### 3.3 Create-Impl-Task Skill

**File**: `.claude/skills/create-impl-task/skill.md`

**Current Flow**:
- Phase 1: Understand Requirement
- Phase 2: Scope Estimation
- Phase 3: Create Task (3.1 location, 3.2 structure, **3.3 write goal.md**)
- Phase 4: Verify & Commit

**Modified Flow** (when Opus mode enabled):
- Phase 3.3 executed via `switch-to-opus` skill
- Opus thinks deeply about goal.md content before writing
- switch-to-opus completes, returns to Sonnet for Phase 4

**Implementation Details**:
```markdown
**Optional Opus Mode**: This skill can use Opus for goal.md writing to ensure clarity and completeness.

**User invokes**:
- Standard: "Use create-impl-task skill for [requirement_path]"
- With Opus: "Use create-impl-task skill with opus for [requirement_path]"

### 3.3 Write goal.md

**If Opus mode enabled**:
1. Invoke `switch-to-opus` skill with instruction:
   ```
   Task: Write comprehensive goal.md for implementation task.

   Context gathered:
   - Requirement content
   - Scope estimation results
   - User-provided additional details

   Instructions:
   1. Review all gathered context thoroughly
   2. Think deeply about:
      - What is the true objective?
      - What scope makes sense?
      - What context will implementation need?
      - What acceptance criteria are sufficient?
   3. Write goal.md following template
   4. Save to: [path]/goal.md

   Return: Path to created file and summary
   ```
2. switch-to-opus completes and returns control
3. Continue with Phase 4

**If standard mode** (default):
   - Write goal.md directly using template (current behavior)
```

**WHY Comments Needed**:
- WHY: switch-to-opus used for goal.md ensures task objectives are well-reasoned, reducing rework during implementation
- Source: requirements_tasks/.../2026-01-11_impl_update_claude_skills/plans_and_protocols/2026-01-11_01_plan_skill_updates.md#3.3

**Changes Required**:
1. Add frontmatter note about optional Opus mode
2. Add conditional invocation of switch-to-opus for step 3.3
3. Document invocation syntax
4. Preserve backward compatibility (default = write directly)

---

### 3.4 Explore-Requirements Skill

**File**: `.claude/skills/explore-requirements/skill.md`

**Current Flow**:
- Phase 1: Setup & Context Gathering
- Phase 2: Investigation (spawn Explore agent)
- **Phase 3: Synthesis & Requirement Writing**
- Phase 4: Review & Iteration
- Phase 5: Completion

**Modified Flow** (when Opus mode enabled):
- Phase 3 entirely executed via `switch-to-opus` skill
- Opus performs analysis and writes requirement document
- switch-to-opus completes, returns to Sonnet for Phase 4

**Implementation Details**:
```markdown
**Optional Opus Mode**: This skill can use Opus for requirement synthesis and writing to ensure depth and clarity.

**User invokes**:
- Standard: "Use explore-requirements skill for [task path]"
- With Opus: "Use explore-requirements skill with opus for [task path]"

## Phase 3: Synthesis & Requirement Writing

**If Opus mode enabled**:
1. Invoke `switch-to-opus` skill with instruction:
   ```
   Task: Synthesize findings and write requirement document.

   Context available:
   - Investigation results from Phase 2
   - Relevant doc/ guidelines
   - Existing requirements
   - Implementation examples

   Instructions:
   1. Review all gathered findings thoroughly
   2. Analyze (section 3.1 questions):
      - Core purpose?
      - Stakeholders?
      - Rules and exceptions?
      - Examples and anti-patterns?
   3. Write/Update requirement document (section 3.2 structure)
   4. Verify quality checklist (section 3.3)
   5. Save to: [requirement_path]/requirement.md

   Return: Path to file and summary of key findings
   ```
2. switch-to-opus completes and returns control
3. Continue with Phase 4

**If standard mode** (default):
   - Execute Phase 3 steps directly (current behavior)
```

**WHY Comments Needed**:
- WHY: Entire Phase 3 delegated to Opus ensures requirements are thoroughly analyzed with proper WHEN/WHEN-NOT logic
- Source: requirements_tasks/.../2026-01-11_impl_update_claude_skills/plans_and_protocols/2026-01-11_01_plan_skill_updates.md#3.4

**Changes Required**:
1. Add frontmatter note about optional Opus mode
2. Add conditional invocation of switch-to-opus for entire Phase 3
3. Document invocation syntax
4. Preserve current Phase 3 steps as template/checklist for Opus
5. Preserve backward compatibility

**Risk Assessment**: MEDIUM
- Phase 3 is substantial (analysis + writing + quality check)
- Need to ensure switch-to-opus gets proper context
- Quality checklist must still be enforced

---

### 3.5 Test-Implementation Skill

**File**: `.claude/skills/test-implementation/skill.md`

**Current Flow**:
1. Setup (setup-task)
2. Plan (spawn test-engineer - planning phase)
3. Implement (test-engineer continues)
4. Report (test-engineer creates report)
5. Quality (verify-quality)
6. Log (log-protocol)
7. Complete (complete-task)
8. Commit

**Modified Flow** (when Opus mode enabled):
- Step 2 changes: Pass Opus mode flag to test-engineer agent
- test-engineer handles Opus internally
- No other changes needed

**Implementation Details**:
```markdown
**Optional Opus Mode**: This skill can use Opus for test planning to ensure comprehensive coverage.

**User invokes**:
- Standard: "Use test-implementation skill for [task name] in [path]"
- With Opus: "Use test-implementation skill with opus for [task name] in [path]"

2. **Plan**: Spawn test-engineer agent (planning phase):
   - **If Opus mode**: Add instruction "Use Opus for planning phase"
   - **CRITICAL**: Read doc/testing.md first
   - Reads goal.md
   - Creates test plan in plans_and_protocols/ of the current task
   - Uses log-protocol skill (with agent ID)
   - **Optional**: Wait for user plan approval
```

**WHY Comments Needed**:
- WHY: Optional Opus mode delegation to test-engineer enables thorough test planning
- Source: requirements_tasks/.../2026-01-11_impl_update_claude_skills/plans_and_protocols/2026-01-11_01_plan_skill_updates.md#3.5

**Changes Required**:
1. Add frontmatter note about optional Opus mode
2. Add conditional instruction passing to test-engineer
3. Document invocation syntax
4. Preserve backward compatibility

---

### 3.6 Test-Engineer Agent

**File**: `.claude/agents/test-engineer.md`

**Current Flow**:
- Phase 1: Planning (read docs, analyze, create plan, log)
- Phase 2: Implementation (TDD)
- Phase 3: Reporting

**Modified Flow** (when Opus mode enabled):
- Phase 1 steps 1-2: Sonnet
- Phase 1 steps 3-4: Opus (via switch-to-opus)
- Phase 1 step 5: Sonnet
- Phase 2-3: Sonnet (unchanged)

**Implementation Details**:
```markdown
**Optional Opus Mode**: This agent can use Opus for test analysis and planning.

**When spawned with Opus mode enabled**:

**Phase 1 - Planning**:
1. Read doc/testing.md (MANDATORY) — **SONNET**
2. Read goal.md (understand what to test) — **SONNET**
3-4. **Invoke switch-to-opus skill** for analysis and planning:
   ```
   Task: Analyze code and create comprehensive test plan.

   Context available:
   - doc/testing.md guidelines
   - goal.md objectives
   - Code to test

   Instructions:
   1. Analyze code to test thoroughly
   2. Create `plans_and_protocols/[date]_test_plan.md`:
      - Which test files to create/modify
      - Test coverage strategy (unit/widget/integration)
      - Mocking requirements
      - Edge cases to cover

   Return: Path to plan and summary
   ```
5. Use log-protocol skill (save agent ID) — **SONNET**

**When spawned WITHOUT Opus mode** (default):
   - Execute original flow (steps 1-5 in sequence)

**Phase 2 - Implementation** (TDD): [unchanged, always Sonnet]
**Phase 3 - Reporting**: [unchanged, always Sonnet]
```

**WHY Comments Needed**:
- WHY: switch-to-opus for steps 3-4 ensures comprehensive test coverage analysis
- Source: requirements_tasks/.../2026-01-11_impl_update_claude_skills/plans_and_protocols/2026-01-11_01_plan_skill_updates.md#3.6

**Changes Required**:
1. Add frontmatter note about optional Opus mode
2. Add conditional logic for switch-to-opus in Phase 1
3. Preserve backward compatibility

---

### 3.7 Update-Guidelines Skill

**File**: `.claude/skills/update-guidelines/skill.md`

**Proposed Integration Point**: Analysis of protocols → synthesis of guidelines

**Modified Flow** (when Opus mode enabled):
- Sonnet: Read protocols, gather patterns
- Opus: Synthesize insights into guideline updates (via switch-to-opus)
- Sonnet: Run merge script, commit

**Implementation Details**:
```markdown
**Optional Opus Mode**: This skill can use Opus for guideline synthesis to ensure thorough analysis of patterns.

**User invokes**:
- Standard: "Use update-guidelines skill"
- With Opus: "Use update-guidelines skill with opus"

**Workflow**:
1. **Gather Context** (Sonnet):
   - Read protocol files from completed tasks
   - Identify patterns and learnings
   - Read existing doc/ guidelines

2. **Synthesize Guidelines** (Opus if enabled):
   - **If Opus mode**: Invoke switch-to-opus skill with instruction:
     ```
     Task: Analyze patterns and synthesize guideline updates.

     Context available:
     - Protocol files from multiple tasks
     - Existing doc/ guidelines
     - Identified patterns and inefficiencies

     Instructions:
     1. Analyze patterns thoroughly
     2. Identify guideline improvements
     3. Draft guideline updates in source files (doc/[subfolder]/)
     4. Ensure updates are actionable and clear

     Return: Summary of proposed updates
     ```
   - **If standard mode**: Analyze and draft updates directly

3. **Apply Updates** (Sonnet):
   - Write to doc/ source files
   - Run merge script
   - Commit changes
```

**WHY Comments Needed**:
- WHY: switch-to-opus for synthesis ensures guideline updates are well-reasoned from pattern analysis
- Source: requirements_tasks/.../2026-01-11_impl_update_claude_skills/plans_and_protocols/2026-01-11_01_plan_skill_updates.md#3.7

**Changes Required**:
1. Add frontmatter note about optional Opus mode
2. Add conditional invocation of switch-to-opus for synthesis step
3. Document invocation syntax
4. Preserve backward compatibility

**Status**: READY (user approved suggested integration)

---

### 3.8 Verify-Quality Skill

**File**: `.claude/skills/verify-quality/skill.md`

**Proposed Integration Point**: Analysis of violations → recommendation synthesis

**Modified Flow** (when Opus mode enabled):
- Sonnet: Gather changed files, run checks
- Opus: Analyze violations, recommend fixes (via switch-to-opus)
- Sonnet: Generate report

**Implementation Details**:
```markdown
**Optional Opus Mode**: This skill can use Opus for thorough quality analysis and fix recommendations.

**User invokes**:
- Standard: "Use verify-quality skill"
- With Opus: "Use verify-quality skill with opus"

**Workflow**:
1. **Gather & Check** (Sonnet):
   - Identify changed files
   - Run quality checks (layer separation, forbidden imports, WHY comments, etc.)
   - Collect violations

2. **Analyze Violations** (Opus if enabled):
   - **If Opus mode**: Invoke switch-to-opus skill with instruction:
     ```
     Task: Analyze quality violations and recommend fixes.

     Context available:
     - List of changed files
     - Quality violations found
     - doc/ guidelines
     - Code context

     Instructions:
     1. Analyze each violation thoroughly
     2. Determine root cause
     3. Recommend specific fixes
     4. Assess severity and priority
     5. Create quality report

     Return: Path to quality report and summary
     ```
   - **If standard mode**: Generate basic violation report

3. **Report** (Sonnet):
   - Present findings to user
   - Suggest next steps
```

**WHY Comments Needed**:
- WHY: switch-to-opus for violation analysis ensures comprehensive root cause identification and fix recommendations
- Source: requirements_tasks/.../2026-01-11_impl_update_claude_skills/plans_and_protocols/2026-01-11_01_plan_skill_updates.md#3.8

**Changes Required**:
1. Add frontmatter note about optional Opus mode
2. Add conditional invocation of switch-to-opus for analysis step
3. Document invocation syntax
4. Preserve backward compatibility

**Status**: READY (user approved suggested integration)

---

## 4. Implementation Order & Dependencies

### 4.1 Recommended Order

```
Phase A - Foundation (Independent):
1. architecture-advisor agent      [3.1]
2. test-engineer agent             [3.6]

Phase B - Skills Using Agents (Depends on Phase A):
3. complex-implementation skill    [3.2]
4. test-implementation skill       [3.5]

Phase C - Skills Using switch-to-opus Directly (Independent):
5. create-impl-task skill          [3.3]
6. explore-requirements skill      [3.4]
7. update-guidelines skill         [3.7]
8. verify-quality skill            [3.8]
```

**Rationale**:
- Start with agents (foundational components)
- Then update skills that delegate to those agents
- Then update skills that use switch-to-opus directly
- Finally address pending items after clarification

### 4.2 Dependencies

```
complex-implementation → architecture-advisor
test-implementation → test-engineer
create-impl-task → none
explore-requirements → none
update-guidelines → none
verify-quality → none
```

### 4.3 Parallel Work Possible

- Phase A: Both agents can be updated in parallel
- Phase B: Both skills can be updated in parallel (after Phase A)
- Phase C: Both skills can be updated in parallel (no dependency on A or B)

---

## 5. Testing Strategy

### 5.1 Unit-Level Verification

For each modified skill/agent:
1. **Without Opus flag**: Verify default behavior unchanged
2. **With Opus flag**: Verify switch-to-opus invoked correctly
3. **Context preservation**: Verify no information lost during switch
4. **Return handling**: Verify plan/output properly returned

### 5.2 Integration Verification

1. **complex-implementation with opus**:
   - End-to-end: Setup → Plan (Opus) → Implement → Complete
   - Verify architecture-advisor uses Opus correctly
   - Verify plan quality improved with Opus

2. **test-implementation with opus**:
   - End-to-end: Setup → Plan (Opus) → Implement → Report
   - Verify test-engineer uses Opus correctly
   - Verify test plan quality improved

3. **create-impl-task with opus**:
   - End-to-end: Understand → Scope → Write goal.md (Opus) → Commit
   - Verify goal.md quality improved

4. **explore-requirements with opus**:
   - End-to-end: Setup → Investigate → Synthesize (Opus) → Review → Complete
   - Verify requirement quality improved

### 5.3 Regression Testing

**Critical**: Verify all workflows work WITHOUT Opus flag (backward compatibility)

Test matrix:
- [ ] complex-implementation (default mode)
- [ ] test-implementation (default mode)
- [ ] create-impl-task (default mode)
- [ ] explore-requirements (default mode)
- [ ] architecture-advisor (default mode)
- [ ] test-engineer (default mode)

---

## 6. Risk Assessment & Mitigation

### 6.1 High Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Context window overflow | Critical | Medium | Document when NOT to use Opus mode |
| Breaking backward compatibility | Critical | Low | Thorough regression testing |
| Opus invoked when not needed | Cost | Medium | Clear documentation, optional flag |

### 6.2 Medium Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Unclear invocation syntax | Usability | Medium | Standardize "with opus" pattern |
| switch-to-opus fails | Workflow break | Low | Add error handling, fallback |
| User confusion about when to use | Usability | High | Add usage guidelines |

### 6.3 Low Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Inconsistent documentation | Minor | Medium | Review all files for consistency |
| Missing WHY comments | Maintenance | Low | Include in verify-quality checks |

### 6.4 Mitigation Strategies

**Strategy 1: Standardize Invocation Pattern**
- All skills use "with opus" suffix
- Example: "Use [skill-name] skill with opus for [task]"
- Document in each skill's frontmatter

**Strategy 2: Add Usage Guidelines**
Create `doc/opus_mode_usage.md`:
- When to use Opus mode (complex planning, requirements synthesis, test planning)
- When NOT to use (simple tasks, tight context window, cost-sensitive)
- Cost implications (Opus is 5x more expensive)

**Strategy 3: Error Handling**
Each integration point should handle switch-to-opus failures:
```markdown
**If switch-to-opus fails**:
1. Log error to protocol
2. Fall back to default (Sonnet) behavior
3. Warn user about fallback
```

**Strategy 4: Context Window Monitoring**
Document warning signs:
- If gathered context > 50K tokens, consider NOT using Opus mode
- If plan will be > 10K tokens, risk overflow

---

## 7. WHY Comments Requirements

### 7.1 Required WHY Comments

**Location**: Each modified skill/agent file

**Pattern**:
```markdown
/// Why: [Explanation of optional Opus mode pattern]
/// Source: requirements_tasks/.../2026-01-11_impl_update_claude_skills/plans_and_protocols/2026-01-11_01_plan_skill_updates.md#[section]
/// Related: .claude/skills/opus-workflow/skill.md (reference implementation)
```

**Specific locations**:

1. **architecture-advisor.md**:
   - Before Phase 2 (switch-to-opus invocation)
   - WHY: Conditional model switching enables cost optimization while preserving strategic planning quality

2. **test-engineer.md**:
   - Before Phase 1 steps 3-4
   - WHY: switch-to-opus for test analysis ensures comprehensive coverage planning

3. **complex-implementation/skill.md**:
   - Step 2 (architecture-advisor invocation)
   - WHY: Optional Opus delegation to architecture-advisor maintains skill simplicity

4. **test-implementation/skill.md**:
   - Step 2 (test-engineer invocation)
   - WHY: Optional Opus delegation to test-engineer maintains skill simplicity

5. **create-impl-task/skill.md**:
   - Step 3.3 (goal.md writing)
   - WHY: switch-to-opus for goal.md ensures task objectives are well-reasoned

6. **explore-requirements/skill.md**:
   - Phase 3 (synthesis & writing)
   - WHY: Entire Phase 3 delegated to Opus ensures requirement depth and WHEN/WHEN-NOT clarity

### 7.2 Documentation WHY Comments

**New file**: `doc/opus_mode_usage.md` (if created)
- WHY: Centralized guidance prevents confusion and inappropriate Opus usage
- Source: This plan #6.4

---

## 8. Quality Criteria

### 8.1 Acceptance Criteria (from goal.md)

- [ ] All 6 skills updated with Opus-switching capability
- [ ] All 2 agents updated to support switch-to-opus skill
- [ ] Documentation added to each skill/agent about optional Opus usage
- [ ] Default behavior (Sonnet-only) preserved for all workflows
- [ ] switch-to-opus skill properly integrated at specified phases
- [ ] User instructions added for how to invoke Opus mode
- [ ] Backward compatibility verified (existing workflows work unchanged)

### 8.2 Additional Quality Checks

- [ ] All WHY comments added (section 7.1)
- [ ] Consistent invocation pattern ("with opus" suffix)
- [ ] Error handling for switch-to-opus failures
- [ ] Context window warnings documented
- [ ] Regression tests passed (section 5.3)
- [ ] Cost implications documented

### 8.3 Verification Steps

**For each skill/agent**:
1. Read modified file
2. Verify optional flag in frontmatter
3. Verify conditional logic correct
4. Verify WHY comment present
5. Verify backward compatibility preserved
6. Test without flag (default behavior)
7. Test with flag (Opus mode)

---

## 9. Scope Limitations

### 9.1 In Scope

- Modifying 6 skills: complex-implementation, create-impl-task, explore-requirements, test-implementation, update-guidelines (pending), verify-quality (pending)
- Modifying 2 agents: architecture-advisor, test-engineer
- Adding optional Opus mode flag
- Documentation updates
- WHY comments
- Backward compatibility

### 9.2 Out of Scope

- Modifying switch-to-opus skill itself
- Automatic detection of when to use Opus (user must explicitly invoke)
- Changing default behavior (remains Sonnet)
- Modifying other skills/agents not listed
- Creating new skills/agents
- Cost tracking/reporting for Opus usage
- Context window size validation (manual user responsibility)

### 9.3 Deferred (Pending Clarification)

- update-guidelines skill Opus integration (instructions TBD)
- verify-quality skill Opus integration (instructions TBD)

---

## 10. Implementation Checklist

### Phase A - Agents
- [ ] architecture-advisor.md
  - [ ] Add frontmatter note
  - [ ] Add Phase 2 (switch-to-opus)
  - [ ] Update phase numbering
  - [ ] Add WHY comment
  - [ ] Test default mode
  - [ ] Test Opus mode

- [ ] test-engineer.md
  - [ ] Add frontmatter note
  - [ ] Add switch-to-opus for steps 3-4
  - [ ] Add WHY comment
  - [ ] Test default mode
  - [ ] Test Opus mode

### Phase B - Skills Using Agents
- [ ] complex-implementation/skill.md
  - [ ] Add frontmatter note
  - [ ] Add conditional instruction to architecture-advisor
  - [ ] Document invocation syntax
  - [ ] Add WHY comment
  - [ ] Test default mode
  - [ ] Test Opus mode

- [ ] test-implementation/skill.md
  - [ ] Add frontmatter note
  - [ ] Add conditional instruction to test-engineer
  - [ ] Document invocation syntax
  - [ ] Add WHY comment
  - [ ] Test default mode
  - [ ] Test Opus mode

### Phase C - Skills Using switch-to-opus Directly
- [ ] create-impl-task/skill.md
  - [ ] Add frontmatter note
  - [ ] Add switch-to-opus for step 3.3
  - [ ] Document invocation syntax
  - [ ] Add WHY comment
  - [ ] Test default mode
  - [ ] Test Opus mode

- [ ] explore-requirements/skill.md
  - [ ] Add frontmatter note
  - [ ] Add switch-to-opus for Phase 3
  - [ ] Document invocation syntax
  - [ ] Add WHY comment
  - [ ] Test default mode
  - [ ] Test Opus mode

### Phase C (continued) - Additional Skills Using switch-to-opus
- [ ] update-guidelines/skill.md
  - [ ] Add frontmatter note
  - [ ] Add switch-to-opus for synthesis step
  - [ ] Document invocation syntax
  - [ ] Add WHY comment
  - [ ] Test default mode
  - [ ] Test Opus mode

- [ ] verify-quality/skill.md
  - [ ] Add frontmatter note
  - [ ] Add switch-to-opus for violation analysis
  - [ ] Document invocation syntax
  - [ ] Add WHY comment
  - [ ] Test default mode
  - [ ] Test Opus mode

### Final Verification
- [ ] All regression tests pass (section 5.3)
- [ ] All WHY comments present
- [ ] Usage guidelines documented
- [ ] Commit changes with proper message

---

## 11. Recommendations

### 11.1 For User

1. **Clarify update-guidelines and verify-quality**: Specify where Opus should be used in these skills
2. **Create usage guidelines**: Consider adding `doc/opus_mode_usage.md` for when to use Opus mode
3. **Set budget alerts**: Monitor Opus usage costs during rollout
4. **Gradual rollout**: Test each phase independently before moving to next

### 11.2 For Implementation

1. **Start with agents**: They're foundational, test them thoroughly
2. **One skill at a time**: Don't batch-update all skills simultaneously
3. **Test each integration**: Verify Opus mode AND default mode for each
4. **Document learnings**: Update protocol with any discoveries during implementation

### 11.3 For Future

1. **Consider auto-detection**: Could heuristics determine when Opus is beneficial?
2. **Cost tracking**: Could we log Opus invocations for cost analysis?
3. **Context window validation**: Could switch-to-opus check context size before proceeding?
4. **Preset templates**: Could we pre-configure common Opus prompts?

---

## 12. Next Steps

**Immediate**:
1. User reviews this plan
2. User clarifies update-guidelines and verify-quality integration points
3. User approves plan or requests modifications

**After Approval**:
1. Begin Phase A (agents)
2. Test Phase A thoroughly
3. Proceed to Phase B
4. Test Phase B thoroughly
5. Proceed to Phase C
6. Test Phase C thoroughly
7. Address Phase D after clarification
8. Final regression testing
9. Commit all changes

**Estimated Effort**:
- Phase A: 2-3 hours (2 agents)
- Phase B: 1-2 hours (2 skills)
- Phase C: 2-3 hours (2 skills)
- Phase D: 1-2 hours (2 skills, after clarification)
- Testing: 2-3 hours
- **Total**: 8-13 hours

---

## Appendix A: File Locations

**Skills**:
- `.claude/skills/complex-implementation/skill.md`
- `.claude/skills/create-impl-task/skill.md`
- `.claude/skills/explore-requirements/skill.md`
- `.claude/skills/test-implementation/skill.md`
- `.claude/skills/update-guidelines/skill.md`
- `.claude/skills/verify-quality/skill.md`

**Agents**:
- `.claude/agents/architecture-advisor.md`
- `.claude/agents/test-engineer.md`

**Reference**:
- `.claude/skills/opus-workflow/skill.md`
- `.claude/skills/switch-to-opus/skill.md`

**Task**:
- `requirements_tasks/process/AI_rules/workflows/smart_and_cost_efficient/tasks/2026-01-11_impl_update_claude_skills/`

---

## Appendix B: Invocation Pattern Examples

**Standard invocation** (default, Sonnet-only):
```
"Use complex-implementation skill for task_name in task_path"
"Use test-implementation skill for task_name in task_path"
"Use create-impl-task skill for requirement_path"
"Use explore-requirements skill for task_path"
```

**Opus invocation** (optional, Sonnet gather → Opus think):
```
"Use complex-implementation skill with opus for task_name in task_path"
"Use test-implementation skill with opus for task_name in task_path"
"Use create-impl-task skill with opus for requirement_path"
"Use explore-requirements skill with opus for task_path"
```

**Key**: The "with opus" suffix is the trigger for Opus mode.

---

**Plan Status**: APPROVED - ALL INTEGRATION POINTS CLARIFIED
**User Decision**: Follow suggested integration points for all skills
**Next**: Proceed with implementation (Phase A → B → C)
