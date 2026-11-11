/**
 * Script Google Ads — dépense par jour vers le Google Sheet du dashboard LFP Crypto.
 * À installer dans le compte Google Ads : Outils → Actions groupées → Scripts → « + ».
 * Fréquence : toutes les heures. Réécrit l'onglet « Google Ads » à chaque exécution.
 */
var SHEET_URL = 'https://docs.google.com/spreadsheets/d/12-YTe6XBagzwkaO0P98Kriww1PKI6Os_sTreLDx3skg/edit';
var TAB = 'Google Ads';
var START = '2026-11-11'; // début de la diffusion

function main() {
  var tz = AdsApp.currentAccount().getTimeZone();
  var today = Utilities.formatDate(new Date(), tz, 'yyyy-MM-dd');
  var rows = AdsApp.search(
    "SELECT segments.date, metrics.cost_micros, metrics.clicks, metrics.impressions, metrics.conversions " +
    "FROM customer WHERE segments.date BETWEEN '" + START + "' AND '" + today + "'"
  );
  var out = [['date', 'depense', 'clics', 'impressions', 'conversions', 'devise', 'maj']];
  var currency = AdsApp.currentAccount().getCurrencyCode();
  var now = Utilities.formatDate(new Date(), tz, 'yyyy-MM-dd HH:mm');
  while (rows.hasNext()) {
    var r = rows.next();
    out.push([
      r.segments.date,
      Math.round(Number(r.metrics.costMicros || 0) / 10000) / 100,
      Number(r.metrics.clicks || 0),
      Number(r.metrics.impressions || 0),
      Math.round(Number(r.metrics.conversions || 0) * 100) / 100,
      currency,
      now
    ]);
  }
  out = [out[0]].concat(out.slice(1).sort(function (a, b) { return a[0] < b[0] ? -1 : 1; }));

  var ss = SpreadsheetApp.openByUrl(SHEET_URL);
  var sh = ss.getSheetByName(TAB) || ss.insertSheet(TAB);
  sh.clearContents();
  sh.getRange(1, 1, out.length, out[0].length).setNumberFormat('@').setValues(out.map(function (l) { return l.map(String); }));
  Logger.log((out.length - 1) + ' jour(s) écrits dans « ' + TAB + ' ».');
}
