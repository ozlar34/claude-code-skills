#!/usr/bin/env python3
"""The github-polish visual brand — one source of truth for every rendered asset.

Every repo's social card, banner, and flow diagram is built from the templates here,
so a whole profile of repos reads as a *family*: dark #0d1117 ground, a per-repo accent
bar down the left, a big glyph top-right, monospace repo name, a `github.com/<owner>`
host line, a tagline, accent chips, and a footer line.

This module is imported by render_card.py, render_banner.py, and render_flow.py. It
produces HTML strings only — the renderers own Playwright/Chromium and the screenshot
step. Keeping the brand here (and nowhere else) is what stops the family from drifting
card to card. If you change the look, change it HERE, then re-render every repo so they
stay matched.

The palette below is GitHub's own dark theme — a deliberately neutral default. To make
it *yours*, the only thing you change per repo is the accent color, glyph, and copy in
the per-repo config (see brand-spec.md). Change the shared chrome (ground, typography)
only if you want a different house style across all repos.
"""
import html

# ---- Palette (GitHub-dark family — neutral default) ----
BG = "#0d1117"
SURFACE = "#161b22"
BORDER = "#30363d"
INK = "#e6edf3"
INK_BRIGHT = "#ffffff"
MUTED = "#8b949e"
MUTED_2 = "#9da7b3"
MUTED_3 = "#6e7681"

FONT = "-apple-system, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif"
MONO = "'SF Mono', 'JetBrains Mono', Menlo, monospace"

# Stamped on assets when a config omits "owner". Left as an obvious placeholder on
# purpose — a forgotten owner shows up as "your-username", not someone else's handle.
# The skill normally fills this from `gh api user --jq .login` before rendering.
DEFAULT_OWNER = "your-username"

CARD_W, CARD_H = 1280, 640
BANNER_W, BANNER_H = 1280, 320


def _esc(s):
    """Escape plain-text copy (card name/tag/foot/chips). Display-safe: an `&` in
    'scrapes, scores & emails' renders as `&`, not a broken entity."""
    return html.escape(str(s), quote=False)


# ---------------------------------------------------------------- social card ----
def card_html(cfg):
    """1280x640 social-preview card. cfg keys:
      accent  (hex, required)   left bar + glow + chips + host highlight
      glyph   (emoji, required) big mark, top-right
      name    (str, required)   repo name, monospace
      tag     (str, required)   one-line tagline
      chips   (list[str])       up to ~4 short tech tags
      foot    (str)             footer line
      owner   (str)             defaults to DEFAULT_OWNER
    """
    owner = _esc(cfg.get("owner", DEFAULT_OWNER))
    accent = cfg["accent"]
    chips = "".join(f'<span class="chip">{_esc(x)}</span>' for x in cfg.get("chips", []))
    foot = _esc(cfg.get("foot", ""))
    return f"""<!doctype html><html><head><meta charset=utf-8><style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{CARD_W}px;height:{CARD_H}px;overflow:hidden}}
body{{background:{BG};font-family:{FONT};color:{INK};
 background-image:radial-gradient(900px 500px at 100% 0%, {accent}22, transparent 60%);
 position:relative}}
.bar{{position:absolute;left:0;top:0;width:10px;height:100%;background:{accent}}}
.wrap{{padding:90px 96px;height:100%;display:flex;flex-direction:column;justify-content:center}}
.host{{font-family:{MONO};font-size:24px;color:{MUTED};letter-spacing:.5px;margin-bottom:26px}}
.host b{{color:{accent}}}
.name{{font-family:{MONO};font-size:78px;font-weight:700;line-height:1.02;color:{INK_BRIGHT};margin-bottom:30px}}
.tag{{font-size:34px;line-height:1.35;color:#c9d1d9;max-width:880px;margin-bottom:44px;font-weight:400}}
.chips{{display:flex;gap:16px;margin-bottom:40px;flex-wrap:wrap}}
.chip{{font-family:{MONO};font-size:22px;padding:10px 20px;border:1px solid {accent}55;
 border-radius:999px;color:{accent};background:{accent}14}}
.foot{{font-size:22px;color:{MUTED}}}
.glyph{{position:absolute;right:80px;top:64px;font-size:120px;opacity:.9}}
</style></head><body>
<div class=bar></div>
<div class=glyph>{cfg['glyph']}</div>
<div class=wrap>
 <div class=host>github.com/<b>{owner}</b></div>
 <div class=name>{_esc(cfg['name'])}</div>
 <div class=tag>{_esc(cfg['tag'])}</div>
 <div class=chips>{chips}</div>
 <div class=foot>{foot}</div>
</div></body></html>"""


# --------------------------------------------------------------- README banner ----
def banner_html(cfg):
    """1280x320 README header banner — a letterhead, not a hero. Goes committed
    into the repo (docs/banner.png) and embedded above the README's H1, so a
    visitor landing straight on the repo sees the brand immediately. Deliberately
    minimal: same accent/glyph/name from the social card, but ONE line of tag and
    NO chips/foot — at 4:1 it reads as a header strip, sitting above the title
    without competing with any real screenshot or artwork below it. cfg keys:
      accent (hex, required)   left bar + glow
      glyph  (emoji, required) mark, right, vertically centered
      name   (str, required)   repo name, monospace
      tag    (str, required)   one short line — keep it tight, it must not wrap
      owner  (str)             defaults to DEFAULT_OWNER
    """
    owner = _esc(cfg.get("owner", DEFAULT_OWNER))
    accent = cfg["accent"]
    return f"""<!doctype html><html><head><meta charset=utf-8><style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{BANNER_W}px;height:{BANNER_H}px;overflow:hidden}}
body{{background:{BG};font-family:{FONT};color:{INK};
 background-image:radial-gradient(700px 320px at 100% 0%, {accent}22, transparent 60%);
 position:relative}}
.bar{{position:absolute;left:0;top:0;width:10px;height:100%;background:{accent}}}
.wrap{{padding:0 96px;height:100%;display:flex;flex-direction:column;justify-content:center}}
.host{{font-family:{MONO};font-size:21px;color:{MUTED};letter-spacing:.5px;margin-bottom:18px}}
.host b{{color:{accent}}}
.name{{font-family:{MONO};font-size:56px;font-weight:700;line-height:1.0;color:{INK_BRIGHT};
 margin-bottom:20px;max-width:900px}}
.tag{{font-size:28px;line-height:1.3;color:#c9d1d9;max-width:900px;font-weight:400}}
.glyph{{position:absolute;right:90px;top:50%;transform:translateY(-50%);font-size:130px;opacity:.9}}
</style></head><body>
<div class=bar></div>
<div class=glyph>{cfg['glyph']}</div>
<div class=wrap>
 <div class=host>github.com/<b>{owner}</b></div>
 <div class=name>{_esc(cfg['name'])}</div>
 <div class=tag>{_esc(cfg['tag'])}</div>
</div></body></html>"""


# ------------------------------------------------------------- flow diagram ----
# Flow box lines accept inline HTML/entities ON PURPOSE — a diagram may use &nbsp;,
# &ge;, <br> for alignment. The skill authors these intentionally, so they are NOT
# escaped. Keep real private data out of them regardless.
def box(b):
    """A single node. b keys: title (str), lines (list[str]), accent (hex), width (int|None)."""
    body = "".join(f"<div class=l>{x}</div>" for x in b.get("lines", []))
    accent = b.get("accent", BORDER)
    width = f"width:{b['width']}px;" if b.get("width") else ""
    return (f'<div class=box style="{width}border-color:{accent}">'
            f'<div class=bt>{b["title"]}</div>{body}</div>')


def _element(el):
    """Render one vertical-flow element. Types:
      boxes  {boxes:[box,...]}      one row, side by side
      arrow  {}                     down arrow
      merge  {}                     ◢  ◣ merge glyph (two branches → one)
      note   {text:str}             italic caption between stages
      side   {box:box, note:str}    a box with a monospace side-tag to its right
    """
    t = el["type"]
    if t == "boxes":
        return '<div class=row>' + "".join(box(b) for b in el["boxes"]) + '</div>'
    if t == "arrow":
        return '<div class=arrow></div>'
    if t == "merge":
        return '<div class=merge>&#9698;&nbsp;&nbsp;&#9699;</div>'
    if t == "note":
        return f'<div class=note>{el["text"]}</div>'
    if t == "side":
        note = el.get("note", "")
        return (f'<div class=side>{box(el["box"])}'
                f'<div class=sidetag>{note}</div></div>')
    raise ValueError(f"unknown flow element type: {t}")


def flow_html(cfg, height=840):
    """Vertical flow/architecture diagram. cfg keys:
      owner   (str)   defaults to DEFAULT_OWNER
      repo    (str)   shown in the header line
      title   (str)   big title under the header
      elements (list) ordered flow elements (see _element)
    """
    owner = _esc(cfg.get("owner", DEFAULT_OWNER))
    repo = _esc(cfg.get("repo", ""))
    title = _esc(cfg.get("title", "Architecture"))
    flow = "\n".join(_element(e) for e in cfg["elements"])
    return f"""<!doctype html><html><head><meta charset=utf-8><style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1280px;height:{height}px;overflow:hidden}}
body{{background:{BG};font-family:{FONT};color:{INK};padding:52px 60px;
 background-image:radial-gradient(800px 400px at 50% -10%, #3fb95018, transparent 60%)}}
.h{{font-family:{MONO};font-size:22px;color:{MUTED};margin-bottom:6px;text-align:center}}
.t{{font-size:30px;font-weight:700;color:{INK_BRIGHT};text-align:center;margin-bottom:34px}}
.flow{{display:flex;flex-direction:column;align-items:center;gap:0}}
.row{{display:flex;justify-content:center;gap:80px;align-items:stretch}}
.box{{background:{SURFACE};border:1.5px solid {BORDER};border-radius:12px;padding:18px 22px;
 min-width:300px}}
.bt{{font-family:{MONO};font-size:21px;font-weight:700;color:{INK_BRIGHT};margin-bottom:8px}}
.l{{font-size:18px;color:{MUTED_2};line-height:1.5}}
.arrow{{width:2px;height:34px;background:#3fb950;position:relative;margin:6px 0}}
.arrow:after{{content:'';position:absolute;bottom:-1px;left:-5px;border:6px solid transparent;
 border-top-color:#3fb950}}
.side{{display:flex;align-items:center;gap:14px}}
.sidetag{{font-family:{MONO};font-size:16px;color:#3fb950;max-width:200px;line-height:1.4}}
.note{{font-size:16px;color:{MUTED_3};font-style:italic;margin:4px 0 2px;max-width:420px;text-align:center}}
.merge{{font-family:{MONO};color:#3fb950;font-size:26px;line-height:1}}
</style></head><body>
<div class=h>github.com/{owner} · {repo}</div>
<div class=t>{title}</div>
<div class=flow>
{flow}
</div>
</body></html>"""
