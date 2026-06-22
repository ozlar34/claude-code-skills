# github-polish

**Trigger:** `/github-polish <repo>`, "polish / spruce up <repo>", "make <repo> recruiter-ready",
"this repo looks bare, fix it up"

**What it does:** One mostly-autonomous pass that makes a public GitHub repo look like something a
recruiter should take seriously — sharp topics + description, a README reframed as a *worked
example*, a LICENSE if one's missing — then hands back a precise checklist of the things only the
GitHub web UI can do. It runs between two gates: **one plan up front, one handback at the end**,
and everything in between executes without per-step approval.

This is the **portable core**. Its only dependency is an authenticated GitHub CLI — no Python, no
rendering toolchain. (The original private version also renders a branded social card / banner /
diagram for each repo; that layer is an optional add-on, documented in [SETUP.md](./SETUP.md), and
not included here on purpose — see *Why layered* below.)

The non-obvious thing this skill gets right is a **hard CLI/UI boundary backed by integrity
rules**. It knows exactly what `gh` can and can't do, and it never pretends a UI-only action (pin
order, social-preview upload) is done — those always route to a human handback. And it's built to
*not oversell*: never a faked screenshot, never an invented metric, never a "fixed" path it didn't
verify is actually stale. For a job-search-facing repo that's the whole point — an oversold repo
gets found out in the interview, which is worse than a plain one.

**Install (the fast path):** hand the repo link to your coding assistant —

> Install the `github-polish` skill from https://github.com/ozlar34/claude-code-skills — follow
> `source/github-polish/INSTALL.md` in that repo.

It checks your `gh` auth, copies the skill into place, and explains usage. Or install it by hand —
see [SETUP.md](./SETUP.md).

**Example:**

> User: /github-polish my-cli-tool --dry-run
>
> Skill: *(surveys the repo, then prints one plan)*
> ```
> Plan for ozlar34/my-cli-tool (PUBLIC, default branch main):
> [CLI] Topics: add  rust, cli, tui, developer-tools  (currently: none)
> [CLI] Description: "" → "A terminal UI for diffing large JSON files, written in Rust."
> [CLI] README: stub → worked-example frame (what it is / how it works / quick start)
> [CLI] LICENSE: none → offer MIT
> [UI]  Pin this above the three forks; upload a 1280×640 social preview.
> ```
> *(--dry-run stops here. A normal run would execute the [CLI] lines, commit + push each, then
> print the [UI] handback.)*

**Why layered (core + optional render):** the rendering is the heaviest, least portable part — it
needs a headless browser and a personal brand spec a stranger doesn't have. Putting it in the
critical path would mean every install risks breaking in someone else's environment, and a broken
demo is a worse signal than a simple one. So the core can't break (gh-only), and branded rendering
is opt-in. That layering *is* the design judgment — build install-and-go for the common case, keep
the powerful path optional.

**Dependencies:** `gh` (authenticated), `git`, `curl`. All standard on a dev machine. See
[SETUP.md](./SETUP.md) and [INSTALL.md](./INSTALL.md).
