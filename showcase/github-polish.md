# github-polish

**Status:** Showcase only. Source not published — it renders against a private brand template (my accent palette, glyph set, card/banner/diagram specs) and assumes a particular asset directory + `gh` auth. The *workflow* — survey, plan, autonomous CLI pass, honest UI handback — is the transferable part. This very repo's social card and banner were produced by it.

## Problem

A job-search GitHub profile lives or dies on first impression: a recruiter skims the pinned repos for ten seconds each. A repo with an empty description, no topics, a wall-of-text README, and no visual identity reads as abandoned — even when the code is good. Polishing each repo by hand is fiddly and inconsistent, and the inconsistency itself is a tell (every repo looking different says "no system here").

I wanted one pass that makes any public repo look deliberate and on-brand, does every machine-doable part itself, and is **honest** — no faked screenshots, no invented metrics, no claimed capabilities the repo doesn't have. An oversold repo is worse than a plain one, because the gap surfaces in the interview.

## Architecture

A four-phase pipeline with a hard CLI/UI boundary and a small set of non-negotiable integrity rules.

**The integrity rules come first because they're the whole point:**

1. **Honesty over polish** — never fabricate a usage screenshot, never invent a metric. If the honest asset is a real capture I can't produce (a terminal session, the running app), write a capture walkthrough and put it on the human's todo list instead of faking it.
2. **No private data in public assets** — placeholder data only (`Company A–I`, generic roles, round numbers); scrub names, paths, emails, keys, internal URLs before anything is committed or rendered.
3. **Know the CLI/UI boundary** — `gh` owns topics, description, file commits, pushes. It *cannot* set pin order or upload a social-preview image; those are UI-only and go on the handback list every time, never faked as done.
4. **A README that lies is worse than one that's ugly** — surgical edits only; never "fix" a path or command without verifying it's actually stale.

## Skill workflow

> User: "/github-polish my-repo" (or "polish my-repo", or "this repo looks bare, fix it up")

### 1 — Survey
Clone (or use cwd), read the metadata (`gh repo view --json …`), read the README end to end, the file tree, the languages, any existing diagrams. Diagnose against a known quality bar (my best shipped repos) — weak description, generic/missing topics, no LICENSE, wall-or-stub README, no worked-example framing, no social card, real structure that's never shown.

### 2 — Plan
Print **one** short prioritized plan, each item tagged `[CLI]` (I'll do it) or `[UI]` (goes to your todo list). This is the single approval surface. A `--dry-run` flag stops here — and the first run on any repo *is* a dry run, so the plan can be sanity-checked before edits.

### 3 — Execute (autonomous, atomic commits, push)
Everything `[CLI]` in one pass, no per-step gates:
- **Metadata** — real searchable topics from the actual stack; a one-line description that says what it is and why it's interesting.
- **README** — surgical edits toward a *worked-example* frame ("this is the system I built for X; treat it as a worked example, not a template" — which turns a personal project into a credibility signal). Collapsible `<details>` for long blocks; every accurate path/command preserved.
- **Branded social card** (1280×640) — rendered from a per-repo config against the shared brand template; staged for UI upload (rule 3), never committed.
- **README header banner** (1280×320) — the 4:1 letterhead *is* committed and embedded above the H1, so a visitor landing on the repo page sees the brand immediately (the social card only ever shows on share links).
- **Architecture diagram** — only if there's real structure to show; otherwise skipped gracefully (rule 1 — don't invent architecture for a picture).
- **Verify every embedded image resolves** — `curl` each raw URL for a 200 before declaring done; a broken README image is worse than none.

### 4 — Handback ("your turn")
A precise, ordered todo list of the UI-only things: recommended pin order with reasoning, exact social-preview upload paths + the Settings location, and step-by-step capture walkthroughs for any real screenshot needed — never fabricated.

## Reusable patterns

**1. Encode integrity rules as rules, not vibes.** For anything public and consequential, the "never do this" list (don't fake, don't leak, don't lie about paths) is more important than the feature list. Put it at the top of the skill and make the model internalize the *why*, so it holds under autonomy.

**2. A hard CLI/UI boundary prevents the worst failure.** The skill knows exactly what the API can and can't do. It never pretends a UI-only action (pin order, image upload) is done — those always route to a human handback. Blurring this is how an autonomous agent silently lies about its own output.

**3. Autonomous between two gates.** One plan up front, one handback at the end; everything in between runs without per-step approval. `--dry-run` (and a forced dry-run on first contact with any repo) gives a cheap preview before the autonomous pass.

**4. A shared brand template is what makes a profile read as a system.** Per-repo configs (accent, glyph, chips) feed one renderer, so every card/banner is a member of the same family. Consistency is the signal; the renderer enforces it for free.

**5. Commit the banner, stage the card.** They're different assets for different surfaces: the 4:1 banner is a letterhead embedded in the README (committed); the 2:1 social card only appears on share links and must be uploaded via UI (staged, not committed). Knowing which goes where avoids burying a real screenshot under a second hero image.

**6. Verify embedded assets resolve before declaring done.** A README that references `docs/banner.png` on the wrong branch shows a broken-image icon — a worse look than no image. One `curl` per asset closes that gap.

## What I'd change to publish this

A runnable version would need:

- Your own brand spec — accent palette, glyph set, and the card/banner/diagram layout templates the renderers draw against. Mine are bespoke; the *schema* (a per-repo JSON config feeding shared renderers) is the part to copy.
- An asset directory convention + `gh` authenticated as you.
- A rendering toolchain (mine is headless-browser-based) — or swap in any image generator that can take a structured config and emit consistent cards.

The leverage isn't my visual identity — it's the **survey → one-plan → autonomous-CLI → honest-handback** loop with the integrity rules baked in. That structure transfers to any "make this artifact presentable, do the machine parts, hand back the human parts" task.
