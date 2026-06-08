Sur la base des recherches ci-dessous, remplis la matrice de qualification prospect pondérée sur 100 points.

MATRICE DE SCORING :

A. Solidité Financière (score 1–5, pondération ×4 = max 20 pts)
  1 = Aucun fonds visible, projet amateur, pas de business réel
  2 = Fonds propres limités, crowdfunding modeste ou non abouti
  3 = Crowdfunding réussi ou fonds propres corrects et traçables
  4 = Business Angels identifiés ou revenus visibles et récurrents
  5 = VC/BA clairement identifiés avec montants, ou serial entrepreneur à succès avéré

B. Potentiel Marketing & Influence (score 1–5, ×4 = max 20 pts)
  1 = <1 000 abonnés, visuels amateurs, fondateurs invisibles en ligne
  2 = Présence naissante, esthétique incohérente, engagement faible
  3 = Belle image de marque, communauté 5–10k, engagement correct
  4 = 10–50k abonnés engagés, couverture presse beauté
  5 = Hype confirmée, fondateurs influenceurs, >50k abonnés fortement engagés

C. Crédibilité de l'Équipe (score 1–5, ×3 = max 15 pts)
  1 = Aucune expérience business ni parfumerie/cosmétique identifiable
  2 = Expérience dans un domaine connexe mais pas cosmétique/parfumerie
  3 = Profils marketing ou business forts, novices en parfumerie
  4 = Expérience en cosmétique ou entrepreneur ayant réussi une exit
  5 = Anciens de l'industrie parfumerie ou entrepreneurs ayant revendu une boîte

D. Cohérence du Projet Produit (score 1–5, ×3 = max 15 pts)
  1 = Concept flou ou prix de vente trop bas (<50€ parfum) pour absorber les coûts R&D
  2 = Concept présent mais positionnement ambigu
  3 = Concept clair, positionnement niche cohérent
  4 = Concept solide avec storytelling distinctif et prix premium
  5 = Concept disruptif, storytelling puissant, prix premium validé par le marché

E. Réalisme des Attentes (score 1–5, ×2 = max 10 pts)
  1 = Signaux forts d'irréalisme (veut tout vite, budget nul, aucune mention de contraintes)
  2 = Peu d'indices de maturité industrielle (défaut si aucune info disponible)
  3 = Compréhension partielle des délais et contraintes
  4 = Bonne compréhension du process, questions techniques visibles
  5 = Connaissance explicite des coûts industriels, MOQs et délais de la parfumerie
  ⚠️ Si aucune donnée disponible en ligne : attribuer 2 (bénéfice du doute minimal) et noter "donnée non disponible en ligne"

F. Réseau de Distribution (score 1–5, ×2 = max 10 pts)
  1 = Uniquement site web non lancé ou aucune présence distributeur
  2 = Site web actif mais faible traction, aucun retailer
  3 = Site web actif + quelques pop-up stores ou revendeurs locaux
  4 = Présence retail régionale établie + e-commerce actif
  5 = Présence chez distributeurs clés (Sephora, Nose, Dover Street Market, Printemps…)

BONUS Personal Branding (+10 pts max) :
  +10 si le fondateur est une célébrité ou influenceur >100k assurant des ventes dès le lancement

SEUILS DE DÉCISION :
  < 40 pts → No-Go (refus ou offre standard sans R&D)
  40–70 pts → À creuser (rendez-vous de qualification nécessaire)
  > 70 pts → Go (fort potentiel, engager les ressources)

─── DONNÉES DE RECHERCHE ───
{research_data}

─── NOTES TERRAIN DE L'ANALYSTE ───
{analyst_notes}

Retourne UNIQUEMENT un objet JSON valide :
{
  "scores": {
    "A": {"score": 3, "weighted": 12, "justification": "...", "confidence": "found|partial|not_found"},
    "B": {"score": 3, "weighted": 12, "justification": "...", "confidence": "found|partial|not_found"},
    "C": {"score": 3, "weighted": 9,  "justification": "...", "confidence": "found|partial|not_found"},
    "D": {"score": 3, "weighted": 9,  "justification": "...", "confidence": "found|partial|not_found"},
    "E": {"score": 2, "weighted": 4,  "justification": "...", "confidence": "found|partial|not_found"},
    "F": {"score": 3, "weighted": 6,  "justification": "...", "confidence": "found|partial|not_found"}
  },
  "bonus": {"applicable": false, "points": 0, "justification": "..."},
  "total": 52,
  "verdict": "No-Go|À creuser|Go",
  "verdict_color": "red|orange|green",
  "green_flags": ["...", "...", "..."],
  "red_flags": ["...", "...", "..."],
  "executive_summary": "3–4 phrases. Score X/100 — verdict. Raison principale. Action recommandée.",
  "next_action": "Action concrète recommandée pour l'équipe commerciale."
}
