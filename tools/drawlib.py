"""Общая библиотека чертежей: координаты, примитивы, размеры, сборка листа SVG.

Используется скриптами tools/draw_<категория>.py. Каждый элемент описывается функцией-
строителем, которая возвращает два вида (основной и вспомогательный) — см. build().
"""
import math
import re
import sys
from html import escape
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

W, H = 1000, 720
FRONT_BOX = (30, 100, 620, 560)   # x, y, w, h
SIDE_BOX = (670, 100, 300, 560)
PAD = 75                          # px вокруг объекта под размерные линии
SIDE_PAD_X = 55                   # по горизонтали на виде сбоку

INK = "#222"
DIM = "#555"
FLOOR = "#888"
S3 = math.sqrt(3)


def hex_colors(s):
    return re.findall(r"#[0-9A-Fa-f]{6}", s or "")


class View:
    def __init__(self, box, ext, k, floor=True):
        x, y, w, h = box
        xmin, xmax, ymin, ymax = ext
        self.k, self.box, self.ext, self.floor = k, box, ext, floor
        self.ox = x + w / 2 - (xmin + xmax) / 2 * k
        self.oy = y + h / 2 + (ymin + ymax) / 2 * k
        self.out = []

    # --- координаты
    def X(self, x): return self.ox + x * self.k
    def Y(self, y): return self.oy - y * self.k
    def P(self, x, y): return f"{self.X(x):.1f},{self.Y(y):.1f}"

    # --- примитивы (в мм модели)
    def rect(self, x, y, w, h, fill="#ccc", stroke=INK, sw=1.2, extra=""):
        self.out.append(
            f'<rect x="{self.X(x):.1f}" y="{self.Y(y + h):.1f}" width="{max(w * self.k, 1):.1f}" '
            f'height="{max(h * self.k, 1):.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')

    def poly(self, pts, fill="#ccc", stroke=INK, sw=1.2):
        self.out.append(f'<polygon points="{" ".join(self.P(*p) for p in pts)}" fill="{fill}" '
                        f'stroke="{stroke}" stroke-width="{sw}"/>')

    def holed(self, outer, inners, fill, stroke=INK, sw=1.2):
        """Фигура с отверстиями: outer/inners — списки точек или ('circle', cx, cy, r)."""
        def sub(sh):
            if sh[0] == "circle":
                _, cx, cy, r = sh
                R = r * self.k
                X, Y = self.X(cx), self.Y(cy)
                return (f"M{X - R:.1f},{Y:.1f} a{R:.1f},{R:.1f} 0 1,0 {2 * R:.1f},0 "
                        f"a{R:.1f},{R:.1f} 0 1,0 {-2 * R:.1f},0 Z")
            return "M" + " L".join(self.P(*p) for p in sh) + " Z"
        d = " ".join(sub(s) for s in [outer] + list(inners))
        self.out.append(f'<path d="{d}" fill="{fill}" fill-rule="evenodd" stroke="{stroke}" stroke-width="{sw}"/>')

    def raw(self, s): self.out.append(s)

    def line(self, x1, y1, x2, y2, stroke=INK, sw=1.2, extra=""):
        self.out.append(f'<line x1="{self.X(x1):.1f}" y1="{self.Y(y1):.1f}" x2="{self.X(x2):.1f}" '
                        f'y2="{self.Y(y2):.1f}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')

    def text(self, x, y, s, size=12, anchor="middle", fill=INK, extra=""):
        self.out.append(f'<text x="{self.X(x):.1f}" y="{self.Y(y):.1f}" font-size="{size}" '
                        f'text-anchor="{anchor}" fill="{fill}" {extra}>{escape(str(s))}</text>')

    # --- размеры
    def hdim(self, x1, x2, y, off, label):
        """Горизонтальный размер. off>0 — выше точки y (в px), off<0 — ниже."""
        yy = self.Y(y) - off
        X1, X2 = self.X(x1), self.X(x2)
        g = 3 if off > 0 else -3
        self.out.append(f'<line x1="{X1:.1f}" y1="{self.Y(y) - g:.1f}" x2="{X1:.1f}" y2="{yy - g:.1f}" class="ext"/>')
        self.out.append(f'<line x1="{X2:.1f}" y1="{self.Y(y) - g:.1f}" x2="{X2:.1f}" y2="{yy - g:.1f}" class="ext"/>')
        self.out.append(f'<line x1="{X1:.1f}" y1="{yy:.1f}" x2="{X2:.1f}" y2="{yy:.1f}" class="dim"/>')
        self.out.append(f'<text x="{(X1 + X2) / 2:.1f}" y="{yy - 4:.1f}" class="dt">{escape(str(label))}</text>')

    def vdim(self, y1, y2, x, off, label):
        """Вертикальный размер. off>0 — правее точки x (в px), off<0 — левее."""
        xx = self.X(x) + off
        Y1, Y2 = self.Y(y1), self.Y(y2)
        g = 3 if off > 0 else -3
        self.out.append(f'<line x1="{self.X(x) + g:.1f}" y1="{Y1:.1f}" x2="{xx + g:.1f}" y2="{Y1:.1f}" class="ext"/>')
        self.out.append(f'<line x1="{self.X(x) + g:.1f}" y1="{Y2:.1f}" x2="{xx + g:.1f}" y2="{Y2:.1f}" class="ext"/>')
        self.out.append(f'<line x1="{xx:.1f}" y1="{Y1:.1f}" x2="{xx:.1f}" y2="{Y2:.1f}" class="dim"/>')
        tx = xx - 5 if off < 0 else xx + 5
        ty = (Y1 + Y2) / 2
        self.out.append(f'<text x="{tx:.1f}" y="{ty:.1f}" class="dt" '
                        f'transform="rotate(-90 {tx:.1f} {ty:.1f})" dy="{"-0" if off < 0 else "10"}">{escape(str(label))}</text>')

    def idim(self, x1, y1, x2, y2, label, side=1):
        """Внутренний размер между двумя точками (например, проём)."""
        X1, Y1, X2, Y2 = self.X(x1), self.Y(y1), self.X(x2), self.Y(y2)
        self.out.append(f'<line x1="{X1:.1f}" y1="{Y1:.1f}" x2="{X2:.1f}" y2="{Y2:.1f}" class="dim in"/>')
        mx, my = (X1 + X2) / 2, (Y1 + Y2) / 2
        if abs(X2 - X1) >= abs(Y2 - Y1):
            self.out.append(f'<text x="{mx:.1f}" y="{my - 5 * side:.1f}" class="dt in" '
                            f'dy="{0 if side > 0 else 9}">{escape(str(label))}</text>')
        else:
            tx = mx - 5 * side
            self.out.append(f'<text x="{tx:.1f}" y="{my:.1f}" class="dt in" '
                            f'transform="rotate(-90 {tx:.1f} {my:.1f})">{escape(str(label))}</text>')

    def flight(self, y, direction="h"):
        """Стрелка направления пролёта."""
        if direction == "h":
            x2 = self.X(self.ext[0]) - 14
            x1 = x2 - 42
            yy = self.Y(y)
            self.out.append(f'<line x1="{x1:.1f}" y1="{yy:.1f}" x2="{x2:.1f}" y2="{yy:.1f}" class="fl"/>')
            self.out.append(f'<text x="{(x1 + x2) / 2:.1f}" y="{yy - 6:.1f}" class="ft">пролёт</text>')
        else:
            xx, y1 = self.X(0), self.Y(self.ext[3]) - 100
            self.out.append(f'<line x1="{xx:.1f}" y1="{y1:.1f}" x2="{xx:.1f}" y2="{y1 + 44:.1f}" class="fl"/>')
            self.out.append(f'<text x="{xx + 8:.1f}" y="{y1 + 14:.1f}" class="ft" text-anchor="start">пролёт</text>')

    def arrow_px(self, x, y, dx, dy, label="пролёт"):
        """Стрелка пролёта от точки модели (x, y) со смещением dx, dy в px."""
        X1, Y1 = self.X(x), self.Y(y)
        self.out.append(f'<line x1="{X1:.1f}" y1="{Y1:.1f}" x2="{X1 + dx:.1f}" y2="{Y1 + dy:.1f}" class="fl"/>')
        self.out.append(f'<text x="{X1 + dx / 2 + (10 if dx == 0 else 0):.1f}" y="{Y1 + dy / 2 - 6:.1f}" class="ft" '
                        f'text-anchor="{"start" if dx == 0 else "middle"}">{label}</text>')

    def draw_floor(self):
        if not self.floor:
            return
        x, _, w, _ = self.box
        y0 = self.Y(0)
        x1, x2 = x + 8, x + w - 8
        self.out.append(f'<line x1="{x1}" y1="{y0:.1f}" x2="{x2}" y2="{y0:.1f}" stroke="{FLOOR}" stroke-width="1.5"/>')
        for xx in range(int(x1), int(x2), 12):
            self.out.append(f'<line x1="{xx}" y1="{y0 + 1:.1f}" x2="{xx - 7}" y2="{y0 + 8:.1f}" '
                            f'stroke="{FLOOR}" stroke-width="0.8"/>')

    def ceiling(self, y):
        x, _, w, _ = self.box
        yy = self.Y(y)
        x1, x2 = x + 8, x + w - 8
        self.out.append(f'<line x1="{x1}" y1="{yy:.1f}" x2="{x2}" y2="{yy:.1f}" stroke="{FLOOR}" stroke-width="1.5"/>')
        for xx in range(int(x1), int(x2), 12):
            self.out.append(f'<line x1="{xx}" y1="{yy - 1:.1f}" x2="{xx + 7}" y2="{yy - 8:.1f}" '
                            f'stroke="{FLOOR}" stroke-width="0.8"/>')


# ---------------------------------------------------------------- геометрия форм
def rect_pts(x, y, w, h):
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def reg_poly(n, cy, flats, phase):
    rc = (flats / 2) / math.cos(math.pi / n)
    return [(rc * math.cos(math.radians(phase + 360 / n * i)),
             cy + rc * math.sin(math.radians(phase + 360 / n * i))) for i in range(n)]


def thin_side(v, y0, h, color, t=8, feet=None, base=None):
    """Вид сбоку на плоские ворота: ребро толщиной t, опционально лапки/подставка."""
    if base:
        bw, bh = base
        v.rect(-bw / 2, 0, bw, bh, fill="#9e9e9e")
    if feet:
        v.rect(-feet / 2, 0, feet, 6, fill="#666")
    v.rect(-t / 2, y0, t, h, fill=color)


# ---------------------------------------------------------------- сборка листа
STYLE = """
<style>
  .dim{stroke:#555;stroke-width:0.9;fill:none;marker-start:url(#ar);marker-end:url(#ar)}
  .dim.in{stroke:#0057B8}
  .ext{stroke:#888;stroke-width:0.6}
  .dt{font-size:12px;fill:#333;text-anchor:middle;font-family:Arial,Helvetica,sans-serif;paint-order:stroke;stroke:#fff;stroke-width:3px;stroke-linejoin:round}
  .dt.in{fill:#0057B8}
  .fl{stroke:#2E7D32;stroke-width:2;marker-end:url(#fa)}
  .ft{font-size:11px;fill:#2E7D32;text-anchor:middle;font-family:Arial,Helvetica,sans-serif;paint-order:stroke;stroke:#fff;stroke-width:3px}
  .incircle{fill:none;stroke:#0057B8;stroke-width:0.8;stroke-dasharray:4 3}
  text{font-family:Arial,Helvetica,sans-serif}
</style>
<defs>
  <marker id="ar" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7"
          orient="auto-start-reverse"><path d="M0,1 L10,5 L0,9 z" fill="#555"/></marker>
  <marker id="fa" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6"
          orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#2E7D32"/></marker>
  <linearGradient id="cylv" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#000" stop-opacity="0.28"/><stop offset="0.35" stop-color="#fff" stop-opacity="0.35"/>
    <stop offset="1" stop-color="#000" stop-opacity="0.32"/></linearGradient>
  <linearGradient id="cylh" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#000" stop-opacity="0.28"/><stop offset="0.35" stop-color="#fff" stop-opacity="0.35"/>
    <stop offset="1" stop-color="#000" stop-opacity="0.32"/></linearGradient>
  <filter id="glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="6"/></filter>
</defs>
"""


def merged(e, v):
    m = {k: e.get(k) for k in ("color", "material", "rigidity", "difficulty", "mount")}
    m.update({k: v[k] for k in m if k in v})
    return m


def _spec(res):
    """Приводит результат строителя к словарю {main, aux}."""
    if isinstance(res, dict):
        return res
    front, side, fext, sext = res[:4]
    side_title = res[4] if len(res) > 4 else "Вид сбоку"
    side_floor = res[5] if len(res) > 5 else True
    return {"main": dict(title="Вид спереди", ext=fext, floor=True, draw=front),
            "aux": dict(title=side_title, ext=sext, floor=side_floor, draw=side)}


def build(path, builders, two_color=()):
    e = yaml.safe_load(path.read_text(encoding="utf-8"))
    fn = builders.get(e["id"])
    if not fn:
        return 0
    n = 0
    for va in e["variants"]:
        m = merged(e, va)
        cols = hex_colors(m["color"]) or ["#BDBDBD"]
        args = [e, va, va["dimensions_mm"], va["aperture_mm"], cols[0]]
        if e["id"] in two_color:
            args.extend(cols[1:])
        sp = _spec(fn(*args))
        mn, ax = sp["main"], sp["aux"]
        fext, sext = mn["ext"], ax["ext"]
        if mn["floor"] and ax["floor"]:   # общая высота, чтобы пол на видах совпадал
            ymin, ymax = min(fext[2], sext[2]), max(fext[3], sext[3])
            fext = (fext[0], fext[1], ymin, ymax)
            sext = (sext[0], sext[1], ymin, ymax)
        k = min((FRONT_BOX[2] - 2 * PAD) / (fext[1] - fext[0]),
                (SIDE_BOX[2] - 2 * SIDE_PAD_X) / max(sext[1] - sext[0], 1),
                (FRONT_BOX[3] - 2 * PAD) / (fext[3] - fext[2]),
                (SIDE_BOX[3] - 2 * PAD) / (sext[3] - sext[2]))
        fv = View(FRONT_BOX, fext, k, floor=mn["floor"])
        sv = View(SIDE_BOX, sext, k, floor=ax["floor"])
        fv.draw_floor()
        sv.draw_floor()
        mn["draw"](fv)
        ax["draw"](sv)

        foot = (f"Материал: {m['material']}  ·  Жёсткость: {m['rigidity']}  ·  "
                f"Крепление: {m['mount']}  ·  Сложность: {m['difficulty']}/5")
        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
            STYLE,
            f'<rect width="{W}" height="{H}" fill="#fff"/>',
            f'<rect x="10" y="10" width="{W - 20}" height="{H - 20}" fill="none" stroke="#333" stroke-width="1.5"/>',
            f'<text x="30" y="46" font-size="22" font-weight="bold" fill="#222">{escape(va["id"])} · '
            f'{escape(e["name_ru"])}</text>',
            f'<text x="30" y="72" font-size="14" fill="#555">Вариант: {escape(va["label"])}  ·  '
            f'{escape(e["name_en"])}  ·  размеры в мм  ·  1 px ≈ {1 / k:.1f} мм</text>',
            f'<line x1="{SIDE_BOX[0] - 10}" y1="90" x2="{SIDE_BOX[0] - 10}" y2="{H - 50}" stroke="#ddd"/>',
            f'<text x="{FRONT_BOX[0] + 10}" y="{FRONT_BOX[1] + 4}" font-size="13" fill="#888">{mn["title"]}</text>',
            f'<text x="{SIDE_BOX[0] + 10}" y="{SIDE_BOX[1] + 4}" font-size="13" fill="#888">{ax["title"]}</text>',
            *fv.out, *sv.out,
            f'<line x1="10" y1="{H - 42}" x2="{W - 10}" y2="{H - 42}" stroke="#333"/>',
            f'<text x="30" y="{H - 20}" font-size="12" fill="#444">{escape(foot)}</text>',
            '</svg>',
        ]
        out = path.parent / va["drawing"]
        out.parent.mkdir(exist_ok=True)
        out.write_text("\n".join(svg), encoding="utf-8")
        n += 1
    return n


def run(category_dir, builders, two_color=()):
    """Точка входа для скриптов категорий: python tools/draw_X.py [ID ...]"""
    want = set(sys.argv[1:])
    total = 0
    for f in sorted((ROOT / "obstacles" / category_dir).glob("*/element.yaml")):
        eid = f.parent.name.split("-")[0]
        if want and eid not in want:
            continue
        total += build(f, builders, two_color)
    print(f"drawings: {total}")
