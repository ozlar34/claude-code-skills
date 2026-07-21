---
name: triage
description: "Triage items sitting in the canonical Inbox/ (web-clipper, Raindrop, Telegram, manual). THREE modes. Dedicated commands: `/triage-propose` (Mode A — async analysis, stages proposals, Telegram push) and `/triage-review` (Mode B — apply staged proposals). Bare `/triage` runs Mode C — the legacy per-clipping interactive walkthrough, bounded to 2 actionable verdicts/session. If .triage/pending.json exists when running bare, offers to switch to review mode instead. Atomicity is promote→flip→destruct, `hold` exempt; resource notes delegate to `obsidian-write`."
allowed-tools: Bash,Read,Write,AskUserQuestion,Skill,Agent,mcp__ticktick__add_task
---

# Triage Skill

Triage items the user dropped into the canonical inbox — web clips, Raindrop exports, manual pastes, or Telegram voice/text captures. Triage is **mechanical, one file at a time** — verdict → promote → flip → archive.

This skill is a verdict-loop closer — verdict → promote → flip → archive. Unlike a pure frontmatter-flip closer, clippings carry a **destructive op** at the end (archive `mv` or `rm`), so the atomicity ordering is **promote → flip → destruct**. The flip is the stamp that says "if my next step fails, the queue can resume here without re-triaging." One verdict — `hold` — is exempt: it deliberately keeps a clipping in `Inbox/` untouched for a future run, performing no promote, flip, or destruct. It is the supported way to say "decide this later" without silently abandoning the file.

---

## Modes & routing

`/triage` has three modes. Parse the skill argument first and branch:

| Argument | Mode | What runs |
|----------|------|-----------|
| `propose` (aliases: `scan`, `batch`, `async`) | **A — Propose** | Fan out one read-only subagent per clipping → stage proposals to `.triage/pending.json` → push a summary to Telegram. **Writes nothing to the vault.** Jump to **Mode A — Propose**. |
| `review` (aliases: `execute`, `apply`, `confirm`) | **B — Review** | Load `.triage/pending.json` → walk proposals (accept-all default) → run the real promote→flip→destruct on confirmed verdicts. Jump to **Mode B — Review**. |
| *(empty)* | **C — Interactive** | The legacy per-clipping walkthrough below, bounded to 2 actionable verdicts. **But first:** if `.triage/pending.json` exists and is non-empty, tell the user a pending proposal queue exists and offer to run Review instead. |

Modes A and B are a **propose-then-execute split**: A is the autonomous analytical pass the user
kicks off whenever (then walks away — his phone gets the action list), B is the fast confirm
pass that actually empties the inbox. C is the original all-in-one interactive flow, untouched.

The split exists because the analytical work (read + fit-scan + enrich) is what's slow and
benefits from per-clipping context isolation, while the *destructive* work (mv/rm/flip) is what
must never happen without the user's confirm. A separates the first from the second; B gates the second.

**Why subagents and not a Workflow:** at typical inbox volume (a handful at a time) plain parallel
subagents give the context-isolation win without the Workflow harness's filesystem dance. If inbox
volume ever grows past ~15 routinely, the clean upgrade is to wrap Mode A's fan-out in a `Workflow`
fanning `agent()` calls with the same schema — the analysis protocol file already is the agent spec.

Shared setup (path resolution below) runs for **all three modes**.

---

## Source of truth: `vault-paths.json`

All vault paths come from `.planning/vault-paths.json` in the project dir. **Never hard-code vault folder names.** If the user has restructured the vault, the JSON is the only place that knows.

Keys consumed:
- `vault_root` — absolute path to the Obsidian vault root
- `vault_root_by_user` — *(optional)* per-user override map (`{ "<login>": "/abs/path/to/vault" }`) for when the same project dir syncs across machines with different home paths; the current user (`basename "$HOME"`) is looked up here first, falling back to `vault_root` when absent
- `inbox` — where unprocessed clippings live (the only place this skill pulls from)
- `resources` — `Resources/` (used only to *compose* resource-note bodies; actual write goes via `obsidian-write`)
- `areas` — `Areas/` (used by `act` + `backlog` to list candidate area notes at runtime)
- `system` — `_System/` (also listed for `act` + `backlog`; the Tool Backlog at `_System/Claude Code/Tool Backlog.md` is surfaced explicitly via `$TOOL_BACKLOG` since it sits below the top-level glob)
- `archive` — `Archive/` (root of cold storage; this skill writes to `<archive>/Source/<YYYY>/`)

Resolve at session start (before any read or write):

```bash
VAULT_PATHS="$HOME/<project>/.planning/vault-paths.json"
VAULT_ROOT=$(jq -er --arg u "$(basename "$HOME")" '.vault_root_by_user[$u] // .vault_root' "$VAULT_PATHS")
[ -d "$VAULT_ROOT" ] || { echo "vault-paths.json: resolved vault_root '$VAULT_ROOT' is not a directory on this host — refusing to guess" >&2; exit 1; }
INBOX=$(jq -er '.inbox' "$VAULT_PATHS")
RESOURCES=$(jq -er '.resources' "$VAULT_PATHS")
AREAS=$(jq -er '.areas' "$VAULT_PATHS")
SYSTEM=$(jq -er '.system' "$VAULT_PATHS")
ARCHIVE=$(jq -er '.archive' "$VAULT_PATHS")
# `jq -er` (NOT `jq -r`): -e forces non-zero exit on missing/null key.

# The Tool Backlog (the CC-tool sink) lives ONE LEVEL DEEPER than the top-level
# `$SYSTEM/*.md` destination glob reaches — `_System/Claude Code/Tool Backlog.md` —
# so `act`/`backlog` never surface it and the proposer guesses a wrong path. Surface
# it explicitly. We do NOT glob `_System` recursively (that floods the candidate list
# with every `Tool Notes/<tool>.md`); the Tool Backlog is the one nested sink worth knowing.
TOOL_BACKLOG="$VAULT_ROOT/$SYSTEM/Claude Code/Tool Backlog.md"

# Staged-proposal queue (Modes A + B). A *working artifact*, NOT vault content —
# lives in the project dir (gitignored), survives a /clear between propose and review.
TRIAGE_STATE="$HOME/<project>/.triage"
PENDING="$TRIAGE_STATE/pending.json"
# Plugin/system files in Inbox/ that are never triage subjects — excluded from all ls snapshots
INBOX_EXCLUDE="_Triage Queue.md"
```

If `vault-paths.json` is missing OR any key is empty, **stop and tell the user** — do not guess paths.

---

ALWAYS write via tempfile-rename — protocol: ~/<project>/.claude/lib/write-discipline.md

The destructive ops (`mv` of the clipping to archive, `rm` for `ignore`) are already atomic on APFS — no `.tmp` indirection needed.

---

## Session budget — every 2 actionable verdicts, hand off to a fresh session

This skill is bounded per invocation: it stops after **2 clippings receive an actionable verdict** (`act`, `save`, `backlog`, or `ignore`). `hold` does NOT count — it is zero-write and produces no context bloat, so a single session can absorb arbitrarily many `hold`s while still resolving up to 2 actionable items.

At the threshold, print a continuation prompt (Step 8.5) and stop the loop. The remaining inbox items will be picked up by the next `/triage` invocation from a cleared session.

Rationale: long triage runs accumulate verdict-by-verdict context that biases later proposals toward "I've already seen things like this, default to backlog." Bounding the session keeps every clipping seen with a fresh analytical lens and keeps token spend predictable.

**Counter mechanic:** initialise `ACTIONABLE_COUNT=0` at the top of the snapshot loop. Increment it inside Step 6, but ONLY for the four actionable verdicts (`act`, `save`, `backlog`, `ignore`). `hold` is exempt — it skips Steps 4–7 entirely, so the counter never advances on a held clipping. After Step 8, Step 8.5 evaluates the threshold against `ACTIONABLE_COUNT` + remaining-inbox count.

---

## Frontmatter contract (Phase 01 schema)

Every clipping in the inbox carries (or will carry, after you patch it) the Phase 01 frontmatter schema:

```yaml
---
note_type: source            # required; one of the Phase 01 enums
captured_from: <source>      # web-clipper | telegram | manual | raindrop
captured_at: 2026-05-19      # ISO date the clipping was captured
processed: false             # flips to true the moment you commit a verdict (after promote, before mv)
tags: [...]                  # optional, from the clipper or added during triage
---
```

**Atomicity rule (load-bearing):** `processed: true` MUST be written to the clipping AFTER the promote step (area-note bullet / resource-note creation) and BEFORE any `mv` / `rm` operation. If the destructive op fails mid-flight, the next run sees a processed-but-still-in-inbox file and can recover by completing the move, rather than silently re-triaging. The promote step precedes the flip because the promote is itself recoverable (a duplicate bullet is annoying but not destructive), but if it fails AFTER the flip, the clipping would be marked processed without the back-link in place. The `hold` verdict sits outside this ordering entirely — it performs no promote, no flip, and no destructive op, so there is no atomicity concern; the clipping is left exactly as-is.

---

## The 5-verdict matrix

For each clipping, choose exactly one verdict. **Verdicts are mutually exclusive — never combine.**

| Verdict   | Meaning                                                                 | Promote (Step 4)                                                                                                                                                       | Destructive op (Step 6) |
| --------- | ----------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- |
| `act`     | This clipping triggers a concrete next action right now.                | Append a bullet to a user-chosen area note's section (default `## Notes`); optional TickTick task at Step 7.                                                            | `mv` to archive          |
| `save`    | Durable reference value — worth a clean resource note for future retrieval. Proposer classifies a `save_subtype`: reference, person, place, or long-form. | Forks on `save_subtype` (proposer-supplied; in Mode C derived from the Step 2c proposal): **reference** → `obsidian-write` (`mode=create-new`), Naming Gate + Resource→Area auto-backlink (current path); **person** → direct Write to `People/<Name>.md`, create-or-append per `save-routing.md`; **place** → direct Write to `Places/<Place>.md`, create-or-append per `save-routing.md`; **long-form** → spawn a `/summarize` sub-agent (minimal mode) that mints the summary note inline; no TickTick task. All four sub-routes keep verdict `save`. | `mv` to archive          |
| `backlog` | Useful-but-not-now — worth keeping for later, but not yet a clean note.   | Append a bullet to a user-chosen area note's `## Backlog` section (auto-create section if missing).                                                                     | `mv` to archive          |
| `ignore`  | Noise, duplicate, stale link, or context the future you won't need.    | None.                                                                                                                                                                  | `rm` (no archive copy)   |
| `hold`    | Decision consciously deferred — keep this clipping in `Inbox/` for a future run.        | None.                                                                                                                                                                  | None — file stays in `Inbox/`, byte-identical, `processed: false` |

**Four of the five verdicts (`act`, `save`, `backlog`, `ignore`) end with the file out of `Inbox/` and `processed: true` written.** `hold` is the deliberate fifth path: the clipping stays in `Inbox/`, byte-identical, `processed: false`, to be re-surfaced in the next run. `hold` is a *conscious* deferral chosen at Step 3 — not an accidental escape hatch. Every clipping must still receive an explicit verdict; what's forbidden is silently abandoning a file mid-loop. If a clipping resists classification, either ask the user for a real verdict or choose `hold` deliberately.

---

## Archive destination shape

For `act`, `save`, and `backlog` verdicts:

```
$VAULT_ROOT/$ARCHIVE/Source/<YYYY>/<original-filename>.md
```

- `Source` is a fixed subfolder name (cold storage of triaged source material — distinct from `source::` as a frontmatter field)
- `<YYYY>` is the year from `captured_at` if present, else current year
- Filename is preserved verbatim (no rename) so existing back-links keep resolving
- Create the year folder if it doesn't exist (`mkdir -p`)

Compute the archive path BEFORE any area-note write or resource-note composition, so the back-links can reference the future archive location and resolve once the `mv` completes at Step 6.

---

## Mode C — Interactive (operating procedure, per clipping)

This is the original all-in-one flow, reached by bare `/triage` (no argument). Modes A and B
reuse its building blocks: Mode A's subagents borrow the Step 2a fit-scan logic (read-only, via
the analysis-protocol reference), and Mode B's executor reuses Steps 4–7 verbatim to apply a
confirmed verdict. Keep those steps the single source of truth — don't fork the promote/flip/
destruct logic into the new modes.

For each `*.md` file currently in `$VAULT_ROOT/$INBOX/`:

### Step 1 — Discover

```bash
ls "$VAULT_ROOT/$INBOX/"*.md 2>/dev/null | grep -v "$INBOX_EXCLUDE"
```

If the directory is empty, print "No clippings to triage." and stop. Otherwise, **snapshot this file list once at the start of the run** and iterate the snapshot — don't re-`ls` between clippings. This matters because of `hold`: a `hold` verdict leaves its file in `Inbox/`, so a fresh `ls` mid-run would re-surface a just-held file in an endless loop. Iterating a fixed snapshot guarantees each clipping is presented exactly once per run; a held file simply reappears in the *next* run's snapshot. Process the snapshot by modification time (oldest first).

If the file's frontmatter already shows `processed: true`, this is a recovery case (a prior run flipped but failed to `mv`). Skip to Step 6 — compute the archive path and complete the move. Do not re-promote or re-prompt.

### Step 2a — Full read + system-fit scan

`Read` the **full** clipping body (no truncation — the fit-scan needs the whole thing; truncation is the root cause of "everything looks like backlog").

Resolve the system-fit signals **once per session** and cache them for the snapshot — do not re-`ls` per clipping:

```bash
RESOURCE_BUCKETS=$(ls -1 "$VAULT_ROOT/$RESOURCES" 2>/dev/null)
# sed, NOT `xargs basename`: the vault root may contain an apostrophe,
# which makes `xargs -I{} basename` fail with "unterminated quote" and silently empties the list.
# If Areas are foldered (`Areas/<X>/<X> Hub.md`), a flat glob silently misses every hub — glob
# ONE level deep too (`Areas/*/*.md`); the flat glob still covers top-level area notes.
AREA_NOTES=$(ls -1 "$VAULT_ROOT/$AREAS"/*.md "$VAULT_ROOT/$AREAS"/*/*.md "$VAULT_ROOT/$SYSTEM"/*.md "$TOOL_BACKLOG" 2>/dev/null | sed -E 's#.*/##; s#\.md$##')
```

`RESOURCE_BUCKETS` currently resolves to subfolders like `Career, Citizenship, Claude, Coffee, Finance, German B1, Health, Home Office, Travel` — these are the buckets a `save` verdict would route into. `AREA_NOTES` are the candidate destinations for `act` and `backlog`.

Classify the clipping into one of three fit buckets by cross-referencing its body, title, tags, and (if web-clipper / raindrop / manual) URL against the cached signals:

- **clear-fit** — body clearly matches at least one known Resources subfolder OR Area note. **Name the match** in the display (e.g. "topic = Coffee → fits `Resources/Coffee/` and `Areas/Coffee Hub.md`").
- **weak-fit** — body has partial topical overlap but no obvious bucket; needs investigation before a confident verdict.
- **no-fit** — empty, garbage, dead URL, off-topic from every tracked domain. Default verdict will be `ignore`.

Display: title (or first sentence for telegram), `captured_from`, `captured_at`, fit bucket + named match. Branch source-specifically on display:

**`captured_from: telegram`:** Telegram captures are short transcribed thoughts — no title, URL, or author. Frame the fit-scan around the thought itself ("this thought fits `Areas/<X>`" / "this thought is about <topic>, no clear bucket" / "noise"). Do not attempt to extract a title or source URL; they won't be present.

**`captured_from: web-clipper | raindrop | manual`:** Frame the fit-scan as an external reference fitting (or not fitting) a destination.

### Step 2b — Optional enrichment (smart default with override)

Call `AskUserQuestion` with two options. The default depends on the fit bucket from Step 2a:

| Fit bucket | Default option | Why |
|------------|----------------|-----|
| clear-fit  | **Skip enrichment** (default) | Bucket is obvious; enrichment rarely changes the verdict. |
| weak-fit   | **Enrich** (default) | This is where enrichment pays off — disambiguate the fit. |
| no-fit     | **Skip enrichment** (default) | Heading for `ignore` anyway; no point researching. |

Both options must always appear so the user can override the smart default. Phrase the question so the default is named, e.g. on a weak-fit clipping:

> "Enrich context before deciding? Enrich (recommended for weak-fit — spawn a scoped Explore agent) / Skip"

If user picks **Enrich**, spawn ONE Explore subagent (single Agent tool call, `subagent_type: "Explore"`) with a prompt shaped like:

> Enrich context for a triage decision. Clipping at `<absolute-path>`, captured_from=`<src>`, title=`<title>`. Tell me in under 200 words: (1) what the source is actually about (defuddle the URL in the body if there is one), (2) which vault notes in `Areas/` or `Resources/` it relates to (1–2 targeted greps under `$VAULT_ROOT`, not a full scan), (3) any obvious near-duplicate already in `Resources/<matched-subfolder>/`. Pointers + 1-line summaries, no full content dumps.

Display the agent's brief inline, then proceed to Step 2c with the enrichment in hand.

If user picks **Skip**, proceed directly to Step 2c with scan-only context.

Failure tolerance: if the Explore agent times out or returns nothing useful, treat it as a Skip — proceed with scan-only context and surface the failure in the receipt at Step 8. Do not block the verdict on enrichment.

### Step 2c — Propose verdict with named destination

With the scan + (optional) enrichment in hand, propose a verdict that names the **specific destination**, not just the verdict letter. The proposal is informational — Step 3 is the binding choice — but the more concrete the proposal, the cheaper the verdict is to confirm. Examples by verdict:

- **save (reference)** → "Save as `Resources/Career/<proposed-title>.md` — will mint via obsidian-write; Naming Gate names the final filename (asks only if the pattern is ambiguous)."
- **save (person)** → "Save as `People/<Name>.md` — subject IS a person; create-or-append `## Appearances`."
- **save (place)** → "Save as `Places/<Place>.md` — subject IS a place; create-or-append `## Appearances`."
- **save (long-form)** → "Save (long-form) → spawn a `/summarize` sub-agent on `<url>`; summary note minted inline, clipping archived on success."
- **act** → "Append to `Areas/Coffee Hub.md` `## Notes` + optional TickTick task in `🧭Errands` titled `<proposed-title>`." OR "Append to `Areas/LinkedIn Hub.md` `## Ideas` as `- [AI tools & workflows] <idea>`."
- **backlog** → "Append a row to `_System/Claude Code/Tool Backlog.md` `## Not Yet Assessed` (CC-tool feedback rule)." OR "Append a bullet to `Areas/<X> Hub.md` `## Backlog`."
- **ignore** → "Stale link / duplicate of `Resources/<X>/<existing>.md` / no-fit."
- **hold** → "Defer one cycle — revisit next run."

Proceed to Step 3.

### Step 3 — Confirm verdict

Call `AskUserQuestion` with the 5 verdicts. Adjust option descriptions based on `captured_from`:

**web-clipper / raindrop / manual** (external reference):
1. **act** — "Triggers a concrete next action right now."
2. **save** — "Durable reference value; mint a clean resource note."
3. **backlog** — "Useful later, not now; log to an area note's ## Backlog section."
4. **ignore** — "Noise / duplicate / stale; flip processed and delete."
5. **hold** — "Not ready to decide — keep it in Inbox/ exactly as-is and revisit it on a future run."

**telegram** (personal thought):
1. **act** — "This thought IS the action — do something concrete with it now."
2. **save** — "Worth preserving as a concept note for future retrieval."
3. **backlog** — "Potentially useful later; log to an area note's ## Backlog section."
4. **ignore** — "Noise or already acted on; flip processed and delete."
5. **hold** — "Not ready to decide on this thought — leave it in Inbox/ as-is for a future run."

Trivial `ignore` (empty file, obvious duplicate) can proceed without the question; surface the reason in the receipt at Step 8.

### Step 4 — Promote (write the back-link)

Compute the archive destination first:

```bash
YEAR=$(grep '^captured_at:' "$CLIPPING" | awk '{print $2}' | cut -d- -f1)
YEAR=${YEAR:-$(date +%Y)}
ARCHIVE_DEST="$VAULT_ROOT/$ARCHIVE/Source/$YEAR/$(basename "$CLIPPING")"
ARCHIVE_REL="$ARCHIVE/Source/$YEAR/$(basename "$CLIPPING" .md)"   # for wikilinks
```

Then branch on verdict:

#### `act`

1. `AskUserQuestion`: pick the destination area note. Build the option list at runtime:
   ```bash
   ls "$VAULT_ROOT/$AREAS/"*.md "$VAULT_ROOT/$SYSTEM/"*.md "$TOOL_BACKLOG" 2>/dev/null
   ```
   Present area-note basenames (without `.md`) as options, plus an "Other" escape for non-area destinations. The `$TOOL_BACKLOG` entry resolves to the nested `_System/Claude Code/Tool Backlog.md` — map the chosen basename back to its full path from this same `ls` output (don't re-derive a top-level path).
2. `AskUserQuestion`: pick the section heading inside that area note. Default offering: `## Notes`. Allow the user to supply an alternate heading.
3. `AskUserQuestion`: pick the bullet text. Default = clipping title (web-clipper/raindrop/manual) or first sentence of the body (telegram). **Exception — `## Ideas` in `LinkedIn Hub.md`:** default to the `[pillar]`-prefixed form from the proposal (e.g. `[AI tools & workflows] idea text`). If the proposal carries `[?]`, ask which of the four pillars applies before proceeding.
4. `Read` the chosen area note. Locate the chosen section.
   - **Exception — `## Ideas` in `LinkedIn Hub.md`:** append `- <bullet text>` (no date prefix, no archive wikilink) to match the Hub's established format: `- [pillar] idea`. This is the only section in the skill that uses this stripped format.
   - If section exists, append `- <YYYY-MM-DD> — <bullet text> — see [[<ARCHIVE_REL>]]` as the LAST line of that section (newest-at-bottom).
   - If section is missing, append the section at the end of the file with the bullet as its only entry:
     ```markdown


     ## Notes

     - <YYYY-MM-DD> — <bullet text> — see [[<ARCHIVE_REL>]]
     ```
5. Build the rebuilt area-note body in memory. `Write` to `<area>.tmp`, then `mv -f <area>.tmp <area>` (Phase 7 tempfile-rename).

#### `save`

Detail for person and place sub-routes: `references/save-routing.md`.

Determine `save_subtype` from the proposal: in Mode B it is carried on `proposal.save_subtype`;
in Mode C it is derived from the Step 2c proposed destination (`People/` → `person`,
`Places/` → `place`, `/summarize handoff` → `long-form`, otherwise `reference`).

**reference** (current path — byte-for-byte unchanged):

1. Compose the resource-note body. Branch on `captured_from`:

   **web-clipper / raindrop / manual** (external reference):
   ```markdown
   source:: [[<ARCHIVE_REL>]]

   <first-person summary of the idea — what the clipping is *about*, why it matters, in 2–5 sentences>

   ## Source

   [[<ARCHIVE_REL>]] — <author or publication if present in the clipping>, <captured_at>.
   ```

   **telegram** (personal thought):
   ```markdown
   source:: [[<ARCHIVE_REL>]]

   <The transcribed thought — verbatim or lightly cleaned for readability>
   ```
   Skip the `## Source` section entirely — there is no external author or publication. No first-person reframing; the thought IS the content. The archive wikilink is sufficient for tracing provenance.

   In both cases, `<ARCHIVE_REL>` points at the FUTURE archive path (where Step 6 will move the clipping), so the link resolves after the `mv`.

2. `AskUserQuestion`: working title for the resource note. For web-clipper/raindrop/manual, default = clipping title sanitized. For telegram, propose a short concept title derived from the thought's first sentence. This becomes the `fragment` passed to `obsidian-write`.
3. Invoke `obsidian-write` via the Skill tool:
   - `fragment` = the working title from step 2
   - `mode` = `create-new`
   - `content` = the composed body from step 1
   `obsidian-write` runs its glob-search → Naming Gate (Step 2.5) → write → Resource→Area auto-backlink (Step 3.5) flow. Do **not** re-implement any of those — let the delegate handle them. If `obsidian-write` surfaces an area-backlink failure, surface it through to the user in Step 8 but do not roll back the resource note.

**person / place** (direct write — delegate to `references/save-routing.md`):

1. `ARCHIVE_REL` is already computed at the top of Step 4.
2. Extract `<Name>` (person) or `<Place>` (place) from the proposal's destination string
   (e.g. `People/Ada Lovelace.md` → `Ada Lovelace`). Pass it through `sanitize_title()` before
   any filesystem use (per `save-routing.md` §2).
3. Follow `references/save-routing.md` §4 in full: idempotency check → create-or-append
   `## Appearances` → tempfile-rename write.
4. No `obsidian-write`, no Naming Gate, no Resource→Area auto-backlink.

**long-form** (spawn a `/summarize` sub-agent — never a TickTick task):

1. Extract the URL from the proposal's destination string (`/summarize handoff: <url>` → `<url>`),
   or grep the clipping body for the first `http` URL if absent from the destination.
2. Spawn ONE sub-agent (single `Agent` call, default subagent type) to run `/summarize` on the URL.
   Prompt shape: instruct it to invoke the Skill tool with `skill="summarize"` and `args="<url>"` in
   **minimal mode** (never pass `detailed`), follow that skill exactly, and return ONLY SUCCESS/FAIL
   plus the absolute path of the summary note created. When several long-form saves are confirmed in
   one batch (Mode B), spawn them all in a SINGLE message so they run concurrently — each `/summarize`
   transcription is heavy, and parallel context-isolation is the whole reason this runs as sub-agents.
3. Do NOT compose a note body, do NOT call `obsidian-write`, do NOT create a TickTick task. The
   sub-agent's `/summarize` run IS the promote step — it mints the summary note (+ transcript sibling
   + creator person notes) itself.
4. **Atomicity:** the `/summarize` run is the promote, so flip+archive ONLY on SUCCESS. If the
   sub-agent returns SUCCESS, proceed to Step 5 (flip) and Step 6 (archive) normally. If it returns
   FAIL, DO NOT flip or archive — leave the clipping in `Inbox/`, `processed: false` (an effective
   `hold`), and surface the failure in the Step 8 receipt so the next run retries it.

The reference, person, and place sub-routes proceed to Step 5 (flip) and Step 6 (archive) normally;
the long-form sub-route proceeds only on sub-agent SUCCESS (see its step 4).

#### `backlog`

1. `AskUserQuestion`: pick the destination area note (same runtime listing as `act` — `Areas/*.md` + `_System/*.md` + `$TOOL_BACKLOG` + Other). A CC-tool clipping (a CLI / MCP / plugin / Skill reference) routes to the **Tool Backlog**, per the CC-tool routing rule.
2. `AskUserQuestion`: pick the bullet text. Default = clipping title (web-clipper/raindrop/manual) or first sentence of the body (telegram).
3. **If the chosen destination is the Tool Backlog** (`_System/Claude Code/Tool Backlog.md`), it does NOT use a `## Backlog` section — it is a structurally-managed note. Append a **table row** to its `## Not Yet Assessed` section instead: `| <tool name> | <Type> | <URL> |`, where `Type` ∈ `CLI · MCP · Plugin · Skill · Feature · Other`. Do not invent an author or metadata the clipping doesn't carry. Do not append a `## Backlog` bullet, and do not add a `see [[<ARCHIVE_REL>]]` link (the table has no link column). The note has a normalizer (`~/Scripts/tool-backlog.py`) that keeps it clean — match the existing row shape exactly. **Otherwise** (any normal area note), `Read` it and locate `## Backlog`:
   - If section exists, append `- <YYYY-MM-DD> — <bullet text> — see [[<ARCHIVE_REL>]]` as the LAST line (newest-at-bottom).
   - If section is missing, append it at the end of the file:
     ```markdown


     ## Backlog

     > Auto-maintained by `/triage`. Newest at bottom.

     - <YYYY-MM-DD> — <bullet text> — see [[<ARCHIVE_REL>]]
     ```
4. Tempfile-rename write to the destination note (same as `act` step 5).

#### `ignore`

Promote step is a no-op. Proceed directly to Step 5.

#### `hold`

Promote step is a no-op — and so are Steps 5, 6, and 7. `hold` performs **zero writes**: no back-link, no `processed` flip, no `mv`/`rm`. The clipping is left in `Inbox/` exactly as it arrived. Skip straight to Step 8 (receipt).

`hold` is the deliberate "decide this later" verdict — for a clipping you've consciously chosen to revisit, not one you couldn't be bothered to classify. Because nothing is written, the clipping reappears unchanged in the next run's queue: `hold` defers the decision by one cycle, it does not resolve it.

### Step 5 — Flip `processed: true` (tempfile-rename)

**`hold` skips this step entirely** — it writes nothing. The four other verdicts proceed as below.

Patch the clipping's frontmatter so `processed: false` → `processed: true`. Tempfile-rename:

1. `Read` the full clipping body.
2. Replace the line `processed: false` with `processed: true` in the captured contents (do not touch any other frontmatter key or body byte).
3. `Write` the rebuilt body to `<clipping>.tmp` adjacent to the source.
4. `Bash("mv -f <clipping>.tmp <clipping>")` — APFS-atomic swap.

Never use `Edit` mid-write on the clipping.

### Step 6 — Destructive op

- `act`, `save`, `backlog`:
  ```bash
  mkdir -p "$VAULT_ROOT/$ARCHIVE/Source/$YEAR"
  mv "$CLIPPING" "$ARCHIVE_DEST"
  ACTIONABLE_COUNT=$((ACTIONABLE_COUNT + 1))
  ```
- `ignore`:
  ```bash
  rm "$CLIPPING"
  ACTIONABLE_COUNT=$((ACTIONABLE_COUNT + 1))
  ```
- `hold`: no-op — nothing to move or delete; the clipping stays in `Inbox/` exactly as it arrived. **Do NOT increment `ACTIONABLE_COUNT`** — `hold` is exempt from the session budget (see Step 8.5).

### Step 7 — Optional TickTick task (act only)

After the archive `mv` completes (so the clipping's final path is stable), call `AskUserQuestion`:

> "Capture the action as a TickTick task? Provide a title, or `skip` if already shipped."

If user supplies a title, call `mcp__ticktick__add_task` with:
- `title` = user-supplied string
- `content` = `From clipping [[<ARCHIVE_REL>]]:\n\n<bullet text from Step 4>`

No date/priority — let the user shape it in TickTick.

If user says `skip`, no task is created. Either way, proceed to Step 8.

This step is intentionally LAST and best-effort: a TickTick failure here does not roll back the verdict; the clipping is fully processed.

### Step 8 — Receipt

Append a one-line entry to the session output:

```
<filename> → <verdict> → <action receipt>
```

Examples:
- `foo-bar.md → ignore → flipped + deleted`
- `react-tips.md → save → flipped + Resources/Career/React server components.md created via obsidian-write → archived to Archive/Source/2026/react-tips.md`
- `coffee-grind.md → backlog → flipped + Areas/Coffee Hub.md ## Backlog appended → archived`
- `tax-deadline.md → act → flipped + Areas/Finance Hub.md ## Notes appended → archived → TickTick task created (id: 12345)`
- `half-baked-idea.md → hold → left in Inbox/ untouched, will re-surface next run`

If a side-effect failed after the flip, surface it as a second line:
```
foo.md → save → flipped + atomic-write FAILED: <reason>, ⚠ clipping NOT archived (still in Inbox/)
```

### Step 8.5 — Circuit-breaker (after each actionable verdict)

After Step 8's receipt for an **actionable** verdict (`act`, `save`, `backlog`, `ignore`), check the session budget. `hold` skips this step entirely — it did not increment `ACTIONABLE_COUNT`.

```bash
REMAINING=$(ls "$VAULT_ROOT/$INBOX/"*.md 2>/dev/null | grep -v "$INBOX_EXCLUDE" | wc -l | tr -d ' ')
if [ "$ACTIONABLE_COUNT" -ge 2 ] && [ "$REMAINING" -gt 0 ]; then
  # print continuation block, stop the loop
fi
```

`REMAINING` is recomputed live (not subtracted from snapshot) because `hold`'d files are still physically in `Inbox/` and must be counted toward the next run's queue.

If both conditions are met, print the End-of-run totals (per the section below) AND the continuation block, then stop. Do not advance to the next clipping in the snapshot — even if more clippings remain unprocessed in memory.

Continuation block format:

```
---
Session budget reached (2 actionable verdicts processed).
Remaining in Inbox/: <REMAINING> clipping(s).

Suggested next step: /clear

Paste this in the fresh session to continue:
---
/triage — <REMAINING> items still in Inbox/. Resume the loop on the next snapshot; processed this session: <verdict counts, e.g. 1 save · 1 backlog · 3 hold>.
---
```

Do **NOT** trigger the circuit-breaker if `REMAINING == 0` — finishing the inbox is its own end-state and the End-of-run totals section below covers it.
Do **NOT** trigger if the just-processed clipping received `hold` — `hold` is zero-write and did not increment `ACTIONABLE_COUNT`, so the threshold check would have already been false.

### End-of-run totals

The loop exits via one of two paths:

1. **Snapshot exhausted** — every clipping in the snapshot received a verdict (any of the five). Print session totals.
2. **Circuit-breaker fired** — `ACTIONABLE_COUNT >= 2` and `REMAINING > 0`. Print session totals AS PART OF Step 8.5's output, then the continuation block, then stop.

Session totals: counts by verdict (e.g. `2 act · 1 save · 3 hold`). Note that `hold`'d files stay in `Inbox/` by design, so an empty `Inbox/` is no longer the end-of-run condition — the run ends when every clipping in the snapshot has a verdict OR the circuit-breaker fires.

---

## Mode A — Propose (autonomous analysis, writes nothing)

Reached by `/triage propose`. The job: analyze the **whole** inbox in parallel, one subagent per
clipping, and produce a staged proposal queue + a Telegram action-list. Mode A is **read-only with
respect to the vault** — no `mv`, no `rm`, no `processed` flip, no back-link. It only writes the
proposal queue, which lives outside the vault. Nothing here is irreversible; that's the whole point.

There is **no 2-actionable circuit-breaker in Mode A.** The breaker exists in Mode C to fight the
verdict-quality decay of a long *serial* run. Here every clipping is analyzed in its own isolated
subagent context, so that decay never accumulates — process the entire inbox in one pass.

### A1 — Snapshot + resolve fit signals (once)

```bash
SNAPSHOT=$(ls -1t "$VAULT_ROOT/$INBOX/"*.md 2>/dev/null | grep -v "$INBOX_EXCLUDE")
COUNT=$(printf '%s\n' "$SNAPSHOT" | grep -c . )
if [ "$COUNT" -eq 0 ]; then
  "$HOME/Scripts/tg.sh" "🗂 Triage: inbox empty — nothing to propose."
  echo "Inbox empty. Nothing to propose."; exit 0
fi
RESOURCE_BUCKETS=$(ls -1 "$VAULT_ROOT/$RESOURCES" 2>/dev/null | paste -sd, -)
# sed (NOT `xargs basename`): the vault root may contain an apostrophe,
# which makes `xargs -I{} basename` fail with "unterminated quote" → empty list. sed strips
# the dir prefix + .md suffix without choking on quotes.
AREA_NOTES=$(ls -1 "$VAULT_ROOT/$AREAS"/*.md "$VAULT_ROOT/$SYSTEM"/*.md "$TOOL_BACKLOG" 2>/dev/null | sed -E 's#.*/##; s#\.md$##' | paste -sd, -)
mkdir -p "$TRIAGE_STATE"
```

### A2 — Fan out one read-only subagent per clipping (parallel)

In a **single message**, spawn one `Agent` (subagent) per file in the snapshot. They run
concurrently; each sees only its own clipping. Use this prompt shape for every one:

> Analyze one inbox clipping for a triage decision. **First read** the protocol at
> `~/<project>/.claude/skills/triage/references/analysis-protocol.md` and follow it
> exactly. You are **read-only** — propose only, never write/move/delete/flip anything.
> Inputs:
> - clipping_path: `<absolute path>`
> - vault_root: `<$VAULT_ROOT>`
> - area_notes: `<$AREA_NOTES>`
> - resource_buckets: `<$RESOURCE_BUCKETS>`
> Return the single JSON object the protocol specifies — JSON only, no prose, no fence.

Use the default subagent type (it needs full `Read` + scoped `Bash`/`Grep` for enrichment — not
Explore, which reads excerpts and would undercut the protocol's full-read requirement). Give each a
descriptive label like `analyze: <basename>`.

### A3 — Collect, validate, stage

Parse each subagent's returned JSON. For any that returns malformed JSON or fails, substitute a
safe fallback proposal `{verdict:"hold", confidence:"low", destination:"inbox", rationale:"analysis failed — re-run"}`
so the clipping is never silently dropped.

**Critical: even if every proposal is a fallback hold, proceed to A4 and push the full list.**
Analysis failure ≠ empty inbox. The "inbox empty" notification path exists only in A1 (when
`COUNT == 0` before any subagents run). If you reach A3 with N proposals — even N all-hold
fallbacks — the inbox had N clippings; report them. Track `FAIL_COUNT` (the number of fallback
substitutions) to surface in A4's header.

Then write the queue (tempfile-rename):

```bash
STAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
# Build pending.json: { generated_at, inbox_count, proposals: [ <one object per clipping> ] }
# Each proposal object MUST also carry "file" (absolute path), beyond the protocol's fields.
# Write to "$PENDING.tmp" then: mv -f "$PENDING.tmp" "$PENDING"
```

Each proposal object stored is the protocol's object **plus** a `"file"` key (the absolute path),
so Mode B can act without re-deriving paths.

### A4 — Push the Telegram action-list

Build a phone-skimmable monospace summary and send it. Phone width is narrow, so short lines win.
Send via the `--pre` (monospace) path so columns hold:

```bash
"$HOME/Scripts/tg.sh" --pre "$SUMMARY"
```

**Formatting rules** (apply when building `$SUMMARY`):

- **Verdict glyph** leads every item. All four `save` sub-types use a `save`-family glyph; the
  glyph telegraphs `save_subtype` so the phone skim stays unambiguous:
  `💾 save` (reference) · `👤 save` (person) · `📍 save` (place) · `📝 save` (long-form → /summarize) ·
  `⚡ act` · `📥 backlog` · `⏸ hold` · `🗑 delete` (verdict `ignore`).
  All four save sub-types still emit verdict `save`; the glyph is display only.
- **Title line** = `N <glyph> <title>`. Drop the `.md` extension; clip to ~36 chars with a trailing `…`.
- **Destination** = meaningful tail only, never the full path:
  `Resources/Tech/Foo.md` → `Resources/Tech` ·
  `Areas/Coffee Hub.md ## Notes` → `Coffee Hub ## Notes` ·
  `_System/Claude Code/Tool Backlog.md ## Not Yet Assessed` → `Tool Backlog ## Not Yet Assessed` ·
  `People/Ada Lovelace.md` → `People/Ada Lovelace` ·
  `Places/Berlin.md` → `Places/Berlin` ·
  `/summarize handoff: <url>` → `→ /summarize <url>` (clip URL to ~30 chars with trailing `…`) ·
  `inbox` (hold) → `stays in inbox`.
- **Deletes collapse to 2 lines** — no real destination, so the second line is a `permanent — <rationale>`
  warning instead of a `→ dest` line. This makes the irreversible `rm` items read differently from the
  3-line save/backlog blocks.
- **Confidence** is shown ONLY when `med` or `low` — append `·med` or `⚠low` to the destination line.
  `high` (the common case) is silent.
- **Rationale** wraps to indented continuation lines as needed (don't truncate the reasoning).
- **Source sort** — When building the list, surface `captured_from: telegram` items first (thoughts need action faster than bookmarks). Within each group, preserve original snapshot order. The item numbers (`1`, `2`, `3`, …) reflect this display order, not the `pending.json` order.
- One blank line between items.

Summary template (matching the rules above):

```
🗂 Triage · <N> items
<counts, e.g. 💾 2 save · 📥 2 backlog · 🗑 1 delete>
[⚠ <FAIL_COUNT> analysis failed — re-run to retry]   ← omit this line if FAIL_COUNT == 0
run: /triage review

1 💾 <title clipped, no .md>
  → <dest short>  <·med / ⚠low if not high>
  <rationale, wrapping as needed>

2 🗑 <title clipped, no .md>
  permanent — <rationale>

3 📥 <title clipped, no .md>
  → <dest short>
  <rationale>
```

### A5 — Close

Print to the session: `Staged <N> proposals → Telegram. Run /triage review to confirm + execute.`
If any analyses failed, name the count: `Staged <N> proposals (<FAIL_COUNT> analysis-failed holds) → Telegram.`
Do **not** execute anything. Mode A ends here.

---

## Mode B — Review (confirm + execute the staged proposals)

Reached by `/triage review` (or offered from bare `/triage` when a queue exists). This is where the
inbox actually gets triaged — fast, because the decisions are already made.

### B1 — Load the queue

```bash
if [ ! -s "$PENDING" ]; then
  echo "No pending proposals. Run /triage propose first."; exit 0
fi
```

Read `pending.json`. Print a compact numbered readout (verdict · destination · confidence ·
rationale) and a verdict-count header, so the user sees the whole batch at a glance.

### B2 — Choose the pass

`AskUserQuestion`: **"How do you want to apply these <N> proposals?"**
1. **Accept all** (default) — execute every proposal as proposed. Deletes are confirmed separately (B3).
2. **Review one-by-one** — decide each proposal individually.
3. **Cancel** — leave the queue untouched, exit.

### B3 — Delete gate (always, even under Accept-all)

Before executing **any** `ignore`/`rm`, collect every `ignore` proposal and surface them as one
grouped `AskUserQuestion`: **"These <k> clippings will be permanently deleted (no archive copy):"**
list the basenames + their one-line rationale → options **Delete all listed** / **Keep as hold**
(downgrade those to `hold`, leaving the files in `Inbox/`) / **Cancel**. This is the conservative-
deletion guard — `rm` is the one irreversible op in the whole flow, so it never rides through on a
blanket "accept all".

### B4 — Execute each accepted proposal

For each proposal to apply, **reuse Mode C Steps 4–7 verbatim** — do not re-implement promote/flip/
destruct. The difference from Mode C is only that the proposal **pre-fills the answers** Step 4
would otherwise ask:

- The verdict is `proposal.verdict` (no Step 3 prompt).
- The destination is `proposal.destination`; the bullet/title is `proposal.title_or_bullet`
  (no Step 4 sub-prompts) — **unless** the user picked "Review one-by-one" and chose to change
  the verdict or destination, in which case fall back to the normal Step 4 prompts for that item.
- `save` still routes through `obsidian-write` (Naming Gate may finalize a different filename — fine).
- `act` still offers the optional TickTick task at Step 7.

**Guard before acting on each:** re-check the file still exists in `Inbox/` and is `processed: false`.
If it's gone or already processed (a capture-pipeline race, or triaged in another session since the
propose run), skip it with a one-line receipt — do not error.

There is **no circuit-breaker in Mode B** — proposals were generated with fresh per-clipping context,
so batch execution doesn't degrade quality. Apply them all.

### B5 — Drain the queue

After each proposal is applied (or skipped/held), rebuild `pending.json` with only the *unresolved*
proposals (tempfile-rename). When none remain, `rm -f "$PENDING"`. Print Mode C's Step-8 receipts for
every executed item, then a session-total line. New clippings that arrived after the propose run are
**not** in the queue by design — they'll be caught by the next `/triage propose`.

---

## Hard rules

- **Never** read or write from any vault path not resolved through `.planning/vault-paths.json`. Hard-coding paths is a recurring drift source — Phase 7 paid this debt down once, don't re-introduce it.
- **Always** `jq -er` (not `jq -r`) when reading `vault-paths.json` — fail-closed on missing/null keys.
- **Never** use `Edit` mid-write on a vault file (clipping, area note, or resource note). Always tempfile-rename per the race-mitigation section above. An open Obsidian editor on the MBP may be holding the file (Pitfall 10).
- **Never** flip `processed: true` BEFORE the promote step. The atomicity ordering is **promote → flip → destruct** because clippings have a destructive op — flipping before the promote would mark an un-promoted clipping done if the promote then fails.
- **Never** flip `processed: true` AFTER the destructive op either — if the `mv` succeeded but the flip is still pending, the next run sees an un-marked clipping that is no longer in Inbox/ (impossible to find).
- **Never** mint a resource note by calling `Write` directly — delegate to `obsidian-write` so the Naming Gate AND the Resource→Area auto-backlink (plan §7.1) both fire.
- **Never** combine verdicts. One file → one verdict — `hold` included; you can't `hold` a clipping and also `save` it.
- **`hold` performs zero writes** — no back-link, no `processed` flip, no `mv`/`rm`. A held clipping must be byte-identical to how it arrived. If you find yourself patching a held clipping's frontmatter, you've broken the contract — `hold` means *leave it exactly as it is*.
- **Never** rename the clipping during archive — preserve the original filename so old back-links resolve.
- **Never** leave a blank line between the closing `---` and the first body line when rebuilding frontmatter — Obsidian renders frontmatter as the Properties panel and a blank line produces a visible gap above the first heading. Pattern: `---\n# Heading`, not `---\n\n# Heading`.
- **Never** re-prompt a clipping whose frontmatter already shows `processed: true`. Skip directly to Step 6 to complete the recovery — the user explicitly flipped it; do not second-guess.
- **Four of the five verdicts end with the file out of `Inbox/` and `processed: true`.** `hold` is the deliberate exception — it leaves the clipping in `Inbox/`, untouched, `processed: false`, to be re-surfaced next run. This is not an escape hatch: `hold` is an explicit, chosen verdict for "revisit later", and every clipping must still receive one of the five verdicts. What's forbidden is *silently* abandoning a clipping mid-loop or skipping it — if a clipping resists classification, either get a real verdict or choose `hold` deliberately.
- **Never** keep processing past 2 actionable verdicts in one session if the inbox still has items. The circuit-breaker (Step 8.5) is load-bearing — long sessions degrade verdict quality and burn tokens; a fresh `/clear` is cheaper than a sloppy `backlog`. `hold` does NOT count toward the budget; only `act`/`save`/`backlog`/`ignore` do.
- **Never** truncate the read at Step 2a. The pre-v2 skill read only the first ~10 lines and was the root cause of "everything looks like backlog." The fit-scan needs the full body to produce a confident clear-fit/weak-fit/no-fit classification.
- **Mode A writes nothing to the vault.** Its subagents are read-only proposers — no `mv`, `rm`, `processed` flip, or back-link. The only file Mode A writes is `.triage/pending.json`, which lives in the project dir, not the vault. If a propose run ever mutates a clipping or an Area note, the contract is broken.
- **The "inbox empty" notification fires ONLY from A1, when `COUNT == 0` before any subagents run.** It must never be sent from A3, A4, or A5. If subagents all failed and every proposal is a fallback hold, the inbox is NOT empty — analysis failed. In that case A4 sends the full hold list with a `⚠ N analysis failed` header, and A5 prints `Staged N proposals (N analysis-failed holds) → …`. Never rationalize "nothing actionable = inbox empty."
- **Mode B is the only path that may execute a `save`/`act`/`backlog`/`ignore` from a proposal**, and a proposed `ignore` (`rm`) may only fire after the B3 grouped delete gate. A proposal is a suggestion, never an authorization to delete — the human's confirm in B2/B3 is the authorization.
- **`.triage/pending.json` is a transient working artifact, never vault content and never committed.** It is gitignored. Mode B drains it to empty and `rm`s it when the queue clears; a stale queue is just the next Review's starting point, not a problem.
- **Before executing any proposal in Mode B, re-verify the clipping still exists in `Inbox/` and is `processed: false`.** Proposals can go stale (a capture race, or a parallel triage session). A stale proposal is skipped with a receipt, never forced.
- **person and place saves are written DIRECT via the Write tool** (per `references/save-routing.md`) — **never** via `obsidian-write`. `obsidian-write`'s Resource→Area auto-backlink is meaningless for `People/` and `Places/`, and its `create-new` mode cannot append to an existing note. Only `reference` saves still route through `obsidian-write`.
- **long-form save runs `/summarize` via a spawned sub-agent, NEVER a TickTick task.** Each long-form save spawns ONE sub-agent that runs `/summarize <url>` in minimal mode and mints the summary note inline. Batch confirms (Mode B) spawn all long-form sub-agents in a single message so the heavy transcription runs concurrently in isolated contexts (the confirm loop waits for them — that latency is accepted). Flip+archive ONLY on sub-agent SUCCESS; on FAIL leave the clipping in `Inbox/`, `processed: false` (effective `hold`), and retry next run. Never create a `/summarize` TickTick task and never propose one.
- **person and place routing is PRIMARY-SUBJECT ONLY.** It fires when the clipping's subject IS a person or a place — a profile, bio, or dedicated place note. Never scan the body for merely-mentioned names; that bloat is what `/summarize` minimal-mode deliberately refuses.
- **save content-type routing covers `People/`, `Places/`, and `Resources/Summaries/` only.** `Meetings/` and `Updates/` are explicitly out of scope — they have dedicated writers. All three paths resolve from `vault-paths.json`; never hard-code folder names.

---

## What this skill is NOT

- Not a writer of arbitrary resource notes — only `save` mints resource notes, one per clipping, via `obsidian-write`.
- Not an area-note organiser — `act` and `backlog` append a single bullet; they don't restructure the area note.
- Not a duplicate detector — if two clippings cover the same source, both still get triaged independently (one may verdict `ignore` as duplicate).
- Not a Raindrop / Web Clipper integration — it only consumes files already present in `$VAULT_ROOT/$INBOX/`. Capture lives upstream.
- Not a TickTick task manager — `act` verdicts MAY create a single task as a convenience, but routing/priority/dates/tags are not this skill's concern. The user shapes the task in TickTick.
- Not a way to dodge triage wholesale — `hold` is a real verdict for clippings you've *consciously* decided to revisit, not a silent skip. A held clipping reappears in the very next run's queue exactly as it was; `hold` buys one cycle of deferral, it does not make the clipping go away.
- Not a research engine — Step 2b's optional Explore agent is a *scoped enrichment* (one call, ~200-word brief), not a `/deep-research` substitute. If a clipping genuinely warrants deep research, the right verdict is `act` with a TickTick task that says "run `/deep-research` on `<topic>`."
