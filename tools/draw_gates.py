"""Генерирует SVG-чертежи для категории 01-gates из element.yaml.

Запуск:  python tools/draw_gates.py          — все ворота
         python tools/draw_gates.py G01 G05  — выбранные элементы

Каждый чертёж: вид спереди + вид сбоку (у G10 — вид сверху), размеры в мм.
Направление пролёта — слева направо на виде сбоку (ось Z).
"""
import math
import re
import sys
from html import escape
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
GATES = ROOT / "obstacles" / "01-gates"

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


# ---------------------------------------------------------------- элементы
# Каждая функция возвращает (front(v), side(v), fext, sext, side_title, side_floor)

def g_ring(e, va, d, a, col):          # G01
    D, b = d["diameter"], d["band"]
    Hh = d["height"]
    cy = 20 + D / 2
    def front(v):
        v.rect(-80, 0, 160, 25, fill="#9e9e9e")
        v.holed(("circle", 0, cy, D / 2), [("circle", 0, cy, D / 2 - b)], col)
        v.hdim(-D / 2, D / 2, Hh, 22, f"Ø{D}")
        v.idim(-(D / 2 - b), cy, D / 2 - b, cy, f"Ø{a['diameter']}")
        v.vdim(0, a["bottom"], -D / 2, -28, a["bottom"])
        v.vdim(0, Hh, D / 2, 28, Hh)
    def side(v):
        thin_side(v, 20, D, col, base=(100, 25))
        v.hdim(-50, 50, 0, -30, 100)
        v.vdim(0, Hh, 50, 28, Hh)
        v.flight(cy)
    return front, side, (-D / 2, D / 2, 0, Hh), (-50, 50, 0, Hh)


def g_hoop(e, va, d, a, col):          # G02
    D, t = d["diameter"], d["tube"]
    def front(v):
        v.rect(-100, 0, 200, 40, fill="#9e9e9e")
        v.holed(("circle", 0, D / 2, D / 2), [("circle", 0, D / 2, D / 2 - t)], col)
        v.hdim(-D / 2, D / 2, D, 22, f"Ø{D}")
        v.idim(-(D / 2 - t), D / 2, D / 2 - t, D / 2, f"Ø{a['diameter']}")
        v.vdim(0, D, D / 2, 28, D)
    def side(v):
        thin_side(v, 0, D, col, t=t, base=(120, 40))
        v.hdim(-60, 60, 0, -30, 120)
        v.hdim(-t / 2, t / 2, D, 22, f"трубка {t}")
        v.flight(D / 2)
    return front, side, (-D / 2, D / 2, 0, D), (-60, 60, 0, D)


def g_rect(e, va, d, a, col):          # G03, G04
    w, h, b = d["width"], d["height"], d["band"]
    iw, ih = a["width"], a["height"]
    def front(v):
        v.holed(rect_pts(-w / 2, 0, w, h), [rect_pts(-iw / 2, b, iw, ih)], col)
        v.hdim(-w / 2, w / 2, h, 22, w)
        v.vdim(0, h, w / 2, 28, h)
        v.idim(-iw / 2, b + ih * 0.35, iw / 2, b + ih * 0.35, iw)
        v.idim(-iw * 0.2, b, -iw * 0.2, b + ih, ih)
        v.vdim(0, b, -w / 2, -28, b)
    def side(v):
        thin_side(v, 0, h, col, feet=d["depth"])
        v.hdim(-d["depth"] / 2, d["depth"] / 2, 0, -30, d["depth"])
        v.vdim(0, h, d["depth"] / 2, 28, h)
        v.flight(b + ih / 2)
    return front, side, (-w / 2, w / 2, 0, h), (-d["depth"] / 2, d["depth"] / 2, 0, h)


def g_triangle(e, va, d, a, col):      # G05
    s, b = d["side"], d["band"]
    si = a["inner_side"]
    hh = s * S3 / 2
    hi = si * S3 / 2
    outer = [(-s / 2, 0), (s / 2, 0), (0, hh)]
    inner = [(-si / 2, b), (si / 2, b), (0, b + hi)]
    def front(v):
        v.holed(outer, [inner], col)
        v.hdim(-s / 2, s / 2, 0, -30, s)
        v.vdim(0, hh, s / 2, 28, round(hh))
        v.idim(-si / 2, b + 12, si / 2, b + 12, si)
        r = si / (2 * S3)
        v.raw(f'<circle cx="{v.X(0):.1f}" cy="{v.Y(b + r):.1f}" r="{r * v.k:.1f}" class="incircle"/>')
        v.text(0, b + r, f"Ø{a['incircle_diameter']} впис.", size=11, fill="#0057B8")
        v.vdim(0, b, -s / 2, -28, b)
    def side(v):
        thin_side(v, 0, hh, col, feet=d["depth"])
        v.hdim(-d["depth"] / 2, d["depth"] / 2, 0, -30, d["depth"])
        v.flight(b + hi / 3)
    return front, side, (-s / 2, s / 2, 0, hh), (-d["depth"] / 2, d["depth"] / 2, 0, hh)


def g_polygon(e, va, d, a, col):       # G06
    n = 6 if a["shape"] == "hexagon" else 8
    F, b = d["across_flats"], d["band"]
    Fi = a["across_flats"]
    phase = 0 if n == 6 else 22.5
    outer = reg_poly(n, F / 2, F, phase)
    inner = reg_poly(n, F / 2, Fi, phase)
    w = d["width"]
    def front(v):
        v.holed(outer, [inner], col, sw=1.4)
        v.hdim(-w / 2, w / 2, F, 22, w)
        v.vdim(0, F, w / 2, 28, F)
        v.idim(-Fi * 0.25, b, -Fi * 0.25, F - b, Fi)
        ac = a["across_corners"]
        if n == 6:
            v.idim(-ac / 2, F / 2, ac / 2, F / 2, ac, side=-1)
        v.vdim(0, b, -w / 2, -28, b)
    def side(v):
        thin_side(v, 0, F, col, t=15, feet=d["depth"])
        v.hdim(-d["depth"] / 2, d["depth"] / 2, 0, -30, d["depth"])
        v.hdim(-7.5, 7.5, F, 22, 15)
        v.flight(F / 2)
    return front, side, (-w / 2, w / 2, 0, F), (-d["depth"] / 2, d["depth"] / 2, 0, F)


def g_arch(e, va, d, a, col):          # G07
    t, R, leg = d["tube"], d["span_axis"] / 2, 330
    Hh = d["height"]
    def front(v):
        for x0 in (-R, R):
            v.rect(x0 - 75, 0, 150, 10, fill="#9e9e9e")
        dpath = (f"M{v.P(-R, 10)} L{v.P(-R, leg)} "
                 f"A{R * v.k:.1f},{R * v.k:.1f} 0 0,1 {v.P(R, leg)} L{v.P(R, 10)}")
        v.raw(f'<path d="{dpath}" fill="none" stroke="{INK}" stroke-width="{t * v.k + 2.4:.1f}"/>')
        v.raw(f'<path d="{dpath}" fill="none" stroke="{col}" stroke-width="{t * v.k:.1f}"/>')
        v.hdim(-d["width"] / 2, d["width"] / 2, Hh, 22, d["width"])
        v.vdim(0, Hh, d["width"] / 2, 28, Hh)
        v.idim(-a["width"] / 2, 180, a["width"] / 2, 180, a["width"])
        v.idim(0, 0, 0, a["height"], a["height"])
        v.hdim(-R, R, 0, -30, f"{2 * R:.0f} по осям")
    def side(v):
        v.rect(-75, 0, 150, 10, fill="#9e9e9e")
        v.rect(-t / 2, 10, t, Hh - 10, fill=col)
        v.hdim(-75, 75, 0, -30, 150)
        v.hdim(-t / 2, t / 2, Hh, 22, f"Ø{t}")
        v.flight(Hh / 2)
    return front, side, (-d["width"] / 2, d["width"] / 2, 0, Hh), (-75, 75, 0, Hh)


def g_tilted(e, va, d, a, col):        # G08
    th = d["tilt_deg"]
    c, s = math.cos(math.radians(th)), math.sin(math.radians(th))
    Hh, dep = d["height"], d["depth"]
    eff = a["effective_height"]
    def front(v):
        v.holed(rect_pts(-250, 0, 500, Hh), [rect_pts(-200, a["bottom"], 400, eff)], col)
        v.hdim(-250, 250, Hh, 22, 500)
        v.vdim(0, Hh, 250, 28, Hh)
        v.idim(-80, a["bottom"], -80, a["bottom"] + eff, f"{eff} видимый")
        v.idim(-200, a["bottom"] + eff * 0.6, 200, a["bottom"] + eff * 0.6, 400)
    def side(v):
        v.rect(0, 0, 300, 15, fill="#9e9e9e")
        v.line(300, 15, 250 * s, 250 * c, stroke="#777", sw=3)
        v.raw(f'<line x1="{v.X(0):.1f}" y1="{v.Y(0):.1f}" x2="{v.X(500 * s):.1f}" y2="{v.Y(500 * c):.1f}" '
              f'stroke="{INK}" stroke-width="{max(8 * v.k, 3) + 2:.1f}"/>')
        v.raw(f'<line x1="{v.X(0):.1f}" y1="{v.Y(0):.1f}" x2="{v.X(500 * s):.1f}" y2="{v.Y(500 * c):.1f}" '
              f'stroke="{col}" stroke-width="{max(8 * v.k, 3):.1f}"/>')
        r = 160
        v.line(0, 0, 0, r + 40, stroke=DIM, sw=0.8, extra='stroke-dasharray="4 3"')
        v.raw(f'<path d="M{v.P(0, r)} A{r * v.k:.1f},{r * v.k:.1f} 0 0,1 {v.P(r * s, r * c)}" '
              f'fill="none" class="dim"/>')
        v.text(r * 0.55 * s + 20, r * 1.05, f"{th}°", size=13, fill=DIM)
        v.hdim(0, dep, 0, -30, dep)
        v.vdim(0, Hh, max(dep, 500 * s), 28, Hh)
        v.flight(Hh / 2)
    return front, side, (-250, 250, 0, Hh), (0, max(dep, 500 * s), 0, Hh)


def g_stand(e, va, d, a, col):         # G09
    low, Hh = d["lower_edge"], d["height"]
    px = -260
    def front(v):
        v.rect(px - 200, 0, 400, 20, fill="#555")
        v.rect(px - 10, 0, 20, Hh, fill="#333")
        v.holed(rect_pts(-250, low, 500, 500), [rect_pts(-200, low + 50, 400, 400)], col)
        v.hdim(-250, 250, Hh, 22, 500)
        v.vdim(0, Hh, 250, 28, Hh)
        v.vdim(0, low, 250, 62, low)
        v.idim(-200, low + 250, 200, low + 250, 400)
        v.vdim(0, a["bottom"], px - 200, -28, a["bottom"])
    def side(v):
        v.rect(-200, 0, 400, 20, fill="#555")
        v.rect(-10, 0, 20, Hh, fill="#333")
        v.rect(10, low, 8, 500, fill=col)
        v.hdim(-200, 200, 0, -30, 400)
        v.flight(low + 250)
    return front, side, (px - 200, 250, 0, Hh), (-200, 200, 0, Hh)


def g_dive(e, va, d, a, col):          # G10
    D, b, Hh = d["diameter"], d["band"], d["height"]
    legs = [90, 210, 330]
    def front(v):
        for ph in legs:
            x = (D / 2) * math.cos(math.radians(ph))
            v.rect(x - 8, 0, 16, Hh - 8, fill="#9e9e9e")
        v.rect(-D / 2, Hh - 8, b, 8, fill=col)
        v.rect(D / 2 - b, Hh - 8, b, 8, fill=col)
        v.line(-D / 2 + b, Hh - 4, D / 2 - b, Hh - 4, stroke=col, sw=2, extra='stroke-dasharray="6 4"')
        v.hdim(-D / 2, D / 2, Hh, 22, f"Ø{D}")
        v.idim(-(D / 2 - b), Hh - 40, D / 2 - b, Hh - 40, f"Ø{a['diameter']}", side=-1)
        v.vdim(0, Hh, D / 2, 28, Hh)
        v.flight(0, "down")
    def top(v):
        v.holed(("circle", 0, 0, D / 2), [("circle", 0, 0, D / 2 - b)], col)
        for ph in legs:
            x, z = (D / 2) * math.cos(math.radians(ph)), (D / 2) * math.sin(math.radians(ph))
            v.raw(f'<circle cx="{v.X(x):.1f}" cy="{v.Y(z):.1f}" r="{max(8 * v.k, 3):.1f}" fill="#9e9e9e" stroke="{INK}"/>')
        v.hdim(-D / 2, D / 2, D / 2, 22, f"Ø{D}")
        v.idim(-(D / 2 - b), 0, D / 2 - b, 0, f"Ø{a['diameter']}")
        v.text(0, -D / 2 - 60, "ножки через 120°", size=11, fill=DIM)
    return front, top, (-D / 2, D / 2, 0, Hh), (-D / 2, D / 2, -D / 2, D / 2), "Вид сверху", False


def g_hanging(e, va, d, a, col):       # G11
    D, b, low = d["diameter"], d["band"], d["lower_edge"]
    ceil = 2500
    cy = low + D / 2
    ax, ay = (D / 2) * math.sin(math.radians(60)), cy + (D / 2) * math.cos(math.radians(60))
    def front(v):
        v.ceiling(ceil)
        for sx in (-1, 1):
            v.line(sx * ax, ay, sx * ax, ceil, stroke="#777", sw=1)
        v.holed(("circle", 0, cy, D / 2), [("circle", 0, cy, D / 2 - b)], col)
        v.hdim(-D / 2, D / 2, low, -26, f"Ø{D}")
        v.idim(-(D / 2 - b), cy, D / 2 - b, cy, f"Ø{a['diameter']}")
        v.vdim(0, low, -D / 2, -28, low)
        v.vdim(0, ceil, D / 2, 40, f"{ceil} потолок (по умолч.)")
    def side(v):
        v.ceiling(ceil)
        v.line(0, ay, 0, ceil, stroke="#777", sw=1)
        thin_side(v, low, D, col)
        v.flight(cy)
    return front, side, (-D / 2, D / 2, 0, ceil), (-60, 60, 0, ceil)


def g_eight(e, va, d, a, col, col2):   # G12
    R, b = d["ring_diameter"] / 2, d["band"]
    cy = 20 + R
    def front(v):
        v.rect(-200, 0, 400, 20, fill="#9e9e9e")
        v.holed(("circle", -R, cy, R), [("circle", -R, cy, R - b)], col)
        v.holed(("circle", R, cy, R), [("circle", R, cy, R - b)], col2)
        v.hdim(-2 * R, 2 * R, 20 + 2 * R, 22, d["width"])
        v.idim(-2 * R + b, cy, -b, cy, f"Ø{a['diameter']}")
        v.vdim(0, d["height"], 2 * R, 28, d["height"])
        v.vdim(0, a["bottom"], -2 * R, -28, a["bottom"])
    def side(v):
        thin_side(v, 20, 2 * R, col, base=(100, 20))
        v.hdim(-50, 50, 0, -30, 100)
        v.flight(cy)
    return front, side, (-2 * R, 2 * R, 0, d["height"]), (-50, 50, 0, d["height"])


def g_grid(e, va, d, a, col):          # G13
    t, cell = d["tube"], a["cell_width"]
    n = int(round(math.sqrt(d["cells"])))
    Wd = d["width"]
    y0 = 150
    def front(v):
        v.rect(-Wd / 2, 0, t, y0, fill=col)
        v.rect(Wd / 2 - t, 0, t, y0, fill=col)
        holes = []
        for i in range(n):
            for j in range(n):
                x = -Wd / 2 + t + i * (cell + t)
                y = y0 + t + j * (cell + t)
                holes.append(rect_pts(x, y, cell, cell))
        v.holed(rect_pts(-Wd / 2, y0, Wd, Wd), holes, col, sw=1.4)
        num = 1
        for row in range(n):
            for i in range(n):
                x = -Wd / 2 + t + i * (cell + t) + cell / 2
                y = y0 + t + (n - 1 - row) * (cell + t) + cell / 2
                v.text(x, y - 15, num, size=max(14, int(cell * v.k * 0.35)), fill="#bbb",
                       extra='font-weight="bold"')
                num += 1
        v.hdim(-Wd / 2, Wd / 2, y0 + Wd, 22, Wd)
        v.vdim(0, d["height"], Wd / 2, 28, d["height"])
        x0 = -Wd / 2 + t
        v.idim(x0, y0 + t + cell * 0.2, x0 + cell, y0 + t + cell * 0.2, cell)
        v.vdim(0, a["bottom"], -Wd / 2, -28, a["bottom"])
    def side(v):
        v.rect(-125, 0, 250, 20, fill="#bdbdbd")
        v.rect(-t / 2, 0, t, d["height"], fill=col)
        v.hdim(-125, 125, 0, -30, 250)
        v.flight(y0 + Wd / 2)
    return front, side, (-Wd / 2, Wd / 2, 0, d["height"]), (-125, 125, 0, d["height"])


def g_keyhole(e, va, d, a, col, col2):  # G14
    Wd, Hh = d["width"], d["height"]
    r, cyc = a["circle_diameter"] / 2, a["circle_center_y"]
    sw_, sb = a["slot_width"] / 2, a["slot_bottom"]
    yi = cyc - math.sqrt(r * r - sw_ * sw_)
    def front(v):
        hole = (f"M{v.P(-sw_, sb)} L{v.P(sw_, sb)} L{v.P(sw_, yi)} "
                f"A{r * v.k:.1f},{r * v.k:.1f} 0 1,0 {v.P(-sw_, yi)} Z")
        outer = "M" + " L".join(v.P(*p) for p in rect_pts(-Wd / 2, 0, Wd, Hh)) + " Z"
        v.raw(f'<path d="{outer} {hole}" fill="{col}" fill-rule="evenodd" stroke="{INK}" stroke-width="1.2"/>')
        v.raw(f'<path d="{hole}" fill="none" stroke="{col2}" stroke-width="4"/>')
        v.hdim(-Wd / 2, Wd / 2, Hh, 22, Wd)
        v.vdim(0, Hh, Wd / 2, 28, Hh)
        v.idim(-r, cyc, r, cyc, f"Ø{a['circle_diameter']}")
        v.idim(-sw_, sb + 60, sw_, sb + 60, a["slot_width"])
        v.vdim(0, sb, -Wd / 2, -28, sb)
        v.vdim(0, cyc, -Wd / 2, -58, f"{cyc} центр круга")
    def side(v):
        v.poly([(2.5, 0), (252.5, 0), (2.5, 350)], fill="#cfd8dc")
        v.rect(-2.5, 0, 5, Hh, fill=col)
        v.hdim(-2.5, 252.5, 0, -30, d["depth"])
        v.vdim(0, Hh, 252.5, 28, Hh)
        v.flight(cyc)
    return front, side, (-Wd / 2, Wd / 2, 0, Hh), (-2.5, 252.5, 0, Hh)


def g_led(e, va, d, a, col):           # G15
    S, t, low = d["width"], d["tube"], d["lower_edge"]
    top = low + S
    hang = top + 30 + 180
    glow = f'filter="url(#glow)"'
    def frame(v, sw=1.2):
        if a["shape"] == "circle":
            v.holed(("circle", 0, low + S / 2, S / 2), [("circle", 0, low + S / 2, S / 2 - t)], col, sw=sw)
        else:
            v.holed(rect_pts(-S / 2, low, S, S), [rect_pts(-S / 2 + t, low + t, S - 2 * t, S - 2 * t)], col, sw=sw)
    def front(v):
        v.line(0, top + 30, 0, hang, stroke="#777", sw=1)
        v.text(8, hang - 30, "подвес", size=11, anchor="start", fill=DIM)
        v.out.append(f'<g {glow} opacity="0.7">')
        frame(v, sw=0)
        v.out.append('</g>')
        frame(v)
        v.rect(-30, top, 60, 30, fill="#333")
        v.hdim(-S / 2, S / 2, low, -26, S if a["shape"] != "circle" else f"Ø{S}")
        inner = S - 2 * t
        v.idim(-inner / 2, low + S / 2, inner / 2, low + S / 2,
               inner if a["shape"] != "circle" else f"Ø{inner}")
        v.vdim(0, low, -S / 2, -28, low)
        v.vdim(low, top, S / 2, 28, S)
    def side(v):
        v.line(0, top + 30, 0, hang, stroke="#777", sw=1)
        v.rect(-10, top, 20, 30, fill="#333")
        v.rect(-t / 2, low, t, S, fill=col, extra=glow)
        v.rect(-t / 2, low, t, S, fill=col)
        v.hdim(-t / 2, t / 2, low, -26, t)
        v.flight(low + S / 2)
    return front, side, (-S / 2, S / 2, 0, hang), (-60, 60, 0, hang)


def g_banner(e, va, d, a, col, col2):  # G16
    Wd, Hh = d["width"], d["height"]
    iw, ih, ib = a["width"], a["height"], a["bottom"]
    def front(v):
        v.holed(rect_pts(-Wd / 2, 0, Wd, Hh), [rect_pts(-iw / 2, ib, iw, ih)], col, sw=2.5)
        v.text(0, ib + ih + (Hh - ib - ih) / 2 - 14, "07", size=max(14, int((Hh - ib - ih) * v.k * 0.7)),
               fill=col2, extra='font-weight="bold"')
        v.hdim(-Wd / 2, Wd / 2, Hh, 22, Wd)
        v.vdim(0, Hh, Wd / 2, 28, Hh)
        v.vdim(ib + ih, Hh, Wd / 2, 62, Hh - ib - ih)
        v.idim(-iw / 2, ib + ih * 0.4, iw / 2, ib + ih * 0.4, iw)
        v.idim(-iw * 0.25, ib, -iw * 0.25, ib + ih, ih)
        v.vdim(0, ib, -Wd / 2, -28, ib)
    def side(v):
        v.rect(-150, 0, 300, 10, fill="#333")
        v.rect(-4, 0, 8, Hh, fill="#333")
        v.hdim(-150, 150, 0, -30, 300)
        v.flight(ib + ih / 2)
    return front, side, (-Wd / 2, Wd / 2, 0, Hh), (-150, 150, 0, Hh)


def g_posts(e, va, d, a, col):         # G17
    sp, Hh, p = d["spacing"], d["height"], d["pole"]
    fw, fh = 200, 150
    def flag(v, x0, sgn):
        cols, rows = 4, 3
        cw, ch = fw / cols, fh / rows
        for i in range(cols):
            for j in range(rows):
                fill = "#E53935" if (i + j) % 2 == 0 else "#FFFFFF"
                x = x0 + sgn * i * cw - (cw if sgn < 0 else 0)
                v.rect(x, Hh - fh + j * ch, cw, ch, fill=fill, sw=0.6)
    def front(v):
        for sx in (-1, 1):
            x = sx * sp / 2
            v.rect(x - 75, 0, 150, 20, fill="#424242")
            v.rect(x - p / 2, 20, p, Hh - 20, fill=col)
            flag(v, x + sx * p / 2, sx)
        v.hdim(-sp / 2, sp / 2, 0, -30, f"{sp} по осям")
        v.idim(-sp / 2 + p / 2, Hh * 0.45, sp / 2 - p / 2, Hh * 0.45, a["width"])
        v.vdim(0, Hh, sp / 2 + p / 2 + fw, 28, Hh)
        v.hdim(sp / 2 + p / 2, sp / 2 + p / 2 + fw, Hh, 22, fw)
    def side(v):
        v.rect(-75, 0, 150, 20, fill="#424242")
        v.rect(-p / 2, 20, p, Hh - 20, fill=col)
        v.rect(-1.5, Hh - fh, 3, fh, fill="#E53935")
        v.hdim(-75, 75, 0, -30, 150)
        v.flight(Hh * 0.45)
    half = sp / 2 + p / 2 + fw
    return front, side, (-half, half, 0, Hh), (-75, 75, 0, Hh)


BUILDERS = {
    "G01": g_ring, "G02": g_hoop, "G03": g_rect, "G04": g_rect, "G05": g_triangle,
    "G06": g_polygon, "G07": g_arch, "G08": g_tilted, "G09": g_stand, "G10": g_dive,
    "G11": g_hanging, "G12": g_eight, "G13": g_grid, "G14": g_keyhole, "G15": g_led,
    "G16": g_banner, "G17": g_posts,
}
TWO_COLOR = {"G12", "G14", "G16"}


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
  <filter id="glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="6"/></filter>
</defs>
"""


def merged(e, v):
    m = {k: e.get(k) for k in ("color", "material", "rigidity", "difficulty", "mount")}
    m.update({k: v[k] for k in m if k in v})
    return m


def build(path):
    e = yaml.safe_load(path.read_text(encoding="utf-8"))
    fn = BUILDERS.get(e["id"])
    if not fn:
        return 0
    n = 0
    for va in e["variants"]:
        m = merged(e, va)
        cols = hex_colors(m["color"]) or ["#BDBDBD"]
        args = [e, va, va["dimensions_mm"], va["aperture_mm"], cols[0]]
        if e["id"] in TWO_COLOR:
            args.append(cols[1] if len(cols) > 1 else INK)
        res = fn(*args)
        front, side, fext, sext = res[:4]
        side_title = res[4] if len(res) > 4 else "Вид сбоку"
        side_floor = res[5] if len(res) > 5 else True
        if side_floor:  # общая высота, чтобы пол на видах совпадал
            ymin, ymax = min(fext[2], sext[2]), max(fext[3], sext[3])
            fext = (fext[0], fext[1], ymin, ymax)
            sext = (sext[0], sext[1], ymin, ymax)
        k = min((FRONT_BOX[2] - 2 * PAD) / (fext[1] - fext[0]),
                (SIDE_BOX[2] - 2 * SIDE_PAD_X) / max(sext[1] - sext[0], 1),
                (FRONT_BOX[3] - 2 * PAD) / (fext[3] - fext[2]),
                (SIDE_BOX[3] - 2 * PAD) / (sext[3] - sext[2]))
        fv = View(FRONT_BOX, fext, k)
        sv = View(SIDE_BOX, sext, k, floor=side_floor)
        fv.draw_floor()
        sv.draw_floor()
        front(fv)
        side(sv)

        mm_per_px = 1 / k
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
            f'{escape(e["name_en"])}  ·  размеры в мм  ·  1 px ≈ {mm_per_px:.1f} мм</text>',
            f'<line x1="{SIDE_BOX[0] - 10}" y1="90" x2="{SIDE_BOX[0] - 10}" y2="{H - 50}" stroke="#ddd"/>',
            f'<text x="{FRONT_BOX[0] + 10}" y="{FRONT_BOX[1] + 4}" font-size="13" fill="#888">Вид спереди</text>',
            f'<text x="{SIDE_BOX[0] + 10}" y="{SIDE_BOX[1] + 4}" font-size="13" fill="#888">{side_title}</text>',
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


def main():
    want = set(sys.argv[1:])
    total = 0
    for f in sorted(GATES.glob("*/element.yaml")):
        eid = f.parent.name.split("-")[0]
        if want and eid not in want:
            continue
        total += build(f)
    print(f"drawings: {total}")


if __name__ == "__main__":
    main()
