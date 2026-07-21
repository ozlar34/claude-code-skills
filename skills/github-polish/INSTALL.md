# INSTALL — github-polish (instructions for a coding assistant)

**You are a coding assistant. Your user handed you the URL of this repo and asked you to install
the `github-polish` skill on their machine. Follow these steps exactly. Do not improvise file
locations.**

This installs the **portable core** — metadata + README + LICENSE + honest CLI/UI handback. It
needs only an authenticated GitHub CLI. There are no other dependencies to install.

---

## Step 1 — Check prerequisites

Run both. Do not continue until both pass.

```bash
gh --version        # GitHub CLI must be installed
gh auth status      # must report an authenticated account
```

- `gh` missing → tell the user to install it (`brew install gh` on macOS, or
  https://github.com/cli/cli#installation), then re-run you.
- `gh` present but not authenticated → tell the user to run `gh auth login` themselves (it's
  interactive — you can't do it for them), then re-run you.

## Step 2 — Locate the skill directory for the user's assistant

This skill is a Claude Code skill. The default location is `~/.claude/skills/`.

- **Claude Code** → install to `~/.claude/skills/github-polish/`.
- **A different agent framework** (Cursor, a custom harness, etc.) → install to wherever that
  framework loads skill/instruction files. If you don't know, ask the user once, then use that
  path for the rest of these steps. The skill body is plain Markdown and is framework-agnostic;
  only the install *location* differs.

## Step 3 — Install the skill

Clone this repo to a temp dir and copy the skill into place. (If you were given the repo as a
local checkout instead of a URL, skip the clone and copy from there.)

```bash
TMP="$(mktemp -d)"
git clone --depth 1 https://github.com/ozlar34/claude-code-skills "$TMP"
mkdir -p ~/.claude/skills/github-polish
cp "$TMP/skills/github-polish/SKILL.md" ~/.claude/skills/github-polish/SKILL.md
rm -rf "$TMP"
```

(Substitute the Step 2 path if it isn't `~/.claude/skills/`.)

## Step 4 — Confirm the install

```bash
test -f ~/.claude/skills/github-polish/SKILL.md && echo "installed OK"
```

Then tell the user, in your own words:

- The skill is installed. **Restart Claude Code (or open a new session)** so it loads.
- Use it with `/github-polish <repo>` — where `<repo>` is a bare repo name (resolves to their
  own GitHub account), an `owner/repo`, a full URL, or `.` for the repo in the current directory.
- **The first run on any repo should be `/github-polish <repo> --dry-run`** — it surveys and
  prints a plan without touching anything, so they can sanity-check before the autonomous pass.
- It edits metadata, polishes the README, and offers a LICENSE; it then hands back a short
  checklist of GitHub-UI-only actions (pin order, social-preview upload) that the API can't do.

## Step 5 — (Optional) offer the rendering add-on

This core renders no branded images on purpose. If the user wants on-brand social cards / banners /
diagrams generated automatically, there's an optional rendering layer — but it pulls in Python +
a headless browser (Playwright + Chromium), so install it **only if they ask**. To install it,
follow `skills/github-polish/render/INSTALL-render.md` (it installs the toolchain, copies
`render/` into the skill dir, and self-tests by rendering the bundled example). Don't install it
as part of the default setup.

---

**Do not** run `/github-polish` against any of the user's repos as part of installation. Installing
and using are separate steps — your job here ends at "installed and explained."
