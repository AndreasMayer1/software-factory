# UX Consistency Review: FLOW-002 vs FLOW-003

**Date**: 2026-03-23
**Reviewer**: Opus (deep investigation specialist)
**Scope**: Cross-flow UX consistency between FLOW-002 "Instruct Client on Protocol" (therapist-to-client) and FLOW-003 "Session Start & Data Transfer" (client-to-therapist)

---

## Consistency Score: 6/10

The two flows share the same transfer infrastructure (animated QR, file transfer, pairing) and are carefully cross-referenced for pairing and app-installation exceptions. However, they were written at different maturity levels (FLOW-002 approved after three iterations; FLOW-003 still in review after three iterations) and diverge in several areas that would create a disjointed user experience if implemented as-is. The most significant inconsistencies involve transfer completion confirmation, navigation entry points, remote session defaults, progress display semantics, encoding specification (fountain code), and troubleshooting behavior. None are architecturally irreconcilable, but they require deliberate alignment before implementation begins.

---

## Shared Mechanisms Overview

| Mechanism | FLOW-002 Approach | FLOW-003 Approach | Consistent? |
|-----------|-------------------|-------------------|-------------|
| **Animated QR transfer** | Therapist's device displays QR; client's phone scans (Step 5) | Client's phone displays QR; therapist's webcam scans (Step 4-7) | Partially -- direction reverses as expected, but encoding spec differs (see Inconsistency #3) |
| **File transfer** | Encrypted file, recommended default for video calls (Exc 1.3) | Encrypted file with dedicated extension + header block, always-visible alternative (Step 4, Exc 4.3) | Partially -- FLOW-003 specifies header block and file association; FLOW-002 does not |
| **Pairing** | Defined here: visual credential on therapist screen or BIP-39 passphrase (Step 5, Exc 1.3) | References FLOW-002 definition (Exc 2.1A) | Consistent |
| **Remote session (video call)** | Animated QR may work for small plans; file transfer recommended default (Exc 1.3) | QR via screen capture is primary; file transfer is fallback (Exc 4.4) | Inconsistent -- contradictory default recommendations (see Inconsistency #4) |
| **Remote session (phone call)** | BIP-39 passphrase for pairing; file-only for data (Exc 1.3) | Not addressed | Gap in FLOW-003 |
| **Progress display (sender side)** | Therapist sends: estimated duration only, no real-time progress (Step 5) | Client sends: accurate frame progress (frames sent/total) (Step 7) | Inconsistent -- senders get different information (see Inconsistency #2) |
| **Progress display (receiver side)** | Client receives: accurate progress (percentage of chunks received) (Step 6) | Therapist receives: accurate frame progress (frames received/total) (Step 7) | Consistent -- both receivers get accurate progress |
| **Transfer completion confirmation** | Therapist closes screen when client verbally confirms (Step 8) | Client taps explicit "Transfer Successful" / "Transfer Failed" button (Step 8) | Inconsistent -- different confirmation models for the same unidirectionality problem (see Inconsistency #1) |
| **App not installed** | Detailed (Exc 1.2): instruction still happens, defer transfer, app store reference, security constraint (no photographing keys) | References FLOW-002 Exc 1.2 for client case (Exc 1.1B); adds therapist-not-installed case (Exc 1.1A) | Consistent via cross-reference |
| **Client switching therapist** | Defined here (Exc 1.1A): multiple pairings supported, N active connections | References FLOW-002 Exc 1.1A (Exc 2.1C) | Consistent via cross-reference |
| **Transfer interrupted** | Therapist can restart from Step 5; protocol persists on therapist device (Exc 1.6) | Fountain code means no partial save; client confirms failure at Step 8; data remains available (Exc 4.2) | Partially -- FLOW-002 lacks fountain code constraint discussion (see Inconsistency #3) |
| **Navigation entry** | No dedicated nav entry; therapist accesses via "protocol delivery interface" (Step 1) | Dedicated nav bar/rail entries for BOTH client (Step 1) and therapist (Step 5) | Inconsistent -- see Navigation Model Assessment |
| **Troubleshooting hints during transfer** | Not specified | 15-second timer, split by device, careful placement constraints (Exc 4.1A/B) | Gap in FLOW-002 |
| **Working distance adjustment** | Not mentioned | Client-side slider with discrete steps to reduce QR density (Step 6) | Gap in FLOW-002 |
| **Encrypted header block** | Not mentioned | Defined in detail: automatic client identification, repeated in QR sequence (Domain Concepts) | Gap in FLOW-002 |
| **Fountain code encoding** | Not mentioned ("data chunks" only) | Central constraint: no partial saves, complete set required for decryption (Step 7) | Inconsistency/gap in FLOW-002 |
| **Version mismatch handling** | Not addressed | Detailed: auto-upgrade for old client format; update prompt for old therapist format (Exc 6.1) | Gap in FLOW-002 |
| **Storage full** | Not addressed | Therapist side only; guidance offered (Exc 5.1) | Gap in FLOW-002 |

---

## Consistent -- These Work Well Together

### 1. Pairing is defined once and referenced correctly
FLOW-002 defines pairing (Step 5: visual credential or BIP-39 passphrase). FLOW-003 consistently references this definition (Exception 2.1A) rather than re-specifying it. The three sub-cases in FLOW-003 Exception 2.1 (first-time pairing, decryption failure, client switching therapist) all properly cross-reference the appropriate FLOW-002 exceptions. This is exactly how shared mechanisms should be handled.

### 2. Receiver always gets accurate progress
In both flows, the receiving device shows accurate progress (FLOW-002 Step 6: "percentage of data chunks received"; FLOW-003 Step 7: "frames received / total"). This is consistent and logical -- the receiver knows what it has received.

### 3. App installation exception handling
FLOW-003 Exception 1.1B explicitly references FLOW-002 Exception 1.2 ("Same recovery path... do not duplicate the logic"). FLOW-003 adds the inverse case (therapist has no app) as Exception 1.1A. This is clean: no duplication, clear cross-reference, and the new case is handled.

### 4. Non-shameful tone in error recovery
Both flows consistently avoid blaming or shaming users when things go wrong. FLOW-002 Exception 9.1 ("Gaps are data, not failure"), FLOW-003 Exception 2.2 ("non-shameful... must not frame this as an error"), and FLOW-003 Step 8 failure path all use the same empathetic framing. The tone is consistent across both flows.

### 5. Plan template architecture cross-referencing
FLOW-002 defines the full architecture (system templates, master templates, client copies). FLOW-003 introduces the "transfer copy" concept and references the FLOW-002 definitions. The plan modification note in FLOW-003 (Step 8) and Open Question 7 correctly identify the bidirectional modification challenge as an open question rather than silently contradicting FLOW-002's unidirectional model.

### 6. Unidirectional transfer acknowledgment
Both flows correctly identify that the QR transfer is optically unidirectional and that the sending side cannot know the receiving side's state. FLOW-002 Step 5: "the therapist's app cannot know the client's reception state." FLOW-003 Step 8: "The client app cannot detect autonomously whether the therapist received all data." Both flows build their confirmation mechanisms around this constraint, even though they reach different solutions (see Inconsistency #1).

### 7. File transfer as universal fallback
Both flows treat file transfer as the fallback when QR is impractical. FLOW-002 Exc 1.3 recommends it for video calls; FLOW-003 Step 4 offers "Switch to file transfer" and suggests it for transfers exceeding 2 minutes. The concept is consistent even where the specifics diverge.

### 8. Privacy-first data handling
Both flows enforce privacy structurally. FLOW-002 separates client copies from master templates; FLOW-003 structurally excludes private diary entries from transfer scope. The principle is consistent: privacy is architectural, not behavioral.

---

## Inconsistencies Found

### Inconsistency #1 (High): Transfer Completion Confirmation Model

**What differs**: Both flows face the identical problem -- the QR transfer is unidirectional, so the sending device cannot confirm whether the receiving device got the data. But they solve it differently:

- **FLOW-002** (therapist sends): The therapist simply closes the transfer screen after the client verbally confirms receipt (Step 8: "Verifies verbally with the client: 'Did you get it?'"). There is no explicit in-app confirmation mechanism on the sender side. The therapist trusts the verbal confirmation and dismisses the screen.

- **FLOW-003** (client sends): The client must tap an explicit "Transfer Successful" or "Transfer Failed" button when closing the QR Transfer Screen (Step 8). This is a formal in-app confirmation that controls whether entries are marked as "shared."

**Why this matters**: A therapist who has used both flows will experience two different confirmation patterns for the same underlying technical constraint. In FLOW-002, the therapist (sender) gets no explicit confirmation UI -- they just close the screen after a verbal check. In FLOW-003, the client (sender) is required to make a formal in-app declaration. This asymmetry is especially jarring because the therapist is present in both flows and will notice the difference.

**Which flow handles it better**: FLOW-003. The explicit confirmation is superior because it creates a reliable record. FLOW-002's verbal-only approach has no audit trail -- if the transfer failed silently, neither device has a record of what happened. FLOW-003's "shared marker" mechanism (set only on explicit confirmation) is a stronger design.

**Recommended alignment**: FLOW-002 should adopt an explicit confirmation model on the therapist side. After the therapist initiates the transfer and the client verbally confirms receipt, the therapist should confirm in the app ("Transfer Successful" / "Transfer Failed" or equivalent). This sets a "delivered" marker on the client copy in the therapist's client profile. The verbal check remains (the therapist still asks the client), but the app records the outcome.

---

### Inconsistency #2 (Medium): Sender-Side Progress Information

**What differs**:
- **FLOW-002** (therapist sends): Therapist's side shows an **estimated transfer duration** only -- no real-time progress (Step 5: "estimated transfer duration... but no real-time progress").
- **FLOW-003** (client sends): Client's side shows **accurate frame-by-frame progress** (Step 7: "Client sees frames sent / total").

**Why this matters**: In FLOW-002, the therapist is told "approximately 30 seconds" and then waits with no feedback until the client says "got it." In FLOW-003, the client sees a live counter ticking up. This is a different experience for the sender in each direction.

**Technical justification**: FLOW-002 was written before the fountain code / animated QR mechanism was fully specified. In an animated QR system, the sender always knows how many frames have been displayed (the sender controls the animation). FLOW-002's claim that the therapist "cannot know the client's reception state" is correct about the *receiver's* state -- but the *sender's own transmission progress* (frames displayed) is always knowable. FLOW-002 conflates "cannot know the receiver's state" with "cannot show any progress," which is inaccurate for the sending device.

**Which flow handles it better**: FLOW-003. The sender should always see frames-sent progress because the sender controls the QR animation. This costs nothing technically and gives the sender useful feedback.

**Recommended alignment**: Update FLOW-002 Step 5 to show frames-sent progress on the therapist's side (how many QR frames have been displayed / total). Retain the caveat that this does NOT indicate reception -- the therapist still needs the client's verbal confirmation. The estimated duration can remain as additional context. Wording: "Therapist's side displays transfer progress (frames displayed / total) and estimated remaining duration. Note: this shows transmission progress, not reception confirmation -- the therapist cannot know whether the client's device has successfully received the data."

---

### Inconsistency #3 (High): Fountain Code / Encoding Specification

**What differs**:
- **FLOW-002**: Mentions "data chunks" (Step 6: "percentage of data chunks received") but does not mention fountain codes, does not discuss the no-partial-save constraint, and does not specify the encoding mechanism.
- **FLOW-003**: Specifies fountain code with encryption as the encoding mechanism (Step 7), explicitly states "data can only be decrypted once the complete set of frames has been received," and builds exception handling around this constraint (Exception 4.2).

**Why this matters**: If both flows use the same transfer infrastructure (which they must -- building two separate transfer systems would be unreasonable), then the fountain code constraint applies to both directions. FLOW-002's silence on this means:
1. Exception 1.6 (transfer interrupted) does not mention that partial transfers yield no usable data on the client device.
2. There is no discussion of what happens if the client scans most but not all QR frames.
3. The "data chunks" language in Step 6 may mislead implementers into thinking progressive/partial reception is possible.

**Which flow handles it better**: FLOW-003. The fountain code specification is detailed, the constraint is clearly stated, and the exception handling accounts for it.

**Recommended alignment**: FLOW-002 should reference the fountain code mechanism (or at minimum, state the same no-partial-save constraint). Exception 1.6 should note that if the transfer is interrupted, the client device has no usable data -- the transfer must restart from the beginning. Step 6 should replace "percentage of data chunks received" with "frames received / total" for consistency with FLOW-003's terminology.

---

### Inconsistency #4 (Medium): Remote Session Default Transfer Method

**What differs**:
- **FLOW-002** Exception 1.3: "**Recommended default for video calls**: File transfer (more reliable, no speed/quality tuning needed)."
- **FLOW-003** Exception 4.4: QR via screen capture is the **primary approach** for remote sessions. File transfer is the **fallback**.

**Why this matters**: A therapist in a video call will get contradictory guidance depending on which transfer direction they are performing. When sending a plan (FLOW-002), the app defaults to file transfer. When receiving data (FLOW-003), the app defaults to QR via screen capture. The therapist must learn two different "normal" behaviors for remote sessions.

**Analysis**: The contradiction may be partially justified by data volume. FLOW-002 notes that most plans are small enough for a static QR (not animated), making animated QR over video unnecessary. FLOW-003 deals with accumulated time-series data that is typically larger, making animated QR the faster option when it works (avoiding file-sharing logistics). However, if animated QR over video is reliable enough to be the primary in FLOW-003, it should also be reliable enough for FLOW-002's small data case -- where it would actually work *better* because the data is smaller.

**Which flow should align**: Both flows should present the same default for video calls. Given that FLOW-003 already promotes QR-via-screen-capture as primary and FLOW-002 acknowledges that most plans fit in a static QR, the consistent approach would be: (a) for small data (most FLOW-002 transfers): static QR shown on-screen in the video call works reliably -- make this the primary; (b) for larger data (most FLOW-003 transfers): animated QR via screen capture as primary, file transfer as fallback; (c) file transfer is always available as a manual alternative in both directions.

**Recommended alignment**: Update FLOW-002 Exception 1.3 to match the hierarchy: QR (static for pairing + small plans, animated for larger plans) as primary; file transfer as fallback. Remove "Recommended default for video calls: File transfer" and replace with the same graduated approach FLOW-003 uses. The design note in FLOW-002 Exc 1.3 already acknowledges that "most plans are small enough that a static QR code suffices" -- lean into this rather than defaulting to file transfer.

---

### Inconsistency #5 (Low-Medium): Encrypted Header Block

**What differs**:
- **FLOW-002**: Does not mention the encrypted header block concept at all. The receiving side (client) does not need automatic identity resolution -- the client knows which therapist they are receiving from (established during pairing in the same session).
- **FLOW-003**: Defines the encrypted header block in detail (Domain Concepts section). The therapist's app uses it to automatically identify the incoming client without manual selection (Step 6).

**Why this matters**: The encrypted header block is a transfer protocol feature, not a flow-specific feature. If it exists in the animated QR encoding for client-to-therapist transfers, it should also exist in therapist-to-client transfers -- even if the receiving client does not *need* it for identity resolution (the client already knows who they are paired with). Including the header block in both directions would:
1. Enable future use cases (e.g., client receiving from multiple therapists in the same session).
2. Keep the transfer encoding symmetric, simplifying implementation (one encoder/decoder for both directions).
3. Allow the client's app to verify that the incoming data matches the expected therapist pairing.

**Recommended alignment**: Add a brief mention in FLOW-002 that the transfer data includes an encrypted header block for identity verification (matching FLOW-003's mechanism). This does not change the user experience but ensures the technical protocol is symmetric.

---

### Inconsistency #6 (Low): Terminology -- "Chunks" vs "Frames"

**What differs**:
- **FLOW-002** Step 6: "percentage of data chunks received"
- **FLOW-003** Steps 6-7: "frames sent / total," "frames received / total," "QR frames"

**Why this matters**: The same transfer mechanism should use consistent terminology. "Chunks" (FLOW-002) and "frames" (FLOW-003) likely refer to the same unit (one QR code in the animated sequence). Using different terms creates confusion in implementation.

**Recommended alignment**: Adopt "frames" consistently in both flows. Update FLOW-002 Step 6 to use "frames received / total" instead of "percentage of data chunks received."

---

## Gaps: FLOW-003 Missing (relative to FLOW-002)

### Gap 3.1: Phone-Only Remote Session (No Video)

FLOW-002 Exception 1.3 covers phone-call-only remote sessions in detail: BIP-39 verbal passphrase for pairing, file-only transfer. FLOW-003 does not address this case. Exception 4.4 only covers video call sessions.

**Impact**: If a client needs to transfer data during a phone-only session (no video), there is no documented path. The client would need to use file transfer independently (email the encrypted file), but the flow does not specify how the client obtains the therapist's file import details without a visual channel.

**Recommendation**: Add a sub-case to FLOW-003 Exception 4.4 (or a new exception) covering phone-only remote sessions. Since pairing already exists (FLOW-003 assumes it), the phone-only case reduces to: client generates encrypted file, sends via email/messaging, therapist imports via file picker. This is simpler than FLOW-002's phone case because pairing is already established.

### Gap 3.2: Paper Fallback / Parallel Delivery

FLOW-002 Exception 1.8 documents paper + digital parallel delivery -- a common pattern for first-time protocol users. FLOW-003 has no equivalent. In the FLOW-003 direction, the "paper fallback" is