#!/usr/bin/env python3
"""Render a branded architecture/flow diagram from a JSON config.

Usage:
  python3 render_flow.py <config.json> <out.png> [height]

The config is the per-repo flow spec (owner, repo, title, elements[]). `elements`
is an ordered list of vertical-flow nodes — boxes / arrow / merge / note / side.
See brand-spec.md for the schema and a worked example. Default canvas height is
840px; pass a larger height for longer pipelines so nothing clips. Run from this
directory (or keep brand.py importable) so `from brand import ...` resolves.

Only diagram a repo that has REAL structure worth showing (an existing ASCII
diagram, workflow/config files, a clear module layout). If there's nothing
meaningful to draw, skip this asset rather than inventing architecture.
"""
import json
import sys

from brand import flow_html
from playwright.sync_api import sync_playwright


def main():
    if len(sys.argv) not in (3, 4):
        sys.exit("usage: render_flow.py <config.json> <out.png> [height]")
    cfg_path, out_path = sys.argv[1], sys.argv[2]
    height = int(sys.argv[3]) if len(sys.argv) == 4 else 840
    with open(cfg_path) as f:
        cfg = json.load(f)
    flow = cfg.get("flow", cfg)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1280, "height": height}, device_scale_factor=2)
        pg.set_content(flow_html(flow, height=height))
        pg.screenshot(path=out_path)
        b.close()
    print("flow ->", out_path)


if __name__ == "__main__":
    main()
