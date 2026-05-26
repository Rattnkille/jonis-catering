"use client";

import { useState } from "react";

const ACCENT = "#E85B2E";

const phases = [
  {
    id: "setup",
    num: "01",
    name: "Setup",
    color: "#E85B2E",
    description: "Fundament für effiziente Website-Produktion.",
    steps: [
      {
        title: "Tool Stack",
        bullets: [
          "Claude Code für Komponenten & Logik",
          "v0.dev für UI-Inspiration",
          "Cursor als IDE",
          "Vercel für Hosting & Preview-Deploys",
          "GitHub für Versionierung",
        ],
      },
      {
        title: "Template-Repo",
        bullets: [
          "Next.js 15 mit App Router",
          "Tailwind v4 vorkonfiguriert",
          "SEO-Defaults: metadata, sitemap, robots.txt",
          "Vercel-Deploy ready out of the box",
        ],
      },
      {
        title: "Angebotsvorlage",
        bullets: [
          "Notion-Template mit Preisstaffel",
          "Basic 499 € / Pro 999 € / Premium 1.999 €",
          "Klare Leistungsabgrenzung & Scope",
          "AGB + Auftragsbestätigung als PDF",
        ],
      },
    ],
    prompt:
      "Erstelle ein Next.js 15 Template-Repo mit App Router, Tailwind v4, SEO-Metadata, sitemap.ts, robots.ts und einer beispielhaften Landing-Page-Struktur (Hero, Features, Pricing, CTA, Footer). Optimiert für Vercel.",
  },
  {
    id: "akquise",
    num: "02",
    name: "Akquise",
    color: "#3B82F6",
    description: "Konstanter Lead-Flow mit minimalem Aufwand.",
    steps: [
      {
        title: "Meta Ads",
        bullets: [
          "Zielgruppe: lokale Selbstständige & Handwerker",
          "Budget: 10–20 €/Tag, 1 Kampagne testen",
          "Creative: Vorher/Nachher-Screenshots",
          "CTA: WhatsApp oder Tally-Formular",
        ],
      },
      {
        title: "Kleinanzeigen",
        bullets: [
          'Kostenlos in Kategorie "Dienstleistungen"',
          "Lokal posten, Stadtnamen im Titel",
          "Anzeige wöchentlich erneuern",
          "Foto vom letzten Projekt einbinden",
        ],
      },
      {
        title: "Direktansprache",
        bullets: [
          "LinkedIn: 10 gezielte Connections/Tag",
          "Cold Email mit konkretem Mehrwert-Vorschlag",
          "Netzwerk-Empfehlungen (10 % Provision)",
          "Lokale Unternehmen ohne Website googeln",
        ],
      },
    ],
    prompt:
      "Schreibe eine Meta-Ads-Copy für KI-gestützte Website-Erstellung. Zielgruppe: lokale Handwerker in Deutschland. Max. 125 Zeichen, klarer Nutzen, konkreter CTA (WhatsApp).",
  },
  {
    id: "briefing",
    num: "03",
    name: "Briefing",
    color: "#A855F7",
    description: "Klarheit über Ziel, Stil & Scope vor dem ersten Prompt.",
    steps: [
      {
        title: "Tally-Formular",
        bullets: [
          "Branche & Zielgruppe",
          "3 Beispiel-Websites als Referenz",
          "Hauptziel: Anrufe, Buchungen oder Anfragen?",
          "Logo, Fotos, Texte vorhanden?",
          "Wunsch-Deadline & Budget",
        ],
      },
      {
        title: "Telefonat-Ablauf (20 Min)",
        bullets: [
          "Begrüßung & Smalltalk (2 Min)",
          "Ziel & Painpoints abfragen (10 Min)",
          "Lösungsvorschlag + Preis nennen (5 Min)",
          "Nächste Schritte fixieren (3 Min)",
        ],
      },
    ],
    prompt:
      "Erstelle ein Tally-Formular mit 8 strukturierten Fragen zum Website-Briefing für Kleinunternehmer. Inklusive Mehrfachauswahl für Zielgruppe, Slider für Budget und Upload-Feld für Referenz-Screenshots.",
  },
  {
    id: "umsetzung",
    num: "04",
    name: "Umsetzung",
    color: "#22C55E",
    description: "KI iterativ steuern statt einmalig prompten.",
    steps: [
      {
        title: "KI iterativ führen",
        bullets: [
          "Section by Section bauen (Hero → Features → CTA)",
          "Nach jedem Schritt Preview prüfen",
          "Komponenten wiederverwenden statt copy-paste",
          "Konkrete Prompts mit Beispielen statt Floskeln",
        ],
      },
      {
        title: "GitHub Push",
        bullets: [
          "Feature-Branches pro Section",
          "Conventional Commits (feat:, fix:, chore:)",
          "Pull Requests als Review-Checkpoint",
          "Main bleibt immer deploybar",
        ],
      },
      {
        title: "Vercel Deploy",
        bullets: [
          "Auto-Deploy aus main",
          "Preview-Links für jeden PR",
          "Custom Domain via DNS-Record",
          "Analytics & Speed Insights aktivieren",
        ],
      },
    ],
    prompt:
      "Baue eine Hero-Section für einen Friseursalon. Buchungs-CTA prominent, Hintergrundbild mit Overlay, mobile-first, Tailwind v4, dunkles Theme, dezente Scroll-Animation. Liefere als React-Komponente mit TypeScript-Props.",
  },
  {
    id: "abschluss",
    num: "05",
    name: "Abschluss",
    color: "#F97316",
    description: "Sauberer Cut + offene Tür für Folgeaufträge.",
    steps: [
      {
        title: "Übergabe",
        bullets: [
          "Login-Daten via Passwort-Manager teilen",
          "Loom-Video mit Kurzanleitung (5 Min)",
          "PDF-Cheatsheet für Content-Updates",
          "Wartungspaket-Angebot beilegen",
        ],
      },
      {
        title: "Rechnung",
        bullets: [
          "50 % Anzahlung bei Auftragsbestätigung",
          "50 % bei Abnahme via Stripe-Link",
          "Rechnung mit Kleinunternehmerregelung",
          "Zahlungsziel: 7 Tage",
        ],
      },
      {
        title: "Upsell",
        bullets: [
          "SEO-Paket (149 € einmalig)",
          "Content-Wartung (49 €/Monat)",
          "Foto-Shooting über Partner",
          "Google Business Profil Optimierung",
        ],
      },
    ],
    prompt:
      "Schreibe eine freundliche Übergabe-Email mit Hinweis auf Login-Daten (Passwort-Manager), Link zum Loom-Video, Wartungspaket-Angebot (49 €/Monat) und Bitte um Google-Bewertung. Tonalität: locker, professionell, deutsch.",
  },
];

export default function Page() {
  const [activeTab, setActiveTab] = useState("setup");
  const [copiedId, setCopiedId] = useState(null);

  const [werbebudget, setWerbebudget] = useState(1000);
  const [costPerLead, setCostPerLead] = useState(15);
  const [conversionRate, setConversionRate] = useState(10);
  const [projektpreis, setProjektpreis] = useState(999);

  const leads = costPerLead > 0 ? Math.round(werbebudget / costPerLead) : 0;
  const projekte = Math.round((leads * conversionRate) / 100);
  const umsatz = projekte * projektpreis;
  const roi =
    werbebudget > 0 ? Math.round(((umsatz - werbebudget) / werbebudget) * 100) : 0;

  const isCalc = activeTab === "kalkulator";
  const phase = phases.find((p) => p.id === activeTab);

  const handleCopy = async (text, id) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch {
      // Clipboard API may be blocked; ignore
    }
  };

  return (
    <main className="min-h-screen bg-[#080808] text-neutral-200">
      <div className="mx-auto max-w-5xl px-4 py-10 sm:py-16">
        {/* Header */}
        <header className="mb-10 border-b border-neutral-800 pb-8">
          <div className="text-[10px] tracking-[0.3em] text-neutral-500">
            // AI WEBSITE WORKFLOW
          </div>
          <h1 className="mt-3 text-3xl sm:text-4xl font-bold text-white">
            Website bauen mit KI
            <span style={{ color: ACCENT }}>.</span>
          </h1>
          <p className="mt-3 max-w-2xl text-sm text-neutral-400 leading-relaxed">
            End-to-End Playbook: vom Setup über Akquise bis Abschluss. Jede Phase
            mit konkreten Schritten und einsatzbereiten KI-Prompts.
          </p>
        </header>

        {/* Tab Navigation */}
        <nav className="mb-8 grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-6">
          {phases.map((p) => {
            const active = activeTab === p.id;
            return (
              <button
                key={p.id}
                onClick={() => setActiveTab(p.id)}
                className={`group relative border px-3 py-3 text-left transition ${
                  active
                    ? "border-neutral-700 bg-neutral-900"
                    : "border-neutral-800 hover:border-neutral-700 hover:bg-neutral-900/50"
                }`}
                style={
                  active
                    ? { borderLeftColor: p.color, borderLeftWidth: "3px" }
                    : undefined
                }
              >
                <div className="text-[10px] text-neutral-500">{p.num}</div>
                <div
                  className="mt-1 text-xs font-bold uppercase tracking-wider"
                  style={{ color: active ? p.color : "#e5e5e5" }}
                >
                  {p.name}
                </div>
              </button>
            );
          })}
          <button
            onClick={() => setActiveTab("kalkulator")}
            className={`group relative border px-3 py-3 text-left transition ${
              isCalc
                ? "border-neutral-700 bg-neutral-900"
                : "border-neutral-800 hover:border-neutral-700 hover:bg-neutral-900/50"
            }`}
            style={
              isCalc
                ? { borderLeftColor: ACCENT, borderLeftWidth: "3px" }
                : undefined
            }
          >
            <div className="text-[10px] text-neutral-500">06</div>
            <div
              className="mt-1 text-xs font-bold uppercase tracking-wider"
              style={{ color: isCalc ? ACCENT : "#e5e5e5" }}
            >
              Kalkulator
            </div>
          </button>
        </nav>

        {/* Phase Content */}
        {!isCalc && phase && (
          <section>
            <div className="mb-6">
              <div className="text-[10px] tracking-[0.3em] text-neutral-500">
                PHASE {phase.num}
              </div>
              <h2
                className="mt-2 text-2xl font-bold"
                style={{ color: phase.color }}
              >
                {phase.name}
              </h2>
              <p className="mt-2 text-sm text-neutral-400">
                {phase.description}
              </p>
            </div>

            <div className="space-y-4">
              {phase.steps.map((step, i) => (
                <div
                  key={i}
                  className="border border-neutral-800 bg-neutral-950 p-5"
                >
                  <div className="flex items-baseline gap-3">
                    <span className="text-xs text-neutral-600">
                      {String(i + 1).padStart(2, "0")}
                    </span>
                    <h3 className="text-sm font-bold uppercase tracking-wider text-white">
                      {step.title}
                    </h3>
                  </div>
                  <ul className="mt-4 space-y-2">
                    {step.bullets.map((b, j) => (
                      <li
                        key={j}
                        className="flex gap-3 text-sm leading-relaxed text-neutral-300"
                      >
                        <span style={{ color: phase.color }}>›</span>
                        <span>{b}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>

            {/* KI-Prompt Block */}
            <div className="mt-6 border border-neutral-800">
              <div className="flex items-center justify-between border-b border-neutral-800 bg-neutral-950 px-4 py-2">
                <span className="text-[10px] uppercase tracking-[0.2em] text-neutral-500">
                  &gt; KI-Prompt
                </span>
                <button
                  onClick={() => handleCopy(phase.prompt, phase.id)}
                  className="border border-neutral-700 px-2 py-1 text-[10px] uppercase tracking-wider text-neutral-300 transition hover:border-neutral-500 hover:text-white"
                >
                  {copiedId === phase.id ? "✓ Kopiert" : "Kopieren"}
                </button>
              </div>
              <pre className="whitespace-pre-wrap p-4 text-sm leading-relaxed text-neutral-300">
                {phase.prompt}
              </pre>
            </div>
          </section>
        )}

        {/* Kalkulator */}
        {isCalc && (
          <section>
            <div className="mb-6">
              <div className="text-[10px] tracking-[0.3em] text-neutral-500">
                PHASE 06
              </div>
              <h2 className="mt-2 text-2xl font-bold" style={{ color: ACCENT }}>
                Kalkulator
              </h2>
              <p className="mt-2 text-sm text-neutral-400">
                Live-Hochrechnung deiner monatlichen Pipeline.
              </p>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              <div className="space-y-6 border border-neutral-800 bg-neutral-950 p-6">
                <Slider
                  label="Werbebudget"
                  suffix="€ / Monat"
                  value={werbebudget}
                  min={100}
                  max={5000}
                  step={100}
                  onChange={setWerbebudget}
                />
                <Slider
                  label="Cost per Lead"
                  suffix="€"
                  value={costPerLead}
                  min={5}
                  max={100}
                  step={1}
                  onChange={setCostPerLead}
                />
                <Slider
                  label="Conversion Rate"
                  suffix="%"
                  value={conversionRate}
                  min={1}
                  max={50}
                  step={1}
                  onChange={setConversionRate}
                />
                <Slider
                  label="Projektpreis"
                  suffix="€"
                  value={projektpreis}
                  min={500}
                  max={10000}
                  step={100}
                  onChange={setProjektpreis}
                />
              </div>

              <div className="space-y-4">
                <Stat
                  label="Leads / Monat"
                  value={leads.toLocaleString("de-DE")}
                  big
                  accent={ACCENT}
                />
                <Stat
                  label="Projekte / Monat"
                  value={projekte.toLocaleString("de-DE")}
                />
                <Stat
                  label="Umsatz / Monat"
                  value={`${umsatz.toLocaleString("de-DE")} €`}
                />
                <Stat
                  label="ROI"
                  value={`${roi.toLocaleString("de-DE")} %`}
                  accent={roi >= 0 ? "#22C55E" : "#EF4444"}
                />
              </div>
            </div>

            <div className="mt-6 border border-neutral-800 bg-neutral-950 p-4 text-xs text-neutral-500">
              <span className="text-neutral-400">Formel:</span> leads = budget /
              cpl &nbsp;·&nbsp; projekte = leads × conv% &nbsp;·&nbsp; umsatz =
              projekte × preis &nbsp;·&nbsp; roi = (umsatz − budget) / budget
            </div>
          </section>
        )}

        <footer className="mt-16 border-t border-neutral-800 pt-6 text-[10px] uppercase tracking-[0.2em] text-neutral-600">
          // ai-website-workflow — next.js 15 · tailwind v4
        </footer>
      </div>
    </main>
  );
}

function Slider({ label, value, min, max, step, onChange, suffix }) {
  return (
    <div>
      <div className="mb-2 flex items-baseline justify-between">
        <label className="text-[10px] uppercase tracking-[0.2em] text-neutral-400">
          {label}
        </label>
        <span className="text-sm font-bold text-white">
          {value.toLocaleString("de-DE")}
          <span className="ml-1 text-xs font-normal text-neutral-500">
            {suffix}
          </span>
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full cursor-pointer"
      />
      <div className="mt-1 flex justify-between text-[10px] text-neutral-600">
        <span>{min.toLocaleString("de-DE")}</span>
        <span>{max.toLocaleString("de-DE")}</span>
      </div>
    </div>
  );
}

function Stat({ label, value, accent, big }) {
  return (
    <div className="border border-neutral-800 bg-neutral-950 p-5">
      <div className="text-[10px] uppercase tracking-[0.2em] text-neutral-500">
        {label}
      </div>
      <div
        className={`mt-2 font-bold ${big ? "text-4xl" : "text-2xl"}`}
        style={{ color: accent || "#ffffff" }}
      >
        {value}
      </div>
    </div>
  );
}
