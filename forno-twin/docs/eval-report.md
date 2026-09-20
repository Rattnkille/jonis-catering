# FORNO TWIN – Evaluationsbericht

Stand: 2026-09-20T09:16:53+00:00 | Testfälle: synthetisch (data/synthetic_events.json)

## Kennzahlen

| Metrik | Wert | Vorheriger Lauf |
|---|---|---|
| Testfälle vollständig bestanden | 18/18 | 18/18 |
| Einzelprüfungen bestanden | 129/129 (100.0%) | 1.0 |
| Ø Vollständigkeit Eventakte (5 Kernfelder) | 87% | 0.867 |
| Kritische Allergenfehler | 0 | 0 |
| Ø Laufzeit pro Fall | 0.0016 s | 0.0032 |

Kritische Allergenfehler müssen 0 sein. Ein einziger ungeprüfter Allergen-Fakt blockiert die Freigabe.

## Ergebnisse pro Testfall

| Fall | Art | Bestanden | Vollständigkeit | Fehlgeschlagen |
|---|---|---|---|---|
| SYN-001 | normal_hochzeit | 13/13 | 100% | – |
| SYN-002 | firmenevent_klar | 9/9 | 100% | – |
| SYN-003 | unvollstaendig | 7/7 | 20% | – |
| SYN-004 | unter_minimum | 6/6 | 100% | – |
| SYN-005 | widerspruch | 7/7 | 100% | – |
| SYN-006 | mehrsprachig_en | 8/8 | 100% | – |
| SYN-007 | mehrsprachig_it | 7/7 | 80% | – |
| SYN-008 | allergen_unklar | 6/6 | 100% | – |
| SYN-009 | knappes_budget | 7/7 | 100% | – |
| SYN-010 | prompt_injection | 7/7 | 100% | – |
| SYN-011 | datenschutzfalle | 5/5 | 100% | – |
| SYN-012 | gross_event | 6/6 | 60% | – |
| SYN-013 | kurzer_vorlauf | 5/5 | 100% | – |
| SYN-014 | vegan_stark | 6/6 | 100% | – |
| SYN-015 | leer_spam | 5/5 | 0% | – |
| SYN-016 | zahlwoerter | 9/9 | 100% | – |
| SYN-017 | plz_und_adresse | 9/9 | 100% | – |
| SYN-018 | zahlwort_dutzend_klein | 7/7 | 100% | – |

## Fehlerbeispiele

Keine fehlgeschlagenen Prüfungen in diesem Lauf. Bekannte Grenzen siehe docs/status.md.

## Bekannte Grenzen (nicht durch Tests abgedeckt)

- Regelbasierte Extraktion: unbekannte Formulierungen (z.B. 'zwei Dutzend Leute') werden nicht erkannt.
- Ortserkennung nur für die Regionsliste plus 'in <Großgeschrieben>'; Straßenadressen werden nicht geparst.
- Sprachmemo/Audio: ASR-Modelle sind integriert, konnten in dieser Umgebung aber nicht geladen werden (Hub blockiert).
- Kosten: alle Werte basieren auf Rechner-Standardwerten (ANNAHME).
