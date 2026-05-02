---
name: sell
description: List an item on Kleinanzeigen. Gathers item details conversationally, writes to <ITEMS_DIR>/current.yaml, then drives the Kleinanzeigen post-ad form via Playwright MCP, narrating each field in English so a non-German-speaker can verify. Stops before publish for manual review. Use when user says "/sell", "list on Kleinanzeigen", "list this on KA", or mentions selling something.
trigger: sell OR list OR kleinanzeigen OR inserieren
---

# Sell (Kleinanzeigen)

Drive the Kleinanzeigen post-ad flow end-to-end. **Always echo German field values back in English** so the user can verify before publishing — a critical UX point if the user doesn't read German fluently.

## Prerequisites

- An items directory at `<ITEMS_DIR>` (set during setup) — defaults to `~/projects/sell-bot/items/`. Created if missing.
- Playwright MCP (`mcp__playwright__*` tools) connected. The MCP browser shares your logged-in Kleinanzeigen session automatically — no separate login step needed.
- Photos ready (any folder, any filenames).
- A Kleinanzeigen account (DE-only marketplace). If you're not in Germany, this skill won't be useful as-is.

## Configuration

Edit these defaults at the top of this file before first use:

```
ITEMS_DIR     : ~/projects/sell-bot/items
PHOTOS_DIR    : ~/projects/sell-bot/items/photos
DEFAULT_ZIP   : <YOUR_5_DIGIT_GERMAN_ZIP>
```

## Flow

### 1. Gather item details

Ask for the following. Batch into 1–2 messages, don't interrogate one field at a time:

- **Title** (will be shown as-is; ≤65 chars)
- **Asking price** in EUR, and whether **firm** (Festpreis) or **negotiable** (VB)
- **Condition** — map to Kleinanzeigen values:
  - `new` → Neu
  - `like-new` → Sehr Gut
  - `good` → Gut
  - `acceptable` → In Ordnung
- **Category path** — 3 levels, real German names as they appear on the site (e.g. `["Elektronik", "PC-Zubehör & Software", "Tastatur & Maus"]`). If unsure, propose a path and confirm.
- **Description** — either the user writes it, or draft one in German and translate it back for approval.
- **Photo folder path + filenames** — or offer to rename/renumber a folder like `~/Downloads/razer/`.
- **Shipping** — default to **pickup only** (`Nur Abholung`) unless told otherwise.
- **ZIP** — default to `DEFAULT_ZIP` from configuration above.

### 2. Write `current.yaml`

Write (overwrite) `<ITEMS_DIR>/current.yaml` using this shape:

```yaml
title: "..."
price: 70
price_type: "fixed"  # or "negotiable"
condition: "like-new"

kleinanzeigen:
  category_path: ["Elektronik", "...", "..."]
  shipping: false
  location_zip: "10409"

description: |
  ...

photos:
  - "01.jpeg"
  - "02.jpeg"
```

Then copy the photos into `<PHOTOS_DIR>/` with the filenames listed above. Use `cp` — don't move, in case the user wants the originals.

### 3. Drive Kleinanzeigen via Playwright MCP

Navigate to `https://www.kleinanzeigen.de/p-anzeige-aufgeben-schritt2.html` and verify the user is logged in (h1 includes "Profil von"). If not, stop and tell them to log in first.

Fill fields via `mcp__playwright__browser_evaluate` using native setters so React state updates:

```js
const set = (id, value) => {
  const el = document.getElementById(id);
  const proto = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
  Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, value);
  el.dispatchEvent(new Event('input', { bubbles: true }));
  el.dispatchEvent(new Event('change', { bubbles: true }));
  el.dispatchEvent(new Event('blur', { bubbles: true }));
};
// IDs: ad-title, ad-price-amount, ad-zip-code, ad-description
```

**Category picker** (separate page):
1. Click the `<a>` inside the Kategorie row ("Wähle deine Kategorie" / "Kategorie ändern") — navigates to `/p-kategorie-aendern.html`
2. Click each breadcrumb level in order by matching `a.textContent.trim() === name`
3. Click the `Weiter` button (German for "Next") to return to the form

**Condition combobox**: find the button next to the "Zustand (optional)" label, click it, then click the `li[role='option']` whose text matches the German condition label.

**Price type combobox**: click `#ad-price-type`, then pick the `li[role='option']` with text `Festpreis` / `VB` / `Zu verschenken`.

**Shipping**: for pickup-only, check `#ad-shipping-enabled-no`.

**Photos**: click the button whose text matches `/zieh deine fotos/i` to trigger the file chooser, then use `mcp__playwright__browser_file_upload` with absolute paths.

**Photo sandbox gotcha**: the MCP playwright tool restricts file access to the current working directory's allowed roots. If you get "File access denied", stage photos into the project's `.playwright-mcp/sell-photos/` subdir first and upload from there. Clean up after publish.

### 4. Verify and translate back

After all fields are set, read back the final state with `browser_evaluate`:

```js
({
  title: document.getElementById('ad-title')?.value,
  price: document.getElementById('ad-price-amount')?.value,
  priceType: document.querySelector("input[name='priceType']")?.value,
  condition: document.querySelector("input[name*='condition']")?.value,
  zip: document.getElementById('ad-zip-code')?.value,
  city: document.getElementById('ad-city')?.value,
  descTail: document.getElementById('ad-description')?.value?.slice(-200),
  categoryId: document.querySelector("input[name='categoryId']")?.value,
})
```

Present a summary table with **English translations** of every German value, the full description translated, and confirmation that photos uploaded. Examples of German → English the user will see:
- Festpreis = fixed price, VB = negotiable
- Nur Abholung = pickup only, Versand möglich = shipping available
- Sehr Gut = like new, Gut = good, In Ordnung = acceptable
- Vorschau = preview, Anzeige aufgeben = publish

### 5. Hand off

Tell the user to review in the browser and click **Vorschau** (preview) or **Anzeige aufgeben** (publish) themselves. **Do not click publish programmatically.**

## Known field mapping

| YAML | Form field | ID / Name |
|---|---|---|
| `title` | Titel | `#ad-title` |
| `price` | Preis | `#ad-price-amount` |
| `price_type: fixed` | Preistyp = Festpreis | `#ad-price-type` combobox |
| `price_type: negotiable` | Preistyp = VB | `#ad-price-type` combobox |
| `condition` | Zustand (optional) | combobox near "Zustand" label |
| `kleinanzeigen.category_path` | Kategorie | separate picker page |
| `kleinanzeigen.shipping: false` | Versand = Nur Abholung | `#ad-shipping-enabled-no` |
| `kleinanzeigen.location_zip` | PLZ | `#ad-zip-code` |
| `description` | Beschreibung | `#ad-description` |
| `photos` | Fotos | file chooser on "Zieh deine Fotos hier rein" button |

## Don'ts

- Don't click **Anzeige aufgeben** (publish) — always hand off
- Don't list to eBay — this skill is Kleinanzeigen-only
- Don't skip the English-translation summary if the user doesn't read German
- Don't leave photos in `.playwright-mcp/sell-photos/` after publish
