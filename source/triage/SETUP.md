# Setup — triage

## 1. Install

```bash
cp -r triage ~/.claude/skills/
```

## 2. Configure your inbox path

Open `~/.claude/skills/triage/SKILL.md` and edit the **Configuration** block:

```
CLIPPINGS_DIR : <ABSOLUTE_PATH_TO_INBOX>
```

Common locations:

- **Obsidian Web Clipper (vault on iCloud):**
  `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/<VaultName>/Web Clippings/`
- **Obsidian Web Clipper (local vault):**
  `~/Documents/Obsidian/<VaultName>/Web Clippings/`
- **Standalone clipper folder:**
  `~/Inbox/Clippings/` (or wherever you point your clipper)

The folder must already exist. Create it if needed:

```bash
mkdir -p "<your path>"
```

## 3. Set up your web clipper

Any extension that saves clipped pages as `.md` files into the configured folder will work.

**[Obsidian Web Clipper](https://github.com/obsidianmd/obsidian-clipper)** is the most common pairing — install the browser extension, point it at your vault and the `Web Clippings/` subfolder, and it's done.

If your clipper doesn't write a `type:` frontmatter field, the skill defaults to treating clippings as articles. To get YouTube-specific TL;DR behavior, your clipper needs to add `type: youtube` to the frontmatter when it captures a video page.

## 4. (Recommended) Wire up routing destinations

The skill's "Save" and "Act" routings are open-ended — Claude will use whatever you have available. To make routing actually work end-to-end, you want:

- **A task tool**: TickTick / Todoist / Things via their MCP, or just write to a tasks file your other workflow picks up
- **A notes destination**: an Obsidian vault path Claude can write to, a Notion MCP, or both

If you have neither, the skill still works — it just becomes "TL;DR + decide + delete," with the action being noted in chat instead of routed externally.

## 5. Restart Claude Code and try it

Pick something to clip from your browser. Make sure it lands in `CLIPPINGS_DIR`. Then:

> /triage

If the folder is empty, the skill says "You have 0 clippings" and stops — zero overhead.

## What's NOT included

- A web-clipper itself. Bring your own.
- A specific routing destination. The skill is intentionally tool-agnostic for the Save / Act actions — wire up whatever you use.

## Dependencies

- Claude Code default tools (Bash, Read, Write, Edit, Glob, Grep)
- A web-clipper that writes `.md` files to a folder
- (Optional but recommended) A task-tool MCP and a notes destination Claude can write to
