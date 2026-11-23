"""SVG-чертежи категории 04-barriers (барьеры и стенки).

Запуск:  python tools/draw_barriers.py          — все барьеры
         python tools/draw_barriers.py B04 B10  — выбранные элементы
"""
import math

from drawlib import DIM, INK, rect_pts, run

PATH = "#2E7D32"


def spec(main_title, main_ext, main_draw, aux_title, aux_ext, aux_draw, main_floor=True, aux_floor=True,
         independent=False):
    return {"main": dict(title=main_title, ext=main_ext, floor=main_floor, draw=main_draw),
            "aux": dict(title=aux_title, ext=aux_ext, floor=aux_floor, draw=aux_draw), "independent": independent}


def circle(v, x, y, r, fill, stroke=INK, sw=1.2):
    v.raw(f'<circle cx="{v.X(x):.1f}" cy="{v.Y(y):.1f}" r="{max(r * v.k, 1.5):.1f}" fill="{fill}" '
          f'stroke="{stroke}" stroke-width="{sw}"/>')


def panel_side(v, H, t, col, depth=300, sup_h=None):
    """Панель сбоку: ребро толщиной t и треугольная подпорка сзади."""
    sup_h = sup_h or H * 0.5
    v.poly([(t / 2, 0), (depth, 0), (t / 2, sup_h)], fill="#cfd8dc")
    v.rect(-t / 2, 0, t, H, fill=col)
    v.hdim(-t / 2, depth, 0, -30, depth)
    v.vdim(0, H, depth, 28, H)


def post_side(v, H, foot=300, post=25, col="#fafafa"):
    v.rect(-foot / 2, 0, foot, 15, fill="#616161")
    v.rect(-post / 2, 15, post, H - 15, fill=col)
    v.hdim(-foot / 2, foot / 2, 0, -30, foot)


def hole_rim(v, d, color, w=3):
    v.raw(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{w + 2}"/>')
    v.raw(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}"/>')


def circ_d(v, cx, cy, r):
    R, X, Y = r * v.k, v.X(cx), v.Y(cy)
    return f"M{X - R:.1f},{Y:.1f} a{R:.1f},{R:.1f} 0 1,0 {2 * R:.1f},0 a{R:.1f},{R:.1f} 0 1,0 {-2 * R:.1f},0 Z"


def rect_d(v, x, y, w, h):
    return "M" + " L".join(v.P(*p) for p in rect_pts(x, y, w, h)) + " Z"


# ---------------------------------------------------------------- элементы
def b_hurdle(e, va, d, a, col, *_):                   # B01 — перелёт над планкой
    h, H, bar = d["bar_axis"], d["height"], d["bar"]
    px = 520

    def front(v):
        for sx in (-1, 1):
            v.rect(sx * px - 30, 0, 60, 15, fill="#616161")
            v.rect(sx * px - 12.5, 15, 25, H - 15, fill="#fafafa")
        v.rect(-500, h - bar / 2, 1000, bar, fill=col)
        v.rect(-500, h - bar / 2, 1000, bar, fill="url(#cylv)", stroke=INK)
        v.hdim(-px - 12.5, px + 12.5, H, 22, d["width"])
        v.vdim(0, h, px + 12.5, 28, f"{h} ось")
        v.vdim(0, a["min_height"], -px - 12.5, -28, f"{a['min_height']} верх планки")
        v.hdim(-500, 500, h + bar / 2, 14, f"планка Ø{bar} × {d['bar_length']}")

    def side(v):
        post_side(v, H)
        circle(v, 0, h, bar / 2, col)
        v.flight(h + bar / 2 + 120)

    return spec("Вид спереди", (-px - 12.5, px + 12.5, 0, H), front, "Вид сбоку", (-150, 150, 0, H), side)


def b_limbo(e, va, d, a, col, col2="#212121", *_):    # B02 — пролёт под планкой
    h, H, bar = d["bar_axis"], d["height"], d["bar"]
    px = 500

    def front(v):
        for sx in (-1, 1):
            v.rect(sx * px - 30, 0, 60, 15, fill="#616161")
            v.rect(sx * px - 12.5, 15, 25, H - 15, fill=col2)
        for i in range(10):
            v.rect(-487.5 + i * 97.5, h - bar / 2, 97.5, bar, fill=col if i % 2 == 0 else col2, sw=0.6)
        v.hdim(-px - 12.5, px + 12.5, H, 22, d["width"])
        v.vdim(0, H, px + 12.5, 28, H)
        v.idim(0, 0, 0, a["height"], f"просвет {a['height']}")
        v.vdim(0, h, -px - 12.5, -28, f"{h} ось")

    def side(v):
        post_side(v, H, col=col2)
        circle(v, 0, h, max(bar / 2, 6), col)
        v.flight(a["height"] / 2)

    return spec("Вид спереди", (-px - 12.5, px + 12.5, 0, H), front, "Вид сбоку", (-150, 150, 0, H), side)


def b_wall(e, va, d, a, col, top="#FFFFFF", *_):      # B03
    W, H, t = d["width"], d["height"], d["thickness"]

    def front(v):
        v.rect(-W / 2, 0, W, H, fill=col)
        v.rect(-W / 2, H - 50, W, 50, fill=top)
        v.hdim(-W / 2, W / 2, H, 22, W)
        v.vdim(0, H, W / 2, 28, H)
        v.text(0, H / 2, "обход сверху или сбоку", size=13, fill="#37474F")

    def side(v):
        panel_side(v, H, t, col)

    return spec("Вид спереди", (-W / 2, W / 2, 0, H), front, "Вид сбоку", (-t / 2, 300, 0, H), side)


def b_window(e, va, d, a, col, rim="#FFFFFF", *_):    # B04
    W, H, t = d["width"], d["height"], d["thickness"]
    cy = a["center_y"]

    def front(v):
        outer = rect_d(v, -W / 2, 0, W, H)
        if a["shape"] == "circle":
            r = a["diameter"] / 2
            hole = circ_d(v, 0, cy, r)
        else:
            hole = rect_d(v, -a["width"] / 2, a["bottom"], a["width"], a["height"])
        v.raw(f'<path d="{outer} {hole}" fill="{col}" fill-rule="evenodd" stroke="{INK}" stroke-width="1.2"/>')
        hole_rim(v, hole, rim)
        v.hdim(-W / 2, W / 2, H, 22, W)
        v.vdim(0, H, W / 2, 28, H)
        if a["shape"] == "circle":
            v.idim(-r, cy, r, cy, f"Ø{a['diameter']}")
        else:
            v.idim(-a["width"] / 2, cy, a["width"] / 2, cy, a["width"])
            v.idim(-a["width"] * 0.3, a["bottom"], -a["width"] * 0.3, a["bottom"] + a["height"], a["height"])
        v.vdim(0, a["bottom"], -W / 2, -28, a["bottom"])
        v.vdim(0, cy, -W / 2, -62, f"{cy} центр")

    def side(v):
        panel_side(v, H, t, col)
        v.flight(cy)

    return spec("Вид спереди", (-W / 2, W / 2, 0, H), front, "Вид сбоку", (-t / 2, 300, 0, H), side)


def b_multi(e, va, d, a, col, rim="#FFD600", *_):     # B05
    W, H, t = d["width"], d["height"], d["thickness"]
    wins = [("c", -300, 700, 350), ("s", 300, 700, 250), ("s", -300, 300, 300), ("c", 300, 300, 200)]

    def front(v):
        holes = []
        for kind, x, y, s in wins:
            holes.append(circ_d(v, x, y, s / 2) if kind == "c" else rect_d(v, x - s / 2, y - s / 2, s, s))
        v.raw(f'<path d="{rect_d(v, -W / 2, 0, W, H)} {" ".join(holes)}" fill="{col}" fill-rule="evenodd" '
              f'stroke="{INK}" stroke-width="1.2"/>')
        for i, ((kind, x, y, s), hd) in enumerate(zip(wins, holes), 1):
            hole_rim(v, hd, rim)
            v.idim(x - s / 2, y, x + s / 2, y, f"Ø{s}" if kind == "c" else s)
            v.text(x - s / 2 - 30, y + s / 2 - 10, i, size=16, fill=rim, extra='font-weight="bold"')
        v.hdim(-W / 2, W / 2, H, 22, W)
        v.vdim(0, H, W / 2, 28, H)
        v.hdim(-300, 300, 0, -30, "600 между центрами")
        v.vdim(300, 700, -W / 2, -28, "400")
        v.vdim(0, 300, -W / 2, -62, "300")

    def side(v):
        panel_side(v, H, t, col)
        v.flight(700)
        v.flight(300)

    return spec("Вид спереди", (-W / 2, W / 2, 0, H), front, "Вид сбоку", (-t / 2, 300, 0, H), side)


def b_streamers(e, va, d, a, col, col2="#E53935", *_):  # B06
    H, sw_, step, sl = d["height"], d["strip_width"], d["strip_step"], d["strip_length"]
    px = 512.5
    bottom = H - sl

    def front(v):
        for sx in (-1, 1):
            v.rect(sx * px - 30, 0, 60, 15, fill="#616161")
            v.rect(sx * px - 12.5, 15, 25, H - 15, fill="#9e9e9e")
        v.rect(-px - 12.5, H - 25, 2 * px + 25, 25, fill="#9e9e9e")
        x, i = -475, 0
        while x <= 475:
            v.rect(x - sw_ / 2, bottom, sw_, sl - 25, fill=col if i % 2 == 0 else col2, sw=0.5)
            x += step
            i += 1
        v.hdim(-px - 12.5, px + 12.5, H, 22, d["width"])
        v.vdim(bottom, H, px + 12.5, 28, sl)
        v.vdim(0, H, px + 12.5, 62, H)
        v.vdim(0, bottom, -px - 12.5, -28, f"просвет {bottom}")
        v.hdim(-475, -475 + step, bottom, -26, f"шаг {step}")

    def side(v):
        post_side(v, H, col="#9e9e9e")
        for dz, c in ((-6, col), (0, col2), (6, col)):
            v.line(dz, bottom, dz * 0.3, H - 25, stroke=c, sw=2)
        v.flight(bottom + sl / 2)

    return spec("Вид спереди", (-px - 12.5, px + 12.5, 0, H), front, "Вид сбоку", (-150, 150, 0, H), side)


def b_net(e, va, d, a, col, frame="#FF6D00", *_):     # B07
    H, nw, nh, mesh = d["height"], d["net_width"], d["net_height"], d["mesh"]
    px = 512.5
    nb = 100
    ow, ob = a["width"], a["bottom"]

    def front(v):
        s = mesh * v.k
        v.raw(f'<defs><pattern id="mesh" width="{s:.2f}" height="{s:.2f}" patternUnits="userSpaceOnUse">'
              f'<path d="M0,0 L{s:.2f},{s:.2f} M{s:.2f},0 L0,{s:.2f}" stroke="{col}" stroke-width="0.7"/>'
              f'</pattern></defs>')
        for sx in (-1, 1):
            v.rect(sx * px - 30, 0, 60, 15, fill="#616161")
            v.rect(sx * px - 12.5, 15, 25, H - 15, fill="#9e9e9e")
        v.rect(-px - 12.5, nb + nh, 2 * px + 25, 20, fill="#9e9e9e")
        v.holed(rect_pts(-nw / 2, nb, nw, nh), [rect_pts(-ow / 2 - 20, ob - 20, ow + 40, ow + 40)], "url(#mesh)",
                sw=0.8)
        v.holed(rect_pts(-ow / 2 - 20, ob - 20, ow + 40, ow + 40), [rect_pts(-ow / 2, ob, ow, ow)], frame)
        v.hdim(-px - 12.5, px + 12.5, H, 22, d["width"])
        v.vdim(0, H, px + 12.5, 28, H)
        v.idim(-ow / 2, ob + ow / 2, ow / 2, ob + ow / 2, ow)
        v.vdim(0, ob, -px - 12.5, -28, ob)
        v.vdim(0, nb, -px - 12.5, -62, nb)
        v.text(nw / 2 - 120, nb - 70, f"ячейка {mesh}", size=11, fill=DIM)

    def side(v):
        post_side(v, H, col="#9e9e9e")
        v.line(0, nb, 0, nb + nh, stroke=col, sw=1.5, extra='stroke-dasharray="3 2"')
        v.rect(-6, ob - 20, 12, ow + 40, fill=frame)
        v.flight(ob + ow / 2)

    return spec("Вид спереди", (-px - 12.5, px + 12.5, 0, H), front, "Вид сбоку", (-150, 150, 0, H), side)


def b_partition(e, va, d, a, col, *_):                # B08
    pw, n, ang, H = d["panel_width"], d["panels"], math.radians(d["angle"]), d["height"]
    px = pw * math.cos(ang)
    W = n * px
    dz = pw * math.sin(ang)

    def front(v):
        shades = [1.0, 0.75, 1.0]
        for i in range(n):
            x0 = -W / 2 + i * px
            v.rect(x0, 0, px, H, fill=col, extra=f'fill-opacity="{shades[i % 3]}"')
            v.rect(x0, 0, px, H, fill="none", stroke="#B0BEC5", sw=3)
        v.hdim(-W / 2, W / 2, H, 22, round(W))
        v.vdim(0, H, W / 2, 28, H)
        v.hdim(-W / 2, -W / 2 + px, 0, -30, f"{round(px)} (створка {pw} под {d['angle']}°)")

    def top(v):
        pts = [(-W / 2 + i * px, 0 if i % 2 == 0 else dz) for i in range(n + 1)]
        v.raw(f'<polyline points="{" ".join(v.P(*p) for p in pts)}" fill="none" stroke="{INK}" '
              f'stroke-width="7" stroke-linejoin="miter"/>')
        v.raw(f'<polyline points="{" ".join(v.P(*p) for p in pts)}" fill="none" stroke="{col}" '
              f'stroke-width="4" stroke-linejoin="miter"/>')
        v.hdim(-W / 2, W / 2, dz, 22, round(W))
        v.vdim(0, dz, W / 2, 28, round(dz))
        v.text(0, -120, "обход сбоку или сверху", size=11, fill=PATH)

    return spec("Вид спереди", (-W / 2, W / 2, 0, H), front, "Вид сверху", (-W / 2, W / 2, -60, dz), top,
                aux_floor=False, independent=True)


def b_maze(e, va, d, a, col, edge="#212121", *_):     # B09 — вид сверху: u = вперёд, w = влево
    L, cw, H = d["depth"], d["corridor_width"], d["height"]
    hw = cw / 2
    inner = L - cw

    def top(v):
        v.poly([(0, -hw), (L, -hw), (L, L - hw), (inner, L - hw), (inner, hw), (0, hw)], fill="#F1F3F4", sw=0)
        wsw = max(10 * v.k, 4)
        for pts in ([(0, -hw), (L, -hw), (L, L - hw)], [(0, hw), (inner, hw), (inner, L - hw)]):
            v.raw(f'<polyline points="{" ".join(v.P(*p) for p in pts)}" fill="none" stroke="{edge}" '
                  f'stroke-width="{wsw:.1f}" stroke-linejoin="miter"/>')
        c = L - hw
        v.raw(f'<path d="M{v.P(0, 0)} L{v.P(c - 300, 0)} Q{v.P(c, 0)} {v.P(c, 300)} L{v.P(c, L - hw)}" '
              f'fill="none" stroke="{PATH}" stroke-width="1.8" stroke-dasharray="7 5"/>')
        v.flight(0)
        v.arrow_px(c, L - hw, 0, -44, "выход")
        v.hdim(0, L, -hw, -30, f"{L} (внешняя стенка {L} + {L})")
        v.vdim(-hw, L - hw, L, 28, L)
        v.idim(L * 0.3, -hw, L * 0.3, hw, cw)
        v.text(inner / 2, hw + 40, f"внутр. стенка {inner} + {inner}", size=11, fill=DIM)

    def front(v):
        v.rect(-hw, 0, cw, H, fill="#ECEFF1", sw=0.8)
        for sx in (-1, 1):
            v.rect(sx * (hw + 5) - 5, 0, 10, H, fill=col)
            v.rect(sx * (hw + 5) - 5, H - 10, 10, 10, fill=edge)
        v.text(0, H / 2, "дальняя стенка", size=11, fill=DIM)
        v.idim(-hw, H * 0.25, hw, H * 0.25, cw)
        v.vdim(0, H, hw + 10, 28, H)

    return spec("Вид сверху", (0, L, -hw, L - hw), top, "Вид на вход", (-hw - 10, hw + 10, 0, H), front,
                main_floor=False, independent=True)


def b_gap(e, va, d, a, col, edge="#FFFFFF", *_):      # B10
    g, pw, H, t = d["gap"], d["panel_width"], d["height"], d["thickness"]
    W = d["width"]

    def front(v):
        v.rect(-g / 2 - pw, 0, pw, H, fill=col)
        v.rect(g / 2, 0, pw, H, fill=col)
        for sx in (-1, 1):
            v.rect(sx * g / 2 - (12 if sx > 0 else 0), 0, 12, H, fill=edge, sw=0.8)
        v.idim(-g / 2, H / 2, g / 2, H / 2, g)
        v.hdim(-W / 2, W / 2, H, 22, W)
        v.vdim(0, H, W / 2, 28, H)
        v.hdim(g / 2, g / 2 + pw, 0, -30, pw)
        v.raw(f'<rect x="{v.X(-47.5):.1f}" y="{v.Y(H * 0.3 + 15):.1f}" width="{95 * v.k:.1f}" '
              f'height="{30 * v.k:.1f}" fill="none" stroke="{PATH}" stroke-dasharray="3 2"/>')
        v.text(0, H * 0.3 - 40, "вуп ≈95", size=11, fill=PATH)

    def side(v):
        panel_side(v, H, t, col)
        v.flight(H / 2)

    return spec("Вид спереди", (-W / 2, W / 2, 0, H), front, "Вид сбоку", (-t / 2, 300, 0, H), side)


BUILDERS = {"B01": b_hurdle, "B02": b_limbo, "B03": b_wall, "B04": b_window, "B05": b_multi,
            "B06": b_streamers, "B07": b_net, "B08": b_partition, "B09": b_maze, "B10": b_gap}

if __name__ == "__main__":
    run("04-barriers", BUILDERS, set(BUILDERS))
