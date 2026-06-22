#!/usr/bin/env python3
"""Render a branded 1280x320 README header banner from a JSON config.

Usage:
  python3 render_banner.py <config.json> <out.png>

The banner reuses the per-repo `card` spec (accent, glyph, name, tag, owner) — one
config drives both the 2:1 social card AND this 4:1 README letterhead, so they stay a
family. A repo whose card tag is too long to fit one banner line can add a `banner`
key with a shorter `tag` (or any field) — it overlays the card values. Schema +
worked example in brand-spec.md. Template lives in brand.py. Run from this directory
(or keep brand.py importable) so `from brand import ...` resolves.
"""
import json
import sys

from brand import banner_html, BANNER_W, BANNER_H
from playwright.sync_api import sync_playwright


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: render_banner.py <config.json> <out.png>")
    cfg_path, out_path = sys.argv[1], sys.argv[2]
    with open(cfg_path) as f:
        cfg = json.load(f)
    # A config holds {"card": {...}, "flow": {...}}; the banner derives from `card`,
    # with an optional `banner` block overlaying it (e.g. a shorter tag).
    card = cfg.get("card", cfg)
    banner = {**card, **cfg.get("banner", {})}
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": BANNER_W, "height": BANNER_H}, device_scale_factor=2)
        pg.set_content(banner_html(banner))
        pg.screenshot(path=out_path)
        b.close()
    print("banner ->", out_path)


if __name__ == "__main__":
    main()
