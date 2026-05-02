# Setup — find-print

## 1. Install

```bash
cp -r find-print ~/.claude/skills/
```

## 2. Edit `SKILL.md`

Open `~/.claude/skills/find-print/SKILL.md` and replace the placeholders in the **Printer Context** section:

```markdown
- **Printer:** <YOUR_PRINTER_MODEL>
- **Materials available:** <YOUR_MATERIALS>
```

Examples:
- `Bambu Lab P1S` and `PLA, PETG, TPU`
- `Prusa MK4` and `PLA only`
- `Voron 2.4` and `PLA, PETG, ABS, ASA`

The printer model gets injected into search queries as a relevance signal — Bambu owners get Bambu-tagged designs prioritized, Prusa owners get Prusa-tagged ones.

## 3. (Optional) Tune quality thresholds

The default thresholds in the **Quality Gates** table assume mainstream printer models with active communities. If you're on a niche printer where 50 downloads is unrealistic, lower them. The thresholds are descriptive — Claude will follow whatever you write in the table.

## 4. Restart Claude Code

Open a new session. Trigger with anything that matches the description — `find me a print for…`, `/find-print`, or natural language describing what you want to print.

## Dependencies

- `WebSearch` and `WebFetch` tools (default Claude Code setup)
- No external API keys, no MCP servers required
