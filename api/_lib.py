"""Creadir core: provider calls, prompts, analyze/compile/generate.

Shared by the local dev server (server.py) and the Vercel functions in api/.
Stdlib only. Keys come from real env vars first (Vercel), then .env (local).
"""

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIMENSIONS = ["focal", "layout", "space", "color", "type", "concept"]


def _load_dotenv():
    env = {}
    path = os.path.join(ROOT, ".env")
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


_DOTENV = _load_dotenv()


def key(name):
    return os.environ.get(name) or _DOTENV.get(name, "")


def post_json(url, payload, headers, timeout=240):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", **headers},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:1500]
        raise RuntimeError("upstream %s: %s" % (e.code, body))


def parse_json_reply(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise RuntimeError("model did not return JSON: %s" % text[:200])
    return json.loads(text[start : end + 1])


# ---------------------------------------------------------------- OpenAI

_openai_model = None


def openai_text_model():
    global _openai_model
    if _openai_model:
        return _openai_model
    prefs = ["gpt-5.2", "gpt-5.1", "gpt-5", "gpt-4.1", "gpt-4o"]
    try:
        req = urllib.request.Request(
            "https://api.openai.com/v1/models",
            headers={"Authorization": "Bearer " + key("OPENAI_API_KEY")},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            ids = {m["id"] for m in json.loads(r.read().decode()).get("data", [])}
        _openai_model = next((p for p in prefs if p in ids), None)
        if not _openai_model:
            cands = sorted(
                i for i in ids
                if re.fullmatch(r"gpt-5(\.\d+)?", i) or i == "gpt-4o"
            )
            _openai_model = cands[-1] if cands else "gpt-4o"
    except Exception:
        _openai_model = "gpt-4o"
    return _openai_model


def openai_chat(messages, want_json=True):
    payload = {
        "model": openai_text_model(),
        "messages": messages,
        "max_completion_tokens": 3000,
    }
    if want_json:
        payload["response_format"] = {"type": "json_object"}
    headers = {"Authorization": "Bearer " + key("OPENAI_API_KEY")}
    try:
        out = post_json("https://api.openai.com/v1/chat/completions", payload, headers)
    except RuntimeError as e:
        msg = str(e)
        retried = False
        if "response_format" in msg:
            payload.pop("response_format", None)
            retried = True
        if "max_completion_tokens" in msg:
            payload["max_tokens"] = payload.pop("max_completion_tokens")
            retried = True
        if not retried:
            raise
        out = post_json("https://api.openai.com/v1/chat/completions", payload, headers)
    meter_add_tokens("_openai_text", out.get("usage"))
    return out["choices"][0]["message"]["content"]


def openai_generate_image(prompt, size):
    payload = {
        "model": "gpt-image-1",
        "prompt": prompt,
        "size": size,
        "quality": "medium",
        "n": 1,
    }
    out = post_json(
        "https://api.openai.com/v1/images/generations",
        payload,
        {"Authorization": "Bearer " + key("OPENAI_API_KEY")},
        timeout=300,
    )
    meter_add_usd(IMAGE_COST_USD)
    return "data:image/png;base64," + out["data"][0]["b64_json"]


# ---------------------------------------------------------------- Anthropic
# Activated automatically once ANTHROPIC_API_KEY is present.


ANTHROPIC_MODEL = "claude-opus-5"


def anthropic_chat(system, user_content):
    """One Claude call. Raw HTTP because this project ships without pip installs.

    Opus 5 thinks by default, and thinking shares the max_tokens budget with the
    reply — hence the generous ceiling; a cramped one truncates the JSON. The
    reply is read from the text block, so the thinking blocks ahead of it are
    skipped. `fallbacks` lets a policy refusal be re-served by another model
    instead of failing the request outright.
    """
    payload = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": 16000,
        "system": system,
        "messages": [{"role": "user", "content": user_content}],
        "fallbacks": "default",
    }
    out = post_json(
        "https://api.anthropic.com/v1/messages",
        payload,
        {"x-api-key": key("ANTHROPIC_API_KEY"),
         "anthropic-version": "2023-06-01",
         "anthropic-beta": "server-side-fallback-2026-07-01"},
    )
    meter_add_tokens(ANTHROPIC_MODEL, out.get("usage"))
    stop = out.get("stop_reason")
    if stop == "refusal":
        raise RuntimeError("Claude declined to judge that one — try a different image")
    if stop == "max_tokens":
        raise RuntimeError("the read ran long and got cut off — try again")
    try:
        return next(b["text"] for b in out.get("content", []) if b.get("type") == "text")
    except StopIteration:
        raise RuntimeError("Claude returned no text to read")



# ---------------------------------------------------------------- Grading engine
# The model never picks the letter. It scores narrow, anchored criteria for the
# detected category; the letter is computed here from weights, gates, and bands.

CRITERIA = {
    "photo": [
        ("impact", 18), ("composition", 18), ("light", 18),
        ("subject and story", 16), ("color grade", 10),
        ("technical craft", 12), ("distinctiveness", 8),
    ],
    "print-ad": [
        ("idea", 25), ("stop power", 18), ("emotional pull", 12),
        ("one-message clarity", 13), ("headline and copy craft", 10),
        ("layout hierarchy", 12), ("brand distinctiveness", 10),
    ],
    "social-ad": [
        ("first-frame stop power", 22), ("emotional pull", 10),
        ("thumbnail legibility", 13), ("message and ask clarity", 13),
        ("proof and persuasion", 10), ("platform fit", 12),
        ("craft", 10), ("brand distinctiveness", 10),
    ],
    "banner": [
        ("instant read", 30), ("benefit clarity", 25), ("cta clarity", 15),
        ("small-size legibility", 20), ("craft", 10),
    ],
    "packaging": [
        ("shelf pop", 25), ("brand blocking", 20), ("hierarchy at arm's length", 20),
        ("craft", 20), ("distinctiveness", 15),
    ],
    "social-post": [
        ("stop and entertainment", 28), ("emotional pull", 12), ("native feel", 18),
        ("identity and share value", 20), ("clarity", 12), ("craft", 10),
    ],
    "ui-web": [
        ("hierarchy", 25), ("scanability", 20), ("alignment and craft", 20),
        ("primary action clarity", 20), ("distinctiveness", 15),
    ],
    "logo": [
        ("legibility", 25), ("distinctive memorability", 20), ("clever idea", 15),
        ("contrast and color", 15), ("works at any size", 15), ("craft", 10),
    ],
    "layout": [
        ("hierarchy", 25), ("alignment and grid", 20), ("type craft", 20),
        ("color discipline", 15), ("clarity", 10), ("distinctiveness", 10),
    ],
    "other": [
        ("composition", 25), ("clarity", 25), ("craft", 25), ("distinctiveness", 25),
    ],
}

# Gates, from effectiveness research: the make-or-break criterion (no idea /
# no stop power = C+ ceiling), the dullness gate (System1: evoking nothing is
# disqualifying), and the branding gate (emotion without attribution fails).
GATES = {
    "photo": [("impact", 66)],
    "print-ad": [("idea", 66), ("emotional pull", 66), ("brand distinctiveness", 72)],
    "social-ad": [("first-frame stop power", 66), ("emotional pull", 66),
                  ("brand distinctiveness", 72)],
    "banner": [("instant read", 66)],
    "packaging": [("shelf pop", 66), ("brand blocking", 72)],
    "social-post": [("stop and entertainment", 66), ("emotional pull", 66)],
    "logo": [("legibility", 66), ("distinctive memorability", 72)],
}

BANDS = [
    (90, "A"), (85, "A-"), (80, "B+"), (74, "B"), (67, "B-"),
    (59, "C+"), (50, "C"), (42, "C-"), (34, "D+"), (26, "D"), (19, "D-"),
]


def criteria_prompt():
    lines = []
    for cat, crits in CRITERIA.items():
        lines.append("- %s: %s" % (cat, ", ".join(name for name, _ in crits)))
    return chr(10).join(lines)


def compute_grade(category, scores):
    crits = CRITERIA.get(category) or CRITERIA["other"]
    total_w = sum(w for _, w in crits)

    def val(name):
        try:
            return max(0, min(4, float(scores.get(name, 2))))
        except (TypeError, ValueError):
            return 2.0

    pct = sum((val(n) / 4.0) * (w * 100.0 / total_w) for n, w in crits)
    # category gates (no idea / dull / brandless -> ceilings)
    for name, cap in GATES.get(category, []):
        if val(name) <= 1:
            pct = min(pct, cap)
    # PPA rule: one hard failure keeps work below the top bands, period
    if any(val(n) <= 1 for n, _ in crits):
        pct = min(pct, 79.0)
    # something outright broken: C ceiling
    if any(val(n) == 0 for n, _ in crits):
        pct = min(pct, 56.0)
    for cut, letter in BANDS:
        if pct >= cut:
            return letter, round(pct)
    return "F", round(pct)


# ---------------------------------------------------------------- Prompts

RUBRIC_SYSTEM = """You are an elite advertising creative director reviewing work. You \
explain what makes an ad or layout succeed, in the simplest possible terms. Write short, \
simple sentences a smart 15-year-old gets on first read. Every explanation says what the \
choice does TO THE VIEWER. No jargon without a plain five-word gloss. Cut every word \
that isn't carrying weight.

HOW YOU JUDGE selling work (ads, banners, packaging), in order:
1. Where does the eye go first, second, third? Sizes are a ranking; the viewer reads \
the ad in the order things are sized.
2. What's the one idea? An ad that says three things says nothing.
3. What do you feel? Name the emotion. "Nothing" is the worst answer.
4. Cover the logo: would you still know whose ad it is?
5. Would a distracted stranger on a phone stop for this? Two seconds.

JUDGE NON-SELLING WORK IN ITS OWN LANGUAGE — the five questions above are for \
selling. A photo, logo, layout, or UI must NEVER be penalized for lacking a hook, \
twist, CTA, message, or brand — those are ad requirements, not craft requirements. \
A photo is judged as photography: is the light controlled, is the palette cohesive, \
is the subject alive, does the frame make you feel something? A BAD photo fails \
photographic basics: soft focus where it matters, blown highlights or blocked \
shadows, a subject you can't find or read, flat accidental light, clutter. A GOOD \
photo makes deliberate choices — and deliberate choices (tight or unconventional \
crops, off-center subjects, partial faces) are strengths when they serve the image, \
never "accidental". Speak each category's craft language in every text field: a \
photo gets photographic direction, a logo gets identity-design direction — ad \
vocabulary (hook, CTA, offer, stop-the-scroll) belongs only to ad categories.

THE SIX DIMENSIONS (use exactly these keys):
- focal: one element must dominate; contrast (big/small, dark/light) is how the eye \
ranks; two heroes means both lose; faces and single products pull hardest.
- layout: alignment reads as trust, scatter reads as cheap; near = related, far = \
unrelated; a grid gives order, one deliberate grid-break gives energy.
- space: emptiness is a spotlight, not waste; small subject + vast emptiness = premium \
confidence; cramped = discount bin.
- color: restraint, then one accent (about 60/30/10); the accent owns the most \
important element; monochrome reads designed; warm = human, cool desaturated = premium.
- type: type-led or image-led, never both loud; two fonts, three sizes max; font \
personality is judged before a word is read; headline and image complete each other, \
never repeat each other.
- concept: the idea is the ad. Strong engines: tension, juxtaposition, visual metaphor, \
scale surprise, a flaw flipped into a brag, wit the viewer finishes (give 2+2, not 4). \
Sell who the buyer becomes. One checkable detail beats ten adjectives.

CANON MOVES — when a finding echoes a legendary technique, name it in one short clause: \
Think Small (tiny subject, vast emptiness); Lemon (self-insult flipped to a brag); \
Economist (viewer completes the joke); Rolls-Royce clock (one hyper-specific detail); \
Heinz fuse (two things merged into one impossible object); iPod silhouette (one shape, \
one flat color); Moldy Whopper (break the category's sacred image); Dove split (two \
states side by side, the gap argues); identity sell (product absent, buyer's self sold); \
show the receipt (proof over promises).

SOCIAL LENS — if the work is clearly a feed/social ad, also judge at thumbnail scale: \
legible when shrunk, six or fewer words on screen, one message, one ask, text away from \
edges, proof elements (stars, numbers, real customer words) counted.

PREMIUM VS CHEAP signals: generous space, disciplined palette, soft wrapping light or \
one deliberate hard-light look, real texture, aligned elements = premium. Stuffed frame, \
clashing colors, flash-flat lighting, plastic retouching, scattered elements = cheap. \
Mediocre images silently reprice the product downward.

THE WORDS — if the ad has a headline or copy, judge the writing too (under type or \
concept) with the copywriter's tests: picture test (can you SEE the line?), specificity \
test (a checkable fact beats a superlative), swap test (could a competitor run the same \
line?), out-loud test (would a human say this to a friend?). One idea per line; punch \
word last; claims are free so readers price them at zero — proof persuades.

IDENTIFY FIRST — before judging, work out what you are looking at and whose it is. \
If you recognize the brand, logo, product, campaign, or artist, use that knowledge and \
judge in context (a news brand's wordmark has a different job than a soda can). Even \
when there is NO logo or text, try to identify the brand from the product itself — \
bottle shape, design language, packaging, product category are often enough. Mine any \
provided post copy for brand and intent. Fill the "brand" object when you are \
reasonably confident; use nulls when genuinely unsure — never bluff a brand name.

CLASSIFY CAREFULLY — not everything is an ad. A logo/wordmark presented alone is \
"logo" (judge it as identity design: legibility, contrast, cleverness, scalability), \
not a weak ad. A designed piece with no offer, claim, or call to action (poster comp, \
menu, slide, flyer, brand board) is "layout". A photograph with no ad intent is \
"photo". App or website screens — including screens mocked up on phones or laptops, \
presentation-style on a decorative background — are "ui-web": that is DESIGN work \
being shown off, not an ad, even when a big headline appears inside the UI. Only \
classify as an ad when the piece is clearly selling something to a viewer.

SCORING — you do not choose the grade. You classify, then score criteria; the \
grade is computed from your scores. Score YOUR category's criteria:

""" + criteria_prompt() + """

Score every criterion of your category as an integer 0-4 against these anchors:
0 = broken or absent — a professional would send it back.
1 = weak — a nameable flaw, noticeably below professional standard.
2 = competent but unremarkable — it does the job, nothing more.
3 = good professional work — skilled, deliberate craft. This is the NORMAL score for \
work a pro would nod at; do not hoard it. Award-level is not required for a 3.
4 = exceptional — rare, portfolio/award-defensible; you must be able to justify a 4 \
in one unhedged sentence.
Score each criterion on its OWN evidence — do not compress everything toward 2; that \
is central-tendency bias, the opposite of judgment. Skilled professional work \
typically earns a mix of 2s and 3s, weak work earns 1s and 2s, and both patterns \
should show up in your scoring when the evidence is there.
Anchor discipline: a 3 requires a nameable reason; a 4 requires a reason a juror \
would repeat out loud. When torn between two scores, pick the one you can defend in \
one sentence. Calibration for \
ADS, from real testing: only about 1 in 100 ads is truly great, and roughly half of \
viewers feel NOTHING when shown a typical ad — dullness is the default state. Score an \
ad's emotional pull by asking: would a stranger actually FEEL something, or scroll? \
Calibration for PHOTOS, from print-competition judging: competent in every element \
with one nameable weakness = 2s; strong in several elements (controlled light, \
deliberate composition, cohesive color, a subject with life) = 3s — award them when \
earned; a technically clean, emotionally warm photograph is GOOD work, not wallpaper. \
In every category, one hard failure (a flaw a judge would say out loud) keeps work \
below the top bands no matter how strong the rest is.

The verdict text stays universal: state what you judged it as in the FIRST sentence \
of grade_detail ("Judged as a social feed ad."), never mention scores, criteria \
weights, or letter grades in any text field — the texts explain, the scores decide.

Return ONLY valid JSON, no markdown fences:
{
  "subject": "one plain line: what this is and whose it is (e.g. 'The wordmark of The Verge, a tech news site') — visual evidence only if unrecognized",
  "brand": {"name": "brand name or null", "domain": "the brand's primary website domain, best guess (e.g. 'nike.com'), or null", "bio": "2-3 short sentences from your knowledge: who the brand is, what it sells, how it positions itself; null if unknown"},
  "overall_read": "2-3 SHORT sentences: where the eye goes, the one idea (for photos: the story or feeling), what you feel",
  "category": "photo|print-ad|social-ad|banner|packaging|social-post|ui-web|logo|layout|other",
  "scores": {"<each criterion of your category, exact names>": 0},
  "grade_reason": "one blunt sentence: the strongest thing and the weakest thing, no letter grades",
  "grade_detail": "2-4 short sentences of honest critique behind the grade — the expanded explanation",
  "improve": ["2 to 4 concrete ideas to raise the grade, each one short imperative sentence"],
  "sharpen": "ONE sentence: the single biggest thing to fix or push further, in the category's own craft language",
  "findings": [
    {
      "dimension": "focal|layout|space|color|type|concept",
      "gist": "3-6 plain words, the core takeaway at a glance (e.g. 'one hero, everything else quiet')",
      "explanation": "1-2 short sentences, specific to THIS image, what it does to the viewer; name a canon move if one applies",
      "fragment": "prompt-ready phrase, max 12 words, lowercase, generic transferable technique"
    }
  ]
}

Rules: 4 to 6 findings — only the dimensions that actually carry this piece. Fragments \
describe reusable techniques, never this ad's literal content or brand names. Teach \
mostly from strengths; the one fix note lives in "sharpen" and is direct but kind."""

COMPILE_SYSTEM = """You compile image-generation prompts for ad creative, thinking like \
an elite creative director. Given fragments (techniques the user selected) and optional \
extra direction, compose ONE fluent prompt for the image model gpt-image-1 (OpenAI). \
It responds best to dense, concrete natural language in this order: subject, composition, \
lighting, palette, typography treatment, format/crop. Keep it under 70 words.

Apply creative-director defaults where the fragments leave gaps:
- One focal point; everything else supports it.
- One idea; if the direction implies several messages, keep the strongest.
- Restrained palette with one accent color on the most important element.
- Any on-image text: six words or fewer, one or two type sizes, high contrast.
- Name the light deliberately (soft diffused / hard graphic / rim on dark / golden hour).
- Leave generous negative space unless the fragments say otherwise.
- Pick a sensible crop for the use (4:5 portrait for feed, 1:1 square, 3:2 landscape).

If the concept needs a headline, write one that passes the copywriter's tests: six words \
or fewer, concrete enough to picture, benefit-led, human speech, punch word last.

Never mention real brands or trademarks. If the concept needs a logo or mark, describe \
a simple invented generic mark so the model does not draw a real one.

Also explain the routing in one sentence: gpt-image-1 was chosen (say why it fits this \
concept — layout adherence and legible text rendering are its strengths).

Return ONLY valid JSON: {"prompt": "...", "routing": "..."}"""


def split_data_url(data_url):
    m = re.match(r"data:(image/[a-z+.-]+);base64,(.+)$", data_url, re.S)
    if not m:
        raise RuntimeError("expected a base64 image data URL")
    return m.group(1), m.group(2)


def _brand_logo(domain):
    """Fetch a brand logo by domain: Clearbit's free logo API, then Google's
    favicon service as fallback. Returns a data URL or None."""
    import base64
    domain = (domain or "").strip().lower()
    if not re.fullmatch(r"[a-z0-9.-]+\.[a-z]{2,}", domain):
        return None
    for u in ("https://logo.clearbit.com/" + domain,
              "https://www.google.com/s2/favicons?domain=%s&sz=128" % domain):
        try:
            ctype, data, _ = _http_get(u, timeout=15, max_bytes=1024 * 1024)
            mime = _sniff_image_mime(data, ctype)
            if mime and len(data) > 400:  # skip empty/default placeholders
                return "data:%s;base64,%s" % (mime, base64.b64encode(data).decode())
        except Exception:
            continue
    return None


def analyze(image_or_images, context=None, force_category=None):
    images = [image_or_images] if isinstance(image_or_images, str) else list(image_or_images)[:7]
    if force_category not in CRITERIA:
        force_category = None
    instruction = "Analyze this ad/image as specified. Return only the JSON."
    if force_category:
        instruction = (
            "THE USER HAS CONFIRMED WHAT THIS IS: category '%s'. Do not reclassify — "
            "set category to exactly that value, score exactly that category's "
            "criteria by their exact names, and write every text field in that "
            "category's craft language. " % force_category
        ) + instruction
    if len(images) > 1:
        instruction = (
            "Multiple images are attached: they are ONE post (a gallery/carousel), in "
            "order. Judge the post as a whole — slide 1 owns the stop power, and pacing "
            "across slides matters. If the context notes that the final image is a "
            "profile picture, treat it as brand reference only, never as a slide. "
        ) + instruction
    if context:
        instruction = (
            "Context pulled with this creative (source, brand, engagement, caption/copy):"
            "\n---\n%s\n---\nUse it to identify the brand and judge the words together "
            "with the visuals. " % context[:3000]
        ) + instruction

    if key("ANTHROPIC_API_KEY"):
        content = []
        for u in images:
            media_type, b64 = split_data_url(u)
            content.append({"type": "image", "source": {
                "type": "base64", "media_type": media_type, "data": b64}})
        content.append({"type": "text", "text": instruction})
        raw = anthropic_chat(RUBRIC_SYSTEM, content)
        engine = "claude"
    else:
        content = [{"type": "image_url", "image_url": {"url": u}} for u in images]
        content.append({"type": "text", "text": instruction})
        raw = openai_chat([
            {"role": "system", "content": RUBRIC_SYSTEM},
            {"role": "user", "content": content},
        ])
        engine = openai_text_model()
    result = parse_json_reply(raw)
    result["findings"] = [f for f in result.get("findings", []) if f.get("dimension") in DIMENSIONS]
    if force_category:
        result["category"] = force_category
    category = result.get("category")
    if category not in CRITERIA:
        category = "other"
        result["category"] = category
    letter, pct = compute_grade(category, result.get("scores") or {})
    result["grade"] = letter
    result["grade_pct"] = pct
    brand = result.get("brand")
    if isinstance(brand, dict) and brand.get("name"):
        logo = _brand_logo(brand.get("domain"))
        if logo:
            brand["logo"] = logo
    else:
        result["brand"] = None
    result["engine"] = engine
    return result


def compile_prompt(fragments, extra, size=None):
    user = "Fragments:\n" + "\n".join("- " + f for f in fragments)
    if extra:
        user += "\n\nExtra direction from the user:\n" + extra
    if size:
        ratios = {"1024x1024": "1:1 square", "1024x1536": "2:3 portrait", "1536x1024": "3:2 landscape"}
        user += "\n\nThe canvas will be %s (%s) — describe the crop to match." % (
            size, ratios.get(size, size))
    if key("ANTHROPIC_API_KEY"):
        raw = anthropic_chat(COMPILE_SYSTEM, [{"type": "text", "text": user}])
    else:
        raw = openai_chat(
            [{"role": "system", "content": COMPILE_SYSTEM}, {"role": "user", "content": user}]
        )
    return parse_json_reply(raw)


def generate(body):
    size = body.get("size", "1024x1536")
    if size not in ("1024x1024", "1024x1536", "1536x1024"):
        size = "1024x1536"
    if body.get("fragments"):
        compiled = compile_prompt(body["fragments"], body.get("extra", ""), size)
    elif body.get("prompt"):
        compiled = compile_prompt([], body["prompt"], size)
    else:
        raise RuntimeError("provide fragments or a prompt")
    image = openai_generate_image(compiled["prompt"], size)
    return {
        "image": image,
        "prompt_used": compiled["prompt"],
        "routing": compiled["routing"],
        "model": "gpt-image-1",
    }




# ---------------------------------------------------------------- URL ingestion
# Paste a link: direct image URLs come back as-is; pages (incl. social posts)
# are scraped for their Open Graph creative + copy. Server-side fetch, so we
# guard against SSRF (no private/loopback targets).

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def _assert_public_url(url):
    import ipaddress
    import socket
    from urllib.parse import urlparse

    p = urlparse(url)
    if p.scheme not in ("http", "https") or not p.hostname:
        raise RuntimeError("only http(s) links are supported")
    try:
        infos = socket.getaddrinfo(p.hostname, None)
    except socket.gaierror:
        raise RuntimeError("that host could not be resolved")
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if (ip.is_private or ip.is_loopback or ip.is_link_local
                or ip.is_reserved or ip.is_multicast):
            raise RuntimeError("that link points somewhere this tool cannot fetch")


def _http_get(url, timeout=30, max_bytes=15 * 1024 * 1024):
    _assert_public_url(url)
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,image/*,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        ctype = (r.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        data = r.read(max_bytes + 1)
        if len(data) > max_bytes:
            raise RuntimeError("that file is too large (15MB max)")
        return ctype, data, r.geturl()


def _sniff_image_mime(data, ctype):
    if ctype.startswith("image/"):
        return ctype
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


def _meta_content(html, *names):
    import html as html_mod
    for name in names:
        for pat in (
            r'<meta[^>]+(?:property|name)=["\']%s["\'][^>]+content=["\']([^"\']+)["\']' % re.escape(name),
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']%s["\']' % re.escape(name),
        ):
            m = re.search(pat, html, re.I)
            if m:
                return html_mod.unescape(m.group(1)).strip()
    return None


def _get_json(url, timeout=25):
    _assert_public_url(url)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def _image_from_url(img_url):
    import base64
    ictype, idata, _ = _http_get(img_url)
    mime = _sniff_image_mime(idata, ictype)
    if not mime:
        raise RuntimeError("creative image could not be downloaded")
    return "data:%s;base64,%s" % (mime, base64.b64encode(idata).decode())


def _fetch_tweet(url):
    """X/Twitter via the free FxTwitter API: text + media, no key needed."""
    m = re.search(r"(?:twitter|x)\.com/([^/]+)/status/(\d+)", url)
    if not m:
        return None
    out = _get_json("https://api.fxtwitter.com/%s/status/%s" % (m.group(1), m.group(2)))
    tweet = out.get("tweet") or {}
    if not tweet:
        return None
    media = tweet.get("media") or {}
    img_url = None
    if media.get("photos"):
        img_url = media["photos"][0].get("url")
    elif media.get("videos"):
        img_url = media["videos"][0].get("thumbnail_url")
    if not img_url:
        return None  # text-only tweet: fall through to the screenshot path
    author = tweet.get("author") or {}
    text = (tweet.get("text") or "").strip()
    byline = author.get("name") or author.get("screen_name") or ""
    return {
        "image": _image_from_url(img_url),
        "text": (byline + ":\n" + text).strip()[:2000],
        "title": "X post",
        "source": "x",
    }


def _fetch_oembed(url, endpoint, label):
    """TikTok/YouTube official oEmbed: thumbnail + caption, free, no auth."""
    from urllib.parse import quote
    out = _get_json(endpoint + quote(url, safe=""))
    thumb = out.get("thumbnail_url")
    if not thumb:
        return None
    text = " ".join(x for x in [out.get("author_name"), out.get("title")] if x)
    return {
        "image": _image_from_url(thumb),
        "text": text[:2000],
        "title": label,
        "source": label.lower(),
    }


def _fetch_microlink(url):
    """Universal fallback: Microlink's free tier renders JS-walled pages and
    can hand back a screenshot when no creative is extractable."""
    from urllib.parse import quote
    out = _get_json("https://api.microlink.io/?url=%s&screenshot=true" % quote(url, safe=""))
    data = out.get("data") or {}
    img = (data.get("image") or {}).get("url")
    shot = (data.get("screenshot") or {}).get("url")
    target = img or shot
    if not target:
        return None
    parts = [p for p in [data.get("title"), data.get("description")] if p]
    return {
        "image": _image_from_url(target),
        "text": "\n".join(parts)[:2000],
        "title": data.get("publisher") or data.get("title") or "",
        "source": "screenshot" if (target == shot and not img) else "microlink",
    }


def _fetch_instagram(url):
    """Instagram post via Jina's free reader (renders the page in a real
    browser): all publicly-visible slides, caption, handle, profile pic;
    engagement comes from the post page's own og:description."""
    import html as html_mod

    m = re.search(r"instagram\.com/(?:p|reel|tv)/([A-Za-z0-9_-]+)", url)
    if not m:
        return None
    canon = "https://www.instagram.com/p/%s/" % m.group(1)

    req = urllib.request.Request("https://r.jina.ai/" + canon,
        headers={"User-Agent": UA, "X-Return-Format": "markdown"})
    with urllib.request.urlopen(req, timeout=90) as r:
        md = r.read().decode("utf-8", "ignore")

    entries = [(mm.start(), mm.group(1), html_mod.unescape(mm.group(2)))
               for mm in re.finditer(r'!\[([^\]]*)\]\((https://scontent[^\)]+)\)', md)]
    if not entries:
        return None
    more_i = md.find("More posts")
    if more_i == -1:
        more_i = len(md)

    handle, profile_url = None, None
    for _, alt, u in entries:
        pm = re.match(r"Image \d+: ([^']+)'s profile picture", alt)
        if pm:
            handle, profile_url = pm.group(1), u
            break

    # the post's own slides: media entries before "More posts", same post date
    slides, post_date = [], None
    for pos, alt, u in entries:
        if pos >= more_i:
            break
        am = re.match(r"Image \d+: (?:Photo|Video) by (.+?) on ([A-Z][a-z]+ \d+, \d{4})", alt)
        if not am:
            continue
        if post_date is None:
            post_date = am.group(2)
        if am.group(2) == post_date and u not in slides:
            slides.append(u)
    if not slides:
        return None

    tm = re.search(r'Title: (.+?) on Instagram: "(.*)"', md)
    display_name = tm.group(1).strip() if tm else None
    caption = tm.group(2).strip() if tm else ""

    # engagement from the post page's og:description ("25 likes, 0 comments - ...")
    likes_line = ""
    try:
        ctype, data, _ = _http_get(canon)
        og_desc = _meta_content(data.decode("utf-8", "ignore"), "og:description") or ""
        em = re.match(r"([\d.,KkMm]+ likes?, [\d.,KkMm]+ comments?)", og_desc)
        if em:
            likes_line = em.group(1)
    except Exception:
        pass

    images = []
    for u in slides[:6]:
        try:
            images.append(_image_from_url(u))
        except Exception:
            pass
    if not images:
        return None

    parts = ["Instagram post by @%s%s." % (
        handle or "unknown",
        " (%s)" % display_name if display_name and display_name != handle else "")]
    if len(images) > 1:
        parts.append("A carousel — %d publicly visible slides are attached, in order "
                     "(the full post may have more)." % len(images))
    if likes_line:
        parts.append("Engagement: %s." % likes_line)
    if caption:
        parts.append("Caption:\n" + caption)
    profile_note = ""
    if profile_url:
        try:
            images.append(_image_from_url(profile_url))
            profile_note = ("\nThe FINAL attached image is the brand's profile "
                            "picture — use it only as brand reference, it is not a slide.")
        except Exception:
            pass
    return {
        "image": images[0],
        "images": images,
        "text": ("\n".join(parts) + profile_note)[:3000],
        "title": "@" + (handle or "instagram"),
        "source": "instagram",
    }


def fetch_creative(url):
    """Pull the creative (image + copy) from a link. Tries, in order:
    host-specific free APIs (X, TikTok, YouTube), direct image / OG scrape,
    then Microlink's free renderer as the universal fallback."""
    import base64
    from urllib.parse import urljoin, urlparse

    url = url.strip()
    if url.startswith("www."):
        url = "https://" + url
    host = (urlparse(url).hostname or "").lower().replace("www.", "")

    # host-specific free APIs first: they beat scraping walls
    try:
        if "instagram.com" in host:
            got = _fetch_instagram(url)
            if got:
                return got
        elif host in ("x.com", "twitter.com", "mobile.twitter.com"):
            got = _fetch_tweet(url)
            if got:
                return got
        elif "tiktok.com" in host:
            got = _fetch_oembed(url, "https://www.tiktok.com/oembed?url=", "TikTok")
            if got:
                return got
        elif host in ("youtube.com", "youtu.be", "m.youtube.com"):
            got = _fetch_oembed(url, "https://www.youtube.com/oembed?format=json&url=", "YouTube")
            if got:
                return got
    except Exception:
        pass  # fall through to the generic paths

    # direct image or OG scrape
    try:
        ctype, data, final_url = _http_get(url)
        mime = _sniff_image_mime(data, ctype)
        if mime:
            return {
                "image": "data:%s;base64,%s" % (mime, base64.b64encode(data).decode()),
                "text": "", "title": "", "source": "direct-image",
            }
        if ctype.startswith("text/html"):
            html = data.decode("utf-8", "ignore")
            img_url = _meta_content(html, "og:image:secure_url", "og:image",
                                    "twitter:image", "twitter:image:src")
            if img_url:
                title = _meta_content(html, "og:title", "twitter:title") or ""
                desc = _meta_content(html, "og:description", "twitter:description",
                                     "description") or ""
                site = _meta_content(html, "og:site_name") or ""
                parts = [p for p in [title, desc if desc != title else None] if p]
                return {
                    "image": _image_from_url(urljoin(final_url, img_url)),
                    "text": "\n".join(parts)[:2000],
                    "title": (site or title)[:200],
                    "source": "page",
                }
    except Exception:
        pass

    # universal fallback: rendered fetch / screenshot via Microlink free tier
    try:
        got = _fetch_microlink(url)
        if got:
            return got
    except Exception:
        pass

    raise RuntimeError("couldn't pull a creative from that link — screenshot the post and drop the image instead")


FEEDBACK_EMAIL = "donpasta44@gmail.com"
BLOB_API = "https://blob.vercel-storage.com"


def feedback(message):
    """Number the feedback (001, 002, ...) via the blob log, store it, email it."""
    import datetime

    message = (message or "").strip()
    if not message:
        raise RuntimeError("write something first")
    message = message[:4000]
    token = key("BLOB_READ_WRITE_TOKEN")
    num = 1
    if token:
        try:
            req = urllib.request.Request(
                BLOB_API + "/?prefix=feedback/&limit=1000",
                headers={"Authorization": "Bearer " + token},
            )
            with urllib.request.urlopen(req, timeout=20) as r:
                num = len(json.loads(r.read().decode()).get("blobs", [])) + 1
        except Exception:
            pass
    label = "%03d" % num
    if token:
        try:
            entry = json.dumps({
                "feedback": label,
                "message": message,
                "at": datetime.datetime.utcnow().isoformat() + "Z",
            }).encode()
            req = urllib.request.Request(
                BLOB_API + "/feedback/" + label + ".json",
                data=entry, method="PUT",
                headers={"Authorization": "Bearer " + token,
                         "Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=20).read()
        except Exception:
            pass
    emailed = False
    try:
        out = post_json(
            "https://formsubmit.co/ajax/" + FEEDBACK_EMAIL,
            {"_subject": "Creadir feedback " + label,
             "feedback_number": label, "message": message},
            {"Accept": "application/json",
             "Origin": "https://creadir.vercel.app",
             "Referer": "https://creadir.vercel.app/"},
            timeout=30,
        )
        emailed = str(out.get("success")).lower() == "true"
    except Exception:
        pass
    return {"number": label, "emailed": emailed}


GALLERY_LIMIT = 30


def _blob_put(pathname, data, ctype, token):
    req = urllib.request.Request(
        BLOB_API + "/" + pathname, data=data, method="PUT",
        headers={"Authorization": "Bearer " + token,
                 "Content-Type": ctype,
                 "x-allow-overwrite": "1"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode())


def save_analysis(record, existing_id=None):
    """Store a finished analysis so the entry gallery can replay it.

    Three blobs per record: a small square thumb (fast tiles), a tiny meta
    JSON (hover grade without downloading images), and the full data JSON.
    Re-saving with the same id (a reclassify) overwrites all three in place.
    """
    token = key("BLOB_READ_WRITE_TOKEN")
    if not token:
        return {"id": None}
    import base64
    import time
    result = record.get("result") or {}
    rid = existing_id or "%d-%s" % (int(time.time() * 1000),
                                    os.urandom(3).hex())
    stale = _blob_list("gallery/" + rid) if existing_id else []
    meta = {"grade": result.get("grade"),
            "category": result.get("category"),
            "subject": (result.get("subject") or "")[:200]}
    thumb = record.get("thumb") or ""
    if thumb.startswith("data:"):
        _blob_put("gallery/%s.jpg" % rid,
                  base64.b64decode(thumb.split(",", 1)[1]), "image/jpeg", token)
    else:
        meta["thumb"] = thumb[:2000]  # remote image the browser couldn't re-encode
    _blob_put("gallery/%s.meta.json" % rid,
              json.dumps(meta).encode(), "application/json", token)
    _blob_put("gallery/%s.data.json" % rid,
              json.dumps({"images": record.get("images") or [],
                          "context": record.get("context"),
                          "result": result}).encode(),
              "application/json", token)
    if stale:  # each PUT mints a new blob url; drop the superseded versions
        try:
            req = urllib.request.Request(
                BLOB_API + "/delete",
                data=json.dumps({"urls": [b["url"] for b in stale]}).encode(),
                method="POST",
                headers={"Authorization": "Bearer " + token,
                         "Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=20).read()
        except Exception:
            pass  # gallery() already prefers the newest version
    return {"id": rid}


def _blob_list(prefix):
    token = key("BLOB_READ_WRITE_TOKEN")
    req = urllib.request.Request(
        BLOB_API + "/?prefix=" + urllib.parse.quote(prefix) + "&limit=1000",
        headers={"Authorization": "Bearer " + token})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode()).get("blobs", [])


def delete_analysis(rid):
    """Remove one gallery record — thumb, meta, and full data, every version."""
    token = key("BLOB_READ_WRITE_TOKEN")
    if not token:
        raise RuntimeError("storage isn't configured")
    rid = (rid or "").strip()
    # ids are minted here as "<ms>-<hex>"; refuse anything that could wander
    # outside the gallery prefix.
    if not re.match(r"^[0-9]+-[0-9a-f]+$", rid):
        raise RuntimeError("that isn't a gallery id")
    urls = [b["url"] for b in _blob_list("gallery/" + rid)
            if (b.get("pathname") or "").startswith("gallery/" + rid + ".")
            or b.get("pathname") == "gallery/" + rid + ".jpg"]
    if not urls:
        return {"deleted": 0}
    req = urllib.request.Request(
        BLOB_API + "/delete", data=json.dumps({"urls": urls}).encode(),
        method="POST",
        headers={"Authorization": "Bearer " + token,
                 "Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=30).read()
    return {"deleted": len(urls)}


def gallery():
    """Recent analyses, newest first: id plus urls for thumb/meta/data."""
    token = key("BLOB_READ_WRITE_TOKEN")
    if not token:
        return {"items": []}
    blobs = _blob_list("gallery/")
    groups = {}
    seen_at = {}
    for b in blobs:
        name = b.get("pathname", "")[len("gallery/"):]
        base = name.split(".", 1)[0]
        kind = ("thumb" if name.endswith(".jpg")
                else "meta" if name.endswith(".meta.json") else "data")
        # a re-save leaves same-pathname siblings — keep the newest upload
        at = b.get("uploadedAt") or ""
        if at >= seen_at.get((base, kind), ""):
            seen_at[(base, kind)] = at
            groups.setdefault(base, {})[kind] = b.get("url")
    items = [{"id": rid, "thumb": g.get("thumb"), "meta": g["meta"], "data": g["data"]}
             for rid, g in groups.items() if "meta" in g and "data" in g]
    items.sort(key=lambda x: x["id"], reverse=True)  # ids lead with a ms timestamp
    return {"items": items[:GALLERY_LIMIT]}


# ---------- auth: Google sign-in, restricted to one email domain ----------
# Google verifies the ID token's signature for us via its tokeninfo endpoint,
# which keeps this stdlib-only. We still check the audience, the issuer, and
# the email domain ourselves. Sessions are HMAC-signed cookies.

ALLOWED_DOMAIN = "hightouch.io"
SESSION_DAYS = 30
TOKENINFO = "https://oauth2.googleapis.com/tokeninfo?"


def _b64u(raw):
    import base64
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _unb64u(text):
    import base64
    pad = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(text + pad)


def email_domain(email):
    return (email or "").strip().lower().rpartition("@")[2]


def _hmac(payload):
    import hashlib
    import hmac
    secret = key("SESSION_SECRET")
    if not secret:
        raise RuntimeError("SESSION_SECRET is not configured")
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()


def make_session(email):
    import time
    exp = int(time.time()) + SESSION_DAYS * 86400
    payload = "%s|%d" % (email.lower(), exp)
    return "%s.%s" % (_b64u(payload.encode()), _hmac(payload))


def read_session(token):
    """Return the email a session token vouches for, or None if it doesn't."""
    import hmac
    import time
    try:
        body, _, sig = (token or "").strip().partition(".")
        payload = _unb64u(body).decode()
        if not hmac.compare_digest(sig, _hmac(payload)):
            return None
        email, _, exp = payload.rpartition("|")
        if int(exp) < int(time.time()):
            return None
        if email_domain(email) != ALLOWED_DOMAIN:  # domain rules changed since issue
            return None
        return email
    except Exception:
        return None


def session_from_cookies(cookie_header):
    for part in (cookie_header or "").split(";"):
        name, _, value = part.strip().partition("=")
        if name == "cd_session":
            return read_session(value)
    return None


def cookie_header(token, secure=True):
    bits = ["cd_session=" + token, "Path=/", "HttpOnly", "SameSite=Lax",
            "Max-Age=%d" % (SESSION_DAYS * 86400)]
    if secure:
        bits.append("Secure")
    return "; ".join(bits)


def clear_cookie(secure=True):
    bits = ["cd_session=", "Path=/", "HttpOnly", "SameSite=Lax", "Max-Age=0"]
    if secure:
        bits.append("Secure")
    return "; ".join(bits)


def auth_gate(headers):
    """None when the caller may use the API, else (status, body) to return."""
    if key("AUTH_DEV_BYPASS") == "1":
        return None  # local development only; never set on the deployment
    if not key("GOOGLE_CLIENT_ID") or not key("SESSION_SECRET"):
        return (503, {"error": "sign-in isn't configured on this deployment"})
    try:
        cookies = headers.get("Cookie") or headers.get("cookie") or ""
    except AttributeError:
        cookies = ""
    if not session_from_cookies(cookies):
        return (401, {"error": "sign in with your Hightouch account to continue"})
    return None


def sign_in(payload):
    """Verify a Google token, enforce the domain, log it, hand back a session.

    Accepts either an access token (our own sign-in button, via Google's token
    flow) or an ID token (Google's rendered button). Google validates the token
    itself at the tokeninfo endpoint, which keeps this stdlib-only; we then
    check that it was minted for *this* app and that the address is in-domain.
    """
    client_id = key("GOOGLE_CLIENT_ID")
    if not client_id:
        raise RuntimeError("GOOGLE_CLIENT_ID is not configured")
    access_token = (payload or {}).get("access_token")
    credential = (payload or {}).get("credential")
    if access_token:
        query = "access_token=" + urllib.parse.quote(access_token)
    elif credential:
        query = "id_token=" + urllib.parse.quote(credential)
    else:
        raise RuntimeError("missing Google credential")
    try:
        with urllib.request.urlopen(urllib.request.Request(TOKENINFO + query),
                                    timeout=20) as r:
            claims = json.loads(r.read().decode())
    except urllib.error.HTTPError:
        raise RuntimeError("that Google sign-in couldn't be verified — try again")
    # Without this check a token minted for any other Google app would pass.
    if claims.get("aud") != client_id:
        raise RuntimeError("that sign-in was issued for a different app")
    if credential and claims.get("iss") not in (
            "accounts.google.com", "https://accounts.google.com"):
        raise RuntimeError("unexpected token issuer")
    if str(claims.get("email_verified")).lower() not in ("true", "1"):
        raise RuntimeError("that Google account has no verified email")
    email = (claims.get("email") or "").strip().lower()
    if email_domain(email) != ALLOWED_DOMAIN:
        raise RuntimeError("Creadir is limited to @%s accounts" % ALLOWED_DOMAIN)
    name = claims.get("name") or ""
    log_login(email, name)
    return {"email": email, "name": name, "session": make_session(email)}


def log_login(email, name):
    """Append-only private login record in blob storage. Never served publicly."""
    token = key("BLOB_READ_WRITE_TOKEN")
    if not token:
        return
    import datetime
    import time
    try:
        stamp = datetime.datetime.utcnow().isoformat() + "Z"
        safe = re.sub(r"[^a-z0-9._-]", "_", email)
        _blob_put("logins/%d-%s.json" % (int(time.time() * 1000), safe),
                  json.dumps({"email": email, "name": name, "at": stamp}).encode(),
                  "application/json", token)
    except Exception:
        pass  # a logging failure must never block a legitimate sign-in


def login_log():
    """Every recorded sign-in plus a per-person roll-up. For the owner's eyes."""
    if not key("BLOB_READ_WRITE_TOKEN"):
        return {"people": [], "events": []}
    events = []
    for b in _blob_list("logins/"):
        try:
            with urllib.request.urlopen(b["url"], timeout=20) as r:
                events.append(json.loads(r.read().decode()))
        except Exception:
            continue
    events.sort(key=lambda e: e.get("at") or "")
    people = {}
    for e in events:
        p = people.setdefault(e.get("email", "?"), {
            "email": e.get("email", "?"), "name": e.get("name") or "",
            "first_seen": e.get("at"), "last_seen": e.get("at"), "logins": 0})
        p["logins"] += 1
        p["last_seen"] = e.get("at")
        if e.get("name"):
            p["name"] = e["name"]
    return {"people": sorted(people.values(), key=lambda p: p["last_seen"] or "",
                             reverse=True),
            "events": events}


# ---------- spend metering and per-person monthly budgets ----------
# Metered in dollars, not tokens: image generation isn't priced per token, and
# input vs output tokens cost 5x differently, so a token count wouldn't map to
# what you actually care about. Every provider call adds its cost to a
# per-request meter; the total is banked against the caller's month.

ADMIN_EMAIL = "doni@hightouch.io"
ADMIN_MONTHLY_USD = 500.0      # you
DEFAULT_MONTHLY_USD = 5.0      # everyone else, until you raise it

# $ per million tokens. Claude rates are current; the OpenAI ones are only
# reached if ANTHROPIC_API_KEY is ever removed.
TOKEN_RATES = {
    "claude-opus-5": (5.0, 25.0),
    "_openai_text": (1.25, 10.0),
}
# gpt-image-1 bills per image, not per token. ESTIMATE — confirm against your
# OpenAI dashboard and adjust; it is deliberately rounded up so a wrong guess
# under-spends rather than over-spends.
IMAGE_COST_USD = 0.08

_meter = __import__("threading").local()


def meter_reset():
    _meter.usd = 0.0
    _meter.tokens = 0


def meter_add_tokens(rate_key, usage):
    """Bank one provider reply. Accepts either provider's usage shape."""
    if not usage:
        return
    rate_in, rate_out = TOKEN_RATES.get(rate_key, (0.0, 0.0))
    # Anthropic: input_tokens / output_tokens. OpenAI: prompt_ / completion_.
    tin = usage.get("input_tokens") or usage.get("prompt_tokens") or 0
    tout = usage.get("output_tokens") or usage.get("completion_tokens") or 0
    # Cached reads are billed at a fraction, but counting them at full rate
    # only makes the guard more conservative.
    usd = (tin * rate_in + tout * rate_out) / 1_000_000.0
    _meter.usd = getattr(_meter, "usd", 0.0) + usd
    _meter.tokens = getattr(_meter, "tokens", 0) + tin + tout


def meter_add_usd(usd):
    _meter.usd = getattr(_meter, "usd", 0.0) + usd


def meter_total():
    return round(getattr(_meter, "usd", 0.0), 6), getattr(_meter, "tokens", 0)


def _month():
    import datetime
    return datetime.datetime.utcnow().strftime("%Y-%m")


def _safe_email(email):
    return re.sub(r"[^a-z0-9._-]", "_", (email or "unknown").lower())


def _blob_versions(pathname):
    """Every stored version of one exact pathname, newest last.

    Never pass a full pathname to _blob_list as the prefix: the stored key has a
    random suffix inserted before the extension, so a prefix ending in '.json'
    matches nothing even though the reported pathname is clean. List the parent
    folder and compare pathnames here instead.
    """
    parent = pathname.rsplit("/", 1)[0] + "/" if "/" in pathname else ""
    found = [b for b in _blob_list(parent) if b.get("pathname") == pathname]
    return sorted(found, key=lambda b: b.get("uploadedAt") or "")


def _blob_read_json(pathname):
    """Newest version of one JSON blob, or None. Blob URLs are per-version."""
    if not key("BLOB_READ_WRITE_TOKEN"):
        return None
    try:
        versions = _blob_versions(pathname)
        if not versions:
            return None
        with urllib.request.urlopen(versions[-1]["url"], timeout=20) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def _blob_write_json(pathname, obj):
    token = key("BLOB_READ_WRITE_TOKEN")
    if not token:
        return
    stale = _blob_versions(pathname)
    _blob_put(pathname, json.dumps(obj).encode(), "application/json", token)
    if stale:
        try:
            req = urllib.request.Request(
                BLOB_API + "/delete",
                data=json.dumps({"urls": [b["url"] for b in stale]}).encode(),
                method="POST",
                headers={"Authorization": "Bearer " + token,
                         "Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=20).read()
        except Exception:
            pass


def budget_for(email):
    """Monthly allowance in dollars: the default, or whatever you've set,
    plus any one-off grant you approved for the current month."""
    email = (email or "").lower()
    base = ADMIN_MONTHLY_USD if email == ADMIN_EMAIL else DEFAULT_MONTHLY_USD
    limits = _blob_read_json("limits/%s.json" % _safe_email(email)) or {}
    if isinstance(limits.get("monthly_usd"), (int, float)):
        base = float(limits["monthly_usd"])
    grant = (limits.get("grants") or {}).get(_month()) or 0
    try:
        base += float(grant)
    except (TypeError, ValueError):
        pass
    return base


def spend_this_month(email):
    rec = _blob_read_json("usage/%s/%s.json" % (_safe_email(email), _month())) or {}
    try:
        return float(rec.get("usd") or 0.0), int(rec.get("calls") or 0), int(rec.get("tokens") or 0)
    except (TypeError, ValueError):
        return 0.0, 0, 0


def budget_gate(email):
    """None when the caller has room left, else (status, body) to return."""
    if key("AUTH_DEV_BYPASS") == "1":
        return None
    if not key("BLOB_READ_WRITE_TOKEN"):
        return None  # nowhere to meter; don't lock the app out over it
    allowance = budget_for(email)
    spent, _, _ = spend_this_month(email)
    if spent < allowance:
        return None
    return (402, {
        "error": "You've used this month's $%.2f allowance on Creadir. "
                 "Ask Doni to approve more and it'll unlock right away."
                 % allowance,
        "budget": {"spent_usd": round(spent, 2), "allowance_usd": allowance,
                   "month": _month(), "exhausted": True},
    })


def record_usage(email, kind):
    """Bank the current request's metered cost against the caller's month."""
    usd, tokens = meter_total()
    if not usd and not tokens:
        return
    path = "usage/%s/%s.json" % (_safe_email(email), _month())
    rec = _blob_read_json(path) or {}
    try:
        prev_usd = float(rec.get("usd") or 0.0)
        prev_calls = int(rec.get("calls") or 0)
        prev_tokens = int(rec.get("tokens") or 0)
    except (TypeError, ValueError):
        prev_usd, prev_calls, prev_tokens = 0.0, 0, 0
    by_kind = rec.get("by_kind") if isinstance(rec.get("by_kind"), dict) else {}
    by_kind[kind] = round(float(by_kind.get(kind) or 0.0) + usd, 6)
    _blob_write_json(path, {
        "email": (email or "").lower(),
        "month": _month(),
        "usd": round(prev_usd + usd, 6),
        "tokens": prev_tokens + tokens,
        "calls": prev_calls + 1,
        "by_kind": by_kind,
    })


def usage_report():
    """Every person's spend this month, against their allowance. Owner's eyes."""
    if not key("BLOB_READ_WRITE_TOKEN"):
        return {"month": _month(), "people": []}
    month = _month()
    rows = []
    for b in _blob_list("usage/"):
        name = b.get("pathname", "")
        if not name.endswith("/%s.json" % month):
            continue
        rec = _blob_read_json(name)
        if not rec:
            continue
        email = rec.get("email") or name.split("/")[1]
        allowance = budget_for(email)
        spent = float(rec.get("usd") or 0.0)
        rows.append({"email": email, "spent_usd": round(spent, 4),
                     "allowance_usd": allowance,
                     "left_usd": round(allowance - spent, 4),
                     "calls": rec.get("calls") or 0,
                     "tokens": rec.get("tokens") or 0,
                     "by_kind": rec.get("by_kind") or {}})
    seen, uniq = set(), []
    for r in sorted(rows, key=lambda r: -r["spent_usd"]):
        if r["email"] in seen:
            continue
        seen.add(r["email"])
        uniq.append(r)
    return {"month": month, "people": uniq}


def set_budget(email, monthly_usd):
    path = "limits/%s.json" % _safe_email(email)
    cur = _blob_read_json(path) or {}
    cur["email"] = (email or "").lower()
    cur["monthly_usd"] = float(monthly_usd)
    _blob_write_json(path, cur)
    return budget_for(email)


def grant_overage(email, extra_usd):
    """Approve a one-off top-up for the current month only."""
    path = "limits/%s.json" % _safe_email(email)
    cur = _blob_read_json(path) or {}
    cur["email"] = (email or "").lower()
    grants = cur.get("grants") if isinstance(cur.get("grants"), dict) else {}
    grants[_month()] = round(float(grants.get(_month()) or 0.0) + float(extra_usd), 4)
    cur["grants"] = grants
    _blob_write_json(path, cur)
    return budget_for(email)


def current_user(headers):
    try:
        cookies = headers.get("Cookie") or headers.get("cookie") or ""
    except AttributeError:
        cookies = ""
    email = session_from_cookies(cookies)
    if not email and key("AUTH_DEV_BYPASS") == "1":
        return "dev@" + ALLOWED_DOMAIN
    return email


def me(headers):
    """What the browser needs on boot: who you are, or how to sign in."""
    try:
        cookies = headers.get("Cookie") or headers.get("cookie") or ""
    except AttributeError:
        cookies = ""
    email = session_from_cookies(cookies)
    if key("AUTH_DEV_BYPASS") == "1" and not email:
        email = "dev@" + ALLOWED_DOMAIN
    return {"authenticated": bool(email), "email": email or "",
            "client_id": key("GOOGLE_CLIENT_ID") or "",
            "domain": ALLOWED_DOMAIN}


def status():
    return {
        "openai": bool(key("OPENAI_API_KEY")),
        "anthropic": bool(key("ANTHROPIC_API_KEY")),
        "critic": "claude" if key("ANTHROPIC_API_KEY") else "openai",
        "image_models": ["gpt-image-1"] if key("OPENAI_API_KEY") else [],
    }
