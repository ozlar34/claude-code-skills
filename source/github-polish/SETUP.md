# Setup — github-polish

Two ways to install. Pick one.

## Option A — hand the link to your coding assistant (the fast path)

Paste this to Claude Code (or any coding assistant) in a fresh session:

> Install the `github-polish` skill from https://github.com/ozlar34/claude-code-skills — follow
> `source/github-polish/INSTALL.md` in that repo.

The assistant reads [INSTALL.md](./INSTALL.md), checks your `gh` auth, copies the skill into
`~/.claude/skills/`, and tells you how to use it. That's the whole point of this version — the
setup labor is the assistant's, not yours.

## Option B — install it yourself

```bash
# Prerequisite: GitHub CLI, authenticated
gh --version && gh auth status        # if not authed: gh auth login

# Install
cp -r github-polish ~/.claude/skills/   # from your local clone of this repo
```

Restart Claude Code. Run `/github-polish <repo> --dry-run` first on any repo — it prints a plan
without editing anything.

That's the entire core setup. No Python, no other dependencies — just `gh`.

## What the core does (and doesn't)

**Does**, all via `gh`:
- Sharpens topics + description.
- Polishes the README toward a worked-example frame (surgical edits, preserves accurate
  paths/commands).
- Offers a LICENSE if the repo has none.
- Hands back a precise checklist of GitHub-UI-only actions it can't do (pin order, social-preview
  upload).

**Deliberately does not:** generate branded social cards, banners, or architecture diagrams. Those
need an image-rendering toolchain and a personal brand spec — see the optional add-on below.

## Optional — the branded rendering add-on

The original (private) version of this skill renders a consistent **social card** (1280×640),
README **banner** (1280×320), and **architecture diagram** for each repo, so a profile of repos
reads as one visual family. That layer is **not included in this core** because it requires:

- A **rendering toolchain** — the original uses headless-browser rendering (Playwright + a cached
  Chromium). Any renderer that takes a structured config and emits a consistent image works.
- A **brand spec** — an accent palette, a glyph set, and the card/banner/diagram layout the
  renderers draw against. This is the genuinely personal part; the *schema* (a per-repo JSON
  config feeding shared renderers) is the transferable idea, not any one palette.

If/when the add-on ships in this repo, it'll live beside this file with its own setup. The design
is intentionally layered: the core above can't break in your environment (no heavy deps), and the
rendering is opt-in for those who want the branded look. Forcing a headless browser on every
installer would be the wrong default.

Until then, you can still add a social preview by hand — any 1280×640 image, uploaded via
*Settings → General → Social preview* (the handback reminds you).
