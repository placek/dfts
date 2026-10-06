"""Sanity-check the generated data.js against expectations."""
import json
import re
import sys


def load(path="../data.js"):
    src = open(path, encoding="utf-8").read()
    body = src.split("window.DF_TILES = ", 1)[1].rstrip().rstrip(";")
    return json.loads(body)


def show(tiles, idx, cp437):
    t = tiles[str(idx)]
    print(f"\n=== tile {idx}  {cp437[idx]!r} ===")
    for u in t.get("uses", []):
        print(f"   use   {u['t']}" + (f"  [{u['f']}]" if "f" in u else ""))
    for m in t.get("map", []):
        vs = "; ".join(f"{v['n'] or '-'}={v['c']}" for v in m["v"])
        print(f"   map   {m['t']:28s} {m['s']:22s} {vs}")
    for l in t.get("lists", []):
        items = ", ".join(i["t"] for i in l["items"])
        print(f"   list  {l['l']}: {items[:150]}{'…' if len(items) > 150 else ''}"
              + (f"  (note: {l['note']})" if l.get("note") else ""))
    for k in ("text", "names"):
        if k in t:
            print(f"   {k:5s} {t[k]}")
    if t.get("unused"):
        print("   unused: wiki lists no known use")


if __name__ == "__main__":
    sys.path.insert(0, ".")
    from wikiparse import cp437_table
    cp437 = cp437_table(open("../index.html", encoding="utf-8").read())
    tiles = load()
    for idx in [int(a) for a in sys.argv[1:]]:
        show(tiles, idx, cp437)
