---
task_id: TASK-PROC-010-09
type: explore
parent_requirement: REQ-PROC-010
urgency: 3
urgency_reason: U3-PLAN (Before writing more scenarios, determine efficient approach)
impact: 4
impact_reason: I4-PROD (Reduces scenario writing effort by ~80%)
status: completed
effort: M
created: 2026-02-01
completed: 2026-02-02
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections:
    - SEC-04  # Scenario Definition
    - SEC-09  # Writing Guidelines
scope_description: "Explore efficient scenario creation strategies - role-level vs per-persona scenarios"
requirements_version:
  commit: 08f8e76
  file: ../requirements.md
---

# Goal: Explore Efficient Scenario Creation Strategy

## Objective

Determine the most efficient way to create scenarios for personas, given that many scenarios are nearly identical across personas with the same role.

## Problem Statement

The current structure creates scenarios **per persona**. However, many scenarios are nearly identical across personas with the same role:

**Current situation:**
- **Therapists** (3 personas: Dr. Sarah, Prof. Dr. Weber, Dr. med. Turan)
- **Clients** (8 personas: Max, Jana, Elias, Sophie, David, Lisa, Hanna, Michael) < actually wrong, some of them are self users

**The duplication problem:**
- "Prepare protocol for client" - same core workflow for all therapists
- "Review protocol with client" - same core workflow for all therapists
- "Complete protocol entry" - same core action for all clients
- "Transfer protocol to therapist" - same core action for all clients

**Without optimization:** 3×5 + 8×5 = **55 scenarios** to write
**With role-level approach:** 5 + 5 = **10 core scenarios** + variations

Writing these scenarios 8+ times with minor variations is:
1. **Inefficient** - significant duplication of effort
2. **Maintenance burden** - changes must be made in multiple places
3. **Inconsistency risk** - scenarios may drift apart over time

## Exploration Questions

Those are just suggestions by sonnet. When you're in opus mode I'm sure you can extend.

### Option A: Role-Level Scenarios with Persona Variations
Create scenarios at the **role level** (e.g., `roles/therapist/scenarios/prepare_protocol/`) with:
- One base scenario describing the universal workflow
- Variation sections for each archetype (e.g., "VT Professional variation", "Depth Psychologist variation")
- Personas reference the role-level scenario

**Questions to explore:**
- How to structure the folder hierarchy?
- How to handle persona-specific barriers/emotional context?
- How to link back to individual personas?

### Option B: Scenario Templates with Persona Instantiation
Create scenario **templates** that get "instantiated" per persona:
- Template defines structure, flow, universal elements
- Each persona has a thin "instance" file with persona-specific details
- Generation could be manual or scripted

**Questions to explore:**
- How much is actually universal vs. persona-specific?
- Would this feel too abstract/templated?
- How to maintain the narrative quality of scenarios?

### Option C: Hybrid Approach
- **Universal scenarios** (same for all within role): Create once at role level
- **Persona-specific scenarios** (unique to archetype): Keep at persona level
- Clear criteria for when to use which

**Questions to explore:**
- What criteria determine "universal" vs. "persona-specific"?
- How to cross-reference between levels?

### Option D: Scenario Inheritance
Scenarios could "inherit" from a base scenario:
- Base scenario defines common structure
- Persona scenario overrides/extends specific sections
- Similar to class inheritance in OOP

**Questions to explore:**
- Is this too complex for the use case?
- How would the file structure work?

## Scope

### In Scope
- Analyze current scenario structure and identify duplication patterns
- Evaluate all four options (A, B, C, D) with pros/cons and come up with more options if needed
- Provide quantified effort comparison
- Recommend preferred approach with example structure
- Define criteria for scenario placement decisions

### Out of Scope
- Actually implementing the new structure
- Migrating existing scenarios
- Creating new scenarios

## Notes

User's initial observation: "A lot of those scenarios will be very similar for all personas with the same role. Maybe it's best not to write the scenarios for each persona individually, but always add a scenario for all personas with the same role?"
