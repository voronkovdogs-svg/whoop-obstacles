"""SVG-чертежи категории 05-combos (составные гоночные элементы).

Запуск:  python tools/draw_combos.py          — все элементы
         python tools/draw_combos.py C01 C05  — выбранные

На одном из видов пунктиром показана траектория манёвра.
"""
import math

from drawlib import DIM, INK, rect_pts, run

PATH = "#2E7D32"
HALO = 'paint-order="stroke" stroke="#fff" stroke-width="3"'


def spec(main_title, main_ext, main_draw, aux_title, aux_ext, aux_draw, main_floor=True, aux_floor=True,
         independent=True):
    return {"main": dict(title=main_title, ext=main_ext, floor=main_floor, draw=main_draw),
            "aux": dict(title=aux_title, ext=aux_ext, floor=aux_floor, draw=aux_draw), "independent": independent}


def sq(v, cx, bottom, outer, band, col, sw=1.2):
    v.holed(rect_pts(cx - outer / 2, bottom, outer, outer),
            [rect_pts(cx - outer / 2 + band, bottom + band, outer - 2 * band, outer - 2 * band)], col, sw=sw)


def ring(v, cx, cy, outer, band, col, sx=1.0):
    """Кольцо, видимое под углом: sx — сжатие по горизонтали (1 — анфас, 0 — ребром)."""
    R, r = outer / 2, outer / 2 - band
    k = v.k
    X, Y = v.X(cx), v.Y(cy)
    rx1, rx2 = max(R * k * sx, 1.5), max(r * k * sx, 0.1)
    d = (f"M{X - rx1:.1f},{Y:.1f} a{rx1:.1f},{R * k:.1f} 0 1,0 {2 * rx1:.1f},0 a{rx1:.1f},{R * k:.1f} 0 1,0 {-2 * rx1:.1f},0 Z "
         f"M{X - rx2:.1f},{Y:.1f} a{rx2:.1f},{r * k:.1f} 0 1,0 {2 * rx2:.1f},0 a{rx2:.1f},{r * k:.1f} 0 1,0 {-2 * rx2:.1f},0 Z")
    v.raw(f'<path d="{d}" fill="{col}" fill-rule="evenodd" stroke="{INK}" stroke-width="1.2"/>')


def route(v, d):
    v.raw(f'<path d="{d}" fill="none" stroke="{PATH}" stroke-width="1.8" stroke-dasharray="7 5" '
          f'stroke-linejoin="round" marker-end="url(#fa)"/>')


def edge(v, u, w1, w2, col, t=10):
    """Ворота ребром на виде сверху: линия поперёк направления u."""
    v.rect(u - t / 2, w1, t, w2 - w1, fill=col)


def circle(v, x, y, r, fill, stroke=INK, sw=1.2):
    v.raw(f'<circle cx="{v.X(x):.1f}" cy="{v.Y(y):.1f}" r="{max(r * v.k, 2):.1f}" fill="{fill}" '
          f'stroke="{stroke}" stroke-width="{sw}"/>')


def posts_front(v, xs, H, col="#212121", foot=60):
    for x in xs:
        v.rect(x - foot / 2, 0, foot, 15, fill="#616161")
        v.rect(x - 12.5, 15, 25, H - 15, fill=col)


# ---------------------------------------------------------------- элементы
def c_split_s(e, va, d, a, col, col2="#1E88E5", post="#212121", *_):   # C01
    H, g, b = d["height"], d["gate"], d["band"]
    lows = [int(x) for x in d["lower_edges"].split(",")]
    px = g / 2 + 15
    cu, cl = lows[1] + g / 2, lows[0] + g / 2

    def front(v):
        posts_front(v, (-px, px), H, post)
        sq(v, 0, lows[0], g, b, col2)
        sq(v, 0, lows[1], g, b, col)
        v.hdim(-px - 12.5, px + 12.5, H, 22, d["width"])
        v.vdim(0, H, px + 12.5, 28, H)
        v.vdim(0, lows[0], -px - 12.5, -28, lows[0])
        v.vdim(0, lows[1], -px - 12.5, -62, lows[1])
        v.idim(-200, cu, 200, cu, 400)

    def side(v):
        v.rect(-150, 0, 300, 15, fill="#616161")
        v.rect(-12.5, 15, 25, H - 15, fill=post)
        v.rect(14, lows[0], 10, g, fill=col2)
        v.rect(14, lows[1], 10, g, fill=col)
        R = (cu - cl) / 2
        k = v.k
        route(v, f"M{v.P(-700, cu)} L{v.P(350, cu)} A{R * k:.1f},{R * k:.1f} 0 0,1 {v.P(350, cl)} L{v.P(-700, cl)}")
        v.text(-450, cu + 60, "вход", size=11, fill=PATH)
        v.text(-450, cl + 60, "выход", size=11, fill=PATH)
        v.hdim(-150, 150, 0, -30, 300)

    return spec("Вид спереди", (-px - 12.5, px + 12.5, 0, H), front, "Вид сбоку: манёвр",
                (-700, 350 + (cu - cl) / 2, 0, H), side)


def c_hairpin(e, va, d, a, colA, colB="#1E88E5", colP="#EC407A", *_):  # C02 — вид сверху: u вперёд, w влево
    sp, pd = d["gate_spacing"], d["pylon_distance"]
    R = sp / 2

    def top(v):
        for w, c in ((R, colA), (-R, colB)):
            v.rect(-100, w - 250, 200, 15, fill="#9e9e9e", sw=0.6)
            v.rect(-100, w + 235, 200, 15, fill="#9e9e9e", sw=0.6)
            edge(v, 0, w - 250, w + 250, c)
        circle(v, pd, 0, 100, "#616161")
        circle(v, pd, 0, 32.5, colP)
        k = v.k
        route(v, f"M{v.P(-700, R)} L{v.P(pd, R)} A{R * k:.1f},{R * k:.1f} 0 0,1 {v.P(pd, -R)} L{v.P(-700, -R)}")
        v.hdim(0, pd, -R - 250, -30, f"{pd} до шеста")
        v.vdim(-R, R, 0, -140, f"{sp} между центрами")
        v.text(-450, R + 60, "вход", size=11, fill=PATH)
        v.text(-450, -R + 60, "выход", size=11, fill=PATH)

    def front(v):
        v.rect(-100, 0, 200, 20, fill="#616161")
        v.rect(-32.5, 20, 65, 1600, fill=colP, extra='fill-opacity="0.6"')
        sq(v, -R, 0, 500, 50, colA)
        sq(v, R, 0, 500, 50, colB)
        v.hdim(-R - 250, R + 250, 500, 22, d["width"])
        v.vdim(0, 1620, R + 250, 28, "1620 шест")
        v.text(0, 1700, "шест за воротами", size=11, fill=DIM)

    return spec("Вид сверху: траектория", (-700, pd + R, -R - 250, R + 250), top, "Вид спереди",
                (-R - 250, R + 250, 0, 1620), front, main_floor=False)


def c_chicane(e, va, d, a, c1, c2="#FFC400", c3="#1E63D6", *_):  # C03
    st, off = d["step"], d["offset"] / 2
    us, ws, cs = [0, st, 2 * st], [off, -off, off], [c1, c2, c3]

    def top(v):
        for u, w, c in zip(us, ws, cs):
            edge(v, u, w - 250, w + 250, c)
        pts = [(-600, off)] + list(zip(us, ws)) + [(2 * st + 600, off)]
        sm = smooth(pts)
        route(v, "M" + " L".join(v.P(*p) for p in sm))
        v.hdim(0, st, off + 250, 22, st)
        v.vdim(-off, off, 2 * st, 40, d["offset"])
        v.hdim(-100, 2 * st + 100, -off - 250, -30, d["depth"])

    def front(v):
        for x, c, op in ((-ws[2], c3, 0.45), (-ws[1], c2, 0.7), (-ws[0], c1, 1)):
            v.out.append(f'<g opacity="{op}">')
            sq(v, x, 0, 500, 50, c)
            v.out.append('</g>')
        v.hdim(-off - 250, off + 250, 500, 22, d["width"])
        v.vdim(0, 500, off + 250, 28, 500)
        v.text(0, 560, "1-е и 3-и на одной линии", size=11, fill=DIM)

    return spec("Вид сверху: траектория", (-600, 2 * st + 600, -off - 250, off + 250), top, "Вид спереди",
                (-off - 250, off + 250, 0, 500), front, main_floor=False)


def smooth(pts, n=12):
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(n):
            t = j / n
            out.append(tuple(0.5 * (2 * p1[c] + (-p0[c] + p2[c]) * t + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t * t
                                    + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * t ** 3) for c in (0, 1)))
    out.append(pts[-1])
    return out


def c_ladder(e, va, d, a, *cols):                       # C04
    cols = list(cols)
    post = cols[-1] if len(cols) > 3 else "#212121"
    H, g, b, n, pitch = d["height"], d["gate"], d["band"], d["levels"], d["pitch"]
    lows = [int(x) for x in d["lower_edges"].split(",")]
    px = g / 2 + 15
    centers = [lo + g / 2 for lo in lows]

    def front(v):
        posts_front(v, (-px, px), H, post)
        for lo, c in zip(lows, cols):
            sq(v, 0, lo, g, b, c)
        v.hdim(-px - 12.5, px + 12.5, H, 22, d["width"])
        v.vdim(0, H, px + 12.5, 28, H)
        v.vdim(lows[0], lows[1], -px - 12.5, -28, f"шаг {pitch}")
        v.vdim(0, lows[0], -px - 12.5, -62, lows[0])
        v.idim(-150, centers[0], 150, centers[0], 300)

    def side(v):
        v.rect(-150, 0, 300, 15, fill="#616161")
        v.rect(-12.5, 15, 25, H - 15, fill=post)
        for lo, c in zip(lows, cols):
            v.rect(14, lo, 10, g, fill=c)
        R = pitch / 2
        k = v.k
        dd = f"M{v.P(-700, centers[0])}"
        for i in range(n - 1):
            sgn = 1 if i % 2 == 0 else -1
            dd += f" L{v.P(sgn * 300, centers[i])} A{R * k:.1f},{R * k:.1f} 0 0,{0 if sgn > 0 else 1} {v.P(sgn * 300, centers[i + 1])}"
        s_last = 1 if (n - 2) % 2 == 0 else -1          # сторона последнего разворота
        dd += f" L{v.P(-s_last * 700, centers[-1])}"
        route(v, dd)
        v.hdim(-150, 150, 0, -30, 300)

    return spec("Вид спереди", (-px - 12.5, px + 12.5, 0, H), front, "Вид сбоку: подъём зигзагом",
                (-700, 700, 0, H), side)


def c_tower(e, va, d, a, c1, c2="#FDD835", c3="#E53935", pole="#9E9E9E", *_):  # C05
    H, R, g = d["height"], d["radius"], d["gate"]
    lows = [int(x) - 50 for x in a["bottoms"].split(",")]
    cols = [c1, c2, c3]

    def front(v):   # смотрим с +X: ворота 1 и 3 — анфас (z = ∓R), ворота 2 — ребром поверх стойки
        v.rect(-250, 0, 500, 20, fill="#757575")
        v.rect(-20, 20, 40, H - 20, fill=pole)
        v.rect(-20, 20, 40, H - 20, fill="url(#cylh)", stroke=INK)
        for z, lo, c in ((-R, lows[0], c1), (R, lows[2], c3)):
            x1, x2 = sorted((math.copysign(20, z), z - math.copysign(g / 2, z)))
            v.rect(x1, lo + g / 2 - 10, x2 - x1, 20, fill="#bdbdbd")
            sq(v, z, lo, g, 50, c)
        v.rect(-10, lows[1], 20, g, fill=c2)
        for z, lo, num in ((-R - g / 2 - 70, lows[0], 1), (40, lows[1], 2), (R + g / 2 + 30, lows[2], 3)):
            v.text(z, lo + g / 2, num, size=15, fill=INK, anchor="start", extra='font-weight="bold"')
        v.vdim(0, H, R + g / 2, 28, H)
        for i, lo in enumerate(lows):
            v.vdim(0, lo, -R - g / 2, -28 - 34 * i, lo)
        v.hdim(0, R, H, 22, f"R{R}")

    def top(v):     # x вправо, z вверх; облёт против часовой
        v.rect(-250, -250, 500, 500, fill="#E0E0E0", sw=0.8)
        circle(v, 0, 0, 20, pole)
        spots = [(0, -R, "x"), (R, 0, "z"), (0, R, "x")]
        for (x, z, nrm), c, num in zip(spots, cols, (1, 2, 3)):
            if nrm == "x":
                v.line(0, math.copysign(20, z), 0, z - math.copysign(g / 2, z), stroke="#9e9e9e", sw=2,
                       extra='stroke-dasharray="4 3"')
                v.rect(-6, z - g / 2, 12, g, fill=c)
                v.text(0, z + math.copysign(g / 2 + 60, z) - 20, f"{num}: низ {lows[num - 1]}", size=11,
                       fill=INK, extra=HALO)
            else:
                v.line(20, 0, x - g / 2, 0, stroke="#9e9e9e", sw=2, extra='stroke-dasharray="4 3"')
                v.rect(x - g / 2, -6, g, 12, fill=c)
                v.text(x, g / 2 + 40, f"{num}: низ {lows[num - 1]}", size=11, fill=INK, extra=HALO)
        k = v.k
        p0 = (-R * math.sin(math.radians(40)), -R * math.cos(math.radians(40)))
        route(v, f"M{v.P(p0[0] - 400, p0[1] - 200)} L{v.P(*p0)} A{R * k:.1f},{R * k:.1f} 0 1,0 "
                 f"{v.P(-R * math.cos(math.radians(30)), R * math.sin(math.radians(30)))}")
        v.text(p0[0] - 380, p0[1] - 120, "вход", size=11, anchor="start", fill=PATH)

    return spec("Вид сбоку (с +X)", (-R - g / 2, R + g / 2, 0, H), front, "Вид сверху: спираль",
                (-R - g / 2, R + g / 2, -R - g / 2 - 200, R + g / 2), top, aux_floor=False)


def c_power_loop(e, va, d, a, col, post="#FAFAFA", *_):  # C06
    h, H, bar = d["bar_axis"], d["height"], d["bar"]
    px = 520
    R = 500

    def front(v):
        posts_front(v, (-px, px), H, post)
        v.rect(-500, h - bar / 2, 1000, bar, fill=col)
        v.rect(-500, h - bar / 2, 1000, bar, fill="url(#cylv)", stroke=INK)
        v.hdim(-px - 12.5, px + 12.5, H, 22, d["width"])
        v.vdim(0, h, px + 12.5, 28, f"{h} ось")
        v.idim(0, 0, 0, a["height"], f"просвет {a['height']}")

    def side(v):
        v.rect(-150, 0, 300, 15, fill="#616161")
        v.rect(-12.5, 15, 25, H - 15, fill=post)
        circle(v, 0, h, bar / 2, col)
        k = v.k
        y0 = h - R
        route(v, f"M{v.P(-800, y0)} L{v.P(0, y0)} A{R * k:.1f},{R * k:.1f} 0 1,0 {v.P(0, h + R)} "
                 f"A{R * k:.1f},{R * k:.1f} 0 1,0 {v.P(0, y0)} L{v.P(800, y0)}")
        v.vdim(0, h + R, 800, 20, f"≈{h + R} верх петли")
        v.hdim(-150, 150, 0, -30, 300)

    return spec("Вид спереди", (-px - 12.5, px + 12.5, 0, H), front, "Вид сбоку: петля",
                (-800, 800, 0, h + R), side)


def c_spiral(e, va, d, a, *cols):                       # C07
    R, n, ring_d, b, rise = d["radius"], d["rings"], d["ring"], d["band"], d["rise"]
    lows = [100 + rise * i for i in range(n)]
    angs = [180 - 45 * i for i in range(n)]
    cols = (list(cols) + ["#BDBDBD"] * n)[:n]

    def top(v):   # x вправо, z вверх; полёт по часовой
        k = v.k
        route(v, f"M{v.P(-R, -700)} L{v.P(-R, 0)} A{R * k:.1f},{R * k:.1f} 0 0,1 {v.P(R, 0)} L{v.P(R, -700)}")
        for i, (th, c) in enumerate(zip(angs, cols)):
            t = math.radians(th)
            x, z = R * math.cos(t), R * math.sin(t)
            ux, uz = math.cos(t), math.sin(t)
            p1 = (x - ux * ring_d / 2, z - uz * ring_d / 2)
            p2 = (x + ux * ring_d / 2, z + uz * ring_d / 2)
            v.raw(f'<line x1="{v.X(p1[0]):.1f}" y1="{v.Y(p1[1]):.1f}" x2="{v.X(p2[0]):.1f}" y2="{v.Y(p2[1]):.1f}" '
                  f'stroke="{INK}" stroke-width="8"/>')
            v.raw(f'<line x1="{v.X(p1[0]):.1f}" y1="{v.Y(p1[1]):.1f}" x2="{v.X(p2[0]):.1f}" y2="{v.Y(p2[1]):.1f}" '
                  f'stroke="{c}" stroke-width="5"/>')
            v.text(x + ux * 330, z + uz * 330 - 20, f"{i + 1}: {lows[i]}", size=11, fill=INK)
        v.line(-15, 0, 15, 0, stroke=DIM, sw=0.8)
        v.line(0, -15, 0, 15, stroke=DIM, sw=0.8)
        v.idim(0, 0, R * math.cos(math.radians(110)), R * math.sin(math.radians(110)), f"R{R}")
        v.text(-R + 40, -600, "вход", size=11, anchor="start", fill=PATH)

    def front(v):  # смотрим вдоль +z
        for i in sorted(range(n), key=lambda j: -math.sin(math.radians(angs[j]))):
            t = math.radians(angs[i])
            x = R * math.cos(t)
            v.rect(x - 10, 0, 20, lows[i], fill="#9e9e9e", sw=0.6)
            v.rect(x - 100, 0, 200, 15, fill="#616161", sw=0.6)
            ring(v, x, lows[i] + ring_d / 2, ring_d, b, cols[i], sx=abs(math.cos(t)))
        for i in range(n):
            x = R * math.cos(math.radians(angs[i]))
            v.text(x, lows[i] + ring_d + 40, i + 1, size=13, fill=INK, extra='font-weight="bold"')
        v.vdim(0, lows[-1], R + ring_d / 2, 28, lows[-1])
        v.vdim(0, lows[0], -R - ring_d / 2, -28, lows[0])
        v.hdim(-R, R, 0, -30, 2 * R)

    return spec("Вид сверху: траектория", (-R - ring_d / 2, R + ring_d / 2, -700, R + ring_d / 2), top,
                "Вид спереди", (-R - ring_d / 2, R + ring_d / 2, 0, lows[-1] + ring_d + 60), front,
                main_floor=False)


def c_funnel(e, va, d, a, c1, c2="#FDD835", c3="#E53935", *_):  # C08
    st = d["step"]
    gates = [(500, 50, c1), (400, 50, c2), (300, 40, c3)]

    def side(v):
        for i, (g, b, c) in enumerate(gates):
            u = i * st
            v.rect(u - 100, 0, 200, 6, fill="#666")
            v.rect(u - 4, 0, 8, g, fill=c)
        cs = [g / 2 for g, _, _ in gates]
        route(v, "M" + " L".join(v.P(*p) for p in smooth([(-600, cs[0]), (0, cs[0]), (st, cs[1]),
                                                           (2 * st, cs[2]), (2 * st + 500, cs[2])])))
        v.hdim(0, st, 500, 22, st)
        v.hdim(-100, 2 * st + 100, 0, -30, d["depth"])
        for i, (g, b, c) in enumerate(gates):
            v.text(i * st + 40, g + 30, f"{g - 2 * b}", size=12, anchor="start", fill="#0057B8")

    def front(v):
        for g, b, c in reversed(gates):
            sq(v, 0, 0, g, b, c)
        v.hdim(-250, 250, 500, 22, 500)
        v.vdim(0, 500, 250, 28, 500)
        v.idim(-110, 40 + 110, 110, 40 + 110, 220)

    return spec("Вид сбоку: траектория", (-600, 2 * st + 500, 0, 500), side, "Вид спереди", (-250, 250, 0, 500), front)


def c_adjustable(e, va, d, a, col, rail="#212121", *_):  # C09
    H, p, L = d["height"], d["post"], d["rail"]
    w, ab, ah = a["width"], a["bottom"], a["height"]

    def frame(v, iw, fill, extra=""):
        for sx in (-1, 1):
            v.rect(sx * (iw / 2 + p / 2) - p / 2, 30, p, H - 30, fill=fill, extra=extra)
        v.rect(-iw / 2 - p, ab - 30, iw + 2 * p, 30, fill=fill, extra=extra)
        v.rect(-iw / 2 - p, ab + ah, iw + 2 * p, 30, fill=fill, extra=extra)

    def front(v):
        v.rect(-L / 2, 0, L, 30, fill=rail)
        for iw in (a["width_min"], a["width_max"]):
            for sx in (-1, 1):
                v.rect(sx * (iw / 2 + p / 2) - p / 2, 30, p, H - 30, fill="none", stroke=DIM, sw=0.8,
                       extra='stroke-dasharray="4 3"')
        frame(v, w, col)
        v.hdim(-L / 2, L / 2, 0, -30, L)
        v.idim(-w / 2, ab + ah / 2, w / 2, ab + ah / 2, w)
        v.idim(-w / 4, ab, -w / 4, ab + ah, ah)
        v.vdim(0, H, L / 2, 28, H)
        v.vdim(0, ab, -L / 2, -28, ab)
        mx = a["width_max"] / 2 + p
        v.hdim(-mx, mx, H, 22, f"ширина {a['width_min']}–{a['width_max']} (пунктир)")

    def side(v):
        v.rect(-150, 0, 300, 30, fill=rail)
        v.rect(-p / 2, 30, p, H - 30, fill=col)
        v.hdim(-150, 150, 0, -30, 300)
        v.flight(ab + ah / 2)

    return spec("Вид спереди", (-L / 2, L / 2, 0, H + 40), front, "Вид сбоку", (-150, 150, 0, H + 40), side,
                independent=False)


BUILDERS = {"C01": c_split_s, "C02": c_hairpin, "C03": c_chicane, "C04": c_ladder, "C05": c_tower,
            "C06": c_power_loop, "C07": c_spiral, "C08": c_funnel, "C09": c_adjustable}

if __name__ == "__main__":
    run("05-combos", BUILDERS, set(BUILDERS))
