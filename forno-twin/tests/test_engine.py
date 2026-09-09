"""Testsuite FORNO TWIN – läuft mit `python -m pytest` oder `python -m unittest`."""
import json
import unittest
from datetime import date
from pathlib import Path

from forno_twin import extract, planning, calc, allergens, simulator, pulse, learn, pipeline, offer, risk
from forno_twin.demo_data import load_events
from forno_twin.schema import EventFile

TODAY = date(2026, 9, 9)
EVENTS = {e["id"]: e for e in load_events()}


def ev_of(eid):
    e = EVENTS[eid]
    text = e["text"] + ("\n" + e["transcript"] if e.get("transcript") else "")
    return extract.extract(text, event_id=eid, today=TODAY)


class TestExtraction(unittest.TestCase):
    def test_normal_wedding_full(self):
        ev = ev_of("SYN-001")
        self.assertEqual(ev.event_type, "hochzeit")
        self.assertEqual(ev.date, "2027-06-20")
        self.assertEqual(ev.location, "Lilienthal")
        self.assertEqual(ev.guests, 100)  # Maximum bei Widerspruch 90 vs 100
        self.assertTrue(any("Gästezahlen" in c for c in ev.conflicts))
        self.assertEqual(ev.gf_count, 2)
        self.assertEqual(ev.serving_start, "18:00")
        self.assertEqual(ev.budget_total, 3500)
        self.assertTrue(ev.allergen_mentions)
        self.assertIn(ev.location_type, ("outdoor", "gemischt"))  # Garten + Scheune
        self.assertTrue(ev.weather_protection)

    def test_pii_pseudonymized(self):
        ev = ev_of("SYN-011")
        dumped = ev.to_json()
        self.assertNotIn("lisa@example.com", dumped)
        self.assertNotIn("9876543", dumped)
        self.assertNotIn("Beispielfrau", dumped)
        self.assertGreaterEqual(len(ev.contact), 2)

    def test_prompt_injection_flagged(self):
        ev = ev_of("SYN-010")
        self.assertGreaterEqual(len(ev.security_findings), 1)
        res = pipeline.run(EVENTS["SYN-010"]["text"], event_id="SYN-010", today=TODAY)
        self.assertNotIn("Rabatt", res["reply_draft"])
        self.assertNotIn("hacker@example.net", res["reply_draft"])
        self.assertTrue(res["auto_release_blocked"])

    def test_incomplete_request_questions(self):
        ev = ev_of("SYN-003")
        self.assertIsNone(ev.guests)
        self.assertIsNone(ev.date)
        self.assertGreaterEqual(len(ev.gaps), 3)
        self.assertLessEqual(len(ev.questions), 3)
        self.assertGreaterEqual(len(ev.questions), 1)

    def test_under_minimum_flagged(self):
        ev = ev_of("SYN-004")
        self.assertEqual(ev.guests, 35)
        self.assertTrue(any("Mindestgröße" in c for c in ev.conflicts))

    def test_multilingual(self):
        en, it = ev_of("SYN-006"), ev_of("SYN-007")
        self.assertEqual(en.language, "en"); self.assertEqual(en.guests, 70); self.assertEqual(en.date, "2027-06-05")
        self.assertEqual(it.language, "it"); self.assertEqual(it.guests, 60); self.assertEqual(it.date, "2026-10-10")

    def test_allergen_unclear_asks(self):
        ev = ev_of("SYN-008")
        self.assertGreaterEqual(len(ev.allergen_mentions), 2)
        self.assertTrue(any("Allerg" in q for q in ev.questions))

    def test_short_lead_and_power(self):
        self.assertTrue(any("Vorlauf" in c for c in ev_of("SYN-013").conflicts))
        self.assertIs(ev_of("SYN-005").power_available, False)

    def test_shares(self):
        ev = ev_of("SYN-014")
        self.assertAlmostEqual(ev.veg_share, 0.5); self.assertAlmostEqual(ev.vegan_share, 0.25)


class TestPlanningCalc(unittest.TestCase):
    def test_plan_formulas(self):
        ev = EventFile(event_id="T", guests=80, veg_share=0.3, vegan_share=0.1, gf_count=0)
        pl = planning.plan(ev, "classic")
        self.assertEqual(pl["pizzas_base"], 160)
        self.assertEqual(pl["pizzas_total"], 176)  # +10 % Puffer
        self.assertEqual(sum(d["pizzas"] for d in pl["distribution"]), 176)
        self.assertEqual(pl["staff"]["helpers"], 2)
        self.assertAlmostEqual(pl["dough_kg"], 44.0, places=1)
        self.assertTrue(all(s["status"] for s in pl["shopping"]))

    def test_calc_matches_kalkulation_html_defaults(self):
        # kalkulation.html Standard: 80 Gäste, 27 € brutto, 9 €/Gast, 50 € Pauschale, 2,5 Helfer x 8 h x 15 €, 31,5 %, 200 € fix
        k = calc.calculate(80, "classic", helpers=2.5, hours=8)
        r = k["results"]
        self.assertAlmostEqual(r["umsatz_brutto"], 2160.0, places=2)
        self.assertAlmostEqual(r["umsatz_netto"], 2160 / 1.19, places=2)
        self.assertAlmostEqual(r["ware"], 770.0, places=2)
        self.assertAlmostEqual(r["personal"], 300 * 1.315, places=2)
        self.assertAlmostEqual(r["prime_cost"], 770 + 394.5, places=2)
        self.assertAlmostEqual(r["gewinn"], 2160 / 1.19 - 1164.5 - 200, places=2)
        self.assertEqual(k["inputs"]["ware_pro_gast_netto"]["status"], "ANNAHME")
        self.assertEqual(k["inputs"]["price_pp_brutto"]["status"], "VERIFIZIERT")

    def test_big_event_bottleneck(self):
        ev = EventFile(event_id="T", guests=250, serving_start="16:00", time_window="16:00-19:00")
        pl = planning.plan(ev, "classic")
        self.assertFalse(pl["oven"]["ok"])
        self.assertTrue(any(r["level"] == "HOCH" for r in risk.assess(ev, pl, TODAY)))

    def test_budget_fit(self):
        ev = ev_of("SYN-009")
        variants = offer.offer_variants(ev)
        self.assertTrue(all(v["fit_notes"] for v in variants))


class TestAllergensSafety(unittest.TestCase):
    def test_matrix_blocks_release_until_approved(self):
        rep = allergens.menu_allergen_report()
        self.assertFalse(rep["approved"])
        self.assertTrue(rep["release_blocked"])
        margherita = next(r for r in rep["rows"] if r["pizza"] == "La Reina Margarita")
        self.assertIn("Milch", margherita["allergens"]); self.assertIn("Gluten", margherita["allergens"])

    def test_approved_matrix_releases(self):
        m = allergens.load_matrix()
        m["approved_by"] = "Test"; m["approved_at"] = "2026-09-09"
        for v in m["ingredients"].values():
            v["verified"] = True
        rep = allergens.menu_allergen_report(m)
        self.assertFalse(rep["release_blocked"])

    def test_signs_marked_draft(self):
        res = pipeline.run(EVENTS["SYN-002"]["text"], event_id="SYN-002", today=TODAY)
        self.assertTrue(all(s["release_blocked"] for s in res["signs"]))
        self.assertIn("ENTWURF", res["signs"][0]["langs"]["en"]["allergens"])
        self.assertIn("Steinofen", res["reply_draft"]); self.assertNotIn("Holzofen", res["reply_draft"])


class TestSimulatorLearnPulse(unittest.TestCase):
    def test_simulations(self):
        ev = ev_of("SYN-002")
        sims = simulator.simulate_all(ev, "classic")
        self.assertEqual(len(sims), 3)
        plus = sims[0]
        self.assertEqual(plus["changes"]["guests"]["after"], 144)
        self.assertGreater(plus["changes"]["pizzas_total"]["delta"], 0)
        rain = sims[2]
        self.assertEqual(rain["changes"]["helpers"]["delta"], -1)
        self.assertGreater(rain["changes"]["hours_per_helper"]["delta"], 0)
        veg = sims[1]
        self.assertGreater(sum(d["pizzas"] for d in veg["distribution_after"] if d["vegan"]), 0)

    def test_pulse(self):
        r = pulse.recommend_next_batch({"Margarita": 10, "Diavola": 4, "Verde": 1}, remaining_pizzas=60, batch_size=12)
        self.assertEqual(sum(r["batch"].values()), 12)
        self.assertEqual(r["top"], "Margarita")
        self.assertGreaterEqual(min(r["batch"].values()), 1)

    def test_waste_lens_and_calibration_guard(self):
        ev = EventFile(event_id="T", guests=80)
        pl = planning.plan(ev, "classic")
        wl = learn.waste_lens(pl, {"pizzas_produced": 150, "leftover_pizzas": 20, "leftover_dough_kg": 6, "guests_actual": 78,
                                   "helpers_actual": 3, "hours_per_helper_actual": 9, "serving_minutes_actual": 150})
        self.assertTrue(wl["hints"])
        res = learn.calibrate(actuals=[{"synthetic": True, "pizzas_produced": 150}], write=False)
        self.assertEqual(res["overrides"], {})  # synthetische Daten kalibrieren nie
        res2 = learn.calibrate(actuals=[
            {"synthetic": False, "pizzas_produced": 150, "serving_minutes_actual": 150, "guests_actual": 78, "helpers_actual": 3, "leftover_pizzas": 20},
            {"synthetic": False, "pizzas_produced": 200, "serving_minutes_actual": 180, "guests_actual": 100, "helpers_actual": 3, "leftover_pizzas": 5}], write=False)
        self.assertIn("oven_pizzas_per_hour", res2["overrides"])


class TestEndToEnd(unittest.TestCase):
    def test_full_demo_exports(self):
        e = EVENTS["SYN-001"]
        out = Path(__file__).resolve().parent.parent / "out" / "test"
        res = pipeline.run(e["text"], event_id="SYN-001", transcript=e["transcript"], distance_km=15, today=TODAY, out_dir=out)
        self.assertTrue((out / "SYN-001_eventakte.json").exists())
        self.assertTrue((out / "SYN-001_einkauf.csv").exists())
        self.assertTrue((out / "SYN-001_einsatzbrief.html").exists())
        self.assertEqual(len(res["offers"]), 3)
        self.assertEqual(len(res["simulations"]), 3)
        data = json.loads((out / "SYN-001_eventakte.json").read_text(encoding="utf-8"))
        self.assertTrue(data["synthetic"])
        self.assertNotIn("anna.beispiel@example.org", json.dumps(data))

    def test_spam_no_plan(self):
        res = pipeline.run(EVENTS["SYN-015"]["text"], event_id="SYN-015", today=TODAY)
        self.assertIsNone(res["plan"]); self.assertIsNone(res["calc"])
        self.assertTrue(res["event"]["questions"])


if __name__ == "__main__":
    unittest.main()
