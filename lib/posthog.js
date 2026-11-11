// A/B test de la page d'inscription (PostHog) : visites ($pageview) et inscriptions (« inscription ») par version.
const env = process.env;

function normCdf(z) {
  const t = 1 / (1 + 0.3275911 * Math.abs(z) / Math.SQRT2);
  const y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-(z * z) / 2);
  return z >= 0 ? (1 + y) / 2 : (1 - y) / 2;
}

const clean = v => String(v).replace(/[^A-Za-z0-9_-]/g, '');
const ts = v => new Date(v).toISOString().slice(0, 19).replace('T', ' ');

export async function getAb(cfg, until) {
  if (!env.POSTHOG_PERSONAL_API_KEY) throw new Error('PostHog : variable POSTHOG_PERSONAL_API_KEY manquante');
  const host = (env.POSTHOG_HOST || 'https://eu.posthog.com').replace(/\/$/, '');
  const visitEvent = cfg.visitEvent || '$pageview', signupEvent = cfg.signupEvent || 'inscription';
  const wanted = [...cfg.test.variants, ...(cfg.pages || []).map(p => p.variant)].map(clean);
  const end = new Date(new Date(until + 'T00:00:00Z').getTime() + 2 * 864e5).toISOString(); // marge fuseau
  const query = `SELECT properties.variant AS v, countIf(event = '${visitEvent}') AS visits, countIf(event = '${signupEvent}') AS signups
    FROM events
    WHERE event IN ('${visitEvent}', '${signupEvent}')
      AND timestamp >= toDateTime('${ts(cfg.since)}') AND timestamp < toDateTime('${ts(end)}')
      AND properties.$host = '${cfg.host.replace(/[^a-z0-9.-]/gi, '')}'
      AND properties.variant IN (${wanted.map(v => `'${v}'`).join(', ')})
    GROUP BY v`;
  const r = await fetch(`${host}/api/projects/${cfg.projectId}/query/`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${env.POSTHOG_PERSONAL_API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: { kind: 'HogQLQuery', query } }),
  });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(`PostHog ${r.status} : ${j.detail || 'requête refusée'}`);
  const rows = Object.fromEntries((j.results || []).map(([v, visits, signups]) => [v, { visits: Number(visits) || 0, signups: Number(signups) || 0 }]));
  const row = v => { const x = rows[v] || { visits: 0, signups: 0 }; return { variant: v, ...x, rate: x.visits ? x.signups / x.visits : null }; };

  const variants = cfg.test.variants.map(clean).map(row);
  const [ref, ...others] = variants;
  const alpha = 0.05 / Math.max(others.length, 1);
  const comparisons = ref.visits ? others.filter(x => x.visits).map(x => {
    const p = (ref.signups + x.signups) / (ref.visits + x.visits);
    const se = Math.sqrt(p * (1 - p) * (1 / ref.visits + 1 / x.visits));
    const z = se ? (x.rate - ref.rate) / se : 0;
    const pValue = 2 * (1 - normCdf(Math.abs(z)));
    return { variant: x.variant, uplift: ref.rate ? x.rate / ref.rate - 1 : null, pValue, significant: pValue < alpha };
  }) : [];
  let result = null;
  if (comparisons.length) {
    const best = variants.filter(x => x.visits).reduce((a, b) => (b.rate > a.rate ? b : a));
    const significant = best === ref ? comparisons.every(c => c.significant && c.uplift < 0)
      : !!comparisons.find(c => c.variant === best.variant && c.significant);
    const cmp = comparisons.find(c => c.variant === best.variant);
    result = { ref: ref.variant, leader: best.variant, significant, alpha, comparisons, uplift: cmp ? cmp.uplift : null };
  }
  return {
    label: cfg.test.label, audience: cfg.test.audience || null, since: cfg.since, variants, test: result,
    pages: (cfg.pages || []).map(p => ({ ...row(clean(p.variant)), label: p.label || null, audience: p.audience || null })),
  };
}
