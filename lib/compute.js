// Calcul du rapport : Meta (dépense, CPL), inscrits du Google Sheet et A/B test PostHog.
import { getMeta } from './meta.js';
import { getSignups } from './sheet.js';
import { getAb } from './posthog.js';

const parisToday = () => new Intl.DateTimeFormat('en-CA', { timeZone: 'Europe/Paris' }).format(new Date());

export async function compute(challenge) {
  const today = parisToday();
  const closed = challenge.status === 'done' && !!challenge.endDate;
  const until = challenge.endDate && challenge.endDate < today ? challenge.endDate : today;
  const { posthog, ...pub } = challenge;
  const base = { challenge: pub, today, until, closed, generatedAt: new Date().toISOString() };
  if (challenge.startDate > today) return { ...base, notStarted: true, meta: null, signups: null, abtest: null, warnings: [], errors: [] };

  const warnings = [], errors = [];
  const [meta, signups, abtest] = await Promise.all([
    getMeta(challenge.startDate, until, warnings).catch(e => (errors.push(e.message), null)),
    getSignups(challenge, challenge.startDate, until, warnings).catch(e => (errors.push(e.message), null)),
    posthog ? getAb(posthog, until, closed).catch(e => (warnings.push(e.message), null)) : Promise.resolve(undefined),
  ]);

  // CPL réel = dépense Meta / inscrits « Meta » du Sheet (total et par jour).
  if (meta && signups) {
    const metaKey = challenge.sources.find(s => s.meta)?.key;
    const byDay = Object.fromEntries(signups.daily.map(d => [d.date, d.sources[metaKey] || 0]));
    meta.signupsSheet = signups.channels.find(c => c.key === metaKey)?.total ?? 0;
    meta.cplReel = meta.signupsSheet ? meta.spend / meta.signupsSheet : null;
    meta.daily = meta.daily.map(d => ({ ...d, signupsSheet: byDay[d.date] ?? 0, cplReel: byDay[d.date] ? d.spend / byDay[d.date] : null }));
  }
  return { ...base, meta, signups, abtest, warnings, errors };
}
