# coffee

**Status:** Showcase only. Source not published — the skill hardcodes Notion database IDs, schema-specific select options, and an equipment inventory unique to my setup.

## Problem

Specialty coffee at home has a few persistent record-keeping problems:

1. **Beans go stale silently.** Without a "days off roast" timer, you reach for a bag that peaked three weeks ago and don't notice why the cup is flat.
2. **Brew adjustments get lost.** You dial in a great recipe, drink three cups over a week, and by the time you brew the same bean again you've forgotten exactly what worked.
3. **Diagnosing a bad cup is muddy.** "Tasted bitter" could mean over-extracted, dark roast, dirty filter, or the beans are old. Without separating the *fault* from the *flavor description*, you can't see patterns.

A flat brew log doesn't solve any of these. You need three relations and one explicit fault axis.

## Architecture

Three Notion databases, all connected by relations:

```
Coffee Stash (bean inventory)
    ↑ relation
Brew Log v2  ──────→  Coffee Recipes
   (one entry          (canonical recipes that
    per brew)           link out to Obsidian notes)
```

**Coffee Stash** tracks: bean name, roaster, origin, region, process, variety, roast level, **roast date** (from the bag, never from a website), decaf flag, and a `Status` field (Current vs Finished). A formula property auto-calculates "Days off Roast" from `today() - Roast Date`.

**Brew Log v2** tracks: bean (relation to Stash), dripper, filter (always specified — different filters = different cups), grinder + grind setting, water temp, dose, water, ratio, brew time, **flavor notes** (descriptive multi-select: Fruity / Chocolatey / Floral / Berry / Citrus / Caramel / Bitter / Sour / Sweet / Clean), **fault tags** (diagnostic multi-select: Clean / Sour / Bitter / Hollow / Astringent / Flat / Muddy / Sharp), brew date, rating, and a recipe relation if the brew traces back to a named recipe.

**Coffee Recipes** is a thin index — entries point out to full recipe notes in Obsidian. Notion is the queryable surface; the actual brewing instructions live as plain markdown.

## Skill workflow

The skill handles three intents, dispatched off natural-language pattern:

### Add a bean to the stash

> User: "bought a bag of Ethiopia from Slurp"

The skill asks for a roast date (taken off the bag, never inferred), confirms roaster + origin + process, optionally fills in variety + region from a quick web search, sets `Status: Current`, and creates the page. Days-off-Roast starts ticking immediately.

### Log a brew

> User: "logged a v60 this morning, La Cabra Colombia, 18g in 270g out, tasted overextracted"

The skill resolves the bean reference against the active stash, suggests a recipe match if one fits, captures the brew parameters, and — critically — separates **flavor notes** ("Bitter") from **fault tags** ("Astringent" / "Bitter"). Same word can appear in both axes; the diagnostic axis is what the user is going to query later when they ask "why did three of my last five brews come out astringent?"

### Suggest brewing parameters

> User: "what grind for this espresso?"

The skill checks the active bean's roast level, age, and roaster's typical profile, factors the brewer (Aeropress with Prismo standard / V60 / FLO Dripper / etc.), and suggests a starting grind on the user's grinder (1Zpresso ZP6 or Varia VS3 V2 in this setup) using each grinder's correct notation (ZP6 uses `X.Y.Z` three-part click notation; getting this wrong is a common LLM failure mode).

## Reusable patterns

**1. Separate descriptive tags from diagnostic tags.** "Bitter" the flavor and "Bitter" the fault are different axes. Free-text notes won't surface patterns; structured fault tags will. This applies to any domain where you want to ask retrospective questions like "what's failing?" — software bugs, training plateaus, recipe failures.

**2. Schema-first MCP calls, always.** Notion is case-sensitive on property names and silently drops unknown select options. Every Notion MCP call in the skill starts with a fetch of the data source schema, then matches property names exactly. This catches drift the moment a property gets renamed.

**3. Multi-select formatting gotcha.** Notion's MCP expects multi-select values as a JSON-array *string*, not a raw array and not a comma-separated string. The skill's `Fault Tags` and `Flavor Notes` fields hit this — codified in the skill so I stop re-discovering it.

**4. Notion as queryable surface, Obsidian as content.** The Coffee Recipes DB is intentionally thin — title + dripper + a link out. The actual recipe markdown lives in Obsidian. Notion gives you `filter by dripper, sort by rating`; Obsidian gives you wikilinks and proper writing. Don't ask one tool to be both.

**5. Token guardrails on a domain skill.** The skill defines hard thresholds: ≥3k projected tokens warns and confirms; ≥10k hard-stops. This matters because adding a bean is cheap but reading every recipe in the index isn't, and the skill needs to know the difference.

## What I'd change to publish this

If the goal were to make this runnable for someone else, the SETUP.md would need to walk through:

- Creating three Notion databases with the exact property types (title / select / multi-select / relation / formula)
- Seeding ~50 select options per multi-select (origin, process, variety, dripper, filter, etc.)
- Wiring the three relations
- Configuring the Days-off-Roast formula

That's a multi-hour onboarding for one user, and the skill's value is mostly in the *patterns* above, not the act of recreating my exact schema. Hence: showcase only.
