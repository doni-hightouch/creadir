# Creative Director

Drop in an ad and get a creative director's breakdown of why it works — or type a
concept and get a generated layout, then the same breakdown. Every insight comes as a
pair: a plain-English explanation plus a prompt-ready fragment you can copy into
Hightouch Ad Studio. Tap fragments into the tray and they compose into one tight prompt.

## Run it

```bash
python3 server.py
```

Then open http://127.0.0.1:8787. Pure-stdlib Python — no installs.

## Keys

Copy `.env.example` to `.env` and fill in:

- `OPENAI_API_KEY` — required. Runs the vision analysis and gpt-image-1 generation.
- `ANTHROPIC_API_KEY` — optional. When present, the critic (analysis + prompt
  compiling) switches to Claude automatically.
- `BFL_API_KEY`, `IDEOGRAM_API_KEY` — placeholders for the multi-model router
  (Flux for photorealism, Ideogram for type-led work). Not wired up yet.

## How it thinks

The analyzer and compiler share a distilled "creative director brain" synthesized from
nine research documents in [knowledge/](knowledge/) — photography craft, advertising
craft, digital/social craft, headline copywriting, the print canon (VW Think Small →
Apple Think Different), the modern canon (Old Spice → Liquid Death), design-masters
commentary, award-judge language, and practitioner teardowns. The distillation lives
in [knowledge/BRAIN.md](knowledge/BRAIN.md); the operative version is embedded in the
system prompts in [server.py](server.py).

Six dimensions, always: focal hierarchy, layout, negative space, color story,
typography, concept. Every breakdown names the canon move it echoes when there is one,
and ends with one "thing to sharpen."

## Architecture

- `server.py` — stdlib HTTP server. Endpoints: `POST /api/analyze` (image → findings),
  `POST /api/compile` (fragments → one prompt + routing), `POST /api/generate`
  (prompt/fragments → compiled prompt → gpt-image-1 → image), `GET /api/status`.
- `public/` — vanilla HTML/CSS/JS. Entry screen with one dual-purpose input; stage
  view with the ad framed left (top on mobile) and findings right; prompt tray fixed
  at the bottom.
- Providers are pluggable functions; the model registry only offers models whose keys
  exist in `.env`.
