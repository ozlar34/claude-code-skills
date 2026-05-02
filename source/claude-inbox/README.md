# claude-inbox

**Trigger:** "/claude-inbox", "process inbox", "check inbox"

**What it does:** Drains an Apple Reminders list one item at a time. For each item, Claude reads the title and notes, infers what you meant (Siri's transcription is noisy), assesses how it connects to your active work, recommends one of five routings (act now / task / note / backlog / ignore), and on confirmation executes that routing and marks the reminder complete.

The point is not the AppleScript — it's the GTD discipline of *one at a time, executed and closed* before moving on. Captures sit in the list until they're triaged, not forever.

**Setup:** see [SETUP.md](./SETUP.md). One Apple Shortcut to create, one list to make, three lines to edit.

**Example mobile capture flow:**

> *(driving)* "Hey Siri, add lookup that vibration plate brand to claude inbox"
> *(later, at desk)* `/claude-inbox`

```
You have 3 items in Claude Inbox.

### [1/3] lookup that vibration plate brand
Captured: 2 hours ago

Interpretation: You want to research the vibration plate brand you saw / heard about — likely the one mentioned at the gym yesterday.

Relevance: Not connected to any active project. Possibly recovery / fitness research.

Recommended action: Task — because it needs follow-up but isn't urgent. "Research vibration plate brands" with a 1-week due date.

Pick one: [Act now / Task / Note / Backlog / Ignore]
```

You answer, the action fires, the reminder gets marked complete, next item.

**Why it exists:** Voice capture is the cheapest way to get an idea out of your head while away from your computer. Without a triage gate, the list grows until you stop trusting it. Without single-item discipline, you skim batches and ignore most of them. This skill keeps the list trustworthy by treating each item as a decision, not a data point.

**Dependencies:**
- macOS (uses AppleScript to read/complete Reminders)
- Apple Reminders list synced to your phone via iCloud
- A Siri Shortcut on your phone that adds to that list (one-line: just creates a reminder in the named list)
- Whatever task/notes tool you route to — TickTick MCP, Notion MCP, plain Obsidian markdown writes, etc.
