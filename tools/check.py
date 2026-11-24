"""Проверяет целостность каталога: обязательные поля, ID, цвета, чертежи.

Запуск:  python tools/check.py
Код возврата 0 — всё в порядке, 1 — есть ошибки (список выводится).
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
OBST = ROOT / "obstacles"

REQUIRED = ["id", "name_ru", "name_en", "category", "scope", "behavior", "status", "description",
            "real_analog", "mount", "material", "rigidity", "color", "difficulty"]
ENUMS = {
    "scope": {"track", "indoor", "outdoor", "service"},
    "behavior": {"static", "dynamic"},
    "status": {"draft", "filled", "reviewed"},
    "mount": {"floor", "stand", "hanging", "wall", "free"},
    "rigidity": {"soft", "semi", "hard"},
}
HEX = re.compile(r"#[0-9A-Fa-f]{6}")


def check():
    errors, seen = [], set()
    for f in sorted(OBST.glob("*/*/element.yaml")):
        rel = f.relative_to(ROOT).as_posix()
        try:
            e = yaml.safe_load(f.read_text(encoding="utf-8"))
        except yaml.YAMLError as ex:
            errors.append(f"{rel}: YAML не читается: {ex}")
            continue
        eid = e.get("id", "?")
        if eid in seen:
            errors.append(f"{rel}: повторный id {eid}")
        seen.add(eid)
        if not f.parent.name.startswith(f"{eid}-"):
            errors.append(f"{rel}: папка не начинается с id {eid}")
        if e.get("status") == "draft":
            continue
        for k in REQUIRED:
            if e.get(k) in (None, ""):
                errors.append(f"{eid}: пустое поле {k}")
        for k, allowed in ENUMS.items():
            if e.get(k) not in allowed:
                errors.append(f"{eid}: {k} = {e.get(k)!r}, допустимо {sorted(allowed)}")
        if e.get("behavior") == "dynamic" and not e.get("motion"):
            errors.append(f"{eid}: dynamic без блока motion")
        diff = e.get("difficulty")
        if not isinstance(diff, int) or not 1 <= diff <= 5:
            errors.append(f"{eid}: difficulty должна быть 1–5")
        variants = e.get("variants") or []
        if not variants:
            errors.append(f"{eid}: нет вариантов")
        for i, v in enumerate(variants):
            vid = v.get("id")
            expect = f"{eid}-{chr(97 + i)}"
            if vid != expect:
                errors.append(f"{eid}: вариант {i + 1} имеет id {vid}, ожидался {expect}")
            color = v.get("color", e.get("color", ""))
            if not HEX.search(str(color)):
                errors.append(f"{vid}: в цвете нет HEX-кода")
            dims = v.get("dimensions_mm") or {}
            for k in ("width", "height", "depth"):
                if k not in dims:
                    errors.append(f"{vid}: в dimensions_mm нет {k}")
            if not (v.get("aperture_mm") or {}).get("shape"):
                errors.append(f"{vid}: в aperture_mm нет shape")
            drawing = f.parent / v.get("drawing", "")
            if not drawing.is_file():
                errors.append(f"{vid}: нет чертежа {v.get('drawing')}")
    return errors, len(seen)


def main():
    errors, n = check()
    if errors:
        print(f"Ошибок: {len(errors)}")
        for x in errors:
            print("  -", x)
        sys.exit(1)
    print(f"OK: {n} элементов, ошибок нет")


if __name__ == "__main__":
    main()
