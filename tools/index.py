"""Пересобирает INDEX.md из obstacles/**/element.yaml и печатает прогресс."""
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
OBST = ROOT / "obstacles"


def main():
    rows, status = [], Counter()
    variants_total = 0
    for f in sorted(OBST.glob("*/*/element.yaml")):
        el = yaml.safe_load(f.read_text(encoding="utf-8"))
        vs = el.get("variants") or []
        variants_total += len(vs)
        drawn = sum((f.parent / v.get("drawing", "")).is_file() for v in vs)
        st = el.get("status", "draft")
        status[st] += 1
        rel = f.parent.relative_to(ROOT).as_posix()
        rows.append(
            f"| [{el['id']}]({rel}/element.yaml) | {el.get('name_ru', '')} | "
            f"{el.get('category', '')} | {el.get('scope', '')} | {el.get('behavior', '')} | "
            f"{len(vs)} | {drawn}/{len(vs)} | {st} |"
        )

    out = [
        "# Индекс препятствий",
        "",
        "_Генерируется `python tools/index.py`, руками не править._",
        "",
        f"Элементов: **{len(rows)}**, вариантов: **{variants_total}**. "
        + ", ".join(f"{k}: {v}" for k, v in sorted(status.items())),
        "",
        "| ID | Название | Категория | Scope | Тип | Вариантов | Чертежи | Статус |",
        "|---|---|---|---|---|---|---|---|",
        *rows,
        "",
    ]
    (ROOT / "INDEX.md").write_text("\n".join(out), encoding="utf-8")
    print(f"elements: {len(rows)}, variants: {variants_total}")
    for k, v in sorted(status.items()):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
