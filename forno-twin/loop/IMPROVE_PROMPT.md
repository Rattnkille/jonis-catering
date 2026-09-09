# FORNO TWIN – Prompt für den KI-Verbesserungslauf

Du arbeitest im Repo `rattnkille/jonis-catering`, Ordner `forno-twin/`. Ziel: den JONIS FORNO TWIN messbar verbessern, ohne Regeln zu brechen.

Vorgehen, in dieser Reihenfolge:

1. `git fetch origin && git checkout -B claude/forno-twin-loop origin/main` (falls der Branch existiert: `git checkout claude/forno-twin-loop && git merge origin/main`).
2. Lies `forno-twin/CHECKPOINT.md`, `forno-twin/docs/loop-status.md` und `forno-twin/loop/backlog.json`.
3. Führe `cd forno-twin && bash loop/improve.sh` aus (Python 3.11+, keine ML-Pakete nötig). Rote Tests oder Allergenfehler > 0 zuerst beheben.
4. Nimm genau **einen** offenen Backlog-Punkt mit der niedrigsten Prioritätszahl, den du ohne Joni erledigen kannst (Owner "Loop"). Setze ihn um, ergänze einen synthetischen Testfall in `data/synthetic_events.json` mit `expected` und eine Prüfung in `eval/run_eval.py` oder `tests/`.
5. Führe den Loop erneut aus. Genauigkeit darf nicht sinken, Allergenfehler bleiben 0. Sonst Änderung zurücknehmen.
6. Markiere den Punkt in `loop/backlog.json` als `erledigt`, ergänze neue Punkte aus Fehlerbeispielen, aktualisiere `CHECKPOINT.md` (Status, Befehle, nächster Schritt).
7. Committe und pushe auf `claude/forno-twin-loop`; öffne oder aktualisiere einen Draft-PR mit dem Inhalt von `docs/loop-status.md`.

Harte Regeln:
- Keine Preise, Kosten, Allergene, Kapazitäten, Kunden oder Messwerte erfinden. Neue Parameter bekommen Status ANNAHME oder TBD.
- Nichts veröffentlichen (keine öffentlichen HF-Repos/Spaces), keine Kundenkontakte, keine kostenpflichtigen Endpoints oder Jobs.
- Keine Secrets in Code, Logs oder Ausgaben. HF_TOKEN nur als Umgebungsvariable.
- Website (`index.html`) nicht anfassen. Nur `forno-twin/` und `.github/workflows/forno-twin-loop.yml`.
- Wenn ein Punkt Joni braucht, im PR-Text als "Benötigt Freigabe/Daten" auflisten und nicht raten.
