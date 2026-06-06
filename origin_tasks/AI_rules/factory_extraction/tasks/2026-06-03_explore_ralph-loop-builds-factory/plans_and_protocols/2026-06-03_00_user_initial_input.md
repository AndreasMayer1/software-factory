# User Initial Input — 2026-06-03

Read this as a seed bed, not a spec.

---

As initial seed I already have first idea how the software factory should look like after extraction.

all artifacts that are required by a project that uses the software factory must be present in the software factory project.

there are 3 personas: one is a solo developer (persona focus is team size and available time to work for the project; we need a broader term instead of developer, since in that setup this person is also doing project management, ux/ui design and so on), one is flutter user and the third is Claude code user. Yes those 3 match what is currently the case in the flutter app project. Should there only be one persona that combines all 3? I'm wondering how the extendability works then.

there must also be a persona that stands for the software factory providers. It contains things like serving as many divers personas with the software factory as possible, not causing harm with the product to no one and also not to the planet, making sure that the factory keeps slim even when it targets multiple team sizes, technologies, llm providers ect ( by providing different bundles?), making sure that multiple contributors can enhance the factory (by having a mechanism to collapse added personas into only a few?) And so on. This is of course similar to the app provider persona for the flutter
