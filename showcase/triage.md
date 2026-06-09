# triage

**Status:** Showcase only. Source not published — wired to my Obsidian vault layout (resolved through a private `vault-paths.json`), a Telegram push script, and a sibling `obsidian-write` skill that owns the actual note creation. The architecture is the interesting part; you'd point it at your own store.

## Problem

I have a single canonical inbox folder that fills up from four directions: a browser web-clipper, Raindrop exports, manual pastes, and Telegram voice/text captures. Left alone it becomes a guilt pile — too big to face, and the longer I avoid it the more every item starts looking like "backlog, deal with it later."

Two failure modes kept recurring:

1. **Truncated reads → everything looks like backlog.** An early version read only the first ~10 lines of each clipping to save tokens. With that little context, almost nothing earns a confident "save" or "act," so the lazy verdict (`backlog`) wins by default and the pile never shrinks.
2. **Long serial runs decay.** Triaging 15 items in one session, the later verdicts get worse — "I've seen things like this, default to backlog" — because the accumulated context biases the model toward pattern-matching instead of judging each item fresh.

This skill is the verdict-loop closer, built to defeat both.

## Architecture

One inbox, one file at a time, exactly five mutually-exclusive verdicts:

| Verdict | Meaning | Promote | Final state |
|---|---|---|---|
| `act` | Triggers a concrete next action now | Bullet → an area note's `## Notes`; optional task in my task manager | archived |
| `save` | Durable reference value | Mint a clean resource note (delegated) | archived |
| `backlog` | Useful later, not now | Bullet → an area note's `## Backlog` | archived |
| `ignore` | Noise / duplicate / stale | none | **deleted** (no archive copy) |
| `hold` | Consciously deferred | none | **stays in inbox, byte-identical** |

**The load-bearing invariant is the atomicity ordering: promote → flip → destruct.** Because four of the five verdicts end in a destructive op (`mv` to archive, or `rm`), the order matters:

1. **Promote** first — write the back-link (a duplicate bullet is annoying, never destructive, so this step is safely re-runnable).
2. **Flip** `processed: false → true` second — this is the recovery stamp. If the next step dies, the next run sees a *processed-but-still-in-inbox* file and completes the move instead of re-triaging from scratch.
3. **Destruct** last — `mv` or `rm`.

`hold` sits entirely outside this ordering: zero writes, no flip, no move. The file is left exactly as it arrived and re-surfaces next run. It's the supported way to say "decide later" without silently abandoning a file.

## Skill workflow — three modes

The skill evolved from a single interactive loop into a **propose → review split**, because the slow analytical work and the dangerous destructive work want different handling.

### Mode C — Interactive (the original, still the default)

Bare invocation. Per file: full read → system-fit scan → optional enrichment → propose a verdict with a *named destination* → confirm → promote/flip/destruct → receipt.

- **System-fit scan** classifies each clipping as **clear-fit** (body obviously matches a known resource bucket or area note — *name the match*), **weak-fit** (partial overlap, needs investigation), or **no-fit** (garbage/dead link → defaults to `ignore`). The destination signals (resource subfolders + area notes) are resolved **once per session and cached**, never re-listed per item.
- **Optional enrichment** spawns *one* scoped sub-agent — but only with a smart default: enrich on weak-fit (where it pays off), skip on clear-fit and no-fit (where it won't change the verdict). Both options always shown so the default can be overridden.
- **Session budget / circuit-breaker:** the loop stops after **2 actionable verdicts** (`act`/`save`/`backlog`/`ignore`) if the inbox still has items, prints a paste-ready continuation prompt, and tells me to `/clear`. `hold` is exempt — it's zero-write, so a session can absorb arbitrarily many holds. This is the direct fix for verdict-quality decay.

### Mode A — Propose (autonomous, writes nothing)

`/triage propose`. Fans out **one read-only sub-agent per clipping, in parallel**, each in isolated context. Every agent reads a shared analysis-protocol file and returns a strict JSON object (`verdict` + concrete `destination` + `confidence` + one-line `rationale`). The orchestrator stages all proposals to a gitignored working file and pushes a phone-skimmable action-list to Telegram.

**It mutates nothing in the store** — no move, no delete, no flip. There's no circuit-breaker here, because per-clipping context isolation means the decay Mode C fights never accumulates: the whole inbox is analyzed in one pass. The point is "kick it off, walk away, your phone gets the decisions, review whenever."

### Mode B — Review (confirm + execute)

`/triage review`. Loads the staged proposals, shows a numbered readout, then one `AskUserQuestion`: **accept all** (default) / **review one-by-one** / **cancel**. It reuses Mode C's promote/flip/destruct steps *verbatim* — the proposal just pre-fills the answers. Two guards survive even "accept all":

- **Grouped delete gate:** every `ignore` (`rm`) is collected and surfaced as one explicit confirm before any deletion — the one irreversible op never rides through on a blanket accept.
- **Stale-proposal check:** before acting on each item, re-verify it still exists and is still unprocessed (a capture race or a parallel session may have moved it). Stale → skip with a receipt, never error.

## Reusable patterns

**1. Order destructive loops promote → flip → destruct.** Any triage/cleanup loop that ends in a delete or move needs a recovery stamp written *after* the recoverable work and *before* the irreversible one. The flip is what lets an interrupted run resume instead of re-deciding. Get this order wrong and a mid-flight failure either loses the item or re-processes it.

**2. A zero-write "hold" verdict beats a skip.** Explicitly modeling "decide later" as a first-class verdict that touches nothing is far better than letting items get silently skipped. Held items re-surface next run unchanged; nothing is ever abandoned.

**3. Split the slow analytical pass from the dangerous executing pass.** Reading + classifying is slow and benefits from parallel, context-isolated sub-agents. Moving + deleting is fast but must never happen without a human confirm. Separating them (propose vs review) lets the analysis run unattended while the destruction stays gated.

**4. Per-item sub-agents kill long-run decay.** A serial loop's later verdicts degrade as context piles up. Fanning out one isolated agent per item means every item is judged with a fresh lens — and as a bonus, removes the need for a circuit-breaker in that mode.

**5. Read the whole thing.** The single biggest verdict-quality win was deleting a token-saving truncation. Under-reading produces a confident-looking wrong classification, which is worse than spending the tokens.

**6. Propose a named destination, not a verdict letter.** "save → `Resources/Career/<title>.md`" is far cheaper to confirm than "save." The more concrete the proposal, the less the human has to fill in.

**7. The delete gate never collapses into accept-all.** Even when the user opts to accept every proposal, deletions are surfaced as a separate grouped confirm. Convenience defaults are fine for reversible ops; the one `rm` gets its own gate.

## What I'd change to publish this

The pattern transfers to any inbox-with-a-canonical-store setup, but a runnable version would need:

- A store abstraction in place of my vault — the verdicts (`act`/`save`/`backlog`/`ignore`/`hold`) and the promote→flip→destruct ordering are store-agnostic; the *destinations* (area notes, resource buckets, an archive folder) are mine.
- A notification sink to replace the Telegram push (or just print the action-list to stdout).
- A note-creation delegate for the `save` path — mine hands off to a sibling skill that owns naming + back-linking; a standalone version would inline a simpler "write a file here" step.

The architecture — five verdicts, the atomicity ordering, the propose→review split, per-item agents to beat decay — is the part worth borrowing. The vault wiring isn't.
