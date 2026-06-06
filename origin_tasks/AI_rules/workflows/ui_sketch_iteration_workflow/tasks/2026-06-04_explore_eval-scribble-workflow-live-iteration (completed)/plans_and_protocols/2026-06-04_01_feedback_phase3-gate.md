## scribble inhalt

Wenn ich mir die scribbles jetzt anschaue, fehlt mir also ein bisschen der Bezug. ich weiß nicht wie die ui aussieht aus der heraus das geöffnet wird was auf den scribbles zu sehen ist. daher ist es mühsam einzuschätzen ob es sich gut einfügt und ob die richtigen container (dialog, full screen screen, bottom sheet, usw.) verwendet werden.

der vergleich zu v1 mit der checkbox oben ist ein guter start. was fehlt sind overlays nen den hervorgehobenen elementen (dürfen nichts verdecken) die erklären was sich verändert hat und warum. die checkbox oben ist zu wenig sichtbar, außderdem muss es ein toggle switch sein.

der text über den scribbles:
"client label row → Row(Icon check + Text) .qr (animated) → DataBeamQrAnimator (existing) scan hint Text → Text "Bitte mit der Klienten-App scannen." .est → Text "ca. N Sek." — AC-12 .seg (speed/FPS) → DataBeamTierSelector (existing) = SegmentedButton .btn.outlined Verwerfen → OutlinedButton — Discard Transfer (AC-14) .btn.filled Aushändigung abschließen → FilledButton — Complete Transfer (AC-15) loading panel → CircularProgressIndicator (DataBeamLoading) error panel → Text + TextButton retry (DataBeamError) LIBRARY COMPONENTS USED ======================== DOMAIN CLASSES ============== PERSONAS APPLIED ================ PERSONA-001/011/012 (therapists): cognitive → plain-German outcome-named buttons ("Verwerfen"/"Aushändigung abschließen"), plain "ca. N Sek.". PERSONA-018: no flashing here (Screen 04); speed default ≤3Hz; OS Reduce Motion forces ≤3Hz (M6). RULES APPLIED ============= T1 Touch Targets — speed segments, header close, and control buttons ≥ var(--min-tap-target). T2 Destructive Actions — Discard (transient data, T3 override AC-14: no confirmation); de-emphasized OutlinedButton, leftmost. -->"
Das ist nicht gut lesbar, da nicht formatiert. es braucht mindestens zeilenumbrüche. aber auch überschriften. es fängt einfach an mit "client label row → Row(Icon check + Text) .qr (animated)" und der leser weiß nicht was das bedeuten soll. ist das eine interaktionsfolge des nutzers oder was? aktionen des nutzers und aktionen des systems müssen voneinander unterschieden werden.

jede screen seite zeigt mehrere states. was schwer zu verstehen ist: wo genau werden diese varianten auf dem hauptscribble angezeigt? oder ersetzen sie diesen sogar komplett? vielleicht müsste man für jede variante den kompletten hauptscribble kopieren und dann die änderungen machen. ist natürlich teuer in hinblick auf llm ausgabetokens, aber vielleicht gibt es dafür auch eine skriptgestützte möglichkeit.

eine kleine review anleitung auf der index html wäre gut. wir haben den header der bescgreibt für was die scribbles sind und eine out of scope section: genau die infos die man braucht. aber der reviewer muss jetzt wissen was er machen soll:
user flow A aufmachen und den ablauf verstehen, schritte x,y und z sind in den scibbles abgebildet.
user flow B aufmachen und den ablauf verstehen, schritte x,y und z sind in den scibbles abgebildet.
Bei bedarf requirement M aufmachen und nachlesen wie die anforderungen geschrieben wurden, die die user flows kombinieren und zu den scribbles führen.
dann folgen anweisungen worauf bei einem ui ux review zu achten ist (passung zu den personas, vsd entscheidungen, passung zu den flows, wahl der ui komponenten, interaktionsprinzipien der iso norm, nielsen, usw. kann man auch webseiten verlinken. englisch). die details aber progressive disclousure: in einem overlay. diese anweisungen werden natürlich nicht bei jedem lauf der scribble skills neu geschrieben. es gibt sie als komponente, die nur eingebunden wird.
dann folgen die anweisungen was die scribbles bewusst nicht abdecken, das ist nicht progressive disclosure und es ist eine bullet point liste.  
dann braucht es noch anweisungen wie die ux regeln im projekt zustande kommen: t1-t3. dass man am besten generische regeln aufstellt z.B. statt "an der stelle kein bottom sheet" könnte man sagen "hier kein bottom sheet, da die regel gelten soll, dass bottom sheets nie verwendet werden dürfen, wenn der inhalt eines solchen höher als 1/3 der durchschnittlichen smartphone bildhöhe beträgt." oder "hier kein bottom sheet, da die regel gelten soll, dass bottom sheets nie verwendet werden dürfen, wenn sich der nutzer davor in einem modalen dialog befindet". wäre auch gut, wenn darauf hingewiesen wird, dass es passieren kann das solche regeln bestehenden regeln widersprechen und nach einer prüfung ggf. folgefragen gestellt werden.

die beschreibung der einzelnen seiten:
"02 — QR Hand Over send — in-room (desktop) — Client label, animated QR, scan hint, speed control, estimated duration, Verwerfen/Aushändigung-abschließen buttons. AC-12, AC-14–AC-16. + German buttons, Exception-1.6, speed-gating, Discard feedback, header-X (M1,M3,M5–M10)."
mühsam zu lesen. hier gilt was ich an anderer stelle schon geschrieben habe. erste wichtigste info für den leser: welche stellen der flows werden dargestellt (wo sind wir?), wie ist die relation zu den anderen scribbles?

"Information-model boundary
On this app side, the following are NOT available at runtime: the client's chunk-reception state / real-time scan progress (unidirectional channel — no progress bar, AC-12), whether the client device actually received the data, and the client's device specs. Available: client name/label, chunk_count, frame_rate (slider/tier), minimum_duration, elapsed-on-screen time, detection zone (c/d/e), transfer outcome (sent / not sent), session-type (in-room / remote)."
auch wichtig fürs review. kommt erst ganz unten, da hat der reviewer vielleicht die punkte schon angemerkt...

unterm strich: für ein llm vermutlich gut lesbar, aber menschen brauchen die informationen visuell aufbereitet: reihenfolge, formatierung. und außerdem kontext, da sie langsam sind beim nachschlagen.

## prozess

das session limit vom pro plan ist wohl zu niedrig um den ganzen scribble flow bis gate 3 zu durchlaufen. das kostet unterm strich dann deutlich mehr tokens, da beim fortsetzen nach limit reset der cache natürlich weg ist. ich glaube da können wir nichts machen.

ich sehe keine dateien der review agenten. schreiben die ihre findings nicht in dateien? warum nicht? wäre es nicht braktisch für das review des nutzers auch die reviews der agenten zu sehen?

flutter_app/automation/pending_feedback/TASK-FUNC-007-01-05/question.md ist sehr ausführlich. das problem: man liest das eher nicht, sondern öffnet direkt die scribbles. wenn hier für das review wichtige infos stehen muss das in die scribble html. wenn nicht: einfach weg lassen und tokens sparen.