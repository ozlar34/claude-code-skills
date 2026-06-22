# INSTALL — github-polish rendering add-on (instructions for a coding assistant)

**You are a coding assistant. The user already has (or is installing) the `github-polish`
core and now wants the optional rendering layer — branded social cards, README banners,
and architecture diagrams. Follow these steps exactly.**

This layer needs Python + a headless browser (Playwright + Chromium). That's the reason
it's optional and not in the core: the core can't break in any environment, this can.
Install it only when the user asks for branded assets.

---

## Step 1 — Check Python

```bash
python3 --version      # need 3.8+
```

If `python3` is missing, tell the user to install it (`brew install python` on macOS, or
their distro's package), then re-run you.

## Step 2 — Install Playwright + Chromium

```bash
python3 -m pip install --user playwright
python3 -m playwright install chromium
```

- The first line installs the Playwright Python package; the second downloads a
  Chromium build it manages (a few hundred MB — tell the user it's downloading).
- If `pip` is externally managed / blocked (common on newer macOS + Homebrew Python),
  fall back to a venv:
  ```bash
  python3 -m venv ~/.github-polish-venv
  ~/.github-polish-venv/bin/pip install playwright
  ~/.github-polish-venv/bin/playwright install chromium
  ```
  and use `~/.github-polish-venv/bin/python3` in place of `python3` for the rest.

## Step 3 — Install the render files into the skill

Copy the `render/` directory next to the installed `SKILL.md`:

```bash
# from a clone of the repo (see core INSTALL.md Step 3 for the clone)
cp -r source/github-polish/render ~/.claude/skills/github-polish/render
```

(Substitute the skill path if the core was installed somewhere other than
`~/.claude/skills/github-polish/`.)

## Step 4 — Verify it actually renders (do not skip)

Render the bundled example config to a temp file and confirm a real PNG comes out. If
this fails, the add-on is **not** working — report the error to the user rather than
leaving them with a half-installed layer.

```bash
cd ~/.claude/skills/github-polish/render
python3 render_card.py configs/example.json /tmp/gh-polish-selftest.png
file /tmp/gh-polish-selftest.png    # must say: PNG image data, 2560 x 1280
```

Expected: `card -> /tmp/gh-polish-selftest.png` and a 2560×1280 PNG (the card is rendered
at 2× for retina). If you used the venv fallback, run with that interpreter.

## Step 5 — Confirm and explain

Tell the user, in your own words:

- The rendering add-on is installed and self-tested.
- From now on, `/github-polish <repo>` can also produce a branded **social card**
  (staged for them to upload via *Settings → Social preview*), a **banner** committed to
  the repo's `docs/banner.png` and embedded above the README H1, and — only if the repo
  has real structure — an **architecture diagram**.
- The look is driven by a small per-repo JSON config (`render/configs/<repo>.json`); the
  schema and accent palette are in `render/brand-spec.md`. They can change the accent,
  glyph, and copy per repo; the shared chrome keeps every repo on one family look.
- If they used the venv fallback in Step 2, the skill must call Python via
  `~/.github-polish-venv/bin/python3` — note that for them (and in the skill config if
  your framework supports it).

---

**Integrity reminders that still apply** (from `SKILL.md`): the social card is rendered
with placeholder/honest copy only — no private data, no invented metrics; a diagram is
drawn only when there's real structure, never faked; and the card is **uploaded by the
human** (the API can't), so it's always staged, never claimed as done.
