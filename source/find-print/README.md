# find-print

**Trigger:** "find me a print for…", "I want to 3D print…", "find an STL for…"

**What it does:** Takes a natural-language description, searches MakerWorld and Printables in parallel, applies a community-validation filter (download count + rating thresholds), and presents the top 3–5 candidates with links, print specs, and a one-line verdict on each.

The point is not to find *any* matching design — it's to filter out the low-quality fork-and-upload noise that flooded both platforms and surface only designs other people have actually printed and rated.

**Setup:** see [SETUP.md](./SETUP.md). Two lines to edit.

**Example:**

> User: find me a print for a desktop holder for 4 fountain pens, minimal style
>
> Skill: *(searches both platforms, filters by thresholds, fetches top results)*
>
> ```
> ### Fountain Pen Holder — Top Options
>
> **1. Minimal Pen Stand (4-slot)** (MakerWorld)
> - Specs: 4 pens, 14mm slot diameter, 80×40×60mm
> - Material: PLA | Print time: 1h 15m | Supports: no
> - Stats: 2,300 downloads, 180 likes
> - Note: Single-piece print, no assembly. Tested with Lamy Safari and TWSBI Eco.
> - [View on MakerWorld](...)
>
> [...two more options...]
>
> For your use case, I'd go with #1 — single-piece, tested with comparable pen sizes, highest engagement.
> ```

**Why it exists:** Default search results on both platforms surface popularity, not quality. A first-page MakerWorld search for "pen holder" returns 30 designs, half with single-digit prints. This skill bakes the "is this worth my filament?" filter into the search itself.
