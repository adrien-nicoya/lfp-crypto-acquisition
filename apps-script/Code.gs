/**
 * Dashboard acquisition LFP Crypto — à coller dans le Sheet (Extensions → Apps Script).
 * Renvoie uniquement des comptages (aucun email ni téléphone) :
 *   { total, byDay: { 'AAAA-MM-JJ': { 'Meta': n, ... } }, noDate, duplicates }
 * Déploiement : Déployer → Nouveau déploiement → Application web,
 *   « Exécuter en tant que : moi », « Accès : tout le monde ».
 */
const TOKEN = 'REMPLACER_PAR_UN_JETON'; // même valeur que SHEET_TOKEN dans Vercel
const TZ = 'Europe/Paris';

function doGet(e) {
  if (!e || !e.parameter || e.parameter.token !== TOKEN) return json({ error: 'Jeton invalide' });
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
  const rows = sheet.getDataRange().getValues();
  const head = rows.shift().map(h => String(h).trim().toLowerCase());
  const iEmail = head.indexOf('email');
  const iSource = head.indexOf('source');
  const iDate = head.findIndex(h => h.indexOf('date') === 0);
  if (iSource < 0 || iDate < 0) return json({ error: 'Colonnes « source » ou « date inscription » introuvables' });

  const seen = {}, byDay = {};
  let total = 0, noDate = 0, duplicates = 0;
  rows.forEach(r => {
    const email = iEmail >= 0 ? String(r[iEmail]).trim().toLowerCase() : '';
    if (!email && !r[iSource] && !r[iDate]) return; // ligne vide
    const day = toDay(r[iDate]);
    if (!day) { noDate++; return; } // avant le dédoublonnage : une ligne sans date ne « réserve » pas l'email
    if (email) { if (seen[email]) { duplicates++; return; } seen[email] = true; }
    const src = String(r[iSource] || '').trim() || 'Sans source';
    byDay[day] = byDay[day] || {};
    byDay[day][src] = (byDay[day][src] || 0) + 1;
    total++;
  });
  return json({ total, byDay, noDate, duplicates, generatedAt: new Date().toISOString() });
}

// Date réelle du Sheet, ou texte « JJ/MM/AAAA HH:MM:SS » / « AAAA-MM-JJ… ».
function toDay(v) {
  if (Object.prototype.toString.call(v) === '[object Date]' && !isNaN(v)) return Utilities.formatDate(v, TZ, 'yyyy-MM-dd');
  const s = String(v || '').trim();
  let m = s.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})/);
  if (m) return m[3] + '-' + ('0' + m[2]).slice(-2) + '-' + ('0' + m[1]).slice(-2);
  m = s.match(/^(\d{4})-(\d{2})-(\d{2})/);
  return m ? m[1] + '-' + m[2] + '-' + m[3] : null;
}

function json(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}
