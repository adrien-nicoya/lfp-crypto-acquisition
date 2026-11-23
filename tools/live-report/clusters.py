import re,json,collections
rows=[l.split('\t') for l in open('comments.txt',encoding='utf-8').read().split('@end',1)[1].strip().split('\n')]
mods={'@TeamModération1','@SaturninDevinsLive'}
def sec(t):
    neg=t.startswith('-'); h,m,s=map(int,t.lstrip('-').split(':')); v=h*3600+m*60+s; return -v if neg else v
P=[(sec(r[0]),r[1],r[2].strip()) for r in rows if r[1] not in mods]
C={
 'plateforme':[r"\b(plate.?forme|platform)",r"\b(kraken|swissborg|swiss borg|binance|coinbase|okx|bitpanda|deskoin|bitvavo|revolut|degiro)\b",r"\bpea\b.{0,40}(crypto|plate|kraken|comment|fonctionne|investir)"],
 'prix':[r"\bcombien.{0,25}(co[uû]te|prix|tarif|int[ée]grer|acc[eè]s|pour avoir)",r"\b(minimum|montant|somme|capital)\b.{0,40}(investi|commencer|d[ée]buter|rentrer|faut|requis|suffisant)",r"\b(prix|tarif|co[uû]t)\b.{0,25}(programme|service|formation|abonnement)",r"payer.{0,15}programme",r"\b(50|60|20|10) ?000 ?(euros?|€)",r"\bminimum\b",r"quelle somme",r"combien pour"],
 'fiscal':[r"\b(imp[oô]ts?|fiscal|taxe[sr]?|tax[ée]e?s?|flat ?tax|plus.?value|d[ée]clar)"],
 'securite':[r"\b(hack|pirat|vol[ée]|ledger|cl[ée] (crypto|ledger)|quantique|s[ée]curit|cold wallet|faille)"],
 'pertes':[r"\b(perdu|perte|pertes|moins \d+ ?%|-\d+ ?%|\d+ ?% en moins|r[ée]cup[ée]rer (mes|toute|mon)|ramass)"],
 'offres':[r"club priv[ée]|patrimoine souverain|leman finance|crypto ia\b|abonn[ée]?e? (a|à) vie|m[eê]me programme|en remplacement|en parall[eè]le|abonnement"],
 'mail':[r"\b(mail|e-mail|email|confirmation)\b",r"\b(dossier|calculateur|cadeau|outil)\b.{0,40}(o[uù]|comment|re[çc]u|avoir|r[ée]cup|t[ée]l[ée]charg|pas)",r"(o[uù]|comment).{0,30}(dossier|calculateur)"],
 'lighter':[r"\b(lighter|ligther|\blit\b)"],
 'duree':[r"\breplay\b",r"\b(longue?|tard)\b",r"vous quitter",r"\b(trop )?long(ue)?\b.{0,30}(soir|demain|leve|pour)|\bfinir plus t[oô]t|plus court|quelle heure|jusqu.{0,3}(à|a) quelle heure|combien de temps (dure|ça dur)|dure combien",r"\bblabla|aller [àa] l.essentiel|rien appris|r[ée]p[ée]t"],
 'son':[r"\b(son|micro|volume|entend)\b.{0,40}(faible|arthur|mal|monter|pas|trop)|arthur.{0,40}(son|micro|entend)"],
 'peur':[r"\b(inquiet|inqui[eè]te|euro num[ée]rique|contr[oô]le|guerre|dette|planche [àa] billets|faillite|banques?.{0,20}(bloqu|contr[oô]l))"],
}
res={}
for k,pats in C.items():
    rx=[re.compile(p,re.I) for p in pats]
    m=[p for p in P if len(p[2])>=12 and any(r.search(p[2]) for r in rx)]
    res[k]=m
    secs=[x[0] for x in m]
    q=collections.Counter((s//900)*15 for s in secs if s>=0)
    print(f"{k:11s} msgs={len(m):4d} pers={len({x[1] for x in m}):4d} top15min={q.most_common(3)}")
json.dump({k:[[s,a,t] for s,a,t in v] for k,v in res.items()},open('clusters.json','w'),ensure_ascii=False)
print('total clusterised',len({(s,a,t) for v in res.values() for s,a,t in v}),'prospects',len(P),'authors',len({p[1] for p in P}))
