# Setup — second-opinion

## 1. Install

```bash
cp -r second-opinion ~/.claude/skills/
```

No API keys, no external dependencies, no config to fill in. The skill uses the
**Agent tool** (ships built-in with Claude Code) to spawn one Opus sub-agent. That
is the only tool it requires — everything else is conversational logic.

Restart Claude Code (or open a new session) and run `/second-opinion` to invoke it.

## 2. Cost note

Each invocation spawns one Opus sub-agent. Opus is more capable — and more expensive
— than a standard Sonnet turn. That is the point: you are paying for a sharper,
independent audit of a claim that actually matters. The skill is designed to be used
*on demand* from a cheaper session (e.g. Sonnet) when a specific assertion is
load-bearing enough to warrant it — not as a routine step on every claim.

## 3. Note on invocation

The skill's frontmatter marks it **user-invocable only** — it won't auto-trigger
on natural-language matches, only when you explicitly type `/second-opinion`. That's
deliberate: spawning an Opus sub-agent on a random mention of "verify this" would
be noisy and expensive. Keep it opt-in unless you want the opposite.

## 4. (Optional) Wire it to a neighboring skill

If you have a "grill me" or adversarial stress-test skill, you can reference it by
name in the `SKILL.md` body's step 4 grill offer ("Want me to grill this out with
Opus…"). The generic wording works as-is; naming the neighbor sharpens the handoff
if you have one.
