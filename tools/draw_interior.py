"""SVG-чертежи категории 07-interior (интерьер: мебель и элементы квартиры).

Запуск:  python tools/draw_interior.py          — все элементы
         python tools/draw_interior.py I01 I10  — выбранные
"""
import math

from drawlib import DIM, INK, rect_pts, run

PATH = "#2E7D32"
MOVE = "#EF6C00"
HALO = 'paint-order="stroke" stroke="#fff" stroke-width="3"'


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


def route(v, d):
    v.raw(f'<path d="{d}" fill="none" stroke="{PATH}" stroke-width="1.8" stroke-dasharray="7 5" '
          f'marker-end="url(#fa)"/>')


# ---------------------------------------------------------------- элементы
def i_table(e, va, d, a, col, *_):                     # I01
    W, D, H, t, leg, ins = d["width"], d["depth"], d["height"], d["top"], d["leg"], d["leg_inset"]

    def legs(v, span):
        for sx in (-1, 1):
            x = sx * (span / 2 - ins - leg / 2)
            v.rect(x - leg / 2, 0, leg, H - t, fill=col)

    def front(v):
        legs(v, W)
        v.rect(-W / 2, H - t, W, t, fill=col)
        v.hdim(-W / 2, W / 2, H, 22, W)
        v.vdim(0, H, W / 2, 28, H)
        v.idim(-a["width"] / 2, 300, a["width"] / 2, 300, a["width"])
        v.idim(-a["width"] / 4, 0, -a["width"] / 4, H - t, a["height"])

    def side(v):
        legs(v, D)
        v.rect(-D / 2, H - t, D, t, fill=col)
        v.hdim(-D / 2, D / 2, H, 22, D)
        v.idim(-a["across_width"] / 2, 200, a["across_width"] / 2, 200, a["across_width"])
        v.flight(H / 2 - 40)

    return spec("Вид спереди (вдоль пролёта)", (-W / 2, W / 2, 0, H), front, "Вид сбоку",
                (-D / 2, D / 2, 0, H), side, independent=False)


def i_chair(e, va, d, a, legc, seat="#D7A86E", *_):    # I02
    S, sh, H, leg = d["seat"], d["seat_height"], d["height"], d["leg"]

    def front(v):
        v.rect(-S / 2, sh, S, H - sh, fill=seat, extra='fill-opacity="0.45"')
        for sx in (-1, 1):
            v.rect(sx * (S / 2 - leg / 2) - leg / 2, 0, leg, sh - 20, fill=legc)
        v.rect(-S / 2, sh - 20, S, 20, fill=seat)
        v.hdim(-S / 2, S / 2, H, 22, S)
        v.vdim(0, H, S / 2, 28, H)
        v.idim(-a["width"] / 2, 120, a["width"] / 2, 120, a["width"])
        v.idim(-100, 0, -100, a["height"], a["height"])
        v.text(0, H - 120, "спинка (сзади)", size=11, fill=DIM)

    def side(v):
        for z in (-S / 2 + leg / 2, S / 2 - leg / 2):
            v.rect(z - leg / 2, 0, leg, sh - 20, fill=legc)
        v.rect(S / 2 - leg, sh, leg, H - sh, fill=legc)
        v.rect(S / 2 - leg - 20, sh + 180, 20, H - sh - 180, fill=seat)
        v.rect(-S / 2, sh - 20, S, 20, fill=seat)
        v.hdim(-S / 2, S / 2, 0, -30, S)
        v.vdim(0, sh, S / 2, 28, sh)
        v.flight(a["height"] / 2)

    return spec("Вид спереди", (-S / 2, S / 2, 0, H), front, "Вид сбоку", (-S / 2, S / 2, 0, H), side,
                independent=False)


def i_doorway(e, va, d, a, wall, door="#ECEFF1", casing="#D7CCC8", *_):  # I03
    W, H, dw, oh, wt, ang = d["width"], d["height"], d["door"], d["opening_height"], d["wall"], d["door_angle"]
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))

    def front(v):
        v.holed(rect_pts(-W / 2, 0, W, H), [rect_pts(-dw / 2 - 70, 0, dw + 140, oh + 70)], wall)
        v.holed(rect_pts(-dw / 2 - 70, 0, dw + 140, oh + 70), [rect_pts(-dw / 2, 0, dw, oh)], casing)
        pw = dw * c
        if pw > 5:
            v.rect(-dw / 2, 0, pw, oh, fill=door)
            v.raw(f'<circle cx="{v.X(-dw / 2 + pw - 60):.1f}" cy="{v.Y(1000):.1f}" r="3" fill="{INK}"/>')
        else:
            v.rect(-dw / 2, 0, 40, oh, fill=door)
        v.hdim(-W / 2, W / 2, H, 22, W)
        v.vdim(0, H, W / 2, 28, f"{H} потолок")
        v.vdim(0, oh, -W / 2, -28, oh)
        gx = -dw / 2 + max(pw, 40)
        v.idim(gx, oh / 2, dw / 2, oh / 2, a["width"])

    def top(v):   # x вправо, z — от пилота вверх
        for x0, x1 in ((-W / 2, -dw / 2), (dw / 2, W / 2)):
            v.rect(x0, 0, x1 - x0, wt, fill=wall)
        hx, hz = -dw / 2, wt
        ex, ez = hx + dw * c, hz + dw * s
        v.raw(f'<line x1="{v.X(hx):.1f}" y1="{v.Y(hz):.1f}" x2="{v.X(ex):.1f}" y2="{v.Y(ez):.1f}" '
              f'stroke="{INK}" stroke-width="6"/>')
        v.raw(f'<line x1="{v.X(hx):.1f}" y1="{v.Y(hz):.1f}" x2="{v.X(ex):.1f}" y2="{v.Y(ez):.1f}" '
              f'stroke="{door}" stroke-width="3"/>')
        k = v.k
        v.raw(f'<path d="M{v.P(hx + dw, hz)} A{dw * k:.1f},{dw * k:.1f} 0 0,0 {v.P(hx, hz + dw)}" fill="none" '
              f'stroke="{DIM}" stroke-width="0.8" stroke-dasharray="4 3"/>')
        v.text(hx + 60, hz + dw * 0.35, f"{ang}°", size=12, anchor="start", fill=DIM, extra=HALO)
        v.raw(f'<line x1="{v.X((ex + dw / 2) / 2 if ang < 90 else 0):.1f}" y1="{v.Y(-350):.1f}" '
              f'x2="{v.X((ex + dw / 2) / 2 if ang < 90 else 0):.1f}" y2="{v.Y(-60):.1f}" class="fl"/>')
        v.text(0, -420, "пролёт", size=11, fill=PATH)

    return spec("Вид спереди (со стороны пилота)", (-W / 2, W / 2, 0, H), front, "Вид сверху",
                (-W / 2, W / 2, -450, wt + dw), top, aux_floor=False)


def i_stairs(e, va, d, a, wood, rail="#212121", wallc="#F5F5F5", *_):  # I04
    n, r, t, Wd = d["steps"], d["riser"], d["tread"], d["width"]
    L, H, rh = d["depth"], d["height"], d["rail_height"]

    def side(v):
        pts = [(0, 0)]
        for i in range(n):
            pts += [(i * t, (i + 1) * r), ((i + 1) * t, (i + 1) * r)]
        pts += [(L, 0)]
        v.poly(pts, fill=wood)
        v.line(0, r + rh, L, H + rh, stroke=rail, sw=3)
        for i in range(n):
            x = i * t + t / 2
            v.line(x, (i + 1) * r, x, r + rh + (H - r) * x / L, stroke=rail, sw=1.2)
        route(v, f"M{v.P(-500, r + 450)} L{v.P(0, r + 450)} L{v.P(L, H + 450)} L{v.P(L + 400, H + 450)}")
        v.hdim(0, L, 0, -30, L)
        v.vdim(0, H, L, 28, H)
        v.hdim(0, t, r, 22, f"проступь {t}")
        v.vdim(0, r, 0, -28, f"подъём {r}")

    def front(v):
        v.rect(-Wd / 2 - 60, 0, 60, H + rh + 200, fill=wallc)
        for i in range(n):
            v.rect(-Wd / 2, i * r, Wd, r, fill=wood, extra=f'fill-opacity="{0.55 + 0.45 * (i % 2)}"')
        v.rect(Wd / 2 - 20, 0, 20, H + rh, fill=rail)
        v.hdim(-Wd / 2, Wd / 2, H + rh, 22, Wd)
        v.text(-Wd / 2 - 30, H + rh + 100, "стена", size=11, fill=DIM)
        v.text(Wd / 2 - 10, H + rh + 60, "перила", size=11, anchor="end", fill=DIM)

    return spec("Вид сбоку: пролёт вдоль марша", (-500, L + 400, 0, H + rh), side, "Вид снизу марша",
                (-Wd / 2 - 60, Wd / 2, 0, H + rh + 200), front)


def i_sofa(e, va, d, a, col, *_):                      # I05
    W, D, H, sh, arm, ah, bk, lg = (d["width"], d["depth"], d["height"], d["seat_height"], d["arm"],
                                    d["arm_height"], d["back"], d["legs"])

    def front(v):
        for sx in (-1, 1):
            v.rect(sx * (W / 2 - 80) - 20, 0, 40, lg, fill="#5D4037")
        v.rect(-W / 2 + arm, sh, W - 2 * arm, H - sh, fill=col, extra='fill-opacity="0.75"')
        v.rect(-W / 2, lg, W, sh - lg, fill=col)
        for sx in (-1, 1):
            v.rect(sx * (W / 2 - arm / 2) - arm / 2, lg, arm, ah - lg, fill=col)
        v.hdim(-W / 2, W / 2, H, 22, W)
        v.vdim(0, H, W / 2, 28, H)
        v.vdim(0, sh, -W / 2, -28, sh)

    def side(v):
        v.rect(-D / 2, lg, D, ah - lg, fill=col, extra='fill-opacity="0.5"')
        v.rect(-D / 2, lg, D, sh - lg, fill=col)
        v.rect(D / 2 - bk, sh, bk, H - sh, fill=col)
        v.hdim(-D / 2, D / 2, 0, -30, D)
        v.vdim(0, ah, -D / 2, -28, f"{ah} подлокотник")

    return spec("Вид спереди", (-W / 2, W / 2, 0, H), front, "Вид сбоку", (-D / 2, D / 2, 0, H), side,
                independent=False)


def i_shelf(e, va, d, a, col, *_):                     # I06
    W, H, D, bd = d["width"], d["height"], d["depth"], d["board"]
    bottoms = [int(x) for x in a["bottoms"].split(",")]
    cw, chh = a["width"], a["height"]

    def front(v):
        v.holed(rect_pts(-W / 2, 0, W, H), [rect_pts(-cw / 2, b, cw, chh) for b in bottoms], col)
        for i, b in enumerate(bottoms, 1):
            v.text(-cw / 2 + 40, b + chh - 70, i, size=15, fill="#8D6E63", extra='font-weight="bold"')
        v.hdim(-W / 2, W / 2, H, 22, W)
        v.vdim(0, H, W / 2, 28, H)
        v.idim(-cw / 2, bottoms[2] + chh / 2, cw / 2, bottoms[2] + chh / 2, cw)
        v.idim(cw / 4, bottoms[2], cw / 4, bottoms[2] + chh, chh)

    def side(v):
        v.rect(-D / 2, 0, D, H, fill=col)
        v.hdim(-D / 2, D / 2, 0, -30, D)
        v.flight(bottoms[2] + chh / 2)
        v.text(0, H + 60, "задней стенки нет", size=11, fill=DIM)

    return spec("Вид спереди: ячейки 1–5", (-W / 2, W / 2, 0, H), front, "Вид сбоку", (-D / 2, D / 2, 0, H + 80),
                side, independent=False)


def i_bed(e, va, d, a, frame, linen="#FAFAFA", *_):    # I07
    W, L, cl, fr, mt, hb = d["width"], d["depth"], d["clearance"], d["frame"], d["mattress_top"], d["headboard"]

    def front(v):
        v.rect(-W / 2, 0, W, hb, fill=frame, extra='fill-opacity="0.55"')
        for sx in (-1, 1):
            v.rect(sx * (W / 2 - 30) - 30, 0, 60, cl, fill=frame)
        v.rect(-W / 2, cl, W, fr, fill=frame)
        v.rect(-W / 2, cl + fr, W, mt - cl - fr, fill=linen)
        v.hdim(-W / 2, W / 2, hb, 22, W)
        v.vdim(0, hb, W / 2, 28, f"{hb} изголовье")
        v.idim(-a["width"] / 2, cl / 2, a["width"] / 2, cl / 2, a["width"])
        v.vdim(0, cl, -W / 2, -28, f"просвет {cl}")
        v.text(0, hb - 150, "изголовье (дальний конец)", size=11, fill="#fff")

    def side(v):
        for z in (-L / 2 + 30, L / 2 - 30):
            v.rect(z - 30, 0, 60, cl, fill=frame)
        v.rect(-L / 2, cl, L, fr, fill=frame)
        v.rect(-L / 2, cl + fr, L - 60, mt - cl - fr, fill=linen)
        v.rect(L / 2 - 60, 0, 60, hb, fill=frame)
        v.hdim(-L / 2, L / 2, 0, -30, L)
        v.vdim(0, mt, -L / 2, -28, mt)
        v.flight(cl / 2)

    return spec("Вид с изножья (вдоль пролёта)", (-W / 2, W / 2, 0, hb), front, "Вид сбоку", (-L / 2, L / 2, 0, hb),
                side)


def i_tall(e, va, d, a, col, *_):                      # I08
    W, H, D = d["width"], d["height"], d["depth"]
    fridge = "холод" in va["label"]

    def front(v):
        v.rect(-W / 2, 0, W, H, fill=col)
        if fridge:
            v.line(-W / 2, H * 0.68, W / 2, H * 0.68, stroke=INK, sw=1.2)
            v.rect(W / 2 - 60, H * 0.72, 15, 250, fill="#9e9e9e", sw=0.6)
            v.rect(W / 2 - 60, H * 0.68 - 400, 15, 300, fill="#9e9e9e", sw=0.6)
        else:
            v.line(0, 0, 0, H, stroke=INK, sw=1.2)
            for sx in (-1, 1):
                v.rect(sx * 40 - 7, H * 0.45, 14, 220, fill="#BCAAA4", sw=0.6)
        v.hdim(-W / 2, W / 2, H, 22, W)
        v.vdim(0, H, W / 2, 28, H)

    def side(v):
        v.rect(-D / 2, 0, D, H, fill=col)
        v.hdim(-D / 2, D / 2, 0, -30, D)

    return spec("Вид спереди", (-W / 2, W / 2, 0, H), front, "Вид сбоку", (-D / 2, D / 2, 0, H), side,
                independent=False)


def i_chandelier(e, va, d, a, brass, shade="#FAFAFA", *_):  # I09
    C, st, n, R, sd = d["ceiling"], d["stem"], d["arms"], d["arm_radius"], d["shade"]
    body_y = C - st - 50
    angs = [90 + 360 / n * i for i in range(n)]

    def front(v):
        v.ceiling(C)
        v.line(0, C, 0, body_y, stroke=brass, sw=3)
        for a_ in sorted(angs, key=lambda q: -math.sin(math.radians(q))):
            x = R * math.cos(math.radians(a_))
            v.line(0, body_y, x, body_y, stroke=brass, sw=2.5)
            v.poly([(x - sd / 2, body_y - sd * 1.25), (x + sd / 2, body_y - sd * 1.25), (x + sd / 4, body_y),
                    (x - sd / 4, body_y)], fill=shade)
        circle(v, 0, body_y, 75, brass)
        low = body_y - sd * 1.25
        v.hdim(-R - sd / 2, R + sd / 2, low, -26, d["width"])
        v.vdim(low, C, R + sd / 2, 28, round(C - low))
        v.text(0, low - 140, f"низ ≈ {round(low)} от пола", size=12, fill=DIM)

    def top(v):
        for a_ in angs:
            t = math.radians(a_)
            x, z = R * math.cos(t), R * math.sin(t)
            v.line(0, 0, x, z, stroke=brass, sw=2.5)
            circle(v, x, z, sd / 2, shade)
        circle(v, 0, 0, 75, brass)
        v.hdim(-R, R, -R - 80, -20, f"R{R} рожки")

    return spec("Вид спереди (под потолком)", (-R - sd / 2, R + sd / 2, body_y - sd * 1.25 - 180, C), front,
                "Вид снизу", (-R - sd / 2, R + sd / 2, -R - sd / 2, R + sd / 2), top, main_floor=False, aux_floor=False)


def i_fan(e, va, d, a, body, blade="#D7CCC8", *_):     # I10
    C, dr, nb, bl = d["ceiling"], d["downrod"], d["blades"], d["blade"]
    Rb = d["width"] / 2
    by = C - dr - 150
    mark = (f'<defs><marker id="mo" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
            f'orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{MOVE}"/></marker></defs>')

    def front(v):
        v.raw(mark)
        v.ceiling(C)
        v.rect(-750, 0, 1500, by, fill="#E3F2FD", stroke="#64B5F6", sw=1, extra='stroke-dasharray="6 4"')
        for x in (-450, 0, 450):
            v.raw(f'<line x1="{v.X(x):.1f}" y1="{v.Y(by - 200):.1f}" x2="{v.X(x):.1f}" y2="{v.Y(400):.1f}" '
                  f'stroke="#64B5F6" stroke-width="1.5" marker-end="url(#fa)"/>')
        v.text(0, 250, "зона нисходящего потока Ø1500", size=12, fill="#1565C0", extra=HALO)
        v.line(0, C, 0, by + 150, stroke=INK, sw=3)
        v.rect(-100, by, 200, 150, fill=body)
        v.rect(-Rb, by + 50, 2 * Rb, 15, fill=blade)
        v.hdim(-Rb, Rb, by + 150, 22, f"Ø{d['width']}")
        v.vdim(0, by + 50, Rb, 28, by + 50)

    def top(v):
        v.raw(f'<circle cx="{v.X(0):.1f}" cy="{v.Y(0):.1f}" r="{Rb * v.k:.1f}" fill="none" stroke="{DIM}" '
              f'stroke-dasharray="4 3"/>')
        for i in range(nb):
            t = math.radians(90 + 360 / nb * i)
            c, s = math.cos(t), math.sin(t)
            pts = [(100 * c - 50 * s, 100 * s + 50 * c), (Rb * c - 60 * s, Rb * s + 60 * c),
                   (Rb * c + 60 * s, Rb * s - 60 * c), (100 * c + 50 * s, 100 * s - 50 * c)]
            v.poly(pts, fill=blade)
        circle(v, 0, 0, 100, body)
        r = Rb + 70
        v.raw(f'<path d="M{v.P(r * math.cos(math.radians(20)), r * math.sin(math.radians(20)))} '
              f'A{r * v.k:.1f},{r * v.k:.1f} 0 0,0 {v.P(r * math.cos(math.radians(80)), r * math.sin(math.radians(80)))}" '
              f'fill="none" stroke="{MOVE}" stroke-width="2" marker-end="url(#mo)"/>')
        v.text(0, -Rb - 120, f"~150 об/мин ({e['motion']['period_s']} с/об)", size=12, fill=MOVE, extra=HALO)

    return spec("Вид спереди", (-750, 750, 0, C), front, "Вид снизу", (-Rb - 80, Rb + 80, -Rb - 160, Rb + 80), top,
                aux_floor=False)


def i_plant(e, va, d, a, leaf, pot="#A1887F", *_):     # I11
    H, P, ph, cr = d["height"], d["pot"], d["pot_height"], d["crown"]
    cy = H - cr / 2

    def crown(v, x0, y0):
        ellipse(v, x0, y0, cr / 2, cr / 2, leaf)
        for dx, dy, rr in ((-180, 100, 130), (150, 140, 120), (-60, -150, 140), (180, -90, 110), (20, 220, 110)):
            circle(v, x0 + dx, y0 + dy, rr, leaf, stroke="#1B5E20", sw=0.6, extra='fill-opacity="0.8"')

    def front(v):
        v.rect(-15, ph, 30, cy - ph, fill="#6D4C41")
        crown(v, 0, cy)
        v.poly([(-P / 2 + 40, 0), (P / 2 - 40, 0), (P / 2, ph), (-P / 2, ph)], fill=pot)
        v.hdim(-cr / 2, cr / 2, H, 22, f"крона ≈{cr}")
        v.vdim(0, H, cr / 2, 28, H)
        v.hdim(-P / 2, P / 2, 0, -30, f"горшок Ø{P}")

    def top(v):
        crown(v, 0, 0)
        circle(v, 0, 0, P / 2, "none", stroke=pot, sw=1.5, extra='stroke-dasharray="5 3"')
        v.hdim(-cr / 2, cr / 2, cr / 2, 22, f"Ø{cr}")

    return spec("Вид спереди", (-cr / 2, cr / 2, 0, H), front, "Вид сверху", (-cr / 2, cr / 2, -cr / 2, cr / 2), top,
                aux_floor=False, independent=False)


def i_boxes(e, va, d, a, col, tape="#D7B98E", *_):     # I12
    def box(v, x, y, w, h):
        v.rect(x, y, w, h, fill=col)
        v.rect(x + w / 2 - 30, y, 60, h, fill=tape, sw=0.6)

    def front(v):
        box(v, -600, 0, 600, 400)
        box(v, 0, 0, 600, 400)
        box(v, -300, 400, 600, 400)
        v.hdim(-600, 600, 0, -30, 1200)
        v.vdim(0, 800, 600, 28, 800)
        v.vdim(0, 400, -600, -28, 400)
        v.hdim(-300, 300, 800, 22, 600)

    def side(v):
        box(v, -200, 0, 400, 400)
        box(v, -200, 400, 400, 400)
        v.hdim(-200, 200, 0, -30, 400)

    return spec("Вид спереди", (-600, 600, 0, 800), front, "Вид сбоку", (-200, 200, 0, 800), side, independent=False)


def i_box_drop(e, va, d, a, col, rim="#FFFFFF", *_):   # I13
    S, wall = d["width"], d["wall"]
    sd, sc = a["side_diameter"], a["side_center_y"]

    def front(v):
        v.holed(rect_pts(-S / 2, 0, S, S), [("circle", 0, sc, sd / 2)], col)
        v.raw(f'<circle cx="{v.X(0):.1f}" cy="{v.Y(sc):.1f}" r="{sd / 2 * v.k:.1f}" fill="none" stroke="{INK}" '
              f'stroke-width="5"/><circle cx="{v.X(0):.1f}" cy="{v.Y(sc):.1f}" r="{sd / 2 * v.k:.1f}" fill="none" '
              f'stroke="{rim}" stroke-width="3"/>')
        v.rect(-S / 2, S - 15, S, 15, fill="#8D6E63", sw=0.6)
        v.text(0, S + 40, "верх открыт", size=11, fill=DIM)
        v.hdim(-S / 2, S / 2, 0, -30, S)
        v.vdim(0, S, S / 2, 28, S)
        v.idim(-sd / 2, sc, sd / 2, sc, f"Ø{sd}")
        v.vdim(0, sc, -S / 2, -28, sc)

    def side(v):   # разрез: передняя стенка слева (z = −S/2), пилот слева
        v.rect(-S / 2, 0, S, wall, fill=col)
        v.rect(S / 2 - wall, 0, wall, S, fill=col)
        v.rect(-S / 2, 0, wall, sc - sd / 2, fill=col)
        v.rect(-S / 2, sc + sd / 2, wall, S - sc - sd / 2, fill=col)
        k = v.k
        route(v, f"M{v.P(0, S + 500)} L{v.P(0, sc + 150)} Q{v.P(0, sc)} {v.P(-150, sc)} L{v.P(-S / 2 - 500, sc)}")
        v.text(60, S + 400, "нырок", size=11, anchor="start", fill=PATH)
        v.text(-S / 2 - 400, sc + 50, "выход", size=11, fill=PATH)
        v.hdim(-S / 2, S / 2, 0, -30, S)

    return spec("Вид спереди", (-S / 2, S / 2, 0, S + 60), front, "Разрез сбоку: нырок",
                (-S / 2 - 500, S / 2, 0, S + 500), side)


BUILDERS = {"I01": i_table, "I02": i_chair, "I03": i_doorway, "I04": i_stairs, "I05": i_sofa, "I06": i_shelf,
            "I07": i_bed, "I08": i_tall, "I09": i_chandelier, "I10": i_fan, "I11": i_plant, "I12": i_boxes,
            "I13": i_box_drop}

if __name__ == "__main__":
    run("07-interior", BUILDERS, set(BUILDERS))
