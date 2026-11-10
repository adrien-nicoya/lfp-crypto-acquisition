# Dashboard acquisition — LFP Crypto

- Inscrits par source et par jour : Google Sheet « LFP Crypto - Challenge » (colonnes `source` et `date inscription`), via un script Apps Script qui ne renvoie que des comptages.
- Meta : dépense, CPL Meta et CPL réel (dépense ÷ inscrits « Meta » du Sheet), par jour.
- A/B test : PostHog (projet Optin LFP, sommet.saturnindevins.com), A3 vs B pour Meta, pages C et D suivies à part.

## Mise en route
1. Sheet → Extensions → Apps Script : coller `apps-script/Code.gs`, remplacer `TOKEN`, puis Déployer → Nouveau déploiement → Application web (exécuter en tant que moi, accès : tout le monde). Copier l'URL `/exec`.
2. Vercel → variables d'environnement : voir `.env.example`, puis redéployer.

## Réglages
`lib/config.js` : nom, dates, sources du Sheet (+ objectifs `target` optionnels), versions du test PostHog.
Une source du Sheet absente de la liste est comptée en « Autre » avec un avertissement. Les doublons d'email sont comptés une fois.

Si le dashboard affiche « Aucune conversion … », mettre l'événement Meta listé dans `META_LEAD_ACTION`.
Logo chargé depuis decouvrir.cryptos-exponentielles.com (repli texte s'il est indisponible).
