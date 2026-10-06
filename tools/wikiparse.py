"""Shared helpers for turning DF wiki markup into plain text."""
import html
import re
import unicodedata

FLAG_CHARS = "*#$¢÷"  # raws / graphic set / d_init / dual colour / inverted

# Characters the wiki writes with a different Unicode codepoint than CP437 uses.
CP437_ALIASES = {
    "μ": "µ",   # Greek mu -> micro sign (tile 230)
    "Π": "π",   # Greek capital Pi -> small pi (tile 227)
    "–": "-",
    "’": "'",
    "´": "'",        # acute accent -> apostrophe (tile 39)
}


def cp437_table(index_html):
    """Pull the CP437 string straight out of index.html so both stay in sync."""
    src = re.search(r"const CP437 =(.*?);\n", index_html, re.S).group(1)
    parts = re.findall(r'"((?:[^"\\]|\\.)*)"', src)
    def unescape(js):
        return re.sub(
            r'\\(u[0-9a-fA-F]{4}|.)',
            lambda m: chr(int(m.group(1)[1:], 16)) if m.group(1)[0] == "u" else m.group(1),
            js,
        )

    table = "".join(unescape(p) for p in parts)
    assert len(table) == 256, f"CP437 table is {len(table)} chars, expected 256"
    return table


def strip_markup(text):
    """Reduce wiki markup to display text, returning (text, links, flags)."""
    links = []

    def take_link(m):
        target, _, label = m.group(1).partition("|")
        links.append(target.strip())
        return (label or target).strip()

    text = re.sub(r"\{\{TST\|.*?\}\}", "", text)
    text = re.sub(r"\{\{version\|[^}]*\}\}", "", text)
    text = re.sub(r"\{\{!\}\}", "|", text)
    text = re.sub(r"\{\{=\}\}", "=", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", take_link, text)
    text = re.sub(r"\[https?://\S+\s+([^\]]*)\]", r"\1", text)
    text = re.sub(r"\[https?://\S+\]", "", text)

    flags = ""
    for m in re.finditer(r"<sup>(.*?)</sup>", text):
        flags += "".join(c for c in m.group(1) if c in FLAG_CHARS)
    text = re.sub(r"<sup>.*?</sup>", "", text)
    text = re.sub(r"<small>|</small>|<br\s*/?>", " ", text)
    text = re.sub(r"<[^>]+>", "", text)

    text = html.unescape(text).replace(" ", " ")
    text = text.replace("'''", "").replace("''", "")

    # Trailing bare '*' is the raws-modifiable marker, not part of the name.
    text = text.strip()
    while text.endswith("*"):
        flags += "*"
        text = text[:-1].strip()

    text = re.sub(r"\s+", " ", text).strip(" ,.;")
    return text, links, "".join(sorted(set(flags)))


def normalise_char(ch):
    ch = CP437_ALIASES.get(ch, ch)
    return unicodedata.normalize("NFC", ch)
