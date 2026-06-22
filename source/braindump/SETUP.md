# Setup — braindump

## 1. Install

```bash
cp -r braindump ~/.claude/skills/
```

That's it. No dependencies, no API keys, no config to fill in. The skill is pure
conversational logic — it writes nothing to disk and calls no external tools
(other than `AskUserQuestion`, which ships with Claude Code).

Restart Claude Code (or open a new session) and run `/braindump` to start.

## 2. (Optional) Tune the neighbor boundaries

`SKILL.md` ends with a **Boundaries with neighbors** section that keeps braindump
from overlapping two adjacent workflows: an adversarial plan stress-test and a
build-this-now spec session. The skill describes those neighbors generically — it
does **not** assume you have skills for them.

If you *do* have such skills (e.g. a "grill-me" stress-test or a "brainstorming"
spec skill), edit that section to name them explicitly. Sharper boundaries make
all three trigger more precisely. If you don't, leave it as is — the generic
framing still does its job.

## 3. Note on invocation

The skill's frontmatter marks it **user-invocable only** — it won't auto-trigger
on natural-language matches, only when you type `/braindump`. That's deliberate:
an open-ended thinking session is something you opt into, not something a passing
mention of "I have an idea" should launch. Keep it that way unless you want the
opposite.
