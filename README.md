# dfts — Dwarf Fortress Tileset Guide

Interactive guide to the 16×16 CP437 tileset (`tileset.png`). Hover or tap a tile to see the Dwarf Fortress
entities (creatures, items, terrain, buildings, plants, UI) that use that glyph.

Features: hover tooltip + detail panel, click to pin, arrow-key navigation, entity search,
category filters, and a 15-colour DF palette tint.

## Run

No build step. Serve the folder and open `index.html`:

    python3 -m http.server 8000

Entity data lives in `data.js` (keyed by tile index 0–255). It is curated for the default ASCII layout and
is not exhaustive; glyphs without entries show a placeholder. Contributions welcome.

## Deployment

`.github/workflows/pages.yml` publishes the site to GitHub Pages on every push to `main`
(one-time setup: **Settings → Pages → Source: GitHub Actions**).
