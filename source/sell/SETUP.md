# Setup — sell

## Geography check

This skill drives **Kleinanzeigen.de**, the dominant German classifieds platform. Account holders need a German address. If you're not in Germany, this skill won't be useful as-is — the form selectors are German-only and the post-ad flow assumes a DE locale.

## 1. Install

```bash
cp -r sell ~/.claude/skills/
```

## 2. Configure paths and defaults

Open `~/.claude/skills/sell/SKILL.md` and edit the **Configuration** block near the top:

```
ITEMS_DIR     : ~/projects/sell-bot/items
PHOTOS_DIR    : ~/projects/sell-bot/items/photos
DEFAULT_ZIP   : <YOUR_5_DIGIT_GERMAN_ZIP>
```

`ITEMS_DIR` and `PHOTOS_DIR` can be anywhere you want. `DEFAULT_ZIP` should be your usual 5-digit listing ZIP (e.g. `10409` for Berlin Prenzlauer Berg). The skill always asks for confirmation, so this is a default, not a hard lock.

```bash
mkdir -p ~/projects/sell-bot/items/photos
```

## 3. Install Playwright MCP

The skill uses the `mcp__playwright__*` tools. If you don't already have Playwright MCP installed in Claude Code, follow the [Playwright MCP setup guide](https://github.com/microsoft/playwright-mcp). Then verify with `/mcp` in Claude Code that `playwright` is connected.

## 4. Log into Kleinanzeigen in the MCP browser

The Playwright MCP browser keeps its own session cookies. The first time you use this skill:

1. Tell Claude something like "open kleinanzeigen.de in playwright"
2. Claude will navigate the MCP browser to the site
3. Log in manually in that browser window
4. Close the window — the session persists across MCP browser restarts

## 5. (Optional) Photo-staging fallback

If you hit "File access denied" errors when uploading photos, the MCP browser sandbox is restricting file reads to the current working directory's allowed roots. Workaround:

```bash
mkdir -p ~/Desktop/<your-project>/.playwright-mcp/sell-photos
```

The skill's SKILL.md mentions this — Claude will copy photos there before uploading. Clean up after.

## 6. Restart Claude Code and try it

> sell my old keyboard, photos in `~/Downloads/keyboard/`, asking 50 EUR firm

The skill takes over from there. Stops one click before publish for your manual review.

## What's NOT included

- A companion `sell-bot` repo. The original (a small Bun-based CLI fallback for non-AI runs) is private. The skill works standalone — it just needs an items directory to write the YAML manifest into.
- A standalone CLI fallback. The original had a `bun list:ka` CLI for non-AI runs. Stripped here — the skill is the primary interface.

## Dependencies

- Playwright MCP
- Tools: `mcp__playwright__browser_navigate`, `mcp__playwright__browser_evaluate`, `mcp__playwright__browser_file_upload`, `mcp__playwright__browser_click`, `mcp__playwright__browser_take_screenshot`
- A Kleinanzeigen.de account in your name
