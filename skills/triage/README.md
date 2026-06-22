# triage

**Trigger:** "/triage", "process clippings", "triage clippings" (`clippings` kept as an alias)

**What it does:** Walks a folder of captured articles and YouTube transcripts (typically the output of a browser web-clipper extension) one file at a time. For each: writes a TL;DR, an honest assessment of whether it actually connects to the user's active work, and a recommended action — act on it, save it somewhere persistent, send it to a backlog, or ignore. Executes the chosen routing on confirmation and deletes the source file.

The folder acts as a triage queue. The skill keeps the queue trustworthy: items are either turned into action, saved durably, or removed. Nothing accumulates.

**Setup:** see [SETUP.md](./SETUP.md). One folder path to configure.

**Example:**

> User: /triage
>
> Skill: You have 4 clippings to process.
>
> ```
> ### [1/4] Why your sourdough is gummy in the middle
> Type: Article
> Source: https://example.com/sourdough-gummy
> Clipped: 2 days ago
>
> TL;DR: Underproofed dough + insufficient bake time at high heat
> are the two most common causes. Author recommends a 12-hour cold
> retard and a Dutch-oven preheat to 250°C before transferring.
>
> Why this matters to you: You've had 3 gummy loaves in the last
> 6 weeks. Directly relevant.
>
> Recommended action: Save — the cold retard advice is non-obvious
> and worth keeping.
>
> Pick one: [Act / Save / Backlog / Ignore]
> ```
>
> User: save to obsidian, baking notes
>
> *(skill writes to vault, asks to delete clipping, deletes on yes, moves to [2/4])*

**Why it exists:** Browser-clipper extensions are great at capture but terrible at follow-through — clippings pile up forever in a folder no one ever opens. This skill turns the folder into a queue with a draining mechanism: every clipping eventually exits the inbox, either as a task, a permanent note, a backlog entry, or a deletion.

The cognitive trick is the "honest about relevance" rule. If you save everything because you might want it later, the system fails. The skill explicitly checks each item against active work — and when there's no connection, says so plainly. Most clippings get ignored. That's fine. The point isn't to keep them, it's to *decide*.

**Dependencies:**
- A web-clipper extension that drops `.md` files into a folder. Tested with [Obsidian Web Clipper](https://github.com/obsidianmd/obsidian-clipper). Any clipper that writes markdown should work — the skill only reads `type` from frontmatter (defaults to `article` if absent).
- Claude Code tools: `Bash`, `Read`, `Write`, `Edit`, `Glob`, `Grep`. No MCPs strictly required, though the routing actions become more useful when you have a task-tool MCP wired up.
