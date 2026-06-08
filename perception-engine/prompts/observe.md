Extract a signal_map from the corpus below. Return a JSON object with EXACTLY these keys:

{
  "product_name": "exact product or service name as stated in documents",
  "sector": "industry sector (e.g. 'Enterprise SaaS', 'Luxury Fragrance', 'FinTech')",
  "product_core": "one sentence: what the product does and for whom",
  "signals": [
    {"id": "S1", "observation": "under 25 words, specific and concrete", "tag": "INTERNAL"}
  ],
  "metrics": [
    {"num": "47%", "label": "what this number represents"}
  ],
  "tensions": ["tension or contradiction observed in the corpus"],
  "catalysts": ["market force or event creating urgency"],
  "strategic_intent": "one sentence: what the organisation is trying to achieve"
}

Rules:
- Extract only from the corpus — never invent
- signals: 5–10 items, each tagged INTERNAL
- metrics: include every number mentioned in the corpus
- tensions: contradictions between stated goals and market reality
- catalysts: external forces creating a window of opportunity
- product_name must be the exact name found in documents (not a description)

Corpus:
{corpus}
