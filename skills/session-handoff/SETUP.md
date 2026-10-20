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

The hook lists every dated handoff from the last 2 hours, each with its one-line situation, rather than just pointing at `latest.md`. `latest.md` is a single slot the last writer wins, so if you run parallel sessions it can hold the *other* session's handoff; the list lets the new session pick the right one.

It also prunes dated handoffs older than 10 days. That lives in the hook rather than the skill because a hook's shell isn't a tool call, so the delete never triggers a permission prompt mid-handoff. (Without the hook, nothing prunes; clear out `~/.claude/handoffs/` by hand now and then.)

Create `~/.claude/hooks/handoff-resume-prompt.sh`:

```bash
#!/usr/bin/env bash
# SessionStart hook: list fresh (<2h) dated handoffs, prune ones >10d old.
DIR="$HOME/.claude/handoffs"
[ -d "$DIR" ] || exit 0
find "$DIR" \( -name "????-??-??-????.md" -o -name "????-??-??-????-min.md" \) -mtime +10 -delete 2>/dev/null
NOW=$(date +%s)
ROWS=()

for f in $(ls -t "$DIR"/[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9].md 2>/dev/null); do
  MTIME=$(stat -f %m "$f" 2>/dev/null || stat -c %Y "$f" 2>/dev/null) || continue
  AGE=$((NOW - MTIME))
  [ "$AGE" -lt 7200 ] || break   # ls -t is newest-first, so the rest are older
  # First sentence of the Situation section, capped at 160 chars.
  SIT=$(awk '/^## Situation/{getline; while ($0=="") getline; print; exit}' "$f" \
        | sed -E 's/\. .*/./' | cut -c1-160)
  ROWS+=("- \`~/.claude/handoffs/$(basename "$f")\` ($((AGE / 60)) min ago) — ${SIT:-no situation line}")
done

[ "${#ROWS[@]}" -gt 0 ] || exit 0

echo "## Recent session handoff available"
echo ""
if [ "${#ROWS[@]}" -eq 1 ]; then
  echo "One handoff from the last 2h:"
else
  echo "**${#ROWS[@]} handoffs from the last 2h — likely parallel sessions.** \`latest.md\` holds only the newest; pick the one that matches what the user is resuming (ask if unclear):"
fi
echo ""
printf '%s\n' "${ROWS[@]}"
echo ""
echo "If resuming work, read the matching file first — it captures the state the prior session didn't get onto disk."
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

After this, every new session that starts within 2 hours of a handoff will see it listed.

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
