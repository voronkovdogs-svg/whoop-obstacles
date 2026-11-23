"""SVG-чертежи категории 01-gates (ворота).

Запуск:  python tools/draw_gates.py          — все ворота
         python tools/draw_gates.py G01 G05  — выбранные элементы

Каждый чертёж: вид спереди + вид сбоку (у G10 — вид сверху), размеры в мм.
Направление пролёта — слева направо на виде сбоку (ось Z).
"""
import math

from drawlib import DIM, INK, S3, rect_pts, reg_poly, run, thin_side


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


def g_eight(e, va, d, a, col, col2=INK, *_):   # G12
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


def g_keyhole(e, va, d, a, col, col2=INK, *_):  # G14
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


def g_banner(e, va, d, a, col, col2=INK, *_):  # G16
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




if __name__ == "__main__":
    run("01-gates", BUILDERS, TWO_COLOR)
