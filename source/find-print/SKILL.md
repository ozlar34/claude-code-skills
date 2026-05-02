---
name: find-print
description: Find proven 3D printable designs based on a natural-language description. Searches MakerWorld + Printables, filters by community-validation thresholds, and presents top options with links. Configure your printer and material defaults below.
allowed-tools: WebSearch,WebFetch
---

# Find Print — 3D Design Finder

Find proven, printable designs based on a natural language description. Quality-gated to filter out low-engagement uploads.

## When to Use

Activate when the user:
- Describes something they want to 3D print
- Asks to find a design/model/STL for something
- Says "find print", "find me a print for...", "I want to print a..."

## Printer Context

<!-- EDIT THESE TWO LINES FOR YOUR SETUP -->
- **Printer:** <YOUR_PRINTER_MODEL> (e.g., Bambu Lab P1S, Prusa MK4, Voron 2.4)
- **Materials available:** <YOUR_MATERIALS> (e.g., PLA and PETG)

## Flow

### Step 1: Understand the request

Read the user's description. If any of these are ambiguous, ask ONE clarifying question before searching:
- **Quantity/capacity** (e.g., "how many cards?", "how many pens?")
- **Size/fit constraints** (e.g., "what diameter?", "desk-mounted or wall-mounted?")
- **Style preference** (e.g., "minimal or decorative?")

Do NOT ask if the request is already clear enough to search. Bias toward searching, not questioning.

### Step 2: Search

Run two parallel searches:
1. `[item description] MakerWorld` (add your printer brand if relevant, e.g. "Bambu Lab")
2. `[item description] 3D print Printables best rated`

Add relevant qualifiers from the user's description (e.g., "minimal", "wall mount", "gridfinity").

### Step 3: Fetch details

For the top 3-5 results that look promising from search snippets, attempt to fetch the page for details:
- Title, creator
- Print time, material, supports needed
- Download count, likes/rating
- Key specs (dimensions, capacity, etc.)

If a page blocks scraping (403), use whatever metadata the search results provided.

### Step 4: Filter — Quality Gates

Apply these minimum thresholds:

| Platform | Minimum Downloads | Minimum Likes/Rating |
|----------|------------------|---------------------|
| MakerWorld | 50+ downloads | 20+ likes |
| Printables | 100+ downloads | 4.0+ rating |

- Designs below these thresholds: **exclude entirely** unless nothing else is available, in which case flag as "Unproven — low community validation"
- Prioritize designs that mention compatibility with your printer brand
- Prioritize designs that need no supports (easier print)

### Step 5: Present results

Present 3-5 options in this format:

```
### [Item] — Top Options

**1. [Design Name]** ([Platform])
- **Specs:** [relevant to query — capacity, dimensions, etc.]
- **Material:** [recommended material] | **Print time:** [estimate] | **Supports:** [yes/no]
- **Stats:** [downloads] downloads, [likes/rating]
- **Note:** [one-line verdict — why this one is good or what to watch out for]
- [View on Platform](link)
```

Rank by: reliability (stats) first, relevance to user's specific need second.

End with a short recommendation: "For your use case, I'd go with #X because..."

## Rules

- Never present a low-engagement design without flagging it
- Always include direct links to the design page
- Match the suggestion scale to the user's actual need (don't suggest a 16-slot holder when they need 2 slots)
- If nothing good is found, say so honestly — don't pad results with bad options
- Do NOT download files, track prints, or maintain any database — this skill only finds and recommends
