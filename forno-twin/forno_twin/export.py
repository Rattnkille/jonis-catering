"""Exporte: Eventakte JSON, Einkaufsplan CSV/XLSX, Einsatzbrief HTML (druckbar)."""
from __future__ import annotations

import csv
import html
import json
from pathlib import Path


def write_json(obj, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)
    return path


def write_shopping_csv(shopping: list[dict], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["item", "qty", "unit", "formula", "status"], delimiter=";")
        w.writeheader()
        for row in shopping:
            w.writerow(row)
    return path


def write_shopping_xlsx(shopping: list[dict], distribution: list[dict], path: Path) -> Path | None:
    try:
        from openpyxl import Workbook  # type: ignore
    except Exception:  # noqa: BLE001
        return None
    wb = Workbook()
    ws = wb.active; ws.title = "Einkauf"
    ws.append(["Artikel", "Menge", "Einheit", "Formel", "Status"])
    for r in shopping:
        ws.append([r["item"], r["qty"], r["unit"], r["formula"], r["status"]])
    ws2 = wb.create_sheet("Sorten")
    ws2.append(["Sorte", "Pizzen", "vegan", "vegetarisch"])
    for d in distribution:
        ws2.append([d["name"], d["pizzas"], d["vegan"], d["vegetarian"]])
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)
    return path


def write_brief_html(brief_text: str, title: str, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = f"""<!DOCTYPE html>
<html lang="de"><head><meta charset="utf-8"><title>{html.escape(title)}</title>
<style>body{{font-family:Georgia,serif;background:#fbf7f0;color:#2b2b2b;max-width:800px;margin:2rem auto;padding:1rem}}
pre{{white-space:pre-wrap;font-family:inherit;line-height:1.5}}h1{{color:#c4461f;border-bottom:2px solid #c4461f}}
@media print{{body{{background:#fff}}}}</style></head>
<body><h1>{html.escape(title)}</h1><pre>{html.escape(brief_text)}</pre>
<p style="font-size:.8rem;color:#666">KI plant. JONIS entscheidet. Nur freigegebene Angaben gelten.</p></body></html>"""
    path.write_text(doc, encoding="utf-8")
    return path
