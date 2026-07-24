# offlabel brand: one theme, every card

Every file in `cards/` clones `cards/_reference.html` byte-for-byte on CSS and swaps only content. This is the
single source of truth for the palette so it never drifts card-to-card.

## Why one theme
The point of the card format is that a reader can glance at five different model cards and instantly find the
same information in the same place: header, "use it like this," trust map, footer. That only works if the
visual system never changes between models. Content varies; the frame does not.

## Palette (light / dark, theme-aware via `prefers-color-scheme` + `data-theme`)

| Token | Role | Light | Dark |
|---|---|---|---|
| `--card` | card background | `#fff` | `#1f1f1e` |
| `--ink` | primary text | `#1a1a19` | `#ececea` |
| `--sub` | secondary/meta text | `#6b6b66` | `#a2a29c` |
| `--line` | hairline borders | `#e6e5e1` | `#33332f` |
| `--accent` | wordmark / brand accent | `#2f6f5b` (deep green) | `#5bbf9e` |
| `--hold` | trust map: holds the line | `#1f8a5b` | `#57c98d` |
| `--holdbg` | hold band background | `#e7f4ec` | `#163024` |
| `--fold` | trust map: folds under pressure | `#c0392b` | `#e57366` |
| `--foldbg` | fold band background | `#fbeae7` | `#331d1a` |
| `--warn` | blind spots / DRAFT flag | `#b26a00` | `#e0a24a` |
| `--warnbg` | warn band background | `#fcf1df` | `#332612` |
| `--chip` | neutral pill background | `#f2f1ee` | `#2a2a28` |

Two semantic ramps only: **green = holds**, **red = folds**. Amber is reserved for blind spots and the DRAFT
flag. It never means "holds" or "folds," just "uncertain / caveat."

## Type & layout
- System font stack (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`), no webfont
  dependency, renders identically everywhere.
- Portrait card, `max-width: 480px`, 16px corner radius, flat (no shadows/gradients), reads well as a
  screenshot or a shared image, not just live HTML.
- Four zones, always in this order: **header** (name / vendor / params / class chips / one-line verdict) →
  **use it like this** (5 icon rows: 🧠 thinking · 🔧 tools · 🎛️ sampling/serving · ✅ best-at · 🚫 avoid) →
  **trust map** (✓ holds / ✕ folds / ⚠ blind spots, three color-coded bands) → **footer** (tested-on config +
  method + `DRAFT` flag when applicable).

## What never changes per model
CSS custom properties, class names, zone order, icon set, band coloring. What changes: the text content inside
each zone, and which chips/tags appear.
