This is the result of a brainstorming with Gemini. Caution: Not all scenarios are created yet, so it is based on the personas and already existing scenarios but it might not have the quality we're aiming for!



---

# User Flow Master Index (Consolidated)

## Phase A: Creation, Setup & Access (Getting Started)

**1. FLOW-021: Installation & Distribution** *NEW*
*   **What:** How users get the app onto their device.
*   **Channels:**
    *   **Android (Clients/Self-Users):** Google Play Store.
    *   **Desktop (Therapists):** Direct Download (Website/GitHub) -> Manual Install. *Constraint: Windows Store is excluded due to costs.*
*   **Challenges:** Handling "Unverified Developer" warnings on Windows/Mac (Trust); Sideloading updates without store automation.
*   **Personas:** All.

**2. FLOW-012: The Gentle Start (Onboarding)**
*   **What:** The very first app launch after installation.
*   **Goal:** Setup without overwhelm ("White Sheet Syndrome"). No account creation required. Immediate value.
*   **Personas:** Max, David, Lisa.

**3. FLOW-015: Template Discovery (Self-User Setup)**
*   **What:** Selecting a starter protocol without a therapist.
*   **Goal:** Lisa finds a "Depression Starter Kit"; David finds "Dopamin Tracker".
*   **Personas:** Lisa, David, Michael, Nina.

**4. FLOW-006: The Protocol Builder (Universal Editor)**
*   **What:** Creating and editing master templates.
*   **Goal:** Dr. Sarah builds specific "Anxiety Protocols"; Elias builds a private "Black Book".
*   **Personas:** Therapists, Advanced Self-Users.

**5. FLOW-002: Instruct Client (Therapist Assignment)** *Exists*
*   **What:** Assigning a plan to a client via QR code during a session.
*   **Personas:** All Therapist-Client pairs.

**6. FLOW-007: Plan Adjustment & Locking**
*   **What:** Modifying an active plan.
*   **Constraint:** Therapist updates require a physical QR rescan (security). Client updates to own plans are instant. "Locking" mechanism for core clinical data.
*   **Personas:** Sophie (tinkering), Dr. Sarah (iterating).

---

## Phase B: Capture (Daily Routine)

**7. FLOW-003: Universal Routine Entry** *PRIORITY*
*   **Includes:**
    *   **Night Mode:** (Formerly FLOW-001) OLED-black interface, whisper-to-text.
    *   **Access:** Widgets (Homescreen/Lockscreen) for Sophie's object permanence; Notifications.
*   **What:** The core daily interaction. Extremely flexible (Scales, Text, Audio, Boolean). Supports multiple parallel plans.
*   **Goal:** Low friction for Max (1 click), high fidelity for Jana (volatility tracking).
*   **Personas:** All.

**8. FLOW-020: External Data Import (Wearables)** *NEW*
*   **What:** Integrating objective data (Garmin Body Battery, Apple Health HRV).
*   **Stages:**
    *   **Setup:** Linking local health APIs (HealthKit/Health Connect) without cloud servers.
    *   **Integration:** How external data appears alongside manual entries in FLOW-003.
    *   **Analysis:** Correlating "Subjective Mood" with "Objective HRV".
*   **Personas:** Nina (Energy Envelope), Michael (Bio-Optimizer).

**9. FLOW-010: Privacy & Camouflage**
*   **What:** Protection in public spaces.
*   **Features:** "Camouflage Mode" (looks like a news app/calculator), "Panic Flip" (close app instantly), "Blur" in app switcher.
*   **Personas:** Elias (Paranoia), Jana (Roommates).

---

## Phase C: Transfer & Exchange (The Bridge)

**10. FLOW-004: Data Handover (Client Sends)** *PRIORITY*
*   **What:** The transmission moment (Waiting room/Session start).
*   **Constraint:** Selective transfer (Therapy data ONLY; Private diaries stay private). Offline/QR-Code "Data Beam".
*   **Personas:** All Clients with Therapists.

**11. FLOW-014: Therapist Reception & Storage** *Updated*
*   **What:** Dr. Turan/Dr. Sarah receives data on their device.
*   **Action:** Data is **permanently imported** into a local, encrypted "Patient Silo" on the therapist's device. (Correction: Not temporary).
*   **Personas:** All Therapists.

**12. FLOW-016: The Paper Bridge (PDF Report Export)** *PRIORITY*
*   **What:** Generating neutral, medical-standard PDF reports locally.
*   **Use Case:** Lisa needs to show data to a GP; Dr. Turan needs to import a summary into the clinic system (KIS).
*   **Personas:** Lisa, Turan, Sarah.

---

## Phase D: Analysis & Reflection (Making Sense)

**13. FLOW-008: Safe Self-Review (Client Prep)**
*   **What:** Client reviews their own week before therapy.
*   **Features:** Pattern recognition ("Sleep vs. Mood"), Text search ("Show all dreams with 'Corridor'").
*   **Goal:** "Trauma-Buffer" (softened display of crisis entries), Shame-reduction (neutral display of missing days).
*   **Personas:** Jana, Max, Sophie.

**14. FLOW-009: Motif Finder (In-Session Analysis)**
*   **What:** Collaborative deep dive during the session.
*   **Features:** Pattern recognition ("Sleep vs. Mood"), Text search ("Show all dreams with 'Corridor'").
*   **Personas:** Prof. Weber, Dr. Sarah, Lena.

**15. FLOW-022: Therapist Solo Analysis** *NEW*
*   **What:** Therapist works with patient data *alone* (after session or during prep).
*   **Use Cases:** Writing insurance reports (Gutachten), preparing for the next session, analyzing long-term trends without the patient present.
*   **Constraint:** Accessing the secure local storage on the practice PC/Tablet or exports/prints.
*   **Personas:** Dr. Sarah, Dr. Turan, Prof. Weber.

---

## Phase E: Safety & Lifecycle (The Frame)

**16. FLOW-005: Crisis Intervention** *PRIORITY*
*   **What:** The Safety Airbag.
*   **Triggers:** Mood < X, Keywords ("Suicide"), Rapid drops.
*   **Action:** UI changes to Crisis Mode (Skills, Emergency Contacts). No tracking pressure.
*   **Personas:** Jana, Max, Dr. Turan.

**17. FLOW-011: Backup & Migration**
*   **What:** Moving data to a new phone or recovering from loss. Local, encrypted file export.
*   **Personas:** System/Maintenance.

**18. FLOW-013: Clean Exit & Deletion**
*   **What:** End of therapy or Privacy Panic.
*   **Features:** "Shredder" (Secure delete).
*   **Therapist use case:** Deletion after 10-year legal retention period expires.
*   **Personas:** Elias, Therapists.

---

## Phase F: Meta & Evolution (App Sustainability)

**19. FLOW-018: Donation (The Support)**
*   **What:** Asking for voluntary support without pressure.
*   **Triggers:** "More" menu, **Release Notes screen** (after an update delivers value).
*   **Persona:** App Provider.

**20. FLOW-019: App Evolution (Feedback & Updates)**
*   **What:** Update notification -> Release Notes -> Feedback Loop.
*   **Feedback Mechanism:** Link to **external website** with an anonymous feedback form (No in-app analytics/tracking).
*   **Persona:** App Provider.

---


---
Das ist eine sehr wichtige methodische Frage.

**Kurze Antwort:** Ja, wir können und sollten das tun ("Backfilling"), aber **nicht stur 1:1**.

**Die differenzierte Antwort:**
Wir haben gerade "Bottom-Up" (vom Problem zum Flow) und "Top-Down" (vom System-Überblick zu den Flows) gemischt. Das ist in der Praxis oft notwendig, um den technischen Umfang ("Scope") abzustecken.

Um die Integrität unserer Dokumentation (`requirements_user_needs`) zu wahren, müssen wir jetzt sicherstellen, dass jeder dieser Flows eine **Daseinsberechtigung in der Realität** hat. Ein Flow ohne Szenario ist nur eine technische Spielerei ohne bewiesenen Nutzen.

Ich schlage folgende Strategie vor: Wir unterscheiden zwischen **System-Szenarien** (technisch) und **Persona-Szenarien** (menschlich/klinisch).

### 1. Die klinischen/menschlichen Flows (Brauchen tiefe Szenarien)
Hier reicht kein generisches 1:1 Szenario. Wir müssen diese Flows spezifischen Personas zuordnen, um die *emotionalen* und *kontextuellen* Hürden zu verstehen.

*   **FLOW-003 (Routine Entry):** Wir brauchen nicht *ein* Szenario, sondern wir müssen sicherstellen, dass wir Szenarien für die Varianz haben.
    *   *Fehlt noch:* Ein Szenario für **Nina** (Energie/Wearables) oder **Michael**, um den Import-Bedarf zu decken.
*   **FLOW-005 (Crisis Intervention):** Das darf kein theoretischer Flow sein.
    *   *To-Do:* Ein Szenario für **Jana** (BPD Krise zu Hause) oder **Dr. Turan** (Patient ruft nicht an).
*   **FLOW-016 (PDF Export):**
    *   *To-Do:* Ein Szenario für **Lisa** (Wartezeit), die zum Hausarzt geht und "Beweise" braucht.
*   **FLOW-022 (Therapist Solo Analysis):**
    *   *To-Do:* Ein Szenario für **Dr. Sarah**, die am Freitagabend Gutachten schreibt und genervt ist, wenn sie Daten nicht findet.

### 2. Die technischen/administrativen Flows (Pragmatische Szenarien)
Hier können wir 1:1 Szenarien erstellen, die eher funktional sind. Oft kann hier die **Persona "System/Maintenance"** oder eine generische Persona herhalten.

*   **FLOW-021 (Installation):** Ein einfaches Szenario ("Max versucht die App zu installieren und hat Angst vor Kostenfallen").
*   **FLOW-011 (Backup):** Ein "Disaster-Szenario" ("Sophie verliert ihr Handy").
*   **FLOW-019 (Updates/Feedback):** Ein Szenario für den **App Provider** ("Möchte Feedback einholen ohne zu tracken").

---
