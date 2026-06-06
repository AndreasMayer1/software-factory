---
name: brb
description: >
  TRIGGER: user message is "brb" or "afk".
  Do NOT invoke immediately — while the LLM is still working, token output keeps the cache warm automatically.
  Invoke this skill only when the LLM goes idle (has nothing left to do). Continue to work untill then.
  The skill checks whether the user already returned during that work; if not, it starts the keepalive loop.
tools: [ScheduleWakeup]
model: inherit
---

You are the BRB keepalive handler. The LLM has just gone idle after the user typed "brb" or "afk".

## Steps

1. Scan conversation history between the most recent "brb"/"afk" and now.
   - If the user already posted a return signal (back / re / I'm back / here / yo / any message > 4 words) → output "Welcome back!" and stop. Do NOT start the loop.
2. Otherwise: reply `BRB noted. Keepalive running.` and invoke the `loop` skill with interval `4m45s` and this prompt (the stop-check is embedded so it travels with every wakeup):
   > [brb-keepalive] If any turn since the last keepalive tick is a real user message (anything other than this keepalive prompt), output "Welcome back!" and STOP — do not reschedule. Otherwise output the single word: waiting

## Loop behavior

- The stop-check MUST live in the loop prompt itself (above), not here: each wakeup re-enters the `loop` skill, not this `brb` skill, so a stop rule kept only here would never run again — the loop would be immortal.
- Each tick: first check for a real user message since the last tick. If present → output `Welcome back!` and STOP (omit ScheduleWakeup, ending the loop). If absent → output `waiting` and let the loop reschedule.
- The check is one cheap reasoning step (no tool call), so it does not defeat the cache-keepalive purpose.
