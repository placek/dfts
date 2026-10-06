"""Generate data.js from the DF wiki 'Tilesets' and 'Map legend' articles.

Usage: python3 gen_data.py <tilesets.wiki> <maplegend.wiki> <index.html> <out data.js>

Every fact written to data.js comes from one of the two wiki articles; nothing
is invented here. Re-run after re-downloading the wiki sources to refresh.
"""
import json
import re
import sys

import parse_maplegend
import parse_tilesets
from wikiparse import cp437_table, normalise_char, strip_markup

FLAGS = {
    "*": "Tile can be changed in the raw data files",
    "#": "Tile can be replaced by a graphic set image",
    "$": "Tile can be changed in d_init.txt",
    "¢": "Uses dual colours",
    "÷": "Uses an inverted tile",
}

# "Detailed use list by type" section -> label shown in the UI.
LIST_LABELS = {
    "Creatures / Main creature tiles": "Creatures",
    "Creatures / Vermin": "Vermin",
    "Creatures / Additional Tiles Used by Creatures": "Creatures (secondary tiles)",
    "Plants / Trees on map": "Trees (as drawn on the map)",
    "Plants / Trees in game": "Tree parts",
    "Plants / Crops": "Crops",
    "Plants / Garden plants": "Garden plants",
    "Plants / Grasses": "Grasses",
    "Unmined inorganic material / Stones": "Stones",
    "Unmined inorganic material / Ores": "Ores",
    "Unmined inorganic material / Gems": "Gems",
    "Unmined inorganic material / Soil": "Soil",
}
LIST_ORDER = list(LIST_LABELS.values())

# "Characters used in text and interface", transcribed from that wiki section.
TEXT_ROLES = [
    ("General text", '"!_+,-./0123456789'
                     "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz █■"),
    ("Bridge direction indicator", "↑↓→←"),
    ("Item quality rating", "-+≡*☼«»"),
    ("Brackets and tags", "()<>{}[]"),
    ("Interface symbol", "♂♀☼Γ√"),
]


def looks_like_list(body):
    """True when a detail-section body is essentially a comma-separated link list."""
    linked = sum(len(m.group(1)) for m in re.finditer(r"\[\[([^\]]+)\]\]", body))
    plain = len(re.sub(r"\s+", "", strip_markup(body)[0]))
    return plain > 0 and linked / max(plain, 1) > 0.6


def member(chunk):
    text, links, flags = strip_markup(chunk)
    if not text:
        return None
    target = links[0].split("#")[0] if links else None
    if target and target.lower() != text.lower():
        return {"t": text, "w": target}
    if target:
        return {"t": text, "w": target}
    return {"t": text}


def build_lists(sections):
    """tile -> [ {l: label, items: [...], note: str} ]"""
    out = {}
    for key, lines in sections.items():
        label = LIST_LABELS.get(key)
        if not label:
            continue
        for block in parse_tilesets.tiles_from_section(lines):
            tile, body = block["tile"], block["body"]
            # Drop wikitable row separators / table terminators.
            body = "\n".join(
                l for l in re.sub(r"^\s*\|", "", body, flags=re.M).split("\n")
                if l.strip() not in ("-", "}", "")
            )
            if key == "Creatures / Additional Tiles Used by Creatures":
                cells = [c for c in body.split("\n") if c.strip() and c.strip() != "-"]
                usage = strip_markup(cells[0])[0] if cells else ""
                note = strip_markup(cells[1])[0] if len(cells) > 1 else ""
                if not usage:
                    continue
                entry = {"l": label, "items": [{"t": usage}], "note": note}
            elif looks_like_list(body):
                items = [member(c) for c in parse_tilesets.split_top_level(body)]
                items = [i for i in items if i]
                if not items:
                    continue
                entry = {"l": label, "items": items}
            else:
                note = strip_markup(body)[0]
                if not note:
                    continue
                # The wiki phrases some notes as a sentence about the tile glyph,
                # which was rendered as the (stripped) {{TST}} template.
                if note.startswith("is "):
                    note = "This tile " + note
                entry = {"l": label, "items": [], "note": note}
            out.setdefault(tile, []).append(entry)
    for entries in out.values():
        entries.sort(key=lambda e: LIST_ORDER.index(e["l"]))
    return out


def build_text_roles(cp437):
    roles = {}
    for label, chars in TEXT_ROLES:
        for ch in chars:
            idx = cp437.find(ch)
            if idx >= 0:
                roles.setdefault(idx, []).append(label)
    return roles


def build_alphabets(text, cp437):
    """Accented characters used in each race's names."""
    out = {}
    for m in re.finditer(r"^(Dwarven|Elven|Human|Goblin):\s*(\S+)\s*$", text, re.M):
        lang, letters = m.group(1), m.group(2)
        for ch in letters:
            if ch.isascii():
                continue
            idx = cp437.find(normalise_char(ch))
            if idx >= 0:
                out.setdefault(idx, []).append(lang)
    return out


def build_unused(text, cp437):
    section = re.search(r"=== No known use ===\n(.*?)(?:\n<!--|\n==|\{\{Category)", text, re.S)
    chars = set()
    if section:
        body = section.group(1)
        # Skip the explanatory prose; the tile list is the last non-empty line.
        line = [l for l in body.strip().split("\n") if l.strip()][-1]
        for ch in line:
            if ch.isspace():
                continue
            if ch.isdigit():
                continue
            idx = cp437.find(normalise_char(ch))
            if idx >= 0:
                chars.add(idx)
        for m in re.finditer(r"\b(\d{1,3})\b", line):
            chars.add(int(m.group(1)))
    return sorted(chars)


def build_map(map_chars, cp437):
    """char-keyed map legend data -> tile-keyed, aggregated per label."""
    out, unmapped = {}, []
    for ch, entries in map_chars.items():
        idx = cp437.find(ch)
        if idx < 0:
            unmapped.append(ch)
            continue
        grouped = {}
        for e in entries:
            # Keep each variant paired with the colours it is actually drawn in.
            g = grouped.setdefault((e["section"], e["label"]), {})
            cols = g.setdefault(e["variant"], [])
            for col in e["cols"]:
                if list(col) not in cols:
                    cols.append(list(col))
        for (section, label), variants in grouped.items():
            out.setdefault(idx, []).append({
                "t": label,
                "s": section,
                "v": [{"n": n, "c": c} for n, c in variants.items()],
            })
    for entries in out.values():
        entries.sort(key=lambda e: (e["s"], e["t"]))
    return out, unmapped


def main(tilesets_path, maplegend_path, index_path, out_path):
    ts_text = open(tilesets_path, encoding="utf-8").read()
    ts_lines = ts_text.split("\n")
    ml_lines = open(maplegend_path, encoding="utf-8").read().split("\n")
    cp437 = cp437_table(open(index_path, encoding="utf-8").read())

    uses = parse_tilesets.parse_rows(ts_lines)
    sections = parse_tilesets.parse_detail_sections(ts_lines, cp437)
    lists = build_lists(sections)
    map_data, unmapped = build_map(parse_maplegend.parse(ml_lines), cp437)
    text_roles = build_text_roles(cp437)
    alphabets = build_alphabets(ts_text, cp437)
    unused = set(build_unused(ts_text, cp437))

    tiles = {}
    for i in range(256):
        rec = {}
        u = [
            {"t": e["text"], **({"f": e["flags"]} if e["flags"] else {})}
            for e in uses.get(i, [])
        ]
        if u:
            rec["uses"] = u
        if i in map_data:
            rec["map"] = map_data[i]
        if i in lists:
            rec["lists"] = lists[i]
        if i in text_roles:
            rec["text"] = text_roles[i]
        if i in alphabets:
            rec["names"] = alphabets[i]
        if i in unused:
            rec["unused"] = True
        tiles[i] = rec

    body = json.dumps(tiles, ensure_ascii=False, indent=1, sort_keys=True)
    body = re.sub(r"\n\s+", " ", body)
    body = re.sub(r'^\{ "', "{\n  \"", body)
    body = re.sub(r'(?<=\]|\}|e) \}, "(\d+)":', lambda m: '},\n  "%s":' % m.group(1), body)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(HEADER)
        f.write("window.DF_FLAGS = %s;\n\n" % json.dumps(FLAGS, ensure_ascii=False, indent=2))
        f.write("window.DF_TILES = %s;\n" % body)

    print(f"tiles with uses      : {sum(1 for t in tiles.values() if 'uses' in t)}")
    print(f"tiles with map data  : {len(map_data)}")
    print(f"tiles with lists     : {len(lists)}")
    print(f"tiles flagged unused : {sorted(unused)}")
    print(f"unmapped map chars   : {unmapped}")
    print(f"list items total     : "
          f"{sum(len(e['items']) for t in lists.values() for e in t)}")
    if unmapped:
        raise SystemExit(
            "error: map legend uses characters absent from CP437: "
            + " ".join(f"{c!r} (U+{ord(c):04X})" for c in unmapped)
            + "\nAdd them to CP437_ALIASES in wikiparse.py."
        )


HEADER = '''// Generated by tools/gen_data.py — do not edit by hand.
//
// Sources (Dwarf Fortress Wiki, v0.50):
//   https://dwarffortresswiki.org/index.php/Tilesets   — "What tiles are used for
//     what" (per-tile uses) and "Detailed use list by type" (creatures, plants,
//     stones, ores, gems, soil), plus the text/interface and alphabet sections.
//   https://dwarffortresswiki.org/index.php/Map_legend — world map, site and
//     fast-travel characters, with their DF COLOR tokens.
//
// Tile record fields (all optional):
//   uses  [{t, f}]        canonical per-tile uses; f = modifiability flags
//   map   [{t, s, v}]     map legend: label, source table, and per-variant
//                         colours — v = [{n: variant name, c: [[fg, bg], …]}]
//   lists [{l, items, note}]  enumerated members (species, stones, …); item.w = wiki page
//   text  [role]          roles the glyph plays in on-screen text
//   names [race]          races whose name alphabet uses this accented glyph
//   unused true           wiki lists this tile as having no known use

'''

if __name__ == "__main__":
    main(*sys.argv[1:5])
