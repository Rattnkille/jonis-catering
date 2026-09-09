"""Evaluationslauf über alle synthetischen Testfälle. Schreibt docs/eval-report.md und eval/history.jsonl.

Metriken: Extraktionsgenauigkeit (Feldtreffer), Vollständigkeit der Eventakte, Rückfragequalität,
kritische Allergenfehler (muss 0 sein), Sicherheitsfälle erkannt, Laufzeit.
"""
from __future__ import annotations

import json
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from forno_twin import pipeline, extract  # noqa: E402
from forno_twin.demo_data import load_events  # noqa: E402

TODAY = date(2026, 9, 9)
HISTORY = ROOT / "eval" / "history.jsonl"
REPORT = ROOT / "docs" / "eval-report.md"


def check_case(e: dict) -> dict:
    exp = e.get("expected", {})
    t0 = time.time()
    res = pipeline.run(e["text"], event_id=e["id"], transcript=e.get("transcript"), distance_km=e.get("distance_km"), today=TODAY)
    dt = time.time() - t0
    ev = res["event"]
    checks = []

    def chk(name, ok, detail=""):
        checks.append({"check": name, "ok": bool(ok), "detail": detail})

    for field in ("event_type", "guests", "date", "location", "serving_start", "budget_total", "budget_pp", "language", "gf_count"):
        if field in exp:
            chk(field, ev.get(field) == exp[field], f"erwartet {exp[field]!r}, erhalten {ev.get(field)!r}")
    if "location_type" in exp:
        chk("location_type", ev.get("location_type") in (exp["location_type"], "gemischt"), ev.get("location_type"))
    if "veg_share" in exp:
        chk("veg_share", abs((ev.get("veg_share") or 0) - exp["veg_share"]) < 0.01)
    if "vegan_share" in exp:
        chk("vegan_share", abs((ev.get("vegan_share") or 0) - exp["vegan_share"]) < 0.01)
    if exp.get("has_conflict_guests"):
        chk("konflikt_gaeste", any("Gästezahlen" in c for c in ev["conflicts"]))
    if exp.get("conflict_min_guests"):
        chk("konflikt_minimum", any("Mindestgröße" in c for c in ev["conflicts"]))
    if exp.get("allergen_hint"):
        chk("allergen_hinweis", len(ev["allergen_mentions"]) >= exp.get("allergen_min", 1), str(ev["allergen_mentions"]))
    if exp.get("question_allergen"):
        chk("rueckfrage_allergen", any("Allerg" in q for q in ev["questions"]))
    if "gaps_min" in exp:
        chk("luecken", len(ev["gaps"]) >= exp["gaps_min"], str(ev["gaps"]))
    if "questions_max" in exp:
        chk("rueckfragen_max3", 1 <= len(ev["questions"]) <= exp["questions_max"])
    if exp.get("power_known"):
        chk("strom_bekannt", ev.get("power_available") is not None or any("Strom" in n for n in ev["access_notes"]))
    if exp.get("power_false"):
        chk("kein_strom", ev.get("power_available") is False)
    if "security_findings_min" in exp:
        chk("security", len(ev["security_findings"]) >= exp["security_findings_min"])
        chk("kein_rabatt_im_entwurf", "Rabatt" not in res["reply_draft"] and "hacker@" not in res["reply_draft"])
    if exp.get("pii_pseudonymized"):
        dumped = json.dumps(res["event"])
        chk("pii_entfernt", "@example.com" not in dumped and "9876543" not in dumped and len(ev["contact"]) >= exp.get("contact_placeholders_min", 1))
    if exp.get("over_budget_all"):
        chk("budget_fit", all(v["fit_notes"] for v in res["offers"]))
    if exp.get("oven_bottleneck"):
        chk("ofen_engpass", res["plan"] and not res["plan"]["oven"]["ok"])
    if exp.get("risk_big"):
        chk("risiko_gross", any("150" in r["risk"] for r in res["risks"]))
    if exp.get("short_lead"):
        chk("kurzer_vorlauf", any("Vorlauf" in c for c in ev["conflicts"]))
    if exp.get("no_plan"):
        chk("kein_plan_ohne_gaeste", res["plan"] is None)
    # Immer: Allergen-Regel und Statusdisziplin
    chk("allergen_release_blocked", res["allergen_report"]["release_blocked"] is True, "Matrix nicht freigegeben -> muss blockieren")
    chk("kein_holzofen", "Holzofen" not in res["reply_draft"])
    if res["calc"]:
        chk("kalkulation_status_sichtbar", all("status" in v for v in res["calc"]["inputs"].values()))
    passed = sum(1 for c in checks if c["ok"])
    completeness = sum(1 for f in ("event_type", "guests", "date", "location", "serving_start") if ev.get(f)) / 5
    return {"id": e["id"], "kind": e["kind"], "checks": checks, "passed": passed, "total": len(checks),
            "completeness": round(completeness, 2), "runtime_s": round(dt, 3),
            "allergen_critical_errors": 0 if res["allergen_report"]["release_blocked"] else 1}


def main() -> int:
    events = load_events()
    results = [check_case(e) for e in events]
    total = sum(r["total"] for r in results); passed = sum(r["passed"] for r in results)
    cases_ok = sum(1 for r in results if r["passed"] == r["total"])
    crit = sum(r["allergen_critical_errors"] for r in results)
    summary = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "cases": len(results), "cases_ok": cases_ok,
               "checks_passed": passed, "checks_total": total, "accuracy": round(passed / total, 4) if total else 0,
               "avg_completeness": round(sum(r["completeness"] for r in results) / len(results), 3),
               "allergen_critical_errors": crit, "avg_runtime_s": round(sum(r["runtime_s"] for r in results) / len(results), 4),
               "failed": [f"{r['id']}:{c['check']}" for r in results for c in r["checks"] if not c["ok"]]}
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    prev = None
    if HISTORY.exists():
        lines = HISTORY.read_text(encoding="utf-8").strip().splitlines()
        prev = json.loads(lines[-1]) if lines else None
    with open(HISTORY, "a", encoding="utf-8") as f:
        f.write(json.dumps(summary, ensure_ascii=False) + "\n")

    md = ["# FORNO TWIN – Evaluationsbericht", "", f"Stand: {summary['ts']} | Testfälle: synthetisch (data/synthetic_events.json)", "",
          "## Kennzahlen", "", "| Metrik | Wert | Vorheriger Lauf |", "|---|---|---|",
          f"| Testfälle vollständig bestanden | {cases_ok}/{len(results)} | {prev['cases_ok'] if prev else '–'}/{prev['cases'] if prev else '–'} |",
          f"| Einzelprüfungen bestanden | {passed}/{total} ({summary['accuracy']:.1%}) | {prev['accuracy'] if prev else '–'} |",
          f"| Ø Vollständigkeit Eventakte (5 Kernfelder) | {summary['avg_completeness']:.0%} | {prev['avg_completeness'] if prev else '–'} |",
          f"| Kritische Allergenfehler | {crit} | {prev['allergen_critical_errors'] if prev else '–'} |",
          f"| Ø Laufzeit pro Fall | {summary['avg_runtime_s']} s | {prev['avg_runtime_s'] if prev else '–'} |", "",
          "Kritische Allergenfehler müssen 0 sein. Ein einziger ungeprüfter Allergen-Fakt blockiert die Freigabe.", "",
          "## Ergebnisse pro Testfall", "", "| Fall | Art | Bestanden | Vollständigkeit | Fehlgeschlagen |", "|---|---|---|---|---|"]
    for r in results:
        failed = ", ".join(c["check"] for c in r["checks"] if not c["ok"]) or "–"
        md.append(f"| {r['id']} | {r['kind']} | {r['passed']}/{r['total']} | {r['completeness']:.0%} | {failed} |")
    md += ["", "## Fehlerbeispiele", ""]
    any_fail = False
    for r in results:
        for c in r["checks"]:
            if not c["ok"]:
                any_fail = True
                md.append(f"- **{r['id']} / {c['check']}**: {c['detail']}")
    if not any_fail:
        md.append("Keine fehlgeschlagenen Prüfungen in diesem Lauf. Bekannte Grenzen siehe docs/status.md.")
    md += ["", "## Bekannte Grenzen (nicht durch Tests abgedeckt)", "",
           "- Regelbasierte Extraktion: unbekannte Formulierungen (z.B. 'zwei Dutzend Leute') werden nicht erkannt.",
           "- Ortserkennung nur für die Regionsliste plus 'in <Großgeschrieben>'; Straßenadressen werden nicht geparst.",
           "- Sprachmemo/Audio: ASR-Modelle sind integriert, konnten in dieser Umgebung aber nicht geladen werden (Hub blockiert).",
           "- Kosten: alle Werte basieren auf Rechner-Standardwerten (ANNAHME).", ""]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(md), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if crit == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
