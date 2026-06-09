# pack-trip

**Status:** Showcase only. Source not published — reads a canonical packing template from my Obsidian vault, resolves vault paths through a private config, and writes to a specific project in my task manager (TickTick) via MCP. The assembly logic is the reusable part.

## Problem

Every trip I'd rebuild the same packing list from memory, forget the same two things (power adapter, enough socks), and end up with either a wall of 24 separate to-do items cluttering my task manager or a vague note I never actually checked off.

The list isn't really *new* each time — it's a stable template (universal items + a clothing formula) plus a few trip-specific deltas (climate, occasions, whether I'm filming content). So the skill's job is: take a canonical template, ask only the questions that change per trip, and produce one clean, checkable artifact.

## Architecture

Two pieces, deliberately separated:

1. **A canonical template note in the vault** — the single source of truth for *what* can be packed, organized into blocks: `## Universal (every trip)`, a base-clothing section, `## Occasions` (beach / wedding / city break), `## Climates` (hot / cold / rainy / variable), and conditional gear blocks (coffee-content filming, photography, work trip). The skill **never inlines the items** — it re-reads this note on every run, so editing the template is how you change the packing logic.

2. **One task in the task manager, with the items as a checklist** — not N separate tasks. This was the load-bearing design correction: an early version created ~24 individual tasks per trip and it was unusable noise. One task titled `🧳 Packing for <Trip>`, every item a checklist sub-item, due the day before departure.

## Skill workflow

> User: "/pack-trip Lisbon 4 nights"

1. **Resolve the template** from the vault (via a path-resolver config — never a hard-coded path, because the store can move).
2. **Locate the trip note**, best-effort — glob the travel folder for a partial name match. If one matches, read its `## Practical Info` and any `trip-date:` frontmatter for context (power adapter, weather, dates). If several match, ask which. If none, proceed without it — don't block.
3. **Ask only the deltas**, batched into as few prompts as possible:
   - Duration in nights (drives the clothing formula)
   - Climate (multi-select: hot / cold / rainy / variable — they compose)
   - Occasions (multi-select: beach / wedding / city break / none)
   - Conditional gear — three yes/no questions in *one* prompt (filming? photography? work trip?)
4. **Assemble the list** from the template: universal block always, plus a **clothing formula** derived from nights (`underwear = nights + 1`, `t-shirts = 2 if nights ≤ 3 else 2 + (nights−3)//4`, etc., with the count rendered into the item label — "Underwear (x5)"), plus each selected occasion/climate/conditional block verbatim. Filming + photography together collapse to a combined block so memory cards aren't doubled.
5. **Show the full list grouped by section and wait for an explicit "proceed."** Free-text adds/removes are applied before writing. This is the one human checkpoint.
6. **Collision check** before writing — if a `🧳 Packing for <Trip>` task already exists, offer replace / append / abort rather than silently duplicating.
7. **Create one task, one API call**, with the items as the checklist array, due departure-minus-one, correct timezone. A single call is also what keeps a write-guard sentinel satisfied with one touch.

## Reusable patterns

**1. Template-in-the-store, logic-in-the-skill.** The *what* (the item catalog) lives in an editable note; the *how* (formula, block selection, assembly order) lives in the skill. Re-reading the template every run means I update my packing list by editing a note, never by touching the skill. Nothing is inlined.

**2. One task with a checklist, never N tasks.** When the output is a set of related sub-items, a single parent task with a checklist is almost always right. N separate tasks shred a task manager into noise. This was a real correction, not a hypothetical — the N-task version got rejected on first use.

**3. Ask only the deltas, and batch them.** The universal block and the clothing formula are derivable — never ask about them. Only the per-trip variables (nights, climate, occasions, conditional gear) get a question, and those collapse into the fewest prompts possible (three yes/no gear questions ride in one multi-question prompt).

**4. Compute counts into the label.** "Underwear (x5)" beats five separate "Underwear" checkboxes. The formula output belongs in the item text, so one checkbox carries the quantity.

**5. Best-effort context enrichment that never blocks.** If a matching trip note exists, pull its dates and practical info; if not, proceed without. Optional enrichment should sharpen the output when available and get out of the way when not — never a hard dependency.

**6. Collision check before a create.** A re-run shouldn't duplicate. Check for an existing artifact and offer replace/append/abort — cheap insurance against the second invocation making a mess.

## What I'd change to publish this

A runnable version would need:

- A packing-template file in whatever format you keep notes (the block structure — universal / clothing-formula / occasions / climates / conditionals — is the contract the skill reads against).
- A path resolver, or just a hard-coded template path if you don't move your store around.
- A task-manager target — mine is TickTick via MCP, but the "one task, items as checklist" shape maps to any to-do app that supports sub-items.

The transferable core is the **template → ask-only-deltas → formula → single checklist artifact** pipeline. It generalizes past packing to any recurring checklist that's mostly stable with a few situational deltas — trip prep, event setup, release checklists, onboarding runbooks.
