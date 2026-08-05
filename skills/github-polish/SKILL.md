---
name: github-polish
description: >-
  Polish a public GitHub repo's presentation — sharpen topics + description, reframe the README as
  a worked example, add a LICENSE if missing, commit and push every CLI-doable change, and hand
  back a GitHub-UI checklist for what the API can't do (pin order, social-preview upload, real
  screenshots). Not for adding features — for how the repo reads to anyone who opens it. Use
  whenever the user says "/github-polish <repo>", "polish / spruce up / clean up <repo>",
  "the README is weak", or points at one of their repos (bare name, owner/repo, or URL) and wants
  it to look polished and professional — even casually or by outcome only ("this repo looks bare,
  fix it up").
---

# github-polish

Give a public repo a clean, professional presentation — sharp metadata and a README that
frames the work as a worked example, not an abandoned experiment.

The job is **mostly autonomous**: survey, print one short plan, then do every CLI-doable thing
in one pass without per-step approval. Only two things come back to the user: the actions
GitHub gates behind the web UI, and any asset needing a real-world capture (you write the
walkthrough, never fake it).

> **Scope of this version.** The default path is the portable, `gh`-only core: metadata, README,
> LICENSE, and an honest CLI/UI handback — everything here runs with nothing but an authenticated
> `gh`, and can't break in your environment. Branded social cards / banners / diagrams are an
> **optional rendering add-on** (Playwright + a brand spec; see `SETUP.md` and `render/`); when
> it's installed, step **d** below activates. When it isn't, the core is complete on its own and
> the handback simply tells the user how to add a social preview by hand.

## Invocation

```
/github-polish <arg>
```

- `<repo>` → `<your-gh-login>/<repo>` (owner resolved via `gh api user --jq .login`).
  `<owner>/<repo>` → explicit. A full URL → parse owner/repo from it. `.` → the repo in cwd
  (use it, don't re-clone).
- `--dry-run` (or "just survey" / "show me the plan first") → SURVEY + plan, then STOP. No
  edits, commits, or pushes. **The first real run on any repo should be a dry run.**

## Hard rules — the integrity of a public, named asset. Internalize the *why*.

Violating any one damages a public, named asset — the gap surfaces eventually, and that's worse
than a plain repo.

1. **Honesty over polish.** Never fabricate a usage screenshot, invent a metric, or imply a
   capability the repo lacks. A repo that oversells gets found out eventually. If the honest move
   is a real capture you can't do, write a capture walkthrough for the UI todo list instead.
2. **No private data in public assets.** Placeholder data only (`Company A`–`I`, generic roles,
   round-number stats). Scrub real names, paths, emails, keys, internal URLs before anything is
   committed. When in doubt, genericize.
   - **Sanitisation grep (mandatory, pre-commit — never skip).** Keep a per-repo pattern of the
     private signals *this* repo must never leak, and run it over the working tree before any
     commit or push, failing closed on any hit — a match blocks the commit until scrubbed:
     ```
     git grep -inE '<your private-signal pattern>' -- . ':!*.png'
     ```
     Zero hits is the only pass. Build the pattern from what would actually harm you if a reader
     found it — personal identifiers, nationality- or health-adjacent signals, self-assessed
     claims you'd never put on a CV, internal hostnames, client names. A public repo linked from
     a CV or profile discloses whatever it contains to every reader, permanently and outside the
     context you'd have chosen. Extend the pattern whenever a new private signal surfaces; never
     narrow it.
3. **Know the CLI/UI boundary.** `gh` owns topics, description, file commits, pushes — do those.
   `gh` *cannot* set pin order or upload a social-preview image — those are UI-only, go on the
   todo list every time, and are never faked via API.
4. **A README that lies is worse than one that's ugly.** Surgical edits only. NEVER "fix" a
   path/command without verifying it's actually stale (read the tree, run it, check the file
   exists). A confidently wrong README is a credibility hit.
5. **Surgical, read-before-edit, conservative.** Touch only what improves presentation.
   No refactors, no reformatting untouched sections, no deleting what you didn't add. Match the
   repo's voice.

## Workflow

### 1 — SURVEY (delegate when you can; get the conclusion, not the file dumps)

Surveying means reading the README end-to-end, the whole file tree, and the metadata — a lot of
context that collapses to a short gap list. If your environment supports subagents, delegate it
to one **pinned to a cheaper model** (e.g. pass `model: sonnet`) so that reading never lands in
the main window — mechanical survey work shouldn't inherit an expensive session model. Brief it
to **return only the structured
gap report below**, no file contents, no narration. The exception is `.` (cwd), where the main
session already holds the repo — survey inline then. If you can't delegate, survey inline but
still distill to the report before acting.

Survey steps:
- **Get the code:** for `<owner>/<repo>`, shallow-clone to a temp dir
  (`git clone --depth 1 https://github.com/<owner>/<repo>`). For `.`, read cwd.
- **Metadata:** `gh repo view <owner>/<repo> --json name,description,repositoryTopics,licenseInfo,homepageUrl,visibility`.
  Confirm it's **PUBLIC**. If private, stop and report that — don't survey further.
- **Read:** README end-to-end, top-level file/dir layout, languages, any docs/ or workflows/.
  Understand the real shape of the project.

Return ONLY this report:
- visibility + default branch
- description: current value + verdict (weak/empty/fine)
- topics: current set + missing searchable ones from the real stack/domain
- license: present? (if absent on a portfolio repo, flag)
- README weaknesses: bulleted (wall/stub, no hook, no worked-example frame, stale paths, etc.)
- private-data risks spotted: any real names/paths/keys to scrub
- accurate paths/commands to PRESERVE verbatim

### 2 — PLAN (one printout, then go)

From the gap report, print ONE short, prioritized plan — what you'll change and why, grouped by
the steps below, each marked `[CLI]` (you do it) or `[UI]` (the user's todo list). Lead with the
highest-leverage gaps; keep it scannable, not an essay. This is the single approval surface: a
normal run proceeds straight through; `--dry-run` stops here.

### 3 — EXECUTE (autonomous, atomic commits, push)

Do everything `[CLI]` in one pass. Commit each logical change atomically with a clear message;
push when done. No per-step approval gates.

**Idempotency — this skill gets re-run on the same repo.** Each step below is conditional on a
real gap from the survey, not a fixed to-do. A README already in the worked-example frame needs
no rewrite; a description that's already sharp needs no edit. Re-do only what's genuinely stale
or missing. A churn commit, or a rewrite of a fine README, violates rule 5 — on an
already-polished repo the correct run is a no-op verify pass, reported as such.

**a. Metadata.**
- Topics: `gh repo edit <owner>/<repo> --add-topic a,b,c` — real, searchable, from the actual
  stack/domain.
- Description: `gh repo edit <owner>/<repo> --description "<one sharp line>"` — concrete, no
  fluff: what it is and what makes it interesting.

**b. README polish.** Surgical edits toward the worked-example frame:
- Strong title + one-line hook.
- "What this is" framing — for a portfolio repo the strongest honest frame is usually *"the
  system I built for X; treat it as a worked example, not a template"*. It turns a personal
  project into a credibility signal.
- Clear sections (what's in here, how it works, quick start) sized to the repo; honest
  placeholder labels on any sample data; collapsible `<details>` for long blocks.
- Preserve every accurate path/command (rule 4).

**c. LICENSE.** If a public portfolio repo has none, flag it and offer MIT (a safe default). Add
only on a clear yes — never silently.

**d. Branded assets — OPTIONAL, only if the rendering add-on is installed.** Check for it:
`test -d <skill-dir>/render && test -f <skill-dir>/render/brand.py`. If absent, skip this step
entirely — the core above is complete without it; do **not** tell the user assets were produced.
If present, you may render an on-brand **social card**, README **banner**, and (only when there's
real structure) an **architecture diagram**, all from one small per-repo config. Resolve the
owner first (`gh api user --jq .login`) so the assets show the user's handle. Before picking an
accent, check what's already taken across your other configs (`grep -h '"accent"' configs/*.json`)
so sibling repos don't collide. Full schema, the
accent palette, render commands, and where each file goes are in `render/brand-spec.md` — follow
it. The integrity rules still bind: honest placeholder copy only, no faked diagrams, and the card
is **staged for the user to upload** (the API can't — rule 3), never claimed as done.

**Verify before done.** If the README references any committed image under `docs/` (e.g. one the
user added themselves), `curl` each raw URL for a 200 before declaring done — a broken image is
worse than none:
`curl -s -o /dev/null -w "%{http_code}" https://raw.githubusercontent.com/<owner>/<repo>/<default-branch>/docs/<file>`.
(Embeds using *relative repo paths* render natively on github.com and are outside this check.)

### 4 — HAND BACK: "YOUR TURN" (GitHub UI only)

Close with a clear, ordered todo list of what only the human + web UI can do — precise paths,
exact UI locations:

- **Pin order** — which repos to pin and in what order, one-line reasoning each (lead with the
  strongest for the user's profile).
- **Social-preview image** — *Settings → General → Social preview → Upload an image*. `gh` can't
  do this (rule 3). If the rendering add-on is installed and you produced a card in step **d**,
  give the exact staged PNG path to upload. Otherwise any 1280×640 image works (and the add-on
  in `SETUP.md` can generate an on-brand one).
- **Real-usage captures** — if any asset needs a genuine screenshot, give a precise capture
  walkthrough (what to open, what state, what to frame, where to save). Never fabricate (rule 1).

## Toolchain

- `gh` (authenticated) for all GitHub reads/writes. That's the only hard dependency of this core.
- `git` + `curl` (present on any dev machine).
