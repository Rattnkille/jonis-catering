# MAP.md – Karte des Repos

Zonen: grün = frei änderbar, gelb = ändern mit Screenshot-Vergleich, rot = nur mit Review durch Jonathan auf jedem Diff.

| Bereich | Pfad | Zone | Warum |
|---|---|---|---|
| Startseite Texte, Abstände, Farben, Bilder | `index.html` HTML + `<style>` | grün | kein Verhalten, Screenshot-Diff reicht |
| Startseite Sektionen (Hero, Leistungen, Pakete, Galerie, Karte, Ablauf, Bewertungen, FAQ) | `index.html` | gelb | Layout und Anker `#leistungen` … `#kontakt` müssen bleiben |
| Anfrageformular + Baukasten | `index.html` `#kontakt`, `<form id="contactForm">` | rot | einziger Conversion-Pfad |
| Formular-Backend | `send_email.php` | rot | Mailversand, Spam-Schutz, Sheets-Webhook |
| Inline-JS (Nav, Modal, FAQ, Formular-Status, Wizard) | `index.html` `<script>` | rot | kein Test außer Playwright |
| SEO-Kopf, JSON-LD `@graph` | `index.html` `<head>`, Script am Ende | rot | Rankings |
| Landingpages | `hochzeit-…/`, `firmenfeier-…/`, `private-feier-…/`, `seo-pages.css` | gelb | eigenes Stylesheet, nicht Teil dieses Umbaus |
| Crawler-Dateien | `llms.txt`, `robots.txt`, `sitemap.xml` | gelb | bei Preis- oder Paketänderung nachziehen |
| Server-Regeln | `.htaccess` | rot | Redirect, Schutz, Caching |
| Deploy | `.github/workflows/deploy.yml` | rot | FTP auf Produktion bei Push auf `main`, keine Preview |
| Analytics | `scripts/cf-analytics.mjs`, `reports/analytics.md`, `.github/workflows/analytics.yml` | gelb | wöchentlicher Bericht, zeigt aktuell 0 Aufrufe |
| Intern | `kalkulation.html` | außerhalb | noindex, aber öffentlich erreichbar (Frage an Jonathan) |
| Außerhalb | `forno-twin/`, `sheets-integration/` | außerhalb | eigene Projekte |

## Owner

Jonathan Sibbing (Inhaber) entscheidet Zonen, Preise, Inhalte. Claude Code arbeitet innerhalb der Zonen.

## Risikostellen

1. Formular ohne Tests: Honeypot und Zeitsperre melden Erfolg, auch wenn keine Mail rausgeht.
2. Kein Preview-Deploy: jeder Merge auf `main` ist sofort live.
3. Inline-JS in einer 3.000-Zeilen-Datei: Sticky Header, Mobilnav, Sticky-CTA, Summary-Leiste und Modal können auf dem Handy kollidieren.
4. FAQ-Texte und JSON-LD FAQPage müssen wortgleich bleiben.
