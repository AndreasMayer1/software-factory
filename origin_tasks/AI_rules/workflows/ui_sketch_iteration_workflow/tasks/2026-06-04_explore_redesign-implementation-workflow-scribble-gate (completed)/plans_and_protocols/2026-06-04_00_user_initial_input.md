# User initial input (verbatim seed)

This redesign task was prompted by the developer's feedback during the evaluation task
TASK-PROC-032-28. The full, unedited feedback is preserved at:
`../../2026-06-04_explore_eval-scribble-workflow-live-iteration/plans_and_protocols/2026-06-04_03_feedback.md`

and synthesized (with grounding) in that task's Round-2 record §4:
`../../2026-06-04_explore_eval-scribble-workflow-live-iteration/plans_and_protocols/2026-06-04_04_round_2_evaluation.md`

Read both as a seed bed, not a spec.

The load-bearing verbatim passages that prompted THIS task (developer's own words, German, unedited):

---

> Ich habe noch eine Ergänzung zu den Scribble Tasks. Die Scribble Tasks müssen ausgeführt werden, bevor
> andere Coding Tasks ausgeführt werden. Am besten wäre es, dass die Scribble Tasks ein eigenes Layer bekommen.
> Denn es kann sein, dass, wenn man das User Interface Reviewt, man Änderungen bemerkt, die dann noch
> vorgenommen werden müssen. An unterschiedlichen Stellen. Es kann sogar sein, dass man User Flows nochmal
> anpassen möchte... Also eigentlich dürften die Coding Tasks erst dann erstellt werden, wenn die Scribbles
> abgenommen sind. Der Workflow ist also Userflow definieren. Dann die Tasks davon ableiten, die die
> Requirements anpassen. Und wenn dann Beginn Implementation Skill aufgerufen wird, werden als erstes die
> Scribbles erstellt... erst wenn alle Scribble Tasks erfolgreich abgeschlossen sind und die Scribbles
> abgenommen sind, dann werden die Implementation Tasks fürs Coding erstellt... Wir müssen wahrscheinlich den
> Begin Implementation Skill in zwei Teile zerlegen. Oder vielleicht sogar in drei...
>
> Wir haben ja auch noch andere Stellen, an denen der Scribble Skill zurückläuft... Wir müssen uns gut
> überlegen... wie wir das in einzelne Teile zerlegen wollen, damit nicht in einem Skill die ganze Komplexität
> steckt... Was wir wollen, ist die insgesamte Token-Nutzung des ganzen Prozess zu minimieren... eine Session
> sollte möglichst nur genau die Informationen halten, die sie tatsächlich auch braucht... Die Frage ist nur,
> wo genau macht man den Cut? Bitte prüfe das auch nochmal bei den bereits existierenden Skills.
>
> [F15] ... macht es wahrscheinlich Sinn, dass dann automatisch ein Task erstellt wird, der eben das Ziel hat,
> die Scribbles anzupassen. Allerdings verlieren wir dann natürlich die Kontrolle darüber, wann diese Anpassung
> erfolgt. Wir haben dann auf jeden Fall in der Zeit... eine Diskrepanz zwischen Requirements und Scribbles.
> Wie wollen wir damit umgehen?...
>
> [F16] ... Was passiert, wenn Requirements angepasst werden, die auch von Scribbles eines anderen Requirements
> benutzt werden... Wenn sich das Dashboard und seine Interaktionsmöglichkeiten grundlegend verändern, kann das
> dazu führen, dass alle Features, die Daten auf dem Dashboard anzeigen oder Aktionen dort anbieten, angepasst
> werden müssen... auf Scribble-Ebene... Wie wird so eine Kaskade aufgelöst?
>
> Bei all diesen Überlegungen zum Workflow müssen wir auf jeden Fall sorgfältig vorgehen und nicht einfach
> diese neuen Funktionen in den bestehenden Workflow reinpressen, sondern wir müssen den kompletten Workflow,
> also alle Skills, die beteiligt sind, nochmal komplett neu denken.

---

Developer's process decision when this task was created (2026-06-04): "create a redesign task. but let the
skill usage open. i think it's more an exploration." And: the comment-nesting render-leak fix is to be
**folded into this redesign**, not spun off separately.
