---
name: learn-from-mistakes
description: Run at the end of a session to extract generalizable failure patterns and propose surgical CLAUDE.md additions that prevent the same mistakes in future sessions. User-invocable only (via /learn-from-mistakes); does not auto-trigger. Distinct from /handoff (which captures project state) — this skill captures behavioral corrections, not work state.
---

# Learn From Mistakes

Scan this session's conversation history for failure patterns. Translate generalizable ones into concise imperative directives. Propose them for the user's approval before writing anything.

## Step 1 — Identify failure patterns

Scan the full conversation history for these signatures:

**Loops** — the same tool or approach was tried multiple times with minor variations before succeeding. Look for repeated Bash/Read/Edit calls on the same target, Claude proposing the same solution twice, or a multi-step sequence that was abandoned and restarted.

**Corrected assumptions** — the user had to explicitly correct something Claude got wrong. Signals: "no, actually...", "that's not how it works here", "you assumed...", "that's wrong because...", or any turn where the user negated or redirected Claude's previous assertion or action.

**Avoidable extra steps** — a task that required significantly more tool calls or turns than its complexity warranted, where the excess traces to a wrong first move (wrong file looked at first, wrong tool chosen, wrong mental model of the system).

For each pattern, note: what happened, what the correct behavior would have been, and whether it arose from a bad assumption, a missing check, or a wrong tool choice.

## Step 2 — Filter: generalizable vs situational

For each pattern, ask: **would this exact mistake plausibly recur in a different session on a different day?**

Keep if yes. Drop if:
- It was caused by genuinely ambiguous or one-off context (a file that's since been deleted, a confused user prompt that got clarified)
- It's already covered by an existing rule in any CLAUDE.md
- You're not confident it generalizes — err on the side of dropping

A small set of high-signal directives is worth more than a long list of marginal ones.

## Step 3 — Translate to directives

For each surviving pattern, write one short imperative directive in the style of existing CLAUDE.md rules:

- Format: `Before [action], [check/verify something]` or `When [situation], [do this instead]`
- Length: one sentence, 15 words max ideally
- Voice: imperative, behavioral — what Claude should DO, not what Claude should know
- No observations ("Claude sometimes assumes X") — only directives ("Before assuming X, check Y")

**Examples of the right style:**
- `Before assuming a path resolves against cwd, check vault-paths.json first.`
- `Before modifying a function, grep all callers.`
- `When the same command fails twice, read the error output fully before retrying.`

**Quality gate:** Ask yourself — *if this exact sentence had been in CLAUDE.md at the start of this session, would it have prevented the mistake?* If the answer is anything other than a clear yes, rewrite or drop.

## Step 4 — Route each directive

Decide where each directive belongs:

- **~/.claude/CLAUDE.md** — universal behavioral rules that apply regardless of project (a wrong assumption about how Claude Code works, a general tool-use mistake, a reasoning pattern to avoid)
- **[project]/CLAUDE.md** — patterns specific to this project's structure, conventions, or tools (a wrong assumption about vault paths, a project-specific workflow)
- **Vault Tool Note** — if the mistake is about a specific tool's behavior, flag it as "suggest adding to Tool Notes for [tool]" rather than writing directly (Tool Notes are in the vault, outside this skill's write scope)

When in doubt between global and project-level, choose project-level — narrower scope is safer.

## Step 5 — Present for review

For each proposed directive, show:

```
[~/.claude/CLAUDE.md · Coding discipline section]

  existing rule above...
→ NEW: Before assuming X, verify Y.
  existing rule below...

Reason: [one sentence — what happened in this session that this prevents]
```

Group by target file. List how many total directives you found vs. how many you're proposing (this signals you applied the filter).

If you found no generalizable patterns, say so directly. That's a valid and good outcome.

## Step 6 — Write approved items

Write only what the user explicitly approves. Use Edit, not Write — insert the directive into the right section of the target file without disturbing surrounding content.

Report in the end-of-turn summary: how many directives were proposed, how many approved, and which files were modified.
