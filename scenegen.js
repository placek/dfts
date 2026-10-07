// Random Dwarf Fortress scene generator. Builds scenes in the same shape as
// scenes.js ({name, blurb, w, h, codes, fg, bg}) so the page can paint and
// inspect them exactly like the hand-made ones.
//
//   window.dfRandomScene(kind, seed, cp437) -> scene
//   window.DF_SCENE_KINDS                   -> ["surface", "fortress", "caverns"]
(function () {
  const BLACK = 0, BLUE = 1, GREEN = 2, CYAN = 3, RED = 4, MAGENTA = 5, BROWN = 6, GRAY = 7,
        DGRAY = 8, LBLUE = 9, LGREEN = 10, LCYAN = 11, LRED = 12, LMAGENTA = 13, YELLOW = 14, WHITE = 15;
  const DWARF = [LRED, YELLOW, LCYAN, LMAGENTA, LGREEN, WHITE, LBLUE];

  // Small seeded PRNG (mulberry32) so a scene can be reproduced from its seed.
  function mulberry32(a) {
    return function () {
      a |= 0; a = a + 0x6D2B79F5 | 0;
      let t = Math.imul(a ^ a >>> 15, 1 | a);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }

  // A scene under construction: parallel grids of glyph, foreground colour.
  function canvas(w, h, idx) {
    const glyph = Array.from({ length: h }, () => Array(w).fill(" "));
    const fg = Array.from({ length: h }, () => Array(w).fill(0));
    return {
      w, h, glyph, fg,
      inb: (x, y) => x >= 0 && y >= 0 && x < w && y < h,
      put(x, y, ch, col) { if (x >= 0 && y >= 0 && x < w && y < h) { glyph[y][x] = ch; fg[y][x] = col; } },
      get: (x, y) => (x >= 0 && y >= 0 && x < w && y < h ? glyph[y][x] : null),
      finish(name, blurb) {
        const codes = glyph.map(r => r.map(ch => {
          if (!(ch in idx)) throw new Error("not a CP437 glyph: " + ch);
          return idx[ch];
        }));
        return {
          name, blurb, w, h, codes,
          fg: fg.map(r => r.map(v => v.toString(16)).join("")),
          bg: fg.map(r => "0".repeat(r.length)),
        };
      },
    };
  }

  const helpers = rnd => ({
    int: (a, b) => a + Math.floor(rnd() * (b - a + 1)),
    pick: arr => arr[Math.floor(rnd() * arr.length)],
    chance: p => rnd() < p,
  });

  // Smooth value noise in [0,1): random lattice, bilinearly interpolated.
  function noise(rnd, w, h, cell) {
    const gw = Math.ceil(w / cell) + 2, gh = Math.ceil(h / cell) + 2;
    const g = Array.from({ length: gh }, () => Array.from({ length: gw }, rnd));
    const sm = t => t * t * (3 - 2 * t);
    return (x, y) => {
      const fx = x / cell, fy = y / cell, ix = Math.floor(fx), iy = Math.floor(fy);
      const tx = sm(fx - ix), ty = sm(fy - iy);
      const a = g[iy][ix] + (g[iy][ix + 1] - g[iy][ix]) * tx;
      const b = g[iy + 1][ix] + (g[iy + 1][ix + 1] - g[iy + 1][ix]) * tx;
      return a + (b - a) * ty;
    };
  }

  const GRASS = [['"', GREEN], [",", LGREEN], ["'", GREEN], [".", GREEN], ['"', LGREEN]];

  // ---- surface ------------------------------------------------------------
  function surface(rnd, idx) {
    const { int, pick, chance } = helpers(rnd);
    const W = 44, H = 16, c = canvas(W, H, idx);
    const forest = noise(rnd, W, H, 7), wet = noise(rnd, W, H, 9);
    const ford = pick([0, 1]);   // stream flows top-to-bottom or left-to-right

    // River: a random walk across the map, 3-7 tiles wide.
    const water = Array.from({ length: H }, () => Array(W).fill(0));
    const long = ford ? W : H;
    let pos = int(8, (ford ? H : W) - 9), width = int(1, 2);
    for (let t = 0; t < long; t++) {
      pos = Math.max(3, Math.min((ford ? H : W) - 4, pos + pick([-1, 0, 0, 1])));
      if (chance(.1)) width = Math.max(1, Math.min(3, width + pick([-1, 1])));
      for (let d = -width; d <= width; d++) {
        const x = ford ? t : pos + d, y = ford ? pos + d : t;
        if (c.inb(x, y)) water[y][x] = Math.abs(d) === width ? 1 : 2;   // shallow edge, deep middle
      }
    }
    // A pond for variety.
    if (chance(.35)) {
      const px = int(6, W - 7), py = int(4, H - 5), r = int(2, 2);
      for (let y = py - r; y <= py + r; y++) for (let x = px - r * 2; x <= px + r * 2; x++)
        if (c.inb(x, y) && ((x - px) / 2) ** 2 + (y - py) ** 2 <= r * r)
          water[y][x] = Math.max(water[y][x], ((x - px) / 2) ** 2 + (y - py) ** 2 < r * r * .5 ? 2 : 1);
    }

    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      if (water[y][x]) {
        c.put(x, y, "≈", water[y][x] === 2 ? BLUE : LBLUE);
        if (water[y][x] === 2 && chance(.04)) c.put(x, y, "α", LCYAN);
        continue;
      }
      const f = forest(x, y), r = rnd();
      const [gch, gcol] = pick(GRASS);
      if (f > .62 && r < .8) {
        c.put(x, y, r < .55 ? "♠" : (r < .7 ? "♣" : "↑"), r < .3 ? LGREEN : GREEN);
      } else if (f > .5 && r < .08) c.put(x, y, "♣", GREEN);
      else if (wet(x, y) > .7 && r < .15) c.put(x, y, "~", BROWN);   // flowing mud/trail
      else if (r < .02) c.put(x, y, "∞", pick([GRAY, DGRAY, BROWN]));
      else if (r < .045) c.put(x, y, "*", pick([YELLOW, LRED, LMAGENTA, WHITE]));   // wildflowers
      else c.put(x, y, gch, gcol);
    }

    // Wagon / depot on dry open ground.
    const sx = int(2, W - 9), sy = int(2, H - 6);
    let clear = true;
    for (let y = sy; y < sy + 4 && clear; y++) for (let x = sx; x < sx + 6; x++)
      if (!c.inb(x, y) || water[y][x]) { clear = false; break; }
    let placed = false;
    if (clear) {
      placed = true;
      for (let y = sy; y < sy + 4; y++) for (let x = sx; x < sx + 6; x++) {
        const edge = y === sy || y === sy + 3 || x === sx || x === sx + 5;
        if (!edge) { c.put(x, y, "·", BROWN); continue; }
        const top = y === sy, bot = y === sy + 3, l = x === sx, r2 = x === sx + 5;
        c.put(x, y, top ? (l ? "╔" : r2 ? "╗" : "═") : bot ? (l ? "╚" : r2 ? "╝" : "═") : "║", BROWN);
      }
      c.put(sx + 2, sy + 1, "≡", BROWN); c.put(sx + 3, sy + 1, "÷", BROWN);
      c.put(sx + 2, sy + 2, "Θ", BROWN); c.put(sx + 3, sy + 2, "■", GRAY);
      c.put(sx + int(1, 4), sy + 3, "┼", BROWN);   // door
    }
    // Dwarves around the wagon (or anywhere dry), and a few animals.
    const dry = () => { for (let i = 0; i < 80; i++) { const x = int(0, W - 1), y = int(0, H - 1); if (!water[y][x]) return [x, y]; } return [0, 0]; };
    const n = int(4, 8);
    for (let i = 0; i < n; i++) {
      let x, y;
      if (placed && i < n - 2) { x = sx + int(-2, 7); y = sy + int(-2, 5); } else [x, y] = dry();
      if (c.inb(x, y) && !water[y][x] && c.get(x, y) !== "║") c.put(x, y, i === 0 ? "☻" : "☺", i === 0 ? LBLUE : DWARF[i % DWARF.length]);
    }
    for (let i = int(1, 3); i > 0; i--) { const [x, y] = dry(); c.put(x, y, pick(["Y", "e", "Y"]), pick([BROWN, LRED, GRAY])); }
    return c.finish("Random surface", "Generated embark site — forest, water and the first wagon. Reload for another.");
  }

  // ---- fortress -----------------------------------------------------------
  const WALL = { 0: "■", 1: "║", 4: "║", 5: "║", 2: "═", 8: "═", 10: "═", 3: "╚", 6: "╔", 12: "╗", 9: "╝",
                 7: "╠", 13: "╣", 14: "╦", 11: "╩", 15: "╬" };

  function fortress(rnd, idx) {
    const { int, pick, chance } = helpers(rnd);
    const W = 50, H = 20, c = canvas(W, H, idx);
    const floor = Array.from({ length: H }, () => Array(W).fill(false));
    const rooms = [];
    const types = ["bedroom", "dining", "workshop", "stockpile", "bedroom", "storage", "statue"];

    for (let tries = 0; tries < 200 && rooms.length < 9; tries++) {
      const w = int(5, 13), h = int(3, 5), x = int(2, W - w - 3), y = int(2, H - h - 3);
      // Rooms (with a 2-tile margin for walls and corridors) must not overlap.
      if (rooms.some(r => x - 3 < r.x + r.w && x + w + 3 > r.x && y - 3 < r.y + r.h && y + h + 3 > r.y)) continue;
      rooms.push({ x, y, w, h, type: pick(types) });
    }
    rooms.sort((a, b) => a.x - b.x);
    for (const r of rooms) for (let y = r.y; y < r.y + r.h; y++) for (let x = r.x; x < r.x + r.w; x++) floor[y][x] = true;
    const inRoomRing = (x, y) => rooms.some(r =>
      x >= r.x - 1 && x <= r.x + r.w && y >= r.y - 1 && y <= r.y + r.h &&
      !(x >= r.x && x < r.x + r.w && y >= r.y && y < r.y + r.h));

    // Corridors: connect each room to the next with an L-shaped tunnel.
    const corridor = [];
    const carve = (x, y) => { if (!floor[y][x]) { floor[y][x] = true; corridor.push([x, y]); } };
    for (let i = 1; i < rooms.length; i++) {
      const a = rooms[i - 1], b = rooms[i];
      let x = a.x + (a.w >> 1), y = a.y + (a.h >> 1);
      const tx = b.x + (b.w >> 1), ty = b.y + (b.h >> 1);
      const horizFirst = chance(.5);
      const walk = (axis) => {
        if (axis === "h") while (x !== tx) { x += Math.sign(tx - x); carve(x, y); }
        else while (y !== ty) { y += Math.sign(ty - y); carve(x, y); }
      };
      if (horizFirst) { walk("h"); walk("v"); } else { walk("v"); walk("h"); }
    }

    // Rock everywhere, smooth walls hugging the carved space.
    const isFloor = (x, y) => c.inb(x, y) && floor[y][x];
    const nearFloor = (x, y) => { for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) if (isFloor(x + dx, y + dy)) return true; return false; };
    const isWall = (x, y) => c.inb(x, y) && !floor[y][x] && nearFloor(x, y);
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      if (floor[y][x]) c.put(x, y, "·", DGRAY);
      else if (isWall(x, y)) {
        const m = (isWall(x, y - 1) ? 1 : 0) | (isWall(x + 1, y) ? 2 : 0) | (isWall(x, y + 1) ? 4 : 0) | (isWall(x - 1, y) ? 8 : 0);
        c.put(x, y, WALL[m], GRAY);
      } else c.put(x, y, "▒", DGRAY);
    }
    // Doors where a corridor pierces a room's wall ring.
    for (const [x, y] of corridor) if (inRoomRing(x, y)) c.put(x, y, "┼", BROWN);

    // Furnish rooms by type.
    for (const r of rooms) {
      const cells = [];
      for (let y = r.y; y < r.y + r.h; y++) for (let x = r.x; x < r.x + r.w; x++) cells.push([x, y]);
      const free = (x, y) => c.get(x, y) === "·";
      const each = (fn) => cells.forEach(([x, y]) => free(x, y) && fn(x, y));
      if (r.type === "bedroom") {
        each((x, y) => { if ((x - r.x) % 2 === 1 && (y - r.y) % 2 === 0) c.put(x, y, "Θ", BROWN); else if ((x - r.x) % 2 === 1 && (y - r.y) === r.h - 1 && chance(.5)) c.put(x, y, "π", BROWN); });
      } else if (r.type === "dining") {
        each((x, y) => { const mid = (y - r.y) % 2 === 0; if (mid && (x - r.x) % 3 === 1) c.put(x, y, "╤", BROWN); else if (mid && (x - r.x) % 3 === 2) c.put(x, y, "╥", chance(.6) ? LRED : BROWN); });
      } else if (r.type === "workshop") {
        each((x, y) => { if ((x - r.x) % 4 < 3 && (y - r.y) % 3 === 1) c.put(x, y, ["•", "σ", "•"][(x - r.x) % 4], (x - r.x) % 4 === 1 ? WHITE : GRAY); });
      } else if (r.type === "stockpile") {
        each((x, y) => { if ((x - r.x) % 2 === 1 && (y - r.y) % 2 === 0) c.put(x, y, pick(["÷", "÷", "≡", "■"]), pick([BROWN, GRAY])); });
      } else if (r.type === "storage") {
        each((x, y) => { if ((y === r.y || y === r.y + r.h - 1) && (x - r.x) % 2 === 0 && chance(.8)) c.put(x, y, pick(["Æ", "π", "0"]), BROWN); });
      } else {
        each((x, y) => { if ((x - r.x) % 3 === 1 && (y - r.y) % 2 === 1) c.put(x, y, "Ω", WHITE); });
      }
    }
    // Stairs, dwarves, a stray animal.
    const open = [];
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) if (c.get(x, y) === "·") open.push([x, y]);
    const take = () => open.splice(int(0, open.length - 1), 1)[0];
    if (open.length > 12) {
      const s = take(); c.put(s[0], s[1], pick(["<", ">", "X"]), GRAY);
      for (let i = int(5, 9); i > 0; i--) { const d = take(); c.put(d[0], d[1], "☺", DWARF[i % DWARF.length]); }
      if (chance(.7)) { const a = take(); c.put(a[0], a[1], "Y", BROWN); }
      if (chance(.4)) { const a = take(); c.put(a[0], a[1], "☻", LBLUE); }
    }
    return c.finish("Random fortress", "Generated fortress level — rooms, doors and corridors cut into the rock. Reload for another.");
  }

  // ---- caverns ------------------------------------------------------------
  function caverns(rnd, idx) {
    const { int, pick, chance } = helpers(rnd);
    const W = 54, H = 20, c = canvas(W, H, idx);
    // Cellular automaton: seed random open space, then smooth into caves.
    let open = Array.from({ length: H }, (_, y) => Array.from({ length: W }, (_, x) =>
      x > 1 && y > 1 && x < W - 2 && y < H - 2 && rnd() < .47));
    for (let i = 0; i < 4; i++) {
      open = open.map((row, y) => row.map((_, x) => {
        let n = 0;
        for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
          const xx = x + dx, yy = y + dy;
          if (xx >= 0 && yy >= 0 && xx < W && yy < H && open[yy][xx]) n++;
        }
        return n >= 5;
      }));
    }
    const isOpen = (x, y) => c.inb(x, y) && open[y][x];
    const edge = (x, y) => !isOpen(x, y) && [[1, 0], [-1, 0], [0, 1], [0, -1]].some(([dx, dy]) => isOpen(x + dx, y + dy));

    const lake = noise(rnd, W, H, 8), fungus = noise(rnd, W, H, 6), fire = noise(rnd, W, H, 10);
    const lakeKind = chance(.6) ? "water" : "magma";
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      if (!isOpen(x, y)) { c.put(x, y, edge(x, y) ? "▓" : "▒", edge(x, y) ? GRAY : DGRAY); continue; }
      const l = lake(x, y), f = fungus(x, y);
      if (l > .66) {
        c.put(x, y, "≈", lakeKind === "water" ? (l > .74 ? BLUE : LBLUE) : (l > .74 ? RED : LRED));
        if (lakeKind === "water" && chance(.03)) c.put(x, y, "α", LCYAN);
      } else if (f > .62 && chance(.8)) {
        c.put(x, y, pick(["♠", "♠", "♣", "♣", "↑"]), pick([LGREEN, GREEN, CYAN, LBLUE]));
      } else if (fire(x, y) > .75 && chance(.3)) c.put(x, y, '"', LGREEN);
      else if (chance(.08)) c.put(x, y, pick([",", "'"]), DGRAY);
      else c.put(x, y, pick([".", "·", "·"]), pick([GRAY, DGRAY]));
    }
    // Gems and ore in the rock next to the caves.
    const gems = [LCYAN, LRED, LGREEN, YELLOW, MAGENTA, WHITE];
    for (let tries = 0; tries < 400; tries++) {
      const x = int(1, W - 2), y = int(1, H - 2);
      if (c.get(x, y) !== "▓" || !chance(.12)) continue;
      c.put(x, y, "♦", pick(gems));
    }
    for (let tries = 0; tries < 60; tries++) {
      const x = int(1, W - 2), y = int(1, H - 2);
      if (c.get(x, y) === "▒" && chance(.2)) c.put(x, y, "▓", GRAY);
    }
    // Residents: miners, boulders, one lobster, and (rarely) something nasty.
    const cells = [];
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) if (["·", ".", ",", "'"].includes(c.get(x, y))) cells.push([x, y]);
    const take = () => cells.length ? cells.splice(int(0, cells.length - 1), 1)[0] : [0, 0];
    for (let i = int(2, 4); i > 0; i--) { const d = take(); c.put(d[0], d[1], "☺", DWARF[i % DWARF.length]); }
    for (let i = int(3, 6); i > 0; i--) { const b = take(); c.put(b[0], b[1], "∞", pick([GRAY, BROWN])); }
    if (chance(.6)) { const l = take(); c.put(l[0], l[1], "¥", LRED); }
    if (chance(.5)) { const m = take(); c.put(m[0], m[1], "☼", YELLOW); }
    if (chance(.25)) { const d = take(); c.put(d[0], d[1], "&", LRED); }
    return c.finish("Random caverns", "Generated cavern level — cave-in rock, a " + (lakeKind === "water" ? "lake" : "magma pool") + ", fungus groves and gems. Reload for another.");
  }

  window.DF_SCENE_KINDS = ["surface", "fortress", "caverns"];
  window.dfRandomScene = function (kind, seed, cp437) {
    const idx = {};
    for (let code = 0; code < cp437.length; code++) if (!(cp437[code] in idx)) idx[cp437[code]] = code;
    const gen = { surface, fortress, caverns }[kind];
    const s = gen(mulberry32(seed >>> 0), idx);
    s.blurb += "  (" + kind + " · seed " + (seed >>> 0) + ")";
    return s;
  };
})();
