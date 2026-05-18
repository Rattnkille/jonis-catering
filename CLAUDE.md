# CLAUDE SYSTEM WORKFLOW — JONIS OS

Du arbeitest innerhalb eines projektbasierten Betriebssystems für mehrere Geschäfts- und Technikbereiche.

Deine Aufgabe ist nicht nur Antworten zu liefern, sondern:
- Wissen strukturiert zu verwalten
- Projektkontext stabil zu halten
- Entscheidungen nachvollziehbar zu dokumentieren
- Wiederholungen und Kontextverlust zu minimieren
- Bestehende Systeme zuerst zu prüfen bevor neue erstellt werden

---

## VAULT

Der Obsidian-Vault liegt unter `/JONIS-OS`.
Einstieg: `JONIS-OS/00_START_HIER.md` (MOC mit Wikilinks zu allen Bereichen).

Bei jedem neuen Task:
1. `JONIS-OS/00_START_HIER.md` lesen
2. Relevanten Bereich öffnen (z. B. `JONIS-OS/Catering/`)
3. Dort `00_START_HIER.md`, `01_AKTUELL.md`, `02_ENTSCHEIDUNGEN.md`, `03_IDEEN.md` prüfen
4. Bestehende SOPs, Prompts, Chat-Summaries berücksichtigen

---

## GRUNDREGELN

### 1. Bestehende Struktur zuerst prüfen

Bevor du:
- neue Dateien erstellst
- neue Systeme vorschlägst
- neue Prozesse definierst
- neue Prompts schreibst
- neue Dokumentationen erzeugst

musst du zuerst prüfen:
- ob bereits Dateien existieren
- ob bereits Regeln definiert wurden
- ob frühere Entscheidungen dokumentiert sind
- ob ähnliche Systeme schon vorhanden sind
- ob ältere Chat-Zusammenfassungen relevant sind

Keine Duplikate erzeugen wenn bereits funktionierende Strukturen existieren.

### 2. Projektkontext laden

Wichtige Startdateien pro Bereich:
- `00_START_HIER.md`
- `01_AKTUELL.md`
- `02_ENTSCHEIDUNGEN.md`
- `03_IDEEN.md`

Wenn vorhanden:
- SOPs (`JONIS-OS/SOPs/`)
- Promptbibliothek (`JONIS-OS/Prompts/`)
- Chat-Summaries (`JONIS-OS/Chat-Summaries/`)
- Angebotsvorlagen
- technische Dokumentationen

### 3. Projektstruktur

```
/JONIS-OS
    /Catering
    /Website
    /Marketing
    /Equipment
    /Solar
    /Finanzen
    /Automationen
    /Prompts
    /Chat-Summaries
    /SOPs
```

Jeder Bereich enthält:
- `00_START_HIER.md`
- `01_AKTUELL.md`
- `02_ENTSCHEIDUNGEN.md`
- `03_IDEEN.md`
- relevante Assets, Prompts, SOPs

### 4. Dokumentationspflicht

Wichtige Entscheidungen immer dokumentieren in `02_ENTSCHEIDUNGEN.md`:
- Was entschieden wurde
- Warum
- Vorteile / Nachteile
- Offene Punkte
- Nächste Schritte

Format-Beispiel:

```
## 2026-05-18 — Dome XL Entscheidung

ENTSCHEIDUNG:
Dome XL bevorzugt gegenüber Arc XL.

GRUND:
Mehr thermische Stabilität bei großen Events.

OFFEN:
Transportlösung prüfen.

NÄCHSTER SCHRITT:
Befestigung im Anhänger testen.
```

### 5. Chat-Zusammenfassungen

Wichtige Chats nach `JONIS-OS/Chat-Summaries/` als Markdown speichern.

Format:
```
## Thema
## Erkenntnisse
## Entscheidungen
## Offene Punkte
## ToDos
```

### 6. Prompt-Management

Vor neuen Prompts:
- prüfen ob ähnliche Prompts in `JONIS-OS/Prompts/` existieren
- bestehende erweitern statt duplizieren

Beispiele:
- `angebot-hochzeit.md`
- `website-premium-copy.md`
- `social-post-premium.md`
- `kalkulation-event.md`

### 7. Tonalität — Jonis Catering

- keine Emojis
- keine aggressive Werbesprache
- hochwertig, sachlich, ruhig, klar strukturiert

Positionierung: Premium neapolitanisches Pizza Catering.

Begriffe:
- „Steinofen" bevorzugen
- nicht wie günstige Pizzeria wirken
- Fokus auf Event-Catering

### 8. Angebotslogik

Bei Eventanfragen fehlende Informationen abfragen:
- Anlass
- Datum
- Ort
- Gästezahl

Wenn vorhanden: passendes Paket empfehlen, konkrete Preisrange, nicht unnötig über Preise diskutieren.
Nach Bestätigung: Rechnungsdaten anfordern, Angebot vorbereiten.

### 9. Website & CRO

Ziele: Premium-Wirkung, hohe Conversion, Vertrauen, hochwertige Eventwirkung.
Vermeiden: Billigwirkung, Überladenheit, generische AI-Sprache.

Vor Änderungen:
- bestehende Website-Struktur prüfen (`index.html` im Repo-Root)
- bestehende Texte analysieren
- bestehende Entscheidungen berücksichtigen

### 10. Technische Projekte

Immer dokumentieren:
- getestete Hardware / Software
- Vor- / Nachteile
- Kosten
- Status
- offene Probleme

Bestehende Systeme berücksichtigen:
- Apple Ecosystem
- VS Code, Claude, ChatGPT
- Obsidian
- Canva
- SumUp
- FYRST / Wise / Revolut
- Hosting / DNS-Strukturen

### 11. Prioritäten

1. Klarheit
2. Wiederverwendbarkeit
3. Konsistenz
4. Dokumentation
5. Skalierbarkeit
6. Automatisierung

Erst stabile Prozesse. Dann Automatisierung.

### 12. Arbeitsweise

Immer:
- strukturiert denken
- vorhandenes Wissen nutzen
- Kontext erhalten
- Entscheidungen nachvollziehbar halten
- bestehende Systeme respektieren

Vermeide:
- redundante Dokumente
- unnötige Neuaufbauten
- Kontextverlust
- widersprüchliche Entscheidungen
- unnötige Tool-Wechsel

Ziel: ein langfristig stabiles Wissens- und Betriebssystem für alle Geschäftsbereiche.
