// Instantané figé du challenge terminé (Vercel Blob privé).
const enabled = () => !!(process.env.BLOB_STORE_ID || process.env.BLOB_READ_WRITE_TOKEN);
const KEY = 'snapshots/lfp-crypto.json';

export async function getSnapshot() {
  if (!enabled()) return null;
  const { get } = await import('@vercel/blob');
  const r = await get(KEY, { access: 'private', useCache: false }).catch(() => null);
  const stream = r?.stream || r?.body;
  if (!stream) return null;
  return JSON.parse(await new Response(stream).text());
}

export async function saveSnapshot(data) {
  if (!enabled()) throw new Error('Stockage non activé : connecte un store Vercel Blob au projet (Storage → Blob), puis redéploie.');
  const { put } = await import('@vercel/blob');
  await put(KEY, JSON.stringify(data), {
    access: 'private', addRandomSuffix: false, allowOverwrite: true, contentType: 'application/json',
  });
}
