![claude-code-skills — Claude Code skills built for my own stack](docs/banner.png)

# Claude Code Skills

A handful of [Claude Code](https://www.anthropic.com/claude-code) skills I built for my own stack — Obsidian, Notion, and a few general-purpose utilities.

Skills are markdown files under `~/.claude/skills/` that Claude Code auto-loads and triggers on natural-language matches. They let you turn repeated workflows into one-shot voice/text commands.

Each skill is packaged for reuse: copy the directory, fill in the `SETUP.md` placeholders, and it runs without depending on my private config.

## Works across tools

These skills follow the [Agent Skills](https://agentskills.io) open standard, published by Anthropic in December 2025. Any coding assistant that supports the standard — Cursor, OpenAI Codex CLI, Google Antigravity, GitHub Copilot, and 20+ others — loads them from `~/.claude/skills/` without modification. Install once; they're available everywhere.

## Catalog

| Skill | Category | One-liner |
|:---:|:---:|---|
| [`braindump`](./skills/braindump) | Thinking | Develops a raw, half-formed idea through adaptive one-question-at-a-time dialogue — what it is, what could be done with it, the smallest next step. Scales depth to the idea; writes nothing. |
| [`second‑opinion`](./skills/second-opinion) | Verification | Pull a fresh, independent Opus agent in to verify the last load-bearing claim the assistant made — confirmed / refuted / can't tell, with evidence. On-demand escalation for cheaper sessions; relays the verdict verbatim instead of rubber-stamping its own reasoning. |
| [`session‑handoff`](./skills/session-handoff) | Workflow | Generate a structured handoff block when context is hot, mid-stream. Persists to disk + clipboard so a fresh session can resume after `/clear`. |
| [`github‑polish`](./skills/github-polish) | GitHub automation | Make a public repo recruiter-ready in one pass — topics, description, worked-example README, LICENSE, honest CLI/UI handback. `gh`-only core (hand the repo link to your assistant and it installs itself), plus an optional rendering add-on for branded social cards / banners / diagrams. |
| [`claude‑inbox`](./skills/claude-inbox) | Capture | Triage an Apple Reminders capture list one item at a time. Pair with a Siri shortcut for hands-free mobile capture. |
| [`triage`](./skills/triage) | Capture | GTD-triage a captured-clippings inbox — analyze each, route, delete. Store-agnostic; wire it to your own vault or task manager. |
| [`sell`](./skills/sell) | Web automation | Drives the Kleinanzeigen post-ad form via Playwright MCP. Fills every field, narrates German values back in English, stops before publish. |
| [`learn‑from‑mistakes`](./skills/learn-from-mistakes) | Workflow | Scans session history for wrong-mental-model failures (not inefficiencies), runs each through a two-gate cost filter, and proposes surgical CLAUDE.md additions — one ~15-word imperative directive per survivor, batched for approval before anything is written. "Nothing cleared the bar" is the expected common outcome. |

## Install

```bash
# Pick one
cp -r skills/braindump ~/.claude/skills/
cp -r skills/second-opinion ~/.claude/skills/
cp -r skills/session-handoff ~/.claude/skills/
cp -r skills/github-polish ~/.claude/skills/
cp -r skills/claude-inbox ~/.claude/skills/
cp -r skills/triage ~/.claude/skills/
cp -r skills/sell ~/.claude/skills/
cp -r skills/learn-from-mistakes ~/.claude/skills/

# Then read the SETUP.md in the copied folder for any placeholders to fill in.
```

Restart Claude Code (or open a new session). The skill auto-surfaces — invoke it with `/<skill-name>` or by triggering the natural-language pattern in its description.
