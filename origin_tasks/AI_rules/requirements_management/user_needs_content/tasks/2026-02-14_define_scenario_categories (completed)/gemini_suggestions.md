Hier ist mein Vorschlag zur Strukturierung deiner neuen Kategorien, Antworten auf deine Fragen zu den Personas und meine Einschätzung zu fehlenden Kategorien.

---

### 1. Strukturierung deiner geplanten Kategorien

Hier sind Vorschläge für die Benennung der Ordner (technisch/englisch für die Struktur) und der Beschreibung, damit sie gut in das bestehende System passen.

#### A. Daten-Sicherheit & Erhalt (Data Management)
**Vorschlag Kategorie:** `management.preservation`
*Warum nicht nur "backup"?* Weil es im Status Quo oft um physischen Erhalt (Brandschutz, Verlustschutz) geht.
*   **Szenarien:**
    *   `device_loss_recovery`: Wiederherstellung nach Verlust (z.B. "Mein Notizbuch wurde in der Bahn gestohlen – was jetzt?", "Handy verloren – sind meine Einträge weg?").
    *   `migration`: Umzug auf ein neues System (z.B. "Neues Handy gekauft", "Vom Zettelchaos in ein festes Buch übertragen").
    *   `long_term_storage`: Archivierung (z.B. "Therapie vorbei, wohin mit den 5 vollen Notizbüchern?").

#### B. Intervention & Krisenmanagement
**Vorschlag Kategorie:** `intervention.support`
*Hier geht es darum, dass das System (oder das Papier) aktiv wird oder konsultiert wird, um eine Handlung auszulösen.*
*   **Subkategorien:**
    *   `acute_coping`: Nutzung von Skills (z.B. Jana sucht ihre Skill-Liste in Panik, kann die kleine Schrift aber nicht lesen).
    *   `safety_protocol`: Sicherheitsplan/Notfall (z.B. Suizidalität steigt → Instruktion "Rufe Klinik an" muss sichtbar sein. Oder: Max bemerkt extreme Nebenwirkung → Instruktion "Arzt anrufen").
    *   `resource_activation`: Positive Verstärkung (z.B. Zugriff auf eine "Hope Box" oder Fotos, die in dunklen Momenten helfen).

#### C. Anpassung des Plans (Modification)
**Vorschlag Kategorie:** `adaptation.plan_modification`
*   **Subkategorien:**
    *   `collaborative_adjustment`: Änderung in der Sitzung (z.B. Dr. Sarah merkt, dass "Schlaf" nicht reicht und fügt "Alpträume" als Spalte hinzu; sie streicht auf dem Papier etwas durch und schreibt neu).
    *   `autonomous_adjustment`: Änderung durch den Klienten (z.B. Sophie merkt, dass sie die Spalte "Essen" stresst und überklebt sie oder ignoriert sie bewusst; David erfindet eine eigene Kurzschrift, weil ihm das Ausfüllen zu lange dauert).

#### D. Wissensaustausch / Templates (Knowledge Exchange)
**Vorschlag Kategorie:** `exchange.knowledge_transfer`
*   **Szenarien:**
    *   `peer_to_peer_sharing`: Therapeut gibt Vorlage an Therapeut weiter (z.B. Dr. Sarah kopiert eine Vorlage aus einem Fachbuch für eine Kollegin).
    *   `self_discovery`: Klient sucht Vorlage (z.B. Lisa sucht im Internet oder in Ratgebern nach "Wie führe ich ein Stimmungstagebuch?", weil sie noch keinen Therapeuten hat).

---

### 2. Check der Personas für "Template Sharing"

Du hast gefragt, ob dieses Bedürfnis (Templates finden/teilen) bei bestimmten Personas ergänzt werden sollte. **Ja, absolut.**

1.  **Lisa (The Waitlist Bridger):**
    *   **Dringlichkeit: Hoch.**
    *   *Begründung:* Sie hat keinen Therapeuten, der ihr einen Plan *gibt*. Sie muss sich ihr System selbst bauen ("Psychoedukation"). Sie sucht aktiv in Büchern, Foren oder App-Stores nach "Was muss ich tracken, damit der Arzt mich ernst nimmt?".
    *   *Action:* In ihrer Persona unter "Jobs to Be Done" ergänzen: "Find structured guidance/templates on *what* to track without having a therapist yet."

2.  **Dr. Sarah (The Structured VT Professional):**
    *   **Dringlichkeit: Mittel.**
    *   *Begründung:* Sie ist Ausbilderin oder Mentorin (implizit durch ihre Erfahrung). Sie nutzt Fachliteratur (kopierte Vorlagen aus VT-Manualen). Sie würde gerne "best practice" Vorlagen mit Kollegen teilen oder digitale Vorlagen anpassen, statt immer neu in Word zu basteln.

3.  **David (The Structure Seeker):**
    *   **Dringlichkeit: Hoch.**
    *   *Begründung:* Er hat "Shiny Object Syndrome". Er sucht ständig nach dem *perfekten* System. Er lädt Templates herunter, probiert Notion-Vorlagen aus, verwirft sie wieder. Das "Browsen im Template Store" ist für ihn fast befriedigender als das Nutzen der App (Dopamin durch Neues).

4.  **Prof. Dr. Weber:**
    *   **Dringlichkeit: Niedrig/Negativ.**
    *   *Begründung:* Er glaubt an das Individuelle. Er würde wahrscheinlich keine Standard-Templates aus einem Store nutzen wollen, sondern besteht auf seinem handgeschriebenen Blatt. Für ihn ist das Feature eher irrelevant oder er muss überzeugt werden, dass er *eigene* Templates speichern kann.

---

### 3. Welche Szenario-Kategorien fehlen noch?

Basierend auf einer vollständigen "Patient Journey" und dem Lebenszyklus von Gesundheitsdaten fehlen meiner Ansicht nach noch folgende Aspekte:

#### A. Onboarding / Einrichtung (Setup)
Wir haben Szenarien, wie jemand ein Protokoll *bekommt* (`distribution`), aber nicht den **Kampf mit der Einrichtung** zu Hause (bevor der erste Eintrag gemacht wird).
*   **Warum wichtig?** Bei Papier: Stift suchen, Mappe beschriften, Platz auf dem Nachttisch freiräumen. Bei Apps: Download, Account-Erstellung (Hürde!), Datenschutz-Erklärung verstehen (Elias!), erste Konfiguration.
*   **Beispiel:** Sophie lädt eine App herunter, muss aber erst 20 Fragen beantworten, verliert die Geduld und löscht sie wieder. Oder Elias liest "Daten werden in der Cloud gespeichert" und bricht sofort ab.

#### B. Daten-Vernichtung / Abschluss (Termination & Destruction)
Das Gegenstück zum Backup. Was passiert, wenn die Therapie vorbei ist oder der Nutzer Angst bekommt?
*   **Warum wichtig?** Besonders für **Elias (The Skeptical Guardian)** und **Jana (Borderline)**.
*   **Szenarien:**
    *   `panic_deletion`: Elias glaubt, sein Partner hat das Handy in der Hand gehabt, und will sofort alle Spuren löschen (Panik-Button). Bei Papier: Verbrennen oder Schreddern.
    *   `therapy_conclusion`: Die Therapie endet erfolgreich. Was passiert mit den Daten? Werden sie archiviert (als Trophäe der Heilung) oder rituell vernichtet (Kapitel geschlossen)?
    *   `selective_destruction`: Jana hat einen Eintrag über einen Wutanfall geschrieben, schämt sich extrem und reißt die Seite aus dem Buch, damit der Therapeut sie nicht sieht. (Dies unterscheidet sich von der *Bearbeitung*, da es um Löschung geht).

#### C. Export für Dritte (Nicht-Therapeuten)
Wir haben `transfer_to_therapist`. Aber was ist mit:
*   **MDK / Krankenkasse / Gutachter:** Dr. Turan oder Dr. Sarah müssen Daten aufbereiten, um eine Therapieverlängerung zu beantragen.
*   **Hausarzt:** Max muss seinem Hausarzt zeigen, wie die Schlafmedikation wirkt (nicht dem Psychotherapeuten).
*   *Unterschied:* Hier geht es oft um aggregierte Berichte ("Wie oft in den letzten 3 Monaten?"), nicht um den detaillierten Wochenverlauf.

### Zusammenfassung der Empfehlung

1.  Füge **`management.preservation`** (Backup/Migration) hinzu.
2.  Füge **`intervention.support`** (Skills, Notfallnummern) hinzu.
3.  Füge **`adaptation.plan_modification`** (Anpassung durch Therapeut/Klient) hinzu.
4.  Füge **`exchange.knowledge_transfer`** (Templates teilen/finden) hinzu.
5.  *Neu:* Erwäge **`lifecycle.setup`** (Einrichtung/Hürden) und **`lifecycle.destruction`** (Löschen/Vernichten), da diese für Datenschutz (Elias) und ADHS (Sophie - Hürde beim Start) essenziell sind.
