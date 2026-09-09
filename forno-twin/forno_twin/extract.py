"""Regelbasierte Extraktion aus unstrukturierten deutschen Anfragen.

Deterministisch, offline, ohne Modell. Ein HF-Modell (Zero-Shot) kann die
Triage optional ergänzen (siehe hf_models.py), setzt aber nie Fakten.
Sicherheitsregeln:
- PII wird früh pseudonymisiert ([EMAIL_1], [TEL_1], [NAME_1]).
- Prompt-Injection-Muster werden als security_finding markiert und ignoriert.
- Allergen-Erwähnungen sind Hinweise, nie Wahrheit.
"""
from __future__ import annotations

import re
from datetime import date
from typing import Optional

from .knowledge import COMPANY, VERIFIZIERT, ABLEITUNG, ANNAHME, KONFLIKT, TBD
from .schema import EventFile

MONTHS = {"januar": 1, "februar": 2, "märz": 3, "maerz": 3, "april": 4, "mai": 5, "juni": 6,
          "juli": 7, "august": 8, "september": 9, "oktober": 10, "november": 11, "dezember": 12,
          "jan": 1, "feb": 2, "mär": 3, "apr": 4, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "sept": 9,
          "okt": 10, "nov": 11, "dez": 12,
          "january": 1, "february": 2, "march": 3, "june": 6, "july": 7, "october": 10, "december": 12}

NUM_WORDS = {"fünfzig": 50, "sechzig": 60, "siebzig": 70, "achtzig": 80, "neunzig": 90,
             "hundert": 100, "einhundert": 100, "hundertfünfzig": 150, "zweihundert": 200}

EVENT_TYPES = [
    ("hochzeit", ["hochzeit", "heiraten", "trauung", "wedding", "matrimonio", "brautpaar", "married", "marry", "sposiamo", "nozze"]),
    ("firmenevent", ["firma", "firmen", "unternehmen", "sommerfest", "betriebsfeier", "team", "mitarbeiter",
                     "kollegen", "kunden-event", "weihnachtsfeier", "corporate", "company", "office", "azienda"]),
    ("privat", ["geburtstag", "jubiläum", "taufe", "konfirmation", "gartenparty", "party", "feier",
                "birthday", "compleanno", "festa", "einweihung", "abschluss"]),
]

DIET_PATTERNS = {
    "vegetarisch": r"vegetar|veggie|ohne fleisch|vegetarian",
    "vegan": r"\bvegan",
    "glutenfrei": r"glutenfrei|gluten-?free|zöliakie|senza glutine|glutenintoleranz",
    "laktosefrei": r"laktose|lactose|lattosio",
    "halal": r"\bhalal\b",
    "kein_schwein": r"kein schwein|ohne schwein|no pork",
}
ALLERGEN_HINTS = r"(allerg\w*|unverträglich\w*|intoleran\w*|nuss|nüsse|erdnuss|sellerie|senf|sesam|soja|krebstier|weichtier|lupine|schwefel|sulfit|ei\b|eier|fisch)"

INJECTION_PATTERNS = [
    r"ignor(e|iere|ieren)\s+(alle|all|die|previous|vorherige)\s+(anweisungen|instructions|regeln)",
    r"(system|assistant)\s*:\s*",
    r"du bist jetzt|you are now",
    r"(gib|gewähre|grant).{0,30}(rabatt|discount|kostenlos|free)",
    r"(sende|send|leite).{0,40}(an|to)\s+\S+@\S+",
    r"(passwort|password|token|api[- ]?key)",
    r"<\s*script",
]

PII_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PII_PHONE = re.compile(r"(\+?\d[\d\s/()-]{7,}\d)")
PII_NAME = re.compile(r"(?:ich bin|ich heiße|mein name ist|viele grüße|liebe grüße|beste grüße|lg|grüße|mit freundlichen grüßen|herzliche grüße|regards|best|saluti|cordiali saluti)[,\s]+([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß-]+){0,2})", re.IGNORECASE)


def pseudonymize(text: str) -> tuple[str, dict]:
    """Ersetzt E-Mail, Telefon und erkannte Namen durch Platzhalter. Gibt Mapping zurück (bleibt lokal)."""
    mapping = {}
    counters = {"EMAIL": 0, "TEL": 0, "NAME": 0}

    def sub(kind, m, group=0):
        counters[kind] += 1
        key = f"[{kind}_{counters[kind]}]"
        mapping[key] = m.group(group)
        return key

    text = PII_EMAIL.sub(lambda m: sub("EMAIL", m), text)
    text = PII_PHONE.sub(lambda m: sub("TEL", m) if not re.search(r"\d{1,2}[.:]\d{2}\s*uhr", m.group(0), re.I) else m.group(0), text)

    def name_sub(m):
        counters["NAME"] += 1
        key = f"[NAME_{counters['NAME']}]"
        mapping[key] = m.group(1)
        return m.group(0).replace(m.group(1), key)

    text = PII_NAME.sub(name_sub, text)
    return text, mapping


def detect_injection(text: str) -> list[str]:
    findings = []
    low = text.lower()
    for pat in INJECTION_PATTERNS:
        if re.search(pat, low):
            findings.append(f"Mögliche Prompt-Injection / unzulässige Anweisung im Dokument: Muster '{pat}'. Ignoriert.")
    return findings


def detect_language(text: str) -> str:
    low = f" {text.lower()} "
    en = sum(low.count(w) for w in [" the ", " we ", " guests ", " wedding ", " would ", " please ", " people "])
    it = sum(low.count(w) for w in [" persone ", " matrimonio ", " vorremmo ", " grazie ", " ospiti ", " festa "])
    de = sum(low.count(w) for w in [" wir ", " und ", " personen ", " gäste ", " bitte ", " für ", " ich "])
    best = max(("de", de), ("en", en), ("it", it), key=lambda x: x[1])
    return best[0] if best[1] > 0 else "de"


def extract_guests(text: str) -> tuple[Optional[int], list[int]]:
    low = text.lower()
    found = []
    for m in re.finditer(r"(?:ca\.?|circa|etwa|rund|ungefähr|about|around|~)?\s*(\d{2,4})\s*(?:-|bis|–|to)?\s*(\d{2,4})?\s*(personen|gäste|gaeste|leute|pax|people|guests|persone|ospiti|mann|köpfe|kollegen|mitarbeiter)", low):
        a = int(m.group(1))
        b = int(m.group(2)) if m.group(2) else None
        found.append(b if b else a)  # bei Spanne: Obergrenze planen
    for w, n in NUM_WORDS.items():
        if re.search(rf"\b{w}\b\s*(personen|gäste|leute|gaeste)", low):
            found.append(n)
    if not found:
        return None, []
    return max(found), sorted(set(found))


def extract_date(text: str, today: date | None = None) -> tuple[Optional[str], Optional[str]]:
    today = today or date.today()
    m = re.search(r"\b(\d{1,2})\.(\d{1,2})\.(\d{4}|\d{2})\b", text)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        y = y + 2000 if y < 100 else y
        try:
            return date(y, mo, d).isoformat(), None
        except ValueError:
            return None, m.group(0)
    m = re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", text)
    if m:
        return m.group(0), None
    m = re.search(r"\b(\d{1,2})\.?\s*(" + "|".join(MONTHS.keys()) + r")\.?\s*(\d{4})?", text, re.I)
    if m:
        d = int(m.group(1)); mo = MONTHS[m.group(2).lower()]
        y = int(m.group(3)) if m.group(3) else (today.year if (mo, d) >= (today.month, today.day) else today.year + 1)
        try:
            return date(y, mo, d).isoformat(), None if m.group(3) else "Jahr angenommen (nächstes Vorkommen)"
        except ValueError:
            return None, m.group(0)
    m = re.search(r"\b(" + "|".join(k for k in MONTHS if len(k) > 3) + r")\b\s*(\d{4})?", text, re.I)
    if m:
        return None, f"nur Monat: {m.group(1)}{(' ' + m.group(2)) if m.group(2) else ''}"
    return None, None


def extract_time_window(text: str) -> tuple[Optional[str], Optional[str]]:
    m = re.search(r"(?:beginn|start|los geht.?s|anfang)\s*(?:um|ab|:)?\s*(\d{1,2})(?:[:.](\d{2}))?\s*(?:uhr)?(?:.{0,25}?(?:ende|bis|schluss)\s*(?:gegen|um|ca\.?)?\s*(\d{1,2})(?:[:.](\d{2}))?\s*(?:uhr)?)?", text, re.I)
    if m:
        start = f"{int(m.group(1)):02d}:{m.group(2) or '00'}"
        if m.group(3):
            return f"{start}-{int(m.group(3)):02d}:{m.group(4) or '00'}", start
        return f"ab {start}", start
    m = re.search(r"(?:ab|von|from|dalle)\s*(\d{1,2})(?:[:.](\d{2}))?\s*(?:uhr)?\s*(?:bis|-|–|to|alle)\s*(\d{1,2})(?:[:.](\d{2}))?\s*(?:uhr)?", text, re.I)
    if m:
        start = f"{int(m.group(1)):02d}:{m.group(2) or '00'}"
        end = f"{int(m.group(3)):02d}:{m.group(4) or '00'}"
        return f"{start}-{end}", start
    m = re.search(r"(?:ab|um|gegen|from|at)\s*(\d{1,2})(?:[:.](\d{2}))?\s*(?:uhr|h|pm|o'clock)", text, re.I)
    if m:
        start = f"{int(m.group(1)):02d}:{m.group(2) or '00'}"
        return f"ab {start}", start
    if re.search(r"\babends?\b|evening|sera", text, re.I):
        return "abends (unbestimmt)", None
    if re.search(r"\bmittags?\b|lunch|pranzo", text, re.I):
        return "mittags (unbestimmt)", None
    return None, None


def extract_budget(text: str) -> tuple[Optional[float], Optional[float]]:
    low = text.lower().replace(".", "").replace(",", ".")
    m = re.search(r"(\d{2,3}(?:\.\d+)?)\s*(?:€|euro|eur)\s*(?:pro|per|p\.?p\.?|je)\s*(?:person|kopf|gast|nase|head)", low)
    pp = float(m.group(1)) if m else None
    m2 = re.search(r"(?:budget|max(?:imal)?|höchstens|bis zu|nicht mehr als|not more than|around)\D{0,20}?(\d{3,6})\s*(?:€|euro|eur)", low)
    total = float(m2.group(1)) if m2 else None
    if total is None:
        m3 = re.search(r"(\d{3,6})\s*(?:€|euro|eur)\s*(?:gesamt|insgesamt|total|budget)", low)
        total = float(m3.group(1)) if m3 else None
    return total, pp


def extract_location(text: str) -> tuple[Optional[str], Optional[str], list[str]]:
    loc = None
    for city in COMPANY["region_cities"]:
        if re.search(rf"\b{city}\b", text, re.I):
            loc = city
            break
    if not loc:
        m = re.search(r"\bin\s+([A-ZÄÖÜ][a-zäöüß]+(?:[- ][A-ZÄÖÜ][a-zäöüß]+)?)", text)
        if m and m.group(1).lower() not in ("juni", "juli", "august", "september", "oktober", "mai", "ordnung", "kürze"):
            loc = m.group(1)
    low = text.lower()
    notes = []
    ltype = None
    if re.search(r"garten|draußen|draussen|outdoor|wiese|hof|feld|open air|park|strand|all'aperto|giardino", low):
        ltype = "outdoor"
    if re.search(r"halle|scheune|saal|innen|indoor|büro|office|restaurant|loft|werkstatt", low):
        ltype = "indoor" if ltype is None else "gemischt"
    for pat, note in [(r"kein strom|ohne strom|no power", "Kein Strom vor Ort (Hinweis Kunde)"),
                      (r"strom", "Strom erwähnt – Details klären"),
                      (r"zufahrt|anfahrt|schmal|eng|kopfsteinpflaster|schotter|zugang", "Zufahrt erwähnt – prüfen"),
                      (r"wasser", "Wasseranschluss erwähnt"),
                      (r"regen|wetter|zelt|überdach|pavillon", "Wetterschutz/Wetter erwähnt")]:
        if re.search(pat, low):
            notes.append(note)
    return loc, ltype, notes


def extract_diets(text: str) -> tuple[list[str], Optional[float], Optional[float], Optional[int], list[str]]:
    low = text.lower()
    diets = [k for k, p in DIET_PATTERNS.items() if re.search(p, low)]
    veg_share = vegan_share = None
    m = re.search(r"(\d{1,3})\s*%\s*(?:sind\s*)?(?:vegetar|veggie)", low)
    if m:
        veg_share = int(m.group(1)) / 100
    m = re.search(r"(\d{1,3})\s*%\s*(?:sind\s*)?vegan", low)
    if m:
        vegan_share = int(m.group(1)) / 100
    m = re.search(r"(\d{1,3})\s*(?:personen|gäste|leute)?\s*(?:sind\s*)?(?:vegetar|veggie)", low)
    if m and veg_share is None and not re.search(r"\d{1,3}\s*%", m.group(0)):
        veg_share = ("count", int(m.group(1)))
    if re.search(r"(hälfte|halb|half).{0,20}(vegetar|veggie)", low):
        veg_share = 0.5
    if re.search(r"viele|einige|mehrere|some|many|diverse|paar", low) and "vegetarisch" in diets and veg_share is None:
        veg_share = None  # bleibt Lücke -> Rückfrage
    gf = None
    m = re.search(r"(\d{1,2})\s*(?:personen|gäste|leute)?\s*(?:mit\s*)?(?:glutenfrei|zöliakie|gluten)", low)
    if m:
        gf = int(m.group(1))
    elif "glutenfrei" in diets:
        gf = 1
    allergens = [m.group(0) for m in re.finditer(ALLERGEN_HINTS, low)]
    allergens = sorted(set(a.strip() for a in allergens))
    return diets, veg_share, vegan_share, gf, allergens


def classify_event_type(text: str) -> tuple[Optional[str], str]:
    low = text.lower()
    scores = {}
    for et, kws in EVENT_TYPES:
        scores[et] = sum(low.count(k) for k in kws)
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return None, ABLEITUNG
    return best, ABLEITUNG


def extract(text: str, event_id: str = "EVT-NEU", synthetic: bool = True, today: date | None = None,
            extra_sources: list | None = None) -> EventFile:
    """Baut aus Freitext (E-Mail, Transkript, PDF-Text) eine Eventakte mit Provenienz."""
    today = today or date.today()
    security = detect_injection(text)
    clean, pii_map = pseudonymize(text)
    ev = EventFile(event_id=event_id, synthetic=synthetic)
    ev.raw_sources = [{"type": "text", "chars": len(text), "pseudonymized": True}] + (extra_sources or [])
    ev.security_findings = security
    ev.contact = {k: "pseudonymisiert (lokal gespeichert)" for k in pii_map}
    ev.language = detect_language(clean)
    prov = {}

    ev.event_type, st = classify_event_type(clean)
    prov["event_type"] = {"status": st if ev.event_type else TBD, "source": "Schlüsselwörter Anfrage"}

    ev.guests, all_guest_numbers = extract_guests(clean)
    if len(all_guest_numbers) > 1:
        ev.conflicts.append(f"Mehrere Gästezahlen genannt: {all_guest_numbers}. Planung mit Maximum {ev.guests}, Bestätigung nötig.")
        prov["guests"] = {"status": KONFLIKT, "source": "Anfrage", "note": str(all_guest_numbers)}
    elif ev.guests:
        prov["guests"] = {"status": VERIFIZIERT, "source": "Anfrage (Kundenangabe)"}
    else:
        ev.gaps.append("Gästezahl fehlt")
        prov["guests"] = {"status": TBD, "source": ""}

    ev.date, ev.date_partial = extract_date(clean, today)
    if ev.date:
        prov["date"] = {"status": VERIFIZIERT if not ev.date_partial else ABLEITUNG, "source": "Anfrage", "note": ev.date_partial or ""}
        try:
            weeks = (date.fromisoformat(ev.date) - today).days / 7
            if weeks < 0:
                ev.conflicts.append(f"Datum {ev.date} liegt in der Vergangenheit (Bezug {today.isoformat()}).")
            elif weeks < 4:
                ev.conflicts.append(f"Vorlauf nur {weeks:.1f} Wochen (Empfehlung 4-6 Wochen, VERIFIZIERT).")
        except ValueError:
            pass
    else:
        ev.gaps.append("Datum fehlt oder unvollständig" + (f" ({ev.date_partial})" if ev.date_partial else ""))
        prov["date"] = {"status": TBD, "source": "", "note": ev.date_partial or ""}

    ev.time_window, ev.serving_start = extract_time_window(clean)
    if not ev.time_window:
        ev.gaps.append("Zeitfenster / Servierbeginn fehlt")
    prov["time_window"] = {"status": VERIFIZIERT if ev.serving_start else (ABLEITUNG if ev.time_window else TBD), "source": "Anfrage"}

    ev.location, ev.location_type, ev.access_notes = extract_location(clean)
    if not ev.location:
        ev.gaps.append("Ort / Location fehlt")
    prov["location"] = {"status": VERIFIZIERT if ev.location else TBD, "source": "Anfrage"}
    if ev.location and ev.location not in COMPANY["region_cities"]:
        ev.conflicts.append(f"Ort '{ev.location}' nicht in der bekannten Regionsliste – Entfernung/Fahrtkosten prüfen (TBD).")
    if ev.location_type in ("outdoor", "gemischt"):
        ev.weather_protection = True if re.search(r"zelt|überdach|pavillon|scheune|halle", clean, re.I) else None
        if ev.weather_protection is None:
            ev.gaps.append("Outdoor: Wetterschutz für Ofen und Ausgabe ungeklärt")
    ev.power_available = False if any("Kein Strom" in n for n in ev.access_notes) else (None)

    ev.budget_total, ev.budget_pp = extract_budget(clean)
    prov["budget"] = {"status": VERIFIZIERT if (ev.budget_total or ev.budget_pp) else TBD, "source": "Anfrage"}

    diets, veg, vegan, gf, allergen_hits = extract_diets(clean)
    ev.dietary_notes = diets
    if isinstance(veg, tuple) and ev.guests:
        veg = round(veg[1] / ev.guests, 3)
    elif isinstance(veg, tuple):
        veg = None
    ev.veg_share, ev.vegan_share, ev.gf_count = veg, vegan, gf
    if ("vegetarisch" in diets or "vegan" in diets) and veg is None and vegan is None:
        ev.gaps.append("Vegetarischer/veganer Anteil unklar (nur 'einige/viele')")
    ev.allergen_mentions = allergen_hits
    prov["allergens"] = {"status": "HINWEIS (nie Wahrheit)", "source": "Schlüsselwörter Anfrage",
                         "note": "Nur freigegebene Allergenmatrix ist gültig."}
    if allergen_hits:
        ev.gaps.append("Allergene erwähnt – konkrete Allergene und Anzahl Betroffener schriftlich bestätigen lassen")

    if ev.guests is not None and ev.guests < 50:
        ev.conflicts.append(f"Gästezahl {ev.guests} unter Mindestgröße 50 (VERIFIZIERT). Mindestberechnung ist TBD – Geschäftsentscheidung.")

    # Priorisierte Rückfragen: maximal drei
    q = []
    if len(all_guest_numbers) > 1:
        q.append(f"Ihr habt {' und '.join(str(n) for n in all_guest_numbers)} Gäste genannt. Mit welcher Zahl sollen wir fest planen?")
    if "Gästezahl fehlt" in ev.gaps:
        q.append("Wie viele Gäste erwartet ihr ungefähr (Erwachsene und Kinder)?")
    if any(g.startswith("Datum") for g in ev.gaps):
        q.append("An welchem Datum soll gefeiert werden, und ab wann sollen die ersten Pizzen rauskommen?")
    elif "Zeitfenster / Servierbeginn fehlt" in ev.gaps:
        q.append("Ab wann sollen die ersten Pizzen aus dem Steinofen kommen, und wie lange soll ausgegeben werden?")
    if "Ort / Location fehlt" in ev.gaps:
        q.append("Wo findet das Event statt (Ort/Adresse), und kommen wir mit dem Anhänger gut bis an den Stellplatz?")
    if any("Allergene" in g for g in ev.gaps):
        q.append("Welche Allergien oder Unverträglichkeiten gibt es genau, und wie viele Gäste sind betroffen?")
    if any("Anteil unklar" in g for g in ev.gaps):
        q.append("Wie viele Gäste essen vegetarisch oder vegan?")
    if any("Wetterschutz" in g for g in ev.gaps):
        q.append("Gibt es draußen einen überdachten Platz für Ofen und Ausgabe, falls es regnet?")
    ev.questions = q[:3]
    ev.provenance = prov
    return ev
