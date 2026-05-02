# gaming

**Status:** Showcase only. Source not published — hardcodes a Notion database ID, page ID, and a select-option enum (Status / Genre / Platform / Where I Play) specific to my library.

## Problem

I track every game I've owned, played, beaten, abandoned, or wishlisted in a Notion database. Notion's built-in automations were doing some of the work — when I changed Status to `Currently Playing`, it auto-set Date Started — but Notion Pro automations are flaky, run on a delay, and break silently when you rename a property.

The skill replaces the automation layer entirely with deterministic text-driven updates. Side-effect: the skill is also the only path to *create* an entry, which forces a metadata-completion gate that the bare Notion form lets you skip.

## Architecture

One Notion database with these properties (only the ones the skill cares about):

| Property | Type | Role |
|---|---|---|
| Title | title | Game name |
| Status | select | Single-state machine: `Currently Playing` / `Complete` / `On Hold` / `Abandoned` / `Backlog` / `Want to Buy` / `Unreleased` / `Emulator (Need to Download)` |
| Date Started | date | Side-effect of `Currently Playing` transition |
| Date Finished | date | Side-effect of `Complete` transition |
| Release Date | date | Earliest known platform release |
| Genre | multi-select | Capped at 1–3 tags |
| Mode | multi-select | Singleplayer / Multiplayer / Co-op |
| Platform | multi-select | Every hardware platform the game shipped on |
| Where I Play | select | Where *I* actually play it (single value) |

## Skill workflow

The skill is a pure intent-router. Every input maps to one of these patterns:

| Phrase | Operation | Status set | Date side-effect |
|---|---|---|---|
| "I'm starting / playing / picked up X" | update or create | `Currently Playing` | Date Started = today |
| "I finished / beat / completed / just beat X" | update | `Complete` | Date Finished = today |
| "Pausing / putting X on hold" | update | `On Hold` | none |
| "I abandoned / dropped / gave up on X" | update | `Abandoned` | none |
| "Add X to my backlog" | update or create | `Backlog` | none |
| "I want X / add to wishlist" | update or create | `Want to Buy` | none |
| "Add X" (no status stated) | update or create | **ask** | none |

The two things that make the skill work:

1. **Date side-effects are mandatory and atomic.** Status `Currently Playing` *always* sets Date Started; `Complete` *always* sets Date Finished. Other transitions never touch dates. The user never has to remember to update both.

2. **Creation forces a metadata gate.** When the game doesn't exist yet, the skill asks for Release Date / Genre / Mode / Platform / Where I Play before creating, with sensible defaults proposed from the model's own knowledge. The bare Notion form lets you create with just a title — three months later you have 40 untyped entries you can't filter.

For "Where I Play," the skill uses a small ruleset to suggest a default:

- Xbox One / 360 / Series → suggest `Xbox Series X`
- PC / Steam → suggest `ROG Ally`
- Older console / handheld → suggest `ROG Ally` (emulation)
- Switch → suggest `Nintendo Switch`
- DS / 3DS → suggest `3DS` (emulated for DS)

User confirms or corrects.

## Reusable patterns

**1. Status as state machine, dates as side-effects.** Don't ask the user to update two fields. Pick one field as the trigger, derive the rest. This generalizes to any tracker: applying for a job (status `Applied` → set Date Applied), shipping content (status `Published` → set Publish Date), reading a book (status `Reading` → set Date Started).

**2. The skill is the only path that runs validation.** If you let users edit Notion directly, eventually the data drifts. If the skill is *strictly easier* than opening Notion (which a one-line natural-language update is), the skill becomes the path of least resistance, and the validation runs on every change.

**3. Use the model's pre-cutoff knowledge before web-searching.** Most games have well-known release dates / genres / developers. The skill's default is "use your own knowledge first; web-search only for genuinely obscure or post-cutoff titles." Saves a `WebSearch` round-trip on 90% of inputs.

**4. Confirmation before creation, not before every update.** Updates are one-shot ("I beat Hollow Knight" → done). Creation is the only gate. Calibrating *when* to interrupt for confirmation matters more than always confirming.

**5. Read-only queries are out of scope.** "What am I playing right now?" is not handled by the skill — the user is directed to the Notion page itself. The skill is a write path, not a query path. Trying to make it both bloats the prompt and leaks data into context unnecessarily.

## What I'd change to publish this

The skill's logic is reusable; the schema isn't. To make this runnable, a SETUP.md would need to walk through:

- Creating one Notion database with the 9 properties above
- Seeding ~30 Genre options + ~25 Platform options + 5 "Where I Play" options
- Picking equivalent values in your own setup ("Where I Play" is meaningless if you don't have a multi-platform play split)

Net: not worth shipping as a clone. The patterns transfer cleanly to any tracker domain.
