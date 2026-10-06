"""Parse the ASCII tables of the DF wiki 'Map legend' article."""
import html
import re
import sys

from wikiparse import normalise_char, strip_markup

# Top-level sections that describe ASCII map tiles, and the label we show for them.
SECTIONS = {
    "Biome/Region key": "World map biome",
    "Terrain feature key": "World map terrain",
    "Construction key": "World map construction",
    "Site key (ASCII)": "World map site",
    "Fast travel key": "Fast travel map",
}

TEMPLATE = re.compile(r"\{\{(Raw Tile|Biome)\|((?:[^{}]|\{\{[^{}]*\}\})*)\}\}")
CELL_STYLE = re.compile(r'^\s*(?:[a-z-]+\s*=\s*"[^"]*"\s*)+\|')


def colour(token):
    """DF COLOR token -> (foreground index 0-15, background index 0-15)."""
    token = token.strip()
    if not token or token.startswith("#") or ":" not in token:
        return None
    parts = token.split(":")
    try:
        nums = [int(p) for p in parts]
    except ValueError:
        return None
    if len(nums) == 2:
        fg, bright = nums
        return (fg + 8 * bright, 0)
    if len(nums) >= 3:
        fg, bg, bright = nums[0], nums[1], nums[2]
        return (fg + 8 * bright, bg)
    return None


def chars_of(raw):
    raw = raw.replace("{{=}}", "=").replace("{{!}}", "|")
    raw = html.unescape(raw).strip()
    return [normalise_char(c) for c in raw if not c.isspace()]


def tiles_in_cell(cell):
    """Yield (char, fg, bg) for every tile template in a table cell."""
    for kind, body in ((m.group(1), m.group(2)) for m in TEMPLATE.finditer(cell)):
        params = body.split("|")
        if kind == "Raw Tile":
            if len(params) < 2:
                continue
            col = colour(params[1])
            for ch in chars_of(params[0]):
                yield ch, col
        else:  # Biome: two characters, one or two colour tokens
            if len(params) < 3:
                continue
            cols = [colour(params[2])]
            if len(params) > 3 and params[3].strip() and params[3].strip() != "altc":
                cols.append(colour(params[3]))
            for ch in chars_of(params[0]) + chars_of(params[1]):
                for col in cols:
                    yield ch, col


def parse(lines):
    """Return {char: [ {label, section, variant, cols:[(fg,bg)]} ]}."""
    out = {}
    path = []
    table = None
    for raw in lines:
        m = re.match(r"^(={2,4})\s*(.*?)\s*=+\s*$", raw)
        if m:
            path = path[: len(m.group(1)) - 2] + [m.group(2)]
            table = None
            continue
        section = SECTIONS.get(path[0]) if path else None
        if not section or "Graphics" in path:
            continue

        if raw.startswith("{|"):
            table = {"headers": [], "rows": []}
            continue
        if table is None:
            continue
        if raw.startswith("|}"):
            emit(table, section, out)
            table = None
            continue
        if raw.startswith("!"):
            for cell in raw.lstrip("!").split("!!"):
                table["headers"].append(strip_markup(cell.lstrip("|"))[0])
            continue
        if raw.startswith("|-"):
            table["rows"].append([])
            continue
        if raw.startswith("|"):
            if not table["rows"]:
                table["rows"].append([])
            body = raw[1:]
            body = CELL_STYLE.sub("", "|" + body) if CELL_STYLE.match("|" + body) else body
            table["rows"][-1].append(body)
            continue
        if table["rows"] and table["rows"][-1]:
            table["rows"][-1][-1] += "\n" + raw
    return out


def emit(table, section, out):
    headers = table["headers"]
    for row in table["rows"]:
        if not row:
            continue
        label = strip_markup(row[0])[0]
        if not label:
            continue
        for idx, cell in enumerate(row[1:], start=1):
            variant = headers[idx] if idx < len(headers) else ""
            seen = {}
            for ch, col in tiles_in_cell(cell):
                seen.setdefault(ch, [])
                if col and col not in seen[ch]:
                    seen[ch].append(col)
            for ch, cols in seen.items():
                out.setdefault(ch, []).append(
                    {"label": label, "section": section, "variant": variant, "cols": cols}
                )


if __name__ == "__main__":
    lines = open(sys.argv[1], encoding="utf-8").read().split("\n")
    res = parse(lines)
    for ch, entries in res.items():
        print(repr(ch), len(entries), sorted({e["label"] for e in entries}))
