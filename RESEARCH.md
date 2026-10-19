# RESEARCH.md – Jonis Catering Website

Gedächtnis für die nächste Session. Jede Behauptung mit Dateipfad oder Quelle.
Stand: 2026-10-19. Branch `claude/brave-knuth-jtg3ka`.

## Fragen an Jonathan (offen, blockieren Inhalte auf der Seite)

Alles, was hier steht, ist auf der Seite entweder weggelassen oder mit "im Angebot" / "auf Anfrage" formuliert, bis eine Antwort da ist.

1. **Extras-Preise.** Vorschlag (hergeleitet aus den Paketdifferenzen und `kalkulation.html`): Antipasti-Empfang zu Classic 7 € p. P., Dessert 5 € p. P., erweiterte Antipasti zu Event 3 € p. P., Zusatz-Servierstunde 150 € pauschal. Solange nicht bestätigt, steht im Code `price: null` und auf der Seite "Preis im Angebot" (`index.html`, Objekt `PRICING`).
2. **Pizza-Menge pro Person.** Seite sagt "Pizza-Flatrate" (`index.html` Pakete), `llms.txt` sagt "2 Pizzen p. P." (Classic) und "2–3" (Event). In Mails stand beides, einmal gab es deshalb Streit nach dem Event (06/2026). Eine Formulierung festlegen.
3. **Strom und Platz.** In Mails stehen acht verschiedene Strom-Angaben (von "nicht nötig" bis "16A CEE, max. 20 m") und sechs Flächenmaße (3×4 m am häufigsten, auch 2,5×6 m, 4×4 m). Für die Seite verwendet: "Öfen laufen mit Gas, normaler 230-V-Anschluss hilfreich, kein Muss; Stellfläche ca. 3 × 4 m, ebene Zufahrt; ohne Anhänger kompakter Aufbau unter Pavillon 3 × 3 m möglich." Bitte bestätigen oder korrigieren.
4. **Kinderpreis.** Belegt nur einmal: Kinder bis 12 Jahre zum halben Event-Preis (18,50 €, 09/2026). Auf der Seite: "Kinder bis 12 Jahre: reduzierter Preis, Details im Angebot". Regel festlegen und ob Kinder zur Mindestzahl zählen.
5. **Mindestgröße.** Seite und `llms.txt`: ab 50 Personen. Gebucht wurden auch 33 und 40 Personen. Formular lässt jetzt ab 20 zu, mit Hinweis "Pakete ab 50 Personen, kleinere Feiern auf Anfrage". Ok so? Alternativ Vorschlag C aus dem Plan: Mindestumsatz 1.850 € statt Mindestpersonen.
6. **Anzahlung / Zahlungsplan.** Seite: 10 % nach Angebotsbestätigung. In Mails bis 05/2026 auch 30 % und 50 %, seit 09/2026 durchgehend 10 %. Seite bleibt bei 10 %. Restzahlung wann? Barzahlung möglich?
7. **Stornierung.** Einzige Aussage in Mails (03/2026): Anzahlung wird bei kompletter Absage erstattet. Soll das als Regel auf die Seite?
8. **Finale Gästezahl.** Mails: "bis 14 Tage vor dem Event anpassbar", "Abrechnung nach tatsächlicher Gästezahl". Auf der Seite als FAQ übernommen. Bestätigen.
9. **Fahrtkosten über 10 km.** Belegte Pauschalen in Angeboten: 35 €, 120 €, 180 € (85 km). Vorschlag: Zonen 10–25 km 50 €, 25–50 km 90 €. Bis zur Antwort: "Pauschale im Angebot".
10. **Premium-Paket.** Servierzeit und Pizza-Umfang fehlen auf der Seite. Werte?
11. **Sorten.** "5 Favoriten" (Ablauf) oder "6 Sorten zur Wahl" (Pakete)?
12. **Hochzeits-Pizzen "La Sposa" und "Tartufo Bianco"** im Modal (`index.html`, Service-Daten im JS) stehen nicht auf der Karte. Behalten oder streichen?
13. **Bewertungen** im Abschnitt `#bewertungen`: echte Google-Rezensionen mit Erlaubnis für die Namen?
14. **Antwortzeit.** Seite verspricht 24 Stunden. In 4 Fällen mussten Kund:innen nachhaken, 3 Entschuldigungen für Verspätung in Mails. Versprechen halten oder auf "spätestens 2 Werktage" ändern?
15. **Getränke / Aperol-Bar / Mietporzellan.** Einmal angeboten (Getränke-Flatrate 25 € p. P., Aperol-Flatrate 12 € p. P., Cocktailbar 350 € + 10 €/Cocktail; Premium "inkl. Mietporzellan" 05/2026). Feste Leistungen mit Preis oder nur auf Anfrage?
16. **`kalkulation.html` ist öffentlich** erreichbar (nicht in `.htaccess` und nicht im Deploy-Exclude in `.github/workflows/deploy.yml`). Interne Kostenannahmen sind damit online. Sperren?
17. **JSON-LD `telephone`** ist die WhatsApp-Festnetznummer, der `tel:`-Link auf der Seite die Mobilnummer. Welche soll wo stehen?
18. **Inhaber-Foto und ein Ich-Satz** für den Kontaktbereich: lieferst du beides?

## Erkenntnisse aus 35 Kundenanfragen per Mail (01/2026 bis 10/2026)

Quelle: Gmail, nur gelesen. Vollständige anonymisierte Auswertung liegt nicht im Repo (Scratchpad `research-mails.md`), hier nur die Zahlen.

- **Anlässe:** 11 Geburtstage, 8 Hochzeiten, 7 Firmenevents, 7 private Feiern, 2 Sonstiges.
- **Gäste:** Median 70, Spanne 30 bis 150. 5 Fälle unter 50.
- **Vorlauf:** Median 14 Wochen. Hochzeiten meist 10 bis 14 Monate vorher.
- **Herkunft:** 15 Website-Formular, 15 direkt per Mail, 4 Empfehlung, 3 Kleinanzeigen, 2 am Wagen kennengelernt.
- **Ausgang:** 16 gebucht, 2 Absagen, 16 offen (9 davon ohne sichtbare Antwort per Mail).
- **Top-Rückfragen der Kund:innen:** Termin frei? (11), vegan/vegetarisch/glutenfrei (9), Strom/Platz/Zufahrt (9), Antipasti (10), Anzahlung/Zahlung/Rechnung (8), ungefährer Preis (7), Dessert (7), Telefonat gewünscht (7), Sorten (6), Kinder (5), Geschirr (4), Ablauf/Pizzen pro Stunde (4).
- **Jonathans eigene Rückfragen:** Startzeit (9), Ort/PLZ (5), Strom/Platz (4), Gästezahl (3), Umfang Antipasti/Dessert (2).
- **Formular-Ursache:** Version 06–09/2026 hatte weder Ort noch Uhrzeit. 9 von 11 Anfragen aus der Zeit nannten keine Uhrzeit. Mindestwert 50 im Gästefeld erzeugte 2 Mal falsche Zahlen.
- **Preis-Signale:** Pakete 27/37/47 € seit 05/2026 Standard. 5 Fälle mit Preisdruck, 4 Zugeständnisse (bis 20 % Nachlass, Dessert weg, Fahrtkosten gestrichen).
- **Was zur Buchung führte:** selbst probiert oder empfohlen (mind. 5 von 16), klare Paketwahl mit Preis pro Person, gelöstes Logistikproblem, schnelle Antwort.
- **Risiken:** späte Antworten (4 Nachfragen), Angebots-PDF nicht lesbar (2), Angebot im Spam (1).
- **Konsistente Logistik-Aussagen in Mails:** Aufbau 2–3 Stunden vor Beginn (4 Mal), 25–35 Pizzen pro Stunde (1 Mal, einzige Zahl), Pizza ca. 30 cm, Öfen laufen mit Gas, finale Gästezahl bis 14 Tage vorher, Abrechnung nach tatsächlichen Gästen.

## Befunde im Code (vor dem Umbau)

| Befund | Stelle | Status |
|---|---|---|
| Hero zeigte "5.0 ★", belegt sind 4,9 bei 47 Bewertungen | `index.html` Hero-Stats, `llms.txt` | korrigiert |
| Hochzeit-Karte versprach "Dessert inklusive", Dessert nur in Premium | `index.html` Services + Modal-Daten | korrigiert auf "dazubuchbar" |
| `var(--background)` nicht definiert | `index.html` CSS | korrigiert |
| Honeypot `website` und Zeitstempel werden in PHP geprüft, fehlten aber im HTML; Spam-Schutz war aus | `send_email.php`, `index.html` Formular | im Konfigurator ergänzt |
| Client-Zeitstempel gegen Server-`time()` verwirft echte Anfragen bei vorgehender Uhr | `send_email.php` | ersetzt durch `form_elapsed` |
| `extras[]` als Array würde von `clean_field` zu "Array" | `send_email.php` | eigene Helfer |
| Cloudflare-Bericht zeigt 0 Seitenaufrufe in 30 Tagen trotz Beacon | `reports/analytics.md`, Beacon in allen 4 Seiten | offen, noch nicht geprüft |
| `kalkulation.html` öffentlich | `.htaccess`, `deploy.yml` | Frage 16 |

## Preismodell: Entscheidungsvorlage

Belegt: Classic 27 €, Event 37 €, Premium 47 € p. P., ab 50 Personen, inkl. MwSt. Kalkulations-Defaults aus `kalkulation.html`: 9 € Ware pro Gast, 2,5 Helfer × 8 h × 15 € × 1,315 Lohnnebenkosten, 200 € Fixkosten.

- **Classic trägt sich bei 50 Gästen kaum** (ca. 40 € Gewinn laut eigener Kalkulation, Prime Cost 79 %). Erst ab ca. 69 Gästen 300 € Gewinn.
- **Vorschlag A (ein Basispaket + Extras):** flexibel, aber Premium-Hochzeiten würden sich auf ca. 3.270 € statt 3.760 € herunterbauen, ca. 250 € weniger Gewinn je Hochzeit. Nicht empfohlen.
- **Vorschlag B (drei Pakete + Extras), empfohlen:** Preise bleiben, Extras so gestaffelt, dass Event und Premium die ehrlich günstigeren Bündel bleiben (Classic + Antipasti 7 € + Stunde < Event; Event + Dessert 5 € + Antipasti-Plus 3 € < Premium). So umgesetzt, Extras-Preise noch `null`.
- **Vorschlag C (Mindestumsatz 1.850 € statt Mindestpersonen):** löst das Classic-Problem und öffnet Feiern unter 50 Gästen. Eigene Entscheidung, ändert "ab 50 Personen" überall.

## Was gebaut wurde (siehe Commits auf dem Branch)

- Fakten-Korrekturen und Sticky-CTA-Leiste (mobil).
- Buchungs-Baukasten in `#kontakt`: 6 Schritte, Live-Richtwert, Progressive Enhancement, `PRICING`-Objekt.
- `send_email.php`: neue Felder, Whitelists, Konfigurationsblock in der Mail, Spam-Schutz aktiv.
- FAQ erweitert um belegte Antworten, JSON-LD FAQPage synchron.

## Baseline (Characterization)

Playwright-Skript und Screenshots (390/768/1440 px) aller vier Seiten plus `report.json` (Titel, Meta, Links, Formularfelder, JSON-LD-Typen) liegen im Session-Scratchpad `lock/before/`. Für die nächste Session: Skript nach `scripts/` übernehmen, wenn Jonathan Tests im Repo will.
