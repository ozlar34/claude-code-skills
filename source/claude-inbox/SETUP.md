# Setup — claude-inbox

## Platform requirement

This skill uses AppleScript to read and complete Apple Reminders. **macOS only.** It won't work on Linux or Windows.

## 1. Install

```bash
cp -r claude-inbox ~/.claude/skills/
```

## 2. Configure

Open `~/.claude/skills/claude-inbox/SKILL.md` and edit the **Configuration** block:

```
LIST_NAME            : Claude Inbox
ROUTE_TO_TASK_TOOL   : TickTick / Todoist / Things / Notion (whichever you use)
ROUTE_TO_NOTES       : Obsidian vault / Notion / etc.
```

`LIST_NAME` must match the Apple Reminders list you'll create in step 3. The two routing fields are descriptive — Claude will use whatever MCPs/tools you have wired up. You don't need to install anything new for this skill itself, but the *routing actions* assume you have at least one task tool and one notes destination available to Claude Code.

The two AppleScript blocks inside `SKILL.md` reference `<LIST_NAME>` literally. Either replace those occurrences with your list name (recommended) or trust Claude to substitute at runtime.

## 3. Create the Apple Reminders list

On your Mac:

1. Open Reminders
2. Click **+ Add List** in the sidebar
3. Name it exactly the value you set as `LIST_NAME` (default: `Claude Inbox`)
4. Set its iCloud account so it syncs to your phone

## 4. Create the Siri Shortcut

This is the non-obvious dependency that makes the skill actually useful. You need a phone-side trigger.

On your iPhone:

1. Open the **Shortcuts** app
2. Create a new shortcut named **Add to Claude Inbox** (or whatever phrase you want to trigger it)
3. Add one action: **Add New Reminder**
4. Configure:
   - **List:** the list you created above
   - **Title:** "Ask Each Time" (Shortcuts will dictate from voice)
5. Add it to your home screen / Siri suggestions
6. Test: *"Hey Siri, add to claude inbox lookup vibration plate brand"*

The shortcut will create a reminder in the list with the dictated text as the title. iCloud syncs it to your Mac within a few seconds.

## 5. Restart Claude Code

Open a new session. Trigger:

- `/claude-inbox`
- `process inbox`
- `check my inbox`

If the list is empty, the skill says so and stops — zero overhead.

## What's NOT included

- Claude can't *write* to Apple Reminders from this skill — only read and mark complete. Items get there via your phone (Siri) or by manually adding from any device.

## Dependencies

- macOS
- Apple Reminders + iCloud sync
- One Siri Shortcut on your phone
- A task tool and a notes tool that Claude Code can write to (use whatever you already have)
