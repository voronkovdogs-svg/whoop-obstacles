"""SVG-чертежи категории 06-dynamic (подвижные препятствия).

Запуск:  python tools/draw_dynamic.py          — все элементы
         python tools/draw_dynamic.py D01      — выбранные

Крайние положения движущихся частей нарисованы бледным пунктиром,
движение — оранжевой стрелкой.
"""
import math

from drawlib import DIM, INK, rect_pts, run

MOVE = "#EF6C00"
GHOST = 'opacity="0.35" stroke-dasharray="5 4"'
MARK = (f'<defs><marker id="mo" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
        f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{MOVE}"/></marker></defs>')


def spec(main_title, main_ext, main_draw, aux_title, aux_ext, aux_draw, main_floor=True, aux_floor=True,
         independent=True):
    return {"main": dict(title=main_title, ext=main_ext, floor=main_floor, draw=main_draw),
            "aux": dict(title=aux_title, ext=aux_ext, floor=aux_floor, draw=aux_draw), "independent": independent}


def arc_arrow(v, cx, cy, r, a1, a2, both=True, label=None):
    """Оранжевая дуга движения от угла a1 до a2 (градусы, от +x против часовой)."""
    k = v.k
    p1 = (cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1)))
    p2 = (cx + r * math.cos(math.radians(a2)), cy + r * math.sin(math.radians(a2)))
    large = 1 if abs(a2 - a1) > 180 else 0
    sweep = 0 if a2 > a1 else 1
    v.raw(f'<path d="M{v.P(*p1)} A{r * k:.1f},{r * k:.1f} 0 {large},{sweep} {v.P(*p2)}" fill="none" '
          f'stroke="{MOVE}" stroke-width="2" marker-end="url(#mo)" {"marker-start=\"url(#mo)\"" if both else ""}/>')
    if label:
        am = math.radians((a1 + a2) / 2)
        v.text(cx + (r + 60) * math.cos(am), cy + (r + 60) * math.sin(am), label, size=12, fill=MOVE,
               extra='font-weight="bold" paint-order="stroke" stroke="#fff" stroke-width="3"')


def line_arrow(v, x1, y1, x2, y2, label=None):
    v.raw(f'<line x1="{v.X(x1):.1f}" y1="{v.Y(y1):.1f}" x2="{v.X(x2):.1f}" y2="{v.Y(y2):.1f}" stroke="{MOVE}" '
          f'stroke-width="2" marker-start="url(#mo)" marker-end="url(#mo)"/>')
    if label:
        v.text((x1 + x2) / 2, (y1 + y2) / 2 + 30, label, size=12, fill=MOVE,
               extra='font-weight="bold" paint-order="stroke" stroke="#fff" stroke-width="3"')


def circle(v, x, y, r, fill, stroke=INK, sw=1.2, extra=""):
    v.raw(f'<circle cx="{v.X(x):.1f}" cy="{v.Y(y):.1f}" r="{max(r * v.k, 2):.1f}" fill="{fill}" '
          f'stroke="{stroke}" stroke-width="{sw}" {extra}/>')


def ring(v, cx, cy, outer, band, col, sx=1.0, extra=""):
    R, r = outer / 2, outer / 2 - band
    k = v.k
    X, Y = v.X(cx), v.Y(cy)
    rx1, rx2 = max(R * k * sx, 1.5), max(r * k * sx, 0.1)
    d = (f"M{X - rx1:.1f},{Y:.1f} a{rx1:.1f},{R * k:.1f} 0 1,0 {2 * rx1:.1f},0 a{rx1:.1f},{R * k:.1f} 0 1,0 {-2 * rx1:.1f},0 Z "
         f"M{X - rx2:.1f},{Y:.1f} a{rx2:.1f},{r * k:.1f} 0 1,0 {2 * rx2:.1f},0 a{rx2:.1f},{r * k:.1f} 0 1,0 {-2 * rx2:.1f},0 Z")
    v.raw(f'<path d="{d}" fill="{col}" fill-rule="evenodd" stroke="{INK}" stroke-width="1.2" {extra}/>')


# ---------------------------------------------------------------- элементы
def d_rotating(e, va, d, a, col, base="#212121", *_):    # D01
    g, b, lo = d["gate"], d["band"], d["lower_edge"]
    H = d["height"]

    def front(v):
        v.raw(MARK)
        v.rect(-125, 0, 250, 120, fill=base)
        v.rect(-12.5, 120, 25, lo - 120, fill="#9e9e9e")
        c = math.cos(math.radians(60))
        v.out.append(f'<g {GHOST}>')
        v.holed(rect_pts(-g / 2 * c, lo, g * c, g), [rect_pts(-(g / 2 - b) * c, lo + b, (g - 2 * b) * c, g - 2 * b)], col)
        v.out.append('</g>')
        v.holed(rect_pts(-g / 2, lo, g, g), [rect_pts(-g / 2 + b, lo + b, g - 2 * b, g - 2 * b)], col)
        v.line(0, 0, 0, H + 80, stroke=DIM, sw=0.8, extra='stroke-dasharray="10 4 2 4"')
        v.raw(f'<ellipse cx="{v.X(0):.1f}" cy="{v.Y(H + 40):.1f}" rx="{g / 2 * v.k:.1f}" ry="{12:.1f}" fill="none" '
              f'stroke="{MOVE}" stroke-width="2" marker-end="url(#mo)"/>')
        v.text(0, H + 110, f"{d['sweep_diameter']} — круг вращения, {e['motion']['period_s']} с/оборот", size=12,
               fill=MOVE, extra='font-weight="bold"')
        v.hdim(-g / 2, g / 2, lo, -24, g)
        v.vdim(0, H, g / 2, 28, H)
        v.vdim(0, lo, -g / 2, -28, lo)
        v.idim(-g / 2 + b, lo + g / 2, g / 2 - b, lo + g / 2, g - 2 * b)

    def top(v):   # вид сверху: x вправо, z вверх (полёт снизу вверх)
        R = g / 2
        for a0 in (0, 180):   # ворота почти анфас (их линия в пределах ±30° от оси x) — можно проходить
            p1 = (R * math.cos(math.radians(a0 - 30)), R * math.sin(math.radians(a0 - 30)))
            p2 = (R * math.cos(math.radians(a0 + 30)), R * math.sin(math.radians(a0 + 30)))
            v.raw(f'<path d="M{v.P(0, 0)} L{v.P(*p1)} A{R * v.k:.1f},{R * v.k:.1f} 0 0,0 {v.P(*p2)} Z" '
                  f'fill="#C8E6C9" stroke="none"/>')
        circle(v, 0, 0, R, "none", stroke=DIM, sw=0.8, extra='stroke-dasharray="4 3"')
        for ang, op in ((45, 0.35), (90, 0.35)):
            t = math.radians(ang)
            v.raw(f'<line x1="{v.X(-R * math.cos(t)):.1f}" y1="{v.Y(-R * math.sin(t)):.1f}" '
                  f'x2="{v.X(R * math.cos(t)):.1f}" y2="{v.Y(R * math.sin(t)):.1f}" stroke="{col}" stroke-width="5" '
                  f'opacity="{op}"/>')
        v.raw(f'<line x1="{v.X(-R):.1f}" y1="{v.Y(0):.1f}" x2="{v.X(R):.1f}" y2="{v.Y(0):.1f}" stroke="{INK}" stroke-width="8"/>')
        v.raw(f'<line x1="{v.X(-R):.1f}" y1="{v.Y(0):.1f}" x2="{v.X(R):.1f}" y2="{v.Y(0):.1f}" stroke="{col}" stroke-width="5"/>')
        arc_arrow(v, 0, 0, R + 60, 20, 70, both=False)
        v.raw(f'<line x1="{v.X(0):.1f}" y1="{v.Y(-R - 220):.1f}" x2="{v.X(0):.1f}" y2="{v.Y(-R - 40):.1f}" class="fl"/>')
        v.text(0, -R - 260, "пролёт", size=11, fill="#2E7D32")
        v.text(0, R + 130, "зелёное — положения ворот, когда можно проходить (±30°)", size=11, fill="#2E7D32")

    return spec("Вид спереди (бледно — поворот 60°)", (-g / 2, g / 2, 0, H + 120), front, "Вид сверху",
                (-g / 2 - 60, g / 2 + 60, -g / 2 - 260, g / 2 + 140), top, aux_floor=False)


def d_pendulum(e, va, d, a, frame, ball="#FF5722", *_):   # D02
    H, span, L, bd, bb = d["height"], d["span"], d["rod"], d["ball"], d["ball_bottom"]
    piv = H - 20
    lr = piv - (bb + bd / 2)                    # длина до центра шара
    amp = 25

    def bob(v, ang, extra=""):
        t = math.radians(ang)
        x, y = lr * math.sin(t), piv - lr * math.cos(t)
        v.raw(f'<line x1="{v.X(0):.1f}" y1="{v.Y(piv):.1f}" x2="{v.X(x):.1f}" y2="{v.Y(y):.1f}" stroke="{INK}" '
              f'stroke-width="2" {extra}/>')
        circle(v, x, y, bd / 2, ball, extra=extra)

    def front(v):
        v.raw(MARK)
        for sx in (-1, 1):
            v.rect(sx * span / 2 - 20, 0, 40, H, fill=frame)
            v.rect(sx * span / 2 - 50, 0, 100, 15, fill="#616161")
        v.rect(-span / 2 - 20, H - 40, span + 40, 40, fill=frame)
        for ang in (-amp, amp):
            bob(v, ang, GHOST)
        bob(v, 0)
        arc_arrow(v, 0, piv, lr + bd / 2 + 60, -90 - amp, -90 + amp, label=f"±{amp}°, {e['motion']['period_s']} с")
        v.hdim(-span / 2 - 20, span / 2 + 20, H, 22, d["width"])
        v.vdim(0, H, span / 2 + 20, 28, H)
        v.vdim(0, bb, -span / 2 - 20, -28, f"{bb} низ шара")
        v.idim(bd / 2 + 20, piv, bd / 2 + 20, piv - L, f"штанга {L}", side=-1)
        v.text(0, bb + bd / 2 - 12, f"Ø{bd}", size=11, fill="#fff", extra='font-weight="bold"')

    def side(v):
        v.rect(-250, 0, 500, 15, fill="#616161")
        v.rect(-20, 15, 40, H - 15, fill=frame)
        v.line(0, piv, 0, bb + bd / 2, stroke=INK, sw=2)
        circle(v, 0, bb + bd / 2, bd / 2, ball)
        v.hdim(-250, 250, 0, -30, 500)
        v.flight(bb + bd / 2)

    return spec("Вид спереди: качание поперёк полёта", (-span / 2 - 20, span / 2 + 20, 0, H), front, "Вид сбоку",
                (-250, 250, 0, H), side)


def d_shutter(e, va, d, a, frame, door="#E53935", trim="#FFD600", *_):  # D03
    F, pr, dw, tr = d["frame"], d["profile"], d["door"], d["travel"]
    lo = 100
    W = d["width"]
    rail_r = F / 2 + 500

    def door_rect(v, x0, extra=""):
        v.rect(x0 - dw / 2, lo + pr - 10, dw, dw, fill=door, extra=extra)
        v.rect(x0 - dw / 2 + 15, lo + pr + 5, dw - 30, dw - 30, fill="none", stroke=trim, sw=3, extra=extra)

    def front(v):
        v.raw(MARK)
        v.rect(-F / 2, 0, 60, lo, fill="#9e9e9e")
        v.rect(F / 2 - 60, 0, 60, lo, fill="#9e9e9e")
        v.holed(rect_pts(-F / 2, lo, F, F), [rect_pts(-F / 2 + pr, lo + pr, F - 2 * pr, F - 2 * pr)], frame, sw=1.4)
        v.rect(-F / 2, lo + F, F / 2 + rail_r, 20, fill="#757575")
        door_rect(v, tr, GHOST)
        door_rect(v, 0)
        line_arrow(v, 0, lo + F + 90, tr, lo + F + 90, f"ход {tr}")
        cyc = e["motion"].get("cycle", "")
        v.text((rail_r - F / 2) / 2, -110, f"цикл {e['motion']['period_s']} с: {cyc}", size=11, fill=MOVE)
        v.hdim(-F / 2, rail_r, 0, -30, W)
        v.vdim(0, lo + F, F / 2, 28, d["height"])
        v.vdim(0, a["bottom"], -F / 2, -28, a["bottom"])
        v.idim(-F / 2 + pr, lo + pr - 40, F / 2 - pr, lo + pr - 40, a["width"], side=-1)

    def side(v):
        v.rect(-150, 0, 300, 15, fill="#9e9e9e")
        v.rect(-10, lo, 20, F, fill=frame)
        v.rect(12, lo + pr - 10, 8, dw, fill=door)
        v.hdim(-150, 150, 0, -30, 300)
        v.flight(lo + F / 2)

    return spec("Вид спереди (бледно — дверь открыта)", (-F / 2, rail_r, -130, lo + F + 120), front, "Вид сбоку",
                (-150, 150, 0, lo + F + 120), side)


def d_swinging(e, va, d, a, col, *_):                   # D04
    D, b, piv, c0 = d["diameter"], d["band"], d["pivot"], d["center_rest"]
    L = piv - c0
    amp = 20

    def side(v):   # качание вдоль полёта: z вправо
        v.raw(MARK)
        v.ceiling(piv)
        for ang, extra in ((-amp, GHOST), (amp, GHOST), (0, "")):
            t = math.radians(ang)
            cz, cy = L * math.sin(t), piv - L * math.cos(t)
            top = (cz - (D / 2) * math.sin(t), cy + (D / 2) * math.cos(t))
            v.raw(f'<line x1="{v.X(0):.1f}" y1="{v.Y(piv):.1f}" x2="{v.X(top[0]):.1f}" y2="{v.Y(top[1]):.1f}" '
                  f'stroke="#777" stroke-width="1" {extra}/>')
            dz, dy = (D / 2) * math.sin(t), (D / 2) * math.cos(t)
            v.raw(f'<line x1="{v.X(cz - dz):.1f}" y1="{v.Y(cy + dy):.1f}" x2="{v.X(cz + dz):.1f}" y2="{v.Y(cy - dy):.1f}" '
                  f'stroke="{INK}" stroke-width="7" {extra}/>')
            v.raw(f'<line x1="{v.X(cz - dz):.1f}" y1="{v.Y(cy + dy):.1f}" x2="{v.X(cz + dz):.1f}" y2="{v.Y(cy - dy):.1f}" '
                  f'stroke="{col}" stroke-width="4" {extra}/>')
        arc_arrow(v, 0, piv, L + D / 2 + 60, -90 - amp, -90 + amp, label=f"±{amp}°, {e['motion']['period_s']} с")
        v.vdim(0, piv, 700, 20, f"{piv} подвес")
        v.vdim(0, c0, -700, -20, f"{c0} центр в покое")
        v.flight(c0)

    def front(v):
        v.ceiling(piv)
        cy = c0
        ax = (D / 2) * math.sin(math.radians(60))
        ay = cy + (D / 2) * math.cos(math.radians(60))
        for sx in (-1, 1):
            v.line(sx * ax, ay, sx * ax, piv, stroke="#777", sw=1)
        ring(v, 0, cy, D, b, col)
        v.hdim(-D / 2, D / 2, cy - D / 2, -24, f"Ø{D}")
        v.idim(-(D / 2 - b), cy, D / 2 - b, cy, f"Ø{D - 2 * b}")

    return spec("Вид сбоку: качание вдоль полёта", (-700, 700, 0, piv), side, "Вид спереди (в покое)",
                (-D / 2, D / 2, 0, piv), front, independent=False)


BUILDERS = {"D01": d_rotating, "D02": d_pendulum, "D03": d_shutter, "D04": d_swinging}

if __name__ == "__main__":
    run("06-dynamic", BUILDERS, set(BUILDERS))
