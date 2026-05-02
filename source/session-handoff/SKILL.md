---
name: session-handoff
description: Generate a structured mid-session handoff block when context grows hot. Persists to ~/.claude/handoffs/ and copies to clipboard so a fresh session can resume without losing state. Supports `--minimal` for ~80-token emergency mode when context is already critical.
---

# Session Handoff

Mid-session reset tool. Use **session-handoff** when context is hot, work is mid-stream, a `/clear` is needed but the conversation holds state that isn't yet on disk.

## Auto-resume

Handoffs are persisted to `~/.claude/handoffs/<currentDate>-<HHMM>.md` and pinned to `~/.claude/handoffs/latest.md`. A `SessionStart` hook can surface the latest handoff at the start of a new session — see the optional setup below.

## Modes

- **default** — full structured handoff. Sections render only when they have content.
- **`--minimal`** — ~80-token bare-bones block: situation + next action + not-on-disk prose. Use when:
  - The user passes the flag explicitly, OR
  - Context is genuinely critical (≤25% remaining) — at that point even the regular block is too expensive. Recommend minimal in one line and let the user confirm.

## Steps

### 1. Gather evidence

Two parts, parallel where independent.

**Disk side — one Bash call:**

```bash
mkdir -p ~/.claude/handoffs && \
echo "=== time ===" && date "+%H:%M" && \
echo "=== cwd ===" && pwd && \
echo "=== git ===" && git status --short 2>/dev/null && git log -5 --oneline 2>/dev/null && git diff --stat HEAD 2>/dev/null
```

The date (`YYYY-MM-DD`) comes from the session reminder — don't shell out for it. Only the wall-clock `HH:MM` needs `date`.

**Conversation side — the cognitive step. This is the value of the handoff.**

Walk this checklist explicitly. Each bucket maps to a tag or section in the block:

| # | Bucket | Renders as |
|---|---|---|
| 1 | **decisions** — concrete choices locked this session | "Decisions locked" section |
| 2 | **mcp-writes** — external writes still in flight (Notion / Linear / Slack drafts not pushed) | At-risk row, tag `[mcp]` |
| 3 | **memory-pending** — memory writes the user asked for but NOT yet saved | At-risk row, tag `[memory]` |
| 4 | **open-Qs** — user-facing decisions waiting on the user's input | "Open questions" section |
| 5 | **deferred** — "do X then Y" — X done, Y still pending | At-risk row, tag `[deferred]` |

Optional 6th tag: `[draft]` — a tool call composed but not yet committed (rare; use only when relevant).

If you skip this scan, the handoff is just a `git status` paraphrase — useless.

### 2. Pick mode

- `--minimal` flag OR context is critical → **minimal** (Step 3b)
- Otherwise → **default** (Step 3a)

### 3a. Write the handoff — default mode

Use the **Write** tool to save to:

```
~/.claude/handoffs/<currentDate>-<HHMM>.md
```

(e.g., `2026-04-26-2247.md`. `currentDate` from the session reminder, `HHMM` = `HH:MM` with the colon stripped.)

Format below. **Sections with count = 0 are omitted entirely.** Situation, the `**Checked:**` line, and "Pick up from here" always render.

```
# Session Handoff — <currentDate> <HH:MM>

**CWD:** <absolute path>
**Project:** <project name>
**Git:** <branch>, <N> modified, <M> untracked, last commit <sha7> "<subject>"
**Checked:** decisions(<n>) at-risk(<n>) open-Qs(<n>)

## Situation (2–3 sentences)
<What user was trying to do; current state; why reset is needed>

## Decisions locked            ← only if decisions > 0
<Concrete choices made>

## At-risk state               ← only if at-risk > 0
<Tagged rows. Each row: [tag] context: action needed.>
- [mcp] <Notion / Linear / Slack — what's drafted but not pushed>
- [memory] <memory rule discussed but not saved>
- [deferred] <Y from "do X then Y" still pending; what it needs>
- [draft] <in-flight tool call not yet committed — rare>

## Open questions              ← only if open-Qs > 0
<Decisions waiting on user's input>

## Pick up from here
1. **Re-read first:** <absolute paths — scratch notes, modified files>
2. **Next action:** <one sentence — exact first task for the new session>
3. **Context not captured in files:** <anything in this conversation but nowhere on disk — prose>
```

Why one "At-risk state" instead of three sections? `mcp-writes`, `memory-pending`, and `deferred instructions` all answer the same question — *what isn't fully landed?* One mental model for the reader, one section to scan, tags reveal the category.

### 3b. Write the handoff — minimal mode

Same path scheme: `~/.claude/handoffs/<currentDate>-<HHMM>.md`. Optional `-min` suffix to distinguish.

Format — keep under ~80 tokens:

```
# Session Handoff (minimal) — <currentDate> <HH:MM>
**CWD:** <abs path> | **Git:** <branch>, +<N>

**Situation:** <1 sentence — what was happening, why reset>
**Next action:** <1 sentence — exact first task>
**Not on disk:** <1–3 sentences of prose — the state that ONLY this conversation knows>
```

No tables, no Checked line, no section headers beyond the three bold labels.

### 4. Push to clipboard and pin as latest

One Bash call:

```bash
pbcopy < ~/.claude/handoffs/<filename>.md && \
cp ~/.claude/handoffs/<filename>.md ~/.claude/handoffs/latest.md && \
echo "Saved → ~/.claude/handoffs/<filename>.md (latest.md updated, clipboard ready)"
```

Confirm with one line. Do not re-emit the block in chat — it's in the Write tool result and on disk.

### 5. Stop

After the clipboard copy, STOP. Do not continue working. Do not ask "what next?" — the user will `/clear`. Either the SessionStart hook surfaces `latest.md` automatically (if installed), or the user pastes from clipboard.

## Style rules

- **Disk first, clipboard second.** `~/.claude/handoffs/latest.md` is the canonical record; clipboard is the fast path. If clipboard is lost, the file isn't.
- **Paths absolute, not relative.** The next session may have a different CWD or none at all.
- **Render only what has content.** The `**Checked:**` line is the audit trail. Empty sections cost tokens for no info.
- **One section per question.** "What isn't landed?" → at-risk. "What was decided?" → decisions. "What's blocked on the user?" → open-Qs. Don't fragment.
- **"Context not captured" / "Not on disk"** — the most important field in either mode. What did the user say in this conversation that isn't in any file?
- **Don't editorialize.** Next-session-you doesn't need commentary, just pointers.
- **Don't shell out for the date.** Use `currentDate` from the session reminder; only `HH:MM` needs `date`.

## Optional: SessionStart auto-resume hook

To make the next session automatically know there's a recent handoff, add this to your hooks config — it surfaces `latest.md` if it's <2 hours old. See [SETUP.md](./SETUP.md) for the hook script.
