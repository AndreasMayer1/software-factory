# User initial input (verbatim seed) — 2026-06-03

Captured from the design conversation that prompted this task. Lightly trimmed to the
user's own words; read as a seed bed, not a spec.

---

> The script scans `lib/`, `test/`, and `integration_test/` for import statements […]
> Are those folders enough for the usage check?

> And we also have the dependencies that are implemented in C++?

> do you see other things we could improve for this dependency retirement check.

> is there a false positive recovery path?

> "So a false positive can't hurt you — a human says 'keep' and it survives."
> That means the human then has to search in the code base if this requirement is still
> needed. Maybe a better approach would be to also have a recovery in case the human
> approves it. And then it gets removed. I mean once you remove the dependency and you
> run the tests, you probably directly see that the removal broke it. So I guess the
> procedure to remove a dependency would be to first run the tests and after that remove
> it and then run the tests again. If the tests fail because the dependency is missing,
> revert with git. One problem with that approach is that the c++ dependencies are not
> testable on the developer's machine. Currently we have a build process in GitHub that
> runs the Windows tests, for example, to test the native Windows libraries. Once we have
> Apple support, we have the same problem there. Same is of course true for native
> Android dependencies.

> capture this as the design for the follow-up task together with the other things.
