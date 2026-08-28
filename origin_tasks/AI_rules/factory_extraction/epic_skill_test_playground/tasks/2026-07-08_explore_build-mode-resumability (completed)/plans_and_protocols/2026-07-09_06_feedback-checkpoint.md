---
skill: ideation-start
mode: automated
decision: ""
task_id: TASK-PROC-068-20
captured_at: 2026-07-09
---

# Question

---
task_id: TASK-PROC-068-20
session_id: f9f98c5d-e1ce-4c6a-a3a5-dbbff842e229
account: gmail2
status: awaiting_answer
asked_at: 2026-07-08T22:42:43Z
skill: ideation-start
---

# Pending Question — End-of-run gate: approve the resume design & confirm next step

Full design in: `requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/tasks/2026-07-08_explore_build-mode-resumability/plans_and_protocols/2026-07-09_004_synthesis.md`
Report: `…/2026-07-09_005_final_report.md` · Ledger (rendered): `…/2026-07-09_001_ideation_ledger.html`

Open the artifacts from the run folder above. One-paragraph recap: model the deployed build-mode run as a
**resumable OUTER `in_progress` task** keyed by a **durable run handle**; move the isolated copy out of
`/tmp` into a durable runs dir; a host-side **run registry** + a `playground-build-resume` skill let a cold
session **re-attach** (skipping deploy/seed/snapshot); gate the irreversible harvest+discard on an
**explicit completion signal** (inner ChainState `complete: true`). Safety invariant: **preserve-by-default,
discard-only-on-verified-complete, skip-harvest-on-incomplete** — every non-clean exit degrades to "copy
preserved, nothing harvested", never a partial deposit. A usage-limit is reframed as a **planned pause**
(new `LaunchResult.reason=="paused"`); the outer pause is free via the orchestrator's existing
`rate_limited`→resume path, the inner orchestrator shares the one `~/.claude` window.

## 1. Approve the synthesis? (APPROVE / ITERATE)
If ITERATE, say what changed (weights, framing, a missing frame, new info).

## 2. Four decisions (recommendations in brackets — confirm or override)
- **D1** — v1 completion policy = **preserve + skip-ALL-harvest on any incomplete exit** (defer per-commit
  partial harvest)? *[recommend: yes]*
- **D2** — state model = **preserve the whole copy in a durable runs dir** (git-bundle rehydrate as
  documented fallback)? *[recommend: yes]*
- **D3** — scope = **design the generic BuildRun seam now, implement the derivation path first** (vs.
  derivation-only, no seam)? *[recommend: seam now, derivation first]*
- **D4** — requirement landing = **REQ-PROC-068** (wrapper/registry/completion-gate ACs), **REQ-PROC-071-06**
  (feat_backfill "unattended across fresh sessions"), or **both**? *[recommend: both]*

## 3. Confirm the next step this session should perform on resume
Per goal AC-06/AC-07, once approved the next actions are:
1. `requ-explore` → author the resumability ACs into the requirement(s) chosen in D4.
2. `task-derive-from-requ` → create the impl tasks that build the mechanism (durable runs dir + registry +
   completion gate + `reason='paused'` + `playground-build-resume` skill + BuildRun seam).
3. Unblock **TASK-PROC-068-12**: set its `after:` to the **new impl-task IDs** (not this explore task),
   re-author its How-to-Approach to the build-mode/deployed-copy resume path, clear its `session_id`, and
   clear its interim `awaiting` hold.

Confirm this is the next step, or state a different one.

## Honest residual uncertainties (U1–U5, detail in synthesis)
U1 per-commit partial harvest (deferred); **U2** inner-orchestrator limit-pause is unexercised (068-18 used a
deterministic child); **U3** limit-detection scrapes child stdout (mitigated by fail-safe preserve); U4 disk
cost of preserved copies; U5 account-rotation-on-resume JSONL path resolution.

# Developer Answer

We need another ideation run because I have some feedback we have to work into.

I like the idea to move the isolated directory out of the temp folder, but I don't agree with where you would put it. We already use work trees in the project. For example, the bug fix skill uses work trees to work on bug fixes. Course work trees have to be in directories that are outside of the project. So it currently uses the parent directory of the project. And I want to do the same for this playground. And I think it actually currently already uses the parent folder of the project. At least I observed that and that's what I requested. So I think it's wrong that it is currently using the temp folder. A bonus would would be if we would have a configuration file in the project where the user can define which folder he wants to use for all additional folders or directories that are needed and must live outside of the project. So he could specify that he wants to use the parent directory like we currently do, or whatever other location he wants. In another exploration we actually thought about having a project environment configuration, but I currently don't remember where.

I like the idea with the registry. I think we have to go more into detail of all the possible states the inner and the outer runs and sessions can be in. Let me kickstart that a bit. So we can have in the outer session that has no task. That wants to use the playground. As you already noted, we might want to force that this is not allowed, so that the skills that work on that playground Um have a step, a phase in the beginning where they demand a task, and if there is no task, they create one. And I think that's a good safety net. But it is actually from my current perspective or current understanding only needed if we don't have the registry. Because once we have a registry, the state of the playground can be recorded there. So when I start a fresh session and I want it to work on the playground, it can access the state of the playground from the registry. And whatever session did it before with or without task. It doesn't really matter because we have the registry that holds the current state. But maybe there are other reasons why we want or need a task.
So auto we have a session that runs with or without task and it can run in a interactive session when start the playground so it can start a fresh playground and um inject or start the inner run. Once it started the inner run, well I guess it terminates. If it is an interactive session, it just waits for what? Do we need to have a inner run succeeded signal somehow? And the session is checking a file every I don't know 15 minutes to see if it is done and if it is done it resumes? 
If the session runs in the auto run mode, so it is started by the orchestrator, it must have a task. In that case, we have two options, I think. We can once the session started the inner run, it can either terminate and tell the orchestrator that it is waiting for the inner run and the orchestrator is handling the monitoring, so the orchestrator is watching a file, for example, to see if the inner run is completed, and once it is completed it resumes the session from the outer run. If we do that, we might have two different mechanisms that are not needed necessarily. So what I explained now, this is the case that we do not hit the usage limit, right? So the session if you assume that there is no usage limit and the session just has the capacity to run forever, there is no problem, and we could also even in the orchestrator in the how to run mode, the session could just use what I described for the interactive mode. It can just check every 15 minutes, for example, if the inner run is completed.
That breaks once the usage limits come into play. In an interactive session. That's not really a problem because the user is in charge. He is responsible to resume it. So we don't really have to think about it that much. But once we decide the how to run method, we have to think about how that method can be applied to the interactive mode. How how it um f fits.
So imagine the session in the outer run started the inner run. If it is not terminating, but it is instead checking every fifteen minutes for the state of the inner run, It will hit the usage limit. That's almost certain. What happens? The orchestrator will see that it hit the usage limit, and it will try to resume it with another account that still has capacity. Imagine that is the case. So it it gets resumed with another account. No problem. It will continue to check every 15 minutes. So if we have enough capacity over all accounts, no problem. It will work. But that's also unlikely. But depending on the use case. It can happen that all accounts hit the rate limit. In that case the orchestrator blocks. It's just sleeping and waiting for the limit to reset. And once the limit resets it resumes the session. So for the outer orchestrator. I think we can actually let the session itself handle the check if the inner run is completed or not. It is of course not as efficient as if we would outsource that check to the orchestrator. But on the other hand, the question is is the auto orchestrator is the orchestrator responsible? Should it be responsible? Does it break encapsulation? Single responsibility.

Now we have to bring the inner orchestrator into the picture. Because the session from the outer run starts work inside the other project and it starts an orchestrator inside the other project. So we have an inner orchestrator running. This inner orchestrator behaves exactly like the outer orchestrator, it's just a copy. That means that it manages the session limits by its own. Once the inner run, the sessions in the inner run hit a usage limit, the orchestrator from the inner run also just tries to switch the account and resume on a different account. Until there is no account with um capacity left and then it just blocks and sleeps and waits for the limit to reset. So it's exactly the same like the outer orchestrator does. And one thing is that the limit is of course shared. So if the inner orchestrator notices that all accounts reach their limit, the outer orchestrator also Notices that. Probably not at exact the same time because um it always depends on if the session is actually doing work and we just said that the session from the outer orchestrator is just checking every 15 minutes and if something happens if the limit is reached in the time between those 15 minutes wait, um it will not notice that it has no limit left. So the outer orchestrator will notice later than the inner orchestrator that there is no limit left. But doesn't really matter. You can imagine that both orchestrators actually sleep to wait for the limit to reset during the same time. So another perspective is that they just freeze in time, nothing happens. And then once the limit is reset, or once the time is up, they resume and they just resume where they left off. So I think maybe it is naive, but I think it should already work without any modifications to the orchestrator.
Maybe I'm wrong. You have to check that. And also check if that easy solution to actually do not modify the orchestrator is the best solution we have.
I think it also depends on those fifteen minutes. I think fifteen minutes is probably too short and too long at the same time. Imagine we have a full layer derivation running that takes multiple hours. In that case we probably don't want to poll every 15 minutes because of course every check also consumes tokens and brings us closer to the usage limits. On the other hand, if we say okay we just check every hour, that means that if we have um work on the playground that just takes ten minutes, um nothing happens for the rest of the fifty minutes. So it's waste of time. Maybe this check can be dynamic based on an estimate how much work it is that needs to be done.

So I just talked about if or how that works from my perspective without even needing a pause. The question of course is is there a different case where we actually need a pause? So where the the work on the playground has to be paused from external or from the outer run. So the outer run has to do something else. So it pauses the inner run to resume it later. Currently I don't know a use case from the top of my head. But maybe you know one? If a pause of the inner run is needed, we could utilize the orchestrator mechanisms. Because I think all we have to do is to signal the inner orchestrator that it must stop. So we can send the stop signal. How that works is described in the auto-run skill. And once we want to resume we just start the orchestrator again.

So bottom line for me It looks much easier than you think. But maybe I am wrong. I did not read all the investigation....

# Rationale Captured

(Automated archival — no rationale extracted.)
