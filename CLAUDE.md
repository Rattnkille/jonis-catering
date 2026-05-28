# CLAUDE.md – Jonis Catering

Bedienungsanleitung dieses Repos für Claude Code. Lies das zuerst, bevor du Änderungen machst.

## Was ist das hier?

Statische One-Page-Website für **Jonis Catering** – neapolitanisches Pizza-Catering
in Bremen & Umgebung (Hochzeiten, Firmenevents, private Feiern). Sprache: Deutsch.

- **Kein Framework, kein Build-Schritt.** Die komplette Seite ist eine einzige Datei.
- Zielgruppe: Kund:innen, die Catering anfragen wollen.

## Projektstruktur

| Pfad | Zweck |
|------|-------|
| `index.html` | Die gesamte Website: HTML, CSS (`<style>` im `<head>`) und JS inline. |
| `.htmlhintrc` | Regeln für den HTML-Linter. |
| `package.json` | Nur Dev-Tooling (htmlhint) + Hilfs-Skripte. Keine Runtime-Abhängigkeiten. |
| `.claude/` | SessionStart-Hook + Settings für Claude Code. |

## Befehle

```bash
npm install      # Dev-Tools installieren (macht der SessionStart-Hook automatisch)
npm run lint     # index.html mit htmlhint prüfen
npm run serve    # Lokale Vorschau auf http://localhost:8000
```

## Arbeitsregeln / Konventionen

- **Alles bleibt in `index.html`.** Kein Build-System, kein Bundler, kein Framework
  einführen, außer ich (der Maintainer) frage ausdrücklich danach.
- **CSS** lebt im `<style>`-Block im `<head>` und nutzt CSS-Variablen (`:root`).
  Neue Styles dort ergänzen, nicht in separate Dateien auslagern.
- **Sprache des Contents ist Deutsch** – Texte, Buttons und Alt-Attribute auf Deutsch.
- **SEO nicht kaputt machen:** Die `<title>`-, `<meta description>`-, OG- und
  `canonical`-Tags im `<head>` sind bewusst gesetzt. Bei Änderungen konsistent halten.
- **Barrierefreiheit:** Bilder brauchen `alt`-Texte, Buttons/Links sinnvolle Labels.
- **Vor dem Commit immer `npm run lint` laufen lassen** und Fehler beheben.

## Definition of Done

1. `npm run lint` läuft ohne Fehler.
2. Seite per `npm run serve` lokal geprüft (Layout/Funktion stimmt).
3. Klarer, beschreibender Commit; Push auf den vereinbarten Branch.
