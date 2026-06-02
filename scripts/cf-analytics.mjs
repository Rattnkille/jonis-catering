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
