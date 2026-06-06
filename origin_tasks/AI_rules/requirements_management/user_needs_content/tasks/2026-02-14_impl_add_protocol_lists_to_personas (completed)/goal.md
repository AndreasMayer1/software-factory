---
task_id: TASK-PROC-027-18
type: impl
parent_requirement: REQ-PROC-027
urgency: 4
urgency_reason: U4-IMPL
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-02-15
effort: L
created: 2026-02-14
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Add comprehensive protocol/homework assignment lists to all therapist, client, and self-user personas based on Gemini clinical research"
references:
  - type: modifies
    target: PERSONA-001
    reason: "Add protocol/homework list (VT therapist prescriptions)"
  - type: modifies
    target: PERSONA-002
    reason: "Add protocol/homework list (psychiatrist prescriptions)"
  - type: modifies
    target: PERSONA-003
    reason: "Add protocol/homework list (depth psychology prescriptions)"
  - type: modifies
    target: PERSONA-004
    reason: "Add self-tracking protocol list (depressed client)"
  - type: modifies
    target: PERSONA-005
    reason: "Add self-tracking protocol list (ADHD client)"
  - type: modifies
    target: PERSONA-006
    reason: "Add self-tracking protocol list (Borderline client)"
  - type: modifies
    target: PERSONA-007
    reason: "Add self-tracking protocol list (social phobia client)"
  - type: modifies
    target: PERSONA-008
    reason: "Add self-tracking protocol list (grief/identity client)"
  - type: modifies
    target: PERSONA-009
    reason: "Add self-tracking protocol list (waitlist self-user)"
  - type: modifies
    target: PERSONA-010
    reason: "Add self-tracking protocol list (self-managed ADHD)"
  - type: modifies
    target: PERSONA-011
    reason: "Add self-tracking protocol list (insomnia self-user)"
  - type: modifies
    target: PERSONA-012
    reason: "Add self-tracking protocol list (burnout prevention)"
  - type: modifies
    target: PERSONA-013
    reason: "Add self-tracking protocol list (Long Covid/CFS pacing)"
requirements_version:
  commit: edb2b1e
  file: ../requirements.md
---

# Goal: Add Protocol/Homework Lists to All Personas

## Objective

Enrich all three persona groups — therapists, clients, and self-users — with comprehensive, clinically grounded lists of protocols and homework assignments relevant to each persona's profile. These lists serve as a direct input for feature design: which protocol types the app must support, which tracking modalities are needed, and what the UI must accommodate.

The Gemini research (provided in requirements_tasks\process\AI_rules\requirements_management\user_needs_content\tasks\2026-02-14_impl_add_protocol_lists_to_personas\gemini_suggestions.md) serves as the basis. It may be extended or corrected if there are doubts about clinical validity.

## Background: The Gemini Research

The following structure was provided as research basis:

### Therapist Prescriptions
- **Dr. Sarah (VT)**: Wochenprotokoll/Aktivitätenprotokoll, Gedankenprotokoll (ABC), Angst-Tagebuch/Expositionsprotokoll, Schlaftagebuch, SORKC-Bogen, Skill-Ketten-Protokoll
- **Dr. med. Turan (Psychiatrist)**: Stimmungs- und Antriebskurve (Mood Chart), Medikamenten-/Nebenwirkungsprotokoll, Schlaf-Wach-Rhythmus-Protokoll, Krisenplan/Notfallplan (static doc), Compliance-Checkliste
- **Prof. Dr. Weber (Depth Psychology)**: Traumtagebuch, Resonanz-Protokoll, Beziehungs-Protokoll, Freies Assoziieren/Morning Pages, Symptom-Kontext-Tagebuch

### Client Self-Tracking (separate from therapist homework)
- **Max (Depression)**: Brain Dump Liste, Energie-Tankstelle, Erfolgs-Tagebuch (3 Dinge)
- **Sophie (ADHD)**: Habit Tracker, Impulskauf-Log, Fokus-Zeit-Log
- **Jana (Borderline)**: Trigger-Logbuch, "Safe People" Liste, Schwarzes Buch (private, never shared)
- **Elias (Social Phobia)**: Sicherheits-Checkliste, Beweis-Ordner, Datenschutz-Log
- **Lena (Grief/Identity)**: Briefe an den Verstorbenen, Erinnerungs-Speicher, Identitäts-Notizen

### Self-User Protocols (no therapist)
- **Lisa (Waitlist)**: Symptom-Tagebuch (ICD-10 orientiert), Panik-Protokoll, Wartezeiten-Countdown
- **David (Self-managed ADHD)**: Pomodoro-Log, Dopamin-Menü, Medikamenten-Timer & Bestand, "Wall of Awful" Breaker
- **Hanna (Insomnia)**: Schlaffenster-Protokoll, Grübel-Stuhl-Protokoll, Koffein & Alkohol Tracker
- **Michael (Burnout Prevention)**: Stress vs. Recovery Log (HRV correlation), Arbeitszeit-Qualität, Energie-Level, Physische Symptome
- **Nina (Long Covid/CFS)**: Activity Log (Spoon Theory), Symptom-Verzögerungs-Tracker (PEM), Ruhepuls-Protokoll, Orthostase-Check

### Additional Clusters Not Yet Covered in Personas (potential expansion)
- **Eating Disorders**: Ess-Protokoll mit Kontext (Fairburn CBT-E), Spiegel-Expositionsprotokoll
- **OCD**: ERP-Protokoll (Exposition mit Reaktionsverhinderung)
- **Addiction**: Konsumtagebuch, Craving-Protokoll (Urge Surfing, Marlatt & Gordon)
- **Chronic Pain**: Deutsches Schmerztagebuch (Deutsche Schmerzgesellschaft)
- **Couple/Family Therapy**: Konflikt-Protokoll (Gottman)

## Clinical References
- Beck, A.T. (Cognitive Therapy / Gedankenprotokoll)
- Hautzinger, M. (KVT Depression / Wochenprotokoll)
- Margraf & Schneider (Lehrbuch VT / Angst)
- Bohus, M. (DBT kompakt / Diary Card)
- Linehan, M.M. (DBT Skills Training)
- Riemann, D. / DGSM (Schlaftagebuch)
- Fairburn, C.G. (CBT-E / Essstörungen)
- Marlatt & Gordon (Rückfallprophylaxe)
- DGBS (Life-Charts / Bipolar)
- Deutsche Schmerzgesellschaft (Schmerztagebuch)
- Gottman (Conflict Protocol)
- Kaluza, G. (Stress-Log)
- Porges / Polyvagal (HRV)
- Charité Fatigue Centrum (Pacing / CFS)

## Scope

### In Scope
- Add a `protocols_and_homework` section to each therapist persona (what they would prescribe to clients)
- Add a `self_tracking_protocols` section to each client persona (what they track privately, with and without intention to share with therapist)
- Add a `self_tracking_protocols` section to each self-user persona (what they would want to track without a therapist)
- For clients: distinguish between "assigned by therapist" (homework) and "self-initiated private tracking"
- For clients: note when a protocol is shared vs. kept private from therapist (e.g., Jana's Schwarzes Buch)
- Extend or correct the Gemini research where there are doubts about clinical validity
- Personas already identified: Dr. Sarah, Dr. med. Turan, Prof. Dr. Weber, Max, Sophie, Jana, Elias, Lena, Lisa, David, Hanna, Michael, Nina

### Out of Scope
- Creating new personas for eating disorder, OCD, addiction, pain patients (document as gap/note only)
- Changes to scenarios or user flows
- Implementation of features in the Flutter app
- Updating the SCENARIO_INDEX or creating new flows

## Acceptance Criteria

- [ ] All 3 therapist personas have a `protocols_and_homework` section with full list of assignable protocols
- [ ] All 5 client personas have a `self_tracking_protocols` section distinguishing homework vs. private tracking, and shared vs. private entries
- [ ] All 5 self-user personas have a `self_tracking_protocols` section reflecting their self-management goals
- [ ] Each protocol entry includes: name, brief description, clinical context (e.g., "VT standard, Hautzinger")
- [ ] Any deviations from or additions to the Gemini research are noted with reasoning
- [ ] A short note is added at the end of the task protocol documenting uncovered persona gaps (eating disorders, OCD, etc.) for future consideration

## Implementation Approach

1. **Read all affected persona files** (13 personas) to understand current content and section structure
2. **Map protocols to personas** using the Gemini research as basis
3. **Write protocol sections** following the existing persona.md format conventions
4. **Apply clinical quality check**: cross-reference with known German therapy standards; flag and correct any inaccuracies
5. **Log to protocol.md** with agent ID after completion

## Notes

- Use German terminology where clinically established (e.g., "Expositionsprotokoll" not "Exposure Protocol")
- DBT Diary Card for Jana is the Linehan/Bohus standard — include both the official homework variant AND Jana's private variants
- Dr. med. Turan's Krisenplan is a static document, not a tracking protocol — mark it distinctly
- Nina's pacing protocols are based on ME/CFS guidelines (Charité), not general fatigue
- The `modify-user-needs` skill can be used for the actual implementation
