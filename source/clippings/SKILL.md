---
name: clippings
description: Process a Web Clippings inbox (e.g. Obsidian Web Clipper output) one item at a time. Analyze each, recommend an action (act, save, backlog, ignore), execute on confirmation, then delete the clipping. GTD-style triage for captured articles and YouTube transcripts.
trigger: clippings OR triage OR process-clippings OR process clippings
allowed-tools: Bash,Read,Write,Edit,Glob,Grep
---

# Clippings — Web Clippings Inbox Processor

Process a folder of captured articles / YouTube transcripts using GTD methodology: one item at a time, analyze, decide, execute, delete.

## Configuration

Edit this default at the top of this file before first use:

```
CLIPPINGS_DIR : <ABSOLUTE_PATH_TO_INBOX>
```

This is wherever your web-clipper writes new captures. For Obsidian Web Clipper that's typically a folder inside your vault, e.g.:

```
~/Library/Mobile Documents/iCloud~md~obsidian/Documents/<VaultName>/Web Clippings/
```

Everything in `CLIPPINGS_DIR` is unprocessed. Once processed, it gets deleted.

## Workflow

### Step 0: Count clippings

Count how many `.md` files are in `CLIPPINGS_DIR` and report: "You have N clippings to process."

If zero, say so and stop.

### Step 1: Present a clipping

For each clipping file in the folder:

1. Read the full file
2. Determine the type from frontmatter `type` field:
   - `type: youtube` → YouTube transcript
   - `type: article` (or missing) → Article
3. Present:

```
### [N/total] Title
**Type:** YouTube / Article
**Source:** [link]
**Published:** date | **Clipped:** date

**TL;DR:** 2-3 sentence summary of the content.

**Why this matters to you:** 1-2 sentences connecting (or not connecting) this to the user's active projects, goals, or interests. Be honest — if it's not relevant, say so.

**Recommended action:** [one of the actions below] — because [reason]
```

### Step 2: User decides

Present the action options. The user picks one (or accepts the recommendation):

| Action | What happens |
|--------|-------------|
| **Act** | Ask what the next action is (suggest one). Then create a task in whichever task tool the user has wired up (TickTick / Todoist / Things / etc). |
| **Save** | Save somewhere persistent — Obsidian vault note, NotebookLM source, Notion entry. Ask where if ambiguous. |
| **Backlog** | One-liner to a long-running ideas/backlog file in the user's notes destination. |
| **Ignore** | Skip — no action needed. |

### Step 3: Execute and delete

1. Execute the chosen action
2. After execution, ask: "Delete this clipping?" — **wait for confirmation**
3. On confirmation, `rm` the file from `CLIPPINGS_DIR`
4. Move to the next clipping (back to Step 1)

### Step 4: Wrap up

When all clippings are processed (or the user says stop), summarize:

```
### Clippings processed: N
- Acted: X (tasks created)
- Saved: X
- Backlog: X
- Ignored: X
```

## Rules

- **One at a time.** Never batch-present multiple clippings.
- **Be concise.** The TL;DR and relevance assessment should be sharp, not padded.
- **Be honest about relevance.** If something doesn't connect to any active project or goal, say "This doesn't connect to anything you're actively working on." Don't stretch to find relevance.
- **YouTube transcripts are long.** For these, focus the TL;DR on key takeaways, not a play-by-play. Skim for actionable insights.
- **"Stop" ends the session early.** Still show the summary.
- **Token efficiency.** Read clippings directly from `CLIPPINGS_DIR`.
- **Delete means delete.** Use `rm` after confirmation. The web clipper will create new ones.
