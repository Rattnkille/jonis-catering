"""Allergen-Logik: ausschließlich aus der Matrix, nie aus Modellen.

Solange die Matrix nicht freigegeben ist (approved_by == null), liefert jede
Funktion `release_blocked=True`. Das ist Absicht: ein ungeprüfter Allergen-Fakt
gilt als kritischer Fehler.
"""
from __future__ import annotations

import json
from pathlib import Path

from .knowledge import MENU

MATRIX_PATH = Path(__file__).resolve().parent.parent / "data" / "allergen_matrix.json"


def load_matrix(path: Path | None = None) -> dict:
    with open(path or MATRIX_PATH, encoding="utf-8") as f:
        return json.load(f)


def is_approved(matrix: dict) -> bool:
    return bool(matrix.get("approved_by")) and bool(matrix.get("approved_at"))


def pizza_allergens(pizza: dict, matrix: dict) -> dict:
    """Allergene einer Pizza laut Matrix. Teig zählt immer mit."""
    ingredients = ["Weizenmehl (Teig)"] + list(pizza["ingredients"])
    found, unknown, unverified = set(), [], []
    for ing in ingredients:
        entry = matrix["ingredients"].get(ing)
        if entry is None:
            unknown.append(ing)
            continue
        found.update(entry.get("allergens", []))
        if not entry.get("verified"):
            unverified.append(ing)
    return {
        "pizza": pizza["name"],
        "allergens": sorted(found),
        "unknown_ingredients": unknown,
        "unverified_ingredients": unverified,
        "matrix_approved": is_approved(matrix),
        "release_blocked": (not is_approved(matrix)) or bool(unknown) or bool(unverified),
        "label": "ENTWURF – Freigabe erforderlich" if not is_approved(matrix) else "freigegeben",
    }


def menu_allergen_report(matrix: dict | None = None, menu: list | None = None) -> dict:
    matrix = matrix or load_matrix()
    rows = [pizza_allergens(p, matrix) for p in (menu or MENU)]
    critical = [r for r in rows if r["release_blocked"]]
    return {
        "matrix_version": matrix.get("version"),
        "matrix_status": matrix.get("_status"),
        "approved": is_approved(matrix),
        "rows": rows,
        "release_blocked": bool(critical),
        "critical_count": len(critical),
        "message": ("Allergenangaben sind ENTWURF. Automatische Freigabe blockiert, bis JONIS die Matrix freigibt."
                    if critical else "Allergen-Matrix freigegeben."),
    }


def check_mentions(mentions: list[str], matrix: dict | None = None) -> list[dict]:
    """Ordnet Allergen-Erwähnungen aus einer Anfrage den EU-Allergenen zu – nur als Hinweis."""
    matrix = matrix or load_matrix()
    mapping = {"nuss": "Schalenfrüchte", "nüsse": "Schalenfrüchte", "erdnuss": "Erdnüsse", "sellerie": "Sellerie",
               "senf": "Senf", "sesam": "Sesam", "soja": "Soja", "krebstier": "Krebstiere", "weichtier": "Weichtiere",
               "lupine": "Lupinen", "schwefel": "Sulfite", "sulfit": "Sulfite", "ei": "Eier", "eier": "Eier",
               "fisch": "Fisch", "laktose": "Milch", "gluten": "Gluten"}
    out = []
    for m in mentions:
        key = m.lower().strip()
        allergen = next((v for k, v in mapping.items() if key.startswith(k)), None)
        affected = []
        if allergen:
            for p in MENU:
                if allergen in pizza_allergens(p, matrix)["allergens"]:
                    affected.append(p["name"])
        out.append({"mention": m, "eu_allergen": allergen or "unklar", "possibly_affected_pizzas": affected,
                    "status": "HINWEIS – schriftlich bestätigen lassen"})
    return out
