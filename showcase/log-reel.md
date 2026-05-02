# log-reel

**Status:** Showcase only. Source not published — hardcodes a Notion database ID, page ID, and a publishing-funnel select enum specific to my content tracker.

## Problem

I run a Notion Content Pipeline that's supposed to track every reel / short / video I ship. Realistically, my pipeline always drifts behind the truth: I post a reel on Instagram, I forget to click into Notion to flip the row to `Published`, and three weeks later I'm reading my own tracker and it tells me my last published video was a month ago — which is wrong, but I can no longer reconstruct exactly when the recent ones went live.

The drift compounds. After a few skipped updates, the tracker becomes lossy enough that I stop trusting it for retros or "what's working / what isn't" analysis.

This skill closes the gap by writing the row at *ship time*, voice or text, in 10 seconds, without me having to open Notion.

## Architecture

One Notion database, one row per shipped piece of content:

| Property | Type | Default at ship time |
|---|---|---|
| Title | title | The published title |
| Status | select | **`Published`** (fixed by this skill) |
| Content Type | select | `Long Form Video` / `Short Form Video` (default) / `Static` |
| Channel | multi-select | `["Instagram Reels"]` (default; ask if multi-channel) |
| Publish Date | date | Today (default; override if shipped on a past date) |
| Priority | select | `Medium` (fixed; irrelevant post-ship) |
| Due Date | date | Skipped post-ship |

The full Status enum (`Idea` → `Script Written` → `Shots Planned` → `Content Shot` → `Editing Complete` → `Scheduled` → `Published` → `Archived`) is what the tracker uses pre-ship. The skill only deals with the `Published` transition — that's where the drift problem sits.

## Skill workflow

> User: "just posted a reel — Travel Coffee Setup (Kazbegi, Georgia)"

The skill:

1. **Confirms ship details** in one batch — Title, Channel(s), Ship date (default today), Content Type. Single message, not field-by-field.

2. **Searches the Pipeline DB for an existing row** with a matching title before creating. If a row exists at any pre-Published status (`Idea` / `Shots Planned` / `Editing Complete` / etc.), the skill **updates** that row to `Published` instead of creating a duplicate. This is the dedup gate that keeps "shipped from idea" content traceable end-to-end without manual cleanup later.

3. **If no match, creates a new row** with the defaults above. The user might ship something they never had a pre-shipped row for — improvised content, reposted-from-elsewhere — and that's a normal create-from-scratch path.

4. **Returns the Notion page URL** so the user can drop a thumbnail or move it visually if needed.

## Reusable patterns

**1. Ship-time capture beats post-hoc backfill.** Any tracker that lives in a different tool from the work itself drifts. The fix is not a recurring "update your tracker" reminder; it's a 10-second skill that the shipper invokes *while still in the ship moment*. The cost has to be lower than opening Notion or it doesn't get done.

**2. Dedup before create on a status transition.** When a tracker has a multi-stage funnel (`Idea` → `Shipped`), and the skill always creates a new row, you end up with two entries per shipped piece — one in `Idea` from when you started, one in `Published` from when you shipped. The skill's `notion-search` for matching titles before create avoids this with no user intervention.

**3. Status-driven property defaults.** When the skill *only* runs at one transition point (here, `→ Published`), all property values that are determined by that transition can be hardcoded. Status = `Published`. Publish Date = today. Priority = `Medium` (because nobody cares about pre-ship priority once it's shipped). The user is asked only what *isn't* derivable — title, channel, content type. This collapses the form.

**4. Channel as multi-select with one default.** Most reels go to one channel. Cross-posting (Reels + TikTok, or YouTube Shorts + Reels) is the exception, but the schema needs to support it. The skill defaults to a single-element list, asks only when the user mentions multi-channel posting.

**5. The skill name should match the user's actual phrasing.** "log-reel" works because that's how I'd describe what I'm doing ("logging a reel I just posted"). If the skill were named something like "publish-content-tracker" the trigger pattern wouldn't fire on natural language. Keep the skill name in the user's own vocabulary.

## What I'd change to publish this

A SETUP.md would need to walk through:

- One Notion Content Pipeline database with the 7 properties above
- The Status enum's 8-stage funnel exactly (or your own equivalent — but the skill assumes `Published` is one of the values)
- The Content Type and Channel enums

The pattern (ship-time capture + dedup-before-create) transfers cleanly to any one-transition tracker — job applications shifting to `Applied`, a habit being marked `Done` for the day, a feature flipping to `Released`. The schema specifics are mine; the architecture is the part worth borrowing.
