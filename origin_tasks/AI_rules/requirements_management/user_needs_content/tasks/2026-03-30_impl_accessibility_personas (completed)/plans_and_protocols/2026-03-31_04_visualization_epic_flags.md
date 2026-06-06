# Visualization Epic Planning Flags
**Date**: 2026-03-31
**From**: TASK-PROC-027-36 Pass 1 (accessibility personas)
**For**: Future visualization / collaborative analysis flow and epic authors

---

## Flag 1: Non-color redundancy in Client Data View

The therapist's Client Data View (FLOW-003 Step 6, FLOW-004 Step 9) shows data visualizations
(charts, trend lines, timeline views). No persona currently drives non-color redundancy requirements
on this screen (the low-vision persona Rahel is a self_user and does not participate in FLOW-003/004).

The app_provider persona now states this as universal policy:
> "Data visualizations must use non-color redundancy — color must not be the sole encoding
> property for any data dimension."

**Action for visualization epic author**: Treat this as a design constraint when specifying
chart types, data series encoding, and legend design. Non-color redundancy = second distinguishing
property alongside color (shape, pattern, text label, dashed vs. solid line).

---

## Flag 2: Felix's in-room presence during FLOW-003 Step 6

Felix (PERSONA-018, photosensitive epilepsy) is a client. In FLOW-003 Step 6, both the client
and therapist observe the entrance animation as the Client Data View opens on the therapist's
laptop. Felix is in the room and can see the therapist's screen.

This means the WCAG 2.3.1 flash rate constraint (≤3Hz) applies to the therapist's visualization
entrance animation from Felix's perspective, not only from the therapist's perspective.

**Current state**: The entrance animation (VTR-005) is specified as ~1–2s smooth fade — this
does not produce repeated flashes and does not violate WCAG 2.3.1. No action required for the
current specification.

**Action for visualization epic author**: If the visualization design introduces any animated
chart elements (pulsing safety alerts, animated trend transitions, auto-refreshing data), these
must comply with WCAG 2.3.1 ≤3Hz because Felix (and potentially other photosensitive clients)
will be in the room observing the therapist's screen at the start of the session.
