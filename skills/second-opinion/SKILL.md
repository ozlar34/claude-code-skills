---
name: second-opinion
description: Get a fresh, independent Opus agent to verify the last load-bearing claim the assistant made — confirmed / refuted / can't tell, with evidence. On-demand capability escalation for cheaper sessions (e.g. Sonnet) that hit a moment where a claim actually matters. User-invocable only (via /second-opinion); does not auto-trigger. This audits the truth of a stated claim — not whether an app runs.
---

# Second Opinion

The user invoked this because the assistant just asserted something that matters and they want a **sharper, independent brain** on it. Often the session is running on a cheaper model (Sonnet) and they want to tap Opus in for one audit without switching the whole session over. The value is twofold: a more capable model, and a *fresh* one that didn't live through this session's reasoning and has no sunk cost in being right.

Your job as the parent agent is to set up that audit honestly, get out of the way, and report what comes back without spin.

## The one rule that makes this work

**Withhold your own reasoning when you brief the Opus agent.**

This is the whole game. If you hand Opus "I checked `parseConfig` and it's fine because the early-return covers the null case," Opus inherits your framing, anchors on your conclusion, and rubber-stamps it. You will have spent Opus tokens to manufacture a more confident version of your own possibly-wrong answer — strictly worse than not running this at all.

So: give Opus the **claim** and the **primitives**, never the justification. Let it form its own view from the actual artifacts.

There are two ways your reasoning leaks in, and both feel innocent in the moment — watch for them:

**Leak 1 — diagnosis smuggled into the claim.** State the claim at the *altitude of the original assertion*, not the altitude of your diagnosis. If the assertion was "this falls back gracefully when Redis is down," that is the claim to verify — not "the `except` only wraps `get()`, leaving `set()` unprotected, so a ConnectionError propagates." The second version has already done Opus's job and handed it the answer to confirm. Verify *what was asserted*, and let Opus discover *why* it's true or false on its own.

**Leak 2 — a "how to check" that telegraphs the answer.** Your check instructions should say *what to examine and how to test it*, never *what you expect to find*. "Pay attention to what `in` costs on a list" points a flashlight at the bug. "Determine the time complexity from first principles, accounting for every operation in the loop body" tells Opus where to look without naming the conclusion.

A test you can apply to your own brief before sending it: **could a reader of this brief guess my verdict?** If yes, you've leaked — strip it back until the brief is genuinely neutral.

### Brief: leaky vs. neutral

**Leaky** (don't):
> Claim: `dedupe()` is O(n²) because `item in result` is a linear scan on a list inside the loop. Confirm the quadratic membership-check cost.

**Neutral** (do):
> Claim: `dedupe()` runs in O(n) time. Artifact: the function below. Determine its worst-case time complexity from first principles, accounting for the cost of every operation in the loop body. Is the O(n) claim right?

## Workflow

### 1. Distill the claim

Identify the last load-bearing claim from your most recent turn — the assertion the turn was building toward, the thing that would matter if it were false. Examples: "the tests pass," "`foo()` handles the empty-list case," "that config key isn't referenced anywhere else," "this is O(n) not O(n²)," "the migration is idempotent."

Reduce it to a **single falsifiable statement**. If your last turn made several claims, pick the one most likely to be load-bearing and wrong; if it's genuinely ambiguous which one the user means, ask before spawning — one short question beats auditing the wrong thing.

Then gather the **raw pointers** Opus needs to check it independently:
- exact file paths (and line ranges / function names) the claim is about
- the precise command(s) that would prove or disprove it (e.g. `npm test`, a specific repro)
- any inputs/fixtures involved
- the verbatim claim, stated neutrally

No analysis. No "I believe." No walkthrough of your logic.

### 2. Spawn a fresh Opus skeptic

Launch a sub-agent via the **Agent tool with `model: "opus"`**. Brief it roughly like this — adapt to the claim, but keep the skeptic's stance and the three-way verdict:

> You are an independent verifier. Another agent claimed: **"<falsifiable claim>"**. Do not trust that framing — it may be wrong. Investigate from the primitives below and reach your *own* verdict.
>
> Artifacts: `<files / functions / line ranges>`
> How to check: `<commands to run / what to read>`
>
> Run the commands and/or read the code yourself. Return exactly:
> - **Verdict:** `confirmed` | `refuted` | `can't tell`
> - **Evidence:** the specific output, line, or reasoning that drove the verdict (concise).
>
> `can't tell` is a legitimate, useful answer — use it when the claim is underspecified, when verifying it would require something you don't have (running state, credentials, a live service), or when the evidence is genuinely mixed. Don't force a binary.

If the claim is checkable by running something, the Opus agent should actually run it (give it the tools/commands), not reason about what would happen.

### 3. Relay verbatim

Paste Opus's verdict and evidence back to the user **as-is**. Do not re-interpret, soften, or argue with it. If Opus refuted a claim you made, resist the pull to add "but technically…" — the entire point was an independent voice, and editing it on the way out hands the last word back to the biased model.

Present it cleanly, e.g.:

```
Second opinion (Opus): REFUTED
> parseConfig throws on a missing file — there's no try/catch and
> readFileSync propagates ENOENT. Repro: `node -e 'require("./config").parseConfig("/nope")'` → throws.
```

### 4. End on the grill offer — and nothing else

Your turn **ends with one line** offering to take it further: e.g. *"Want me to grill this out with Opus, or take it from here?"* This is not optional and not a place to be terse-by-omission — it's the single most-skipped step, so treat it as the required last sentence of the turn.

What must **not** come between the verdict and that offer:

- **No fix.** Don't patch the code, and don't even prescribe the fix ("just wrap `set()` in a try/except" / "replace the list with a set"). A refutation is information, not a mandate — handing the user a fix presumes the verdict is both correct and actionable the obvious way, and quietly takes the decision away from them. They may know the edge case is out of scope, want a different fix, or want to interrogate Opus's reasoning first.
- **No re-litigating.** Don't argue with a `refuted` or soften a `can't tell`. You already relayed it verbatim in step 3; let it stand.

Report the finding, offer the grill, stop. If the user takes the offer, *then* continue the dialogue with the Opus agent (same sub-agent or a follow-up) until it's resolved — and only act on the outcome once they've pointed you at the next move.
