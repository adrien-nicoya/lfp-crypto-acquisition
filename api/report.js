// GET /api/report : challenge en cours → direct ; challenge terminé et figé → instantané.
import challenge from '../lib/config.js';
import { compute } from '../lib/compute.js';
import { getSnapshot } from '../lib/store.js';

export const config = { maxDuration: 30 };

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  if (challenge.status === 'done') {
    const snap = await getSnapshot().catch(() => null);
    if (snap) return res.status(200).json({ ...snap, frozen: true });
  }
  const data = await compute(challenge);
  res.status(data.meta || data.signups || data.notStarted ? 200 : 502).json({ ...data, frozen: false });
}
