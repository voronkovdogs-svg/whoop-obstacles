"""Пересобирает чертежи всех категорий.

Запуск:  python tools/draw_all.py
"""
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from drawlib import build, ROOT  # noqa: E402

CATEGORIES = [
    ("01-gates", "draw_gates", "TWO_COLOR"),
    ("02-tunnels", "draw_tunnels", "ALL_COLORS"),
    ("03-markers", "draw_markers", None),
    ("04-barriers", "draw_barriers", None),
    ("05-combos", "draw_combos", None),
    ("06-dynamic", "draw_dynamic", None),
    ("07-interior", "draw_interior", None),
    ("08-outdoor", "draw_outdoor", None),
    ("09-service", "draw_service", None),
]


def main():
    total = 0
    for folder, module, colors_attr in CATEGORIES:
        mod = importlib.import_module(module)
        two = getattr(mod, colors_attr) if colors_attr else set(mod.BUILDERS)
        n = 0
        for f in sorted((ROOT / "obstacles" / folder).glob("*/element.yaml")):
            n += build(f, mod.BUILDERS, two)
        print(f"{folder:14} {n:3} чертежей")
        total += n
    print(f"всего: {total}")


if __name__ == "__main__":
    main()
