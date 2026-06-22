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

`SKILL.md` Step 4 describes three routing destinations: global CLAUDE.md,
project-level CLAUDE.md, and a "Vault Tool Note" flag for tool-specific patterns.

The third destination assumes an Obsidian vault with a `_System/Tool Notes/`
structure. If you do not use this setup, edit Step 4 to reflect where tool-specific
notes live in your system — or simply remove that option and route everything to
global or project-level.

## 3. Note on when to run it

Run this skill at the end of sessions that involved real implementation work —
debugging, file editing, system navigation. Discussion-only sessions (brainstorming,
planning, talking through ideas) rarely produce failure patterns worth capturing,
and the skill will correctly report "no generalizable patterns found."

The signal-to-noise ratio is better if you run it selectively rather than after
every session.

## 4. Note on invocation

The skill is **user-invocable only** — it will not auto-trigger based on
natural-language matches. That is intentional: retrospective analysis should be
an opt-in ritual, not something that fires automatically when a session winds down.

