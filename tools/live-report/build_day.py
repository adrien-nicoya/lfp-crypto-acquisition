"""Génère le panel d'un jour J2+ et le remplace dans live/index.html.

Usage : python3 build_day.py <page.html> <dossier jour> <dossier J1>
Le dossier du jour contient liveViewership_*.csv et event-data-*.csv (export Calendly cumulé),
et éventuellement comments.txt + clusters.json (analyse du chat).
"""
import csv, glob, json, collections, html, sys, os, re

PAGE, DDIR, J1DIR = sys.argv[1], sys.argv[2], sys.argv[3]
cfg = json.load(open(os.path.join(DDIR, 'day.json'), encoding='utf-8'))
J = cfg['day']                      # 'J2'
DATE = cfg['date']                  # '2026-11-23'
LABEL = cfg['label']                # 'lun. 23 nov.'
START_MIN = cfg['start_min']        # minutes depuis minuit (Paris) du début du direct
INSCRITS = cfg['inscrits']
J1 = cfg['j1']                      # valeurs historiques du J1 (figées à la date du rapport J1)
NB = ' '

def n(x): return f"{x:,}".replace(',', NB)
def pct(x, d=1): return f"{x*100:.{d}f}".replace('.', ',') + NB + '%'
def num(x, d=1): return f"{x:.{d}f}".replace('.', ',')
def hm(mins): return f"{(mins // 60) % 24}h{mins % 60:02d}"
esc = lambda s: html.escape(s, quote=True)

def delta_ratio(cur, base):
    r = cur / base - 1
    cls = 'neu' if abs(r) < 0.01 else ('pos' if r > 0 else 'neg')
    return f'<span class="kpi-delta {cls}">{"+" if r >= 0 else "−"}{num(abs(r) * 100)}{NB}% vs J1</span>'
def delta_pt(cur, base):
    d = (cur - base) * 100
    cls = 'neu' if abs(d) < 1 else ('pos' if d > 0 else 'neg')
    return f'<span class="kpi-delta {cls}">{"+" if d >= 0 else "−"}{num(abs(d))}{NB}pt vs J1</span>'

def curve_of(d):
    vr = list(csv.DictReader(open(glob.glob(f'{d}/liveViewership*')[0], encoding='utf-8-sig')))
    k = list(vr[0].keys())
    return [(int(r[k[0]]), int(r[k[1]])) for r in vr], sum(int(r[k[5]] or 0) for r in vr)

curve, reactions = curve_of(DDIR)
curve1, _ = curve_of(J1DIR)
peak_sec, peak = max(curve, key=lambda p: p[1])
duration = curve[-1][0]

# ---------- Calendly (réservations actives, non dédoublonnées) ----------
cal = list(csv.DictReader(open(glob.glob(f'{DDIR}/event-data*')[0], encoding='utf-8-sig')))
active = cal  # toutes les réservations, doublons et annulations compris
ts = lambda r: r['Event Created Date & Time']
soir = [r for r in active if ts(r)[:10] == DATE and ts(r)[11:13] >= '20']
journee = [r for r in active if ts(r)[:10] == DATE and ts(r)[11:13] < '20']
cumul = [r for r in active if ts(r)[:10] <= DATE]
uniq = lambda rs: len({r['Invitee Email'].lower().strip() for r in rs})
slots = collections.Counter()
for r in soir:
    h, m = int(ts(r)[11:13]), int(ts(r)[14:16])
    slots[f"{h}h{(m // 15) * 15:02d}"] += 1
J1_SLOTS = J1['slots']

def sit_of(rs):
    c = collections.Counter(r['Response 2'].strip().lstrip('⁠').rstrip('.') for r in rs)
    return collections.Counter({('Sans réponse' if k.startswith('Où en êtes') else k): v for k, v in c.items()})

# ---------- SVG ----------
MARKERS = cfg.get('markers', [])
def mins20(t):
    h, m = map(int, t.split(':')); return h * 60 + m - 20 * 60
def marks_svg(X, T, PH):
    out = []
    for i, mk in enumerate(MARKERS, 1):
        x = X(mins20(mk['time']))
        out.append(f'<line x1="{x:.1f}" y1="{T-8}" x2="{x:.1f}" y2="{T+PH}" stroke="#011c40" stroke-width="1.1" stroke-dasharray="3,4" opacity=".55"/>'
                   f'<circle cx="{x:.1f}" cy="{T-16}" r="9" fill="#011c40"/><text x="{x:.1f}" y="{T-12}" text-anchor="middle" font-size="11" font-weight="700" fill="#fff">{i}</text>')
    return ''.join(out)
def marks_legend():
    if not MARKERS: return ''
    return '<ol class="marks">' + ''.join(
        f'<li><span class="mk-n">{i}</span><span class="mk-t">{mk["time"].replace(":", "h")}</span><span class="mk-l"><strong>{esc(mk["label"])}</strong>'
        + (f' · {esc(mk["note"])}' if mk.get('note') else '') + '</span></li>' for i, mk in enumerate(MARKERS, 1)) + '</ol>'

def retention_svg():
    W, H, L, R, T, B = 920, 440, 60, 30, 76, 60
    PW, PH = W - L - R, H - T - B
    ymax, xmax = 1200, 270
    X = lambda m: L + m / xmax * PW
    Y = lambda v: T + PH - v / ymax * PH
    p = []
    for gy in range(0, ymax + 1, 200):
        p.append(f'<line x1="{L}" y1="{Y(gy):.1f}" x2="{W-R}" y2="{Y(gy):.1f}" stroke="#e3e8ef"/>'
                 f'<text x="{L-10}" y="{Y(gy)+4:.1f}" text-anchor="end" font-size="12" fill="#5b6b82">{n(gy)}</text>')
    for mm in range(0, xmax + 1, 30):
        p.append(f'<line x1="{X(mm):.1f}" y1="{T}" x2="{X(mm):.1f}" y2="{T+PH}" stroke="#f1f4f8"/>'
                 f'<text x="{X(mm):.1f}" y="{T+PH+20}" text-anchor="middle" font-size="12" fill="#5b6b82">{hm(20*60+mm).replace("h00","h")}</text>')
    off1, off = J1['start_min'] - 20 * 60, START_MIN - 20 * 60
    pts1 = " ".join(f"{X(off1 + s/60):.1f},{Y(v):.1f}" for s, v in curve1)
    pts = [f"{X(off + s/60):.1f},{Y(v):.1f}" for s, v in curve]
    area = pts + [f"{X(off + curve[-1][0]/60):.1f},{Y(0):.1f}", f"{X(off):.1f},{Y(0):.1f}"]
    px, py = X(off + peak_sec / 60), Y(peak)
    p1s, p1 = max(curve1, key=lambda q: q[1])
    return f'''<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;display:block" role="img" aria-label="Spectateurs simultanés pendant le {J}">
  <defs><linearGradient id="rg{J}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#056cf2" stop-opacity=".22"/><stop offset="100%" stop-color="#056cf2" stop-opacity="0"/></linearGradient></defs>
  {"".join(p)}
  <line x1="{L}" y1="{T+PH}" x2="{W-R}" y2="{T+PH}" stroke="#c5cfdc" stroke-width="1.5"/>
  <polygon points="{" ".join(area)}" fill="url(#rg{J})"/>
  <polyline points="{" ".join(pts)}" fill="none" stroke="#056cf2" stroke-width="2.4" stroke-linejoin="round"/>
  {marks_svg(X, T, PH)}
  <circle cx="{px:.1f}" cy="{py:.1f}" r="4.5" fill="#056cf2" stroke="#fff" stroke-width="2"/>
  <text x="{px:.1f}" y="{py-10:.1f}" text-anchor="middle" font-size="12" font-weight="700" fill="#011c40">{n(peak)} · {hm(START_MIN + peak_sec // 60)}</text>
  <rect x="{L}" y="8" width="14" height="14" rx="2" fill="#056cf2"/><text x="{L+22}" y="20" font-size="13" font-weight="600" fill="#011c40">{J} ({LABEL}) · pic {n(peak)}</text>
</svg>'''

def bars_svg():
    labels = [f"{h}h{m:02d}" for h in (20, 21, 22, 23) for m in (0, 15, 30, 45)]
    W, H, L, R, T, B = 920, 300, 50, 30, 40, 44
    PW, PH = W - L - R, H - T - B
    ymax = max(slots.values()) * 1.18
    Y = lambda v: T + PH - v / ymax * PH
    sw = PW / len(labels)
    p = []
    for i in range(5):
        gy = round(ymax * i / 4)
        p.append(f'<line x1="{L}" y1="{Y(gy):.1f}" x2="{W-R}" y2="{Y(gy):.1f}" stroke="#e3e8ef"/><text x="{L-6}" y="{Y(gy)+4:.1f}" text-anchor="end" font-size="10" fill="#5b6b82">{gy}</text>')
    for i, lab in enumerate(labels):
        v = slots.get(lab, 0)
        bw = sw * 0.6
        x2 = L + i * sw + sw * 0.2
        p.append(f'<rect x="{x2:.1f}" y="{Y(v):.1f}" width="{bw:.1f}" height="{T+PH-Y(v):.1f}" rx="2" fill="#056cf2"/>')
        if v: p.append(f'<text x="{x2+bw/2:.1f}" y="{Y(v)-5:.1f}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#011c40">{v}</text>')
        p.append(f'<text x="{L + i*sw + sw/2:.1f}" y="{H-B+18}" text-anchor="middle" font-size="10.5" fill="#5b6b82">{lab}</text>')
    return f'''<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;display:block" role="img" aria-label="RDV par tranche de 15 minutes pendant le {J}">
  {"".join(p)}
  <rect x="{L}" y="8" width="14" height="14" rx="2" fill="#056cf2"/><text x="{L+22}" y="20" font-size="13" font-weight="600" fill="#011c40">{J} soir (total {n(len(soir))})</text>
</svg>'''

def dist(title, items, total):
    rows_ = "".join(
        f'<div class="dist-row"><div class="dist-label">{esc(l)}</div><div class="dist-bar-wrap"><div class="dist-bar" style="width:{v/total*100:.1f}%"></div></div>'
        f'<div class="dist-pct">{pct(v/total)}</div><div class="dist-n">{n(v)}</div></div>'
        for l, v in sorted(items.items(), key=lambda kv: -kv[1]))
    return f'<div class="qual-block"><h4>{esc(title)}</h4>{rows_}</div>'

def kpi(label, value, meta='', delta=''):
    return (f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div>'
            + (f'<div class="kpi-meta">{meta}</div>' if meta else '') + delta + '</div>')

# ---------- Chat (optionnel) ----------
def chat_section():
    cards_file = os.path.join(DDIR, 'cards.json')
    if not os.path.exists(cards_file):
        return f'''<div class="section"><h2>💬 Analyse du chat</h2>
    <div class="pending" style="padding:32px 20px"><div class="pending-ico">⏳</div><div class="pending-title">Analyse du chat du {J} en attente</div><div class="pending-desc">Ajoutée dès réception de l'export des commentaires.</div></div></div>'''
    return open(cards_file, encoding='utf-8').read()

# ---------- Panel ----------
peak_clock = hm(START_MIN + peak_sec // 60)
RET = cfg.get('ret_base', {'label': 'J1', 'peak': J1['peak']})  # jour de référence de la rétention
ret = peak / RET['peak']
tx = len(soir) / peak
waves = sorted(slots.items(), key=lambda kv: kv[0])
early = sum(v for k, v in slots.items() if k < '21h00')
late = sum(v for k, v in slots.items() if k >= '22h00')
end_min = START_MIN + duration // 60

def count_between(a, b):
    return sum(a <= ts(r)[11:16] <= b for r in soir)
bars_lede = cfg['bars_lede'].format(**{k: n(count_between(*v)) for k, v in cfg.get('bars_counts', {}).items()}) if cfg.get('bars_lede') else \
    f"Deux vagues ce soir : {n(early)} RDV entre 20h et 21h, en début de live, puis {n(late)} après 22h au moment de l'appel à l'action."
has_chat = os.path.exists(os.path.join(DDIR, 'cards.json'))
notes = ([] if has_chat else [f"<strong>Analyse du chat à venir :</strong> l'export des commentaires du {J} n'est pas encore disponible. Heure de début du direct estimée à {hm(START_MIN)}, à confirmer avec le chat."]) + cfg.get('notes', [])
banner = ''.join(f'  <div class="banner warn">{x}</div>' for x in notes)
panel = f'''<section class="tab-panel active" id="panel-{J.lower()}" role="tabpanel">
{banner}

  <div class="section">
    <h2>Indicateurs clés</h2>
    <div class="kpi-row">
      {kpi('Pic spectateurs', n(peak), f'à {peak_clock}')}
      {kpi('Rétention de participation', pct(ret), f'{n(peak)} au pic pour {n(RET["peak"])} au {RET["label"]}')}
      {kpi(f'RDV {J} soir', n(len(soir)), f'{n(len(journee))} sur la journée<br>{n(len(soir) + len(journee))} au total {J}')}
      {kpi('Cumul challenge', n(len(cumul)), 'tous les RDV pris depuis le J1')}
      {kpi('Taux RDV soir / pic', pct(tx), f'{n(len(soir))} RDV pour {n(peak)} au pic')}
      {kpi('Taux RDV / inscrits', pct(len(cumul) / INSCRITS), f'{n(len(cumul))} RDV au total pour {n(INSCRITS)} inscrits')}
    </div>
  </div>

  <div class="section">
    <h2>Courbe de rétention : spectateurs simultanés <span class="h2-sub">({J} · {LABEL})</span></h2>
    {retention_svg()}
    {marks_legend()}
    <p class="note right">Direct de {hm(START_MIN)} à {hm(end_min)} · durée {duration // 3600}h{duration % 3600 // 60:02d} · pic {n(peak)} · {n(curve[-1][1])} spectateurs à la fin ({pct(curve[-1][1] / peak, 0)} du pic)</p>
  </div>

  <div class="section">
    <h2>Prises de RDV par tranche de 15 minutes <span class="h2-sub">({J} soir)</span></h2>
    <p class="lede">{bars_lede}</p>
    {bars_svg()}
    <p class="note right">Toutes les réservations Calendly, doublons et annulations compris, par heure de création (heure de Paris).</p>
  </div>


  {chat_section()}
</section>'''

# ---------- Injection ----------
s = open(PAGE, encoding='utf-8').read()
pat = re.compile(r'<section class="tab-panel[^"]*" id="panel-%s"[^>]*>.*?</section>' % J.lower(), re.S)
assert pat.search(s), 'panel introuvable'
s = pat.sub(lambda m: panel, s, count=1)
# l'ancien panel actif devient normal (masqué), le nouveau jour devient actif
s = re.sub(r'<section class="tab-panel active" id="panel-(?!%s)([a-z0-9]+)" role="tabpanel">' % J.lower(),
           r'<section class="tab-panel" id="panel-\1" role="tabpanel" hidden>', s)
s = re.sub(r'<button class="tab-btn active" type="button" role="tab" data-tab="([a-z0-9]+)" aria-selected="true">',
           r'<button class="tab-btn" type="button" role="tab" data-tab="\1" aria-selected="false">', s)
s = re.sub(r'<button class="tab-btn[^"]*" type="button" role="tab" data-tab="%s" aria-selected="(?:true|false)">' % J.lower(),
           f'<button class="tab-btn active" type="button" role="tab" data-tab="{J.lower()}" aria-selected="true">', s)
if '.marks{' not in s:
    s = s.replace('.pending{text-align:center', '.marks{list-style:none;margin:14px 0 0;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:6px 28px;font-size:13px}\n.marks li{display:flex;gap:8px;align-items:baseline}\n.mk-n{flex:none;width:20px;height:20px;border-radius:50%;background:var(--ink);color:#fff;font-size:11px;font-weight:700;display:inline-grid;place-items:center}\n.mk-t{flex:none;width:42px;font-weight:700}\n.mk-l{color:var(--muted)}\n.mk-l strong{color:var(--ink);font-weight:600}\n@media (max-width:760px){.marks{grid-template-columns:1fr}}\n.pending{text-align:center', 1)
if '.kpi-delta' not in s:
    s = s.replace('.kpi-meta{font-size:12px;color:var(--muted)}',
                  '.kpi-meta{font-size:12px;color:var(--muted)}\n.kpi-delta{display:inline-block;margin-top:6px;font-size:11.5px;font-weight:700}\n.kpi-delta.pos{color:#16a34a}.kpi-delta.neg{color:#dc2626}.kpi-delta.neu{color:#94a3b8}')
open(PAGE, 'w', encoding='utf-8').write(s)
print(J, 'peak', peak, peak_clock, 'ret', round(ret, 3), 'soir', len(soir), uniq(soir), 'journee', len(journee), 'cumul', len(cumul), uniq(cumul),
      'tx', round(tx, 3), 'slots', dict(slots), 'early', early, 'late', late, 'dur', duration)
