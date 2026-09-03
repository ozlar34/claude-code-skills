---
name: session-handoff
description: Generate a structured mid-session handoff block. Invoke proactively when remaining context drops to ~15% and meaningful task state would otherwise be lost; also on explicit /session-handoff. Persists to ~/.claude/handoffs/ and copies to clipboard so a fresh session can resume without losing state. Supports `--minimal` for a bare-bones block.
---

# Session Handoff

Mid-session reset. Distinct from: `/done` (end-of-day), `/gsd-pause-work` (active GSD phase — prefer that; see Step 2a), `/gsd-session-report` (retrospective telemetry). Use when context is hot, a `/clear` is needed, and conversation state isn't yet on disk.

**Autonomy note:** the description above triggers this skill automatically at ~15% remaining context, not just on explicit invocation. Prefer manual-only? Edit the `description:` frontmatter (line 3) to "Use only when the user explicitly invokes /session-handoff."

Persisted handoffs live at `~/.claude/handoffs/<currentDate>-<HHMM>.md`, with `latest.md` as a pinned copy. A SessionStart hook surfaces `latest.md` if <2h old, so the next session finds it automatically.

## Modes

- **default** — full structured handoff. Sections render only when they have content.
- **`--minimal`** — ~80-token bare-bones block: situation + next action + not-on-disk prose. Use when the user passes the flag explicitly.

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

Walk this checklist. Each bucket maps to a tag or section in the block:

- `[mcp]` **mcp-writes**: Notion/TickTick/NotebookLM/Actual Budget drafts not yet pushed → At-risk row
- `[vault]` **vault-writes**: Obsidian writes drafted in chat, not yet appended (CONTEXT.md, _decisions-log.md, hub, atomic note) → At-risk row
- `[memory]` **memory-pending**: durable rules/facts discussed but not yet written to their scoped home (root or subtree `CLAUDE.md`, or the relevant vault note) → At-risk row
- `[deferred]` **deferred**: Y from "do X then Y" still pending → At-risk row
- **decisions**: concrete choices locked this session → "Decisions locked" section
- **open-Qs**: decisions waiting on the user's input → "Open questions" section

### 2. Decide path

**2a. Active GSD phase? → delegate to `/gsd-pause-work` (if installed).**

Detection: `PLAN.md` exists in `.planning/phase-*/` but no `SUMMARY.md` in the same dir = phase active.

If yes, also check whether GSD is installed in this repo: `test -f ./.claude/get-shit-done/VERSION`.

- **GSD installed**: stop and output: "Active GSD phase at `<path>`. Use `/gsd-pause-work` (phase-aware, produces PAUSE.md) — or confirm to proceed with session-handoff." Don't continue until confirmed; don't silently produce a parallel handoff.
- **GSD not installed**: stop and output: "Active GSD phase detected at `<path>`, but GSD is not installed in this repo (`.claude/get-shit-done/VERSION` missing). Run `/gsd-install` to enable `/gsd-pause-work`, or confirm to proceed with session-handoff instead." Don't continue until confirmed.

**2b. Pick mode.**

- `--minimal` flag OR context monitor at critical → **minimal** (Step 3b)
- Otherwise → **default** (Step 3a)

### 3a. Write the handoff — default mode

Save via the **Write** tool to `~/.claude/handoffs/<currentDate>-<HHMM>.md` (e.g., `2026-04-26-2247.md`. `currentDate` from the session reminder, `HHMM` = `HH:MM` with the colon stripped).

Format below. **Sections with count = 0 are omitted entirely.** Situation, the `**Checked:**` line, and "Pick up from here" always render.

```
# Session Handoff — <currentDate> <HH:MM>

**CWD:** <absolute path>
**Project:** <project-name | ~/projects/<name> | GSD phase N | other>
**Git:** <branch>, <N> modified, <M> untracked, last commit <sha7> "<subject>"
**Checked:** decisions(<n>) at-risk(<n>) open-Qs(<n>)

## Situation (2–3 sentences)
<What user was trying to do; current state; why reset is needed>

## Decisions locked
<Concrete choices made>

## At-risk state
<Tagged rows. Each row: [tag] context: action needed.>
- [mcp] <what's drafted but not pushed>
- [vault] <write drafted in chat but not yet appended>
- [memory] <memory rule not yet saved>
- [deferred] <Y pending; what it needs>

## Open questions
<Decisions waiting on the user's input>

## Pick up from here
1. **Re-read first:** <absolute paths; include CONTEXT.md if vault state changed>
2. **Next action:** <one sentence — exact first task for the new session>
3. **Context not captured in files:** <anything in this conversation but nowhere on disk — prose>
```

### 3b. Write the handoff — minimal mode

Same path scheme as 3a. Optional `-min` suffix to distinguish.

Format — the three lines below, nothing more:

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
find ~/.claude/handoffs \( -name "????-??-??-????.md" -o -name "????-??-??-????-min.md" \) -mtime +10 -delete && \
echo "Saved → ~/.claude/handoffs/<filename>.md (latest.md updated, clipboard ready, >10d pruned)"
```

Confirm with one line. Do not re-emit the block in chat — it's in the Write tool result and on disk.

### 5. Stop

After the clipboard copy, STOP. Do not continue working. Do not ask "what next?" — the user will `/clear`. The next session's `SessionStart` hook will surface `latest.md` automatically (if <2h old); otherwise paste from clipboard or read the file.

## Style rules

- **One section per question.** "What isn't landed?" → at-risk. "What was decided?" → decisions. "What's blocked on the user?" → open-Qs. Don't fragment.
- **"Context not captured" / "Not on disk" is the most important field in either mode.** What did the user say in this conversation that isn't in any file?
- **Don't editorialize.** Next-session-you doesn't need commentary, just pointers.
- **Don't re-list files.** The `**Git:**` header line + `git status` in the next session beats any table.
