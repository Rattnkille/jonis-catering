"""End-to-End-Pipeline: Anfrage -> Eventakte -> Plan -> Kalkulation -> Angebot -> Simulator -> Exporte."""
from __future__ import annotations

import time
from datetime import date
from pathlib import Path

from . import allergens, extract, planning, calc, offer, risk, simulator, export, hf_models
from .knowledge import knowledge_snapshot, CONFLICTS
from .schema import EventFile, APPROVAL_STEPS

OUT = Path(__file__).resolve().parent.parent / "out"


def run(text: str, event_id: str = "EVT-DEMO", package: str | None = None, synthetic: bool = True,
        today: date | None = None, use_hf: bool = False, out_dir: Path | None = None, distance_km: float | None = None,
        transcript: str | None = None) -> dict:
    t0 = time.time()
    full_text = text + ("\n\n[TRANSKRIPT SPRACHMEMO]\n" + transcript if transcript else "")
    ev = extract.extract(full_text, event_id=event_id, synthetic=synthetic, today=today,
                         extra_sources=[{"type": "transcript", "chars": len(transcript)}] if transcript else None)
    if distance_km is not None:
        ev.distance_km = distance_km
    pkg = package or ("event" if ev.event_type == "hochzeit" else "classic")
    ev.package = pkg
    ev.approvals = {k: {"approved": False, "by": None, "at": None, "label": lbl} for k, lbl in APPROVAL_STEPS}

    matrix = allergens.load_matrix()
    allergen_report = allergens.menu_allergen_report(matrix)
    allergen_hints = allergens.check_mentions(ev.allergen_mentions, matrix)
    pl = planning.plan(ev, pkg) if ev.guests else None
    kalk = calc.calculate(ev.guests, pkg, helpers=pl["staff"]["helpers"], hours=pl["staff"]["hours_per_helper"]) if pl else None
    risks = risk.assess(ev, pl, today) if pl else []
    variants = offer.offer_variants(ev)
    reply = offer.response_draft(ev, recommended=pkg)
    signs = offer.menu_signs(pl["menu"], allergen_report) if pl else []
    brief = offer.team_brief(ev, pl, risks) if pl else "Kein Einsatzbrief: Gästezahl fehlt."
    sims = simulator.simulate_all(ev, pkg) if pl else []
    hf = {"triage": hf_models.zero_shot_triage(full_text) if use_hf else {"available": False, "reason": "use_hf=False"}}

    critical = []
    if allergen_report["release_blocked"]:
        critical.append("Allergen-Matrix nicht freigegeben")
    if ev.security_findings:
        critical.append("Sicherheitsauffälligkeit im Eingabedokument")
    if ev.conflicts:
        critical.append(f"{len(ev.conflicts)} Konflikt(e)")
    result = {
        "event": ev.to_dict(), "package": pkg, "plan": pl, "calc": kalk, "risks": risks, "offers": variants,
        "reply_draft": reply, "signs": signs, "team_brief": brief, "simulations": sims,
        "allergen_report": allergen_report, "allergen_hints": allergen_hints, "hf": hf,
        "source_conflicts": CONFLICTS, "auto_release_blocked": bool(critical), "blockers": critical,
        "runtime_s": round(time.time() - t0, 3), "knowledge_checked": knowledge_snapshot()["checked"],
    }
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        export.write_json(result["event"], out_dir / f"{event_id}_eventakte.json")
        export.write_json(result, out_dir / f"{event_id}_full.json")
        if pl:
            export.write_shopping_csv(pl["shopping"], out_dir / f"{event_id}_einkauf.csv")
            export.write_shopping_xlsx(pl["shopping"], pl["distribution"], out_dir / f"{event_id}_einkauf.xlsx")
            export.write_brief_html(brief, f"Einsatzbrief {event_id}", out_dir / f"{event_id}_einsatzbrief.html")
        (out_dir / f"{event_id}_antwort.txt").write_text(reply, encoding="utf-8")
        result["exports"] = sorted(str(p.relative_to(out_dir.parent)) for p in out_dir.glob(f"{event_id}_*"))
    return result


def summary(result: dict) -> str:
    ev = result["event"]; pl = result["plan"]; k = result["calc"]
    lines = [f"Eventakte {ev['event_id']} ({'SYNTHETISCHE DEMO' if ev['synthetic'] else 'real'})",
             f"  Typ: {ev['event_type']} | Datum: {ev['date']} | Ort: {ev['location']} | Gäste: {ev['guests']} | Paket: {result['package']}",
             f"  Lücken: {len(ev['gaps'])} | Konflikte: {len(ev['conflicts'])} | Rückfragen: {len(ev['questions'])} | Security: {len(ev['security_findings'])}"]
    if pl:
        lines.append(f"  Pizzen: {pl['pizzas_total']} | Teig: {pl['dough_kg']} kg | Team: {pl['staff']['helpers']} x {pl['staff']['hours_per_helper']} h | Ofen: {'ok' if pl['oven']['ok'] else 'ENGPASS'}")
    if k:
        r = k["results"]
        lines.append(f"  Umsatz netto {r['umsatz_netto']:.0f} € | Prime Cost {r['prime_cost_pct']} % ({r['prime_status']}) | Gewinn {r['gewinn']:.0f} € [{r['gewinn_band'][0]:.0f}..{r['gewinn_band'][1]:.0f}] (ANNAHME)")
    lines.append(f"  Auto-Freigabe blockiert: {result['auto_release_blocked']} -> {result['blockers']}")
    lines.append(f"  Laufzeit: {result['runtime_s']} s")
    return "\n".join(lines)
