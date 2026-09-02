# learn-from-mistakes

**Trigger:** `/learn-from-mistakes` (user-invocable only — does not auto-trigger)

**What it does:** Runs at the end of a session and scans the conversation for
one class of failure: moments where Claude acted on a *wrong mental model* of
how your systems, tools, or conventions work and had to be corrected. The ones
that clear a high cost bar become one-line imperative directives, proposed as a
single batched approval before anything is written to a CLAUDE.md file.

The non-obvious thing this skill does is maintain a **very high bar for what gets
saved.** Every line added to an always-loaded CLAUDE.md is taxed on every future
session in every project, so the default outcome is "nothing cleared the bar" —
and that is success, not failure. Four design choices drive that:

- **Wrong beliefs only, not inefficiencies.** Loops, repeated greps, and
  "took more steps than needed" are clues, never findings. The skill asks
  whether a wrong belief sat underneath them; if so, the belief is the
  candidate. A generic "don't loop" or "search more efficiently" rule is
  bloat by definition and is never proposed.

- **Two gates, both required.** *Wrong-action gate:* without this rule, would
  Claude take a substantively wrong action next time, not merely a slower one?
  *Cost gate:* is this a durable fact about how your systems work, rather than
  syntax trivia that tooling already catches? Candidates already covered by an
  existing CLAUDE.md rule, or arising from one-off context, are dropped.

- **Directive format, not observations.** Only behavioral imperatives in the
  register of existing CLAUDE.md rules: `Before [action], [check X]` or
  `When [situation], [do this instead]`, one sentence, about 15 words.
  Final test: *if this exact sentence had been in CLAUDE.md at the start of
  the session, would it have prevented the wrong action?* Anything short of a
  clear yes is rewritten or dropped.

- **Routing by scope, with a demotion tier.** Survivors go to the narrowest
  CLAUDE.md that fits (project over global). A real but narrow tool quirk that
  fails the cost gate is appended to that tool's existing note instead of an
  always-loaded file — and if no such note exists, it is dropped rather than
  spawning a new "gotchas" file.

Corrections that patch *model behavior* (fabrication, over-defaulting to
optional, AI-writing tells) rather than a durable world-fact are stamped
`(model, date)` and logged to a Crutch Register so they get re-tested at the
next model release instead of living forever.

**Example:**

> Session contained: Claude called `grep` four times with different patterns
> before finding a symbol; the user had to correct Claude's assumption that a
> config path resolved against the current directory.
>
> Output:
>
> ```
> Found 2 candidates. Proposing 1.
>
> 1. [myproject/CLAUDE.md · Conventions]
>    → Before resolving a config path against cwd, read paths.json first.
>    Reason: this session edited the wrong file for ten minutes on that assumption.
>
> Dropped 1: grep loop (no wrong belief underneath).
>
> Approve all? (or: which numbers)
> ```

"Nothing cleared the bar this session." is the most common output, and the
right one for a clean session.
