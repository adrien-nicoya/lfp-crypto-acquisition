"""Construit la section « Analyse du chat » d'un jour J2+ (cards.json lu par build_day.py).
Usage : python3 chat_cards.py <dossier jour>  (lit comments.txt, clusters.json et cards_def.json)"""
import json, html, sys, os
D = sys.argv[1]
NB = ' '
esc = lambda s: html.escape(s, quote=True)
n = lambda x: f"{x:,}".replace(',', NB)
cfg = json.load(open(os.path.join(D, 'cards_def.json'), encoding='utf-8'))
cl = json.load(open(os.path.join(D, 'clusters.json'), encoding='utf-8'))
rows = [l.split('\t') for l in open(os.path.join(D, 'comments.txt'), encoding='utf-8').read().split('@end', 1)[1].strip().split('\n')]
mods = set(cfg['mods'])
prospects = [r for r in rows if r[1] not in mods]
def card(c):
    m = cl[c['key']]
    return (f'<div class="chat-card"><div class="chat-card-head"><div class="chat-card-title">{c["ico"]} {esc(c["title"])}</div>'
            f'<div class="chat-card-count">{len(m)}{NB}msgs · {len({x[1] for x in m})}{NB}pers.</div></div>'
            f'<div class="chat-card-desc">{esc(c["desc"])}</div><ul class="chat-card-samples">'
            + "".join(f'<li>« {esc(s)} »</li>' for s in c['samples']) +
            f'</ul><div class="chat-reco">🎯 {esc(c["reco"])}</div></div>')
shown = cfg['main'] + cfg['extra']
clustered = len({tuple(x) for c in shown for x in cl[c['key']]})
lede = cfg['lede'].format(total=n(len(rows)), prospects=n(len(prospects)), authors=n(len({r[1] for r in prospects})), clustered=n(clustered))
out = (f'<div class="section"><h2>💬 Analyse du chat</h2><p class="lede">{esc(lede)}</p>'
       f'<div class="chat-grid">{"".join(card(c) for c in cfg["main"])}</div><h3>Autres signaux</h3>'
       f'<div class="chat-grid">{"".join(card(c) for c in cfg["extra"])}</div></div>')
open(os.path.join(D, 'cards.json'), 'w', encoding='utf-8').write(out)
print('messages', len(rows), 'prospects', len(prospects), 'clustered', clustered)
