// startDate : début des pubs. endDate : fin de l'acquisition (J1 du challenge), ou null pour « jusqu'à aujourd'hui ». Format AAAA-MM-JJ.
export default {
  name: 'Challenge Crypto',
  startDate: '2026-11-11',
  endDate: null,

  // Sources du Sheet (colonne « source »), dans l'ordre d'affichage. key = nom dans le Sheet, aliases = autres noms possibles (casse et accents ignorés).
  // Optionnels : target (objectif d'inscrits) → « % de l'objectif » ; byDay: true → détail des inscrits jour par jour sous la carte.
  sources: [
    { key: 'Meta', label: 'Meta', target: 3300, color: '#056cf2', meta: true },
    { key: 'Google Ads', label: 'Google Ads', target: 400, color: '#dc2626', aliases: ['Google', 'GAds', 'Adwords', 'YouTube Ads'] },
    { key: 'Liste Saturnin', label: 'Liste Saturnin', target: 2500, byDay: true, color: '#0d9488', aliases: ['Liste Crypto'] },
    { key: 'Liste Capital', label: 'Liste Capital', target: 500, byDay: true, color: '#d97706', aliases: ['Liste Interne Capital'] },
    { key: 'Ataraxia', label: 'Ataraxia', target: 500, byDay: true, color: '#7c3aed' },
  ],

  // A/B test de la page d'inscription (PostHog, projet « Optin LFP »).
  posthog: {
    projectId: '313940',
    host: 'sommet.saturnindevins.com',
    since: '2026-11-10T23:00:00Z', // 11/11 à minuit (Paris) : exclut le trafic de test
    // Test en cours (1re version = référence). since : début du test.
    test: { label: 'A1 vs B vs E', audience: 'trafic Meta', variants: ['A1', 'B', 'E'], since: '2026-11-13T10:01:00Z' }, // 13/11 11h01 (Paris)
    // Tests terminés, affichés en historique (du plus récent au plus ancien). until : fin du test.
    history: [
      { label: 'A1 vs B', audience: 'trafic Meta', variants: ['A1', 'B'], since: '2026-11-12T09:21:00Z', until: '2026-11-13T10:01:00Z' },
      { label: 'A2 vs B', audience: 'trafic Meta', variants: ['A2', 'B'], since: '2026-11-11T17:35:00Z', until: '2026-11-12T09:21:00Z' },
      { label: 'A3 vs B', audience: 'trafic Meta', variants: ['A3', 'B'], since: '2026-11-10T23:00:00Z', until: '2026-11-11T17:35:00Z' },
    ],
    pages: [ // pages dédiées, suivies sans comparaison (variant = valeur PostHog, label = nom affiché, optionnel)
      { variant: 'C', label: 'Liste Saturnin', audience: 'Liste Saturnin (/nl)' },
      { variant: 'Capital', audience: 'Liste Capital (/independance-capital)' },
      { variant: 'Ataraxia', audience: 'Ataraxia (/ataraxia)' },
    ],
  },
};
