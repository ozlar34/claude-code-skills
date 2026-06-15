---
name: session-handoff
description: Generate a structured mid-session handoff block when context grows hot (~120k tokens on Opus 1M, ~60% on 200k models). Use when the user invokes /session-handoff, or proactively suggest when context monitor warns and work is mid-stream. Persists to ~/.claude/handoffs/ and copies to clipboard so a fresh session can resume without losing state. Supports `--minimal` for ~80-token emergency mode when context is already critical.
---

# Session Handoff

Mid-session reset tool. Distinct from:
- `/done` — end-of-session wrap-up (closing for the day)
- `/gsd-pause-work` — GSD-phase-specific checkpoint (preferred when a `.planning/` phase is active; see Step 2a)
- `/gsd-session-report` — retrospective telemetry

Use **session-handoff** when: context is hot, work is mid-stream, a `/clear` is needed but the conversation holds state that isn't yet on disk.

Persisted handoffs live at `~/.claude/handoffs/<currentDate>-<HHMM>.md`, with `latest.md` as a pinned copy. A SessionStart hook surfaces `latest.md` if <2h old, so the next session finds it automatically.

## Modes

- **default** — full structured handoff. Sections render only when they have content.
- **`--minimal`** — ~80-token bare-bones block: situation + next action + not-on-disk prose. Use when:
  - The user passes the flag explicitly, OR
  - the context monitor is at "critical" (≤25% remaining) — at that point, even the regular block is too expensive. Recommend minimal in one line and let the user confirm.

## Steps

### 1. Gather evidence

Two parts, parallel where independent.

**Disk side — one Bash call:**

```bash
mkdir -p ~/.claude/handoffs && \
echo "=== time ===" && date "+%H:%M" && \
echo "=== cwd ===" && pwd && \
echo "=== git ===" && git status --short 2>/dev/null && git log -5 --oneline 2>/dev/null && git diff --stat HEAD 2>/dev/null && \
echo "=== planning ===" && (ls .planning/phase-*/PLAN.md .planning/phase-*/SUMMARY.md 2>/dev/null | tail -10 || echo "no .planning")
```

The date (`YYYY-MM-DD`) comes from `currentDate` in the session reminder — don't shell out for it. Only the wall-clock `HH:MM` needs `date`.

**Conversation side — the cognitive step. This is the value of the handoff.**

Walk this checklist explicitly. Each bucket maps to a tag or section in the block:

| # | Bucket | Renders as |
|---|---|---|
| 1 | **decisions** — concrete choices locked this session | "Decisions locked" section |
| 2 | **mcp-writes** — external writes still in flight (Notion / TickTick / NotebookLM / Actual Budget drafts not pushed) | At-risk row, tag `[mcp]` |
| 3 | **vault-writes** — Obsidian vault writes drafted in chat but not yet appended/created (direct `Write`, `obsidian-write`, or content destined for `CONTEXT.md` / `_decisions-log.md` / a hub / an atomic note) | At-risk row, tag `[vault]` |
| 4 | **memory-pending** — memory writes the user asked for but NOT yet saved to `MEMORY.md` or memory files | At-risk row, tag `[memory]` |
| 5 | **open-Qs** — user-facing decisions waiting on the user's input | "Open questions" section |
| 6 | **deferred** — "do X then Y" — X done, Y still pending | At-risk row, tag `[deferred]` |

If you skip this scan, the handoff is just a `git status` paraphrase — useless.

### 2. Decide path

**2a. Active GSD phase? → delegate to `/gsd-pause-work`.**

Detection from Step 1's `=== planning ===` block: a `.planning/phase-*/PLAN.md` exists and the same directory has no `SUMMARY.md` (= phase active, not yet completed).

If yes, stop. Output one line:

> "Active GSD phase detected at `<path>`. `/gsd-pause-work` is phase-aware and produces `PAUSE.md` that integrates with the GSD resume flow. Use that instead, or confirm to proceed with session-handoff anyway."

Wait for confirmation. Don't silently produce a parallel handoff that competes with `PAUSE.md`. If the user says "proceed anyway" (e.g., for a generic cross-project handoff), continue.

**2b. Pick mode.**

- `--minimal` flag OR context monitor at critical → **minimal** (Step 3b)
- Otherwise → **default** (Step 3a)

### 3a. Write the handoff — default mode

Save via the **Write** tool to `~/.claude/handoffs/<currentDate>-<HHMM>.md` (e.g., `2026-04-26-2247.md`. `currentDate` from the session reminder, `HHMM` = `HH:MM` with the colon stripped).

Format below. **Sections with count = 0 are omitted entirely.** Situation, the `**Checked:**` line, and "Pick up from here" always render.

```
# Session Handoff — <currentDate> <HH:MM>

**CWD:** <absolute path>
**Project:** <<project> | ~/projects/<name> | GSD phase N | other>
**Git:** <branch>, <N> modified, <M> untracked, last commit <sha7> "<subject>"
**Checked:** decisions(<n>) at-risk(<n>) open-Qs(<n>)

## Situation (2–3 sentences)
<What user was trying to do; current state; why reset is needed>

## Decisions locked
<Concrete choices made>

## At-risk state
<Tagged rows. Each row: [tag] context: action needed.>
- [mcp] <Notion / TickTick / NotebookLM / Actual Budget — what's drafted but not pushed>
- [vault] <Obsidian write drafted in chat but not yet appended — CONTEXT.md / _decisions-log.md / hub / atomic note>
- [memory] <memory rule discussed but not saved>
- [deferred] <Y from "do X then Y" still pending; what it needs>

## Open questions
<Decisions waiting on the user's input>

## Pick up from here
1. **Re-read first:** <absolute paths — GSD phase files, scratch notes, CLAUDE.md additions, modified vault notes. If the session touched vault state, include `CONTEXT.md` and/or `_Dashboard/_decisions-log.md` explicitly — they're the canonical state surfaces, easy to forget.>
2. **Next action:** <one sentence — exact first task for the new session>
3. **Context not captured in files:** <anything in this conversation but nowhere on disk — prose>
```

### 3b. Write the handoff — minimal mode

Same path scheme as 3a. Optional `-min` suffix to distinguish.

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

One Bash call (substitute `<filename>` with the file written in Step 3):

```bash
pbcopy < ~/.claude/handoffs/<filename>.md && \
cp ~/.claude/handoffs/<filename>.md ~/.claude/handoffs/latest.md && \
echo "Saved → ~/.claude/handoffs/<filename>.md (latest.md updated, clipboard ready)"
```

Confirm with one line. Do not re-emit the block in chat — it's in the Write tool result and on disk.

### 5. Stop

After the clipboard copy, STOP. Do not continue working. Do not ask "what next?" — the user will `/clear`. The next session's `SessionStart` hook will surface `latest.md` automatically (if <2h old); otherwise paste from clipboard or read the file.

## Style rules

- **Disk first, clipboard second.** `latest.md` is the canonical record; clipboard is the fast path. If clipboard is lost, the file isn't.
- **Paths absolute, not relative.** The next session may have a different CWD or none at all.
- **Render only what has content.** The `**Checked:**` line is the audit trail. Empty sections cost tokens for no info.
- **One section per question.** "What isn't landed?" → at-risk. "What was decided?" → decisions. "What's blocked on the user?" → open-Qs. Don't fragment.
- **"Context not captured" / "Not on disk" is the most important field in either mode.** What was said in this conversation that isn't in any file?
- **Don't editorialize.** Next-session-you doesn't need commentary, just pointers.
- **Don't re-list files.** The `**Git:**` header line + `git status` in the next session beats any table.
