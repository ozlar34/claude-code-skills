# session-handoff

**Trigger:** "/session-handoff", "save this session", "wrap up before clear"

**What it does:** Captures the live state of an in-flight session into a structured markdown block, writes it to `~/.claude/handoffs/<date>-<time>.md` and `~/.claude/handoffs/latest.md`, copies it to your clipboard, and stops. The next session — after `/clear` — can either auto-surface it via a SessionStart hook, or you paste from clipboard.

The non-obvious thing this skill does is the **cognitive scan**: not just `git status`, but a checklist that distinguishes decisions you made, MCP/external writes that haven't been pushed yet, memory rules the user asked you to save, deferred follow-ups, and open questions waiting on the user. That's what makes a handoff useful versus a glorified `git diff`.

A `--minimal` flag exists for emergency use when context is already critical — drops to ~80 tokens for the entire handoff.

**Setup:** see [SETUP.md](./SETUP.md). The skill works standalone; the optional auto-resume hook is one extra script.

**Example:**

> User: /session-handoff
>
> Skill: *(runs git/cwd/branch check, mentally walks the 5 buckets, writes block, pbcopy, pins latest.md)*
>
> ```
> Saved → ~/.claude/handoffs/2026-05-02-2247.md (latest.md updated, clipboard ready)
> ```
>
> User: /clear
>
> *(in fresh session)* Skill auto-resumes from latest.md if <2h old, otherwise paste from clipboard.

**Why it exists:** Long Claude Code sessions accumulate state — files modified, MCP writes drafted, memory rules discussed, decisions made — that lives in the conversation but not on disk. `/clear` is a hard reset; without a structured handoff, you lose all of it. With one, the new session resumes mid-stream with full context in ~one screen of markdown.

The skill exists separately from `/done` (end-of-day wrap-up) and any phase-specific pause tools (which are scoped to a single planning artifact). It's the cross-project handoff for "I need to clear, but I'm not done."

**Dependencies:**
- macOS `pbcopy` (or substitute `xclip` / `wl-copy` on Linux — edit Step 4)
- `~/.claude/handoffs/` directory (created on first use)
- (Optional) SessionStart hook for auto-resume — see SETUP.md
