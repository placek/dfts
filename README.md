# dfts — Dwarf Fortress Tileset Guide

Interactive guide to the 16×16 CP437 tileset (`tileset.png`). Hover or tap a tile to see everything
Dwarf Fortress draws with that glyph — in the fortress, in on-screen text, and on the world map.

Each tile shows:

- **Used for** — the canonical per-tile use list, with the wiki's modifiability markers
  (`*` raws, `#` graphic set, `$` `d_init.txt`, `¢` dual colour, `÷` inverted).
- **On the map** — world map, site and fast-travel meanings, each variant (normal / snow / good /
  evil / ruins / night creature) rendered in the colours DF actually uses.
- **Enumerated members** — the creatures, vermin, trees, crops, grasses, stones, ores and soils that
  use the tile, each linking to its wiki page.
- **In on-screen text** and **name alphabets** for glyphs used in the interface or in race names.

Click or press <kbd>Enter</kbd> to pin a tile (the URL updates to `#tile=N` so it can be linked),
arrow keys move the selection, <kbd>Esc</kbd> unpins. Search matches across every field above.

## Scenes

Below the grid, "In the game" shows a few example screens (embark site, fortress interior, deep
caverns) drawn with the same tileset. Hover or tap any cell to inspect that tile in the side panel
(with the colours it is drawn in); every cell using the hovered or pinned glyph is outlined.

`scenes.js` is generated from the ASCII-art layouts in `tools/gen_scenes.py`:

    cd tools && python3 gen_scenes.py ../index.html ../scenes.js

## Run

No build step. Serve the folder and open `index.html`:

    python3 -m http.server 8000

## Data

`data.js` is **generated** — do not edit it by hand. Every fact in it comes from two Dwarf Fortress
Wiki articles:

- [Tilesets](https://dwarffortresswiki.org/index.php/Tilesets) — the "What tiles are used for what"
  row tables, the "Detailed use list by type" sections, the text/interface list and the alphabets.
- [Map legend](https://dwarffortresswiki.org/index.php/Map_legend) — the ASCII biome, terrain,
  construction, site and fast-travel tables, including their DF `COLOR` tokens.

To refresh it against the current wiki:

    cd tools
    curl -sL "https://dwarffortresswiki.org/index.php?title=Tilesets&action=raw"   -o /tmp/tilesets.wiki
    curl -sL "https://dwarffortresswiki.org/index.php?title=Map_legend&action=raw" -o /tmp/maplegend.wiki
    python3 gen_data.py /tmp/tilesets.wiki /tmp/maplegend.wiki ../index.html ../data.js
    python3 verify.py 7 15 65 227 230      # spot-check any tile indices

`gen_data.py` reads the CP437 table out of `index.html`, so the page and the data can never disagree
about which glyph a tile index is. It prints coverage counts and fails loudly on map-legend
characters it cannot place, rather than dropping them silently.

## Deployment

`.github/workflows/pages.yml` publishes the site to GitHub Pages on every push to `main`
(one-time setup: **Settings → Pages → Source: GitHub Actions**).
