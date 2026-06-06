---
task_id: TASK-PROC-013-01
type: impl
parent_requirement: REQ-PROC-013
parent_requirement_path: requirements_tasks/process/AI_rules/requirements_management/user_needs_content/max_client/requirement.md
urgency: 3
urgency_reason: U3-QUAL
impact: 4
impact_reason: I4-CORE
status: completed
effort: XS
created: 2026-01-21
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections:
    - "Persona: Jobs to Be Done (Functional, Social)"
    - "Persona: Mental Models & Expectations"
    - "Persona: Current Status Quo (Pain Points)"
    - "Persona: Friction & Barriers (Fears)"
    - "Scenarios: brain_dump_at_night (rewrite to status quo)"
    - "Scenarios: forgotten_protocol_transfer (new scenario)"
scope_description: |
  Incrementally improve Max Client persona and scenarios by:
  1. Rewriting persona to reflect status quo (pen and paper) without app references
  2. Adding Jobs to Be Done (functional/social dimensions for therapy collaboration)
  3. Updating Mental Models with psychological concepts (energy/control)
  4. Adding pain points (ineffective therapy sessions)
  5. Adding fears (context loss/mixing private vs therapy content)
  6. Rewriting brain_dump_at_night scenario to status quo
  7. Adding new forgotten_protocol_transfer scenario
requirements_version:
  commit_hash: b1b783a
  file: requirement.md
  timestamp: 2026-01-21
---

Modify max client like described below. Note that you must not just copy paste what is written below, but understand the contained information and write it to the files according to the requirements for the files. Maybe you have to add more information, maybe you have to remove or modify. If you have to remove or modify, ask the user how to do it.

# Persona

Die Persona bildet den Status Quo ab (Stift und Papier) und darf keine Referenzen auf die App Lösung enthalten. Entsprechend muss die Persona komplett überarbeitet werden.

Zusätzlich dazu:

#### 1. Sektion: Jobs to Be Done
**Anweisung:** Erweitere die Functional und Emotional Jobs um die Dimension der Zusammenarbeit und Trennung der Bereiche.

*   **Hinzufügen bei Functional Jobs:**
    *   **Vorbereitung auf die Therapiesitzung:** Max möchte Informationen sammeln, um sie in der nächsten Sitzung mit Dr. Sarah zu besprechen. Er will vermeiden, wieder mit "leerem Kopf" (Memory Fog) dazusitzen und wertvolle Therapiezeit mit Erinnerungslücken zu verschwenden.
    *   **Trennung von Kanal und Inhalt:** Er muss unterscheiden können zwischen "Privates Ventil" (Gedanken, die niemand sehen soll) und "Therapeutisches Material" (Beobachtungen, die für Dr. Sarah relevant sind).

*   **Hinzufügen bei Social Jobs:**
    *   **Therapeutisches Bündnis stärken:** Er möchte seinen Teil der Abmachung einhalten ("Hausaufgabe machen"), um aktiv an seiner Genesung mitzuarbeiten. Er nimmt die Hilfestellung an, auch wenn sie anstrengend ist.

#### 2. Sektion: Mental Models & Expectations
**Anweisung:** Ersetze technische Begriffe durch psychologische Konzepte zu Energie, Beständigkeit und Kontrolle.

*   **Ersetzen/Anpassen:**
    *   Statt "Erwartet Autosave..." -> **Schutz der emotionalen Investition:** Für Max kostet es enorme Überwindung (Energie/"Löffel"), seine Gefühle in Worte zu fassen. Wenn er diese Energie einmal aufgebracht hat, erwartet er absolute Sicherheit, dass das Ergebnis nicht verloren geht (egal ob durch verlorene Zettel oder technische Fehler). Ein Verlust würde sofortige Resignation auslösen ("Ich habe keine Kraft, das nochmal zu schreiben").
    *   Statt "Angst vor Sync..." -> **Hoheit über die Offenbarung:** Max betrachtet seine Aufzeichnungen als Erweiterung seines Gedächtnisses. Er erwartet, dass *nichts* davon sein Gerät verlässt oder von anderen gesehen wird, es sei denn, er entscheidet sich in einem expliziten, bewussten Moment dazu, es zu "übergeben" (wie das Überreichen eines Blattes Papier). Automatische Hintergrundprozesse empfindet er als Kontrollverlust.

#### 3. Sektion: Current Status Quo (Pain Points)
**Anweisung:** Ergänze den Frust über fehlende Ergebnisse in der Sitzung.

*   **Hinzufügen:**
    *   🔴 **Ineffektive Sitzungen:** Ohne Aufzeichnungen verbringt er die ersten 20 Minuten der Therapie damit, sich mühsam zu erinnern, wie die Woche war. Er ärgert sich darüber, dass er Dr. Sarah keine konkreten Anhaltspunkte geben kann, um an seinen Problemen zu arbeiten.

#### 4. Sektion: Friction & Barriers (Fears)
**Anweisung:** Ergänze die Angst vor der Vermischung.

*   **Hinzufügen:**
    *   🟡 **Angst vor Kontextverlust:** Die Sorge, dass er in der Sitzung versehentlich private, ungefilterte Wut-Gedanken vorliest oder übergibt, die eigentlich nur zum "Dampf ablassen" gedacht waren. Er braucht eine klare Grenze.


**Änderungen:**

*   **Unter `Jobs to Be Done / Functional Jobs` hinzufügen:**
    *   **Therapie-Zuarbeit:** Informationen sammeln, um in der Sitzung arbeitsfähig zu sein (Vermeidung von "Ich weiß nicht mehr").
    *   **Kanal-Trennung:** Er muss sicher unterscheiden können: Was ist mein privates Ventil (Tagebuch) und was ist die "Hausaufgabe" für Dr. Sarah?

*   **Unter `Mental Models` (Anpassung):**
    *   **Schutz der emotionalen Investition:** Das Formulieren von Gefühlen kostet Max viel Kraft ("Löffel"). Er erwartet, dass diese Investition sicher ist (kein technischer Verlust), sobald er sie getätigt hat.


# Scenarios

## brain_dump_at_night

Rewrite the scenario so it is based on the status quo (pen and paper). We did not conduct interviews, this is just invented by google gemini, so review is still needed.

```
---
# Scenario: Brain Dump at Night (Status Quo)

## Persona

**Reference**: [Max (Client with Depression/ADHD)](../../persona.md)

**Archetype**: The Overwhelmed Seeker

## Goal

**What the user wants to achieve**: Offload circular thoughts from his mind onto a physical medium so he can stop ruminating and fall asleep.

**Why this goal matters** (emotional/functional):
- **Functional**: Stop the mental loop that's preventing sleep.
- **Emotional**: Regain a sense of control over his racing mind.
- **Physical**: Maximize remaining sleep time before work.

## Context

**Triggers**: Lying in bed at night (02:15 AM), unable to sleep because of repetitive thoughts about a mistake at work and a missed email.

**Frequency**: 2-3 times per week.

**Environment**:
- **Physical location**: In bed, pitch black room, next to sleeping partner (Sophie).
- **Time of day**: Late night (02:15 AM).
- **Emotional state**: Anxious, mentally exhausted, frustrated by insomnia.
- **Constraints**: Cannot make noise (thin walls, light sleeper partner), cannot turn on light.

**Cognitive load**: High—thoughts are looping, "wall of awful" blocking sleep.

🟡 *Proto-persona: Based on common depression/ADHD sleep disturbance patterns (rumination, racing thoughts).*

## The Story (Three-Act Structure)

### Act 1: Context & Inciting Incident

It's 02:15 AM. Max has been staring at the ceiling for an hour. His body is tired, but his brain is running a marathon.

*Internal thought: "I definitely forgot to send that attachment. My boss is going to ask about it first thing. And I didn't call my mom back. She probably thinks I'm ignoring her."*

The thoughts loop. Work. Mom. Work. Mom. The anxiety tightens in his chest. He knows from experience that unless he gets these thoughts "out" of his head and onto paper, he won't sleep.

He remembers his therapy notebook is on the nightstand. Dr. Sarah told him: "Write it down, then it's a problem for tomorrow, not tonight."

### Act 2: Interaction & Resistance (The Analog Struggle)

Max reaches out slowly in the dark, his hand sweeping across the nightstand. He knocks over a water glass—luckily empty—but it makes a loud *clatter* as it hits the floor.

Next to him, Sophie stirs and groans. "Mmh... Max? Everything okay?"

Max freezes. "Yeah. Sorry. Go back to sleep."

He waits until her breathing deepens again. He finds the notebook and the pen. Now he has a problem: It's pitch black.

*Option A: Turn on the bedside lamp.*
*Outcome:* It will flood the room with light, definitely waking Sophie fully. She has an early shift. He can't do that.

*Option B: Go to the living room.*
*Outcome:* Requires getting up, cold floor, fully waking up his body. He knows if he stands up now, he'll be awake for another two hours. The barrier is too high.

*Option C: Write in the dark.*
He chooses this. He clicks the pen—*CLICK*. It sounds incredibly loud in the silence. He winces. He opens the book to a random page and starts scribbling blindly.

*"Forgot attachment. Call mom."*

He tries to keep his handwriting legible, but he can't see the edges of the page. He feels the pen crossing over the spiral binding. He's probably writing over yesterday's notes.

The friction of pen on paper feels loud. The effort of holding the thought while trying to write legibly without sight increases his agitation rather than reducing it.

### Act 3: Result & Feeling (Failure)

After two minutes of blind scribbling, Max gives up. He puts the pen down (carefully, to avoid another clatter).

He lies back down. The thoughts are technically "on paper," but he feels no relief. He worries: *"Did I write it clearly? Will I be able to read that mess tomorrow? Did I ruin the entry from yesterday?"*

The anxiety about the *method* of recording has now replaced the anxiety about the work email.

**Next morning**: Max wakes up groggy. He opens the notebook. The page is a mess of overlapping scrawls. He can decipher "Call m--" but the rest is illegible hieroglyphics written over a previous list. He feels frustrated and stupid. The "therapy homework" feels like just another thing he failed at.

**Emotional shift**: From Anxiety (Looping thoughts) → Frustration (Physical barriers) → Resignation (Giving up) → Shame (Next morning).

## Current Status Quo Analysis (Why Paper Fails)

This scenario demonstrates why the current analog solution is insufficient for Max's specific context:

1.  **Light Constraint**: Paper requires external light to be usable. Turning on light breaks the "sleep state" and disturbs the non-user (partner).
2.  **Sound Constraint**: Physical interactions (pen clicking, pages turning, objects falling) are audible and risky in a shared bedroom.
3.  **Physical Friction**: The requirement to sit up or move to another room creates a "Wall of Awful" (ADHD barrier) that prevents the therapeutic action.
4.  **Data Integrity**: Writing blindly results in illegible data (Data Loss), rendering the therapeutic exercise useless.
5.  **Feedback Loop**: The failure to successfully log the thought creates *new* shame/anxiety, counteracting the therapy goal.

## Derived Needs (For Digital Solution)

Based on this failure, a digital solution must provide:
1.  **OLED/Dark Mode**: Usable in pitch darkness without illuminating the room (pixel-level control).
2.  **Silent Input**: Typing (haptic feedback only) or Whisper-to-Text (adaptive gain) to avoid waking partner.
3.  **Low Friction**: One-tap access from bed, no need to sit up or leave the room.
4.  **Auto-Save/Legibility**: Perfect capture of thoughts regardless of darkness; no risk of "bad handwriting."

## Data Sources

**Evidence**:
- 🟢 Grounded: ADHD executive dysfunction (difficulty initiating tasks like "getting up to write").
- 🟢 Grounded: Insomnia and rumination patterns in depression.
- 🟡 Proto-persona: Co-sleeping constraints (partner disturbance).
- 🟡 Proto-persona: "Parking Lot Syndrome" / Shame regarding imperfect therapy homework.

---
```

## forgotten_protocol_transfer

Add this new scenario as draft:

```
# Scenario: Forgotten Protocol & Transfer Shame (Status Quo)

## Persona

**Reference**: [Max (Client with Depression/ADHD)](../../persona.md)

**Archetype**: The Overwhelmed Seeker

## Goal

**What the user wants to achieve**: Successfully hand over his filled "Weekly Anxiety Protocol" to Dr. Sarah at the beginning of the session so they can analyze his progress.

**Why this goal matters** (emotional/functional):
- **Functional**: Provide data for the therapy session to work on specific triggers.
- **Social**: Prove to Dr. Sarah that he is "doing the work" and is a compliant client.
- **Emotional**: Avoid the shame of appearing disorganized or unmotivated.

## Context

**Triggers**: Tuesday afternoon, 15:45. Max is on the S-Bahn (train), commuting to his 16:00 therapy appointment.

**Frequency**: Happens approx. once a month (ADHD symptom: forgetfulness).

**Environment**:
- **Physical location**: Public transit, moving vehicle.
- **Time of day**: Afternoon rush hour.
- **Emotional state**: Rushed, slightly anxious about the upcoming session.
- **Constraints**: Physical separation from home (cannot go back).

**Cognitive load**: High—thinking about what to discuss in therapy, navigating transit.

🟡 *Proto-persona: Based on common ADHD challenges with object permanence and task switching.*

## The Story (Three-Act Structure)

### Act 1: The Verification & Shock

Max sits on the train, scrolling through Instagram to distract himself. He passes the stop two stations before Dr. Sarah's practice. His brain switches to "Therapy Mode."

*Internal thought: "Okay, what do I need? Wallet, keys, insurance card... and the protocol."*

He reaches into his backpack. He feels his laptop, his gym clothes, a water bottle. He feels for the distinct texture of the plastic folder Dr. Sarah gave him.

It's not there.

He unzips the bag fully, rummaging frantically. People on the train glance at him. He checks the laptop sleeve. Nothing.

Then the image hits him: The blue folder is sitting on the shoe rack in his hallway. He put it there specifically so he *wouldn't* forget it. And then he walked right past it.

*Internal thought: "Oh no. Not again. She's going to think I didn't fill it out. She's going to think I don't care."*

### Act 2: The Attempted Reconstruction (Panic)

Max has 10 minutes before he arrives. He pulls out his phone. Maybe he can reconstruct the data?

He opens his Notes app.
*"Okay, Monday... Monday was... bad? I think I had a fight with Sophie. Anxiety level... maybe 7?"*

He types: `Mon: Anx 7, Fight`.

*"Tuesday... I don't remember Tuesday. Was I at the office? I think so. It was probably fine. Let's say 4."*

He types: `Tue: Anx 4`.

He realizes he is guessing. He isn't actually tracking; he is fabricating data to avoid embarrassment. He feels a wave of guilt. This isn't therapy; this is performance. He stops typing. It's pointless.

### Act 3: The Confession & Wasted Time

16:05. Max sits in the therapy chair across from Dr. Sarah.

**Dr. Sarah**: "Hello Max. Good to see you. Did you bring your protocol for this week?"

Max looks at his shoes. The shame is hot on his neck.

**Max**: "I... I left it on the shoe rack. I filled it out! I swear. I really did it this week. But I walked right past it."

Dr. Sarah nods sympathetically, but Max interprets it as disappointment.

**Dr. Sarah**: "That happens. It's okay. But since we don't have the data, maybe we can try to reconstruct the key moments together? How was your weekend?"

**Max**: "It was... okay, I guess."

They spend the next 15 minutes—**30% of the session time**—trying to remember what happened on Thursday. Max's recall is foggy. They miss a critical pattern about his sleep medication because Max can't remember exactly which night he skipped it.

**Result**: The session is less effective. Max feels demoralized. The insights are shallow because the hard data is sitting on a shoe rack 5km away.

**Emotional shift**: From Prepared (on train) → Panic (Realization) → Guilt (Fabrication attempt) → Shame (Confession).

## Current Status Quo Analysis (Why Paper Fails)

This scenario demonstrates the critical points of failure in the analog workflow:

1.  **Single Point of Failure**: The data exists in only one physical location (the paper). If the object is not present, the data is inaccessible.
2.  **Object Permanence (ADHD)**: The requirement to remember a physical object runs directly counter to Max's executive dysfunction symptoms.
3.  **Data Quality vs. Recall Bias**: When the physical record is missing, Max resorts to memory, which is unreliable ("Recall Bias"), reducing therapeutic value.
4.  **Inefficiency**: Valuable therapy time (expensive and scarce) is wasted on administrative reconstruction rather than clinical work.
5.  **Relational Strain**: The repeated failure to bring materials creates a dynamic of "teacher/student" or "disappointment," increasing Max's shame and potentially leading to therapy avoidance.

## Derived Needs (For Digital Solution)

Based on this failure, a digital solution must provide:
1.  **"Always On" Availability**: The data must live on the device Max never forgets (his smartphone).
2.  **Digital Transfer**: The ability to transfer data to the therapist without physical handover (e.g., if he forgets the phone but has cloud access, OR strictly local transfer if he has the phone). *Correction per project constraints*: Since we are Local-First/Zero-Knowledge, the need is strictly that **the device itself is the carrier**, eliminating the "extra object" (paper folder).
3.  **Backup/Export**: A way to send the data (e.g., via secure file/email) if he is physically present but perhaps running late or for remote sessions, so the therapist has it *before* the session starts.

## Data Sources

**Evidence**:
- 🟢 Grounded: ADHD symptoms (forgetfulness, working memory deficits).
- 🟢 Grounded: Recall bias in retrospective symptom reporting (psychological standard).
- 🟡 Proto-persona: Max's desire to be a "good patient" vs. his functional limitations.
```
