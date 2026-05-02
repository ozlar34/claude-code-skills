# Setup — session-handoff

## 1. Install

```bash
cp -r session-handoff ~/.claude/skills/
mkdir -p ~/.claude/handoffs
```

That's the minimum. Trigger with `/session-handoff` and the skill writes to disk + clipboard.

## 2. (Linux only) Replace `pbcopy`

Step 4 of `SKILL.md` uses macOS `pbcopy`. If you're on Linux, swap one line:

```diff
- pbcopy < ~/.claude/handoffs/<filename>.md && \
+ xclip -selection clipboard < ~/.claude/handoffs/<filename>.md && \
```

Or use `wl-copy` on Wayland.

## 3. (Optional) Auto-resume hook

To make the *next* session automatically tell Claude there's a recent handoff, add a `SessionStart` hook.

Create `~/.claude/hooks/handoff-resume-prompt.sh`:

```bash
#!/usr/bin/env bash
# SessionStart hook: surface ~/.claude/handoffs/latest.md if it's <2h old
LATEST=~/.claude/handoffs/latest.md
[ -f "$LATEST" ] || exit 0

# How old is it?
AGE_SECONDS=$(($(date +%s) - $(stat -f %m "$LATEST" 2>/dev/null || stat -c %Y "$LATEST")))
[ "$AGE_SECONDS" -gt 7200 ] && exit 0  # >2h, skip

cat <<EOF
## Session Handoff Available

A recent handoff exists at \`~/.claude/handoffs/latest.md\` (saved $((AGE_SECONDS / 60)) minutes ago).
Read it to resume mid-stream work.
EOF
```

Make it executable:

```bash
chmod +x ~/.claude/hooks/handoff-resume-prompt.sh
```

Wire it into Claude Code by adding to your `~/.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/handoff-resume-prompt.sh"
          }
        ]
      }
    ]
  }
}
```

If you already have other hooks, merge instead of overwrite.

After this, every new session that starts within 2 hours of a handoff will see the prompt.

## 4. Restart Claude Code and try it

Mid-session, run `/session-handoff`. Verify:

- `~/.claude/handoffs/<today>-<HHMM>.md` exists and looks structured
- `~/.claude/handoffs/latest.md` matches
- Clipboard has the same content (paste anywhere to verify)

Then `/clear` and start a new session within 2 hours — the hook (if installed) should surface the handoff. Otherwise paste from clipboard.

## What's NOT included

- The original version of this skill detected and deferred to a `gsd-pause-work` command for active planning phases. Stripped here — most users won't have GSD installed. If you do, add a Step 2a back manually.

## Dependencies

- macOS `pbcopy` (or Linux equivalent)
- Claude Code's native `Write` and `Bash` tools (default)
- (Optional) Hook script for auto-resume — pure shell, no extra runtime
