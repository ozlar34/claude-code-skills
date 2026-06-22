#!/usr/bin/env python3
"""Render a branded 1280x640 social-preview card from a JSON config.

Usage:
  python3 render_card.py <config.json> <out.png>

The config is the per-repo card spec (accent, glyph, name, tag, chips, foot, owner).
See brand-spec.md for the schema and a worked example. The card template itself lives
in brand.py so every repo stays on the same family look. Run from this directory (or
keep brand.py importable) so `from brand import ...` resolves.
"""
import json
import sys

from brand import card_html, CARD_W, CARD_H
from playwright.sync_api import sync_playwright


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: render_card.py <config.json> <out.png>")
    cfg_path, out_path = sys.argv[1], sys.argv[2]
    with open(cfg_path) as f:
        cfg = json.load(f)
    # A config file may hold {"card": {...}, "flow": {...}}; accept either shape.
    card = cfg.get("card", cfg)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": CARD_W, "height": CARD_H}, device_scale_factor=2)
        pg.set_content(card_html(card))
        pg.screenshot(path=out_path)
        b.close()
    print("card ->", out_path)


if __name__ == "__main__":
    main()
