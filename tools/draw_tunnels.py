"""SVG-чертежи категории 02-tunnels (тоннели).

Запуск:  python tools/draw_tunnels.py          — все тоннели
         python tools/draw_tunnels.py T01 T07  — выбранные элементы

Основной вид — сбоку (у изогнутых и разветвлённых — сверху), пролёт слева направо.
Вспомогательный — вид на вход (или разрез).
"""
import math

from drawlib import DIM, INK, rect_pts, run

WIRE = "#00000040"


def spec(main_title, main_ext, main_draw, aux_title, aux_ext, aux_draw, main_floor=True, aux_floor=True):
    return {"main": dict(title=main_title, ext=main_ext, floor=main_floor, draw=main_draw),
            "aux": dict(title=aux_title, ext=aux_ext, floor=aux_floor, draw=aux_draw)}


def tube_side(v, z0, L, D, col, pitch, accent=None, y0=0):
    """Горизонтальная труба на виде сбоку: тело, тень цилиндра, витки проволоки, окантовка торцов."""
    v.rect(z0, y0, L, D, fill=col)
    v.rect(z0, y0, L, D, fill="url(#cylv)", stroke="none")
    z = z0 + pitch
    while z < z0 + L - 1:
        v.line(z, y0, z, y0 + D, stroke=WIRE, sw=1)
        z += pitch
    if accent:
        v.rect(z0, y0, 15, D, fill=accent)
        v.rect(z0 + L - 15, y0, 15, D, fill=accent)
    v.rect(z0, y0, L, D, fill="none")


def entrance(v, D, Din, col, accent=None, bottom=0):
    """Вид на круглый вход тоннеля, лежащего на полу."""
    cy = bottom + D / 2
    v.raw(f'<circle cx="{v.X(0):.1f}" cy="{v.Y(cy):.1f}" r="{Din / 2 * v.k:.1f}" fill="#fff"/>')
    v.raw(f'<circle cx="{v.X(0):.1f}" cy="{v.Y(cy):.1f}" r="{Din / 2 * v.k:.1f}" fill="{col}" '
          f'fill-opacity="0.18" stroke="none"/>')
    v.holed(("circle", 0, cy, D / 2), [("circle", 0, cy, Din / 2)], accent or col)
    v.hdim(-D / 2, D / 2, bottom, -30, f"Ø{D}")
    v.idim(-Din / 2, cy, Din / 2, cy, f"Ø{Din}")


# ---------------------------------------------------------------- элементы
def t_straight(e, va, d, a, col, accent=None, *_):        # T01, T03
    L, D, Din = d["depth"], d["diameter"], a["diameter"]
    pitch = d.get("wire_pitch") or d.get("rib_pitch")

    def side(v):
        tube_side(v, 0, L, D, col, pitch, accent)
        v.hdim(0, L, D, 22, L)
        v.vdim(0, D, L, 28, D)
        v.hdim(0, pitch, 0, -30, f"шаг {pitch}")
        v.flight(D / 2)

    def front(v):
        entrance(v, D, Din, col, accent)
        v.vdim(0, D, D / 2, 28, D)

    return spec("Вид сбоку", (0, L, 0, D), side, "Вид на вход", (-D / 2, D / 2, 0, D), front)


def t_curved(e, va, d, a, col, accent=None, *_):          # T02 — вид сверху: u = z (вправо), w = x (вверх — влево)
    R, D = d["bend_radius"], d["diameter"]
    r1, r2 = R - D / 2, R + D / 2
    cx, cy = 0, -R

    def top(v):
        k = v.k
        p = (f"M{v.P(0, cy + r2)} A{r2 * k:.1f},{r2 * k:.1f} 0 0,1 {v.P(r2, cy)} "
             f"L{v.P(r1, cy)} A{r1 * k:.1f},{r1 * k:.1f} 0 0,0 {v.P(0, cy + r1)} Z")
        v.raw(f'<path d="{p}" fill="{col}" stroke="{INK}" stroke-width="1.2"/>')
        n = int(R * math.pi / 2 // 150)
        for i in range(1, n + 1):
            t = i * 150 / R
            c, s = math.cos(math.pi / 2 - t), math.sin(math.pi / 2 - t)
            v.line(cx + r1 * c, cy + r1 * s, cx + r2 * c, cy + r2 * s, stroke=WIRE, sw=1)
        if accent:
            v.line(0, cy + r1, 0, cy + r2, stroke=accent, sw=4)
            v.line(r1, cy, r2, cy, stroke=accent, sw=4)
        v.raw(f'<path d="M{v.P(0, 0)} A{R * k:.1f},{R * k:.1f} 0 0,1 {v.P(R, cy)}" fill="none" '
              f'stroke="{DIM}" stroke-width="0.8" stroke-dasharray="6 4"/>')
        v.line(-15, cy, 15, cy, stroke=DIM, sw=0.8)
        v.line(0, cy - 15, 0, cy + 15, stroke=DIM, sw=0.8)
        v.idim(0, cy, R * math.cos(math.radians(40)), cy + R * math.sin(math.radians(40)), f"R{R} по оси")
        v.hdim(0, r2, cy + r2, 22, d["depth"])
        v.vdim(cy, cy + r2, r2, 28, d["width"])
        v.flight(0)
        v.arrow_px(R, cy, 0, 46)

    def front(v):
        entrance(v, D, a["diameter"], col, accent)
        v.vdim(0, D, D / 2, 28, D)

    return spec("Вид сверху", (0, r2, cy, cy + r2), top, "Вид на вход", (-D / 2, D / 2, 0, D), front,
                main_floor=False)


def t_frames(e, va, d, a, col, accent=None, *_):          # T04
    L, Hh, f, step = d["depth"], d["height"], d["frame"], d["frame_step"]
    accent = accent or "#FFD600"

    def side(v):
        v.rect(0, 0, L, Hh, fill=col)
        for i in range(d["frames"]):
            z = i * step
            last = i in (0, d["frames"] - 1)
            v.rect(z, 0, f, Hh, fill=accent if last else "#9e9e9e")
        v.hdim(0, L, Hh, 22, L)
        v.vdim(0, Hh, L, 28, Hh)
        v.hdim(0, step, 0, -30, f"шаг {step}")
        v.flight(Hh / 2)

    def front(v):
        w = d["width"]
        v.holed(rect_pts(-w / 2, 0, w, Hh), [rect_pts(-a["width"] / 2, 0, a["width"], a["height"])], accent)
        v.hdim(-w / 2, w / 2, Hh, 22, w)
        v.vdim(0, Hh, w / 2, 28, Hh)
        v.idim(-a["width"] / 2, a["height"] * 0.6, a["width"] / 2, a["height"] * 0.6, a["width"])
        v.idim(-a["width"] * 0.25, 0, -a["width"] * 0.25, a["height"], a["height"])
        v.text(0, 15, "пол открыт", size=11, fill=DIM)

    return spec("Вид сбоку", (0, L, 0, Hh), side, "Вид на вход", (-d["width"] / 2, d["width"] / 2, 0, Hh), front)


def t_rings(e, va, d, a, col, col2="#F5F5F5", *_):        # T05
    n, step, D, b = d["rings"], d["step"], d["diameter"], d["band"]
    Hh, L = d["height"], d["depth"]

    def side(v):
        for i in range(n):
            z = 50 + i * step
            v.rect(z - 50, 0, 100, 25, fill="#9e9e9e")
            v.rect(z - 4, 20, 8, D, fill=col if i % 2 == 0 else col2)
        v.hdim(50, 50 + step, Hh, 22, step)
        v.hdim(0, L, 0, -30, L)
        v.vdim(0, Hh, L, 28, Hh)
        v.flight(20 + D / 2)

    def front(v):
        cy = 20 + D / 2
        v.rect(-80, 0, 160, 25, fill="#9e9e9e")
        v.holed(("circle", 0, cy, D / 2), [("circle", 0, cy, D / 2 - b)], col)
        v.hdim(-D / 2, D / 2, Hh, 22, f"Ø{D}")
        v.idim(-(D / 2 - b), cy, D / 2 - b, cy, f"Ø{a['diameter']}")
        v.vdim(0, a["bottom"], -D / 2, -28, a["bottom"])

    return spec("Вид сбоку", (0, L, 0, Hh), side, "Вид на вход", (-D / 2, D / 2, 0, Hh), front)


def t_boxes(e, va, d, a, col, tape="#D7B98E", *_):         # T06
    L, Hh, bl, w = d["depth"], d["height"], d["box_length"], d["width"]

    def side(v):
        for i in range(d["boxes"]):
            v.rect(i * bl, 0, bl, Hh, fill=col)
            v.line(i * bl + 20, Hh - 40, i * bl + bl - 20, Hh - 40, stroke="#00000030", sw=1)
        for i in range(1, d["boxes"]):
            v.rect(i * bl - 30, 0, 60, Hh, fill=tape, stroke="#00000050", sw=0.8)
        v.hdim(0, L, Hh, 22, L)
        v.vdim(0, Hh, L, 28, Hh)
        v.hdim(0, bl, 0, -30, f"коробка {bl}")
        v.flight(Hh / 2)

    def front(v):
        wall = d["wall"]
        v.rect(-w / 2 + wall, wall, w - 2 * wall, Hh - 2 * wall, fill=col, stroke="none", extra='fill-opacity="0.25"')
        v.holed(rect_pts(-w / 2, 0, w, Hh), [rect_pts(-w / 2 + wall, wall, w - 2 * wall, Hh - 2 * wall)], col,
                sw=2.5)
        v.hdim(-w / 2, w / 2, Hh, 22, w)
        v.vdim(0, Hh, w / 2, 28, Hh)
        v.idim(-a["width"] / 2, Hh * 0.55, a["width"] / 2, Hh * 0.55, a["width"])
        v.text(0, Hh * 0.3, f"стенка {wall}", size=11, fill=DIM)

    return spec("Вид сбоку", (0, L, 0, Hh), side, "Вид на вход", (-w / 2, w / 2, 0, Hh), front)


def t_l_up(e, va, d, a, col, accent=None, *_):             # T07
    D, Lh, R, Lv = d["diameter"], d["horizontal_length"], d["bend_radius"], d["vertical_length"]
    yc = D / 2
    zb, yb = Lh + R, yc + R            # конец изгиба (ось вертикального участка)
    top = yb + Lv
    depth = d["depth"]

    def side(v):
        k = v.k
        # стойка за тоннелем
        v.rect(depth - 100, 0, 100, 15, fill="#555")
        v.rect(depth - 30, 0, 20, top, fill="#333")
        for y in (yb + 120, top - 120):
            v.rect(zb + D / 2, y, depth - 30 - zb - D / 2, 20, fill="#777")
        path = (f"M{v.P(0, yc)} L{v.P(Lh, yc)} A{R * k:.1f},{R * k:.1f} 0 0,0 {v.P(zb, yb)} L{v.P(zb, top)}")
        v.raw(f'<path d="{path}" fill="none" stroke="{INK}" stroke-width="{D * k + 2.4:.1f}"/>')
        v.raw(f'<path d="{path}" fill="none" stroke="{col}" stroke-width="{D * k:.1f}"/>')
        for z in range(150, Lh, 150):
            v.line(z, 0, z, D, stroke=WIRE, sw=1)
        for y in range(int(yb) + 150, int(top), 150):
            v.line(zb - D / 2, y, zb + D / 2, y, stroke=WIRE, sw=1)
        for i in range(1, 5):
            t = math.radians(18 * i)
            cz, cyy = Lh, yb
            v.line(cz + (R - D / 2) * math.sin(t), cyy - (R - D / 2) * math.cos(t),
                   cz + (R + D / 2) * math.sin(t), cyy - (R + D / 2) * math.cos(t), stroke=WIRE, sw=1)
        if accent:
            v.rect(0, 0, 15, D, fill=accent)
            v.rect(zb - D / 2, top - 15, D, 15, fill=accent)
        v.line(Lh - 12, yb, Lh + 12, yb, stroke=DIM, sw=0.8)
        v.line(Lh, yb - 12, Lh, yb + 12, stroke=DIM, sw=0.8)
        v.text(Lh - 20, yb + 20, f"R{R}", size=12, anchor="end", fill=DIM)
        v.hdim(0, Lh, 0, -30, Lh)
        v.hdim(0, depth, 0, -62, depth)
        v.vdim(0, top, depth, 28, f"{int(top)} выход")
        v.flight(yc)
        v.arrow_px(zb, top, 0, -50)

    def front(v):
        v.rect(-D / 2, yc, D, top - yc, fill=col)
        v.rect(-D / 2, yc, D, top - yc, fill="url(#cylh)", stroke="none")
        entrance(v, D, a["diameter"], col, accent)
        v.vdim(0, top, D / 2, 28, int(top))

    return spec("Вид сбоку", (0, depth, 0, top), side, "Вид на вход", (-D / 2, D / 2, 0, top), front)


def t_fork(e, va, d, a, col, cl="#E53935", cr="#43A047", *_):   # T08 — вид сверху, слева от пилота = вверх
    D, Lt, Lb = d["diameter"], d["trunk_length"], d["branch_length"]
    ang = math.radians(d["branch_angle"])
    ex, ey = Lt + Lb * math.cos(ang), Lb * math.sin(ang)
    U, Wd = d["depth"], d["width"]

    def top(v):
        k = v.k
        sw = D * k
        full = f"M{v.P(0, 0)} L{v.P(Lt, 0)} L{v.P(ex, ey)} M{v.P(Lt, 0)} L{v.P(ex, -ey)}"
        v.raw(f'<path d="{full}" fill="none" stroke="{INK}" stroke-width="{sw + 2.4:.1f}" stroke-linejoin="round"/>')
        for (x1, y1, x2, y2, c) in [(Lt, 0, ex, ey, cl), (Lt, 0, ex, -ey, cr)]:
            v.raw(f'<line x1="{v.X(x1):.1f}" y1="{v.Y(y1):.1f}" x2="{v.X(x2):.1f}" y2="{v.Y(y2):.1f}" '
                  f'stroke="{c}" stroke-width="{sw:.1f}" stroke-linecap="butt"/>')
        v.raw(f'<line x1="{v.X(0):.1f}" y1="{v.Y(0):.1f}" x2="{v.X(Lt):.1f}" y2="{v.Y(0):.1f}" '
              f'stroke="{col}" stroke-width="{sw:.1f}"/>')
        apex = Lt + (D / 2) / math.sin(ang)          # где расходятся внутренние стенки ветвей
        v.poly([(Lt, D / 2), (apex, 0), (Lt, -D / 2)], fill=col, stroke=INK, sw=0.8)
        v.raw(f'<circle cx="{v.X(apex):.1f}" cy="{v.Y(0):.1f}" r="3.5" fill="{INK}"/>')
        v.text(apex + 40, -110, "перегородка", size=11, anchor="start", fill=DIM)
        v.line(Lt, 0, Lt + 600, 0, stroke=DIM, sw=0.8, extra='stroke-dasharray="6 4"')
        r = 500
        v.raw(f'<path d="M{v.P(Lt + r, 0)} A{r * k:.1f},{r * k:.1f} 0 0,0 '
              f'{v.P(Lt + r * math.cos(ang), r * math.sin(ang))}" fill="none" class="dim"/>')
        v.text(Lt + r + 50, r * math.sin(ang) / 2 - 20, f"{d['branch_angle']}°", size=12, anchor="start", fill=DIM)
        v.text(ex + 40, ey + 40, "левая", size=12, anchor="start", fill=cl, extra='font-weight="bold"')
        v.text(ex + 40, -ey - 70, "правая", size=12, anchor="start", fill=cr, extra='font-weight="bold"')
        v.hdim(0, U, Wd / 2, 22, U)
        v.vdim(-Wd / 2, Wd / 2, U, 28, Wd)
        v.hdim(0, Lt, -D / 2, -30, f"вход {Lt}")
        v.flight(0)

    def front(v):
        entrance(v, D, a["diameter"], col)
        v.vdim(0, D, D / 2, 28, D)

    return spec("Вид сверху", (0, U, -Wd / 2, Wd / 2), top, "Вид на вход", (-D / 2, D / 2, 0, D), front,
                main_floor=False)


def t_windows(e, va, d, a, col, rim="#FFFFFF", *_):          # T09
    L, D, Din = d["depth"], d["diameter"], a["diameter"]
    wd = a["window_diameter"]
    zs = [int(z) for z in str(a["window_centers_z"]).split(",")]
    wy = a["window_center_y"]

    def side(v):
        tube_side(v, 0, L, D, col, d["wire_pitch"], "#FFC400")
        for z in zs:
            v.raw(f'<circle cx="{v.X(z):.1f}" cy="{v.Y(wy):.1f}" r="{wd / 2 * v.k:.1f}" fill="#fff" '
                  f'stroke="{INK}" stroke-width="1.2"/>')
            v.raw(f'<circle cx="{v.X(z):.1f}" cy="{v.Y(wy):.1f}" r="{wd / 2 * v.k - 2:.1f}" fill="none" '
                  f'stroke="{rim if rim.lower() != "#ffffff" else "#BDBDBD"}" stroke-width="3"/>')
        v.hdim(0, L, D, 22, L)
        v.vdim(0, D, L, 28, D)
        v.hdim(0, zs[0], 0, -30, zs[0])
        v.hdim(zs[0], zs[1], 0, -30, zs[1] - zs[0])
        v.idim(zs[1] - wd / 2, wy, zs[1] + wd / 2, wy, f"Ø{wd}")
        v.flight(D / 2)

    def cut(v):
        cy, r = D / 2, D / 2 - 2.5
        al = math.asin((wd / 2) / r)
        rk = r * v.k
        def pt(t): return v.P(r * math.cos(t), cy + r * math.sin(t))
        for t1, t2 in [(al, math.pi - al), (math.pi + al, 2 * math.pi - al)]:
            v.raw(f'<path d="M{pt(t1)} A{rk:.1f},{rk:.1f} 0 0,0 {pt(t2)}" fill="none" stroke="{INK}" '
                  f'stroke-width="5"/>')
            v.raw(f'<path d="M{pt(t1)} A{rk:.1f},{rk:.1f} 0 0,0 {pt(t2)}" fill="none" stroke="{col}" '
                  f'stroke-width="3"/>')
        v.vdim(wy - wd / 2, wy + wd / 2, -D / 2, -28, f"окно Ø{wd}")
        v.hdim(-D / 2, D / 2, 0, -30, f"Ø{D}")
        v.arrow_px(0, wy, 95, 0, "выход")

    return spec("Вид сбоку", (0, L, 0, D), side, "Разрез по окнам", (-D / 2, D / 2, 0, D), cut)


BUILDERS = {
    "T01": t_straight, "T02": t_curved, "T03": t_straight, "T04": t_frames, "T05": t_rings,
    "T06": t_boxes, "T07": t_l_up, "T08": t_fork, "T09": t_windows,
}
ALL_COLORS = set(BUILDERS)

if __name__ == "__main__":
    run("02-tunnels", BUILDERS, ALL_COLORS)
