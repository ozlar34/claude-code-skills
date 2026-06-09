# add-watch

**Status:** Showcase only. Source not published — hardcodes a Notion database ID and a curated brand/style/price-range select enum unique to my wishlist.

## Problem

I keep a watch wishlist for two reasons: I sometimes buy them, and more often I research them and decide not to. Without a structured wishlist, I'd re-research the same Longines reference three times across six months and forget why I'd ruled it out the first time.

The bare-data-entry version of this fails because manually filling 12 fields per watch (Brand / Reference / Movement / Caliber / Country of Origin / Style / Case Size / Price Range / Exact Price / Status / Link / Notes) every time I see a watch I like is a 2-minute task that I will not do. The skill collapses it to one URL or one "name + reference" string, and Claude does the spec lookup.

## Architecture

One Notion database, one select-driven row per candidate watch. Properties:

| Property | Type | Notes |
|---|---|---|
| Watch Name | title | Brand + model (e.g. "Longines Conquest Heritage") |
| Brand | select | Curated list of ~40 brands; new ones get added on demand |
| Model/Reference | text | Reference number as given (e.g. "L1.611.4.78.6") |
| Movement | select | Automatic / Manual / Manual-wind / Quartz / Mecha-quartz / Spring Drive / Solar / Other |
| Movement Name | text | Caliber name/number |
| Condition | select | Vintage / Pre-owned / New / TBD |
| Country of Origin | select | Switzerland / Japan / Germany / etc. |
| Style/Type | multi-select | Dress / Diver / Chronograph / GMT / Pilot / Field / Vintage / Everyday / Tool / etc. |
| Case Size (mm) | text | Allows non-round formats like `27 x 32` |
| Price Range (€) | select | Bucketed for filtering: `< 500`, `500-800`, `1000-1800`, etc. |
| Exact Price (new) | number | EUR |
| Link | URL | Source page if there was one |
| Status | select | `Wishlist` (default) / `Researching` / `Ready to Buy` / `Purchased` / `On Hold` |
| Notes | text | Year, key details, "SOLD on source" if applicable |

Page icon is always `⌚` — non-negotiable, set on creation.

## Skill workflow

> User: "/add-watch Longines L1.611.4.78.6"
>
> or
>
> User: "add this watch: https://watches.example.com/longines-conquest-heritage-1955"

The skill runs `WebSearch` (not WebFetch — for structured specs, search results are sufficient and ~3× cheaper), extracts as many of the 12 fields as it can find, and creates the Notion page with everything filled in. Then prompts:

> "Created. Open the entry in Notion and add a cover photo."

That cover-photo reminder is the one thing the skill *can't* do (Notion MCP doesn't accept image uploads), so it always tells the user.

## Empty-field convention

Text fields with no data found are written as `"-"`, not left null. The reason: filtering "no data yet" vs "doesn't apply" matters when scanning the wishlist later. Empty cells are ambiguous; `"-"` is explicit. Select and number fields stay null because Notion handles those filters cleanly.

## Reusable patterns

**1. Web search beats web fetch for structured specs.** A 1,200-character search snippet from Hodinkee gives you brand / movement / case size / approximate price — enough to fill the form. Defuddling a full product page costs 3–8k tokens and adds nothing the form needs.

**2. Curated select enums age in place.** The Brand list has ~40 entries; new ones get added when a watch from a missing brand comes up. The skill is told: "match to existing options if possible, otherwise Notion will create the new option." This keeps the list curated without forcing a brand-management UX.

**3. Empty marker `"-"` for text fields.** Resolves the "is this missing or N/A?" ambiguity at write time. Cheaper than building a separate "data quality" property.

**4. Single-shot creation, no follow-up loop.** The skill creates the entry and stops. It does not chase a cover photo, transition the status, or remind the user later. Different lifecycles (`Wishlist → Researching → Ready to Buy → Purchased`) are manual transitions in Notion. The skill is a capture path, not a workflow engine.

**5. The reminder for what the skill can't do.** Cover photos must be added manually; the skill tells you so on every create. Cheap to surface, eliminates the "did I forget something?" loop.

## What I'd change to publish this

A SETUP.md would need to walk through:

- One Notion database with the 13 properties typed exactly
- Seeding ~40 Brand options + 10 Movement options + ~20 Style options + ~30 Price Range buckets
- Setting `⌚` as the database default icon (or accepting the per-page set)

For watches specifically, the value of this skill is mostly the *capture-with-spec-lookup* loop — which transfers to any wishlist domain (vinyl records, mechanical keyboards, lenses, knives). Recreating the exact watch schema isn't where the leverage is.
