// startDate : début des pubs. endDate : fin de l'acquisition (J1 du challenge), ou null pour « jusqu'à aujourd'hui ». Format AAAA-MM-JJ.
export default {
  name: 'Challenge Crypto',
  startDate: '2026-11-10', // TEST : remettre '2026-11-11'
  endDate: null,

  // Sources du Sheet (colonne « source »), dans l'ordre d'affichage. key = nom dans le Sheet, aliases = autres noms possibles (casse et accents ignorés).
  // Optionnel : target (objectif d'inscrits) → « % de l'objectif ».
  sources: [
    { key: 'Meta', label: 'Meta', color: '#056cf2', meta: true },
    { key: 'Liste Saturnin', label: 'Liste Saturnin', color: '#0d9488', aliases: ['Liste Crypto'] },
    { key: 'Liste Capital', label: 'Liste Capital', color: '#d97706', aliases: ['Liste Interne Capital'] },
    { key: 'Ataraxia', label: 'Ataraxia', color: '#7c3aed' },
  ],

  // A/B test de la page d'inscription (PostHog, projet « Optin LFP »).
  posthog: {
    projectId: '313940',
    host: 'sommet.saturnindevins.com',
    since: '2026-11-09T23:00:00Z', // TEST : remettre '2026-11-10T23:00:00Z' // 11/11 à minuit (Paris) : exclut le trafic de test
    test: { label: 'A3 vs B', audience: 'trafic Meta', variants: ['A3', 'B'] }, // 1re version = référence
    pages: [ // pages dédiées, suivies sans comparaison
      { variant: 'C', audience: 'Liste Saturnin' },
      { variant: 'D', audience: 'Ataraxia + Liste Capital' },
    ],
  },
};
