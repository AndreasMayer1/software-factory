# User Initial Input

> Raw seed input from the developer that prompted this exploration.
> Read it as a seed bed, not a spec.

---

When an AI agent changes a script/skill/hook/dart code/devcontainer to do Z instead of Y,
the old behaviour Y is maybe also stated in a requirement and needs to be updated as well.
We need a rule to enforce this — but it's not easy because it applies to potentially all
file writes (except requ and task writes and some other exceptions of course).

The WHAT is now defined in REQ-PROC-064. This task is about designing the HOW:
how does the enforcement mechanism actually work across all artifact types without
becoming unworkable or creating noise?
