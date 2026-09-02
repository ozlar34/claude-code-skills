# Setup — learn-from-mistakes

## 1. Install

```bash
cp -r learn-from-mistakes ~/.claude/skills/
```

No dependencies, no API keys, no external tools required. The skill reads the
current conversation history (already in context) and writes to local CLAUDE.md
files using the Edit tool.

Restart Claude Code or open a new session, then run `/learn-from-mistakes` at the
end of any working session.

## 2. Adapt the routing logic to your setup

`SKILL.md` Step 3 routes each survivor to one of three places: global CLAUDE.md,
project-level CLAUDE.md, or (Tier-B) an existing tool note for narrow quirks that
fail the cost gate.

Tier-B assumes an Obsidian vault with a `_System/Tool Notes/` structure and an
`obsidian-write` skill for appends. If you do not use this setup, edit Step 3 and
the Tier-B write line in Step 5 to point at wherever tool-specific notes live in
your system, or remove Tier-B and route everything to global or project-level.

Step 4 also stamps model-behavior corrections `(model, date)` and Step 5 appends
a row to a "Crutch Register" table in a vault note. If you do not keep such a
register, delete those two paragraphs; the rest of the skill does not depend on
them.

## 3. Note on when to run it

Run this skill at the end of sessions that involved real implementation work —
debugging, file editing, system navigation. Discussion-only sessions rarely
produce wrong-model failures worth capturing, and the skill will correctly
report "Nothing cleared the bar this session."

The signal-to-noise ratio is better if you run it selectively rather than after
every session.

## 4. Note on invocation

The skill is **user-invocable only** — it will not auto-trigger based on
natural-language matches. That is intentional: retrospective analysis should be
an opt-in ritual, not something that fires automatically when a session winds down.

## 5. Evals

`evals/evals.json` holds three simulated-session cases (one clean session, one
mixed, one with four candidates of which two should survive) describing the
exact expected output shape. Use them to check the skill still behaves after you
adapt it.
