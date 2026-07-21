# Setup — github-polish

Two ways to install. Pick one.

## Option A — hand the link to your coding assistant (the fast path)

Paste this to Claude Code (or any coding assistant) in a fresh session:

> Install the `github-polish` skill from https://github.com/ozlar34/claude-code-skills — follow
> `skills/github-polish/INSTALL.md` in that repo.

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

This skill can also render a consistent **social card** (1280×640), README **banner**
(1280×320), and **architecture diagram** for each repo, so a profile of repos reads as one
visual family. It lives in [`render/`](./render) and is **opt-in** — it needs Python + a headless
browser (Playwright + Chromium), which is exactly why it isn't in the core: the core can't break
in your environment, this can.

The design is deliberately layered. Forcing a headless browser on every installer would be the
wrong default, so the core works with nothing but `gh`, and the rendering is something you add
only if you want the branded look. When `render/` is present next to `SKILL.md`, the skill's
execute step **d** activates and produces the assets; when it isn't, the skill skips that step and
never claims it made any.

**Install it (fast path):** ask your coding assistant to follow
[`render/INSTALL-render.md`](./render/INSTALL-render.md) — it installs Playwright + Chromium,
copies `render/` into place, and **self-tests by rendering the bundled example config** before
declaring success.

**Install it by hand:**
```bash
python3 -m pip install --user playwright
python3 -m playwright install chromium       # downloads a managed Chromium (a few hundred MB)
cp -r render ~/.claude/skills/github-polish/render
# verify:
cd ~/.claude/skills/github-polish/render && python3 render_card.py configs/example.json /tmp/test.png
```
(If `pip` is externally managed, use a venv — see `render/INSTALL-render.md` for the fallback.)

The look is driven by a per-repo JSON config; the schema, accent palette, and a full worked
example are in [`render/brand-spec.md`](./render/brand-spec.md) and
[`render/configs/example.json`](./render/configs/example.json). You change the accent, glyph, and
copy per repo; the shared chrome keeps every repo on one family look. The palette ships as
GitHub's own neutral dark theme — make it yours by editing `render/brand.py`.

Without the add-on you can still add a social preview by hand — any 1280×640 image, uploaded via
*Settings → General → Social preview* (the handback reminds you).
