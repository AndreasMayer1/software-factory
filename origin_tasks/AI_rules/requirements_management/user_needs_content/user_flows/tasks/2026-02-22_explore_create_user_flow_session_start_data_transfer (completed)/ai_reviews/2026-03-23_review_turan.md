# FLOW-003 Fit Review: Dr. med. Turan (PERSONA-012) — SCEN-012-02

## Fit Score: 6/10

## What Works Well

1. Eliminates the paper failure modes that blocked Dr. Turan in the scenario
2. Correct visualization type specified for Dr. Turan's protocol type (timeline/trend view for structured mood/medication log)
3. Accurate self-aware "partial" scope documentation — the flow does not overclaim coverage
4. MVZ open-door privacy risk named explicitly in Environmental Considerations
5. Value Trade-off 2 (clinical safety vs. client control) correctly framed — acknowledges the tension without resolving it incorrectly
6. Cross-therapist data design appropriate for clinic context (multi-therapist patients common in psychiatry)
7. Compliance improvement via phone-based protocols addressed as a baseline improvement over paper

## Missing Elements

1. **The 90-second safety scan is entirely absent** — the scenario's defining moment (Dr. Turan's first action after receiving data is a rapid safety assessment for agitation, mood crash, side effect spikes) has no representation in the flow. The visualization spec defers to "implementing epics" without flagging that psychiatry requires safety signals to be immediately prominent, not buried.
2. **KIS integration and exportable summary unaddressed** — SCEN-012-02 references the need to eventually import data into the clinic information system (KIS). This is out of scope for FLOW-003 but should be flagged as a gap.
3. **Threshold alerts and safety signal detection absent** — three planned flows away, but SCEN-012-02's success criteria include detecting safety-critical signals. No path from FLOW-003 to that detection exists yet.
4. **Cross-cycle comparison not addressed in visualization spec** — Dr. Turan needs to compare current cycle data to previous cycles for dose adjustment decisions. The visualization spec is silent on temporal cross-referencing.
5. **Protocol adaptation between cycles has no home** — when Dr. Turan adjusts a medication protocol based on what she sees, there is no flow for that modification. Should be flagged.
6. **Verbal report integration undocumented** — in Dr. Turan's clinic context, the transferred data supplements (not replaces) a verbal report. The flow treats the visualization as the session entry point without acknowledging that verbal context arrives simultaneously.
7. **Clinic desktop without webcam underexplored** — Exception 4.3 (file transfer) is the fallback, but a clinic desktop without webcam is likely the norm in institutional settings. This should be more prominently surfaced, not treated as an exception.

## Contradictions

1. **"One flow for all archetypes" understates urgency of psychiatric visualization spec** — the flow correctly defers visualization details to implementing epics, but this deferral means the psychiatry-specific 90-second safety scan requirement (which is safety-critical, not a preference) gets buried in Open Questions rather than being surfaced as a hard requirement.
2. **First-session orientation dialog contradicts PERSONA-012's anti-traits** — the Adaptive UI rule specifying a "brief orientation" after the first transfer directly conflicts with Dr. Turan's documented anti-trait of not reading multi-part announcements in a 15-minute appointment context. This dialog could create clinical liability by adding friction at a safety-critical moment.
3. **Step 8 client confirmation adds friction in time-critical appointments** — Dr. Turan's 15-minute appointment structure means every extra step the client must perform (confirming transfer success/failure) consumes appointment time. The flow does not acknowledge this time pressure.

## Observations on Partial Coverage

"Partial" is accurate but understates the gap. FLOW-003 covers only the entry point (transfer + visualization open). All seven of SCEN-012-02's success criteria (safety scan, dose review, threshold detection, cross-cycle comparison, KIS-ready summary, verbal integration, protocol adaptation) fall entirely outside FLOW-003's scope. The flow is a necessary prerequisite but satisfies none of the scenario's actual clinical goals on its own.

## Recommendations

1. **Create the psychiatry analysis flow as next priority** — SCEN-012-02 cannot be marked "addressed" until a dedicated analysis flow exists for Dr. Turan's safety-first clinical model.
2. **Add Turan-specific note to Step 9** flagging that the visualization must surface safety signals prominently for medication monitoring protocols — do not leave this entirely to implementing epics.
3. **Modify first-session orientation to be non-blocking for clinical contexts** — make it dismissible with a single tap or auto-dismiss after 3 seconds, not a read-and-confirm dialog.
4. **Document the webcam-less clinic desktop more prominently** — move file transfer closer to primary status for institutional/desktop contexts, not purely as a fallback.
5. **Flag KIS export as a requirements gap** in the Gaps section — it's downstream of FLOW-003 but the flow should note it exists.
6. **Add verbal report integration as an open question** — the relationship between transferred data and simultaneous verbal report is a design question that affects visualization priorities.
7. **Reconsider coverage language** — "partial" correctly signals incompleteness but "enabling" might more accurately communicate that FLOW-003 is a prerequisite, not a partial solution.
