Produce a research plan from the signal map below. You MUST return a JSON object with this exact structure — no other keys at the top level:

{
  "questions": [
    {
      "id": "Q1",
      "dimension": "market",
      "question": "Full research question?",
      "queries": ["short web query 1", "short web query 2"]
    }
  ]
}

Rules:
- Cover all six dimensions: market, technology, narrative, regulatory, adoption, validation
- Generate 2-3 questions per dimension (12-18 questions total)
- Each question must trace to a specific signal, tension, or catalyst from the signal map
- queries: 2-4 per question, 2-6 words each, generic market terms only — never include the product name or any internal/proprietary detail
- dimension must be exactly one of: market, technology, narrative, regulatory, adoption, validation

Signal map:
{signal_map}
