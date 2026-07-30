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
- `GOOGLE_CLIENT_ID` — required for sign-in. See below.
- `SESSION_SECRET` — required for sign-in. Any long random string; it signs the
  session cookie. Rotating it signs everyone out.
- `AUTH_DEV_BYPASS` — local development escape hatch. `1` skips sign-in
  entirely. Never set this on the deployment.

## Sign-in

Creadir is gated to **@hightouch.io** Google accounts. Everything under `/api`
returns 401 without a valid session, and the browser shows a sign-in screen
before any of the app renders.

How it works: the browser gets a Google ID token, `POST /api/auth` verifies it
against Google's tokeninfo endpoint (so no crypto libraries are needed), then
checks the audience, the issuer, the verified-email flag, and that the address
ends in `@hightouch.io`. On success the server sets an HMAC-signed,
HttpOnly, Secure, SameSite=Lax cookie good for 30 days.

It fails closed: if `GOOGLE_CLIENT_ID` or `SESSION_SECRET` is missing, every
endpoint returns 503 rather than letting anyone in.

**One-time Google setup** (needed before anyone can sign in):

1. Go to <https://console.cloud.google.com/apis/credentials>.
2. **Create credentials → OAuth client ID → Web application.**
3. Under **Authorized JavaScript origins** add `https://creadir.vercel.app`
   (and `http://localhost:8787` if you want to sign in locally too).
4. Copy the client ID (it ends in `.apps.googleusercontent.com`) and set it as
   `GOOGLE_CLIENT_ID` in the Vercel project's environment variables, then
   redeploy. Add it to local `.env` as well for local sign-in.

No client secret is needed — this is the browser-side ID-token flow.

## Who has signed in

Every sign-in appends a private record to Vercel Blob under `logins/`. Nothing
on the website exposes it. To read it:

```
python3 users.py            # one line per person
python3 users.py --events   # every individual sign-in
```

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
