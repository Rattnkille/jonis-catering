#!/usr/bin/env node
/**
 * Holt Cloudflare-Web-Analytics-Kennzahlen (RUM) per GraphQL Analytics API
 * und schreibt einen Markdown-Bericht nach reports/analytics.md.
 *
 * Erwartete Umgebungsvariablen (in der GitHub Action als Secrets gesetzt):
 *   CLOUDFLARE_API_TOKEN   – read-only Token mit Scope "Account Analytics: Read"
 *   CLOUDFLARE_ACCOUNT_ID  – Cloudflare Account-ID
 *   CLOUDFLARE_SITE_TAG    – optional; Default ist der Web-Analytics-Beacon-Token
 */

import { writeFile, mkdir } from 'node:fs/promises';

const API_TOKEN = process.env.CLOUDFLARE_API_TOKEN;
const ACCOUNT_ID = process.env.CLOUDFLARE_ACCOUNT_ID;
// Der Beacon-Token ist ohnehin öffentlich im Seitenquelltext – als Default ok.
const SITE_TAG = process.env.CLOUDFLARE_SITE_TAG || '558d48c00c6d4458ac8390fbc7f5b566';

if (!API_TOKEN || !ACCOUNT_ID) {
    console.error('Fehlende Secrets: CLOUDFLARE_API_TOKEN und/oder CLOUDFLARE_ACCOUNT_ID sind nicht gesetzt.');
    process.exit(1);
}

const DAYS = 30;
const fmt = (d) => d.toISOString().slice(0, 10);
const today = new Date();
const start = new Date(today);
start.setUTCDate(start.getUTCDate() - (DAYS - 1));
const START = fmt(start);
const END = fmt(today);

const group = (alias, extraFilter, dims, orderBy, limit) => `
  ${alias}: rumPageloadEventsAdaptiveGroups(
    filter: { date_geq: "${START}", date_leq: "${END}", siteTag: "${SITE_TAG}"${extraFilter} }
    limit: ${limit}
    orderBy: [${orderBy}]
  ) {
    count
    sum { visits }
    ${dims ? `dimensions { ${dims} }` : ''}
  }`;

const query = `
query {
  viewer {
    accounts(filter: { accountTag: "${ACCOUNT_ID}" }) {
      ${group('byDate', '', 'date', 'date_ASC', 60)}
      ${group('topReferers', '', 'refererHost', 'count_DESC', 10)}
      ${group('topPaths', '', 'requestPath', 'count_DESC', 10)}
      ${group('topCountries', '', 'countryName', 'count_DESC', 10)}
      ${group('byDevice', '', 'deviceType', 'count_DESC', 10)}
      ${group('byBrowser', '', 'userAgentBrowser', 'count_DESC', 10)}
    }
  }
}`;

const res = await fetch('https://api.cloudflare.com/client/v4/graphql', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${API_TOKEN}`,
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query }),
});

if (!res.ok) {
    console.error(`Cloudflare API HTTP ${res.status}: ${await res.text()}`);
    process.exit(1);
}

const json = await res.json();
if (json.errors && json.errors.length) {
    console.error('GraphQL-Fehler:', JSON.stringify(json.errors, null, 2));
    process.exit(1);
}

const account = json?.data?.viewer?.accounts?.[0];
if (!account) {
    console.error('Keine Account-Daten erhalten – Token-Scope oder Account-ID prüfen.');
    process.exit(1);
}

const sumCount = (rows) => rows.reduce((a, r) => a + (r.count || 0), 0);
const sumVisits = (rows) => rows.reduce((a, r) => a + (r.sum?.visits || 0), 0);

const byDate = account.byDate || [];
const last7 = byDate.slice(-7);
const prev7 = byDate.slice(-14, -7);

// --- Automatische Auswertung (regelbasiert, ohne KI / ohne Credits) ---
const views7 = sumCount(last7);
const viewsPrev7 = sumCount(prev7);
const views30 = sumCount(byDate);
const visits7 = sumVisits(last7);

const trend = (cur, prev) => {
    if (prev === 0) return cur === 0 ? '±0 %' : 'neu (Vorwoche 0)';
    const d = ((cur - prev) / prev) * 100;
    const arrow = d > 0.5 ? '▲ +' : d < -0.5 ? '▼ ' : '± ';
    return `${arrow}${Math.round(d)} %`;
};

const firstReal = (rows, key) => {
    const r = (rows || []).find((x) => {
        const v = (x.dimensions?.[key] || '').trim();
        return v && v.toLowerCase() !== 'none';
    });
    return r ? { label: r.dimensions[key], count: r.count } : null;
};

const topRef = firstReal(account.topReferers, 'refererHost');
const topPage = firstReal(account.topPaths, 'requestPath');

const insights = [];
insights.push(`- **Seitenaufrufe (7 Tage):** ${views7} — Trend ggü. Vorwoche: ${trend(views7, viewsPrev7)}`);
insights.push(`- **Besuche (7 Tage):** ${visits7}`);
insights.push(`- **Stärkste Quelle:** ${topRef ? `${topRef.label} (${topRef.count} Aufrufe)` : 'überwiegend direkt/unbekannt'}`);
insights.push(`- **Beliebteste Seite:** ${topPage ? `${topPage.label} (${topPage.count} Aufrufe)` : '–'}`);

const tips = [];
if (views30 === 0) {
    tips.push('Noch keine Daten im Zeitraum. Der Beacon ist live — Werte erscheinen, sobald die Seite besucht wird.');
} else if (views7 === 0) {
    tips.push('In den letzten 7 Tagen kein Traffic, im 30-Tage-Fenster aber schon. Google-Business-Profil und Social-Posts ankurbeln.');
} else {
    if (viewsPrev7 > 0 && views7 < viewsPrev7 * 0.8) {
        tips.push('Deutlicher Rückgang ggü. Vorwoche (>20 %). Quellen prüfen: Ist eine wichtige Referrer-Quelle weggebrochen?');
    }
    if (viewsPrev7 > 0 && views7 > viewsPrev7 * 1.2) {
        tips.push('Deutliches Wachstum ggü. Vorwoche (>20 %). Schauen, welche Quelle den Anstieg trägt, und dort nachlegen.');
    }
    if (!topRef) {
        tips.push('Fast nur Direktzugriffe, kaum Referrer. Sichtbarkeit über Google-Suche/-Maps und Verlinkungen ausbauen.');
    }
}
if (!tips.length) tips.push('Keine Auffälligkeiten — Werte im erwartbaren Rahmen.');

const autoEval = `${insights.join('\n')}\n\n**Hinweise:**\n${tips.map((t) => `- ${t}`).join('\n')}\n`;

const table = (rows, key, label) => {
    if (!rows || !rows.length) return `_Noch keine Daten._\n`;
    const lines = rows
        .map((r) => `| ${r.dimensions?.[key] || '(direkt/unbekannt)'} | ${r.count} |`)
        .join('\n');
    return `| ${label} | Seitenaufrufe |\n|---|---|\n${lines}\n`;
};

const seriesTable = (rows) => {
    if (!rows.length) return '_Noch keine Daten._\n';
    const lines = rows
        .map((r) => `| ${r.dimensions?.date} | ${r.count} | ${r.sum?.visits ?? '–'} |`)
        .join('\n');
    return `| Datum | Seitenaufrufe | Besuche |\n|---|---|---|\n${lines}\n`;
};

const report = `# Cloudflare Web Analytics – Bericht

> Automatisch generiert am ${new Date().toISOString().replace('T', ' ').slice(0, 16)} UTC.
> Zeitraum: **${START} bis ${END}** (letzte ${DAYS} Tage). Quelle: Cloudflare Web Analytics (RUM), cookieless.

## Überblick

| Kennzahl | Letzte 7 Tage | Letzte ${DAYS} Tage |
|---|---|---|
| Seitenaufrufe | ${sumCount(last7)} | ${sumCount(byDate)} |
| Besuche | ${sumVisits(last7)} | ${sumVisits(byDate)} |

## Automatische Auswertung

${autoEval}
## Verlauf pro Tag

${seriesTable(byDate)}

## Top-Quellen (Referrer)

${table(account.topReferers, 'refererHost', 'Referrer-Host')}

## Top-Seiten

${table(account.topPaths, 'requestPath', 'Pfad')}

## Top-Länder

${table(account.topCountries, 'countryName', 'Land')}

## Geräte

${table(account.byDevice, 'deviceType', 'Gerätetyp')}

## Browser

${table(account.byBrowser, 'userAgentBrowser', 'Browser')}
`;

await mkdir('reports', { recursive: true });
await writeFile('reports/analytics.md', report, 'utf8');
console.log(`Bericht geschrieben: reports/analytics.md (${sumCount(byDate)} Seitenaufrufe in ${DAYS} Tagen).`);
