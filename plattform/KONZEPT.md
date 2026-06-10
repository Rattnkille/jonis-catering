# PizzaPool – Konzept (Arbeitstitel)

> Das Netzwerk für mobile Pizza-Caterer: Anfragen teilen, Tools nutzen, gemeinsam wachsen.

Stand: Juni 2026 · Initiator: Jonathan (Jonis Catering, Bremen)

---

## 1. Die Idee in einem Satz

Eine Plattform, auf der mobile Pizza-Caterer (umgebaute Anhänger, Foodtrucks,
mobile Holzöfen) Anfragen, die sie selbst nicht bedienen können, an passende
Kolleg:innen in anderen Städten weiterreichen – und im Gegenzug Anfragen aus
ihrer Region erhalten. Dazu kommen Tools, die den Alltag als
Solo-Caterer leichter machen.

## 2. Das Problem

Wer mobiles Pizza-Catering anbietet, kennt diese Situationen:

1. **Verlorene Anfragen:** Eine Hochzeit in München fragt an – aber du sitzt in
   Bremen. Oder der Termin ist schon belegt. Die Anfrage (und der Umsatz) ist weg,
   der Kunde muss von vorne suchen.
2. **Einzelkämpfertum:** Jeder baut sich allein dieselben Dinge: Preiskalkulation,
   Angebots-Vorlagen, Verträge, Einkaufslisten, Buchungsübersicht.
3. **Keine Sichtbarkeit außerhalb von Instagram:** Endkunden finden Caterer fast
   nur über Instagram oder Google – ein Verzeichnis speziell für mobiles
   Pizza-Catering gibt es nicht.

Die Szene ist auf Instagram gut sichtbar und untereinander vernetzt – Anfragen
werden heute schon informell per DM weitergereicht. Es fehlt nur der
verlässliche, faire Kanal dafür.

## 3. Die Lösung & das Nutzenversprechen

**Kern-Nutzen (MVP): Anfragen-Vermittlung.**

> „Verwandle Anfragen, die du absagen musst, in Einnahmen – und bekomme
> Anfragen geschenkt, wenn andere absagen müssen."

Warum Vermittlung zuerst (und nicht Tools oder Verzeichnis)?

- Es ist der einzige Nutzen, den **kein Caterer allein** haben kann →
  Netzwerkeffekt als Burggraben. Tools kann jeder kopieren, ein Netzwerk nicht.
- Es knüpft an **bestehendes Verhalten** an (DM-Weiterleitungen) – die Plattform
  muss kein neues Verhalten erzeugen, nur ein bestehendes verbessern.
- Es passt exakt zum Geschäftsmodell (Gebühr pro vermittelter Anfrage).
- Tools und Verzeichnis kommen als Ausbaustufen dazu (siehe Roadmap).

## 4. Zielgruppe

**Phase 1 – Pizza zuerst:** Mobile Pizza-Caterer im DACH-Raum mit eigenem Setup
(umgebauter Anhänger, Ape, Foodtruck, mobiler Holzofen). Meist Solo oder
2-Personen-Betriebe, Akquise fast ausschließlich über Instagram.
Scharfes Profil, homogene Bedürfnisse – Tools passen für alle gleich gut.

**Phase 2 – später öffnen:** Weitere mobile Food-Caterer (Grill, Pasta, Burger,
Kaffee). Erst wenn die Pizza-Nische funktioniert und die Mechanik bewiesen ist.

## 5. Wie die Vermittlung konkret funktioniert (MVP-Flow)

1. **Profil anlegen:** Caterer registriert sich mit Name, Region/Radius,
   Setup, Kapazität (Gäste min/max), Instagram, Preisrahmen.
2. **Anfrage einstellen:** Caterer A bekommt eine Anfrage, die er nicht bedienen
   kann (Ort/Termin), und stellt sie mit Eckdaten ein (Ort, Datum, Gästezahl,
   Anlass, Budgetrahmen). Kontaktdaten des Endkunden bleiben zunächst verdeckt.
3. **Matching & Benachrichtigung:** Passende Caterer in der Region werden
   benachrichtigt (E-Mail/WhatsApp) und können die Anfrage annehmen.
4. **Übergabe:** Bei Annahme werden die Kontaktdaten freigegeben; Caterer B
   übernimmt die Anfrage und meldet zurück, ob daraus eine Buchung wurde.
5. **Fairness:** Wer Anfragen einstellt, wird bei der Vergabe eingehender
   Anfragen bevorzugt (Geben-und-Nehmen-Prinzip, sichtbar als einfacher
   Karma-Wert).

## 6. Feature-Roadmap

| Phase | Inhalt | Ziel |
|-------|--------|------|
| **0 – Validierung (jetzt)** | Landingpage mit Warteliste (`plattform/index.html`), Instagram-Outreach an 50–100 Caterer | Beweisen, dass Bedarf existiert |
| **1 – MVP Vermittlung** | Profile, Anfragen einstellen/annehmen, Benachrichtigungen, einfaches Matching nach Region/Datum | Erste echte Vermittlungen |
| **2 – Tools (Pro-Abo)** | Preiskalkulation (Basis existiert: `kalkulation.html`), Angebots-PDF-Generator, Buchungskalender, Vertrags- & E-Mail-Vorlagen | Wiederkehrender Umsatz, täglicher Nutzen |
| **3 – Verzeichnis & Sichtbarkeit** | Öffentliche Profile („Pizza-Catering in [Stadt]"), SEO, Anfrageformular für Endkunden direkt auf der Plattform | Eigener Anfragen-Strom, unabhängig von Instagram |
| **4 – Community & Einkauf** | Geschlossener Austausch, Equipment-Börse, Sammelbestellungen (Mehl, Verpackung, San-Marzano…) | Bindung, weiterer Mehrwert |

## 7. Geschäftsmodell (Kombi)

| Stufe | Preis | Enthalten |
|-------|-------|-----------|
| **Free** | 0 € | Profil, Anfragen empfangen & einstellen, Community-Basis |
| **Vermittlungsgebühr** | z. B. 15 € pro **angenommener** Anfrage (nicht pro Weiterleitung) – die ersten 3 frei | Fair: Kosten entstehen nur, wenn Wert entsteht |
| **Pro-Abo** | 19–29 €/Monat | Alle Tools (Kalkulation, Angebots-PDF, Kalender, Vorlagen), bevorzugtes Matching, öffentliches Verzeichnis-Profil |

Grundsätze: Einstieg immer kostenlos (Henne-Ei-Problem!), Gebühren erst, wenn
nachweislich Wert geflossen ist. Preise sind Hypothesen – in
Validierungsgesprächen testen.

## 8. Validierungsplan (nächste 4–6 Wochen)

1. **Landingpage live schalten** (liegt unter `plattform/` – auf der bestehenden
   Domain z. B. unter `jonis-catering.de/plattform/`, später eigene Domain).
2. **Liste bauen:** 50–100 Pizza-Caterer auf Instagram recherchieren
   (Suchbegriffe: „mobiles pizza catering", „pizzatrailer", „pizza foodtruck"
   + Städtenamen).
3. **Persönlicher Outreach per DM** – als Kollege, nicht als Verkäufer:
   „Ich mache das Gleiche in Bremen, mir gehen ständig Anfragen verloren,
   ich baue gerade was dagegen – schau mal."
4. **Messen:** Ziel z. B. 30 Wartelisten-Einträge und 10 ehrliche Gespräche
   (Telefon/Video). Kernfragen: Wie viele Anfragen sagst du pro Monat ab?
   Was würdest du für eine vermittelte Anfrage zahlen? Welche Aufgabe nervt
   dich am meisten?
5. **Entscheiden:** Genug Resonanz → MVP Phase 1 bauen. Wenig Resonanz →
   Hypothese anpassen (z. B. Tools zuerst) statt blind weiterbauen.

## 9. Risiken & offene Fragen

- **Henne-Ei:** Vermittlung braucht Dichte pro Region. Gegenmittel: regional
  starten (Norddeutschland), Einstieg kostenlos, dein eigenes
  Instagram-Netzwerk als Startkapital.
- **Umgehung der Gebühr:** Caterer könnten sich nach dem ersten Kontakt direkt
  einigen. Gegenmittel: Gebühr klein halten (15 € tut nicht weh), Karma-System,
  Wert der Plattform über die reine Vermittlung hinaus (Tools).
- **Vertrauen/Abwerben:** Angst, dass Kollegen Kunden „klauen". Gegenmittel:
  Kontaktdaten erst nach verbindlicher Annahme, klare Spielregeln.
- **DSGVO:** Weitergabe von Endkunden-Daten braucht deren Einwilligung –
  ins Anfrage-Formular von Anfang an einbauen („Ich bin einverstanden, dass
  meine Anfrage an einen Partner-Caterer weitergegeben wird").
- **Rechtsform/Haftung:** Ab echten Zahlungsflüssen klären (Kleingewerbe
  reicht anfangs vermutlich, später ggf. UG/GmbH).

## 10. Namensideen (Arbeitstitel: PizzaPool)

PizzaPool · Ofennetz · Pizzakollektiv · TeigWerk Netzwerk · NapoliCrew ·
SliceUnited. Vor dem Launch: Domain- und Markenverfügbarkeit prüfen.

## 11. Nächste Schritte

- [ ] Landingpage live schalten und Link in der Instagram-Bio testen
- [ ] Outreach-Liste (50–100 Accounts) anlegen
- [ ] 10 Validierungsgespräche führen, Antworten dokumentieren
- [ ] Danach: Build-Prompt für den MVP (Phase 1) formulieren – auf Basis der
      Gesprächsergebnisse, in einem eigenen Repo (die Plattform braucht ein
      Backend und wächst aus dem Statische-Seite-Setup dieses Repos heraus)
