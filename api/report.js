// GET /api/report : Meta (dépense, CPL), inscrits du Google Sheet et A/B test PostHog, en direct.
import challenge from '../lib/config.js';
import { getMeta } from '../lib/meta.js';
import { getSignups } from '../lib/sheet.js';
import { getAb } from '../lib/posthog.js';

export const config = { maxDuration: 30 };

const parisToday = () => new Intl.DateTimeFormat('en-CA', { timeZone: 'Europe/Paris' }).format(new Date());

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  const today = parisToday();
  const until = challenge.endDate && challenge.endDate < today ? challenge.endDate : today;
  const { posthog, ...pub } = challenge;
  const base = { challenge: pub, today, until, generatedAt: new Date().toISOString() };
  if (challenge.startDate > today) return res.status(200).json({ ...base, notStarted: true, meta: null, signups: null, abtest: null, warnings: [], errors: [] });

  const warnings = [], errors = [];
  const [meta, signups, abtest] = await Promise.all([
    getMeta(challenge.startDate, until, warnings).catch(e => (errors.push(e.message), null)),
    getSignups(challenge, challenge.startDate, until, warnings).catch(e => (errors.push(e.message), null)),
    posthog ? getAb(posthog, until).catch(e => (warnings.push(e.message), null)) : Promise.resolve(undefined),
  ]);

  // CPL réel = dépense Meta / inscrits « Meta » du Sheet (total et par jour).
  if (meta && signups) {
    const metaKey = challenge.sources.find(s => s.meta)?.key;
    const byDay = Object.fromEntries(signups.daily.map(d => [d.date, d.sources[metaKey] || 0]));
    meta.signupsSheet = signups.channels.find(c => c.key === metaKey)?.total ?? 0;
    meta.cplReel = meta.signupsSheet ? meta.spend / meta.signupsSheet : null;
    meta.daily = meta.daily.map(d => ({ ...d, signupsSheet: byDay[d.date] ?? 0, cplReel: byDay[d.date] ? d.spend / byDay[d.date] : null }));
  }
  res.status(meta || signups ? 200 : 502).json({ ...base, meta, signups, abtest, warnings, errors });
}
