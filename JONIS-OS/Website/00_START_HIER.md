---
tags:
  - website
  - start
status: aktiv
erstellt: 2026-05-18
aktualisiert: 2026-05-20
---

# Website — Start

jonis-catering.de — Premium-Auftritt mit Conversion-Fokus.
Single-Page-Site, statisches HTML.

## Dateien

- [[01_AKTUELL]] — laufende Änderungen
- [[02_ENTSCHEIDUNGEN]] — Struktur, Copy, Tech-Stack
- [[03_IDEEN]] — Verbesserungen, Tests

## Asset im Repo

- `index.html` im Repo-Root — aktueller Stand, ca. 2720 Zeilen, alles inline (CSS + JS)
- Kontaktformular sendet an `send_email.php` (nicht im Repo — serverseitig)
- Bilder erwartet unter `img/` (galerie-event, galerie-ofen, galerie-pizza, galerie-auswahl, galerie-scheune)

## Seitenstruktur (Anker)

1. Hero
2. `#leistungen` — Leistungen
3. `#pakete` — Pakete (siehe [[../Catering/Pakete]])
4. `#galerie` — Galerie
5. `#menu` — Pizza-Karte (siehe [[../Catering/Menue]])
6. `#ablauf` — So funktioniert's (3 Schritte)
7. `#bewertungen` — Kundenbewertungen
8. `#faq` — Häufige Fragen
9. `#kontakt` — Kontaktformular und Kontaktkarten
10. Footer mit Impressum- und Datenschutz-Modal

## Kontaktdaten auf der Seite

Telefon +49 176 3237 0375 · info@jonis-catering.de · WhatsApp · Konsul-Smidt-Straße 35, 28217 Bremen.
Stammdaten zentral in [[../Catering/00_START_HIER]].

## Querverweise

- Catering: [[../Catering/00_START_HIER|Catering]] (Pakete, Preise, Tonalität)
- Marketing: [[../Marketing/00_START_HIER|Marketing]] (Branding, Bilder)
- Prompts: [[../Prompts/00_START_HIER|Prompts]] (`website-premium-copy.md`)

## CRO-Prinzipien

- Premium-Wirkung über alles
- Vertrauen statt Druck
- klare CTA-Hierarchie
- keine Billig-Optik, keine generische AI-Sprache

## Offene Punkte

- Impressum enthält `TODO: Impressum-Daten anpassen` — prüfen
- `send_email.php` nicht versioniert — Backup / Doku fehlt
