# second-opinion

**Trigger:** `/second-opinion` (user-invocable only — does not auto-trigger)

**What it does:** Pulls a fresh, independent Opus agent into the session to audit
the last load-bearing claim the assistant made — returning `confirmed`, `refuted`,
or `can't tell`, with evidence. No tools other than the Agent tool are required.

The non-obvious thing the skill does is **withhold the parent session's reasoning
when briefing the Opus agent.** If the parent hands Opus its own diagnosis, Opus
inherits the framing and rubber-stamps it — you've spent Opus tokens to manufacture
a more confident version of a possibly-wrong answer. The skill's discipline is to
give Opus only the claim and the raw artifacts, never the justification, so the
verdict is genuinely independent. There is a concrete test: *could a reader of the
brief guess the parent's verdict?* If yes, the brief is leaky — strip it back.

Two failure modes the skill explicitly guards against:

- **Leak 1 — diagnosis smuggled into the claim.** "The `except` only wraps
  `get()`, leaving `set()` unprotected" is already Opus's job done. The brief
  should say what was *asserted* ("this degrades gracefully"), not what was
  *found*.
- **Leak 2 — a "how to check" that telegraphs the answer.** Pointing a flashlight
  at the bug ("pay attention to what `in` costs on a list") is not neutral. The
  instruction should say what to examine and how to measure it, not what to expect.

After relaying Opus's verdict verbatim, the turn ends on one line offering to
continue: *"Want me to grill this out with Opus, or take it from here?"* No fix
is proposed. No re-litigating. The verdict is information, not a mandate — the
user decides the next move.

**When to use:**

- You're on a cheaper session (Sonnet) and a single claim is load-bearing enough
  to warrant Opus-level scrutiny.
- You want a fresh brain that didn't live through this session's reasoning and has
  no sunk cost in being right.
- A refactoring, migration, or algorithm analysis has one assertion doing a lot of
  weight — "this is idempotent," "this is O(n)," "the fallback always fires."

**What it does NOT do:** propose a fix, argue with the verdict, or trigger
automatically. One audit, relayed verbatim, then it stops.

---

## Worked example

### Setup

A session on Sonnet was reviewing `get_or_set()` in a Redis cache module and
asserted: *"This degrades gracefully when Redis is down — any ConnectionError is
handled and the function always falls back to `compute()`."*

The function under review:

```python
from external_redis import redis_client  # third-party client, configured elsewhere


def get_or_set(key, compute):
    """Return the cached value for `key`, computing and caching it on a miss.

    Designed to degrade gracefully: if the cache backend is unreachable,
    fall back to computing the value directly.
    """
    try:
        cached = redis_client.get(key)
    except ConnectionError:
        return compute()

    if cached is not None:
        return cached

    value = compute()
    redis_client.set(key, value)
    return value
```

### The neutral brief

`/second-opinion` distilled that assertion and handed this to a fresh Opus agent
— note that it states only *what was claimed*, not *what the parent found*. A
reader of this brief cannot guess the verdict:

> You are an independent verifier. Another agent claimed: **"get_or_set() degrades
> gracefully when Redis is down — any ConnectionError raised by the cache backend
> is handled, and the function always falls back to compute() rather than
> propagating an exception to the caller."**
>
> Do not trust that framing — it may be wrong. Investigate from the primitives
> below and reach your own verdict.
>
> **How to check:**
> - Enumerate every call to `redis_client` in the function body.
> - For each call, determine whether a `ConnectionError` raised by that call would
>   be caught or would propagate to the caller.
> - Trace all code paths (cache hit, cache miss, Redis unreachable at each point).
> - Consider whether the exception type used covers all relevant failure modes.
>
> Return exactly: **Verdict:** `confirmed` | `refuted` | `can't tell` and
> **Evidence:** the specific line(s) or reasoning that drove the verdict.

### Opus's verdict

Opus returned **REFUTED**:

> There are two `redis_client` calls, and the claim's invariant fails on both grounds:
>
> 1. **Uncaught `set()` on the cache-miss path (decisive).** Only
>    `redis_client.get(key)` is inside the `try/except ConnectionError`. The second
>    call, `redis_client.set(key, value)`, sits *after* the try block:
>    ```python
>    value = compute()
>    redis_client.set(key, value)   # not guarded
>    return value
>    ```
>    If Redis fails at the `set`, the `ConnectionError` propagates to the caller.
>    The value was already computed, yet the function raises instead of returning it.
>    "Always falls back to compute()" is false.
>
> 2. **Exception type likely too narrow (secondary).** The handler catches the
>    builtin `ConnectionError`. The backend (`external_redis`) likely raises
>    `redis.exceptions.ConnectionError`, which does *not* subclass the builtin.
>    If so, even the guarded `get()` call would not be caught. Point 1 alone
>    refutes the claim regardless of point 2.

### The relay

The parent session relayed the verdict verbatim and ended the turn on one line:

> Want me to grill this out with Opus, or take it from here?

No fix was proposed. No re-litigating. The verdict was information — the next
move was the user's call.

---

**Dependencies:** none. Pure Agent tool (built into Claude Code) + conversational
logic. See [SETUP.md](./SETUP.md).
