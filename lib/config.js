// startDate : début des pubs. endDate : fin de l'acquisition (J1 du challenge), ou null pour « jusqu'à aujourd'hui ». Format AAAA-MM-JJ.
export default {
  name: 'Challenge Crypto',
  startDate: '2026-11-11',
  endDate: null,

  // Sources du Sheet (colonne « source »), dans l'ordre d'affichage. key = nom dans le Sheet, aliases = autres noms possibles (casse et accents ignorés).
  // Optionnel : target (objectif d'inscrits) → « % de l'objectif ».
  sources: [
    { key: 'Meta', label: 'Meta', target: 3300, color: '#056cf2', meta: true },
    { key: 'Google Ads', label: 'Google Ads', target: 400, color: '#dc2626', aliases: ['Google', 'GAds', 'Adwords', 'YouTube Ads'] },
    { key: 'Liste Saturnin', label: 'Liste Saturnin', target: 2500, color: '#0d9488', aliases: ['Liste Crypto'] },
    { key: 'Liste Capital', label: 'Liste Capital', target: 500, color: '#d97706', aliases: ['Liste Interne Capital'] },
    { key: 'Ataraxia', label: 'Ataraxia', target: 500, color: '#7c3aed' },
  ],

  // A/B test de la page d'inscription (PostHog, projet « Optin LFP »).
  posthog: {
    projectId: '313940',
    host: 'sommet.saturnindevins.com',
    since: '2026-11-10T23:00:00Z', // 11/11 à minuit (Paris) : exclut le trafic de test
    test: { label: 'A3 vs B', audience: 'trafic Meta', variants: ['A3', 'B'] }, // 1re version = référence
    pages: [ // pages dédiées, suivies sans comparaison
      { variant: 'C', audience: 'Liste Saturnin' },
      { variant: 'D', audience: 'Ataraxia + Liste Capital' },
    ],
  },
};
