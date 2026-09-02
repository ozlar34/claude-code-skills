---
name: learn-from-mistakes
description: Run at the end of a session to extract wrong-mental-model failures (not inefficiencies) and propose surgical, cost-justified CLAUDE.md additions that prevent the same wrong action in future sessions. User-invocable only (via /learn-from-mistakes); does not auto-trigger. Distinct from /session-handoff (which captures work state) — this skill captures behavioral corrections.
disable-model-invocation: true
---

# Learn From Mistakes

Scan this session for a **single class** of failure: moments where Claude acted on a *wrong mental model* of how the user's systems, tools, or conventions actually work. Translate only the ones that clear a high cost bar into one-line imperative directives. Propose them as a single batched approval.

**The default outcome is "nothing cleared the bar this session."** Most sessions produce no rule. That is success, not failure. Every line added to an always-loaded CLAUDE.md is taxed on every future session in every project, forever — so the bar to add one is deliberately high. Proposing a marginal rule just to have something to show is the exact failure this skill must avoid.

## Step 1 — Find wrong-model mistakes only

Scan the conversation for moments where Claude **believed something false about how things work and acted on it** — then had to be corrected or course-correct. Signals:

- The user negated or redirected an assertion/action: "no, actually…", "that's not how it works here", "you assumed…", "that's wrong because…".
- Claude operated on a wrong assumption about a path, file location, tool behavior, convention, or system structure, and the action had to be redone.

**Loops, repeated greps, and "took more steps than needed" are NOT findings.** They are *clues*. When you see one, ask: *was there a wrong belief underneath it?*
- If yes → the **belief** is the candidate (not the loop).
- If no → it was a one-off bad day. Drop it. Do not turn it into a rule.

A generic "don't loop" or "search more efficiently" rule is bloat by definition. Never propose one.

## Step 2 — Two-gate filter

Each candidate must pass **both** gates to earn an always-loaded slot. If it fails either, it is dropped or demoted to Tier-B (Step 3).

1. **Wrong-action gate.** Would *not* having this rule cause Claude to take a substantively *wrong action* in a future session — not merely be slower or take an extra step? Efficiency misses fail here.
2. **Cost gate.** Is the lesson a durable fact about *how the user's systems or conventions work* (broad blast radius), rather than syntax/API trivia that tooling already catches or that's hit-once-and-fixed-in-seconds? Trivia fails here.

Also drop if:
- It's already covered by an existing rule in any CLAUDE.md (read the relevant CLAUDE.md to check — don't guess).
- It arose from genuinely one-off context (a since-deleted file, a confused prompt that got clarified).
- You're not confident it generalizes — **err on the side of dropping.**

**Final gate.** For each survivor, ask: *if this exact sentence had been in CLAUDE.md at the start of this session, would it have prevented the wrong action?* Anything short of a clear yes → rewrite or drop.

## Step 3 — Route each survivor

- **Tier-A — always-loaded CLAUDE.md.** Passed both gates. Decide scope:
  - `~/.claude/CLAUDE.md` — universal: a wrong assumption about how Claude Code itself works, or a cross-project convention.
  - `[project]/CLAUDE.md` — specific to this project's structure, conventions, or tools.
  - When in doubt between global and project, choose **project** — narrower scope is safer.
- **Tier-B — existing pointer-loaded note.** A *real, recurring, narrow* fact/quirk that failed the cost gate (e.g. a genuine tool gotcha) but has an **obvious existing home**: that tool's `_System/Tool Notes/<tool>.md`, or the relevant project subtree note. Append there via `obsidian-write` (Step 5). **No obvious existing home → drop. Never create a new "gotchas" note** — that just relocates the bloat.
- **Drop** — everything else, including all inefficiency patterns with no wrong-model root.

## Step 4 — Write the directive

One short imperative directive per survivor, in the style of existing CLAUDE.md rules:

- Format: `Before [action], [check/verify X]` or `When [situation], [do this instead]`.
- One sentence, ~15 words. Imperative and behavioral — what to DO, not what to know.
- No observations ("Claude sometimes assumes X") — only directives ("Before assuming X, check Y").

Right style:
- `Before assuming a path resolves against cwd, check vault-paths.json first.`
- `Before modifying a function, grep all callers.`

**Model-behavior vs. world-fact.** Ask what the correction compensates. If it patches *model behavior* (the model fabricates, over-defaults to optional, emits an AI tell, degrades at a task on a cheaper tier) rather than a durable *world-fact* (how a path, tool, or convention works), stamp the directive `(model, date)` and add a row to the **Crutch Register** (vault [[Claude Code Hub]] §Model-Release Molt) so the next release re-tests it. World-fact corrections are exempt — they don't molt with the model.

## Step 5 — Present once, terse, and write on approval

Lead with the verdict in one line. If nothing cleared the bar, that is the whole output:

```
Nothing cleared the bar this session.
```

Otherwise, show only what needs a decision — each proposal as a ready-to-approve diff with a **one-line** reason — then the dropped count as terse labels, in this shape:

```
Found N candidates. Proposing M.

1. [~/.claude/CLAUDE.md · Coding discipline]
   → Before assuming X, verify Y.
   Reason: <one line — what this session's wrong action this prevents>

2. [Tool Notes/Codex.md] (Tier-B append)
   → <directive>
   Reason: <one line>

Dropped N−M: <label>, <label>.

Approve all? (or: which numbers)
```

Take a **single batched approval** — not one question per item. Approval is mandatory: never self-initiate a CLAUDE.md edit.

On approval, write each item:
- Tier-A → `Edit` (not Write) into the right section of the target CLAUDE.md, leaving surrounding content untouched.
- Tier-B → `obsidian-write` append to the existing note.
- Stamped `(model, date)` per Step 4 (a model-behavior crutch) → also append one row to the **Crutch Register** table in vault "Areas/Claude Code/Claude Code Hub.md" §Model-Release Molt, via `obsidian-write` (append, tempfile-rename discipline). Match the existing row format: `Pointer` = the directive's file/section, `Compensates (model behavior)` = one-line description of what it patches, `Observed` = `<model> · <date>`.

Report in the end-of-turn summary: candidates found, proposed, approved, and which files were modified.
