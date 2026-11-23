"""SVG-чертежи категории 03-markers (флаги, конусы, столбы — огибаемые ориентиры).

Запуск:  python tools/draw_markers.py          — все маркеры
         python tools/draw_markers.py M03 M07  — выбранные элементы

У маркеров нет проёма: вместо стрелки пролёта на виде сверху показана траектория облёта.
"""
import math

from drawlib import DIM, INK, run

PATH = "#2E7D32"


def spec(main_title, main_ext, main_draw, aux_title, aux_ext, aux_draw, main_floor=True, aux_floor=True,
         independent=False):
    return {"main": dict(title=main_title, ext=main_ext, floor=main_floor, draw=main_draw),
            "aux": dict(title=aux_title, ext=aux_ext, floor=aux_floor, draw=aux_draw), "independent": independent}


def circle(v, x, y, r, fill, stroke=INK, sw=1.2):
    v.raw(f'<circle cx="{v.X(x):.1f}" cy="{v.Y(y):.1f}" r="{max(r * v.k, 1.5):.1f}" fill="{fill}" '
          f'stroke="{stroke}" stroke-width="{sw}"/>')


def path(v, pts, dashed=True, arrow=True):
    d = "M" + " L".join(v.P(*p) for p in pts)
    v.raw(f'<path d="{d}" fill="none" stroke="{PATH}" stroke-width="1.8" stroke-linejoin="round" '
          f'{"stroke-dasharray=\"7 5\"" if dashed else ""} {"marker-end=\"url(#fa)\"" if arrow else ""}/>')


def smooth(pts, n=12):
    """Сглаживание ломаной (Catmull-Rom) — для траекторий облёта."""
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(n):
            t = j / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[c]) + (-p0[c] + p2[c]) * t + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t2
                                    + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * t3) for c in (0, 1)))
    out.append(pts[-1])
    return out


# ---------------------------------------------------------------- элементы
def m_flag(e, va, d, a, col, *_):                     # M01, M02
    Hh, p = d["height"], d["pole"]
    sw_, sh = d["sail_width"], d["sail_height"]
    rb = d["base_diameter"] / 2
    sb = Hh - sh
    feather = e["id"] == "M02"

    def sail(v):
        if feather:
            return (f"M{v.P(p / 2, sb)} L{v.P(sw_, sb)} L{v.P(sw_, Hh - 0.3 * sh)} "
                    f"Q{v.P(sw_, Hh)} {v.P(p / 2, Hh)} Z")
        return (f"M{v.P(p / 2, sb)} L{v.P(sw_, sb + 0.12 * sh)} "
                f"Q{v.P(sw_ * 1.05, Hh - 0.05 * sh)} {v.P(p / 2, Hh)} Z")

    def front(v):
        v.rect(-rb, 0, 2 * rb, 30, fill="#616161")
        v.raw(f'<path d="{sail(v)}" fill="{col}" stroke="{INK}" stroke-width="1.2"/>')
        top_bend = f" Q{v.P(p / 2 + sw_ * 0.5, Hh + 20)} {v.P(sw_ * 0.9, Hh - 0.12 * sh)}" if feather else ""
        v.raw(f'<path d="M{v.P(0, 30)} L{v.P(0, Hh)}{top_bend}" fill="none" stroke="{INK}" '
              f'stroke-width="{max(p * v.k, 1.5) + 2:.1f}"/>')
        v.raw(f'<path d="M{v.P(0, 30)} L{v.P(0, Hh)}{top_bend}" fill="none" stroke="#fafafa" '
              f'stroke-width="{max(p * v.k, 1.5):.1f}"/>')
        v.hdim(0, sw_, Hh, 22, f"полотно {sw_}")
        v.vdim(sb, Hh, sw_, 28, sh)
        v.vdim(0, Hh, sw_, 62, Hh)
        v.hdim(-rb, rb, 0, -30, f"Ø{d['base_diameter']}")

    def side(v):
        v.rect(-rb, 0, 2 * rb, 30, fill="#616161")
        v.rect(-p / 2, 30, p, Hh - 30, fill="#fafafa")
        v.rect(-1.5, sb, 3, sh, fill=col, sw=0.6)
        v.vdim(0, Hh, rb, 28, Hh)
        v.hdim(-rb, rb, 0, -30, f"Ø{d['base_diameter']}")

    return spec("Вид спереди (полотно)", (-rb, sw_, 0, Hh), front, "Вид сбоку", (-rb, rb, 0, Hh), side)


def m_cone(e, va, d, a, col, band="#FFFFFF", *_):     # M03
    B, Hh, bh = d["width"], d["height"], d["base_height"]
    rb, rt = d["body_bottom"] / 2, d["body_top"] / 2

    def rx(y):  # радиус тела на высоте y
        return rb + (rt - rb) * (y - bh) / (Hh - bh)

    def front(v):
        v.rect(-B / 2, 0, B, bh, fill=col)
        v.poly([(-rb, bh), (rb, bh), (rt, Hh), (-rt, Hh)], fill=col)
        fr = [(0.35, 0.55)] if d["bands"] == 1 else [(0.3, 0.42), (0.58, 0.7)]
        for f1, f2 in fr:
            y1, y2 = bh + f1 * (Hh - bh), bh + f2 * (Hh - bh)
            v.poly([(-rx(y1), y1), (rx(y1), y1), (rx(y2), y2), (-rx(y2), y2)], fill=band)
        v.hdim(-B / 2, B / 2, 0, -30, B)
        v.vdim(0, Hh, B / 2, 28, Hh)
        v.hdim(-rt, rt, Hh, 22, f"Ø{d['body_top']}")
        v.idim(-rb, bh + 8, rb, bh + 8, f"Ø{d['body_bottom']}", side=-1)

    def top(v):
        v.rect(-B / 2, -B / 2, B, B, fill=col)
        circle(v, 0, 0, rb, col)
        circle(v, 0, 0, rb * 0.75, band, sw=0.6)
        circle(v, 0, 0, rb * 0.55, col, sw=0.6)
        circle(v, 0, 0, rt, "#fff")
        v.hdim(-B / 2, B / 2, B / 2, 22, B)

    return spec("Вид спереди", (-B / 2, B / 2, 0, Hh), front, "Вид сверху", (-B / 2, B / 2, -B / 2, B / 2), top,
                aux_floor=False)


def m_disc(e, va, d, a, col, *_):                     # M04
    D, Hh, hole = d["width"], d["height"], d["top_hole"]
    rt = hole / 2 + 10

    def front(v):
        v.raw(f'<path d="M{v.P(-D / 2, 0)} L{v.P(D / 2, 0)} Q{v.P(D / 2 - 15, Hh * 0.9)} {v.P(rt, Hh)} '
              f'L{v.P(-rt, Hh)} Q{v.P(-D / 2 + 15, Hh * 0.9)} {v.P(-D / 2, 0)} Z" fill="{col}" '
              f'stroke="{INK}" stroke-width="1.2"/>')
        v.line(-hole / 2, Hh, hole / 2, Hh, stroke="#fff", sw=3)
        v.hdim(-D / 2, D / 2, 0, -30, f"Ø{D}")
        v.vdim(0, Hh, D / 2, 28, Hh)
        v.hdim(-hole / 2, hole / 2, Hh, 22, f"отв. Ø{hole}")

    def top(v):
        circle(v, 0, 0, D / 2, col)
        circle(v, 0, 0, rt, col, sw=0.6)
        circle(v, 0, 0, hole / 2, "#fff")
        v.hdim(-D / 2, D / 2, D / 2, 22, f"Ø{D}")

    return spec("Вид спереди", (-D / 2, D / 2, 0, Hh), front, "Вид сверху", (-D / 2, D / 2, -D / 2, D / 2), top,
                aux_floor=False)


def m_pole(e, va, d, a, col, *_):                     # M05
    Hh, t, rb = d["height"], d["tube"], d["base_diameter"] / 2

    def front(v):
        v.rect(-rb, 0, 2 * rb, 20, fill="#616161")
        v.rect(-t / 2, 20, t, Hh - 20, fill=col)
        v.rect(-t / 2, 20, t, Hh - 20, fill="url(#cylh)", stroke="none")
        v.hdim(-rb, rb, 0, -30, f"Ø{d['base_diameter']}")
        v.vdim(0, Hh, rb, 28, Hh)
        v.hdim(-t / 2, t / 2, Hh, 22, f"Ø{t}")

    def top(v):
        circle(v, 0, 0, rb, "#616161")
        circle(v, 0, 0, t / 2, col)
        circle(v, 0, 0, 10, "#fafafa", sw=0.8)
        v.hdim(-rb, rb, rb, 22, f"Ø{d['base_diameter']}")
        v.idim(-t / 2, 0, t / 2, 0, f"Ø{t}", side=-1)

    return spec("Вид спереди", (-rb, rb, 0, Hh), front, "Вид сверху", (-rb, rb, -rb, rb), top, aux_floor=False,
                independent=True)


def m_pylon(e, va, d, a, col, col2="#212121", *_):    # M06
    Hh, c, st, B = d["height"], d["column"], d["stripe"], d["base"]
    R = 350

    def front(v):
        v.rect(-B / 2, 0, B, 20, fill="#757575")
        y, i = 20, 0
        while y < Hh - 1:
            h = min(st, Hh - y)
            v.rect(-c / 2, y, c, h, fill=col if i % 2 == 0 else col2, sw=0.6)
            y += h
            i += 1
        v.rect(-c / 2, 20, c, Hh - 20, fill="url(#cylh)", stroke=INK)
        v.hdim(-B / 2, B / 2, 0, -30, B)
        v.vdim(0, Hh, B / 2, 28, Hh)
        v.vdim(20, 20 + st, -c / 2, -28, f"полоса {st}")
        v.hdim(-c / 2, c / 2, Hh, 22, f"Ø{c}")

    def top(v):  # разворот на 180° вокруг колонны
        v.rect(-B / 2, -B / 2, B, B, fill="#757575")
        circle(v, 0, 0, c / 2, col)
        pts = [(-1100, R)] + [(R * math.sin(t), R * math.cos(t))
                              for t in [i * math.pi / 16 for i in range(17)]] + [(-1100, -R)]
        path(v, pts)
        v.idim(0, 0, R * math.sin(math.radians(60)), R * math.cos(math.radians(60)), f"R≈{R}")
        v.text(-700, R + 50, "заход", size=11, fill=PATH)
        v.text(-700, -R - 90, "выход", size=11, fill=PATH)

    return spec("Вид спереди", (-B / 2, B / 2, 0, Hh), front, "Вид сверху: разворот", (-1100, R, -R - 60, R + 60),
                top, aux_floor=False, independent=True)


def m_slalom(e, va, d, a, col, col2="#1E88E5", *_):   # M07
    n, sp, p, rb, Hh = d["poles"], d["spacing"], d["pole"], d["base_diameter"] / 2, d["height"]
    L = d["depth"]
    zs = [rb + i * sp for i in range(n)]
    off = 300

    def top(v):
        pts = [(-350, 0)] + [(z, off if i % 2 == 0 else -off) for i, z in enumerate(zs)] + [(L + 350, 0)]
        path(v, smooth(pts))
        for i, z in enumerate(zs):
            circle(v, z, 0, rb, "#424242")
            circle(v, z, 0, p / 2 + 6, col if i % 2 == 0 else col2)
        v.hdim(zs[0], zs[1], 0, 70, sp)
        v.hdim(0, L, -off, -40, L)
        v.vdim(0, off, L + 350, 20, f"≈{off}")
        v.text(-330, 50, "заход", size=11, anchor="start", fill=PATH)

    def front(v):
        v.rect(-rb, 0, 2 * rb, 20, fill="#424242")
        v.rect(-p / 2, 20, p, Hh - 20, fill=col)
        v.rect(-p / 2, 20, p, Hh - 20, fill="url(#cylh)", stroke=INK)
        v.vdim(0, Hh, rb, 28, Hh)
        v.hdim(-rb, rb, 0, -30, f"Ø{d['base_diameter']}")
        v.hdim(-p / 2, p / 2, Hh, 22, f"Ø{p}")

    return spec("Вид сверху: траектория", (-350, L + 350, -off - 60, off + 60), top,
                "Шест, вид спереди", (-rb, rb, 0, Hh), front, main_floor=False, independent=True)


BUILDERS = {"M01": m_flag, "M02": m_flag, "M03": m_cone, "M04": m_disc, "M05": m_pole,
            "M06": m_pylon, "M07": m_slalom}

if __name__ == "__main__":
    run("03-markers", BUILDERS, set(BUILDERS))
