// POST /api/freeze : recalcule le challenge terminé et enregistre l'instantané.
import challenge from '../lib/config.js';
import { compute } from '../lib/compute.js';
import { saveSnapshot } from '../lib/store.js';

export const config = { maxDuration: 30 };

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') return res.status(405).json({ errors: ['POST uniquement'] });
  if (challenge.status !== 'done') return res.status(400).json({ errors: ['Un challenge en cours ne se fige pas'] });
  const data = await compute(challenge);
  if (data.errors.length) return res.status(502).json({ ...data, frozen: false });
  try {
    await saveSnapshot(data);
    res.status(200).json({ ...data, frozen: true });
  } catch (e) {
    res.status(500).json({ ...data, frozen: false, errors: [e.message] });
  }
}
