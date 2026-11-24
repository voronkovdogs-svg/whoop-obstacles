"""SVG-чертежи категории 09-service (служебные и тренировочные элементы).

Запуск:  python tools/draw_service.py          — все элементы
         python tools/draw_service.py S02      — выбранные
"""
import math

from drawlib import DIM, INK, rect_pts, run

PATH = "#2E7D32"
HALO = 'paint-order="stroke" stroke="#fff" stroke-width="3"'


def spec(main_title, main_ext, main_draw, aux_title, aux_ext, aux_draw, main_floor=True, aux_floor=True,
         independent=True):
    return {"main": dict(title=main_title, ext=main_ext, floor=main_floor, draw=main_draw),
            "aux": dict(title=aux_title, ext=aux_ext, floor=aux_floor, draw=aux_draw), "independent": independent}


def circle(v, x, y, r, fill, stroke=INK, sw=1.2, extra=""):
    v.raw(f'<circle cx="{v.X(x):.1f}" cy="{v.Y(y):.1f}" r="{max(r * v.k, 1.5):.1f}" fill="{fill}" '
          f'stroke="{stroke}" stroke-width="{sw}" {extra}/>')


def flat_side(v, W, t, col, label=None):
    v.rect(-W / 2, 0, W, max(t, 3), fill=col)
    v.hdim(-W / 2, W / 2, 0, -30, W)
    if label:
        v.text(0, 60, label, size=11, fill=DIM)


# ---------------------------------------------------------------- элементы
def s_start(e, va, d, a, col, white="#FFFFFF", orange="#FF6D00", *_):  # S01
    W = d["width"]

    def top(v):
        v.rect(-W / 2, -W / 2, W, W, fill=col)
        v.rect(-W / 2 + 10, -W / 2 + 10, W - 20, W - 20, fill="none", stroke=white, sw=1.5)
        v.line(-90, 0, 90, 0, stroke=white, sw=3)
        v.line(0, -90, 0, 90, stroke=white, sw=3)
        v.poly([(-35, 100), (35, 100), (0, 140)], fill=orange, stroke="none")
        v.rect(-6, 60, 12, 40, fill=orange, stroke="none")
        v.text(-W / 2 + 40, -W / 2 + 35, "1", size=18, fill=orange, extra='font-weight="bold"')
        v.raw(f'<rect x="{v.X(-45):.1f}" y="{v.Y(45):.1f}" width="{90 * v.k:.1f}" height="{90 * v.k:.1f}" '
              f'fill="none" stroke="{PATH}" stroke-dasharray="3 2"/>')
        v.text(0, -W / 2 - 45, "пунктир — вуп ≈90×90, нос по стрелке", size=11, fill=PATH, extra=HALO)
        v.hdim(-W / 2, W / 2, W / 2, 22, W)
        v.vdim(-W / 2, W / 2, W / 2, 28, W)

    def side(v):
        flat_side(v, W, d["height"], col, f"толщина {d['height']}")

    return spec("Вид сверху", (-W / 2, W / 2, -W / 2 - 60, W / 2), top, "Вид сбоку", (-W / 2, W / 2, 0, 80), side,
                main_floor=False)


def s_landing(e, va, d, a, *cols):                    # S02
    W = d["width"]
    target = "мишень" in va["label"]

    def top(v):
        if target:
            rings = [int(x) for x in d["rings"].split(",")]
            for r, c in zip(rings, cols):
                circle(v, 0, 0, r / 2, c)
            mids = [(rings[i] + (rings[i + 1] if i + 1 < len(rings) else 0)) / 4 for i in range(len(rings))]
            for m_, pts in zip(mids, (1, 2, 3, 4)):
                v.text(0, (m_ if pts < 4 else 0) - 12, pts, size=14, fill=INK, extra='font-weight="bold" ' + HALO)
            v.hdim(-W / 2, W / 2, W / 2, 22, f"Ø{W}")
            v.text(0, -W / 2 - 80, "очки за посадку", size=11, fill=DIM)
        else:
            circle(v, 0, 0, W / 2, cols[0])
            circle(v, 0, 0, W / 2 - 20, "none", stroke=cols[1] if len(cols) > 1 else "#fff", sw=2)
            v.text(0, -55, "H", size=int(160 * v.k) or 20, fill=cols[1] if len(cols) > 1 else "#fff",
                   extra='font-weight="bold"')
            v.hdim(-W / 2, W / 2, W / 2, 22, f"Ø{W}")

    def side(v):
        flat_side(v, W, d["height"], cols[0], f"толщина {d['height']}")

    return spec("Вид сверху", (-W / 2, W / 2, -W / 2 - 100, W / 2), top, "Вид сбоку", (-W / 2, W / 2, 0, 80), side,
                main_floor=False)


def s_finish(e, va, d, a, col, black="#212121", *_):  # S03
    W, H, tb, sb, bb = d["width"], d["height"], d["top_band"], d["side_band"], d["bottom_bar"]
    iw, ih = a["width"], a["height"]

    def front(v):
        v.holed(rect_pts(-W / 2, 0, W, H), [rect_pts(-iw / 2, bb, iw, ih)], col, sw=2.5)
        n = int(W // 60)
        cw = W / n
        for i in range(n):
            for j in range(2):
                if (i + j) % 2 == 0:
                    v.rect(-W / 2 + i * cw, H - tb + j * tb / 2, cw, tb / 2, fill=black, sw=0)
        v.rect(-W / 2, 0, W, H, fill="none", stroke=INK, sw=2.5)
        v.hdim(-W / 2, W / 2, H, 22, W)
        v.vdim(0, H, W / 2, 28, H)
        v.idim(-iw / 2, bb + ih / 2, iw / 2, bb + ih / 2, iw)
        v.idim(-iw / 4, bb, -iw / 4, bb + ih, ih)
        v.vdim(H - tb, H, -W / 2, -28, tb)

    def side(v):
        v.rect(-150, 0, 300, 10, fill="#333")
        v.rect(-4, 0, 8, H, fill="#333")
        v.line(-4, bb, -4, bb + ih, stroke="#C62828", sw=2, extra='stroke-dasharray="5 3"')
        v.hdim(-150, 150, 0, -30, 300)
        v.flight(bb + ih / 2)
        v.text(-60, H + 40, "финишная плоскость", size=11, fill="#C62828", extra=HALO)

    return spec("Вид спереди", (-W / 2, W / 2, 0, H), front, "Вид сбоку", (-150, 150, 0, H + 60), side)


def s_timing(e, va, d, a, col, led="#00E5FF", box="#212121", *_):  # S04
    g, b = d["gate"], d["band"]

    def front(v):
        v.holed(rect_pts(-g / 2, 0, g, g), [rect_pts(-g / 2 + b, b, g - 2 * b, g - 2 * b)], col)
        v.rect(-g / 2 + b, b, g - 2 * b, g - 2 * b, fill="none", stroke=led, sw=3)
        v.rect(-60, g, 120, 40, fill=box)
        v.raw(f'<circle cx="{v.X(40):.1f}" cy="{v.Y(g + 20):.1f}" r="3" fill="#76FF03"/>')
        v.hdim(-g / 2, g / 2, g + 40, 22, g)
        v.vdim(0, g + 40, g / 2, 28, d["height"])
        v.idim(-g / 2 + b, g / 2, g / 2 - b, g / 2, a["width"])

    def side(v):
        v.rect(-100, 0, 200, 6, fill="#666")
        v.rect(-4, 0, 8, g, fill=col)
        v.rect(-20, g, 40, 40, fill=box)
        v.line(0, b, 0, g - b, stroke=led, sw=2, extra='stroke-dasharray="5 3"')
        v.text(0, -90, "плоскость проёма — триггер круга", size=11, fill="#0097A7", extra=HALO)
        v.hdim(-100, 100, 0, -30, 200)
        v.flight(g / 2)

    return spec("Вид спереди", (-g / 2, g / 2, 0, g + 80), front, "Вид сбоку", (-100, 100, -120, g + 80), side)


def s_cube(e, va, d, a, col, *_):                     # S05
    C, lift, rod = d["cube"], d["lift"], d["rod"]

    def frame(v, y0, depth_lines=True):
        for x in (-C / 2, C / 2):
            v.rect(x - rod / 2, 0, rod, y0 + C, fill=col, sw=0.6)
        for y in (y0, y0 + C):
            v.rect(-C / 2, y - rod / 2, C, rod, fill=col, sw=0.6)
        if depth_lines:
            off = 120
            for x, y in ((-C / 2, y0), (C / 2, y0), (-C / 2, y0 + C), (C / 2, y0 + C)):
                v.line(x, y, x + off, y + off, stroke=col, sw=1.5, extra='opacity="0.6"')
            v.rect(-C / 2 + off, y0 + off, C, C, fill="none", stroke=col, sw=1.5, extra='opacity="0.6"')

    def front(v):
        frame(v, lift)
        v.raw(f'<rect x="{v.X(-45):.1f}" y="{v.Y(lift + C / 2 + 15):.1f}" width="{90 * v.k:.1f}" '
              f'height="{30 * v.k:.1f}" fill="none" stroke="{PATH}" stroke-dasharray="3 2"/>')
        v.text(0, lift + C / 2 - 60, "висеть 5–10 с", size=11, fill=PATH, extra=HALO)
        v.hdim(-C / 2, C / 2, lift + C + 120, 22, C)
        v.vdim(0, lift + C, C / 2 + 120, 28, lift + C)
        v.vdim(0, lift, -C / 2, -28, lift)

    def top(v):
        v.rect(-C / 2, -C / 2, C, C, fill="none", stroke=col, sw=3)
        for x in (-C / 2, C / 2):
            for z in (-C / 2, C / 2):
                circle(v, x, z, 12, col)
        v.hdim(-C / 2, C / 2, C / 2, 22, C)
        v.text(0, 0, "грани открыты", size=11, fill=DIM)

    return spec("Вид спереди (перспектива задней грани — бледно)", (-C / 2, C / 2 + 120, 0, lift + C + 120), front,
                "Вид сверху", (-C / 2, C / 2, -C / 2, C / 2), top, aux_floor=False)


def s_figure8(e, va, d, a, c1, c2="#29B6F6", *_):     # S06
    sp, R = d["spacing"], d["loop_radius"]

    def top(v):   # x — вдоль оси столбов
        pts = []
        for i in range(181):
            t = 2 * math.pi * i / 180
            x = (sp / 2 + R) * math.sin(t)
            z = (R * 1.0) * math.sin(2 * t)
            pts.append((x, z))
        v.raw(f'<polyline points="{" ".join(v.P(*p) for p in pts[:170])}" fill="none" stroke="{PATH}" '
              f'stroke-width="1.8" stroke-dasharray="7 5" marker-end="url(#fa)"/>')
        for x, c in ((-sp / 2, c1), (sp / 2, c2)):
            circle(v, x, 0, 100, "#616161")
            circle(v, x, 0, 32.5, c)
        v.hdim(-sp / 2, sp / 2, -R, -40, f"{sp} между шестами")
        v.text(0, R + 80, "перекрестье", size=11, fill=PATH, extra=HALO)

    def front(v):
        for x, c in ((-sp / 2, c1), (sp / 2, c2)):
            v.rect(x - 100, 0, 200, 20, fill="#616161")
            v.rect(x - 32.5, 20, 65, 1600, fill=c)
        v.vdim(0, 1620, sp / 2 + 100, 28, 1620)
        v.hdim(-sp / 2, sp / 2, 0, -30, sp)

    W = sp / 2 + R + 60
    return spec("Вид сверху: траектория", (-W, W, -R - 120, R + 140), top, "Вид спереди",
                (-sp / 2 - 100, sp / 2 + 100, 0, 1620), front, main_floor=False)


def s_arrow(e, va, d, a, bg, fg="#212121", *_):       # S07
    pw, ph, pb = 400, 250, d["plate_bottom"]

    def front(v):
        for sx in (-1, 1):
            v.rect(sx * 150 - 8, 0, 16, pb + 40, fill="#757575")
        v.rect(-pw / 2, pb, pw, ph, fill=bg)
        cx, cy = 0, pb + ph / 2
        v.poly([(cx - 140, cy + 50), (cx + 30, cy + 50), (cx + 30, cy + 95), (cx + 150, cy), (cx + 30, cy - 95),
                (cx + 30, cy - 50), (cx - 140, cy - 50)], fill=fg, stroke="none")
        v.hdim(-pw / 2, pw / 2, pb + ph, 22, pw)
        v.vdim(pb, pb + ph, pw / 2, 28, ph)
        v.vdim(0, pb, -pw / 2, -28, pb)

    def side(v):
        v.rect(-100, 0, 200, 10, fill="#757575")
        v.rect(-8, 0, 16, pb + 40, fill="#757575")
        v.rect(-1.5, pb, 3, ph, fill=bg)
        v.hdim(-100, 100, 0, -30, 200)

    return spec("Вид спереди", (-pw / 2, pw / 2, 0, pb + ph), front, "Вид сбоку", (-100, 100, 0, pb + ph), side,
                independent=False)


def s_number(e, va, d, a, bg, fg="#212121", *_):      # S08
    P, st, dg = d["plate"], d["stand"], d["digit"]

    def front(v):
        v.rect(-60, 0, 120, 10, fill="#757575")
        v.rect(-8, 10, 16, st - 10, fill="#757575")
        v.rect(-P / 2, st, P, P, fill=bg)
        v.text(0, st + P / 2 - dg * 0.36, "7", size=max(12, int(dg * v.k)), fill=fg, extra='font-weight="bold"')
        v.hdim(-P / 2, P / 2, st + P, 22, P)
        v.vdim(st, st + P, P / 2, 28, P)
        v.vdim(0, st, -P / 2, -28, st)
        v.idim(P / 2 - 30, st + (P - dg) / 2, P / 2 - 30, st + (P + dg) / 2, f"цифра {dg}")

    def side(v):
        v.rect(-60, 0, 120, 10, fill="#757575")
        v.rect(-8, 10, 16, st - 10, fill="#757575")
        v.rect(-1.5, st, 3, P, fill=bg)
        v.rect(1.5, st + P - 40, 20, 40, fill="#9e9e9e", sw=0.6)
        v.text(30, st + P - 10, "клипса", size=11, anchor="start", fill=DIM)
        v.hdim(-60, 60, 0, -30, 120)

    return spec("Вид спереди", (-P / 2, P / 2, 0, st + P), front, "Вид сбоку", (-60, 60, 0, st + P), side,
                independent=False)


def s_net(e, va, d, a, net, post="#9E9E9E", *_):      # S09
    W, H, m, p = d["width"], d["height"], d["mesh"], d["post"]

    def front(v):
        s = max(m * v.k * 4, 3)
        v.raw(f'<defs><pattern id="snet" width="{s:.2f}" height="{s:.2f}" patternUnits="userSpaceOnUse">'
              f'<path d="M0,0 L{s:.2f},0 M0,0 L0,{s:.2f}" stroke="{net}" stroke-width="0.6"/></pattern></defs>')
        v.rect(-W / 2 + p, 50, W - 2 * p, H - 50, fill="url(#snet)", sw=0.8)
        for sx in (-1, 1):
            v.rect(sx * (W / 2 - p / 2) - p / 2, 0, p, H, fill=post)
            v.rect(sx * (W / 2 - p / 2) - 60, 0, 120, 15, fill="#616161")
        v.hdim(-W / 2, W / 2, H, 22, W)
        v.vdim(0, H, W / 2, 28, H)
        v.text(0, H / 2, f"сетка, ячейка {m}", size=12, fill=INK, extra=HALO)

    def side(v):
        v.rect(-300, 0, 600, 15, fill="#616161")
        v.rect(-p / 2, 15, p, H - 15, fill=post)
        v.hdim(-300, 300, 0, -30, 600)
        v.text(-200, H + 60, "трасса", size=11, fill=DIM)
        v.text(200, H + 60, "пилоты", size=11, fill=DIM)

    return spec("Вид спереди", (-W / 2, W / 2, 0, H), front, "Вид сбоку", (-300, 300, 0, H + 80), side)


BUILDERS = {"S01": s_start, "S02": s_landing, "S03": s_finish, "S04": s_timing, "S05": s_cube,
            "S06": s_figure8, "S07": s_arrow, "S08": s_number, "S09": s_net}

if __name__ == "__main__":
    run("09-service", BUILDERS, set(BUILDERS))
