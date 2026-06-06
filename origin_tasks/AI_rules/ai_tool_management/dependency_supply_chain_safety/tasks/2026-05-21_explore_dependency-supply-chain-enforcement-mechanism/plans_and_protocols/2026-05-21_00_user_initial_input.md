# User's Initial Input — REQ-PROC-056 Enforcement Exploration

> Verbatim, unedited. Captured 2026-05-21 at the moment the requirement was authored.
> Read as a seed bed, not a spec.

---

There are increasingly more security risks when installing packages. There have been a lot of injections into new packages, and I'm very afraid to install up to date packages because of that. The thing is that the LLM likes to install new packages without asking. And I want to make sure that there is a mechanism in place that prevents the LLM from installing packages or updates for packages that are very very new. For example, if you have a package that was released last week, it's likely that if there was a major security risk, that this is already fixed. But of course it can happen that the fix is from yesterday and the problematic version is seven days old and then you say okay I installed the old version and then you have the problem but yeah you it's very difficult to know okay which is the not infected version. So I think we need a mechanism where the LLM is actually researching which versions are safe. And it does not install versions that have known risks. And of course if the package is very very new or the release is very new like from yesterday no one might have had the time or the chance to actually find the problem or the security risk so it might still be unknown. So I never want to have updates for packages um that are newer than say one week.
I think we have to write a requirement for that and after that also create a implementation uh um exploration task that um is researching a solution how we can make sure that this uh can be uh prevented.

---

## Skill-flow clarifications captured during requirement authoring

- **Scope**: Code-runtime deps + dev tooling only (pubspec.yaml + Python deps in scripts/ + npm/uv used by skills). OS-level (apt/brew) excluded — those have distro-level review.
- **Age rule**: ≥ 7 days old, no exceptions in automation. User can override interactively.
- **Enforcement**: Decide in this exploration task — the requirement is WHAT-only.
- **Placement**: New category `ai_tool_management/dependency_supply_chain_safety/` (sibling of `codegraph_integration/`, `roo_code_deprecation/`).
