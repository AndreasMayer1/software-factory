# User initial input (verbatim) — whole-factory-deploy AC

Captured 2026-07-01 during the orchestration-chain planning session. Unedited developer statements.

---

On decoupling from REQ-PROC-066 and not enumerating the factory in a requirement:

> REQ-PROC-066 factory extraction is much more than just extracting, it's also building artifacts in the
> new factory project. the extraction is the easiest part. could we just do that without REQ-PROC-066? of
> course the extraction solution we find now before REQ-PROC-066 can be consumed by REQ-PROC-066. or has
> that disadvantages?
> one thing: we don't necessarily need to write requirements that explain to details of which
> files/artifacts belong to the factory to do that, and i think it would be bad to do it. we can just have
> a ac that states that the whole factory needs to be deployed. what the factory is, will be defined once
> the factory exists as independend project: everything that is perovided by that. but we could already
> create a task in the scope of skill playground that does a implementation without having the factory as a
> dedicated project. after the extraction there might be another task needed to then switch that
> implementation to just use everything what the factory provides (whatever that is) - what the factory
> provides can change in the future and must not be defined anywhere outside of the factory, once it is a
> dedicated project.

On the exclude-list refinement (this belongs to the IMPLEMENTATION task T-B, not to this AC):

> Approved with a little change: also not part of the factory (not a complete list): [.codegraph,
> .dart_tool, .idea, .roo_archive, .vscode, .VSCodeCounter, android, assets, build, coverage, doc-temp,
> all folders between doc-temp and packages alphabetically, test folders, temp folder, web folder, windows
> folder]

---

Bottom line for THIS task: author ONE intent-level AC ("the whole factory is deployed such that a
contained child can run any factory skill"), with NO file/artifact enumeration. The exclude list above is
implementation guidance for the downstream deploy task (T-B), captured in the orchestration-chain plan; it
must not enter the requirement.
