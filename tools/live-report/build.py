"""Génère live/index.html (analyse post-live) pour le dashboard LFP Crypto."""
import csv, glob, json, collections, html, sys, os

D = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]
INSCRITS = 5662
START_MIN = 20 * 60 + 2  # début du direct : 20h02 (heure de Paris)
NB = ' '

def n(x): return f"{x:,}".replace(',', NB)
def pct(x, d=1): return f"{x*100:.{d}f}".replace('.', ',') + NB + '%'
def clock(sec):
    m = START_MIN + sec // 60
    return f"{(m // 60) % 24}h{m % 60:02d}"
esc = lambda s: html.escape(s, quote=True)

# ---------- YouTube ----------
vr = list(csv.DictReader(open(glob.glob(f'{D}/liveViewership*')[0], encoding='utf-8-sig')))
k = list(vr[0].keys())
curve = [(int(r[k[0]]), int(r[k[1]])) for r in vr]
reactions = sum(int(r[k[5]] or 0) for r in vr)
peak_sec, peak = max(curve, key=lambda p: p[1])
duration = curve[-1][0]

# ---------- Calendly ----------
cal = list(csv.DictReader(open(glob.glob(f'{D}/event-data*')[0], encoding='utf-8-sig')))
em = lambda r: r['Invitee Email'].lower().strip()
active = [r for r in cal if r['Canceled'] == 'false']
first = {}
for r in sorted(active, key=lambda r: r['Event Created Date & Time']):
    first.setdefault(em(r), r)
rdv = active  # réservations actives, non dédoublonnées
RDV = len(rdv)
UNIQ = len(first)
canceled = [r for r in cal if r['Canceled'] == 'true']
rebooked = sum(em(r) in first for r in canceled)
slots = collections.Counter()
for r in rdv:
    h, m = map(int, r['Event Created Date & Time'][11:16].split(':'))
    slots[f"{h}h{(m // 15) * 15:02d}"] += 1
first_rdv = min(r['Event Created Date & Time'][11:16] for r in rdv).replace(':', 'h')
sit = collections.Counter(r['Response 2'].strip().lstrip('⁠').rstrip('.') for r in rdv)
sit_labels = {"Où en êtes-vous aujourd'hui ?": 'Sans réponse'}
sit = collections.Counter({sit_labels.get(k2, k2): v for k2, v in sit.items()})
days = collections.Counter(r['Start Date & Time'][:10] for r in rdv)

# ---------- Chat ----------
rows = [l.split('\t') for l in open(f'{D}/comments.txt', encoding='utf-8').read().split('@end', 1)[1].strip().split('\n')]
MODS = {'@TeamModération1', '@SaturninDevinsLive'}
msgs_total = len(rows)
prospects = [r for r in rows if r[1] not in MODS]
prosp_authors = len({r[1] for r in prospects})
cl = json.load(open(f'{D}/clusters.json'))
clustered = len({tuple(x) for v in cl.values() for x in v})
def cnt(key): return len(cl[key]), len({x[1] for x in cl[key]})

# ---------- SVG rétention ----------
def retention_svg():
    W, H, L, R, T, B = 920, 420, 60, 30, 50, 60
    PW, PH = W - L - R, H - T - B
    ymax = 1200
    xmax = 270  # minutes depuis 20h00
    X = lambda mins_from_20h: L + mins_from_20h / xmax * PW
    Y = lambda v: T + PH - v / ymax * PH
    p = []
    for gy in range(0, ymax + 1, 200):
        p.append(f'<line x1="{L}" y1="{Y(gy):.1f}" x2="{W-R}" y2="{Y(gy):.1f}" stroke="#e3e8ef"/>'
                 f'<text x="{L-10}" y="{Y(gy)+4:.1f}" text-anchor="end" font-size="12" fill="#5b6b82">{n(gy)}</text>')
    for mm in range(0, xmax + 1, 30):
        lab = f"{(20 + mm // 60) % 24}h{mm % 60:02d}".replace('h00', 'h')
        p.append(f'<line x1="{X(mm):.1f}" y1="{T}" x2="{X(mm):.1f}" y2="{T+PH}" stroke="#f1f4f8"/>'
                 f'<text x="{X(mm):.1f}" y="{T+PH+20}" text-anchor="middle" font-size="12" fill="#5b6b82">{lab}</text>')
    pts = [f"{X(2 + s / 60):.1f},{Y(v):.1f}" for s, v in curve]
    area = pts + [f"{X(2 + curve[-1][0] / 60):.1f},{Y(0):.1f}", f"{X(2):.1f},{Y(0):.1f}"]
    cta = 2 + 155  # CTA ≈ 2h35 après le début (22h37)
    px, py = X(2 + peak_sec / 60), Y(peak)
    return f'''<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;display:block" role="img" aria-label="Spectateurs simultanés pendant le live">
  <defs><linearGradient id="rg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#056cf2" stop-opacity=".22"/><stop offset="100%" stop-color="#056cf2" stop-opacity="0"/></linearGradient></defs>
  {"".join(p)}
  <line x1="{L}" y1="{T+PH}" x2="{W-R}" y2="{T+PH}" stroke="#c5cfdc" stroke-width="1.5"/>
  <polygon points="{" ".join(area)}" fill="url(#rg)"/>
  <polyline points="{" ".join(pts)}" fill="none" stroke="#056cf2" stroke-width="2.4" stroke-linejoin="round"/>
  <line x1="{X(cta):.1f}" y1="{T}" x2="{X(cta):.1f}" y2="{T+PH}" stroke="#011c40" stroke-width="1.2" stroke-dasharray="4,4"/>
  <text x="{X(cta)+6:.1f}" y="{T+12}" font-size="11" font-weight="600" fill="#011c40">Lien de réservation · 22h37</text>
  <circle cx="{px:.1f}" cy="{py:.1f}" r="4.5" fill="#056cf2" stroke="#fff" stroke-width="2"/>
  <text x="{px:.1f}" y="{py-10:.1f}" text-anchor="middle" font-size="12" font-weight="700" fill="#011c40">{n(peak)} · {clock(peak_sec)}</text>
  <rect x="{L}" y="6" width="14" height="14" rx="2" fill="#056cf2"/><text x="{L+22}" y="18" font-size="13" font-weight="600" fill="#011c40">J1 Sommet Exponentiel (pic {n(peak)})</text>
</svg>'''

def bars_svg():
    labels = [f"{h}h{m:02d}" for h in (22, 23) for m in (0, 15, 30, 45)]
    W, H, L, R, T, B = 920, 300, 50, 30, 34, 44
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
        x0 = L + i * sw + sw * 0.18
        w = sw * 0.64
        p.append(f'<rect x="{x0:.1f}" y="{Y(v):.1f}" width="{w:.1f}" height="{T+PH-Y(v):.1f}" rx="3" fill="#056cf2"/>')
        if v: p.append(f'<text x="{x0+w/2:.1f}" y="{Y(v)-5:.1f}" text-anchor="middle" font-size="11" font-weight="700" fill="#011c40">{v}</text>')
        p.append(f'<text x="{x0+w/2:.1f}" y="{H-B+18}" text-anchor="middle" font-size="11" fill="#5b6b82">{lab}</text>')
    return f'''<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;display:block" role="img" aria-label="RDV par tranche de 15 minutes">
  {"".join(p)}
  <rect x="{L}" y="6" width="14" height="14" rx="2" fill="#056cf2"/><text x="{L+22}" y="18" font-size="13" font-weight="600" fill="#011c40">J1 Sommet Exponentiel (total {n(RDV)})</text>
</svg>'''

def dist(title, items, total, order=None):
    items = order(items) if order else sorted(items.items(), key=lambda kv: -kv[1])
    rows_ = "".join(
        f'<div class="dist-row"><div class="dist-label">{esc(l)}</div><div class="dist-bar-wrap"><div class="dist-bar" style="width:{v/total*100:.1f}%"></div></div>'
        f'<div class="dist-pct">{pct(v/total)}</div><div class="dist-n">{n(v)}</div></div>' for l, v in items)
    return f'<div class="qual-block"><h4>{esc(title)}</h4>{rows_}</div>'

JOURS = ['dim.', 'lun.', 'mar.', 'mer.', 'jeu.', 'ven.', 'sam.']
def day_label(d):
    import datetime
    dt = datetime.date.fromisoformat(d)
    return f"{JOURS[(dt.weekday() + 1) % 7].capitalize()} {dt.day} nov."
days_items = [(day_label(d), v) for d, v in sorted(days.items())]

# ---------- Clusters ----------
CARDS = [
 ('plateforme', '🏦', '« Quelle plateforme ? Kraken, Swissborg, mon PEA… »',
  "Premier sujet du chat. Il revient tout le live (comparatifs Kraken, Swissborg, OKX, Coinbase, Binance que plusieurs disent fermé en France) et explose après la pépite : 37 messages entre 23h32 et 23h47. Plusieurs prospects pensent pouvoir investir depuis leur PEA.",
  ["Il y a autant de plateformes que de cryptos, pouvez-vous nous lister les 3 meilleures plateformes selon vous ?",
   "Est-ce qu'on peut rester sur notre plateforme actuelle ? Ou faut-il forcément investir via votre plateforme ?",
   "Je suis en France et je n'ai qu'un PEA, comment je peux faire pour passer sur Kraken ?",
   "Mes cryptos sont sur Coinbase, dois-je migrer sur Kraken ou Swissborg ?"],
  "Afficher une slide fixe « Où acheter » (Kraken ou Swissborg, pas de PEA, liens d'ouverture) dès le début du J2, et l'épingler dans le chat."),
 ('peur', '🌍', '« Euro numérique, dette, banques : je suis inquiet »',
  "Réponse massive à la question « Êtes-vous inquiet ? » : 78 messages entre 21h02 et 21h32. L'euro numérique, le contrôle des comptes et les virements bloqués par la banque reviennent le plus. L'angle souveraineté résonne fortement.",
  ["Très inquiète par le risque de blocage des banques et l'obligation de l'euro numérique",
   "Tout est inquiétant et notamment un possible contrôle des changes et des capitaux",
   "Oui. Pas réussi à virer des sommes sur Kraken Pro.",
   "Nous ne sommes plus maîtres de notre argent"],
  "Reprendre 2 ou 3 de ces verbatims au début du J2 pour relier l'inquiétude exprimée à la solution, puis au CTA."),
 ('fiscal', '🧾', '« Et les impôts ? Les stablecoins vont être taxés ? »',
  "Pic à 21h02-21h17 pendant la séquence fiscalité : flat tax citée à 31,4 %, imposition à la conversion en euros, projet de taxe sur les échanges cryptos/stablecoins en 2027. Revient en fin de live.",
  ["Le futur budget de l'État prévoit de taxer les virements vers les stablecoins à 30 %, sauf si vous avez des astuces",
   "Quand on convertit en €, comment est-on taxé ?",
   "Est-ce qu'on doit déclarer aux impôts tant qu'on ne passe pas l'argent sur le compte bancaire ?",
   "Parlerez-vous dans les deux prochains jours de la fiscalité de manière plus approfondie ?"],
  "Prévoir une FAQ fiscalité courte (3 règles + le projet 2027) au J2 ou J3, et l'annoncer dès ce soir pour retenir l'audience."),
 ('lighter', '💎', '« Lighter : quel ticker, sur quelle plateforme ? »',
  "33 messages en 15 minutes après la pépite. Confusion de ticker (LIT = Litentry sur Kraken, Lighter = LIGHTER), question de la dilution de décembre, et dossier promis pas encore reçu.",
  ["Sur Kraken LIT = Litentry ! et Lighter = LIGHTER",
   "Possible d'avoir le dossier d'étude de LIGHTER ?",
   "Y a-t-il une dilution de LIT en décembre ?"],
  "Afficher le nom exact par plateforme sur la slide de la pépite et envoyer le dossier dans le mail du soir, avant la fin du live."),
]
EXTRA = [
 ('duree', '⏱️', '« C\'est trop long, il y aura un replay ? »',
  "Live de 4h29. Les demandes de replay arrivent dès les 20 premières minutes ; les départs pour « lever tôt » et les demandes de finir plus tôt se concentrent entre 23h30 et minuit.",
  ["Très bonne soirée, mais merci de finir plus tôt demain et mardi soir",
   "Intéressant mais long pour ceux qui se lèvent tôt le lendemain",
   "Y aura-t-il un replay pour demain soir car pas dispo demain soir ?"],
  "Annoncer la règle du replay à 20h et viser une fin vers 23h au J2, CTA compris."),
 ('prix', '💰', '« Combien ça coûte ? Quel montant minimum ? »',
  "Arrive après 22h, avant et pendant le CTA. Deux questions mêlées : le prix du programme (et « peut-on le payer en crypto ? », 5 fois) et le capital minimum pour commencer (10 000 €, 50 000 €, 60 000 € ?).",
  ["Quel est le minimum d'argent qu'il faut avoir pour rentrer ?",
   "Un capital d'investissement de 10 000 euros est-il suffisant pour commencer ?",
   "On peut payer en crypto le programme ?"],
  "Donner un ordre de grandeur du capital de départ avant le CTA pour rassurer les petits portefeuilles."),
 ('mail', '📩', '« Pas reçu le mail, le dossier, le calculateur »',
  "Confirmations de RDV non reçues, dossier de la pépite et calculateur introuvables, lien Kraken attendu. Se concentre après 22h45.",
  ["J'ai pris RDV mais pas reçu de mail de confirmation",
   "Où avons-nous le calculateur ?",
   "Vous aviez promis un dossier sur la pépite et ?"],
  "Rappeler à l'écran « vérifiez vos spams » et indiquer à quelle heure partent le mail et le dossier."),
 ('offres', '🔀', '« C\'est différent du Club Privé Crypto ? »',
  "Les membres existants (Club Privé Crypto, abonnés à vie, Patrimoine Souverain) ne comprennent pas comment l'offre s'articule avec ce qu'ils ont déjà.",
  ["Crypto Exponentielles c'est en remplacement du Club Privé Crypto ?",
   "Si on est déjà sur Crypto IA, y a-t-il un tarif préférentiel ?",
   "Club Privé Crypto existera toujours ?"],
  "Préparer une réponse type « je suis déjà membre » à épingler par la modération pendant le CTA."),
 ('pertes', '📉', "« J'ai perdu de l'argent, je veux me refaire »",
  "Dès la question sur le portefeuille (20h13-20h17), de nombreux prospects décrivent des pertes de 30 à 90 % (Pump, Solana, Bitcoin acheté au plus haut). Le thème revient vers 22h, juste avant le CTA. C'est aussi la 2e réponse du formulaire Calendly (26 %).",
  ["Retraité, investi à hauteur de 15 000 € avec 90 % de perte. Je n'y comprends rien.",
   "J'ai investi du bitcoin en 2022 et j'ai perdu depuis 60 % !",
   "Oui absolument, je veux récupérer surtout mes pertes"],
  "Prévoir au J2 un témoignage d'un membre parti en perte qui a remonté son portefeuille, pour traiter ce frein avant le CTA."),
 ('securite', '🔐', '« Et si la plateforme se fait pirater ? »',
  "Hacks d'exchanges (Binance, Coinbase), Ledger, ordinateur quantique : la question de la garde des cryptos revient surtout entre 21h17 et 21h47.",
  ["Quid en cas de piratage des bases de données crypto ?",
   "L'ordinateur quantique pourrait « craquer » les cryptos ?",
   "Vous conseillez une plateforme ou une clé Ledger ?"],
  "Ajouter une minute sur la sécurité (plateforme régulée + clé matérielle pour le long terme) au moment du choix de plateforme."),
]

# messages couverts par les cartes affichées
clustered = len({tuple(x) for c in CARDS + EXTRA for x in cl[c[0]]})

def card(c):
    key, ico, title, desc, samples, reco = c
    m, p = cnt(key)
    return (f'<div class="chat-card"><div class="chat-card-head"><div class="chat-card-title">{ico} {esc(title)}</div>'
            f'<div class="chat-card-count">{m}{NB}msgs · {p}{NB}pers.</div></div>'
            f'<div class="chat-card-desc">{esc(desc)}</div><ul class="chat-card-samples">'
            + "".join(f'<li>« {esc(s)} »</li>' for s in samples) +
            f'</ul><div class="chat-reco">🎯 {esc(reco)}</div></div>')

def kpi(label, value, meta='', flag=''):
    return (f'<div class="kpi"><div class="kpi-label">{label}{flag}</div><div class="kpi-value">{value}</div>'
            + (f'<div class="kpi-meta">{meta}</div>' if meta else '') + '</div>')

conv = peak / INSCRITS
panel_j1 = f'''<section class="tab-panel active" id="panel-j1" role="tabpanel">
  <div class="banner warn"><strong>RDV :</strong> export Calendly des réservations créées le 22/11 jusqu'à 23h59 ; celles prises après minuit n'y figurent pas.</div>

  <div class="section">
    <h2>Indicateurs clés</h2>
    <div class="kpi-row">
      {kpi('Inscrits challenge', n(INSCRITS), 'total définitif')}
      {kpi('Pic spectateurs', n(peak), f'à {clock(peak_sec)}')}
      {kpi('Taux conversion inscrits → pic', pct(conv), f'{n(peak)} au pic pour {n(INSCRITS)} inscrits')}
      {kpi('RDV J1 soir', n(RDV), f'{n(UNIQ)} personnes uniques · premier RDV à {first_rdv}')}
      {kpi('Taux RDV / inscrits', pct(RDV / INSCRITS), f'{pct(RDV / peak)} du pic spectateurs')}
    </div>
  </div>

  <div class="section">
    <h2>Courbe de rétention : spectateurs simultanés <span class="h2-sub">(J1 · dim. 22 nov.)</span></h2>
    {retention_svg()}
    <p class="note right">Direct de 20h02 à {clock(duration)} · durée {duration // 3600}h{duration % 3600 // 60:02d} · {n(curve[-1][1])} spectateurs à la fin ({pct(curve[-1][1] / peak, 0)} du pic)</p>
  </div>

  <div class="section">
    <h2>Prises de RDV par tranche de 15 minutes</h2>
    <p class="lede">Aucun RDV avant le lien de réservation. {n(slots['22h30'] + slots['22h45'] + slots['23h00'])} RDV sur {n(RDV)} ({pct((slots['22h30'] + slots['22h45'] + slots['23h00']) / RDV, 0)}) sont pris dans les 45 premières minutes qui suivent, puis le rythme retombe à une dizaine par quart d'heure.</p>
    {bars_svg()}
    <p class="note right">{n(RDV)} réservations actives ({n(UNIQ)} personnes uniques) · heure de création dans Calendly (heure de Paris)</p>
  </div>

  <div class="section">
    <h2>Qualité des leads</h2>
    <p class="lede">Réponses au formulaire Calendly des {n(RDV)} RDV du J1. Le formulaire ne pose qu'une question de qualification.</p>
    <div class="qual-grid">
      {dist("Où en êtes-vous aujourd'hui dans vos investissements ?", sit, RDV)}
      {dist('Date du rendez-vous', dict(days_items), RDV, order=lambda d: list(d.items()))}
    </div>
  </div>

  <div class="section">
    <h2>💬 Analyse du chat</h2>
    <p class="lede">Clusters émergents sur les {n(msgs_total)} messages du J1 ({n(len(prospects))} hors modération, écrits par {n(prosp_authors)} personnes, dont {n(clustered)} clusterisés). Le chat est aussi très positif : nombreux remerciements, témoignage de Magne très salué, et beaucoup de « RDV pris » après 22h40.</p>
    <div class="chat-grid">{"".join(card(c) for c in CARDS)}</div>
    <h3>Autres signaux</h3>
    <div class="chat-grid">{"".join(card(c) for c in EXTRA)}</div>
  </div>
</section>'''

def pending(j, date):
    return f'''<section class="tab-panel" id="panel-{j.lower()}" role="tabpanel" hidden>
  <div class="section"><div class="pending"><div class="pending-ico">⏳</div><div class="pending-title">Rapport {j} en attente</div><div class="pending-desc">Disponible après le live du {date}.</div></div></div>
</section>'''

TABS = [('J1', 'Dim 22 nov', True), ('J2', 'Lun 23 nov', False), ('J3', 'Mar 24 nov', False)]
tabs = "".join(f'<button class="tab-btn{" active" if a else " is-pending"}" type="button" role="tab" data-tab="{j.lower()}" aria-selected="{str(a).lower()}"><span class="tab-label">{j}</span><span class="tab-date">{d}</span></button>' for j, d, a in TABS)
panels = panel_j1 + pending('J2', 'lundi 23 novembre') + pending('J3', 'mardi 24 novembre')

page = open(f'{D}/template.html', encoding='utf-8').read().replace('{{TABS}}', tabs).replace('{{PANELS}}', panels)
open(OUT, 'w', encoding='utf-8').write(page)
print('peak', peak, clock(peak_sec), 'duration', duration, 'RDV', RDV, 'uniq', UNIQ, 'canceled', len(canceled), 'rebooked', rebooked,
      'msgs', msgs_total, 'prospects', len(prospects), 'clustered', clustered, 'slots', dict(slots), 'sit', dict(sit))
