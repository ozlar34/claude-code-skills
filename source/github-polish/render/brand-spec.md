# github-polish — brand spec & render configs

The visual contract every repo's assets hold, plus the JSON schemas the render scripts
read. Read this when you're about to render a card, banner, or diagram. The template
lives in `brand.py`; this file is the human-facing spec + config reference. A complete
worked config is in [`configs/example.json`](./configs/example.json).

## Why a fixed template

A profile's repos are read *together* — on your profile page, in a CV link block, side
by side in a recruiter's tab. A shared card template makes them a *family*: same dark
ground, same accent-bar grammar, same typography. The only thing that changes per repo
is the accent color, glyph, and copy. Never invent a new layout for one repo — change
the per-repo config, not the template. If the template itself needs to evolve, change
`brand.py` once and re-render every repo so none drifts.

## Visual contract (social card, 1280×640)

- Ground `#0d1117`, ink `#e6edf3`, with a soft radial glow in the accent, top-right.
  (This is GitHub's own dark palette — a neutral default. Change it in `brand.py` only
  if you want a different house style across *all* your repos.)
- A 10px accent bar down the left edge — the per-repo signature color.
- Big emoji glyph, top-right, ~120px, slightly faded.
- `github.com/<owner>` host line (monospace, owner bolded in the accent).
- Repo name in monospace, ~78px, white.
- One tagline, ≤ ~880px wide — what the repo *is*, plainly.
- Up to ~4 chips — the real stack (languages, frameworks, platforms), accent-tinted.
- A footer line — a short "what it runs on / where it lives" clause.

Accent colors that sit well on the GitHub-dark ground (reuse where one fits; give each
repo on your profile a distinct one so they don't blur together):
`#58a6ff` blue · `#3fb950` green · `#bc8cff` purple · `#f0883e` orange ·
`#d29922` amber · `#e11d48` rose (use sparingly).

## Card config schema

A per-repo config file: `configs/<repo>.json`. Card fields can sit at the top level, or
nested under a `"card"` key (so one file can hold `card`, `banner`, and `flow`).

```json
{
  "card": {
    "accent": "#58a6ff",
    "glyph": "🔭",
    "name": "json-diff-tui",
    "tag": "A terminal UI for diffing large JSON files, side by side",
    "chips": ["Rust", "ratatui", "serde"],
    "foot": "Single static binary · no runtime deps",
    "owner": "your-username"
  }
}
```

`owner` is optional (defaults to the `DEFAULT_OWNER` placeholder in `brand.py`). The
skill normally fills it from `gh api user --jq .login` before rendering, so the card
shows *your* handle. Copy is plain text — it's HTML-escaped for you, so write
`scrapes, scores & emails`, not `&amp;`.

Render:
```bash
python3 render_card.py configs/<repo>.json /tmp/<repo>-card.png
```

The social card is **not committed** — it's uploaded via GitHub's UI
(*Settings → General → Social preview*), so render it to a temp path and hand that path
back to the user for upload.

## README header banner (1280×320)

The card above is for the *share-link* context — it never shows on the repo page itself.
The **banner** is the on-repo equivalent: a 4:1 letterhead committed into the repo and
embedded above the README's H1, so a visitor landing straight on the repo sees the brand
immediately.

Same accent/glyph/name as the card, but **deliberately minimal** — one tag line, NO
chips or footer. The 4:1 ratio is the whole point: at 2:1 a card embedded at the top of
a README renders ~640px tall and buries the title and any real screenshot below it; at
4:1 it reads as a *header strip* that sits above the title without competing with a real
product shot underneath. That's why the banner goes on every repo, including ones that
already lead with a real screenshot — the strip is a letterhead, not a second hero.

The banner reuses the `card` block — no separate config needed. If the card's `tag` is
too long to fit one banner line (~50 chars is the safe budget), add a `banner` key with
a shorter `tag`; it overlays the card values:

```json
{
  "card": { "accent": "#58a6ff", "glyph": "🔭", "name": "json-diff-tui",
            "tag": "A terminal UI for diffing large JSON files, side by side",
            "chips": ["Rust", "ratatui", "serde"], "foot": "...", "owner": "your-username" },
  "banner": { "tag": "Diff large JSON files in your terminal, side by side" }
}
```

Render, then commit into the repo's `docs/` as `banner.png` and embed above the H1:
```bash
python3 render_banner.py configs/<repo>.json /tmp/<repo>-banner.png
# cp /tmp/<repo>-banner.png <repo>/docs/banner.png  (then commit)
```
```markdown
![<repo> — <one-line tag>](docs/banner.png)

# Repo Title
```
Keep the H1 — the banner is graphical branding, the H1 is the semantic title (anchor +
SEO). The slight name repetition is expected and fine. Unlike the social card, the
banner IS committed and embedded; verify its raw URL returns 200 like any other embedded
asset.

## Flow / architecture diagram

Only draw a diagram when the repo has **real** structure worth showing — an existing
ASCII diagram in the README, a `workflows/` or `docs/` layout, a clear module split, a
compose file with named services. If there's nothing meaningful to draw, skip it; a
faked architecture is worse than none.

`elements` is an ordered list of vertical-flow nodes. Types:

| type    | fields              | renders |
|---------|---------------------|---------|
| `boxes` | `boxes: [box, ...]` | one row of nodes, side by side |
| `arrow` | —                   | a down arrow |
| `merge` | —                   | a `◢ ◣` glyph (two branches converging) |
| `note`  | `text`              | an italic caption between stages |
| `side`  | `box`, `note`       | a node with a monospace side-tag to its right |

A `box` is `{title, lines: [..], accent, width}` (`width` optional). **Box lines accept
inline HTML/entities on purpose** — use `&nbsp;` for alignment, `&ge;` for ≥, `<br>` in
side notes. This is the one place text is *not* escaped, because the layout needs it.
Keep real private data out regardless. See `configs/example.json` for a full `flow`.

Render (bump height for longer pipelines so nothing clips):
```bash
python3 render_flow.py configs/<repo>.json /tmp/<repo>-flow.png 840
# cp /tmp/<repo>-flow.png <repo>/docs/architecture.png  (then commit)
```

Embed pattern in the README — image first, ASCII kept as a `<details>` fallback so the
diagram survives anywhere markdown renders and stays diffable:

```markdown
## Architecture

![<descriptive alt text of the actual flow>](docs/architecture.png)

<details>
<summary>Text version</summary>

```
<the ASCII diagram>
```

</details>
```

## The digest trick — render real OUTPUT with placeholder data

The strongest asset a *tool* repo can show is what it actually produces — but real output
usually contains private data. The trick: take the repo's **real output template** (the
email HTML, the report layout, the generated card) and populate it with safe placeholder
data (`Company A`–`I`, generic roles, round-number stats), then screenshot that. It reads
as genuine because the chrome and layout *are* genuine — only the data is swapped.

This is inherently bespoke per repo (each tool emits a different artifact), so there's no
generic script — you adapt the repo's own template. Keep the real chrome, swap only the
data, and label it honestly in the README ("Rendered from the real template with
placeholder data"). Never screenshot real usage and call it placeholder; never invent
metrics. If the only honest way to show output is a real capture (a terminal session, the
actual app), that goes on the human todo list as a capture walkthrough — see `SKILL.md`.

## Where files go

- **Per-repo configs** → `configs/<repo>.json` (next to this file). Create on first
  polish; reuse and refine on re-runs.
- **Social card** → render to a temp path; hand the path back for UI upload. Never
  committed.
- **Banner / diagram / output shot** → render to a temp path, then `cp` into the target
  repo's `docs/` and commit. These are embedded in the README, so they must live in the
  repo to be served by `raw.githubusercontent.com`.
