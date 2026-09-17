# Chancenportfolio ChatGPT + Hugging Face für JONIS (Phase 1)

Bewertung 1 (schwach) bis 5 (stark). Datenreife: wie viele echte Daten heute vorhanden sind. Zeit bis Nutzen in Wochen.

| # | Anwendungsfall | Phase | Geschäftswert | Datenreife | Aufwand | Risiko | Laufende Kosten | Zeit bis Nutzen | Entscheidung |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **FORNO TWIN**: Anfrage → Eventakte → Plan → Kalkulation → Simulator → Lern-Loop | alle | 5 | 3 | 4 | 2 | 0 € (lokal) | 0 (Pilot da) | **Flaggschiff** |
| 2 | **Anfrage-Triage + Antwortentwurf in 24 h** (Regeln + optional mDeBERTa, Antwort im JONIS-Ton) | Akquise | 5 | 4 | 1 | 1 | 0 € | 0 | **Quick Win 1** (Teil des Twins, sofort nutzbar) |
| 3 | **Mengen- und Einkaufsplan als CSV/XLSX pro Event** (deterministisch, mit Parameterstatus) | Planung | 4 | 3 | 1 | 1 | 0 € | 0 | **Quick Win 2** |
| 4 | **Pizza Pulse**: anonyme Präferenzen live → nächste Charge | Durchführung | 3 | 2 | 2 | 1 | 0 € | 2 | **Überraschungsfunktion** (Pilot gebaut, Tab 6) |
| 5 | Waste Lens: Restmengen wiegen → Kalibrierung Puffer/Teigling | Nachbereitung | 4 | 1 | 2 | 1 | 0 € | 4 (2 Events) | gebaut, wartet auf Ist-Daten |
| 6 | Sprachmemo → Transkript → Eventakte (whisper-tiny lokal, primeline turbo german als Kandidat) | Akquise | 3 | 2 | 2 | 2 | 0 € lokal | 1 (auf Mac) | vorbereitet, Adapter da |
| 7 | Location Scout: Foto/Video → Hinweise Zufahrt, Stellfläche, Wetterschutz (SmolVLM2) | Planung | 3 | 1 | 3 | 3 | 0 € lokal | 4 | Backlog B8 |
| 8 | Wissensbasis-Retrieval (FAQ, SOPs, Menü) für Kundenantworten und Team-Onboarding (MiniLM/e5) | Akquise/Team | 3 | 3 | 2 | 1 | 0 € | 2 | lexikalischer Fallback gebaut, Embeddings vorbereitet |
| 9 | B2B-Weihnachtsfeier-Kampagne: Segmentierung eingehender Firmenanfragen und Vorlagen | Akquise | 4 | 2 | 2 | 2 | 0 € | 3 | später, nach Triage-Daten |
| 10 | Fine-Tuning eines Extraktionsmodells auf JONIS-Anfragen | alle | 2 | 1 | 5 | 3 | GPU-Kosten | 12+ | **nicht jetzt** (Regeln erreichen 100 % auf Testfällen; keine echten Daten) |

Begründung Flaggschiff: Der Twin bündelt 2, 3, 4, 5 in einem Datenmodell und liefert den Wow-Moment (unstrukturierte Anfrage → prüfbare Akte, drei Angebote, Einkauf, Einsatzbrief, drei Störungsszenarien) ohne Modellkosten.
