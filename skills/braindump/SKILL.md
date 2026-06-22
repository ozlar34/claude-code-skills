---
name: braindump
description: Develop a fleeting idea through adaptive one-question-at-a-time dialogue — figure out what it actually is, what could be done with it, and what the next step would be. User-invocable only (via /braindump); does not auto-trigger. Distinct from an adversarial plan stress-test and from a build-this-now spec session — braindump stays open-ended and writes nothing.
---

# Braindump

The user just shared a raw idea. Your job is to help them think it through — not to build it, not to interrogate it adversarially, just to develop it until it's clear what it is and what the next step would be.

## Mode

Collaborative and exploratory. One question at a time. For each question, offer your own best guess as a starting point so a half-formed idea has something to push against — the hardest moment is activation, not continuation, so never open with a blank wall of questions.

**Prose by default, widget for discrete branches.** Ask in free-flowing prose most of the time — open-ended questions invite the messy elaboration that develops an idea, and a chip-picker short-circuits that. But when a question genuinely reduces to 2–4 mutually-exclusive options (a clean fork, not an open prompt), use `AskUserQuestion` instead: it's lower-friction to answer and still leaves "Other" open. The test is the shape of the question, not the stage of the conversation.

## Adaptive depth

Read how much the idea has legs and scale to it. Do **not** run a fixed checklist.

- **Thin / passing thought** → one or two clarifying questions, name what it might be, stop. Don't manufacture depth that isn't there.
- **Has legs** (the user leans in, adds detail, gets animated) → go deeper, one question at a time, across whichever of these the idea actually needs:
  - **What is it really?** — the version underneath the first phrasing. What problem, itch, or want does it answer?
  - **What could be done with it?** — concrete forms it could take. A project? A post? A tool? A habit? Nothing? All valid landing spots.
  - **What's the smallest next step?** — one concrete action, sized for activation. A single first move, not a roadmap.

Let the user steer. If they say "that's enough" or the idea has clearly resolved, stop there.

## What this is not

- This skill **writes nothing**. No note, no task, no file. The output is the thinking. That's deliberate — the user decides afterward whether anything is worth keeping.
- If, at the very end, the idea clearly wants a home, you may offer a one-line handoff (e.g. "want me to drop the next step in your task manager, or capture this as a note?") — but only as an offer, and only once. Don't push.

## Boundaries with neighbors

These distinguish braindump from two adjacent things you might have skills for. The point is to stay in the right lane, not to assume the neighbors exist.

- **Adversarial stress-test** (e.g. a "grill me" skill) — pokes holes in a plan you *already have*. Braindump is upstream of that: the idea isn't a plan yet.
- **Spec / brainstorming** — turns an idea into a software design and gates toward building it now. Braindump stays open-ended; the idea might not be software at all, and nothing gets built here.
