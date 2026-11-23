# Dashboard acquisition — LFP Crypto

- Inscrits par source et par jour : Google Sheet « LFP Crypto - Challenge » (colonnes `source` et `date inscription`), via un script Apps Script qui ne renvoie que des comptages.
- Meta : dépense, CPL Meta et CPL réel (dépense ÷ inscrits « Meta » du Sheet), par jour.
- A/B test : PostHog (projet Optin LFP, sommet.saturnindevins.com), B vs B2 vs B3 vs B4 pour Meta (historique : A1 vs B vs E, A1 vs B, A2 vs B, A3 vs B), pages C (Liste Saturnin), Capital et Ataraxia suivies à part.

## Mise en route
1. Sheet → Extensions → Apps Script : coller `apps-script/Code.gs`, remplacer `TOKEN`, puis Déployer → Nouveau déploiement → Application web (exécuter en tant que moi, accès : tout le monde). Copier l'URL `/exec`.
2. Vercel → variables d'environnement : voir `.env.example`, puis redéployer.

## Réglages
`lib/config.js` : nom, dates, sources du Sheet (+ objectifs `target` optionnels), versions du test PostHog.
Une source du Sheet absente de la liste est comptée en « Autre » avec un avertissement. Les doublons d'email sont comptés une fois.

Si le dashboard affiche « Aucune conversion … », mettre l'événement Meta listé dans `META_LEAD_ACTION`.
Logo chargé depuis decouvrir.cryptos-exponentielles.com (repli texte s'il est indisponible).

Pages : `/` accueil · `/acquisition/` dashboard acquisition · `/live/` analyse des lives.

## Analyse des lives (`/live/`)
Page statique générée par `tools/live-report/` (un onglet par soirée). Déposer dans ce dossier l'export YouTube
(`liveViewership_*.csv`), l'export Calendly (`event-data-*.csv`) et les commentaires (`comments.txt`), puis :
`python3 clusters.py && python3 build.py ../../live/index.html` (J1). Jours suivants : un dossier par jour avec un `day.json`
(jour, date, heure de début, inscrits, valeurs J1), puis `python3 build_day.py ../../live/index.html <dossier jour> <dossier J1>`.
Les données brutes ne sont pas versionnées.
