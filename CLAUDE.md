# CLAUDE.md – Jonis Catering

Bedienungsanleitung dieses Repos für Claude Code. Lies das zuerst, bevor du Änderungen machst.

## Was ist das hier?

Statische Website für **Jonis Catering** – neapolitanisches Pizza-Catering
in Bremen & Umgebung (Hochzeiten, Firmenevents, private Feiern). Sprache: Deutsch.

- **Kein Framework, kein Build-Schritt.** Reines HTML/CSS/JS, keine Abhängigkeiten zur Laufzeit.
- Die Startseite (`index.html`) ist weiterhin eine einzige Datei (HTML, CSS, JS inline).
  Seit September 2026 gibt es zusätzlich eigenständige SEO-Landingpages (siehe unten) –
  das ist eine bewusste, begrenzte Ausnahme von der "alles in index.html"-Regel, keine
  allgemeine Einladung, weitere Unterseiten oder Frameworks einzuführen.
- Zielgruppe: Kund:innen, die Catering anfragen wollen.

## Projektstruktur

| Pfad | Zweck |
|------|-------|
| `index.html` | Die Startseite: HTML, CSS (`<style>` im `<head>`) und JS inline. |
| `hochzeit-pizza-catering-bremen/index.html` | SEO-Landingpage Hochzeiten. |
| `firmenfeier-pizza-catering-bremen/index.html` | SEO-Landingpage Firmenfeiern. |
| `private-feier-pizza-catering-bremen/index.html` | SEO-Landingpage private Feiern. |
| `seo-pages.css` | Gemeinsames Stylesheet **nur** für die drei Landingpages oben (nicht für `index.html`). |
| `favicon.svg` | Favicon für alle Seiten. |
| `llms.txt`, `robots.txt`, `sitemap.xml` | GEO/SEO-Crawler-Dateien. |
| `.htaccess` | Repo-Schutz (blockt `.md/.json/.yml/.mjs` etc. + versteckte Dateien), www→Hauptdomain-Redirect, Caching/Kompression. |
| `.htmlhintrc` | Regeln für den HTML-Linter. |
| `package.json` | Nur Dev-Tooling (htmlhint) + Hilfs-Skripte. Keine Runtime-Abhängigkeiten. |
| `.claude/` | SessionStart-Hook + Settings für Claude Code. |

## Befehle

```bash
npm install      # Dev-Tools installieren (macht der SessionStart-Hook automatisch)
npm run lint     # index.html + alle Landingpages mit htmlhint prüfen
npm run serve    # Lokale Vorschau auf http://localhost:8000
```

## Arbeitsregeln / Konventionen

- **`index.html` bleibt in sich geschlossen** (HTML, `<style>`, `<script>` inline). Kein
  Build-System, kein Bundler, kein Framework einführen, außer ich (der Maintainer) frage
  ausdrücklich danach.
- **Neue Landingpages nur nach Absprache.** Die drei bestehenden SEO-Seiten sind die
  Ausnahme; weitere Unterseiten nicht einfach ergänzen, ohne zu fragen.
- **CSS der Startseite** lebt im `<style>`-Block im `<head>` von `index.html` und nutzt
  CSS-Variablen (`:root`). Neue Styles dort ergänzen, nicht auslagern. Die Landingpages
  teilen sich dagegen bewusst `seo-pages.css` (eigene, an `index.html` angelehnte
  `:root`-Variablen) – dort ebenfalls in dieser einen Datei bleiben.
- **Sprache des Contents ist Deutsch** – Texte, Buttons und Alt-Attribute auf Deutsch.
- **SEO nicht kaputt machen:** `<title>`, `<meta description>`, OG-/Twitter-Tags,
  `canonical` und das JSON-LD-Schema (`@graph` in `index.html`) sind bewusst gesetzt.
  Bei Änderungen konsistent halten.
- **Keine unbelegten Fakten in Schema/Content aufnehmen** (Preise, Öffnungszeiten,
  Kapazitätsgrenzen o. Ä.) – im Zweifel nachfragen statt zu raten. Insbesondere: keine
  selbst-referenzierten `Review`/`aggregateRating`-Markups im JSON-LD (verstößt gegen
  Googles Richtlinien für Rezensions-Snippets).
- **Barrierefreiheit:** Bilder brauchen `alt`-Texte, Buttons/Links sinnvolle Labels.
- **Vor dem Commit immer `npm run lint` laufen lassen** und Fehler beheben.

## Definition of Done

1. `npm run lint` läuft ohne Fehler (deckt `index.html` + alle Landingpages ab).
2. Seite per `npm run serve` lokal geprüft (Layout/Funktion stimmt, inkl. betroffener
   Landingpages und – falls geändert – Impressum/Datenschutz-Verlinkung von dort aus).
3. Klarer, beschreibender Commit; Push auf den vereinbarten Branch.
