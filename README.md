![claude-code-skills — Claude Code skills built for my own stack](docs/banner.png)

# Claude Code Skills

A handful of [Claude Code](https://www.anthropic.com/claude-code) skills I built for my own stack — Obsidian, Notion, NotebookLM, and a few general-purpose utilities.

Skills are markdown files under `~/.claude/skills/` that Claude Code auto-loads and triggers on natural-language matches. They let you turn repeated workflows into one-shot voice/text commands.

## Two tiers

This repo splits skills into two folders by how reusable they actually are.

| Folder | What it is | When to use |
|---|---|---|
| [`source/`](./source) | Sanitized, runnable skills. Copy a directory into `~/.claude/skills/` and follow the per-skill `SETUP.md`. | Genuinely portable — they don't assume anything about your private databases or APIs. |
| [`showcase/`](./showcase) | Pattern walkthroughs only. No source code. | Skills tightly coupled to my private setup — Notion databases, my Obsidian vault, my task manager, my brand assets. The architecture and prompt design are the interesting parts; you'd rebuild against your own data anyway. |

## Catalog

### Source — runnable

| Skill | Category | One-liner |
|---|---|---|
| [`sell`](./source/sell) | Web automation | Drives the Kleinanzeigen post-ad form via Playwright MCP. Fills every field, narrates German values back in English, stops before publish. |
| [`claude-inbox`](./source/claude-inbox) | Capture | Triage an Apple Reminders capture list one item at a time. Pair with a Siri shortcut for hands-free mobile capture. |
| [`session-handoff`](./source/session-handoff) | Workflow | Generate a structured handoff block when context is hot, mid-stream. Persists to disk + clipboard so a fresh session can resume after `/clear`. |
| [`clippings`](./source/clippings) | Capture | GTD-triage an Obsidian Web Clippings inbox — analyze each, route, delete. |

### Showcase — patterns only

| Skill | Category | One-liner |
|---|---|---|
| [`coffee`](./showcase/coffee.md) | Notion | Coffee bean inventory + brew log + recipe index across three Notion databases. Captures faults as a separate axis from descriptive flavor notes. |
| [`gaming`](./showcase/gaming.md) | Notion | Video game library with auto-applied date side-effects (`Currently Playing` sets Date Started; `Complete` sets Date Finished). |
| [`add-watch`](./showcase/add-watch.md) | Notion | Watch wishlist. Web-search-driven spec extraction into a typed Notion entry. |
| [`log-reel`](./showcase/log-reel.md) | Notion | Ship-time logger for shipped content. Closes the gap between publish and tracker — dedupes against in-progress entries. |
| [`triage`](./showcase/triage.md) | Obsidian / capture | Inbox triage with a `promote → flip → destruct` atomicity loop, a zero-write `hold` verdict, and a propose-then-review split (parallel per-item agents propose, a gated review pass executes). |
| [`pack-trip`](./showcase/pack-trip.md) | TickTick / vault | Per-trip packing checklist from a canonical template — asks only the per-trip deltas, computes a clothing formula, writes one task with the items as a checklist. |
| [`github-polish`](./showcase/github-polish.md) | GitHub automation | One mostly-autonomous pass to make a public repo recruiter-ready: metadata, README, branded card + banner. Hard CLI/UI boundary, honest-handback, no faked assets. |

## Install (source skills)

```bash
# Pick one
cp -r source/sell ~/.claude/skills/
cp -r source/claude-inbox ~/.claude/skills/
cp -r source/session-handoff ~/.claude/skills/
cp -r source/clippings ~/.claude/skills/

# Then read the SETUP.md in the copied folder for any placeholders to fill in.
```

Restart Claude Code (or open a new session). The skill auto-surfaces — invoke it with `/<skill-name>` or by triggering the natural-language pattern in its description.

## Why no source for showcase skills?

The showcase skills are wired into my private setup — Notion database/page IDs and select-option enums, my Obsidian vault layout, my task-manager project, my brand-asset templates. Sanitizing them into runnable templates means writing a `SETUP.md` that walks you through recreating my exact schema/vault/config piece-by-piece — which nobody is going to do, and which would still leave you debugging mismatches against your own data.

What's actually useful from those skills is the *pattern*: schema-first MCP calls, status-driven date side-effects, dedup-before-create, fault tags as a separate axis from descriptive tags, ship-time capture vs post-hoc backfill, `promote → flip → destruct` atomicity, propose-then-review with parallel per-item agents, and an honest CLI/UI boundary for autonomous automation. Those are documented in each `showcase/<name>.md` walkthrough.

## More

- [ozlar34/ozlar34](https://github.com/ozlar34) — profile and pinned projects
- Skills not in this repo: 5 job-search skills wired into a private n8n + Supabase + Apify pipeline. Architecture lives in [job-match-radar](https://github.com/ozlar34/job-match-radar).
