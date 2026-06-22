# braindump

**Trigger:** `/braindump` (user-invocable only — does not auto-trigger)

**What it does:** Develops a raw, half-formed idea through adaptive,
one-question-at-a-time dialogue until it's clear *what the idea actually is*,
*what could be done with it*, and *what the smallest next step would be*. It is
collaborative, not adversarial — and it writes nothing.

The non-obvious thing this skill does is **scale its depth to the idea instead of
running a fixed checklist.** A passing thought gets one or two clarifying
questions and a name for what it might be, then it stops — no manufactured depth.
An idea with legs gets developed further, one question at a time, across only the
dimensions it actually needs. Two more design choices make the difference:

- **Best-guess scaffolding.** Every question leads with the skill's own guess as
  a starting point, because the user's hardest moment with a fleeting idea is
  *activation*, not continuation. A blank wall of questions kills a half-formed
  idea; something to push against develops it.
- **Prose by default, widget for forks.** Most questions are open-ended prose
  (which invites the messy elaboration that grows an idea). Only when a question
  genuinely reduces to 2–4 mutually-exclusive options does it switch to a
  chip-picker — a picker on an open prompt would short-circuit the thinking.

**Example:**

> User: /braindump — I keep thinking about a tiny tool that renames my screenshots
>
> Skill: *(one question, with a guess)* My read: the real itch isn't renaming, it's
> that screenshots pile up unsearchable. Is the pain finding an old one later, or
> the mess in the folder right now?
>
> User: finding them later, definitely
>
> Skill: *(goes one level deeper, since it has legs)* Then the leverage is content,
> not filenames — OCR the text in the shot and make it searchable. Smallest version:
> a folder action that runs OCR and drops the text into a sidecar file. Want the
> next step to be "spike the OCR step on one screenshot" or "check if Spotlight
> already indexes this"?
>
> *(…continues until the idea resolves or the user says "that's enough." Writes nothing.)*

**Why it exists:** A fleeting idea is fragile. Open a blank doc and it evaporates;
hand it to a build-this-now spec session and you commit before you understand it;
hand it to an adversarial stress-test and you kill it before it can breathe.
braindump is the missing upstream step — a low-friction thinking partner that
develops the idea just far enough to decide whether it's worth keeping, and leaves
the decision to keep it entirely to you.

**What it deliberately does NOT do:** write a note, create a task, or save a file.
The output *is* the thinking. At most, once, at the very end, it offers a one-line
handoff ("want me to capture this somewhere?") — an offer, never a push.

**Dependencies:** none. Pure conversational logic + `AskUserQuestion` (built into
Claude Code). See [SETUP.md](./SETUP.md).
