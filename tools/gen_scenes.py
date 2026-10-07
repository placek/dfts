#!/usr/bin/env python3
"""Generate scenes.js: small Dwarf Fortress "screenshots" built from tileset glyphs.

Each scene is drawn below as ASCII art plus a legend mapping a drawing key to
(CP437 glyph, foreground colour index, background colour index). The output
stores, per scene, a grid of tile codes with foreground / background colours,
so the page can paint it with the same sprites as the tileset grid.

    python3 gen_scenes.py ../index.html ../scenes.js
"""
import json
import random
import sys

from wikiparse import cp437_table

# Colour indices into the 16-colour DF palette used by index.html.
BLACK, BLUE, GREEN, CYAN, RED, MAGENTA, BROWN, GRAY = range(8)
DGRAY, LBLUE, LGREEN, LCYAN, LRED, LMAGENTA, YELLOW, WHITE = range(8, 16)

GRASS = [('"', GREEN), (",", LGREEN), ("'", GREEN), (".", GREEN), ('"', LGREEN)]
DWARF = [LRED, YELLOW, LCYAN, LMAGENTA, LGREEN, WHITE, LBLUE]

SCENES = []


def scene(name, blurb, legend, rows, grass=None, pad=" ", seed=1):
    SCENES.append(dict(name=name, blurb=blurb, legend=legend, rows=rows,
                       grass=grass, pad=pad, seed=seed))


# --------------------------------------------------------------------------
scene(
    "Embark site",
    "A fresh embark on the surface: forest, a stream, wildlife and the first wagon.",
    {
        "^": ("♠", GREEN), "T": ("♠", LGREEN), "q": ("♣", GREEN), "Q": ("♣", LGREEN),
        "c": ("↑", GREEN), "s": ("\"", LGREEN), "o": ("∞", GRAY), "O": ("∞", DGRAY),
        "~": ("≈", LBLUE), "=": ("≈", BLUE), "f": ("α", LCYAN),
        "d": ("☺", DWARF), "m": ("☻", LBLUE), "Y": ("Y", BROWN), "e": ("e", LRED),
        "#": ("█", BROWN), "w": ("•", BROWN), "[": ("╔", BROWN), "]": ("╗", BROWN),
        "{": ("╚", BROWN), "}": ("╝", BROWN), "-": ("═", BROWN), "|": ("║", BROWN),
        "h": ("♦", LCYAN), "%": ("%", DGRAY), ":": (".", BROWN), "x": ("☼", YELLOW),
        "a": ("♣", BROWN), "p": ("≡", BROWN), "b": ("÷", BROWN), "k": ("Θ", BROWN),
    },
    [
        "ccc^^^T^^____ss____sTT^^^^_s_ss_^^^^Tcc",
        "cc^T^^^q__ss__~~~~~____Q__ss____^^T^^^cc",
        "c^^^T^__s___~~=====~~____s___e___s^^^T^^",
        "^^T^__ss__~~====f===~~~___ss__ss____^^^^",
        "^^___s___~~===========~~~____o_____q_^^T",
        "T_____ss_~====f========~~__ss__ssQ_____^",
        "___ss____~~=======f===~~_____:::::::____",
        "__s_______~~~=====~~~~____ssss:[---]:__s",
        "_q_ss__d____~~~~~~~___ss_____:|p#b|:___",
        "___s____m_d__s_____sss_____::::{--}:::__",
        "__o_s_____ss_______s__Y______x__:::_____",
        "^_______sss___d_____sss__ss_hq_d__ssY_^^",
        "^^T___ss_____ss______s______ss_____s_^^^",
        "T^^^__s_Q____ss__o_____ss_O____ss__^^^T^",
        "^T^^^c__s_sss_____s_____s____ssss_c^^^^^",
    ],
    grass="_", seed=7,
)

TOP = "╔" + "═" * 14 + "╦" + "═" * 15 + "╦" + "═" * 13 + "╗"
BOTTOM = "╚════╩" + "═" * 25 + "╩" + "═" * 13 + "╝"

# --------------------------------------------------------------------------
scene(
    "Fortress interior",
    "One z-level of a dwarven fort: bedrooms, a dining hall, workshops, a stockpile, "
    "a flooded cistern and the stairs down.",
    {
        # smooth walls: key is the box-drawing glyph itself
        "╔": ("╔", GRAY), "╗": ("╗", GRAY), "╚": ("╚", GRAY), "╝": ("╝", GRAY),
        "═": ("═", GRAY), "║": ("║", GRAY), "╦": ("╦", GRAY), "╩": ("╩", GRAY),
        "╠": ("╠", GRAY), "╣": ("╣", GRAY), "╬": ("╬", GRAY),
        ".": ("·", DGRAY), ",": (".", DGRAY),
        "D": ("┼", BROWN), "Z": ("╫", BROWN), "U": ("▲", GRAY),
        "<": ("<", GRAY), ">": (">", GRAY), "X": ("X", GRAY),
        "b": ("Θ", BROWN), "c": ("╤", BROWN), "t": ("╥", BROWN), "h": ("╥", LRED),
        "s": ("Ω", WHITE), "k": ("π", BROWN), "C": ("Æ", BROWN), "o": ("0", BROWN),
        "B": ("÷", BROWN), "R": ("≡", GRAY), "F": ("σ", GRAY),
        "w": ("•", GRAY), "W": ("•", BROWN), "A": ("σ", WHITE), "M": ("•", RED),
        "m": ("■", GRAY), "n": ("■", BROWN), "g": ("♦", LCYAN), "j": ("♦", LRED),
        "i": ("*", YELLOW), "T": ("=", DGRAY), "L": ("ò", LRED), "l": ("ó", LGREEN),
        "~": ("≈", LBLUE), "=": ("≈", BLUE), "f": ("α", LCYAN),
        "d": ("☺", DWARF), "!": ("☻", LBLUE),
        "y": ("Y", BROWN), "p": ("↨", BROWN), "r": ("²", BROWN), "u": ("═", BROWN),
        "8": ("☼", YELLOW), "9": ("%", DGRAY), "z": ("≈", LRED),
        "e": ("║", BROWN), "q": ("•", DGRAY),
    },
    [
        TOP,
        "║.b.b.b.b.b.b..║" + "..cttc..cttc..." + "║" + "..R.R.R.R.R.." + "║",
        "║..............║" + "..h.d....h.d..." + "║" + ".mmm.nnn.mmm." + "║",
        "║.k.k.k.k.k.k..D" + "..cttc..cttc..s" + "D" + ".mmm.nnn.mmm." + "║",
        "╠═══D═════D════╣" + "..h.....d..h..." + "║" + "..B.B.B.B.B.." + "║",
        "║.b.b.C.o.b.b..║" + "..s.....s......" + "║" + "..B.B.B.B.B.." + "║",
        "║..d...d.......║" + ".C.C.C......k.k" + "╠═══Z═════════╣",
        "╠═══════D══════╩" + "═══D═══════════" + "╣" + "..w.A.w......" + "║",
        "║" + "~~~~║" + "....w.A.w".ljust(25, ".") + "║" + "..W.W.M.q...." + "║",
        "║" + "=f~~║" + "....w.w.w........U".ljust(25, ".") + "╠═══D═════════╣",
        "║" + "~~~~D" + "....L....<........>..X".ljust(25, ".") + "║" + "..R.n.n.i...." + "║",
        "║" + "~~=~║" + "....................y".ljust(25, ".") + "║" + "..d.....y...." + "║",
        BOTTOM,
    ],
)

# --------------------------------------------------------------------------
scene(
    "Deep caverns",
    "Digging deeper: unexplored rock, ore veins, gems, a magma river and something "
    "that really should have stayed asleep.",
    {
        "#": ("▒", DGRAY), "%": ("▓", GRAY), "$": ("░", DGRAY), "r": ("█", BROWN),
        ".": (".", GRAY), ",": (",", DGRAY), ":": ("·", DGRAY), "'": ("'", BROWN),
        "o": ("∞", GRAY), "O": ("∞", BROWN), "0": ("0", RED),
        "g": ("♦", LCYAN), "j": ("♦", LRED), "v": ("♦", LGREEN), "e": ("♦", YELLOW),
        "n": ("♦", MAGENTA),
        "*": ("☼", YELLOW), "m": ("≈", LRED), "M": ("≈", RED), "~": ("≈", LBLUE),
        "=": ("≈", BLUE), "f": ("α", LCYAN),
        "d": ("☺", DWARF), "!": ("☻", LBLUE), "&": ("&", LRED), "L": ("¥", LRED),
        "S": ("♠", LGREEN), "q": ("♣", GREEN), "\"": ("\"", LGREEN), "H": ("♠", CYAN),
        "t": ("♣", LBLUE), "u": ("Σ", YELLOW), "B": ("÷", BROWN), "X": ("╬", GRAY),
        "<": ("<", GRAY), ">": (">", GRAY), "Z": ("Z", GRAY),
        "w": ("▲", GRAY), "W": ("▼", GRAY), "a": ("☺", LRED),
        "z": ("╬", BROWN), "-": ("═", BROWN), "|": ("║", BROWN), "k": ("╤", BROWN),
        "p": ("δ", LBLUE), "l": ("æ", GRAY),
    },
    [
        "####################################################",
        "#####%%%###########$$$$$$$#######%%%%%###############",
        "####%%g%%%#######$$$$$:::$$$$#####%%j%%%%############",
        "###%%%%e%%%###$$$$:::::,,::::$$####%%%%%%%###########",
        "###%%%v%%%%##$$:::::,,,,,,,,::::$$##%%%%%%############",
        "####%%%%%%####$::,,\"\"qqS\"\",,,:::$$#####%%n%%#########",
        "#######%%#####::,,qSSHHtS\"\"\",,,::$$#####%%%%%#########",
        "#######d######:,\"qSHHtttHSq\"\",,::$$#########L########",
        "######rrr####::,\"SHtt!ttHS\"\",,::$$$####%%%%%%%%######",
        "####a.rrr..##::,,qSHtttHSq,,,:::$$$$###%%%%%%j%%%####",
        "###O..:::...$::::,,\"\"qq\"\",:::::$$$$$##%%%%%%%%%######",
        "#####.d.,.O.$$$$:::::,,,,::::::$$$$########%%%%######",
        "#######.:..*.$$$$$$:::::::::$$$$$$#######&##########",
        "########MMMMMMMMM%%%$$$$$$$$$$$##########%%%%########",
        "#######MmmmmmmmmmMM%%#########%%%%%%%######%%%########",
        "#######MmmmmmmmmmmMM%%######%%%%e%%%%%######%%u######",
        "####%%##MMmmmmmmmmMM%%%#####%%%%%%%%%%%######%%######",
        "####%%%###MMMMMMMMMM%%%%####%%%%%%%%%%%%#############",
    ],
    pad="#", seed=3,
)

# --------------------------------------------------------------------------


def build(table):
    index = {}
    for code, ch in enumerate(table):
        index.setdefault(ch, code)
    out = []
    for s in SCENES:
        rng = random.Random(s["seed"])
        w = max(len(r) for r in s["rows"])
        legend = s["legend"]
        codes, fgs, bgs = [], [], []
        dwarf_i = 0
        for row in s["rows"]:
            row = row.ljust(w, s["grass"] or s["pad"])
            rc, rf, rb = [], [], []
            for ch in row:
                if ch == " ":
                    rc.append(32); rf.append(0); rb.append(0); continue
                if ch == s["grass"]:
                    ch2, fg = rng.choice(GRASS)
                    rc.append(index[ch2]); rf.append(fg); rb.append(0); continue
                if ch not in legend:
                    sys.exit(f"scene {s['name']!r}: no legend entry for {ch!r}")
                glyph, fg = legend[ch]
                if isinstance(fg, list):
                    fg = fg[dwarf_i % len(fg)]; dwarf_i += 1
                if glyph not in index:
                    sys.exit(f"scene {s['name']!r}: {glyph!r} is not a CP437 glyph")
                rc.append(index[glyph]); rf.append(fg); rb.append(0)
            codes.append(rc); fgs.append(rf); bgs.append(rb)
        out.append(dict(name=s["name"], blurb=s["blurb"], w=w, h=len(s["rows"]),
                        codes=codes, fg=["".join(f"{v:x}" for v in r) for r in fgs],
                        bg=["".join(f"{v:x}" for v in r) for r in bgs]))
    return out


def main():
    index_html, dest = sys.argv[1:3]
    table = cp437_table(open(index_html, encoding="utf-8").read())
    scenes = build(table)
    with open(dest, "w", encoding="utf-8") as f:
        f.write("// Generated by tools/gen_scenes.py — do not edit by hand.\n"
                "// Each scene: w×h grid of tile codes plus foreground / background\n"
                "// palette indices (one hex digit per cell).\n"
                "window.DF_SCENES = [\n")
        for i, s in enumerate(scenes):
            f.write("  {\n")
            f.write(f'    "name": {json.dumps(s["name"], ensure_ascii=False)},\n')
            f.write(f'    "blurb": {json.dumps(s["blurb"], ensure_ascii=False)},\n')
            f.write(f'    "w": {s["w"]}, "h": {s["h"]},\n')
            f.write('    "codes": [\n' + ",\n".join(
                "      " + json.dumps(r) for r in s["codes"]) + "\n    ],\n")
            f.write(f'    "fg": {json.dumps(s["fg"])},\n')
            f.write(f'    "bg": {json.dumps(s["bg"])}\n')
            f.write("  }" + ("," if i < len(scenes) - 1 else "") + "\n")
        f.write("];\n")
    # Text preview so scene layouts can be checked without a browser.
    for s in scenes:
        print(f"== {s['name']} ({s['w']}x{s['h']})")
        for r in s["codes"]:
            print("".join(table[c] for c in r))


if __name__ == "__main__":
    main()
