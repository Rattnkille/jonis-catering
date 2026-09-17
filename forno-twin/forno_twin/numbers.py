"""Deutsche Zahlwörter in Zahlen umwandeln (Backlog B3).

Deterministisch, ohne Modell. Deckt 1 bis 999 in üblicher deutscher Schreibweise ab,
inklusive zusammengesetzter Formen ("fünfundsechzig", "hundertzwanzig") und "Dutzend".
"""
from __future__ import annotations

import re
from typing import Optional

UNITS = {"ein": 1, "eine": 1, "eins": 1, "zwei": 2, "drei": 3, "vier": 4, "fünf": 5, "fuenf": 5,
         "sechs": 6, "sieben": 7, "acht": 8, "neun": 9}
TEENS = {"zehn": 10, "elf": 11, "zwölf": 12, "zwoelf": 12, "dreizehn": 13, "vierzehn": 14,
         "fünfzehn": 15, "fuenfzehn": 15, "sechzehn": 16, "siebzehn": 17, "achtzehn": 18, "neunzehn": 19}
TENS = {"zwanzig": 20, "dreißig": 30, "dreissig": 30, "vierzig": 40, "fünfzig": 50, "fuenfzig": 50,
        "sechzig": 60, "siebzig": 70, "achtzig": 80, "neunzig": 90}

DOZEN = 12
DOZEN_WORDS = ("dutzend",)


def _below_hundred(word: str) -> Optional[int]:
    if word in TENS:
        return TENS[word]
    if word in TEENS:
        return TEENS[word]
    if word in UNITS:
        return UNITS[word]
    if "und" in word:
        left, _, right = word.partition("und")
        if left in UNITS and right in TENS:
            return UNITS[left] + TENS[right]
    return None


def parse_german_number(word: str) -> Optional[int]:
    """'fünfundsechzig' -> 65, 'hundertzwanzig' -> 120, 'zweihundert' -> 200. Sonst None."""
    w = (word or "").strip().lower()
    if not w or not w.isalpha():
        return None
    if "hundert" in w:
        prefix, _, rest = w.partition("hundert")
        hundreds = 1 if prefix == "" else UNITS.get(prefix)
        if hundreds is None:
            return None
        if rest == "":
            return hundreds * 100
        rest = rest[3:] if rest.startswith("und") and _below_hundred(rest[3:]) is not None else rest
        tail = _below_hundred(rest)
        if tail is None:
            return None
        return hundreds * 100 + tail
    return _below_hundred(w)


def parse_number_phrase(tokens: list[str]) -> list[int]:
    """Liest eine Wortfolge vor einem Mengenwort und gibt alle gefundenen Zahlen zurück.

    Beispiele: ['zwei','dutzend'] -> [24]; ['achtzig','bis','hundert'] -> [80, 100].
    """
    values: list[int] = []
    if tokens and tokens[-1] in DOZEN_WORDS:
        mult = parse_german_number(tokens[-2]) if len(tokens) >= 2 else None
        return [DOZEN * (mult if mult else 1)]
    for t in tokens:
        n = parse_german_number(t)
        if n is not None and n >= 10:  # 'ein'/'zwei' allein ist meist kein Gästezähler
            values.append(n)
    return values


def digits_before(text: str, end: int, window: int = 70, max_tokens: int = 5) -> list[str]:
    """Die letzten Worttoken vor Position `end` (für die Zahlwort-Erkennung)."""
    start = max(0, end - window)
    return re.findall(r"[a-zäöüßA-ZÄÖÜ]+", text[start:end])[-max_tokens:]
