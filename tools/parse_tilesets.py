"""Parse the DF wiki Tilesets article into per-tile data."""
import re
import sys

from wikiparse import normalise_char, strip_markup

ROW_HEADING = re.compile(r"^====\s*Row \d+ \((\d+)-(\d+)\)\s*====")
TILE_CELL = re.compile(r'^\|(?:[^|]*\|)?\s*<small>(\d{1,3})</small>')


def parse_rows(lines):
    """The 'What tiles are used for what' tables: tile -> list of uses."""
    uses = {}
    row_section = False
    tile = None
    for raw in lines:
        if raw.startswith("===="):
            row_section = bool(ROW_HEADING.match(raw))
            tile = None
            continue
        if not row_section:
            continue
        m = TILE_CELL.match(raw)
        if m:
            tile = int(m.group(1))
            uses.setdefault(tile, [])
            continue
        if raw.startswith("|}"):
            tile = None
            continue
        if tile is not None and raw.startswith("|"):
            body = raw[1:]
            if body.strip() in ("-", ""):
                if body.strip() == "-":
                    tile = None
                continue
            uses[tile] = split_uses(body)
            tile = None
    return uses


def split_uses(body):
    """Split a wiki description cell into individual uses."""
    out = []
    for chunk in split_top_level(body):
        text, links, flags = strip_markup(chunk)
        if not text:
            continue
        out.append({"text": text, "links": links, "flags": flags})
    return out


def split_top_level(body):
    """Split on commas that are not inside brackets/parens."""
    depth = 0
    cur = ""
    for ch in body:
        if ch in "[({":
            depth += 1
        elif ch in "])}":
            depth = max(0, depth - 1)
        if ch == "," and depth == 0:
            cur, out = "", cur
            yield out
            continue
        cur += ch
    if cur.strip():
        yield cur


def parse_detail_sections(lines, cp437):
    """The 'Detailed use list by type' sections: tile -> {section: [members]}."""
    sections = {}
    path = []
    for raw in lines:
        m = re.match(r"^(={2,4})\s*(.*?)\s*=+\s*$", raw)
        if m:
            level = len(m.group(1))
            path = path[: level - 2] + [m.group(2)]
            continue
        if len(path) < 2 or path[0] != "Detailed use list by type":
            continue
        key = " / ".join(path[1:])
        sections.setdefault(key, []).append(raw)
    return sections


def tiles_from_section(lines):
    """Within one detail section, pull <small>NNN</small> blocks and their bodies."""
    blocks = []
    cur = None
    for raw in lines:
        for m in re.finditer(r"<small>\s*(\d{1,3})\s*</small>", raw):
            tile = int(m.group(1))
            rest = raw[m.end():]
            cur = {"tile": tile, "body": [rest]}
            blocks.append(cur)
        if cur is not None and not re.search(r"<small>\s*\d{1,3}\s*</small>", raw):
            cur["body"].append(raw)
    for b in blocks:
        b["body"] = "\n".join(b["body"])
    return blocks


if __name__ == "__main__":
    lines = open(sys.argv[1], encoding="utf-8").read().split("\n")
    uses = parse_rows(lines)
    print(f"tiles with a row entry: {len(uses)}")
    missing = [i for i in range(256) if i not in uses]
    print(f"missing from row tables: {missing}")
    for i in range(256):
        u = uses.get(i)
        if u is None:
            continue
        print(f"{i:3d}  " + " | ".join(
            e["text"] + (f" [{e['flags']}]" if e["flags"] else "") for e in u) )
