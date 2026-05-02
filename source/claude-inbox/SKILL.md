---
name: claude-inbox
description: Process an Apple Reminders capture list one item at a time — ideas captured via Siri on mobile. Analyze each against current context, recommend routing (act/save/backlog/ignore), execute on confirmation, then mark complete. Configure the list name and routing destinations below.
trigger: claude-inbox OR claude inbox OR inbox OR process inbox OR check inbox
allowed-tools: Bash,Read,Write,Edit
---

# Claude Inbox — Mobile Capture Processor

Process ideas captured on mobile via Siri → Apple Reminders → an iCloud-synced list. GTD-style: one at a time, analyze, decide, execute, complete.

## Configuration

Edit these defaults at the top of this file before first use:

```
LIST_NAME            : Claude Inbox
ROUTE_TO_TASK_TOOL   : <task tool of choice — TickTick, Todoist, Things, etc.>
ROUTE_TO_NOTES       : <notes destination — Obsidian vault, Notion, etc.>
```

The list name must match exactly what you create in Apple Reminders. The two routing destinations are descriptive — Claude will use whatever tools/MCPs you have wired up.

## How items get here

You say: *"Hey Siri, add [idea] to <LIST_NAME>"* from your phone or watch while away from the Mac. Items sync via iCloud Reminders.

## Reading the list (AppleScript)

```bash
osascript <<'APPLESCRIPT'
tell application "Reminders"
  set output to ""
  set inboxList to list "<LIST_NAME>"
  set activeItems to (reminders of inboxList whose completed is false)
  repeat with r in activeItems
    set output to output & (id of r) & "|||" & (name of r) & "|||" & ((creation date of r) as string)
    if body of r is not missing value then
      set output to output & "|||" & (body of r)
    end if
    set output to output & linefeed
  end repeat
  return output
end tell
APPLESCRIPT
```

Replace `<LIST_NAME>` literally before running. If the list doesn't exist, AppleScript errors. Tell the user to create a Reminders list with the exact name they configured and try again.

## Marking an item complete

```bash
osascript -e 'tell application "Reminders" to set completed of (first reminder whose id is "REMINDER_ID") to true'
```

Use the id captured from the read step.

## Workflow

### Step 0: Load inbox

1. Read the list. Count items. Report: "You have N items in <LIST_NAME>."
2. If empty, say so and stop.

### Step 1: Present one item

For each reminder:

```
### [N/total] Title
**Captured:** date (relative — "2 hours ago", "yesterday")
**Notes:** [body if present]

**Interpretation:** What you think the user meant by this. One sentence.

**Relevance:** How it connects to active projects/goals — or honestly, that it doesn't.

**Recommended action:** [one below] — because [reason]
```

### Step 2: User decides

| Action | What happens |
|--------|-------------|
| **Act now** | Do it in this session if small + bounded; for anything bigger, suggest creating a planning artifact instead. |
| **Task** | Create a task in the configured `ROUTE_TO_TASK_TOOL` (confirm title/project/priority/date before creating). |
| **Note** | Append to or create a note in `ROUTE_TO_NOTES`. Ask where if ambiguous. |
| **Backlog** | One-liner to a "tool/idea backlog" file in `ROUTE_TO_NOTES`. |
| **Ignore** | Drop it — bad idea in hindsight, already done, duplicate. |

### Step 3: Execute and complete

1. Execute the chosen action.
2. Ask: "Mark this item complete in <LIST_NAME>?" — **wait for confirmation**.
3. On confirmation, mark complete via AppleScript using the item's id.
4. Move to the next item.

### Step 4: Wrap up

```
### <LIST_NAME> processed: N
- Acted: X
- Tasks created: X
- Notes saved: X
- Backlog: X
- Ignored: X
```

## Rules

- **One at a time.** Never batch.
- **Be honest about relevance.** If an item doesn't connect to anything, say so.
- **Voice-captured text is noisy.** Interpret generously — Siri mishears words. If ambiguous, ask what was meant before routing.
- **"Stop" ends the session.** Still show the summary.
- **Complete means complete.** Don't delete reminders — marking complete preserves history and keeps the list clean.
