# ai-website-workflow

Interaktives Workflow-Dashboard für ein **„Website bauen mit KI"**-Business. Dunkles Theme, Monospace, fünf Phasen + Pipeline-Kalkulator — vom Setup bis zum Abschluss.

Gebaut mit **Next.js 15** (App Router), **React 19** und **Tailwind CSS v4**.

## Phasen

| #  | Phase       | Inhalt                                              |
|----|-------------|-----------------------------------------------------|
| 01 | Setup       | Tool Stack · Template-Repo · Angebotsvorlage        |
| 02 | Akquise     | Meta Ads · Kleinanzeigen · Direktansprache          |
| 03 | Briefing    | Tally-Formular · Telefonat-Ablauf                   |
| 04 | Umsetzung   | KI iterativ führen · GitHub Push · Vercel Deploy    |
| 05 | Abschluss   | Übergabe · Rechnung · Upsell                        |
| 06 | Kalkulator  | Werbebudget · CPL · Conversion · Projektpreis → ROI |

Jede Phase enthält nummerierte Schritte mit Bullet Points und einen **kopierbaren KI-Prompt** am Ende.

## Quickstart

```bash
npm install
npm run dev
```

Dann `http://localhost:3000` öffnen.

## Build

```bash
npm run build
npm run start
```

## Projektstruktur

```
.
├── app/
│   ├── globals.css     # Tailwind v4 + Slider-Styling
│   ├── layout.jsx      # Root Layout + Metadata
│   └── page.jsx        # Dashboard (Client Component)
├── next.config.mjs
├── postcss.config.mjs  # @tailwindcss/postcss
├── jsconfig.json
└── package.json
```

## Tech Stack

- Next.js 15 — App Router
- React 19
- Tailwind CSS v4 (PostCSS plugin)
- ESLint 9

## Deployment

Auf Vercel deploybar ohne Konfiguration — Repository importieren, fertig.
