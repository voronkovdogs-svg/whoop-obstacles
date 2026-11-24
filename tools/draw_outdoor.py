"""SVG-чертежи категории 08-outdoor (уличные объекты).

Запуск:  python tools/draw_outdoor.py          — все элементы
         python tools/draw_outdoor.py O02      — выбранные
"""
import math

from drawlib import DIM, INK, rect_pts, run

PATH = "#2E7D32"


def spec(main_title, main_ext, main_draw, aux_title, aux_ext, aux_draw, main_floor=True, aux_floor=True,
         independent=True):
    return {"main": dict(title=main_title, ext=main_ext, floor=main_floor, draw=main_draw),
            "aux": dict(title=aux_title, ext=aux_ext, floor=aux_floor, draw=aux_draw), "independent": independent}


def circle(v, x, y, r, fill, stroke=INK, sw=1.2, extra=""):
    v.raw(f'<circle cx="{v.X(x):.1f}" cy="{v.Y(y):.1f}" r="{max(r * v.k, 1.5):.1f}" fill="{fill}" '
          f'stroke="{stroke}" stroke-width="{sw}" {extra}/>')


def ellipse(v, x, y, rx, ry, fill, stroke=INK, sw=1.2, extra=""):
    v.raw(f'<ellipse cx="{v.X(x):.1f}" cy="{v.Y(y):.1f}" rx="{rx * v.k:.1f}" ry="{ry * v.k:.1f}" fill="{fill}" '
          f'stroke="{stroke}" stroke-width="{sw}" {extra}/>')


def foliage(v, cx, cy, rx, ry, col, n=7, seed=1):
    ellipse(v, cx, cy, rx, ry, col)
    for i in range(n):
        t = 2 * math.pi * i / n + seed
        r = 0.55
        circle(v, cx + rx * r * math.cos(t), cy + ry * r * math.sin(t), min(rx, ry) * 0.35, col,
               stroke="#1B5E20", sw=0.6, extra='fill-opacity="0.85"')


def thick(v, d, col, w_mm, outline=True):
    if outline:
        v.raw(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{w_mm * v.k + 2.4:.1f}" stroke-linejoin="round"/>')
    v.raw(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{max(w_mm * v.k, 1.5):.1f}" stroke-linejoin="round"/>')


# ---------------------------------------------------------------- элементы
def o_bush(e, va, d, a, col, *_):                     # O01
    W, H, D = d["width"], d["height"], d["depth"]

    def front(v):
        foliage(v, 0, H / 2, W / 2, H / 2, col)
        v.hdim(-W / 2, W / 2, H, 22, W)
        v.vdim(0, H, W / 2, 28, H)

    def side(v):
        foliage(v, 0, H / 2, D / 2, H / 2, col, seed=2)
        v.hdim(-D / 2, D / 2, 0, -30, D)

    return spec("Вид спереди", (-W / 2, W / 2, 0, H), front, "Вид сбоку", (-D / 2, D / 2, 0, H), side,
                independent=False)


def o_branch(e, va, d, a, bark, leaf="#43A047", *_):  # O02
    T, bh, bl, H = d["trunk"], d["branch_height"], d["branch_length"], d["height"]

    def front(v):
        v.rect(-T / 2, 0, T, H, fill=bark)
        v.poly([(T / 2, bh - 60), (T / 2 + bl, bh - 20), (T / 2 + bl, bh + 20), (T / 2, bh + 60)], fill=bark)
        foliage(v, T / 2 + bl * 0.75, bh + 120, bl * 0.28, 230, leaf, n=8)
        v.text(0, H - 120, "ствол", size=11, fill="#fff")
        v.idim(T / 2 + bl * 0.3, 0, T / 2 + bl * 0.3, bh - 60, a["height"])
        v.hdim(T / 2, T / 2 + bl, 0, -30, f"ветка {bl}")
        v.vdim(0, bh, -T / 2, -28, bh)
        v.hdim(-T / 2, T / 2, H, 22, f"Ø{T}")

    def side(v):
        v.rect(-T / 2, 0, T, H, fill=bark)
        circle(v, 0, bh, 60, bark)
        v.flight(bh / 2)
        v.hdim(-300, 300, 0, -30, "≈600")

    return spec("Вид спереди", (-T / 2, T / 2 + bl, 0, H), front, "Вид сбоку (ветка — к зрителю)",
                (-300, 300, 0, H), side)


def o_bench(e, va, d, a, wood, iron="#263238", *_):   # O03
    W, H, sh, sd, sw_ = d["width"], d["height"], d["seat_height"], d["seat_depth"], d["side"]

    def front(v):
        v.rect(-W / 2 + 60, sh + 80, W - 120, H - sh - 80, fill=wood, extra='fill-opacity="0.6"')
        for i in range(3):
            v.rect(-W / 2 + 60, sh + 120 + i * 110, W - 120, 70, fill=wood, sw=0.6)
        for sx in (-1, 1):
            v.rect(sx * (W / 2 - 60) - (sw_ if sx > 0 else 0) + (0 if sx > 0 else 0), 0, sw_, H, fill=iron)
        v.rect(-W / 2 + 60, sh - 30, W - 120, 30, fill=wood)
        v.hdim(-W / 2 + 60, W / 2 - 60, H, 22, W)
        v.vdim(0, H, W / 2 - 60, 28, H)
        v.idim(-a["width"] / 2, sh / 2, a["width"] / 2, sh / 2, a["width"])
        v.idim(-a["width"] / 3, 0, -a["width"] / 3, a["height"], a["height"])

    def side(v):
        v.poly([(-sd / 2, 0), (-sd / 2 + 60, 0), (-sd / 2 + 60, sh - 30), (-sd / 2, sh - 30)], fill=iron)
        v.poly([(sd / 2 - 60, 0), (sd / 2, 0), (sd / 2 + 120, H), (sd / 2 + 60, H)], fill=iron)
        v.rect(-sd / 2, sh - 30, sd, 30, fill=wood)
        for i in range(3):
            y = sh + 120 + i * 110
            x = sd / 2 + 60 * (y / H) * 2 - 40
            v.rect(x, y, 30, 70, fill=wood, sw=0.6)
        v.hdim(-sd / 2, sd / 2, 0, -30, sd)
        v.vdim(0, sh, -sd / 2, -28, sh)
        v.flight(sh / 2)

    return spec("Вид спереди", (-W / 2 + 60, W / 2 - 60, 0, H), front, "Вид сбоку", (-sd / 2, sd / 2 + 120, 0, H),
                side)


def o_fence(e, va, d, a, col, *_):                    # O04
    W, H, pk, gp, po = d["width"], d["height"], d["picket"], d["gap"], d["post"]
    ph = H - 100

    def front(v):
        for y in (250, 750):
            v.rect(-W / 2 + po, y - 40, W - 2 * po, 80, fill="#E0E0E0")
        x = -W / 2 + po + gp / 2
        while x + pk <= W / 2 - po:
            v.poly([(x, 50), (x + pk, 50), (x + pk, ph - 60), (x + pk / 2, ph), (x, ph - 60)], fill=col)
            x += pk + gp
        for sx in (-1, 1):
            v.rect(sx * (W / 2 - po / 2) - po / 2, 0, po, H, fill=col)
        v.hdim(-W / 2, W / 2, H, 22, W)
        v.vdim(0, H, W / 2, 28, H)
        v.hdim(-W / 2 + po + gp / 2, -W / 2 + po + gp / 2 + pk, 50, -26, pk)

    def side(v):
        v.rect(-po / 2, 0, po, H, fill=col)
        for y in (250, 750):
            v.rect(po / 2, y - 40, 25, 80, fill="#E0E0E0")
        v.flight(H + 200)
        v.hdim(-po / 2, po / 2, 0, -30, po)

    return spec("Вид спереди", (-W / 2, W / 2, 0, H), front, "Вид сбоку: перелёт", (-300, 300, 0, H + 260), side)


def o_arch(e, va, d, a, metal, plant="#66BB6A", *_):  # O05
    W, H, D, t, lh = d["width"], d["height"], d["depth"], d["tube"], d["leg_height"]
    R = W / 2 - t / 2

    def front(v):
        k = v.k
        dd = f"M{v.P(-R, 0)} L{v.P(-R, lh)} A{R * k:.1f},{R * k:.1f} 0 0,1 {v.P(R, lh)} L{v.P(R, 0)}"
        thick(v, dd, metal, t)
        for i in range(9):
            ang = math.radians(180 - i * 22.5)
            circle(v, R * math.cos(ang), lh + R * math.sin(ang), 80, plant, stroke="#2E7D32", sw=0.6,
                   extra='fill-opacity="0.8"')
        for sx in (-1, 1):
            for y in (400, 900, 1300):
                circle(v, sx * R, y, 70, plant, stroke="#2E7D32", sw=0.6, extra='fill-opacity="0.8"')
        v.hdim(-W / 2, W / 2, H, 22, W)
        v.vdim(0, H, W / 2, 28, H)
        v.idim(-a["width"] / 2, 700, a["width"] / 2, 700, a["width"])
        v.idim(0, 0, 0, a["height"], a["height"])

    def side(v):
        for z in (-D / 2, D / 2):
            v.rect(z - t / 2, 0, t, H, fill=metal)
        for y0 in range(0, H - 200, 400):
            v.line(-D / 2, y0, D / 2, y0 + 400, stroke=metal, sw=1.2)
            v.line(D / 2, y0, -D / 2, y0 + 400, stroke=metal, sw=1.2)
        v.hdim(-D / 2, D / 2, 0, -30, D)
        v.flight(H / 2)

    return spec("Вид спереди", (-W / 2, W / 2, 0, H), front, "Вид сбоку", (-D / 2, D / 2, 0, H), side,
                independent=False)


def o_slide(e, va, d, a, post, plat="#E53935", chute="#FDD835", *_):  # O06-a
    P, ph, cl, cw, ang = d["platform"], d["platform_height"], d["chute"], d["chute_width"], d["chute_angle"]
    run_ = cl * math.cos(math.radians(ang))

    def side(v):
        for z in (0, P):
            v.rect(z - 30, 0, 60, ph + 900, fill=post)
        v.rect(0, ph - 60, P, 60, fill=plat)
        v.rect(0, ph + 800, P, 40, fill=plat)
        v.poly([(P, ph), (P + run_, 0), (P + run_, 60), (P, ph + 60)], fill=chute)
        for i in range(6):
            y = i * 200 + 100
            v.line(-600 + y / 2, y, -600 + y / 2 + 400, y, stroke=post, sw=1.5)
        v.line(-600, 0, 0, ph, stroke=post, sw=2.5)
        v.line(-200, 0, 30, ph, stroke=post, sw=2.5)
        v.hdim(0, P, ph + 900, 22, P)
        v.vdim(0, ph, P + run_, 28, ph)
        v.hdim(P, P + run_, 0, -30, f"скат {cl} под {ang}°")
        v.idim(P * 0.5, 0, P * 0.5, ph - 60, a["height"])
        v.text(-450, 1100, "лестница", size=11, fill=DIM)

    def front(v):   # со стороны ската
        for x in (-P / 2 + 30, P / 2 - 30):
            v.rect(x - 30, 0, 60, ph + 900, fill=post)
        v.rect(-P / 2, ph - 60, P, 60, fill=plat)
        v.rect(-cw / 2, 0, cw, ph, fill=chute, extra='fill-opacity="0.85"')
        v.hdim(-P / 2, P / 2, ph + 900, 22, P)
        v.hdim(-cw / 2, cw / 2, 0, -30, f"скат {cw}")

    return spec("Вид сбоку", (-600, P + run_, 0, ph + 900), side, "Вид со стороны ската", (-P / 2, P / 2, 0, ph + 900),
                front)


def o_swings(e, va, d, a, frame, seat="#212121", *_):  # O06-b
    B, H, D, sh = d["beam"], d["height"], d["depth"], d["seat_height"]

    def front(v):
        for sx in (-1, 1):
            v.rect(sx * B / 2 - 30, 0, 60, H, fill=frame)
        v.rect(-B / 2 - 30, H - 60, B + 60, 60, fill=frame)
        for cx in (-B / 4, B / 4):
            for dx in (-200, 200):
                v.line(cx + dx, H - 60, cx + dx, sh + 30, stroke="#757575", sw=1.2, extra='stroke-dasharray="3 2"')
            v.rect(cx - 225, sh, 450, 30, fill=seat)
        v.hdim(-B / 2 - 30, B / 2 + 30, H, 22, d["width"])
        v.vdim(0, H, B / 2 + 30, 28, H)
        v.idim(-B / 4 + 200, 1300, B / 4 - 200, 1300, int(B / 2 - 400))
        v.vdim(0, sh, -B / 2 - 30, -28, sh)

    def side(v):
        v.line(-D / 2, 0, 0, H, stroke=frame, sw=4)
        v.line(D / 2, 0, 0, H, stroke=frame, sw=4)
        v.line(0, H, 0, sh + 30, stroke="#757575", sw=1.2, extra='stroke-dasharray="3 2"')
        v.rect(-150, sh, 300, 30, fill=seat)
        v.hdim(-D / 2, D / 2, 0, -30, D)
        v.flight(1300)

    return spec("Вид спереди", (-B / 2 - 30, B / 2 + 30, 0, H), front, "Вид сбоку", (-D / 2, D / 2, 0, H), side)


def o_playground(e, va, d, a, *cols):
    return (o_slide if "горка" in va["label"] else o_swings)(e, va, d, a, *cols)


def o_rack(e, va, d, a, col, *_):                     # O07
    W, H, n, st, t = d["width"], d["height"], d["hoops"], d["step"], d["tube"]
    R = W / 2 - t / 2
    leg = H - t / 2 - R

    def front(v):
        k = v.k
        thick(v, f"M{v.P(-R, 0)} L{v.P(-R, leg)} A{R * k:.1f},{R * k:.1f} 0 0,1 {v.P(R, leg)} L{v.P(R, 0)}", col, t)
        v.hdim(-W / 2, W / 2, H, 22, W)
        v.vdim(0, H, W / 2, 28, H)
        v.idim(-a["width"] / 2, 300, a["width"] / 2, 300, a["width"])
        v.idim(0, 0, 0, a["height"], a["height"])

    def side(v):
        for i in range(n):
            v.rect(i * st - t / 2, 0, t, H, fill=col)
        path = f"M{v.P(-600, 450)} L{v.P((n - 1) * st + 600, 450)}"
        v.raw(f'<path d="{path}" fill="none" stroke="{PATH}" stroke-width="1.8" stroke-dasharray="7 5" '
              f'marker-end="url(#fa)"/>')
        v.hdim(0, st, H, 22, st)
        v.hdim(-t / 2, (n - 1) * st + t / 2, 0, -30, d["depth"])

    return spec("Вид спереди: одна дуга", (-W / 2, W / 2, 0, H), front, "Вид сбоку: ряд дуг",
                (-600, (n - 1) * st + 600, 0, H), side)


BUILDERS = {"O01": o_bush, "O02": o_branch, "O03": o_bench, "O04": o_fence, "O05": o_arch,
            "O06": o_playground, "O07": o_rack}

if __name__ == "__main__":
    run("08-outdoor", BUILDERS, set(BUILDERS))
