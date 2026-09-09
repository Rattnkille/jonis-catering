"""JONIS FORNO TWIN – lokales Operations-Cockpit (Gradio).

Start: python app.py   (oder: make run)
Alle Berechnungen laufen lokal. Keine Daten verlassen den Rechner.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import gradio as gr

from forno_twin import pipeline, learn, pulse, planning, hf_models
from forno_twin.demo_data import load_events
from forno_twin.schema import EventFile, APPROVAL_STEPS

EVENTS = load_events()
OUT = Path(__file__).resolve().parent / "out" / "app"
STATE: dict = {"result": None}

CSS = """
:root{--ivory:#fbf7f0;--terra:#c4461f;--terra2:#e0572f;--anthr:#1f1f1f;--gold:#b8892b}
body,.gradio-container{background:var(--ivory)!important;color:var(--anthr)}
h1,h2,h3{font-family:Georgia,'Playfair Display',serif}
.jonis-head{border-bottom:3px solid var(--terra);padding-bottom:.4rem;margin-bottom:.6rem}
.badge{display:inline-block;padding:.15rem .5rem;border-radius:999px;font-size:.75rem;font-weight:700;letter-spacing:.04em}
.badge.block{background:#fde8e6;color:#c0392b}.badge.ok{background:#e6f4ec;color:#2e8b57}
button.primary{background:var(--terra)!important;border-color:var(--terra)!important}
"""


def _md_table(rows, cols):
    if not rows:
        return "_keine Daten_"
    head = "| " + " | ".join(cols) + " |\n|" + "---|" * len(cols) + "\n"
    return head + "\n".join("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |" for r in rows)


def run_request(text, transcript, package, distance, use_hf):
    if not text.strip():
        return ("Bitte eine Anfrage eingeben.",) + ("",) * 8
    res = pipeline.run(text, event_id="APP-" + date.today().strftime("%Y%m%d"), transcript=transcript or None,
                       package=package or None, distance_km=float(distance) if distance else None,
                       use_hf=bool(use_hf), out_dir=OUT, synthetic=True)
    STATE["result"] = res
    ev = res["event"]
    badge = '<span class="badge block">Auto-Freigabe blockiert</span>' if res["auto_release_blocked"] else '<span class="badge ok">keine Blocker</span>'
    akte = [f"### Eventakte {ev['event_id']} {badge}", "",
            _md_table([{"Feld": k, "Wert": ev.get(k), "Status": ev["provenance"].get(k, {}).get("status", "")} for k in
                       ("event_type", "date", "location", "location_type", "guests", "time_window", "budget_total", "budget_pp", "veg_share", "vegan_share", "gf_count", "language")],
                      ["Feld", "Wert", "Status"]),
            "", "**Konflikte**", *([f"- {c}" for c in ev["conflicts"]] or ["- keine"]),
            "", "**Lücken**", *([f"- {g}" for g in ev["gaps"]] or ["- keine"]),
            "", "**Rückfragen (max. 3)**", *([f"- {q}" for q in ev["questions"]] or ["- keine"]),
            "", "**Allergen-Hinweise (nie Wahrheit)**", *([f"- {h['mention']} → {h['eu_allergen']}; evtl. betroffen: {', '.join(h['possibly_affected_pizzas']) or '–'}" for h in res["allergen_hints"]] or ["- keine"]),
            "", "**Sicherheit**", *([f"- {s}" for s in ev["security_findings"]] or ["- unauffällig"]),
            "", "**Pseudonymisierte Kontakte**: " + (", ".join(ev["contact"].keys()) or "keine erkannt"),
            "", "**HF-Triage**: " + json.dumps(res["hf"]["triage"], ensure_ascii=False)[:400]]
    pl, k = res["plan"], res["calc"]
    if pl:
        menu = ["### Menü & Mengen", f"Paket **{pl['package_name']}** · {pl['guests']} Gäste · {pl['pizzas_total']} Pizzen (Basis {pl['pizzas_base']} + Puffer {pl['buffer']:.0%}) · Teig {pl['dough_kg']} kg",
                "", _md_table(pl["menu"], ["name", "why"]), "", _md_table(pl["distribution"], ["name", "pizzas", "vegan", "vegetarian"]),
                "", f"**Ofen:** {pl['oven']['note']}", "", "**Annahmen:** " + ("; ".join(pl["assumptions"]) or "keine")]
        r = k["results"]
        kalk = ["### Kalkulation (Formeln sichtbar, Freigabe nötig)", f"⚠️ {k['warning']}", "",
                _md_table([{"Eingabe": n, "Wert": v["value"], "Status": v["status"], "Quelle": v["source"]} for n, v in k["inputs"].items()], ["Eingabe", "Wert", "Status", "Quelle"]),
                "", _md_table([{"Formel": n, "Rechnung": f} for n, f in k["formulas"].items()], ["Formel", "Rechnung"]), "",
                f"**Umsatz netto** {r['umsatz_netto']:.2f} € · **Ware** {r['ware']:.2f} € · **Personal** {r['personal']:.2f} € · **Fix** {r['fix']:.2f} €",
                f"**Prime Cost** {r['prime_cost_pct']} % ({r['prime_status']}) · **Gewinn** {r['gewinn']:.2f} € · Band [{r['gewinn_band'][0]:.0f} … {r['gewinn_band'][1]:.0f}] · {r['band_note']}",
                "", "### Angebotsvarianten", _md_table([{"Paket": o["name"], "ab €/P.": o["price_pp_brutto"], "Gäste (Abrechnung)": o["billing_guests"], "ab gesamt €": o["total_brutto_ab"], "Hinweise": "; ".join(o["fit_notes"]) or "–"} for o in res["offers"]],
                                                       ["Paket", "ab €/P.", "Gäste (Abrechnung)", "ab gesamt €", "Hinweise"])]
        team = ["### Einkauf", _md_table(pl["shopping"], ["item", "qty", "unit", "formula", "status"]), "", "### 48-Stunden-Countdown", _md_table(pl["countdown"], ["t", "task"]),
                "", "### Personal", f"{pl['staff']['helpers']} Helfer à {pl['staff']['hours_per_helper']} h ({pl['staff']['status']}) · {pl['staff']['formula']}",
                "", "### Equipment", *[f"- {e}" for e in pl["equipment"]], "", "### Einsatzbrief", "```\n" + res["team_brief"] + "\n```"]
        sim = ["### Was-wäre-wenn-Simulator (Vorher → Nachher)"]
        for s in res["simulations"]:
            sim += [f"#### {s['name']}", s["desc"], "", _md_table([{"Größe": n, "vorher": c["before"], "nachher": c["after"], "Δ": c["delta"]} for n, c in s["changes"].items()], ["Größe", "vorher", "nachher", "Δ"]),
                    "", "**Einkauf-Delta:** " + ("; ".join(f"{d['item']} {d['before']}→{d['after']} {d['unit']}" for d in s["shopping_diff"]) or "keine"),
                    "", "**Maßnahmen:**", *[f"- {m}" for m in s["measures"]], "", "**Zusätzliche Risiken:**", *([f"- {r}" for r in s["risk_delta"]] or ["- keine"]), ""]
        risks = ["### Risiko-, Engpass- und Notfallcheck", _md_table(res["risks"], ["level", "risk", "measure"])]
    else:
        menu = kalk = team = sim = risks = ["_Keine Planung möglich: Gästezahl fehlt. Siehe Rückfragen._"]
    signs = ["### Menüschilder (DE / EN / IT)"]
    for s in res["signs"]:
        for lang, d in s["langs"].items():
            signs.append(f"**{d['title']}** [{lang}] — {d['ingredients']} · _{d['tags']}_ · {d['allergens']}")
        signs.append("")
    quellen = ["### Quellen, Status und Freigaben", "", "**Freigabeschritte (Human-in-the-loop)**",
               _md_table([{"Schritt": v["label"], "Freigegeben": "nein" if not v["approved"] else "ja"} for v in ev["approvals"].values()], ["Schritt", "Freigegeben"]),
               "", "**Allergen-Matrix**: " + res["allergen_report"]["message"], "", "**Quellen-Konflikte im Repo**",
               _md_table(res["source_conflicts"], ["topic", "a", "b", "action"]), "", "**Blocker**: " + (", ".join(res["blockers"]) or "keine"),
               "", f"Exporte: {', '.join(res.get('exports', []))}"]
    return ("\n".join(akte), "\n".join(menu), "\n".join(kalk), "\n".join(team), "\n".join(sim), "\n".join(risks), "\n".join(signs), res["reply_draft"], "\n".join(quellen))


def load_demo(eid):
    e = next(x for x in EVENTS if x["id"] == eid)
    return e["text"], e.get("transcript", ""), e.get("distance_km") or 10


def do_learn(pizzas_produced, leftover_pizzas, leftover_dough, guests_actual, helpers_actual, hours_actual, serving_minutes):
    res = STATE.get("result")
    if not res or not res["plan"]:
        return "Erst eine Anfrage mit Gästezahl verarbeiten."
    wl = learn.waste_lens(res["plan"], {"pizzas_produced": int(pizzas_produced or 0), "leftover_pizzas": int(leftover_pizzas or 0),
                                        "leftover_dough_kg": float(leftover_dough or 0), "guests_actual": int(guests_actual or res["plan"]["guests"]),
                                        "helpers_actual": int(helpers_actual or 0) or None, "hours_per_helper_actual": float(hours_actual or 0) or None,
                                        "serving_minutes_actual": int(serving_minutes or 0) or None})
    return "### Waste Lens\n" + _md_table(wl["rows"], ["metric", "plan", "ist"]) + "\n\n**Hinweise**\n" + "\n".join(f"- {h}" for h in wl["hints"]) + f"\n\n_{wl['photo_policy']}_\n\nIst-Daten als JSON in `data/actuals/` ablegen (synthetic=false), dann `python -m forno_twin calibrate`."


def do_pulse(v1, v2, v3, v4, remaining, batch):
    votes = {"La Reina Margarita": int(v1 or 0), "La Guerrera OG Pepperoni": int(v2 or 0), "La Marinera Noble": int(v3 or 0), "San Champiñón": int(v4 or 0)}
    r = pulse.recommend_next_batch(votes, int(remaining or 0), int(batch or 12))
    return "### Pizza Pulse – nächste Charge (Empfehlung)\n" + _md_table([{"Sorte": s, "Stimmen": votes[s], "Anteil": r["shares"][s], "Charge": r["batch"][s]} for s in votes], ["Sorte", "Stimmen", "Anteil", "Charge"]) + f"\n\n_{r['note']}_"


with gr.Blocks(title="JONIS FORNO TWIN") as demo:
    gr.HTML('<div class="jonis-head"><h1>JONIS FORNO TWIN</h1><p>KI plant. JONIS entscheidet. Lokal, deterministisch, mit Quellen und Freigaben.</p></div>')
    with gr.Tab("1 · Anfrage erfassen"):
        with gr.Row():
            demo_pick = gr.Dropdown([e["id"] + " – " + e["kind"] for e in EVENTS], label="Synthetischen Demo-Fall laden", value=None)
            package = gr.Dropdown(["", "classic", "event", "premium"], value="", label="Paket (leer = automatisch)")
            distance = gr.Number(value=10, label="Entfernung ab Bremen (km)")
            use_hf = gr.Checkbox(value=False, label="HF-Triage (Zero-Shot) versuchen")
        text = gr.Textbox(lines=8, label="Anfrage (E-Mail, Formular, PDF-Text) – wird lokal pseudonymisiert")
        transcript = gr.Textbox(lines=4, label="Transkript Sprachmemo (optional; ASR-Modell laut Modellregister)")
        audio = gr.Audio(label="Sprachmemo (optional, lokal; ASR nur wenn Modell verfügbar)", type="filepath")
        gr.File(label="Foto / Video der Location (optional, Location Scout – Hinweise, keine Freigabe)")
        run_btn = gr.Button("Eventakte erzeugen", variant="primary")
        demo_pick.change(lambda v: load_demo(v.split(" – ")[0]) if v else ("", "", 10), demo_pick, [text, transcript, distance])
    with gr.Tab("2 · Eventakte prüfen"):
        akte_md = gr.Markdown()
    with gr.Tab("3 · Menü & Kalkulation"):
        menu_md = gr.Markdown(); kalk_md = gr.Markdown()
    with gr.Tab("4 · Einkauf, Vorbereitung, Personal"):
        team_md = gr.Markdown()
    with gr.Tab("5 · Event-Simulator"):
        sim_md = gr.Markdown()
    with gr.Tab("6 · Lernen nach dem Event"):
        risks_md = gr.Markdown()
        with gr.Row():
            p1 = gr.Number(label="Pizzen produziert"); p2 = gr.Number(label="Pizzen übrig"); p3 = gr.Number(label="Teig übrig (kg)")
            p4 = gr.Number(label="Gäste tatsächlich"); p5 = gr.Number(label="Helfer tatsächlich"); p6 = gr.Number(label="Stunden je Helfer"); p7 = gr.Number(label="Servierdauer (min)")
        learn_btn = gr.Button("Waste Lens auswerten"); learn_md = gr.Markdown()
        learn_btn.click(do_learn, [p1, p2, p3, p4, p5, p6, p7], learn_md)
        gr.Markdown("#### Pizza Pulse (anonyme Präferenzen während des Events)")
        with gr.Row():
            v1 = gr.Number(label="Margarita", value=0); v2 = gr.Number(label="Pepperoni", value=0); v3 = gr.Number(label="Marinera", value=0); v4 = gr.Number(label="Champiñón", value=0)
            rem = gr.Number(label="Pizzen noch offen", value=60); bs = gr.Number(label="Chargengröße", value=12)
        pulse_btn = gr.Button("Nächste Charge empfehlen"); pulse_md = gr.Markdown()
        pulse_btn.click(do_pulse, [v1, v2, v3, v4, rem, bs], pulse_md)
    with gr.Tab("7 · Quellen & Freigaben"):
        signs_md = gr.Markdown(); reply_tb = gr.Textbox(lines=14, label="Antwortentwurf (JONIS-Ton) – Freigabe nötig"); quellen_md = gr.Markdown()
        gr.Markdown("**Modellregister / Umgebung:**\n```\n" + json.dumps({"registry": {k: v["id"] for k, v in hf_models.REGISTRY.items()}, "status": hf_models.status()}, ensure_ascii=False, indent=1) + "\n```")
    run_btn.click(run_request, [text, transcript, package, distance, use_hf], [akte_md, menu_md, kalk_md, team_md, sim_md, risks_md, signs_md, reply_tb, quellen_md])

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7861, show_error=True, css=CSS)
