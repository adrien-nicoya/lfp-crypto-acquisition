// Inscrits du Google Sheet, via le script Apps Script (apps-script/Code.gs) : comptages par jour et par source.
const env = process.env;
const norm = s => String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]/g, '');

export async function getSignups(ch, since, until, warnings) {
  if (!env.SHEET_API_URL) throw new Error('SHEET_API_URL manquant');
  const url = new URL(env.SHEET_API_URL);
  if (env.SHEET_TOKEN) url.searchParams.set('token', env.SHEET_TOKEN);
  const r = await fetch(url, { redirect: 'follow' });
  const j = await r.json().catch(() => null);
  if (!r.ok || !j) throw new Error(`Google Sheet : réponse illisible (${r.status})`);
  if (j.error) throw new Error('Google Sheet : ' + j.error);

  const known = Object.fromEntries(ch.sources.map(s => [norm(s.key), s]));
  const totals = {}, other = {}, byDay = {};
  let before = 0;
  for (const [date, counts] of Object.entries(j.byDay || {})) {
    if (date > until) continue;
    if (date < since) { before += Object.values(counts).reduce((a, b) => a + b, 0); continue; }
    for (const [name, n] of Object.entries(counts)) {
      const s = known[norm(name)];
      const key = s ? s.key : 'Autre';
      if (!s) other[name] = (other[name] || 0) + n;
      totals[key] = (totals[key] || 0) + n;
      const d = (byDay[date] ??= { date, total: 0, sources: {} });
      d.total += n; d.sources[key] = (d.sources[key] || 0) + n;
    }
  }
  if (Object.keys(other).length) warnings.push(`Sources non reconnues dans le Sheet, comptées en « Autre » : ${Object.entries(other).map(([k, v]) => `${k} (${v})`).join(', ')}.`);
  if (j.noDate) warnings.push(`${j.noDate} ligne${j.noDate > 1 ? 's' : ''} du Sheet sans date d'inscription, non comptée${j.noDate > 1 ? 's' : ''}.`);

  const channels = [...ch.sources, ...(totals.Autre ? [{ key: 'Autre', label: 'Autre', color: '#94a3b8' }] : [])]
    .map(s => ({ key: s.key, label: s.label, color: s.color, target: s.target ?? null, meta: !!s.meta, total: totals[s.key] || 0 }));
  let cumul = 0;
  const daily = Object.values(byDay).sort((a, b) => a.date.localeCompare(b.date))
    .map(d => ({ ...d, cumul: (cumul += d.total) }));
  return { total: cumul, channels, daily, beforeStart: before, duplicates: j.duplicates || 0 };
}
