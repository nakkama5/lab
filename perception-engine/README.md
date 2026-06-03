# Perception Engine

Internal brand-intelligence tool. Pipeline: **Ingest → OBSERVE → DERIVE → RESEARCH → SYNTHESIZE → DISTILL**

- **Input**: internal product docs (`.pptx`, `.pdf`, `.docx`, `.txt`, `.md`)
- **Output**: brand dossier (Markdown) + branded deck (`.pptx`)

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY
```

## Run

```bash
streamlit run app.py
```

Open the browser at the URL shown (usually http://localhost:8501).

## Fonts

The deck renderer uses **Georgia** (display) and **Calibri** (body) by default. These are
system fonts available on most Windows and macOS machines. On Linux you may need to install
`fonts-liberation` or edit `config/brand_tokens.json` to use fonts that are available.

## Requirements

- `ANTHROPIC_API_KEY` is required for all pipeline stages.
- `GAMMA_API_KEY` is optional; if set, an "Export to Gamma" button appears after DISTILL.
- Web search in the RESEARCH stage uses the Anthropic `web_search` tool — no separate key needed.

## Customisation

- **Prompts**: edit files in `prompts/` or use the Prompt Studio tab. Defaults are in `prompts/defaults/`.
- **Brand tokens**: edit `config/brand_tokens.json` or use the Brand Studio tab.
- **Deck layout**: edit `config/deck_layout.json` or use the Deck Studio tab.
- All edits are versioned; history stored in `prompts/.history/` and `config/.history/`.
- Run artifacts are saved to `runs/<ISO-timestamp>/`.
