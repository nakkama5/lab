MISSION : Réalise une due diligence complète sur le prospect "{prospect_name}" pour qualifier son potentiel en tant que client d'un fournisseur de fragrances/ingrédients.

{analyst_notes_block}

Lance des recherches web ciblées sur chacun des 7 axes ci-dessous. Pour chaque axe, indique explicitement : données trouvées / partiellement trouvées / non disponibles en ligne.

─── AXE 1 · IDENTITÉ & STRUCTURE ───
- Site web officiel (UX/UI, positionnement prix, gamme)
- Date de création, pays, siège social
- Modèle de vente : DTC, Retail, Hybride
- Fourchette de prix (le prix de vente est-il cohérent pour absorber un développement fragrance sur mesure ?)

─── AXE 2 · SOLIDITÉ FINANCIÈRE ───
- Type de financement : bootstrapping, Business Angels, VC, crowdfunding (Ulule, Kickstarter, etc.)
- Levées de fonds récentes — montant, investisseurs nommés
- Mentions dans la presse économique (Maddyness, Les Échos, TechCrunch, etc.)
- Signaux de croissance : recrutements LinkedIn, nouvelles ouvertures, partenariats annoncés
- Données Pappers/Societe.com/Companies House si disponibles

─── AXE 3 · POTENTIEL MARKETING & INFLUENCE ───
- Instagram : compte officiel, nombre d'abonnés, fréquence de publication, taux d'engagement estimé
- TikTok : présence, abonnés, viralité
- Les fondateurs se mettent-ils en scène ? (personal branding, compte perso suivi)
- Esthétique de la marque : cohérente, instagrammable, premium ?
- Mentions presse beauté / parfumerie (Vogue, Grazia, Nez Magazine, etc.)

─── AXE 4 · CRÉDIBILITÉ DE L'ÉQUIPE ───
- Noms et parcours des fondateurs (LinkedIn)
- Expérience antérieure en cosmétique, parfumerie ou business en général
- Primo-entrepreneurs ou vétérans ? Ont-ils déjà revendu une entreprise ?
- Taille et qualité du réseau professionnel

─── AXE 5 · COHÉRENCE DU PROJET PRODUIT ───
- Concept de la marque : clair, distinctif, différenciant ?
- Positionnement niche : crédible et cohérent ?
- Prix de vente : suffisamment premium pour justifier un développement sur mesure (typiquement >80€ pour un parfum) ?
- Storytelling : y a-t-il une vraie histoire de marque communicable ?

─── AXE 6 · RÉALISME & MATURITÉ INDUSTRIELLE ───
- Mentions explicites de MOQ, délais de développement, processus de fabrication ?
- Indices de compréhension des réalités industrielles de la parfumerie
- Comportement en ligne : demandes de devis visibles, questions techniques, etc.
- Si aucune information disponible : le dire clairement — ne pas extrapoler

─── AXE 7 · RÉSEAU DE DISTRIBUTION ───
- Retailers actuels ou partenariats annoncés (Sephora, Nose, Dover Street Market, Colette, Printemps, Harvey Nichols, etc.)
- Site e-commerce actif ? Volume estimé ?
- Pop-up stores, marchés, événements ?
- Distribution internationale ?

─── SYNTHÈSE ───
- 3 Drapeaux Verts (signaux positifs les plus forts)
- 3 Drapeaux Rouges (risques ou signaux d'alarme)

Retourne UNIQUEMENT un objet JSON valide avec cette structure exacte :
{
  "prospect_name": "...",
  "identity": {
    "website": "...", "founded": "...", "country": "...",
    "sales_model": "DTC|Retail|Hybride|inconnu",
    "price_range": "...", "summary": "..."
  },
  "financial": {
    "funding_type": "...", "investors": "...", "amounts": "...",
    "press_mentions": "...", "growth_signals": "...",
    "summary": "...", "confidence": "found|partial|not_found"
  },
  "marketing": {
    "instagram": "...", "tiktok": "...", "engagement": "...",
    "personal_branding": "...", "aesthetics": "...", "press": "...",
    "summary": "...", "confidence": "found|partial|not_found"
  },
  "team": {
    "founders": "...", "experience_level": "primo|experienced|veteran",
    "industry_background": "...", "network": "...",
    "summary": "...", "confidence": "found|partial|not_found"
  },
  "product": {
    "concept": "...", "positioning": "...", "price_coherence": "ok|low|unknown",
    "storytelling": "...", "summary": "...", "confidence": "found|partial|not_found"
  },
  "realism": {
    "moq_awareness": "...", "timeline_awareness": "...",
    "industry_maturity": "...",
    "summary": "...", "confidence": "found|partial|not_found"
  },
  "distribution": {
    "key_retailers": [], "ecommerce_active": true,
    "international": "...", "summary": "...", "confidence": "found|partial|not_found"
  },
  "green_flags": ["...", "...", "..."],
  "red_flags": ["...", "...", "..."],
  "sources_used": ["url1", "url2"]
}
