# learn-from-mistakes

**Trigger:** `/learn-from-mistakes` (user-invocable only — does not auto-trigger)

**What it does:** Runs at the end of a session to scan the conversation history
for failure patterns — loops, corrected assumptions, avoidable extra steps —
translates the generalizable ones into concise imperative directives, and proposes
them for your approval before writing anything to a CLAUDE.md file.

The non-obvious thing this skill does is maintain a **very high bar for what gets
saved.** Most end-of-session retrospective tools produce noise; this one aims
to produce one or two high-signal directives per session, or nothing at all.
Three design choices drive that:

- **Directive format, not observations.** The skill refuses to write reflections
  like "Claude sometimes assumes X." It only writes behavioral imperatives — the
  same register as existing CLAUDE.md rules — because those are what actually
  change future behavior. Every candidate is tested against a quality gate: *if
  this exact sentence had been in CLAUDE.md at the start of this session, would it
  have prevented the mistake?* If the answer is not a clear yes, the candidate is
  dropped.

- **Generalizability filter.** A mistake that happened because of one-off context
  (a deleted file, a user typo, an ambiguous prompt) is dropped. The skill only
  proposes directives for patterns that would plausibly recur in a different
  session on a different day.

- **Routing by scope.** Directives go to the most specific CLAUDE.md file relevant
  to where the mistake would recur — global (`~/.claude/CLAUDE.md`) for universal
  behavioral rules, project-level for project-specific patterns. Narrower scope is
  always safer.

**Example:**

> Session contained: Claude called `grep` four times with different patterns before
> finding a symbol; user had to correct Claude's assumption that paths resolve
> against cwd.
>
> Skill surfaces two candidates:
> 1. `When the same grep fails twice, try searching from the repo root before varying the pattern.` → routes to `~/.claude/CLAUDE.md`
> 2. `Before assuming a path resolves against cwd, check vault-paths.json first.` → routes to `myproject/CLAUDE.md`
>
> User approves #2, drops #1. Skill writes one line to `myproject/CLAUDE.md`
> and reports what was modified.

"No generalizable patterns found" is a valid and good outcome — it means the
session was clean, not that the skill failed.

