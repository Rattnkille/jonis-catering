"""Pizza Pulse: anonyme Gästepräferenzen während des Events aggregieren.

Eingabe: Zählungen pro Sorte (Strichliste, Tablet-Tap, QR-Abstimmung) ohne Personenbezug.
Ausgabe: Empfehlung für die nächste Charge. Die Küche entscheidet.
"""
from __future__ import annotations


def recommend_next_batch(votes: dict[str, int], remaining_pizzas: int, batch_size: int = 12,
                         min_per_sort: int = 1, served_so_far: dict[str, int] | None = None) -> dict:
    served_so_far = served_so_far or {}
    total_votes = sum(max(0, v) for v in votes.values())
    sorts = list(votes.keys())
    if not sorts or batch_size <= 0:
        return {"batch": {}, "note": "keine Daten"}
    if total_votes == 0:
        share = {s: 1 / len(sorts) for s in sorts}
    else:
        # Laplace-Glättung gegen Überreaktion auf wenige Stimmen
        share = {s: (max(0, votes[s]) + 1) / (total_votes + len(sorts)) for s in sorts}
    raw = {s: share[s] * batch_size for s in sorts}
    batch = {s: max(min_per_sort, int(raw[s])) for s in sorts}
    diff = batch_size - sum(batch.values())
    order = sorted(sorts, key=lambda s: raw[s] - int(raw[s]), reverse=True)
    i = 0
    while diff != 0 and order:
        s = order[i % len(order)]
        if diff > 0:
            batch[s] += 1; diff -= 1
        elif batch[s] > min_per_sort:
            batch[s] -= 1; diff += 1
        i += 1
        if i > 10 * len(order):
            break
    top = max(sorts, key=lambda s: votes[s])
    return {"batch": batch, "shares": {s: round(share[s], 3) for s in sorts}, "total_votes": total_votes,
            "remaining_pizzas": remaining_pizzas, "top": top,
            "note": "Empfehlung, keine Anweisung. Küche entscheidet. Keine personenbezogenen Daten erfasst."}
