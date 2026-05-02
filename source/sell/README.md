# sell

**Trigger:** "/sell", "list this on Kleinanzeigen", "sell this on KA"

**What it does:** Drives the entire Kleinanzeigen post-ad form via Playwright MCP. Gathers the listing details conversationally, writes them to a YAML manifest, navigates the category picker, fills every field, uploads photos, then reads the final state back and translates all German values to English so a non-German-speaker can verify everything before clicking publish.

The skill stops one click before publish — you click `Anzeige aufgeben` yourself in the browser. That's intentional: the form has occasional dynamic content (price suggestions, AI-detected category warnings) that the skill can't reliably interpret.

**Setup:** see [SETUP.md](./SETUP.md). Three values to configure, plus Playwright MCP installed and a logged-in Kleinanzeigen session.

**Example:**

> User: sell my old Razer keyboard, photos in `~/Downloads/razer/`, asking 70 EUR firm
>
> Skill: *(asks for title, condition, category path, description, ZIP — gets answers in one round-trip; writes `current.yaml`; copies photos; navigates Kleinanzeigen; fills every field; uploads photos; reads back the form state; translates German → English in a verification table)*
>
> ```
> ## Field check (German → English)
>
> | Field | German | English |
> |---|---|---|
> | Title | Razer BlackWidow Tournament Edition | (as given) |
> | Preis | 70 € | 70 € |
> | Preistyp | Festpreis | fixed price |
> | Zustand | Sehr Gut | like new |
> | Versand | Nur Abholung | pickup only |
> | PLZ | 10409 | 10409 |
> | Photos | 4 uploaded | 4 uploaded |
>
> Click Vorschau (preview) or Anzeige aufgeben (publish) yourself.
> ```

**Why it exists:** Kleinanzeigen is the dominant DE classifieds platform, but it's German-only and the post-ad form has 12+ interactive widgets (combobox state, category picker on a separate page, async price suggestions). Manually filling it in a language you don't read is slow and error-prone. The skill does the form-filling deterministically and surfaces every German value as English for a final sanity check.

**Limitation:** Kleinanzeigen is German-market-only. If you're listing somewhere else (Facebook Marketplace, Vinted, eBay), the form selectors won't match and you'd need a different skill.
